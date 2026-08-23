"""
Idempotent Payment Service

Demonstrates:
- Idempotency keys for preventing duplicate charges
- Distributed locking
- State tracking
- Cache + Database hybrid storage
"""

import json
import hashlib
import time
from typing import Optional, Dict
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
import redis
import psycopg2
from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel


# Redis client
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Database connection (in production, use connection pool)
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="idempotency_demo",
        user="postgres",
        password="postgres"
    )


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentRequest(BaseModel):
    user_id: int
    amount: float
    currency: str = "USD"
    description: str


class PaymentResponse(BaseModel):
    payment_id: str
    status: PaymentStatus
    transaction_id: Optional[str] = None
    amount: float
    currency: str
    created_at: str


def hash_request(data: dict) -> str:
    """Generate stable hash of request data"""
    return hashlib.sha256(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()


class DistributedLock:
    """Redis-based distributed lock"""
    
    def __init__(self, key: str, timeout: int = 30):
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.lock_id = f"{time.time()}_{id(self)}"
    
    def __enter__(self):
        # Try to acquire lock
        end_time = time.time() + 10  # Max 10s wait
        while time.time() < end_time:
            acquired = redis_client.set(
                self.key,
                self.lock_id,
                nx=True,  # Only if not exists
                ex=self.timeout
            )
            if acquired:
                return self
            time.sleep(0.05)
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not acquire lock"
        )
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Release lock atomically (Lua script)
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        redis_client.eval(lua_script, 1, self.key, self.lock_id)


