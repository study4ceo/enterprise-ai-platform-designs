# Idempotency Troubleshooting Guide

## Common Issues & Solutions

### Issue 1: Duplicate Operations Despite Idempotency

**Symptoms**:
- Multiple charges for same idempotency key
- Duplicate database records
- Multiple email notifications

**Root Causes**:

**1. Race Condition**
```python
# Problem
if not cache.exists(key):  # ← Two requests check simultaneously
    process()  # ← Both enter here
```

**Solution**: Use distributed lock
```python
with distributed_lock(key, timeout=30):
    if not cache.exists(key):
        process()
```

**2. Cache Miss + DB Miss**
```python
# Problem: Cache expired but DB query fails
cached = redis.get(key)  # Miss
db_result = db.query(key)  # Also miss (network issue)
process()  # Duplicate!
```

**Solution**: Use database as source of truth
```python
# Always check DB if cache misses
if not redis.get(key):
    db_result = db.query(key)
    if db_result:
        # Warm cache
        redis.set(key, db_result)
        return db_result
    # Only process if both miss
```

**3. No Unique Constraint**
```sql
-- Problem: No constraint prevents duplicates
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    idempotency_key VARCHAR(255)  -- ← No UNIQUE constraint
);
```

**Solution**: Add unique constraint
```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    idempotency_key VARCHAR(255) UNIQUE NOT NULL
);
```

**Debugging**:
```python
# Add detailed logging
logger.info("idempotency_check", 
    key=key,
    cache_exists=cache.exists(key),
    db_exists=db.exists(key),
    lock_acquired=lock_acquired,
    timestamp=time.time())
```

---

### Issue 2: Operations Stuck in "Processing" State

**Symptoms**:
- Status remains "processing" indefinitely
- Retries return 409 Conflict
- Operations never complete

**Root Causes**:

**1. Process Died During Execution**
```python
# Mark as processing
set_state(key, "processing")
result = long_running_operation()  # ← Process crashes here
set_state(key, "completed")  # Never reached
```

**Solution**: Implement timeout and retry
```python
def check_stuck_operation(key):
    state = get_state(key)
    if state['status'] == 'processing':
        elapsed = time.time() - state['started_at']
        if elapsed > 300:  # 5 minutes
            logger.warning(f"Operation {key} stuck, retrying")
            # Reset state and retry
            set_state(key, "pending")
            return retry_operation(key)
```

**2. Lock Never Released**
```python
# Problem
lock.acquire(key)
process()  # ← Exception here
lock.release()  # Never reached
```

**Solution**: Use context manager or finally
```python
try:
    lock.acquire(key)
    process()
finally:
    lock.release()

# Or use context manager
with distributed_lock(key):
    process()
```

**3. Deadlock**
```python
# Problem: Circular dependency
with lock("key_a"):
    with lock("key_b"):  # ← Service B has key_b, waiting for key_a
        process()
```

**Solution**: Consistent lock ordering
```python
keys = sorted([key_a, key_b])  # Always lock in same order
with lock(keys[0]):
    with lock(keys[1]):
        process()
```

**Monitoring**:
```python
# Alert on stuck operations
def monitor_stuck_operations():
    stuck = db.query("""
        SELECT COUNT(*) FROM idempotency_keys
        WHERE status = 'processing'
        AND created_at < NOW() - INTERVAL '5 minutes'
    """).fetchone()[0]
    
    if stuck > 10:
        alert("High stuck operations", count=stuck)
```

---

### Issue 3: Conflicting Requests (422 Errors)

**Symptoms**:
- 422 Unprocessable Entity errors
- "Idempotency key reused with different payload"
- Legitimate retries rejected

**Root Causes**:

**1. Non-Deterministic Request Hash**
```python
# Problem: Timestamp or random data in request
request = {
    "amount": 100,
    "timestamp": time.time()  # ← Changes on retry!
}
hash_request(request)  # Different each time
```

**Solution**: Exclude volatile fields from hash
```python
def hash_request(data):
    # Only hash stable fields
    stable_data = {
        k: v for k, v in data.items()
        if k not in ['timestamp', 'request_id', 'nonce']
    }
    return hashlib.sha256(
        json.dumps(stable_data, sort_keys=True).encode()
    ).hexdigest()
```

