# Idempotency - Complete Theory Guide

## Table of Contents
1. [What is Idempotency?](#what-is-idempotency)
2. [Why Idempotency Matters](#why-idempotency-matters)
3. [Types of Idempotency](#types-of-idempotency)
4. [HTTP Methods and Idempotency](#http-methods-and-idempotency)
5. [Implementing Idempotency](#implementing-idempotency)
6. [Common Challenges](#common-challenges)
7. [Real-World Examples](#real-world-examples)

---

## What is Idempotency?

### Definition
An operation is **idempotent** if performing it multiple times has the same effect as performing it once.

**Mathematical Definition**:
```
f(f(x)) = f(x)
```

### Simple Examples

**✅ Idempotent Operations**:
```python
# Setting a value
x = 10  # No matter how many times, x is always 10

# Absolute value
abs(-5) = 5
abs(abs(-5)) = 5  # Same result

# SQL UPDATE with fixed value
UPDATE users SET status = 'active' WHERE id = 123
# Running multiple times: status is still 'active'

# DELETE operation
DELETE FROM orders WHERE id = 456
# First time: deletes the order
# Subsequent times: no change (already deleted)
```

**❌ Non-Idempotent Operations**:
```python
# Incrementing a value
x = x + 1  # Result changes each time

# Appending to list
list.append(item)  # List grows each time

# SQL INSERT
INSERT INTO orders (user_id, amount) VALUES (123, 100)
# Each execution creates a new order

# Charging a credit card
charge_card(card_number, amount)  # Multiple charges!
```

### Key Characteristics

1. **Same Input → Same Output**: Given identical inputs, produces identical results
2. **No Side Effects**: Additional executions don't cause additional changes
3. **Safe Retries**: Can be safely retried on failure
4. **Eventual Consistency**: Multiple operations converge to same state

---

## Why Idempotency Matters

### 1. Network Failures

```
Client → Request → [Network Issue] → Server
       ↓ Timeout
       Retry → Request → Success
```

**Problem**: Server may have received first request
**Solution**: Idempotent operations make retries safe

### 2. Duplicate Messages

```
Message Queue: [Message 1, Message 1, Message 2]
                   ↓         ↓        ↓
              Process once, once, or twice?
```

**Problem**: At-least-once delivery guarantees duplicates
**Solution**: Idempotent processing handles duplicates safely

### 3. User Actions

```
User double-clicks "Submit Payment" button
    ↓               ↓
Request 1        Request 2
    ↓               ↓
Charge once or twice?
```

**Problem**: Accidental duplicate submissions
**Solution**: Idempotent API prevents double charging

### 4. Distributed Systems

```
Service A → Service B → Service C
    ↓           ↓           ↓
  Retry     Retry      Retry
```

**Problem**: Cascading retries in microservices
**Solution**: Each service implements idempotency

### Real-World Impact

#### Without Idempotency
- 💸 Customer charged $500 twice
- 📦 Order created twice, double shipping
- 📧 Duplicate email notifications
- 📊 Incorrect analytics/metrics
- 🚨 Data inconsistency

#### With Idempotency
- ✅ Safe retries
- ✅ Correct business logic
- ✅ Consistent data
- ✅ Better user experience
- ✅ System reliability

---

## Types of Idempotency

### 1. Natural Idempotency

Operations that are inherently idempotent.

```python
# Setting absolute values
user.status = "active"
user.email = "user@example.com"

# Boolean flags
is_deleted = True
is_verified = False

# Overwriting data
cache.set("key", "value")

# SQL UPDATE with fixed value
UPDATE products SET price = 99.99 WHERE id = 123
```

**Characteristics**:
- No additional implementation needed
- Based on operation semantics
- Examples: PUT, DELETE (if implemented correctly)

### 2. Idempotency Keys

Client-generated unique identifiers to detect duplicates.

```python
# Client generates unique key
idempotency_key = "order_2024_user123_abc789"

# Server checks if key was used before
if redis.exists(idempotency_key):
    # Return cached response
    return redis.get(f"{idempotency_key}_response")
else:
    # Process request
    result = process_payment(...)
    # Store result with key
    redis.setex(idempotency_key, 3600, result)
    return result
```

**Characteristics**:
- Client-side generated
- Server-side validation
- Time-limited (TTL)
- Examples: Payment APIs, order creation

### 3. Conditional Operations

Operations that only execute if conditions are met.

```python
# SQL conditional update
UPDATE accounts 
SET balance = balance - 100 
WHERE id = 123 AND balance >= 100

# Only updates if sufficient balance
# Repeated execution: fails after first success

# Redis conditional set
redis.setnx("lock_key", "value")  # Set if Not eXists
# Only sets on first call
```

**Characteristics**:
- Built-in guards
- Database-level guarantees
- Examples: Compare-and-swap, optimistic locking

### 4. Versioning

Track operation versions to detect duplicates.

```python
# Include version number
{
    "order_id": "123",
    "version": 5,
    "status": "shipped"
}

# Server checks version
current_version = get_order_version(order_id)
if request_version <= current_version:
    # Already processed
    return cached_response
else:
    # Process new version
    process_order_update(...)
```

**Characteristics**:
- Sequential versioning
- Optimistic concurrency control
- Examples: Event sourcing, CQRS

---

## HTTP Methods and Idempotency

### Idempotent HTTP Methods

#### GET
```http
GET /api/users/123
```
- ✅ **Idempotent**: Multiple calls return same data
- ✅ **Safe**: No side effects
- Use: Retrieving data

#### PUT
```http
PUT /api/users/123
{
    "name": "John Doe",
    "email": "john@example.com"
}
```
- ✅ **Idempotent**: Multiple calls result in same state
- ⚠️ **Not Safe**: Modifies data
- Use: Update (replace entire resource)

#### DELETE
```http
DELETE /api/users/123
```
- ✅ **Idempotent**: Multiple calls have same effect (resource deleted)
- ⚠️ **Not Safe**: Modifies data
- Use: Delete resource

**Note**: First call returns 200, subsequent calls may return 404 (acceptable)

#### PATCH
```http
PATCH /api/users/123
{
    "status": "active"
}
```
- ⚠️ **Conditionally Idempotent**: Depends on implementation
- Use: Partial update

### Non-Idempotent HTTP Methods

#### POST
```http
POST /api/orders
{
    "user_id": 123,
    "items": [...],
    "total": 99.99
}
```
- ❌ **Not Idempotent**: Each call creates new resource
- Use: Create resource

**Making POST Idempotent**:
```http
POST /api/orders
Idempotency-Key: order_2024_user123_abc789

{
    "user_id": 123,
    "items": [...],
    "total": 99.99
}
```

### HTTP Status Codes for Idempotency

```
First Request:
POST /api/payments
Idempotency-Key: pay_123
→ 201 Created

Duplicate Request:
POST /api/payments
Idempotency-Key: pay_123
→ 200 OK (or 201 with same response)

Conflicting Request:
POST /api/payments
Idempotency-Key: pay_123 (different payload)
→ 422 Unprocessable Entity
```

---

## Implementing Idempotency

### 1. Using Idempotency Keys

#### Architecture
```
1. Client generates unique key (UUID)
2. Client sends request with key in header
3. Server checks if key exists in cache/database
4. If exists: return cached response
5. If new: process request, store result with key
6. Return response to client
```

#### Implementation Pattern
```python
from fastapi import FastAPI, Header, HTTPException
import redis
import uuid

app = FastAPI()
redis_client = redis.Redis()

@app.post("/api/payments")
async def create_payment(
    amount: float,
    idempotency_key: str = Header(None)
):
    # Validate key provided
    if not idempotency_key:
        raise HTTPException(400, "Idempotency-Key required")
    
    # Check if already processed
    cached = redis_client.get(f"idem:{idempotency_key}")
    if cached:
        return json.loads(cached)
    
    # Process payment (not shown)
    result = process_payment(amount)
    
    # Cache result (24 hour TTL)
    redis_client.setex(
        f"idem:{idempotency_key}",
        86400,
        json.dumps(result)
    )
    
    return result
```

#### Key Generation (Client-side)
```python
import uuid
from datetime import datetime

# Option 1: UUID
idempotency_key = str(uuid.uuid4())
# "f47ac10b-58cc-4372-a567-0e02b2c3d479"

# Option 2: Meaningful key
idempotency_key = f"order_{user_id}_{timestamp}_{nonce}"
# "order_123_20240813_abc123"

# Option 3: Hash of request
import hashlib
request_hash = hashlib.sha256(
    json.dumps(request_data, sort_keys=True).encode()
).hexdigest()
```

### 2. Using Database Constraints

#### Unique Constraints
```sql
-- Prevent duplicate orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(10,2),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_idempotency_key ON orders(idempotency_key);
```

```python
# Attempt to insert
try:
    cursor.execute("""
        INSERT INTO orders (user_id, idempotency_key, amount, status)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (user_id, idempotency_key, amount, 'pending'))
    order_id = cursor.fetchone()[0]
    conn.commit()
except IntegrityError:
    # Idempotency key already exists
    cursor.execute("""
        SELECT id, status, amount 
        FROM orders 
        WHERE idempotency_key = %s
    """, (idempotency_key,))
    existing_order = cursor.fetchone()
    return existing_order
```

### 3. Using Distributed Locks

```python
import redis
from contextlib import contextmanager

redis_client = redis.Redis()

@contextmanager
def distributed_lock(lock_key, timeout=30):
    """Acquire distributed lock using Redis"""
    lock_id = str(uuid.uuid4())
    
    # Try to acquire lock
    acquired = redis_client.set(
        lock_key,
        lock_id,
        nx=True,  # Only set if not exists
        ex=timeout  # Expiry in seconds
    )
    
    if not acquired:
        raise Exception("Could not acquire lock")
    
    try:
        yield
    finally:
        # Release lock (with Lua script for atomicity)
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        redis_client.eval(lua_script, 1, lock_key, lock_id)

# Usage
with distributed_lock(f"payment:{idempotency_key}"):
    # Process payment
    result = charge_credit_card(...)
```

### 4. Using Event Sourcing

```python
# Store events instead of current state
events = [
    {"type": "OrderCreated", "order_id": "123", "timestamp": "..."},
    {"type": "PaymentProcessed", "order_id": "123", "timestamp": "..."},
    {"type": "OrderShipped", "order_id": "123", "timestamp": "..."}
]

# Each event has unique ID (idempotent)
def process_event(event_id, event_data):
    # Check if event already processed
    if event_store.exists(event_id):
        return  # Skip duplicate
    
    # Process event
    handle_event(event_data)
    
    # Mark as processed
    event_store.add(event_id, event_data)
```

---

## Common Challenges

### 1. Race Conditions

**Problem**: Multiple requests arrive simultaneously
```
Request A ──→ Check (not found) ──→ Process ──→ Save
Request B ──→ Check (not found) ──→ Process ──→ Save
         Both processed! ❌
```

**Solution**: Use locks or database constraints
```python
# With lock
with distributed_lock(idempotency_key):
    if not exists(idempotency_key):
        process()

# With database
INSERT ... ON CONFLICT DO NOTHING
```

### 2. Partial Failures

**Problem**: Request processed but response lost
```
Client → Request → Server (process success)
       ← [Network Error] ← Response lost
Client → Retry → Server (already processed)
       ← What to return?
```

**Solution**: Store both processing state and response
```python
# Store processing state
redis.hset(idempotency_key, {
    "status": "processing",
    "started_at": timestamp
})

# After success, store result
redis.hset(idempotency_key, {
    "status": "completed",
    "result": json.dumps(result),
    "completed_at": timestamp
})

# On retry
state = redis.hgetall(idempotency_key)
if state["status"] == "completed":
    return json.loads(state["result"])
elif state["status"] == "processing":
    # Check if stuck, retry or wait
```

### 3. Conflicting Requests

**Problem**: Same idempotency key, different payloads
```
Request 1: idempotency_key=abc123, amount=100
Request 2: idempotency_key=abc123, amount=200
```

**Solution**: Validate payload matches
```python
# Store request hash
request_hash = hashlib.sha256(
    json.dumps(request_data, sort_keys=True).encode()
).hexdigest()

stored_hash = redis.hget(idempotency_key, "request_hash")
if stored_hash and stored_hash != request_hash:
    raise HTTPException(
        422,
        "Idempotency key reused with different payload"
    )
```

### 4. Key Expiration

**Problem**: When to expire idempotency keys?

**Solution**: Use business logic to determine TTL
```python
# Payment: 24 hours (user might retry same day)
TTL_PAYMENT = 86400

# Order: 1 hour (checkout session timeout)
TTL_ORDER = 3600

# Webhook: 7 days (allow for retries over days)
TTL_WEBHOOK = 604800

redis.setex(idempotency_key, TTL_PAYMENT, result)
```

---

## Real-World Examples

### Example 1: Payment Processing

```python
class PaymentService:
    def process_payment(
        self,
        user_id: int,
        amount: float,
        idempotency_key: str
    ):
        # Check cache
        cached = self.cache.get(f"payment:{idempotency_key}")
        if cached:
            return cached
        
        # Acquire lock
        with self.lock(f"payment_lock:{idempotency_key}"):
            # Double-check (after acquiring lock)
            cached = self.cache.get(f"payment:{idempotency_key}")
            if cached:
                return cached
            
            # Check database
            existing = self.db.query(
                "SELECT * FROM payments WHERE idempotency_key = ?",
                idempotency_key
            )
            if existing:
                return existing
            
            # Process payment
            result = self.charge_card(user_id, amount)
            
            # Save to database
            self.db.insert("payments", {
                "user_id": user_id,
                "amount": amount,
                "idempotency_key": idempotency_key,
                "status": result.status
            })
            
            # Cache result
            self.cache.setex(
                f"payment:{idempotency_key}",
                86400,
                result
            )
            
            return result
```

### Example 2: Order Creation

```python
@app.post("/api/orders")
async def create_order(
    order_data: OrderCreate,
    idempotency_key: str = Header(...)
):
    # Generate order ID from idempotency key
    # This ensures same order ID for duplicates
    order_id = hashlib.sha256(idempotency_key.encode()).hexdigest()[:16]
    
    try:
        # Attempt to insert with unique constraint
        order = await db.orders.insert_one({
            "_id": order_id,
            "idempotency_key": idempotency_key,
            "user_id": order_data.user_id,
            "items": order_data.items,
            "total": order_data.total,
            "status": "pending",
            "created_at": datetime.utcnow()
        })
        
        # Process order
        await process_order_async(order_id)
        
        return {"order_id": order_id, "status": "created"}
        
    except DuplicateKeyError:
        # Idempotency key already used
        existing_order = await db.orders.find_one({
            "idempotency_key": idempotency_key
        })
        return {"order_id": existing_order["_id"], "status": "already_exists"}
```

### Example 3: Message Queue Processing

```python
class MessageHandler:
    def __init__(self):
        self.processed_messages = set()  # In production: use Redis set
    
    def process_message(self, message):
        message_id = message["id"]
        
        # Check if already processed
        if message_id in self.processed_messages:
            logger.info(f"Duplicate message {message_id}, skipping")
            return
        
        try:
            # Process message
            self.handle_message(message)
            
            # Mark as processed
            self.processed_messages.add(message_id)
            
            # Acknowledge message
            queue.ack(message)
            
        except Exception as e:
            logger.error(f"Error processing {message_id}: {e}")
            # Don't acknowledge, will be redelivered
            raise
```

---

## Summary

### Key Takeaways

1. **Idempotency is Critical**: Essential for reliable distributed systems
2. **Multiple Approaches**: Keys, constraints, locks, versioning
3. **Not Free**: Requires additional storage and complexity
4. **Trade-offs**: Performance vs correctness
5. **Business Logic**: TTL and retry policies depend on use case

### When to Use Idempotency

✅ **Use idempotency for**:
- Payment processing
- Order creation
- State changes (status updates)
- External API calls
- Message queue processing
- Retry-able operations

❌ **Not needed for**:
- Pure read operations (GET)
- Analytics/logging (if duplicates acceptable)
- Fire-and-forget operations
- Operations with natural deduplication

### Best Practices

1. **Always** use idempotency for financial operations
2. **Client-generated** keys for POST requests
3. **Store** both request and response
4. **Validate** payload matches for duplicate keys
5. **Set appropriate** TTL based on business needs
6. **Monitor** idempotency key usage and conflicts
7. **Document** your idempotency strategy
8. **Test** with concurrent requests

---

**Next**: Read `02_INTERVIEW_QA.md` for interview questions, and `03_PATTERNS.md` for implementation patterns.
