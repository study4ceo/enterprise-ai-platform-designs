# Idempotency Best Practices

## Production-Ready Guidelines

### 1. Key Generation

**✅ DO**:
- Use UUIDs for client-generated keys
- Include context in key (user_id, entity_type)
- Make keys deterministic when possible
- Use URL-safe characters

**❌ DON'T**:
- Use timestamps alone
- Use sequential integers
- Include sensitive data
- Make keys too long (> 255 chars)

**Examples**:
```python
# Good
idempotency_key = str(uuid.uuid4())
idempotency_key = f"order_{user_id}_{cart_hash}"
idempotency_key = hashlib.sha256(request_data).hexdigest()

# Bad
idempotency_key = str(time.time())  # Not unique enough
idempotency_key = f"user_{ssn}_{credit_card}"  # Sensitive data
```

---

### 2. TTL Selection

**Guidelines**:
- Payment processing: 24-48 hours
- Order creation: 1-2 hours  
- Webhooks: 7 days
- Message processing: 1 hour
- File uploads: 1 hour

**Considerations**:
- User retry window
- Business requirements
- Storage costs
- Compliance

```python
# Configure per operation type
TTL_CONFIG = {
    "payment": 86400,      # 24 hours
    "order": 3600,         # 1 hour
    "webhook": 604800,     # 7 days
    "message": 3600,       # 1 hour
}

def get_ttl(operation_type):
    return TTL_CONFIG.get(operation_type, 3600)  # Default 1 hour
```

---

### 3. Storage Strategy

**Choose based on requirements**:

| Requirement | Solution |
|-------------|----------|
| Speed | Redis cache |
| Durability | PostgreSQL |
| Audit trail | Database + logs |
| High throughput | Hybrid (cache + DB) |
| Low cost | Cache with longer TTL |

**Hybrid approach** (recommended):
```python
def check_idempotency(key):
    # L1: Cache (fast)
    cached = redis.get(key)
    if cached:
        metrics.cache_hit.inc()
        return cached
    
    # L2: Database (durable)
    db_result = db.query("SELECT * FROM idempotency WHERE key = ?", key)
    if db_result:
        # Warm cache
        redis.setex(key, 3600, db_result)
        metrics.cache_miss_db_hit.inc()
        return db_result
    
    metrics.cache_miss_db_miss.inc()
    return None
```

---

### 4. Error Handling

**Status codes**:
- `200 OK`: Duplicate request, cached response
- `201 Created`: New resource created
- `409 Conflict`: Operation in progress
- `422 Unprocessable`: Key reused with different payload
- `500 Internal Error`: Processing failed

**Implementation**:
```python
@app.post("/api/payments")
def create_payment(data, idempotency_key: str = Header(...)):
    try:
        state = get_state(idempotency_key)
        
        if state['status'] == 'completed':
            return JSONResponse(
                status_code=200,
                content=state['result']
            )
        
        if state['status'] == 'processing':
            if not is_stuck(state):
                return JSONResponse(
                    status_code=409,
                    content={"error": "Request still processing"}
                )
        
        # Validate payload
        if state.get('request_hash') and state['request_hash'] != hash(data):
            return JSONResponse(
                status_code=422,
                content={"error": "Idempotency key reused with different payload"}
            )
        
        # Process
        result = process_payment(idempotency_key, data)
        return JSONResponse(status_code=201, content=result)
        
    except Exception as e:
        logger.error(f"Payment error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
```

---

### 5. Monitoring & Observability

**Key metrics**:
```python
from prometheus_client import Counter, Histogram, Gauge

# Counters
idempotency_total = Counter('idempotency_requests_total', 'Total requests')
idempotency_hits = Counter('idempotency_cache_hits', 'Cache hits')
idempotency_misses = Counter('idempotency_cache_misses', 'Cache misses')
idempotency_conflicts = Counter('idempotency_conflicts', 'Payload conflicts')

# Histograms
processing_duration = Histogram(
    'idempotency_processing_seconds',
    'Processing duration',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

# Gauges
stuck_operations = Gauge('stuck_operations', 'Operations stuck processing')

# Usage
@processing_duration.time()
def process_request(key):
    idempotency_total.inc()
    
    if cache.exists(key):
        idempotency_hits.inc()
        return cache.get(key)
    
    idempotency_misses.inc()
    result = process()
    return result
```