**2. JSON Serialization Differences**
```python
# Problem: Inconsistent key ordering
json.dumps({"a": 1, "b": 2})  # '{"a":1,"b":2}'
json.dumps({"b": 2, "a": 1})  # '{"b":2,"a":1}' ← Different hash!
```

**Solution**: Sort keys consistently
```python
json.dumps(data, sort_keys=True)  # Always same order
```

**3. Floating Point Precision**
```python
# Problem
request1 = {"amount": 0.1 + 0.2}  # 0.30000000000000004
request2 = {"amount": 0.3}         # 0.3
hash(request1) != hash(request2)   # Different!
```

**Solution**: Round or use Decimal
```python
from decimal import Decimal

def normalize_floats(data):
    if isinstance(data, float):
        return round(data, 2)
    elif isinstance(data, dict):
        return {k: normalize_floats(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_floats(v) for v in data]
    return data
```

**Debugging**:
```python
# Log hash mismatches
if stored_hash != request_hash:
    logger.error("hash_mismatch",
        key=key,
        stored_request=stored_request,
        current_request=current_request,
        stored_hash=stored_hash,
        current_hash=request_hash)
```

---

### Issue 4: Cache and Database Out of Sync

**Symptoms**:
- Cache returns different data than database
- Stale data returned
- Inconsistent states

**Root Causes**:

**1. Cache Not Invalidated on Update**
```python
# Problem
db.update("payments", {"id": payment_id, "status": "refunded"})
# Cache still has "completed" status!
```

**Solution**: Invalidate cache on updates
```python
def update_payment(payment_id, updates):
    db.update("payments", {"id": payment_id, **updates})
    # Invalidate cache
    cache.delete(f"payment:{payment_id}")
```

**2. Write to Cache Failed**
```python
# Problem
result = process_payment()
db.insert("payments", result)
cache.set(key, result)  # ← Fails silently
```

**Solution**: Check cache write success
```python
result = process_payment()
db.insert("payments", result)
if not cache.set(key, result):
    logger.error("cache_write_failed", key=key)
    # Continue - DB is source of truth
```

**3. Race Between Cache and DB**
```python
# Problem: Update in wrong order
cache.set(key, new_value)  # ← Written first
time.sleep(0.1)  # Delay
db.update(key, new_value)  # ← Another process reads from cache
```

**Solution**: Write to DB first, then cache
```python
# Always: DB first, cache second
db.update(key, new_value)
cache.set(key, new_value)
```

**Best Practice**: Database is source of truth
```python
def get_with_cache(key):
    # Try cache
    cached = cache.get(key)
    if cached:
        return cached
    
    # Fallback to DB (source of truth)
    db_value = db.query(key)
    if db_value:
        cache.setex(key, 3600, db_value)
    return db_value
```

---

### Issue 5: Performance Degradation

**Symptoms**:
- Slow response times
- High latency on idempotency checks
- Database/cache overload

**Root Causes**:

**1. No Indexing**
```sql
-- Problem: Full table scan
SELECT * FROM idempotency_keys WHERE key = 'abc123';
```

**Solution**: Add indexes
```sql
CREATE INDEX idx_idempotency_key ON idempotency_keys(key);
CREATE INDEX idx_status ON idempotency_keys(status);
CREATE INDEX idx_created_at ON idempotency_keys(created_at);
```

**2. Large Payloads in Cache**
```python
# Problem: Storing huge responses
cache.set(key, json.dumps(large_object))  # 10MB!
```

**Solution**: Store references or compress
```python
# Option 1: Store ID, fetch from DB on cache miss
cache.set(key, {"result_id": result.id})

# Option 2: Compress
import gzip
compressed = gzip.compress(json.dumps(result).encode())
cache.set(key, compressed)
```

**3. No Connection Pooling**
```python
# Problem: New connection per request
redis = redis.Redis()  # New connection each time
```

**Solution**: Use connection pool
```python
# Create pool once
redis_pool = redis.ConnectionPool(host='localhost', port=6379)
redis_client = redis.Redis(connection_pool=redis_pool)
```

