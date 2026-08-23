# Idempotency Patterns & Anti-Patterns

## Table of Contents
1. [Implementation Patterns](#implementation-patterns)
2. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
3. [Design Patterns](#design-patterns)
4. [Testing Patterns](#testing-patterns)

---

## Implementation Patterns

### Pattern 1: Check-Process-Store

**Intent**: Simple idempotency for stateless operations

**Structure**:
```python
def idempotent_operation(key, operation_func, *args):
    # 1. Check
    cached = cache.get(key)
    if cached:
        return cached
    
    # 2. Process
    result = operation_func(*args)
    
    # 3. Store
    cache.set(key, result, ttl=86400)
    
    return result
```

**When to use**:
- Simple operations
- No state transitions
- Fast execution (< 1s)

**Pros**:
- Simple to implement
- Low overhead
- Suitable for most use cases

**Cons**:
- Race condition without locks
- No partial failure handling

---

### Pattern 2: Check-Lock-Process-Store

**Intent**: Prevent race conditions with distributed locks

**Structure**:
```python
def idempotent_with_lock(key, operation_func, *args):
    # 1. Check (fast path)
    cached = cache.get(key)
    if cached:
        return cached
    
    # 2. Lock
    with distributed_lock(key, timeout=30):
        # 3. Double-check
        cached = cache.get(key)
        if cached:
            return cached
        
        # 4. Process
        result = operation_func(*args)
        
        # 5. Store
        cache.set(key, result, ttl=86400)
    
    return result
```

**When to use**:
- Concurrent requests expected
- Critical operations (payments, orders)
- Longer processing time

**Pros**:
- Prevents race conditions
- Guarantees single execution

**Cons**:
- Lock overhead
- Potential for deadlocks

---

### Pattern 3: State-Tracked Processing

**Intent**: Handle partial failures and retries

**Structure**:
```python
class ProcessingState(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

def stateful_idempotent_operation(key, operation_func, *args):
    # Check state
    state = get_state(key)
    
    if state == ProcessingState.COMPLETED:
        return get_result(key)
    
    if state == ProcessingState.PROCESSING:
        # Check if stuck
        if is_stuck(key):
            # Retry
            pass
        else:
            raise StillProcessingError()
    
    # Mark as processing
    set_state(key, ProcessingState.PROCESSING, {
        "started_at": time.time(),
        "request_hash": hash(args)
    })
    
    try:
        # Process
        result = operation_func(*args)
        
        # Mark completed
        set_state(key, ProcessingState.COMPLETED, {
            "result": result,
            "completed_at": time.time()
        })
        
        return result
        
    except Exception as e:
        set_state(key, ProcessingState.FAILED, {
            "error": str(e),
            "failed_at": time.time()
        })
        raise
```

**When to use**:
- Long-running operations
- Network calls to external services
- Operations that may timeout

**Pros**:
- Handles partial failures
- Supports retries
- Provides visibility into processing state

**Cons**:
- More complex
- Requires state storage

---

### Pattern 4: Database-Backed Idempotency

**Intent**: Use database constraints for atomicity

**Structure**:
```python
def db_idempotent_operation(conn, key, operation_func, *args):
    cursor = conn.cursor()
    
    # Try to insert idempotency record
    try:
        cursor.execute("""
            INSERT INTO idempotency_keys (key, status, request_hash)
            VALUES (%s, 'processing', %s)
        """, (key, hash(args)))
        conn.commit()
    except IntegrityError:
        # Already exists
        cursor.execute("""
            SELECT status, result FROM idempotency_keys WHERE key = %s
        """, (key,))
        row = cursor.fetchone()
        
        if row['status'] == 'completed':
            return row['result']
        elif row['status'] == 'processing':
            raise StillProcessingError()
    
    try:
        # Process
        result = operation_func(*args)
        
        # Update record
        cursor.execute("""
            UPDATE idempotency_keys 
            SET status = 'completed', result = %s, completed_at = NOW()
            WHERE key = %s
        """, (json.dumps(result), key))
        conn.commit()
        
        return result
        
    except Exception as e:
        cursor.execute("""
            UPDATE idempotency_keys SET status = 'failed' WHERE key = %s
        """, (key,))
        conn.commit()
        raise
```

**When to use**:
- Need durability
- Audit trail required
- Already using database

**Pros**:
- Durable
- ACID guarantees
- Audit trail

**Cons**:
- Slower than cache
- Database load

---

### Pattern 5: Hybrid Cache + Database

**Intent**: Fast lookups with durable storage

**Structure**:
```python
def hybrid_idempotent_operation(key, operation_func, *args):
    # Fast path: Cache
    cached = cache.get(key)
    if cached:
        return cached
    
    # Slow path: Database
    db_result = db.query("SELECT result FROM idempotency WHERE key = ?", key)
    if db_result:
        # Warm cache
        cache.setex(key, 3600, db_result)
        return db_result
    
    # Not found - process
    with distributed_lock(key):
        # Double-check
        cached = cache.get(key)
        if cached:
            return cached
        
        # Process
        result = operation_func(*args)
        
        # Store in database (source of truth)
        db.insert("idempotency", {
            "key": key,
            "result": json.dumps(result),
            "created_at": datetime.utcnow()
        })
        
        # Cache for fast access
        cache.setex(key, 3600, result)
        
        return result
```

**When to use**:
- High throughput systems
- Need both speed and durability
- Production environments

**Pros**:
- Fast (cache hit)
- Durable (database)
- Best of both worlds

**Cons**:
- More complex
- Cache invalidation challenges

---

### Pattern 6: Request Hash Validation

**Intent**: Detect conflicting requests with same key

**Structure**:
```python
import hashlib
import json

def hash_request(data):
    """Generate stable hash of request data"""
    return hashlib.sha256(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()

def idempotent_with_validation(key, operation_func, request_data):
    request_hash = hash_request(request_data)
    
    # Check existing request
    existing = cache.hgetall(key)
    if existing:
        stored_hash = existing.get('request_hash')
        
        if stored_hash != request_hash:
            # Same key, different request - conflict!
            raise ConflictError(
                "Idempotency key reused with different payload"
            )
        
        # Same request, return cached result
        return json.loads(existing['result'])
    
    # Store request hash
    cache.hset(key, 'request_hash', request_hash)
    cache.hset(key, 'status', 'processing')
    
    # Process
    result = operation_func(request_data)
    
    # Store result
    cache.hset(key, 'result', json.dumps(result))
    cache.hset(key, 'status', 'completed')
    cache.expire(key, 86400)
    
    return result
```

**When to use**:
- User-facing APIs
- Prevent malicious key reuse
- Strict payload validation needed

**Pros**:
- Detects conflicts
- Security enhancement
- Data integrity

**Cons**:
- Extra computation (hashing)
- Slightly more storage

---

### Pattern 7: Multi-Step Workflow (Saga)

**Intent**: Idempotent multi-service operations

**Structure**:
```python
class WorkflowStep(Enum):
    VALIDATE = 1
    RESERVE_INVENTORY = 2
    CHARGE_PAYMENT = 3
    CONFIRM_ORDER = 4
    COMPLETE = 5

class IdempotentWorkflow:
    def execute(self, key, data):
        # Load workflow state
        state = self.get_state(key)
        
        # Resume from last completed step
        while state.current_step < WorkflowStep.COMPLETE:
            if state.current_step == WorkflowStep.VALIDATE:
                self.validate_order(key, data)
                state = self.advance_step(key, WorkflowStep.RESERVE_INVENTORY)
            
            elif state.current_step == WorkflowStep.RESERVE_INVENTORY:
                self.reserve_inventory(key, data)
                state = self.advance_step(key, WorkflowStep.CHARGE_PAYMENT)
            
            elif state.current_step == WorkflowStep.CHARGE_PAYMENT:
                self.charge_payment(key, data)
                state = self.advance_step(key, WorkflowStep.CONFIRM_ORDER)
            
            elif state.current_step == WorkflowStep.CONFIRM_ORDER:
                result = self.confirm_order(key, data)
                state = self.advance_step(key, WorkflowStep.COMPLETE, result)
        
        return state.result
    
    def get_state(self, key):
        state = db.query("SELECT * FROM workflow_state WHERE key = ?", key)
        if not state:
            # Initialize
            state = db.insert("workflow_state", {
                "key": key,
                "current_step": WorkflowStep.VALIDATE.value,
                "created_at": datetime.utcnow()
            })
        return state
    
    def advance_step(self, key, next_step, result=None):
        db.execute("""
            UPDATE workflow_state 
            SET current_step = ?, result = ?, updated_at = NOW()
            WHERE key = ?
        """, (next_step.value, json.dumps(result), key))
        
        return self.get_state(key)
```

**When to use**:
- Multi-service transactions
- Long-running processes
- Compensation needed

**Pros**:
- Resilient to failures
- Can retry any step
- Clear audit trail

**Cons**:
- Complex implementation
- Requires state management

---

### Pattern 8: Event Sourcing with Idempotency

**Intent**: Immutable event log with deduplication

**Structure**:
```python
class EventStore:
    def append(self, event_id, event_type, data):
        # Idempotent append (unique constraint on event_id)
        try:
            self.db.insert("events", {
                "event_id": event_id,
                "event_type": event_type,
                "data": json.dumps(data),
                "timestamp": datetime.utcnow()
            })
            return True
        except IntegrityError:
            # Event already exists (duplicate)
            return False

class OrderAggregate:
    def create_order(self, idempotency_key, order_data):
        event_id = idempotency_key
        
        # Try to append event
        if not event_store.append(event_id, "OrderCreated", order_data):
            # Event already exists, replay to get current state
            return self.replay_events(idempotency_key)
        
        # New event - create order
        order = Order(**order_data)
        return order
    
    def replay_events(self, aggregate_id):
        events = event_store.get_events(aggregate_id)
        order = Order()
        
        for event in events:
            order.apply_event(event)
        
        return order
```

**When to use**:
- Event-driven architectures
- Need full audit trail
- CQRS pattern

**Pros**:
- Complete history
- Time-travel debugging
- Natural idempotency

**Cons**:
- Storage overhead
- Complexity
- Replay performance

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Not Checking Before Processing

**Problem**:
```python
# ❌ Bad - Always processes
def process_payment(key, amount):
    result = charge_card(amount)  # Charges every time!
    cache.set(key, result)  # Too late
    return result
```

**Solution**:
```python
# ✅ Good - Check first
def process_payment(key, amount):
    cached = cache.get(key)
    if cached:
        return cached
    
    result = charge_card(amount)
    cache.set(key, result)
    return result
```

---

### Anti-Pattern 2: Race Conditions

**Problem**:
```python
# ❌ Bad - Race condition
if not cache.exists(key):
    result = expensive_operation()  # Multiple can enter here
    cache.set(key, result)
```

**Solution**:
```python
# ✅ Good - Use lock
with distributed_lock(key):
    if not cache.exists(key):
        result = expensive_operation()
        cache.set(key, result)
```

---

### Anti-Pattern 3: Only Storing Flags

**Problem**:
```python
# ❌ Bad - Just a flag, no response data
cache.set(key, "processed")
```

**Solution**:
```python
# ✅ Good - Store full response
cache.set(key, json.dumps({
    "status": "success",
    "transaction_id": "tx123",
    "amount": 100,
    "timestamp": "2024-08-13T10:00:00Z"
}))
```

---

### Anti-Pattern 4: Mutable Idempotency Keys

**Problem**:
```python
# ❌ Bad - Key changes each time
key = f"order_{datetime.now().isoformat()}"
```

**Solution**:
```python
# ✅ Good - Stable key
key = f"order_{user_id}_{cart_hash}"
# or
key = str(uuid.uuid4())  # Client-generated
```

---

### Anti-Pattern 5: No TTL on Keys

**Problem**:
```python
# ❌ Bad - Infinite storage
redis.set(key, result)  # Never expires
```

**Solution**:
```python
# ✅ Good - Set appropriate TTL
redis.setex(key, 86400, result)  # 24 hours
```

---

### Anti-Pattern 6: Ignoring Payload Validation

**Problem**:
```python
# ❌ Bad - Different payloads with same key
if redis.exists(key):
    return redis.get(key)
# Process new_data (might be different!)
```

**Solution**:
```python
# ✅ Good - Validate payload
stored = redis.hgetall(key)
if stored:
    if hash(new_data) != stored['hash']:
        raise ConflictError()
    return stored['result']
```

---

### Anti-Pattern 7: Using POST for Idempotent Operations

**Problem**:
```python
# ❌ Bad - Updating with POST
@app.post("/api/users/{id}/activate")
def activate_user(id):
    user.status = "active"
```

**Solution**:
```python
# ✅ Good - Use PUT for updates
@app.put("/api/users/{id}")
def update_user(id, data):
    user.update(data)
```

---

### Anti-Pattern 8: Server-Generated Idempotency Keys

**Problem**:
```python
# ❌ Bad - Server generates key
@app.post("/api/orders")
def create_order(data):
    key = str(uuid.uuid4())  # Server generates
    # Client can't retry with same key!
```

**Solution**:
```python
# ✅ Good - Client provides key
@app.post("/api/orders")
def create_order(data, idempotency_key: str = Header(...)):
    # Client generates and sends key
    return process_order(idempotency_key, data)
```

---

## Design Patterns

### Decorator Pattern for Idempotency

```python
def idempotent(key_param='idempotency_key', ttl=86400):
    """Decorator to make functions idempotent"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract key from parameters
            key = kwargs.get(key_param)
            if not key:
                raise ValueError(f"{key_param} is required")
            
            # Check cache
            cached = cache.get(f"idem:{key}")
            if cached:
                return json.loads(cached)
            
            # Call original function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.setex(f"idem:{key}", ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

# Usage
@idempotent(key_param='payment_key', ttl=3600)
def process_payment(amount, payment_key):
    return charge_card(amount)
```

---

### Context Manager Pattern

```python
class IdempotencyContext:
    def __init__(self, key, storage):
        self.key = key
        self.storage = storage
    
    def __enter__(self):
        # Check if already processed
        result = self.storage.get(self.key)
        if result:
            raise AlreadyProcessedError(result)
        
        # Mark as processing
        self.storage.set_status(self.key, "processing")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Success
            self.storage.set_status(self.key, "completed")
        else:
            # Failure
            self.storage.set_status(self.key, "failed")
        return False

# Usage
try:
    with IdempotencyContext(key, storage):
        result = process_operation()
except AlreadyProcessedError as e:
    result = e.result
```

---

## Testing Patterns

### Pattern: Concurrent Request Testing

```python
import concurrent.futures

def test_concurrent_idempotency():
    key = "test_concurrent"
    num_requests = 10
    results = []
    
    def make_request():
        return process_payment(key, amount=100)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    # All should return same result
    assert all(r == results[0] for r in results)
    
    # Only one actual charge
    assert get_charge_count(key) == 1
```

---

### Pattern: Chaos Testing

```python
def test_with_failures():
    """Test idempotency with simulated failures"""
    key = "test_chaos"
    
    # Attempt 1: Timeout during processing
    with patch('external_service.call', side_effect=Timeout):
        with pytest.raises(Timeout):
            process_payment(key, 100)
    
    # Attempt 2: Network error during cache write
    with patch('cache.set', side_effect=NetworkError):
        with pytest.raises(NetworkError):
            process_payment(key, 100)
    
    # Attempt 3: Should succeed and not duplicate
    result = process_payment(key, 100)
    assert result['status'] == 'success'
    
    # Verify only one charge occurred
    assert get_charge_count(key) == 1
```

---

**Summary**: Use appropriate patterns based on requirements. Start simple (Check-Process-Store), add complexity as needed (locks, state tracking). Avoid anti-patterns that lead to duplicates or conflicts.

**Next**: See `04_BEST_PRACTICES.md` for production guidelines and `05_TROUBLESHOOTING.md` for common issues.