**Logging**:
```python
import structlog

logger = structlog.get_logger()

def idempotent_operation(key, func):
    logger.info("idempotency.check", key=key)
    
    cached = cache.get(key)
    if cached:
        logger.info("idempotency.hit", key=key, source="cache")
        return cached
    
    logger.info("idempotency.miss", key=key)
    
    try:
        with processing_duration.time():
            result = func()
        
        logger.info("idempotency.success", key=key, duration=duration)
        cache.set(key, result)
        return result
        
    except Exception as e:
        logger.error("idempotency.error", key=key, error=str(e), exc_info=True)
        raise
```

---

### 6. Security

**Validate keys**:
```python
import re

def validate_idempotency_key(key: str) -> bool:
    # UUID format or custom format
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    custom_pattern = r'^[a-zA-Z0-9_-]{10,255}$'
    
    return bool(re.match(uuid_pattern, key) or re.match(custom_pattern, key))

@app.post("/api/orders")
def create_order(data, idempotency_key: str = Header(...)):
    if not validate_idempotency_key(idempotency_key):
        raise HTTPException(400, "Invalid idempotency key format")
    
    # Process...
```

**Rate limiting per key**:
```python
def check_rate_limit(key):
    """Prevent abuse of same idempotency key"""
    request_count = redis.incr(f"rate:{key}")
    redis.expire(f"rate:{key}", 60)
    
    if request_count > 100:  # Max 100 requests per minute
        raise HTTPException(429, "Too many requests with same idempotency key")
```

**Tenant isolation**:
```python
def scope_key(tenant_id, key):
    """Isolate keys per tenant"""
    return f"tenant_{tenant_id}:{key}"

def process_tenant_request(tenant_id, idempotency_key, data):
    scoped_key = scope_key(tenant_id, idempotency_key)
    return process_request(scoped_key, data)
```

---

### 7. Testing Strategy

**Unit tests**:
```python
def test_basic_idempotency():
    key = "test_basic"
    
    result1 = process_payment(key, 100)
    result2 = process_payment(key, 100)
    
    assert result1 == result2
    assert get_charge_count(key) == 1
```

**Integration tests**:
```python
@pytest.mark.integration
def test_end_to_end():
    client = TestClient(app)
    key = str(uuid.uuid4())
    
    response1 = client.post(
        "/api/orders",
        headers={"Idempotency-Key": key},
        json={"items": []}
    )
    assert response1.status_code == 201
    
    response2 = client.post(
        "/api/orders",
        headers={"Idempotency-Key": key},
        json={"items": []}
    )
    assert response2.status_code == 200
    assert response1.json()['id'] == response2.json()['id']
```

**Concurrency tests**:
```python
def test_concurrent_requests():
    key = "test_concurrent"
    
    with concurrent.futures.ThreadPoolExecutor(10) as executor:
        futures = [
            executor.submit(process_payment, key, 100)
            for _ in range(10)
        ]
        results = [f.result() for f in futures]
    
    assert all(r == results[0] for r in results)
    assert get_charge_count(key) == 1
```

**Load tests**:
```python
# Using locust
from locust import HttpUser, task

class IdempotencyLoadTest(HttpUser):
    @task
    def test_payment(self):
        key = str(uuid.uuid4())
        self.client.post(
            "/api/payments",
            headers={"Idempotency-Key": key},
            json={"amount": 100}
        )
```

---

### 8. Documentation

**API documentation**:
```yaml
# OpenAPI/Swagger
paths:
  /api/payments:
    post:
      summary: Create payment
      parameters:
        - name: Idempotency-Key
          in: header
          required: true
          schema:
            type: string
            format: uuid
          description: |
            Client-generated unique key for idempotency.
            Duplicate requests with same key return cached response.
            TTL: 24 hours
      responses:
        '201':
          description: Payment created
        '200':
          description: Duplicate request, cached response
        '409':
          description: Request still processing
        '422':
          description: Key reused with different payload
```

**Code comments**:
```python
def process_payment(idempotency_key: str, amount: float) -> dict:
    """
    Process payment idempotently.
    
    Args:
        idempotency_key: Client-generated UUID for deduplication
        amount: Payment amount in USD
    
    Returns:
        Payment result with transaction_id and status
    
    Raises:
        ConflictError: If key reused with different amount
        ProcessingError: If previous request still processing
    
    Notes:
        - Idempotency keys expire after 24 hours
        - Duplicate requests return cached response
        - Uses distributed lock to prevent race conditions
    """
```