**4. Synchronous Operations**
```python
# Problem: Blocking calls
def process_request(key):
    check_cache(key)  # Blocks
    check_db(key)     # Blocks
    process()         # Blocks
```

**Solution**: Use async/await
```python
async def process_request(key):
    cached = await async_cache.get(key)
    if cached:
        return cached
    
    result = await async_process()
    await async_cache.set(key, result)
    return result
```

**Monitoring**:
```python
# Track latency
processing_duration = Histogram(
    'idempotency_check_seconds',
    'Idempotency check duration',
    buckets=[0.001, 0.01, 0.05, 0.1, 0.5, 1.0]
)

@processing_duration.time()
def check_idempotency(key):
    # Measure performance
    pass
```

---

### Issue 6: Memory Leaks in Idempotency Storage

**Symptoms**:
- Redis memory usage growing continuously
- Out of memory errors
- Performance degradation over time

**Root Causes**:

**1. No TTL Set**
```python
# Problem: Keys never expire
redis.set(key, value)  # Lives forever
```

**Solution**: Always set TTL
```python
redis.setex(key, 86400, value)  # 24 hour TTL
```

**2. TTL Not Applied to All Keys**
```python
# Problem: Hash fields don't inherit TTL
redis.hset(key, "field1", "value1")
redis.hset(key, "field2", "value2")
# Need to set TTL separately!
```

**Solution**: Set TTL explicitly
```python
redis.hset(key, mapping={"field1": "value1", "field2": "value2"})
redis.expire(key, 86400)  # Set TTL on entire hash
```

**3. Abandoned Processing States**
```python
# Problem: "processing" states never cleaned up
redis.hset(key, "status", "processing")
# Process crashes, status never updated
```

**Solution**: Periodic cleanup
```python
def cleanup_abandoned():
    """Clean up abandoned processing states"""
    cursor = 0
    while True:
        cursor, keys = redis.scan(cursor, match="idem:*", count=100)
        
        for key in keys:
            state = redis.hget(key, "status")
            started = redis.hget(key, "started_at")
            
            if state == "processing" and started:
                if time.time() - float(started) > 3600:  # 1 hour
                    redis.delete(key)
        
        if cursor == 0:
            break
```

**Monitoring**:
```python
# Monitor memory usage
def check_redis_memory():
    info = redis.info('memory')
    used_memory_mb = info['used_memory'] / 1024 / 1024
    
    if used_memory_mb > 1000:  # 1 GB
        alert("High Redis memory usage", memory_mb=used_memory_mb)
```

---

### Issue 7: Idempotency Keys Expiring Too Soon

**Symptoms**:
- Duplicate operations after key expiry
- Users retry and create duplicates
- "Key not found" errors

**Root Causes**:

**1. TTL Too Short**
```python
# Problem: Expires before user can retry
redis.setex(key, 60, value)  # Only 1 minute!
```

**Solution**: Set appropriate TTL based on use case
```python
# Payment: User might retry next day
redis.setex(payment_key, 86400, value)  # 24 hours

# Webhook: May be retried over days
redis.setex(webhook_key, 604800, value)  # 7 days
```

**2. Clock Skew Between Services**
```python
# Problem: Different server times
server1_time = time.time()  # 10:00:00
server2_time = time.time()  # 09:59:00 (1 minute behind)
```

**Solution**: Use centralized time source or logical clocks
```python
# Use Redis TIME command (centralized)
server_time = redis.time()[0]
```

**3. TTL Refreshes Not Implemented**
```python
# Problem: Long operation, TTL expires mid-processing
redis.setex(key, 300, "processing")
long_operation()  # Takes 10 minutes
# Key expired!
```

**Solution**: Refresh TTL during processing
```python
def long_operation_with_refresh(key):
    redis.setex(key, 600, "processing")
    
    for step in steps:
        process_step(step)
        # Refresh TTL
        redis.expire(key, 600)
```

---

### Issue 8: Distributed Lock Issues

**Symptoms**:
- Deadlocks
- Lock never released
- Multiple processes enter critical section

**Root Causes**:

