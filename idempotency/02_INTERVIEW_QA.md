# Idempotency - Interview Questions & Answers

## Table of Contents
- [Fundamentals (Q1-Q15)](#fundamentals)
- [Implementation (Q16-Q30)](#implementation)
- [Advanced Concepts (Q31-Q45)](#advanced-concepts)
- [System Design (Q46-Q60)](#system-design)
- [Troubleshooting (Q61-Q70)](#troubleshooting)

---

## Fundamentals

### Q1: What is idempotency?
**Answer**: Idempotency means that performing an operation multiple times produces the same result as performing it once. In mathematical terms: `f(f(x)) = f(x)`.

**Example**:
- ✅ Idempotent: `SET x = 5` (always results in x=5)
- ❌ Not idempotent: `x = x + 1` (result changes each time)

**Why it matters**: In distributed systems with network failures and retries, idempotency ensures operations can be safely retried without unintended side effects.

---

### Q2: Why is idempotency important in distributed systems?
**Answer**: Distributed systems face:
1. **Network failures**: Requests timeout and get retried
2. **Duplicate messages**: Message queues deliver at-least-once
3. **Concurrent operations**: Multiple processes may act simultaneously
4. **User actions**: Double-clicks, accidental re-submissions

Without idempotency:
- Payments charged twice
- Orders created multiple times
- Inconsistent data states

With idempotency:
- Safe retries
- Predictable behavior
- Data consistency

---

### Q3: Which HTTP methods are idempotent?
**Answer**:

**Idempotent methods**:
- **GET**: Retrieves data, no side effects
- **PUT**: Replace resource (same state after multiple calls)
- **DELETE**: Remove resource (idempotent - resource stays deleted)
- **HEAD, OPTIONS**: Read-only operations

**Non-idempotent methods**:
- **POST**: Creates new resources each time

**Note**: PATCH can be idempotent depending on implementation.

**Example**:
```http
DELETE /api/orders/123
First call: 200 OK (order deleted)
Second call: 404 Not Found (still idempotent - order is deleted)
```

---

### Q4: What's the difference between idempotency and pure functions?
**Answer**:

**Pure functions**:
- Same input → same output
- No side effects at all
- Deterministic
- Example: `max(5, 10)` always returns 10

**Idempotent operations**:
- Same result after multiple executions
- May have side effects (but only once)
- Example: `DELETE /api/users/123` has side effects but is idempotent

**Key difference**: Pure functions have NO side effects. Idempotent operations may have side effects that only occur once.

---

### Q5: How do you make POST requests idempotent?
**Answer**: Use **idempotency keys** in request headers.

**Implementation**:
```python
# Client side
import uuid
idempotency_key = str(uuid.uuid4())

response = requests.post(
    '/api/orders',
    headers={'Idempotency-Key': idempotency_key},
    json=order_data
)

# Server side
@app.post("/api/orders")
def create_order(request, idempotency_key: str = Header(None)):
    # Check if key already processed
    cached_result = cache.get(f"order:{idempotency_key}")
    if cached_result:
        return cached_result
    
    # Process new request
    result = process_order(request.data)
    
    # Cache result
    cache.setex(f"order:{idempotency_key}", 86400, result)
    return result
```

**Best practices**:
- Client generates unique key (UUID)
- Server stores key with result
- Set appropriate TTL (24-48 hours typically)
- Return 422 if key reused with different payload

---

### Q6: What storage options exist for idempotency keys?
**Answer**:

**1. In-memory cache (Redis)**
- ✅ Fast lookup (< 10ms)
- ✅ Built-in TTL
- ❌ Not durable
- Use: Short-lived operations

**2. Database (PostgreSQL, MySQL)**
- ✅ Durable
- ✅ ACID guarantees
- ❌ Slower than cache
- Use: Long-term storage, audit trail

**3. Hybrid approach**
- Check cache first (fast path)
- Fall back to database (slow path)
- Best of both worlds

**Example**:
```python
def check_idempotency(key):
    # Fast path: cache
    result = redis.get(key)
    if result:
        return result
    
    # Slow path: database
    result = db.query("SELECT * FROM requests WHERE key = ?", key)
    if result:
        # Warm cache
        redis.setex(key, 3600, result)
    return result
```

---

### Q7: How long should idempotency keys be stored?
**Answer**: Depends on business requirements:

**TTL Guidelines**:

| Operation Type | TTL | Rationale |
|---------------|-----|-----------|
| Payment processing | 24-48 hours | User might retry same day |
| Order creation | 1-2 hours | Checkout session timeout |
| API webhooks | 7 days | Allow for extended retries |
| Message processing | 1 hour | Recent duplicates only |
| File uploads | 1 hour | Session-based |

**Factors to consider**:
1. **User retry window**: How long might users retry?
2. **Network timeout**: Typical retry intervals
3. **Business logic**: When is retry no longer valid?
4. **Storage cost**: Longer TTL = more storage

**Example**:
```python
# Payment: 24 hours
redis.setex(f"payment:{key}", 86400, result)

# Webhook: 7 days
redis.setex(f"webhook:{key}", 604800, result)
```

---

### Q8: What happens when two requests arrive simultaneously?
**Answer**: **Race condition** - both might think they're first.

**Problem**:
```
Request A ──→ Check (not found) ──→ Process ──→ Save
Request B ──→ Check (not found) ──→ Process ──→ Save
         Both processed! ❌
```

**Solutions**:

**1. Distributed lock**:
```python
with redis_lock(f"lock:{idempotency_key}", timeout=30):
    if not exists(idempotency_key):
        result = process_request()
        save(idempotency_key, result)
```

**2. Database unique constraint**:
```sql
CREATE TABLE requests (
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    result JSONB,
    created_at TIMESTAMP
);

-- Insert will fail for duplicate
INSERT INTO requests (idempotency_key, result)
VALUES ('abc123', '{"status": "success"}');
```

**3. Optimistic locking**:
```python
# Use version numbers
UPDATE orders 
SET status = 'completed', version = version + 1
WHERE id = 123 AND version = 5
```

---

### Q9: How do you handle partial failures?
**Answer**: Store processing state alongside result.

**Problem**:
```
Client → Request → Server (processes successfully)
       ← [Network timeout] ← Response lost
Client → Retry → Server (what to return?)
```

**Solution**:
```python
# Store state during processing
redis.hset(idempotency_key, mapping={
    "status": "processing",
    "started_at": time.time(),
    "request_hash": hash(request)
})

try:
    # Process request
    result = process_payment(...)
    
    # Store success
    redis.hset(idempotency_key, mapping={
        "status": "completed",
        "result": json.dumps(result),
        "completed_at": time.time()
    })
    return result
    
except Exception as e:
    # Store failure
    redis.hset(idempotency_key, mapping={
        "status": "failed",
        "error": str(e),
        "failed_at": time.time()
    })
    raise

# On retry
state = redis.hgetall(idempotency_key)
if state["status"] == "completed":
    return json.loads(state["result"])
elif state["status"] == "processing":
    # Check if stuck (timeout)
    if time.time() - float(state["started_at"]) > 300:
        # Retry processing
        pass
    else:
        # Still processing, wait
        raise HTTPException(409, "Request still processing")
```

---

### Q10: What's the difference between idempotency and deduplication?
**Answer**:

**Deduplication**:
- Detect and remove duplicates
- Focus: preventing duplicates
- When: Before processing
- Example: Message queue filtering

**Idempotency**:
- Handle duplicates safely
- Focus: making operations repeatable
- When: During/after processing
- Example: Reprocessing same request gives same result

**Relationship**: Deduplication is one way to achieve idempotency.

**Example**:
```python
# Deduplication: prevent duplicates
seen_messages = set()
if message_id in seen_messages:
    return  # Skip
seen_messages.add(message_id)

# Idempotency: handle duplicates safely
result = process_or_get_cached(idempotency_key)
```

---

### Q11: How do you validate idempotency key reuse?
**Answer**: Check if the request payload matches.

**Problem**: Same key, different request
```python
# Request 1
POST /api/payments
Idempotency-Key: abc123
{"amount": 100, "currency": "USD"}

# Request 2 (malicious or error)
POST /api/payments
Idempotency-Key: abc123
{"amount": 999, "currency": "USD"}
```

**Solution**: Store and compare request hash
```python
import hashlib
import json

def get_request_hash(data):
    # Stable hash (sorted keys)
    return hashlib.sha256(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()

@app.post("/api/payments")
def create_payment(request, idempotency_key: str):
    request_hash = get_request_hash(request.json)
    
    # Check existing request
    existing = redis.hgetall(f"payment:{idempotency_key}")
    if existing:
        stored_hash = existing.get("request_hash")
        if stored_hash != request_hash:
            # Different payload with same key
            raise HTTPException(
                422,
                "Idempotency key reused with different payload"
            )
        # Same request, return cached result
        return json.loads(existing["result"])
    
    # New request - store hash
    redis.hset(f"payment:{idempotency_key}", mapping={
        "request_hash": request_hash,
        "status": "processing"
    })
    
    # Process...
```

---

### Q12: Can GET requests be non-idempotent?
**Answer**: **Yes**, if poorly implemented.

**Non-idempotent GET examples**:
```python
# Bad: Side effects in GET
@app.get("/api/increment-counter")
def increment():
    counter += 1  # ❌ Modifies state
    return {"counter": counter}

# Bad: Tracking views
@app.get("/api/posts/{id}")
def get_post(id):
    post = db.get_post(id)
    db.increment_view_count(id)  # ❌ Side effect
    return post
```

**Best practices**:
- GET should only read
- Use POST for operations with side effects
- If tracking needed, do it asynchronously/separately

**Correct implementation**:
```python
# Good: Read-only GET
@app.get("/api/posts/{id}")
def get_post(id):
    return db.get_post(id)

# Good: Separate POST for tracking
@app.post("/api/posts/{id}/views")
def track_view(id):
    db.increment_view_count(id)
```

---

### Q13: What is natural idempotency?
**Answer**: Operations that are inherently idempotent by design.

**Examples**:
```python
# Setting absolute values (naturally idempotent)
user.status = "active"
user.email = "new@example.com"

# SQL UPDATE with fixed value
UPDATE users SET status = 'active' WHERE id = 123
# Multiple executions: status is still 'active'

# Redis SET
redis.set("key", "value")
# Multiple executions: value is still "value"

# Boolean flags
is_deleted = True
is_verified = False
```

**Vs explicit idempotency**:
```python
# Requires explicit handling (not naturally idempotent)
balance = balance + 100  # ❌ Changes each time

# Made idempotent with conditions
UPDATE accounts 
SET balance = balance + 100 
WHERE id = 123 AND NOT EXISTS (
    SELECT 1 FROM transactions WHERE idempotency_key = 'abc123'
)
```

**Benefits**:
- No additional infrastructure needed
- Simpler implementation
- Lower overhead

---

### Q14: How does versioning help with idempotency?
**Answer**: Track operation versions to detect replays.

**Implementation**:
```python
# Each operation has version number
class Order:
    id: str
    version: int
    status: str
    updated_at: datetime

# Update with version check
def update_order(order_id, new_status, expected_version):
    result = db.execute("""
        UPDATE orders 
        SET status = ?,
            version = version + 1,
            updated_at = NOW()
        WHERE id = ? AND version = ?
        RETURNING *
    """, (new_status, order_id, expected_version))
    
    if result.rowcount == 0:
        # Version mismatch - already updated
        current = db.query("SELECT * FROM orders WHERE id = ?", order_id)
        if current.version > expected_version:
            return current  # Return current state
        raise ConflictError("Version conflict")
    
    return result.fetchone()

# Client usage
order = get_order("123")  # version = 5
update_order("123", "shipped", version=5)  # Success
update_order("123", "shipped", version=5)  # Returns current (idempotent)
```

**Benefits**:
- Optimistic concurrency control
- No distributed locks needed
- Works well with event sourcing

---

### Q15: What's the role of timestamps in idempotency?
**Answer**: Timestamps help with:

1. **Detecting stuck operations**
2. **Time-based deduplication**
3. **Audit trails**

**Example**:
```python
# Detect stuck processing
state = redis.hgetall(idempotency_key)
if state["status"] == "processing":
    started_at = float(state["started_at"])
    if time.time() - started_at > 300:  # 5 minutes
        # Operation stuck, retry
        logger.warning(f"Operation {idempotency_key} stuck, retrying")
        retry_operation()

# Time-based deduplication (sliding window)
def is_duplicate_message(message_id, window_seconds=3600):
    key = f"msg:{message_id}"
    if redis.exists(key):
        return True
    redis.setex(key, window_seconds, "1")
    return False

# Audit trail
{
    "idempotency_key": "abc123",
    "request_received_at": "2024-08-13T10:00:00Z",
    "processing_started_at": "2024-08-13T10:00:01Z",
    "processing_completed_at": "2024-08-13T10:00:05Z",
    "response_sent_at": "2024-08-13T10:00:05Z"
}
```

---

## Implementation

### Q16: How do you implement idempotency with Redis?
**Answer**: Use Redis as fast lookup cache for idempotency keys.

**Basic pattern**:
```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def idempotent_operation(idempotency_key, operation_func, *args, **kwargs):
    # Check if already processed
    cached_result = redis_client.get(f"idem:{idempotency_key}")
    if cached_result:
        return json.loads(cached_result)
    
    # Process operation
    result = operation_func(*args, **kwargs)
    
    # Cache result (24 hour TTL)
    redis_client.setex(
        f"idem:{idempotency_key}",
        86400,
        json.dumps(result)
    )
    
    return result

# Usage
result = idempotent_operation(
    "payment_abc123",
    process_payment,
    user_id=123,
    amount=99.99
)
```

**With state tracking**:
```python
def idempotent_with_state(key, func, *args, **kwargs):
    # Check existing state
    state = redis_client.hgetall(f"idem:{key}")
    
    if state:
        if state.get("status") == "completed":
            return json.loads(state["result"])
        elif state.get("status") == "processing":
            # Check timeout
            if time.time() - float(state["started_at"]) > 300:
                # Retry
                pass
            else:
                raise Exception("Still processing")
    
    # Mark as processing
    redis_client.hset(f"idem:{key}", mapping={
        "status": "processing",
        "started_at": time.time()
    })
    
    try:
        result = func(*args, **kwargs)
        
        # Mark completed
        redis_client.hset(f"idem:{key}", mapping={
            "status": "completed",
            "result": json.dumps(result),
            "completed_at": time.time()
        })
        redis_client.expire(f"idem:{key}", 86400)
        
        return result
    except Exception as e:
        redis_client.hset(f"idem:{key}", mapping={
            "status": "failed",
            "error": str(e)
        })
        raise
```

---

### Q17: How do you implement idempotency with PostgreSQL?
**Answer**: Use unique constraints on idempotency keys.

**Schema**:
```sql
CREATE TABLE idempotency_keys (
    id SERIAL PRIMARY KEY,
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    request_hash VARCHAR(64) NOT NULL,
    status VARCHAR(20) NOT NULL,
    request_payload JSONB,
    response_payload JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_idempotency_key ON idempotency_keys(idempotency_key);
CREATE INDEX idx_created_at ON idempotency_keys(created_at);
```

**Implementation**:
```python
import psycopg2
from psycopg2 import IntegrityError

def idempotent_payment(conn, idempotency_key, amount, user_id):
    cursor = conn.cursor()
    
    # Check if already processed
    cursor.execute("""
        SELECT status, response_payload 
        FROM idempotency_keys 
        WHERE idempotency_key = %s
    """, (idempotency_key,))
    
    existing = cursor.fetchone()
    if existing:
        status, response = existing
        if status == 'completed':
            return response
        elif status == 'processing':
            raise Exception("Request still processing")
    
    try:
        # Insert idempotency record
        cursor.execute("""
            INSERT INTO idempotency_keys 
            (idempotency_key, request_hash, status, request_payload)
            VALUES (%s, %s, 'processing', %s)
        """, (
            idempotency_key,
            hash_request({"amount": amount, "user_id": user_id}),
            json.dumps({"amount": amount, "user_id": user_id})
        ))
        conn.commit()
        
    except IntegrityError:
        # Concurrent request - retry lookup
        conn.rollback()
        return idempotent_payment(conn, idempotency_key, amount, user_id)
    
    try:
        # Process payment
        result = process_payment(amount, user_id)
        
        # Update as completed
        cursor.execute("""
            UPDATE idempotency_keys 
            SET status = 'completed',
                response_payload = %s,
                completed_at = NOW()
            WHERE idempotency_key = %s
        """, (json.dumps(result), idempotency_key))
        
        conn.commit()
        return result
        
    except Exception as e:
        cursor.execute("""
            UPDATE idempotency_keys 
            SET status = 'failed'
            WHERE idempotency_key = %s
        """, (idempotency_key,))
        conn.commit()
        raise
```

---

### Q18: How do you implement distributed locks for idempotency?
**Answer**: Use Redis or database-based locks.

**Redis-based lock**:
```python
import redis
import uuid
import time

class RedisLock:
    def __init__(self, redis_client, lock_key, timeout=30):
        self.redis = redis_client
        self.lock_key = f"lock:{lock_key}"
        self.lock_id = str(uuid.uuid4())
        self.timeout = timeout
    
    def __enter__(self):
        # Try to acquire lock
        end_time = time.time() + self.timeout
        while time.time() < end_time:
            # SET NX (set if not exists) with expiry
            acquired = self.redis.set(
                self.lock_key,
                self.lock_id,
                nx=True,
                ex=self.timeout
            )
            if acquired:
                return self
            time.sleep(0.1)
        
        raise Exception(f"Could not acquire lock {self.lock_key}")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Release lock (atomically with Lua)
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        self.redis.eval(lua_script, 1, self.lock_key, self.lock_id)

# Usage
redis_client = redis.Redis()

def process_payment(idempotency_key, amount):
    with RedisLock(redis_client, f"payment:{idempotency_key}"):
        # Only one process can enter this block
        if exists_in_cache(idempotency_key):
            return get_from_cache(idempotency_key)
        
        result = charge_card(amount)
        save_to_cache(idempotency_key, result)
        return result
```

**PostgreSQL advisory lock**:
```python
def with_advisory_lock(conn, lock_id):
    cursor = conn.cursor()
    
    # Acquire lock (blocks until available)
    cursor.execute("SELECT pg_advisory_lock(%s)", (lock_id,))
    
    try:
        yield
    finally:
        # Release lock
        cursor.execute("SELECT pg_advisory_unlock(%s)", (lock_id,))

# Usage
def idempotent_operation(conn, idempotency_key):
    lock_id = hash(idempotency_key) % (2**31)  # Convert to int
    
    with with_advisory_lock(conn, lock_id):
        # Check and process
        result = check_or_process(idempotency_key)
        return result
```

---

### Q19: How do you handle idempotency in microservices?
**Answer**: Each service should implement idempotency independently.

**Architecture**:
```
API Gateway
    ↓ (generates idempotency key)
Order Service (idempotent)
    ↓ (propagates key)
Payment Service (idempotent)
    ↓ (propagates key)
Notification Service (idempotent)
```

**Implementation**:
```python
# API Gateway
@app.post("/api/checkout")
async def checkout(request):
    # Generate or extract idempotency key
    idempotency_key = request.headers.get("Idempotency-Key") or str(uuid.uuid4())
    
    # Forward to Order Service
    order_response = await http_client.post(
        "http://order-service/orders",
        headers={"Idempotency-Key": idempotency_key},
        json=request.json
    )
    return order_response

# Order Service
@app.post("/orders")
async def create_order(request, idempotency_key: str = Header(...)):
    # Check if already processed
    cached = await cache.get(f"order:{idempotency_key}")
    if cached:
        return cached
    
    # Create order
    order = await db.create_order(request.json)
    
    # Call Payment Service with same key
    payment_response = await http_client.post(
        "http://payment-service/payments",
        headers={"Idempotency-Key": f"{idempotency_key}_payment"},
        json={"order_id": order.id, "amount": order.total}
    )
    
    # Cache result
    result = {"order": order, "payment": payment_response}
    await cache.setex(f"order:{idempotency_key}", 3600, result)
    
    return result

# Payment Service
@app.post("/payments")
async def process_payment(request, idempotency_key: str = Header(...)):
    # Independent idempotency check
    cached = await cache.get(f"payment:{idempotency_key}")
    if cached:
        return cached
    
    result = await charge_card(request.json)
    await cache.setex(f"payment:{idempotency_key}", 3600, result)
    
    return result
```

**Key patterns**:
1. **Propagate keys**: Pass idempotency key through call chain
2. **Derive keys**: Create sub-keys for downstream services
3. **Independent checks**: Each service validates independently
4. **Shared storage**: Use distributed cache/database

---

### Q20: How do you implement idempotency for message queues?
**Answer**: Track message IDs and process each message only once.

**Pattern**:
```python
import boto3
import redis

sqs = boto3.client('sqs')
redis_client = redis.Redis()

def process_messages(queue_url):
    while True:
        # Receive messages
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20
        )
        
        for message in response.get('Messages', []):
            message_id = message['MessageId']
            
            # Check if already processed
            if redis_client.exists(f"processed:{message_id}"):
                # Already processed, just delete from queue
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                continue
            
            try:
                # Process message
                process_order(json.loads(message['Body']))
                
                # Mark as processed (7 day TTL)
                redis_client.setex(f"processed:{message_id}", 604800, "1")
                
                # Delete from queue
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                
            except Exception as e:
                logger.error(f"Error processing {message_id}: {e}")
                # Message will be redelivered after visibility timeout
```

**With database tracking**:
```python
def process_with_db(message):
    message_id = message['MessageId']
    
    try:
        # Atomic insert (unique constraint on message_id)
        db.execute("""
            INSERT INTO processed_messages (message_id, processed_at)
            VALUES (%s, NOW())
        """, (message_id,))
        
        # Process message
        handle_message(message)
        
        # Mark as successful
        db.execute("""
            UPDATE processed_messages 
            SET status = 'completed'
            WHERE message_id = %s
        """, (message_id,))
        
        return True
        
    except IntegrityError:
        # Already processed
        logger.info(f"Duplicate message {message_id}, skipping")
        return False
```

---

### Q21: How do you test idempotency?
**Answer**: Test concurrent requests and verify single execution.

**Unit test**:
```python
import pytest

def test_idempotent_payment():
    idempotency_key = "test_payment_123"
    
    # First call
    result1 = process_payment(idempotency_key, amount=100)
    assert result1['status'] == 'success'
    assert result1['amount'] == 100
    
    # Second call (duplicate)
    result2 = process_payment(idempotency_key, amount=100)
    
    # Should return same result
    assert result1 == result2
    
    # Verify only one charge occurred
    charges = get_charges_for_key(idempotency_key)
    assert len(charges) == 1
```

**Concurrency test**:
```python
import concurrent.futures
import threading

def test_concurrent_requests():
    idempotency_key = "concurrent_test_456"
    results = []
    errors = []
    
    def make_request():
        try:
            result = process_payment(idempotency_key, amount=100)
            results.append(result)
        except Exception as e:
            errors.append(e)
    
    # Send 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        concurrent.futures.wait(futures)
    
    # All should succeed
    assert len(results) == 10
    assert len(errors) == 0
    
    # All should return same result
    assert all(r == results[0] for r in results)
    
    # Only one actual charge
    charges = get_charges_for_key(idempotency_key)
    assert len(charges) == 1
```

**Integration test**:
```python
@pytest.mark.integration
def test_end_to_end_idempotency():
    client = TestClient(app)
    idempotency_key = str(uuid.uuid4())
    
    # First request
    response1 = client.post(
        "/api/orders",
        headers={"Idempotency-Key": idempotency_key},
        json={"items": [{"id": 1, "qty": 2}]}
    )
    assert response1.status_code == 201
    order1 = response1.json()
    
    # Duplicate request
    response2 = client.post(
        "/api/orders",
        headers={"Idempotency-Key": idempotency_key},
        json={"items": [{"id": 1, "qty": 2}]}
    )
    assert response2.status_code == 200  # or 201
    order2 = response2.json()
    
    # Same order returned
    assert order1['id'] == order2['id']
    
    # Only one order in database
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user_id)
    assert len(orders) == 1
```

**Chaos test**:
```python
def test_with_failures():
    """Test idempotency with simulated failures"""
    
    # Simulate network timeout during processing
    with patch('redis_client.setex', side_effect=TimeoutError):
        with pytest.raises(TimeoutError):
            process_payment("chaos_test_789", 100)
    
    # Retry should succeed and not duplicate
    result = process_payment("chaos_test_789", 100)
    assert result['status'] == 'success'
    
    # Verify single charge
    charges = get_charges_for_key("chaos_test_789")
    assert len(charges) == 1
```

---

### Q22: How do you monitor idempotency in production?
**Answer**: Track metrics, logs, and alerts.

**Key metrics**:
```python
from prometheus_client import Counter, Histogram, Gauge

# Counter: idempotency key hits/misses
idempotency_hits = Counter(
    'idempotency_cache_hits_total',
    'Number of idempotency key cache hits'
)

idempotency_misses = Counter(
    'idempotency_cache_misses_total',
    'Number of idempotency key cache misses'
)

# Counter: conflicts
idempotency_conflicts = Counter(
    'idempotency_conflicts_total',
    'Number of idempotency key conflicts (same key, different payload)'
)

# Histogram: processing time
processing_duration = Histogram(
    'request_processing_duration_seconds',
    'Time spent processing requests'
)

# Gauge: stuck operations
stuck_operations = Gauge(
    'stuck_operations_count',
    'Number of operations stuck in processing state'
)

# Usage
def process_request(idempotency_key, data):
    # Check cache
    cached = redis.get(idempotency_key)
    if cached:
        idempotency_hits.inc()
        return cached
    
    idempotency_misses.inc()
    
    # Check for conflicts
    stored_hash = redis.hget(idempotency_key, "request_hash")
    if stored_hash and stored_hash != hash(data):
        idempotency_conflicts.inc()
        raise ConflictError()
    
    # Process with timing
    with processing_duration.time():
        result = process(data)
    
    return result
```

**Logging**:
```python
import structlog

logger = structlog.get_logger()

def idempotent_operation(key, func):
    logger.info("idempotency_check", key=key, action="checking")
    
    if exists(key):
        logger.info("idempotency_hit", key=key, action="cache_hit")
        return get_cached(key)
    
    logger.info("idempotency_miss", key=key, action="processing")
    
    try:
        result = func()
        logger.info("idempotency_success", key=key, action="completed")
        cache(key, result)
        return result
    except Exception as e:
        logger.error("idempotency_error", key=key, error=str(e))
        raise
```

**Alerts**:
```yaml
# Prometheus alert rules
groups:
  - name: idempotency
    rules:
      # High conflict rate
      - alert: HighIdempotencyConflicts
        expr: rate(idempotency_conflicts_total[5m]) > 10
        annotations:
          summary: "High rate of idempotency conflicts"
      
      # Low cache hit rate
      - alert: LowIdempotencyCacheHitRate
        expr: |
          rate(idempotency_cache_hits_total[5m]) /
          (rate(idempotency_cache_hits_total[5m]) + rate(idempotency_cache_misses_total[5m])) < 0.5
        annotations:
          summary: "Idempotency cache hit rate below 50%"
      
      # Stuck operations
      - alert: StuckIdempotentOperations
        expr: stuck_operations_count > 100
        annotations:
          summary: "Many operations stuck in processing state"
```

---

### Q23: What are common anti-patterns in idempotency?
**Answer**:

**1. Not checking before processing**:
```python
# ❌ Bad
def process_payment(key, amount):
    result = charge_card(amount)  # Always charges
    cache(key, result)  # Caches after
    return result

# ✅ Good
def process_payment(key, amount):
    cached = get_cache(key)
    if cached:
        return cached
    result = charge_card(amount)
    cache(key, result)
    return result
```

**2. Ignoring race conditions**:
```python
# ❌ Bad (race condition)
if not redis.exists(key):
    result = process()  # Two requests can enter here
    redis.set(key, result)

# ✅ Good (atomic)
with distributed_lock(key):
    if not redis.exists(key):
        result = process()
        redis.set(key, result)
```

**3. Not storing responses**:
```python
# ❌ Bad (no response for retries)
redis.set(key, "processed")  # Just a flag

# ✅ Good (store full response)
redis.set(key, json.dumps({
    "status": "success",
    "transaction_id": "tx123",
    "amount": 100
}))
```

**4. Using mutable idempotency keys**:
```python
# ❌ Bad (key changes)
key = f"order_{current_timestamp()}"

# ✅ Good (stable key)
key = f"order_{user_id}_{cart_hash}"
```

**5. No TTL on keys**:
```python
# ❌ Bad (infinite storage)
redis.set(key, result)

# ✅ Good (with expiry)
redis.setex(key, 86400, result)
```

**6. Not validating payload on key reuse**:
```python
# ❌ Bad (allows different payloads)
if redis.exists(key):
    return redis.get(key)
process(new_payload)  # Different from original!

# ✅ Good (validate payload)
stored = redis.hgetall(key)
if stored and hash(payload) != stored["hash"]:
    raise ConflictError()
```

---

### Q24: How do you handle idempotency across databases?
**Answer**: Use distributed transactions or saga pattern.

**Two-Phase Commit (2PC)**:
```python
def distributed_transaction(idempotency_key, operations):
    # Phase 1: Prepare
    prepared = []
    for db in databases:
        if db.prepare(idempotency_key, operations):
            prepared.append(db)
        else:
            # Abort all
            for p in prepared:
                p.abort()
            raise Exception("Prepare failed")
    
    # Phase 2: Commit
    for db in prepared:
        db.commit()
```

**Saga Pattern** (preferred for microservices):
```python
class OrderSaga:
    def execute(self, idempotency_key, order_data):
        # Step 1: Create order
        order_id = order_service.create(idempotency_key, order_data)
        
        try:
            # Step 2: Reserve inventory
            inventory_service.reserve(f"{idempotency_key}_inv", order_id)
            
            # Step 3: Process payment
            payment_service.charge(f"{idempotency_key}_pay", order_id)
            
            # Step 4: Confirm order
            order_service.confirm(order_id)
            
        except Exception as e:
            # Compensating transactions
            payment_service.refund(f"{idempotency_key}_pay")
            inventory_service.release(f"{idempotency_key}_inv")
            order_service.cancel(order_id)
            raise
```

---

### Q25: How do you implement idempotency for file uploads?
**Answer**: Use content hash as idempotency key.

```python
import hashlib

def upload_file(file_content, metadata):
    # Generate content hash
    content_hash = hashlib.sha256(file_content).hexdigest()
    idempotency_key = f"upload_{metadata['user_id']}_{content_hash}"
    
    # Check if already uploaded
    existing = db.query("""
        SELECT file_id, url FROM uploads 
        WHERE idempotency_key = ?
    """, (idempotency_key,))
    
    if existing:
        return existing
    
    # Upload to storage
    file_url = s3.upload(file_content)
    
    # Save metadata
    file_id = db.insert("uploads", {
        "idempotency_key": idempotency_key,
        "url": file_url,
        "user_id": metadata['user_id'],
        "filename": metadata['filename']
    })
    
    return {"file_id": file_id, "url": file_url}
```

---

## Advanced Concepts

### Q26: What is eventual idempotency?
**Answer**: Operations that become idempotent after a delay.

**Example**: Asynchronous processing
```python
# Request is idempotent, but processing is async
@app.post("/api/export")
def create_export(idempotency_key: str):
    # Check if already requested
    existing = redis.get(f"export:{idempotency_key}")
    if existing:
        return {"status": "processing", "job_id": existing}
    
    # Queue export job
    job_id = queue.enqueue(export_data, args=(idempotency_key,))
    redis.setex(f"export:{idempotency_key}", 3600, job_id)
    
    return {"status": "queued", "job_id": job_id}

# Worker processes idempotently
def export_data(idempotency_key):
    # Check if already completed
    if redis.exists(f"export_done:{idempotency_key}"):
        return
    
    # Generate export
    data = generate_export()
    s3.upload(f"exports/{idempotency_key}.csv", data)
    
    # Mark complete
    redis.set(f"export_done:{idempotency_key}", "1")
```

---

### Q27: How does idempotency relate to CQRS?
**Answer**: Commands should be idempotent; queries naturally are.

**Command side** (requires idempotency):
```python
# Command: Create order
class CreateOrderCommand:
    command_id: str  # Idempotency key
    user_id: int
    items: List[Item]

def handle_create_order(command: CreateOrderCommand):
    # Check if command already processed
    if event_store.exists(command.command_id):
        return event_store.get_result(command.command_id)
    
    # Process command
    order = Order.create(command.items)
    
    # Store event
    event = OrderCreatedEvent(command.command_id, order)
    event_store.append(event)
    
    return order
```

**Query side** (naturally idempotent):
```python
# Query: Get order
def get_order(order_id: str):
    return read_model.get(order_id)  # Always returns same data
```

---

### Q28: What is semantic idempotency?
**Answer**: Same business outcome, not necessarily same data.

**Example**:
```python
# Request 1: Set price to $100
UPDATE products SET price = 100 WHERE id = 123

# Request 2: Set price to $100 (idempotent)
UPDATE products SET price = 100 WHERE id = 123

# vs

# Request 1: Increase price by 10%
UPDATE products SET price = price * 1.1 WHERE id = 123

# Request 2: Increase by 10% (NOT idempotent - different result)
# But with business context:
UPDATE products 
SET price = price * 1.1 
WHERE id = 123 AND version = 5  # Only if not already updated
```

---

### Q29: How do you implement idempotency in event-driven systems?
**Answer**: Track event IDs and use idempotent event handlers.

```python
# Event with unique ID
class OrderCreatedEvent:
    event_id: str  # UUID
    order_id: str
    timestamp: datetime
    data: dict

# Idempotent event handler
class EmailNotificationHandler:
    def __init__(self):
        self.processed_events = {}  # Use Redis in production
    
    def handle(self, event: OrderCreatedEvent):
        # Check if already processed
        if event.event_id in self.processed_events:
            logger.info(f"Event {event.event_id} already processed")
            return
        
        # Send email
        send_email(
            to=event.data['customer_email'],
            subject="Order Confirmation",
            body=f"Order {event.order_id} created"
        )
        
        # Mark as processed
        self.processed_events[event.event_id] = event.timestamp

# Event sourcing with idempotency
class EventStore:
    def append(self, event):
        try:
            # Unique constraint on event_id
            self.db.insert("events", {
                "event_id": event.event_id,
                "event_type": event.type,
                "data": json.dumps(event.data),
                "timestamp": event.timestamp
            })
        except IntegrityError:
            # Event already exists (idempotent)
            logger.info(f"Event {event.event_id} already in store")
```

---

### Q30: How do you handle idempotency with third-party APIs?
**Answer**: Use idempotency keys if supported, otherwise track requests yourself.

**API with idempotency support** (e.g., Stripe):
```python
import stripe

def charge_customer(amount, customer_id, idempotency_key):
    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            customer=customer_id,
            idempotency_key=idempotency_key
        )
        return charge
    except stripe.error.IdempotencyError:
        # Key reused with different params
        raise ConflictError()
```

**API without idempotency support**:
```python
def call_third_party_api(idempotency_key, data):
    # Check if already called
    cached = redis.hgetall(f"api:{idempotency_key}")
    if cached:
        if cached['status'] == 'completed':
            return json.loads(cached['response'])
        elif cached['status'] == 'processing':
            # Wait or return processing status
            raise ProcessingError()
    
    # Mark as processing
    redis.hset(f"api:{idempotency_key}", mapping={
        "status": "processing",
        "started_at": time.time()
    })
    
    try:
        # Call API
        response = external_api.call(data)
        
        # Store response
        redis.hset(f"api:{idempotency_key}", mapping={
            "status": "completed",
            "response": json.dumps(response)
        })
        redis.expire(f"api:{idempotency_key}", 86400)
        
        return response
        
    except Exception as e:
        redis.hset(f"api:{idempotency_key}", "status", "failed")
        raise
```

---

### Q31: What's the difference between at-most-once and at-least-once delivery?
**Answer**:

**At-most-once** (may lose messages):
```
Send → Process → Acknowledge
If process fails: message lost ❌
```

**At-least-once** (may duplicate):
```
Send → Acknowledge → Process
If process fails: message redelivered ✅ (but may process twice)
```

**Exactly-once** (ideal but complex):
```
Send → Process + Acknowledge (atomic)
Requires idempotent processing + transactional semantics
```

**Implementation**:
```python
# At-least-once with idempotency
def process_message(message):
    message_id = message['id']
    
    # Idempotency check
    if is_processed(message_id):
        return  # Already done
    
    # Process
    handle_message(message['body'])
    
    # Mark processed (idempotent)
    mark_processed(message_id)
    
    # Acknowledge
    queue.ack(message)

# Even if message redelivered, won't process twice
```

---

### Q32: How do you implement conditional idempotency?
**Answer**: Operations that are idempotent under certain conditions.

```python
# Conditional based on state
def transfer_money(idempotency_key, from_account, to_account, amount):
    # Check if already done
    existing = db.query("""
        SELECT * FROM transactions WHERE idempotency_key = ?
    """, (idempotency_key,))
    
    if existing:
        return existing
    
    # Conditional update (only if sufficient balance)
    result = db.execute("""
        UPDATE accounts 
        SET balance = balance - ? 
        WHERE account_id = ? AND balance >= ?
        RETURNING balance
    """, (amount, from_account, amount))
    
    if result.rowcount == 0:
        raise InsufficientFundsError()
    
    # Credit receiving account
    db.execute("""
        UPDATE accounts 
        SET balance = balance + ? 
        WHERE account_id = ?
    """, (amount, to_account))
    
    # Record transaction
    db.insert("transactions", {
        "idempotency_key": idempotency_key,
        "from_account": from_account,
        "to_account": to_account,
        "amount": amount
    })
    
    return {"status": "success"}
```

---

### Q33: How do you implement multi-step idempotent workflows?
**Answer**: Track workflow state and make each step idempotent.

```python
from enum import Enum

class WorkflowState(Enum):
    PENDING = "pending"
    INVENTORY_RESERVED = "inventory_reserved"
    PAYMENT_CHARGED = "payment_charged"
    ORDER_CONFIRMED = "order_confirmed"
    COMPLETED = "completed"

class OrderWorkflow:
    def execute(self, idempotency_key, order_data):
        # Get or create workflow state
        state = self.get_state(idempotency_key)
        
        if state.status == WorkflowState.COMPLETED:
            return state.result
        
        # Step 1: Reserve inventory (idempotent)
        if state.status in [WorkflowState.PENDING]:
            self.reserve_inventory(idempotency_key, order_data)
            self.update_state(idempotency_key, WorkflowState.INVENTORY_RESERVED)
        
        # Step 2: Charge payment (idempotent)
        if state.status in [WorkflowState.INVENTORY_RESERVED]:
            self.charge_payment(idempotency_key, order_data)
            self.update_state(idempotency_key, WorkflowState.PAYMENT_CHARGED)
        
        # Step 3: Confirm order (idempotent)
        if state.status in [WorkflowState.PAYMENT_CHARGED]:
            result = self.confirm_order(idempotency_key, order_data)
            self.update_state(
                idempotency_key,
                WorkflowState.COMPLETED,
                result=result
            )
        
        return self.get_state(idempotency_key).result
    
    def get_state(self, idempotency_key):
        state = db.query("""
            SELECT status, result FROM workflow_state 
            WHERE idempotency_key = ?
        """, (idempotency_key,))
        
        if not state:
            # Create initial state
            db.insert("workflow_state", {
                "idempotency_key": idempotency_key,
                "status": WorkflowState.PENDING.value
            })
            return WorkflowState.PENDING
        
        return state
```

---

### Q34: How do you handle clock skew in distributed idempotency?
**Answer**: Use logical clocks (vector clocks, Lamport timestamps) instead of wall clocks.

```python
# Problem: Wall clock timestamps unreliable
def is_expired(timestamp):
    # ❌ Servers may have different times
    return time.time() > timestamp + TTL

# Solution: Use monotonic counters
class LogicalClock:
    def __init__(self):
        self.counter = 0
    
    def tick(self):
        self.counter += 1
        return self.counter
    
    def update(self, received_time):
        self.counter = max(self.counter, received_time) + 1
        return self.counter

# Usage with idempotency
def process_with_logical_clock(idempotency_key, data, timestamp):
    stored = redis.hgetall(idempotency_key)
    
    if stored:
        stored_timestamp = int(stored['timestamp'])
        if timestamp <= stored_timestamp:
            # Already processed (logical time)
            return stored['result']
    
    # Process and store with logical timestamp
    result = process(data)
    redis.hset(idempotency_key, mapping={
        "result": result,
        "timestamp": timestamp
    })
    return result
```

---

### Q35: How do you implement idempotency for batch operations?
**Answer**: Track batch ID and individual item IDs.

```python
def process_batch(batch_id, items):
    # Check if batch already processed
    batch_state = redis.hgetall(f"batch:{batch_id}")
    
    if batch_state and batch_state['status'] == 'completed':
        return json.loads(batch_state['results'])
    
    # Initialize batch tracking
    redis.hset(f"batch:{batch_id}", "status", "processing")
    results = []
    
    for item in items:
        item_id = f"{batch_id}:{item['id']}"
        
        # Each item processed idempotently
        if redis.exists(f"item:{item_id}"):
            result = json.loads(redis.get(f"item:{item_id}"))
        else:
            result = process_item(item)
            redis.setex(f"item:{item_id}", 3600, json.dumps(result))
        
        results.append(result)
    
    # Mark batch complete
    redis.hset(f"batch:{batch_id}", mapping={
        "status": "completed",
        "results": json.dumps(results)
    })
    redis.expire(f"batch:{batch_id}", 3600)
    
    return results
```

---

### Q36: What is the Outbox pattern and how does it relate to idempotency?
**Answer**: Ensures atomic state change + event publishing.

```python
# Problem: State saved but event not published (or vice versa)
def create_order(order_data):
    order = db.insert("orders", order_data)  # ✅ Saved
    event_bus.publish(OrderCreatedEvent(order))  # ❌ May fail
    return order

# Solution: Outbox pattern
def create_order_with_outbox(idempotency_key, order_data):
    with db.transaction():
        # Check idempotency
        existing = db.query("""
            SELECT order_id FROM orders WHERE idempotency_key = ?
        """, (idempotency_key,))
        
        if existing:
            return existing
        
        # Insert order
        order = db.insert("orders", {
            **order_data,
            "idempotency_key": idempotency_key
        })
        
        # Insert event to outbox (atomic with order)
        db.insert("outbox", {
            "event_id": str(uuid.uuid4()),
            "event_type": "OrderCreated",
            "aggregate_id": order.id,
            "payload": json.dumps(order)
        })
    
    return order

# Separate process publishes from outbox
def outbox_processor():
    while True:
        events = db.query("SELECT * FROM outbox ORDER BY created_at LIMIT 100")
        
        for event in events:
            # Publish event (idempotent with event_id)
            event_bus.publish(event.event_id, event.payload)
            
            # Remove from outbox
            db.delete("outbox", event.id)
        
        time.sleep(1)
```

---

### Q37: How do you implement idempotency for webhooks?
**Answer**: Deduplicate by webhook ID and signature.

```python
@app.post("/webhooks/stripe")
def handle_stripe_webhook(request):
    # Extract webhook ID (Stripe provides this)
    webhook_id = request.headers.get('Stripe-Webhook-Id')
    signature = request.headers.get('Stripe-Signature')
    
    # Verify signature
    if not verify_webhook_signature(request.body, signature):
        raise HTTPException(401, "Invalid signature")
    
    # Check if already processed (7 day window)
    if redis.exists(f"webhook:{webhook_id}"):
        logger.info(f"Webhook {webhook_id} already processed")
        return {"status": "ok"}
    
    # Process webhook
    event_data = request.json()
    handle_stripe_event(event_data)
    
    # Mark as processed
    redis.setex(f"webhook:{webhook_id}", 604800, "1")
    
    return {"status": "ok"}
```

---

### Q38-Q45: Quick-fire Advanced Questions

**Q38: Can DELETE be non-idempotent?**
A: Yes, if implemented poorly. DELETE should be idempotent (first call deletes, subsequent calls have no effect). Returning different status codes (200 vs 404) is fine and still idempotent.

**Q39: How do you handle idempotency in GraphQL?**
A: Use mutation IDs:
```graphql
mutation CreateOrder($input: OrderInput!, $idempotencyKey: String!) {
  createOrder(input: $input, idempotencyKey: $idempotencyKey) {
    id
    status
  }
}
```

**Q40: What's the CAP theorem's role in idempotency?**
A: In partitioned systems, choose between consistency (strong idempotency) or availability (eventual idempotency). Most systems choose availability + eventual consistency.

**Q41: How do you implement idempotency for streaming data?**
A: Use watermarks and event-time processing:
```python
# Track processed event IDs within time window
def process_stream_event(event):
    if is_within_watermark(event.timestamp):
        if not is_processed(event.id):
            process(event)
            mark_processed(event.id)
```

**Q42: What's idempotency's role in retry policies?**
A: Idempotency enables safe retries. Exponential backoff + idempotency = reliable systems:
```python
@retry(max_attempts=3, backoff=exponential)
def idempotent_api_call(key, data):
    return process_with_idempotency(key, data)
```

**Q43: How do you handle idempotency across regions?**
A: Use global idempotency keys with region-aware storage:
```python
# Store in multiple regions
def multi_region_idempotency(key, func):
    # Check local region first
    if local_cache.exists(key):
        return local_cache.get(key)
    
    # Check global store
    if global_db.exists(key):
        result = global_db.get(key)
        local_cache.set(key, result)  # Cache locally
        return result
    
    # Process and replicate
    result = func()
    global_db.set(key, result)
    return result
```

**Q44: What's the difference between deduplication window and idempotency TTL?**
A: Deduplication window is how far back you check for duplicates. TTL is how long you store idempotency data. Window ≤ TTL.

**Q45: How do you audit idempotency key usage?**
A: Log all key operations:
```python
def audit_idempotency(key, action, result):
    audit_log.insert({
        "key": key,
        "action": action,
        "result": result,
        "timestamp": datetime.utcnow(),
        "user_id": current_user.id
    })
```

---

## System Design

### Q46: Design an idempotent payment system
**Answer**: Multi-layer approach with idempotency keys.

**Architecture**:
```
Client
  ↓ (Idempotency-Key header)
API Gateway
  ↓ (validate + forward key)
Payment Service
  ↓ (check cache)
Redis Cache (fast path)
  ↓ (check DB)
PostgreSQL (source of truth)
  ↓ (process if new)
Payment Provider (Stripe)
  ↓ (with provider's idempotency)
```

**Implementation highlights**:
1. Client generates UUID as idempotency key
2. API Gateway validates key format
3. Payment Service checks Redis first (< 10ms)
4. Falls back to PostgreSQL for older requests
5. Uses distributed lock during processing
6. Stores request hash to detect conflicts
7. Forwards key to Stripe for double safety
8. Caches response for 24 hours
9. Returns cached response for duplicates

**Key tables**:
```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY,
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    stripe_charge_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_idempotency_key ON payments(idempotency_key);
```

---

### Q47: Design an idempotent order processing system
**Answer**: Workflow-based with state tracking.

**State machine**:
```
PENDING → VALIDATED → INVENTORY_RESERVED → PAYMENT_PROCESSED → CONFIRMED → SHIPPED
```

**Each transition is idempotent**:
```python
class OrderStateMachine:
    def process(self, idempotency_key, order_data):
        state = self.get_state(idempotency_key)
        
        while state != OrderState.CONFIRMED:
            if state == OrderState.PENDING:
                self.validate_order(idempotency_key, order_data)
                state = self.transition(idempotency_key, OrderState.VALIDATED)
            
            elif state == OrderState.VALIDATED:
                self.reserve_inventory(idempotency_key, order_data)
                state = self.transition(idempotency_key, OrderState.INVENTORY_RESERVED)
            
            elif state == OrderState.INVENTORY_RESERVED:
                self.process_payment(idempotency_key, order_data)
                state = self.transition(idempotency_key, OrderState.PAYMENT_PROCESSED)
            
            elif state == OrderState.PAYMENT_PROCESSED:
                self.confirm_order(idempotency_key)
                state = self.transition(idempotency_key, OrderState.CONFIRMED)
        
        return self.get_order(idempotency_key)
```

---

### Q48: Design an idempotent messaging system
**Answer**: Track message IDs with time-based expiry.

**Components**:
1. **Publisher**: Assigns unique message ID
2. **Queue**: Ensures at-least-once delivery
3. **Consumer**: Deduplicates by message ID
4. **Tracker**: Redis set of processed IDs

**Implementation**:
```python
class IdempotentMessageConsumer:
    def __init__(self):
        self.redis = redis.Redis()
        self.ttl = 86400  # 24 hours
    
    def consume(self, queue_name):
        while True:
            messages = self.queue.receive(queue_name, batch_size=10)
            
            for msg in messages:
                if self.is_processed(msg.id):
                    self.queue.ack(msg)
                    continue
                
                try:
                    self.handle_message(msg)
                    self.mark_processed(msg.id)
                    self.queue.ack(msg)
                except Exception as e:
                    logger.error(f"Failed to process {msg.id}: {e}")
                    # Will be redelivered
    
    def is_processed(self, message_id):
        return self.redis.sismember("processed_messages", message_id)
    
    def mark_processed(self, message_id):
        self.redis.sadd("processed_messages", message_id)
        # Cleanup old IDs periodically
```

---

### Q49: How would you scale idempotency checking?
**Answer**: Multi-tier caching + sharding.

**Tier 1: Application memory** (fastest)
```python
local_cache = TTLCache(maxsize=10000, ttl=300)  # 5 min
```

**Tier 2: Redis cluster** (fast, distributed)
```python
redis_cluster = RedisCluster(nodes=...)
```

**Tier 3: Database** (source of truth, sharded)
```python
# Shard by hash of idempotency key
shard = hash(idempotency_key) % num_shards
db = databases[shard]
```

**Lookup flow**:
```python
def check_idempotency(key):
    # L1: Local cache
    if key in local_cache:
        return local_cache[key]
    
    # L2: Redis
    result = redis_cluster.get(key)
    if result:
        local_cache[key] = result
        return result
    
    # L3: Database
    shard = hash(key) % num_shards
    result = databases[shard].query(
        "SELECT * FROM idempotency WHERE key = ?", key
    )
    if result:
        redis_cluster.setex(key, 3600, result)
        local_cache[key] = result
    
    return result
```

---

### Q50: Design idempotency for a multi-tenant system
**Answer**: Isolate idempotency keys per tenant.

**Key structure**:
```python
idempotency_key = f"tenant_{tenant_id}:payment:{client_key}"
```

**Tenant-aware checking**:
```python
def process_tenant_payment(tenant_id, idempotency_key, amount):
    # Scope key to tenant
    scoped_key = f"tenant_{tenant_id}:{idempotency_key}"
    
    # Check tenant's idempotency store
    cached = tenant_cache.get(tenant_id, scoped_key)
    if cached:
        return cached
    
    # Process with tenant context
    with tenant_context(tenant_id):
        result = process_payment(amount)
        tenant_cache.set(tenant_id, scoped_key, result, ttl=86400)
        return result
```

**Database partitioning**:
```sql
-- Separate schema per tenant
CREATE SCHEMA tenant_123;
CREATE TABLE tenant_123.idempotency_keys (...);

-- Or partition by tenant_id
CREATE TABLE idempotency_keys (
    tenant_id INTEGER,
    idempotency_key VARCHAR(255),
    ...
    PRIMARY KEY (tenant_id, idempotency_key)
) PARTITION BY HASH (tenant_id);
```

---

## Troubleshooting

### Q51-Q60: Common Issues

**Q51: What if idempotency key expires mid-processing?**
A: Store "processing" state with timestamp, extend TTL:
```python
# Extend TTL while processing
redis.expire(key, original_ttl)
```

**Q52: How do you handle stuck operations?**
A: Monitor processing time, auto-retry after timeout:
```python
state = redis.hgetall(key)
if state['status'] == 'processing':
    if time.time() - state['started_at'] > 300:
        # Retry or alert
        retry_operation(key)
```

**Q53: What if cache and database diverge?**
A: Database is source of truth, invalidate cache:
```python
# On write
db.insert(...)
cache.delete(key)  # Force reload from DB
```

**Q54: How do you handle partial failures in multi-step workflows?**
A: Use compensating transactions (saga pattern) - see Q24.

**Q55: What if client never receives response?**
A: Client retries with same key, gets cached result - that's the point of idempotency!

**Q56: How do you debug idempotency issues?**
A: Comprehensive logging:
```python
logger.info("idempotency_check", 
    key=key,
    cache_hit=cache_hit,
    db_hit=db_hit,
    processing_time=duration)
```

**Q57: What if two clients use same key accidentally?**
A: Validate payload hash, return 422 Conflict if different.

**Q58: How do you clean up old idempotency keys?**
A: Use TTL + periodic cleanup:
```python
# TTL on cache
redis.setex(key, 86400, value)

# Periodic DB cleanup
DELETE FROM idempotency_keys 
WHERE created_at < NOW() - INTERVAL '30 days'
```

**Q59: What if distributed lock times out?**
A: Operation may be retried - ensure idempotent:
```python
with distributed_lock(key, timeout=30):
    # Still check if processed
    if not exists(key):
        process()
```

**Q60: How do you test idempotency in production?**
A: Chaos engineering + monitoring:
```python
# Inject duplicate requests
if random.random() < 0.01:  # 1% of requests
    duplicate_request()

# Monitor metrics
assert duplicate_charge_rate < 0.001  # < 0.1%
```

---

## Summary

### Key Principles
1. **Check before processing**: Always verify idempotency key first
2. **Atomic operations**: Use transactions, locks, or constraints
3. **Store responses**: Cache full responses, not just flags
4. **Validate payloads**: Detect conflicting requests
5. **Set appropriate TTLs**: Balance storage vs safety
6. **Handle failures**: Track processing state
7. **Test thoroughly**: Concurrency, chaos, integration tests
8. **Monitor**: Metrics, logs, alerts

### Common Patterns
- **Idempotency keys**: Client-generated UUIDs
- **Distributed locks**: Redis SETNX or database locks
- **Database constraints**: Unique indexes
- **State machines**: Track workflow progress
- **Event sourcing**: Immutable event log

### Best Practices
- Always use idempotency for financial operations
- Client generates keys for POST requests
- Scope keys appropriately (per-tenant, per-user)
- Use hybrid caching (Redis + database)
- Implement comprehensive logging
- Set up monitoring and alerts

---

**Total Questions: 60+** covering fundamentals through advanced system design and troubleshooting.

**Next**: See `03_PATTERNS.md` for implementation patterns and `04_BEST_PRACTICES.md` for production guidelines.