---

### 9. Deployment

**Configuration**:
```python
# config.py
class IdempotencyConfig:
    # Redis connection
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # TTL settings
    DEFAULT_TTL = int(os.getenv("IDEMPOTENCY_TTL", "3600"))
    PAYMENT_TTL = int(os.getenv("PAYMENT_TTL", "86400"))
    
    # Lock settings
    LOCK_TIMEOUT = int(os.getenv("LOCK_TIMEOUT", "30"))
    
    # Monitoring
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    # Feature flags
    STRICT_VALIDATION = os.getenv("STRICT_VALIDATION", "true").lower() == "true"
```

**Health checks**:
```python
@app.get("/health/idempotency")
def idempotency_health():
    try:
        # Check Redis connectivity
        redis.ping()
        
        # Check database
        db.execute("SELECT 1")
        
        # Check stuck operations
        stuck_count = get_stuck_operation_count()
        
        return {
            "status": "healthy",
            "redis": "ok",
            "database": "ok",
            "stuck_operations": stuck_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 500
```

**Gradual rollout**:
```python
def should_use_idempotency(user_id: int) -> bool:
    """Feature flag for gradual rollout"""
    # Start with 10% of users
    return hash(user_id) % 100 < 10

@app.post("/api/orders")
def create_order(data, user_id: int, idempotency_key: str = Header(None)):
    if should_use_idempotency(user_id) and idempotency_key:
        return idempotent_create_order(idempotency_key, data)
    else:
        return regular_create_order(data)
```

---

### 10. Maintenance

**Cleanup old keys**:
```python
# Scheduled job
def cleanup_expired_keys():
    """Remove expired idempotency keys from database"""
    cutoff = datetime.utcnow() - timedelta(days=30)
    
    deleted = db.execute("""
        DELETE FROM idempotency_keys 
        WHERE created_at < ?
        RETURNING id
    """, (cutoff,))
    
    logger.info(f"Cleaned up {deleted.rowcount} expired keys")

# Run daily
schedule.every().day.at("02:00").do(cleanup_expired_keys)
```

**Monitor stuck operations**:
```python
def check_stuck_operations():
    """Alert on operations stuck in processing"""
    stuck = db.query("""
        SELECT key, created_at 
        FROM idempotency_keys 
        WHERE status = 'processing' 
        AND created_at < NOW() - INTERVAL '5 minutes'
    """)
    
    if len(stuck) > 100:
        alert("Too many stuck operations", count=len(stuck))
    
    for op in stuck:
        logger.warning(f"Operation {op['key']} stuck since {op['created_at']}")
```

**Performance optimization**:
```python
# Index on frequently queried columns
CREATE INDEX idx_idempotency_key ON idempotency_keys(key);
CREATE INDEX idx_created_at ON idempotency_keys(created_at);
CREATE INDEX idx_status ON idempotency_keys(status);

# Partition by creation date
CREATE TABLE idempotency_keys (
    ...
) PARTITION BY RANGE (created_at);

CREATE TABLE idempotency_keys_2024_08 
    PARTITION OF idempotency_keys
    FOR VALUES FROM ('2024-08-01') TO ('2024-09-01');
```

---

## Summary Checklist

### Development
- [ ] Client generates idempotency keys
- [ ] Server validates key format
- [ ] Check cache before processing
- [ ] Use distributed locks for race conditions
- [ ] Store full responses, not just flags
- [ ] Validate payload on key reuse
- [ ] Set appropriate TTLs
- [ ] Handle partial failures gracefully

### Testing
- [ ] Unit tests for basic idempotency
- [ ] Integration tests end-to-end
- [ ] Concurrency tests with multiple threads
- [ ] Chaos tests with simulated failures
- [ ] Load tests for performance

### Production
- [ ] Monitoring and metrics enabled
- [ ] Structured logging configured
- [ ] Health checks implemented
- [ ] Alerts for high conflict rates
- [ ] Alerts for stuck operations
- [ ] Cleanup jobs scheduled
- [ ] Documentation updated

### Security
- [ ] Input validation on keys
- [ ] Rate limiting per key
- [ ] Tenant isolation
- [ ] No sensitive data in keys
- [ ] Audit logs enabled

---

**Next**: See `05_TROUBLESHOOTING.md` for common issues and solutions, and `implementations/` for working code examples.
