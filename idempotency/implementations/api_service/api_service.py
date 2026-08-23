"""
Generic Idempotent API Service with Middleware

Demonstrates:
- Automatic idempotency middleware
- Multiple endpoint types
- Flexible storage backends
- RESTful API patterns
"""

import json
import hashlib
import time
from typing import Optional, Dict, Callable
from datetime import datetime
from functools import wraps
import redis
from fastapi import FastAPI, Header, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# Redis client
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


class IdempotencyMiddleware:
    """Middleware for automatic idempotency handling"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.ttl = 3600  # 1 hour default
    
    async def __call__(self, request: Request, call_next: Callable):
        # Only apply to POST requests
        if request.method != "POST":
            return await call_next(request)
        
        # Get idempotency key from header
        idempotency_key = request.headers.get("idempotency-key")
        
        if not idempotency_key:
            # No key provided, process normally
            return await call_next(request)
        
        # Check cache
        cache_key = f"api:{request.url.path}:{idempotency_key}"
        cached = redis_client.hgetall(cache_key)
        
        if cached and cached.get('status') == 'completed':
            # Return cached response
            return JSONResponse(
                status_code=int(cached.get('status_code', 200)),
                content=json.loads(cached['body']),
                headers={"X-Idempotency": "hit"}
            )
        
        if cached and cached.get('status') == 'processing':
            # Still processing
            elapsed = time.time() - float(cached.get('started_at', 0))
            if elapsed < 300:  # 5 minutes
                return JSONResponse(
                    status_code=status.HTTP_409_CONFLICT,
                    content={"error": "Request is being processed"}
                )
        
        # Read request body for validation
        body = await request.body()
        request_hash = hashlib.sha256(body).hexdigest()
        
        # Check for conflicts
        stored_hash = cached.get('request_hash') if cached else None
        if stored_hash and stored_hash != request_hash:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"error": "Idempotency key reused with different payload"}
            )
        
        # Mark as processing
        redis_client.hset(cache_key, mapping={
            "status": "processing",
            "started_at": str(time.time()),
            "request_hash": request_hash
        })
        redis_client.expire(cache_key, self.ttl)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Read response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Cache successful response
            if 200 <= response.status_code < 300:
                redis_client.hset(cache_key, mapping={
                    "status": "completed",
                    "status_code": str(response.status_code),
                    "body": response_body.decode(),
                    "completed_at": str(time.time())
                })
                redis_client.expire(cache_key, self.ttl)
            
            # Return response
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
        except Exception as e:
            # Mark as failed
            redis_client.hset(cache_key, "status", "failed")
            raise


# FastAPI app with middleware
app = FastAPI(title="Idempotent API Service")
app.middleware("http")(IdempotencyMiddleware(app))


# Models
class CreateUserRequest(BaseModel):
    username: str
    email: str
    full_name: str


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


class CreateOrderRequest(BaseModel):
    user_id: int
    items: list
    total: float


class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    created_at: str


class Order(BaseModel):
    id: int
    user_id: int
    items: list
    total: float
    status: str
    created_at: str


# In-memory storage (replace with real database)
users_db = {}
orders_db = {}
user_id_counter = 1
order_id_counter = 1


# Endpoints
@app.post("/api/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: CreateUserRequest):
    """
    Create a new user (idempotent with Idempotency-Key header)
    """
    global user_id_counter
    
    # Check if username already exists
    for existing_user in users_db.values():
        if existing_user['username'] == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
    
    # Create user
    user_id = user_id_counter
    user_id_counter += 1
    
    new_user = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "created_at": datetime.utcnow().isoformat()
    }
    
    users_db[user_id] = new_user
    return new_user


@app.get("/api/users/{user_id}", response_model=User)
def get_user(user_id: int):
    """Get user by ID (naturally idempotent - GET request)"""
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@app.put("/api/users/{user_id}", response_model=User)
def update_user(user_id: int, updates: UpdateUserRequest):
    """
    Update user (idempotent - PUT request)
    Multiple calls with same data produce same result
    """
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if updates.full_name:
        user['full_name'] = updates.full_name
    if updates.email:
        user['email'] = updates.email
    
    users_db[user_id] = user
    return user


@app.delete("/api/users/{user_id}")
def delete_user(user_id: int):
    """
    Delete user (idempotent - DELETE request)
    First call deletes, subsequent calls return 404
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    del users_db[user_id]
    return {"message": "User deleted successfully"}


@app.post("/api/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(order: CreateOrderRequest):
    """
    Create order (idempotent with Idempotency-Key header)
    Automatically handled by middleware
    """
    global order_id_counter
    
    # Validate user exists
    if order.user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    # Create order
    order_id = order_id_counter
    order_id_counter += 1
    
    new_order = {
        "id": order_id,
        "user_id": order.user_id,
        "items": order.items,
        "total": order.total,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    
    orders_db[order_id] = new_order
    return new_order


@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    """Get order by ID (naturally idempotent)"""
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@app.put("/api/orders/{order_id}/status")
def update_order_status(order_id: int, status_update: dict):
    """
    Update order status (idempotent - setting absolute state)
    """
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    new_status = status_update.get('status')
    if new_status not in ['pending', 'processing', 'completed', 'cancelled']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )
    
    order['status'] = new_status
    orders_db[order_id] = order
    return order


@app.post("/api/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    """
    Confirm order (idempotent with Idempotency-Key)
    State transition: pending -> confirmed
    """
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Idempotent state transition
    if order['status'] in ['completed', 'confirmed']:
        # Already confirmed, return success
        return {"message": "Order already confirmed", "order": order}
    
    if order['status'] == 'cancelled':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot confirm cancelled order"
        )
    
    order['status'] = 'confirmed'
    orders_db[order_id] = order
    return {"message": "Order confirmed", "order": order}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return {
            "status": "healthy",
            "redis": "ok",
            "users_count": len(users_db),
            "orders_count": len(orders_db)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/api/idempotency/stats")
def idempotency_stats():
    """Get idempotency cache statistics"""
    cursor = 0
    total_keys = 0
    processing = 0
    completed = 0
    
    while True:
        cursor, keys = redis_client.scan(cursor, match="api:*", count=100)
        total_keys += len(keys)
        
        for key in keys:
            status_val = redis_client.hget(key, "status")
            if status_val == "processing":
                processing += 1
            elif status_val == "completed":
                completed += 1
        
        if cursor == 0:
            break
    
    return {
        "total_cached_requests": total_keys,
        "processing": processing,
        "completed": completed,
        "cache_hit_potential": f"{(completed / total_keys * 100) if total_keys > 0 else 0:.1f}%"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