class IdempotentPaymentService:
    """Payment service with idempotency"""
    
    def __init__(self):
        self.cache_ttl = 86400  # 24 hours
    
    def check_cache(self, key: str) -> Optional[Dict]:
        """Check Redis cache for existing result"""
        cached = redis_client.hgetall(f"payment:{key}")
        if cached and cached.get('status') == PaymentStatus.COMPLETED:
            return {
                "payment_id": cached['payment_id'],
                "status": PaymentStatus.COMPLETED,
                "transaction_id": cached.get('transaction_id'),
                "amount": float(cached['amount']),
                "currency": cached['currency'],
                "created_at": cached['created_at']
            }
        return None
    
    def check_database(self, key: str) -> Optional[Dict]:
        """Check database for existing payment"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT payment_id, status, transaction_id, amount, 
                       currency, created_at
                FROM payments 
                WHERE idempotency_key = %s
            """, (key,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "payment_id": row[0],
                    "status": row[1],
                    "transaction_id": row[2],
                    "amount": float(row[3]),
                    "currency": row[4],
                    "created_at": row[5].isoformat()
                }
        finally:
            conn.close()
        return None
    
    def validate_request(self, key: str, request_data: dict) -> None:
        """Validate that request matches stored request hash"""
        stored_hash = redis_client.hget(f"payment:{key}", "request_hash")
        if stored_hash:
            current_hash = hash_request(request_data)
            if stored_hash != current_hash:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Idempotency key reused with different payload"
                )
    
    def check_processing_state(self, key: str) -> None:
        """Check if payment is currently being processed"""
        state = redis_client.hgetall(f"payment:{key}")
        if state.get('status') == PaymentStatus.PROCESSING:
            started_at = float(state.get('started_at', 0))
            elapsed = time.time() - started_at
            
            if elapsed < 300:  # 5 minutes
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Payment is currently being processed"
                )
            # If > 5 minutes, consider it stuck and allow retry
    
    def process_payment(
        self,
        idempotency_key: str,
        payment_data: PaymentRequest
    ) -> PaymentResponse:
        """Process payment idempotently"""
        
        # 1. Check cache (fast path)
        cached = self.check_cache(idempotency_key)
        if cached:
            return PaymentResponse(**cached)
        
        # 2. Check database (slow path)
        db_result = self.check_database(idempotency_key)
        if db_result and db_result['status'] == PaymentStatus.COMPLETED:
            # Warm cache
            self._cache_result(idempotency_key, db_result)
            return PaymentResponse(**db_result)
        
        # 3. Acquire distributed lock
        with DistributedLock(idempotency_key):
            # Double-check after acquiring lock
            cached = self.check_cache(idempotency_key)
            if cached:
                return PaymentResponse(**cached)
            
            # 4. Validate request
            request_dict = payment_data.dict()
            self.validate_request(idempotency_key, request_dict)
            
            # 5. Check processing state
            self.check_processing_state(idempotency_key)
            
            # 6. Mark as processing
            self._mark_processing(idempotency_key, request_dict)
            
            try:
                # 7. Process payment (simulate)
                payment_result = self._charge_payment(payment_data)
                
                # 8. Store in database
                self._store_payment(idempotency_key, payment_result)
                
                # 9. Cache result
                self._cache_result(idempotency_key, payment_result)
                
                return PaymentResponse(**payment_result)
                
            except Exception as e:
                # Mark as failed
                redis_client.hset(
                    f"payment:{idempotency_key}",
                    "status",
                    PaymentStatus.FAILED
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Payment processing failed: {str(e)}"
                )
    
    def _mark_processing(self, key: str, request_data: dict) -> None:
        """Mark payment as processing"""
        redis_client.hset(f"payment:{key}", mapping={
            "status": PaymentStatus.PROCESSING,
            "started_at": str(time.time()),
            "request_hash": hash_request(request_data)
        })
        redis_client.expire(f"payment:{key}", self.cache_ttl)
    
    def _charge_payment(self, payment_data: PaymentRequest) -> Dict:
        """Simulate charging payment (replace with actual payment gateway)"""
        # Simulate processing time
        time.sleep(0.1)
        
        # In production: call Stripe, PayPal, etc.
        transaction_id = f"txn_{int(time.time())}_{payment_data.user_id}"
        
        return {
            "payment_id": f"pay_{int(time.time())}",
            "status": PaymentStatus.COMPLETED,
            "transaction_id": transaction_id,
            "amount": payment_data.amount,
            "currency": payment_data.currency,
            "created_at": datetime.utcnow().isoformat()
        }
    
    def _store_payment(self, idempotency_key: str, payment_data: Dict) -> None:
        """Store payment in database"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO payments 
                (payment_id, idempotency_key, status, transaction_id, 
                 amount, currency, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (idempotency_key) DO NOTHING
            """, (
                payment_data['payment_id'],
                idempotency_key,
                payment_data['status'],
                payment_data['transaction_id'],
                payment_data['amount'],
                payment_data['currency'],
                payment_data['created_at']
            ))
            conn.commit()
        finally:
            conn.close()
    
    def _cache_result(self, key: str, payment_data: Dict) -> None:
        """Cache payment result in Redis"""
        redis_client.hset(f"payment:{key}", mapping={
            "payment_id": payment_data['payment_id'],
            "status": payment_data['status'],
            "transaction_id": payment_data.get('transaction_id', ''),
            "amount": str(payment_data['amount']),
            "currency": payment_data['currency'],
            "created_at": payment_data['created_at']
        })
        redis_client.expire(f"payment:{key}", self.cache_ttl)


# FastAPI app
app = FastAPI(title="Idempotent Payment Service")
payment_service = IdempotentPaymentService()


@app.post("/api/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment: PaymentRequest,
    idempotency_key: str = Header(..., description="Client-generated UUID for idempotency")
):
    """
    Create a payment idempotently.
    
    - **Idempotency-Key**: Required header with unique identifier (UUID)
    - Duplicate requests with same key return cached response
    - Key expires after 24 hours
    - Returns 422 if key reused with different payload
    - Returns 409 if payment is currently processing
    """
    return payment_service.process_payment(idempotency_key, payment)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Check Redis
        redis_client.ping()
        
        # Check Database
        conn = get_db_connection()
        conn.close()
        
        return {"status": "healthy", "redis": "ok", "database": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