**1. Lock Not Released on Exception**
```python
# Problem
lock.acquire()
process()  # ← Exception
lock.release()  # Never reached
```

**Solution**: Use try/finally or context manager
```python
try:
    lock.acquire()
    process()
finally:
    lock.release()
```

**2. Lock Expires During Processing**
```python
# Problem
with RedisLock(key, timeout=10):
    long_operation()  # Takes 30 seconds
    # Lock expired at 10s, another process acquired it!
```

**Solution**: Set longer timeout or refresh lock
```python
with RedisLock(key, timeout=60):  # Longer timeout
    long_operation()
```

**3. Wrong Lock Released**
```python
# Problem: Process A releases Process B's lock
lock_value = "process_a"
redis.set(lock_key, lock_value)
# ...
redis.delete(lock_key)  # ← Process B might have the lock now!
```

**Solution**: Check lock ownership before release
```lua
-- Lua script for atomic check-and-delete
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

---

### Issue 9: Testing Challenges

**Problem**: Hard to test idempotency in development

**Solutions**:

**1. Mock Concurrent Requests**
```python
import concurrent.futures

def test_concurrency():
    with concurrent.futures.ThreadPoolExecutor(10) as executor:
        futures = [executor.submit(process, key) for _ in range(10)]
        results = [f.result() for f in futures]
    
    assert all(r == results[0] for r in results)
```

**2. Simulate Failures**
```python
from unittest.mock import patch

def test_with_failures():
    with patch('cache.set', side_effect=[Exception, None]):
        # First attempt fails, second succeeds
        process(key)
        result = process(key)  # Should work
```

**3. Time-based Testing**
```python
from freezegun import freeze_time

@freeze_time("2024-08-13 10:00:00")
def test_expiry():
    process(key)  # Cached
    
    # Fast-forward time
    with freeze_time("2024-08-14 10:00:01"):
        # Should reprocess (expired)
        process(key)
```

---

## Debugging Checklist

When investigating idempotency issues:

- [ ] Check cache hit/miss rates in metrics
- [ ] Review logs for duplicate operations
- [ ] Verify unique constraints exist in database
- [ ] Check if distributed locks are being used
- [ ] Validate TTL settings are appropriate
- [ ] Look for race conditions in code
- [ ] Verify request hashing is deterministic
- [ ] Check for stuck operations in monitoring
- [ ] Review error rates (409, 422 responses)
- [ ] Test with concurrent requests locally
- [ ] Check Redis memory usage
- [ ] Verify indexes exist on lookup columns
- [ ] Review lock timeout settings
- [ ] Check for clock skew between servers

---

## Emergency Procedures

### Stuck Operations Cleanup
```python
# Reset all stuck operations
def emergency_unstuck():
    affected = db.execute("""
        UPDATE idempotency_keys
        SET status = 'failed'
        WHERE status = 'processing'
        AND created_at < NOW() - INTERVAL '10 minutes'
        RETURNING key
    """)
    
    for row in affected:
        cache.delete(row['key'])
    
    logger.warning(f"Reset {affected.rowcount} stuck operations")
```

### Cache Flush
```python
# Nuclear option: clear all idempotency cache
def emergency_cache_flush():
    cursor = 0
    count = 0
    
    while True:
        cursor, keys = redis.scan(cursor, match="idem:*", count=1000)
        if keys:
            redis.delete(*keys)
            count += len(keys)
        
        if cursor == 0:
            break
    
    logger.warning(f"Flushed {count} idempotency keys from cache")
    alert("Emergency cache flush performed", count=count)
```

### Rollback Feature
```python
# Temporarily disable idempotency
@app.post("/api/payments")
def create_payment(data, idempotency_key: str = Header(None)):
    if not feature_flags.idempotency_enabled():
        # Bypass idempotency
        return process_payment(data)
    
    # Normal idempotent flow
    return idempotent_process_payment(idempotency_key, data)
```

---

**Summary**: Most issues stem from race conditions, improper TTLs, or missing error handling. Use distributed locks, set appropriate TTLs, and implement comprehensive monitoring. Database is always source of truth; cache is for performance.

**Next**: See `implementations/` for working examples and `scenarios/` for real-world use cases.
