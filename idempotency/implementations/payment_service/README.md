# Idempotent Payment Service

A production-ready payment service demonstrating comprehensive idempotency patterns.

## Features

✅ **Idempotency Keys**: Client-generated UUIDs prevent duplicate charges  
✅ **Distributed Locking**: Redis-based locks prevent race conditions  
✅ **Hybrid Storage**: Redis cache + PostgreSQL for speed and durability  
✅ **State Tracking**: Monitors processing, completed, and failed states  
✅ **Request Validation**: Detects conflicting payloads with same key  
✅ **Timeout Handling**: Recovers from stuck operations  

## Architecture

```
Client
  ↓ (Idempotency-Key: uuid)
FastAPI Endpoint
  ↓
Check Redis Cache (fast path)
  ↓ (miss)
Check PostgreSQL (slow path)
  ↓ (miss)
Acquire Distributed Lock
  ↓
Validate Request
  ↓
Process Payment
  ↓
Store in PostgreSQL (source of truth)
  ↓
Cache in Redis (24h TTL)
  ↓
Return Response
```

## Setup

### Prerequisites
- Python 3.10+
- PostgreSQL
- Redis

### Installation

1. Install dependencies:
```bash
pip install -r ../../requirements.txt
```

2. Start Redis:
```bash
redis-server
```

3. Setup PostgreSQL:
```bash
psql -U postgres -f schema.sql
```

4. Run the service:
```bash
python payment_service.py
```

Server starts at `http://localhost:8000`

## Usage

### Create Payment

```bash
curl -X POST http://localhost:8000/api/payments \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000" \
  -d '{
    "user_id": 123,
    "amount": 99.99,
    "currency": "USD",
    "description": "Product purchase"
  }'
```

**Response** (201 Created):
```json
{
  "payment_id": "pay_1691234567",
  "status": "completed",
  "transaction_id": "txn_1691234567_123",
  "amount": 99.99,
  "currency": "USD",
  "created_at": "2024-08-13T10:00:00"
}
```

### Duplicate Request (same idempotency key)

```bash
# Same request again
curl -X POST http://localhost:8000/api/payments \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key": 550e8400-e29b-41d4-a716-446655440000" \
  -d '{
    "user_id": 123,
    "amount": 99.99,
    "currency": "USD",
    "description": "Product purchase"
  }'
```

**Response** (200 OK - cached):
```json
{
  "payment_id": "pay_1691234567",
  "status": "completed",
  "transaction_id": "txn_1691234567_123",
  "amount": 99.99,
  "currency": "USD",
  "created_at": "2024-08-13T10:00:00"
}
```

### Conflicting Request (same key, different payload)

```bash
curl -X POST http://localhost:8000/api/payments \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000" \
  -d '{
    "user_id": 123,
    "amount": 199.99,
    "currency": "USD",
    "description": "Different amount!"
  }'
```

**Response** (422 Unprocessable Entity):
```json
{
  "detail": "Idempotency key reused with different payload"
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "redis": "ok",
  "database": "ok"
}
```

## Testing

### Run Tests
```bash
pytest test_payment_service.py -v
```

### Concurrency Test
```bash
python test_concurrent.py
```

### Load Test
```bash
locust -f locustfile.py --host=http://localhost:8000
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI.

## Key Components

### DistributedLock
Redis-based distributed lock to prevent race conditions:
```python
with DistributedLock(idempotency_key, timeout=30):
    # Only one request can enter this block
    process_payment()
```

### Request Validation
Detects if idempotency key is reused with different payload:
```python
stored_hash = get_stored_hash(key)
current_hash = hash_request(new_data)
if stored_hash != current_hash:
    raise ConflictError()
```

### State Tracking
Tracks processing state to handle timeouts:
- `PENDING`: Initial state
- `PROCESSING`: Currently being processed
- `COMPLETED`: Successfully completed
- `FAILED`: Processing failed

### Hybrid Storage
- **Redis**: Fast cache with 24h TTL
- **PostgreSQL**: Durable source of truth

## Configuration

Edit `payment_service.py` to configure:

```python
# Redis connection
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

# Database connection
get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="idempotency_demo",
        user="postgres",
        password="postgres"
    )

# Cache TTL
self.cache_ttl = 86400  # 24 hours
```

## Production Considerations

1. **Connection Pooling**: Use connection pools for Redis and PostgreSQL
2. **Monitoring**: Add Prometheus metrics (see monitoring/metrics.py)
3. **Logging**: Use structured logging (structlog)
4. **Rate Limiting**: Add per-key rate limiting
5. **Cleanup**: Schedule job to remove expired keys from database
6. **Replication**: Use Redis Sentinel or Cluster for HA
7. **Secrets**: Use environment variables or secrets manager

## Error Responses

| Status Code | Meaning |
|-------------|---------|
| 201 | Payment created successfully |
| 200 | Duplicate request, cached response returned |
| 409 | Payment is currently being processed |
| 422 | Idempotency key reused with different payload |
| 500 | Internal server error |
| 503 | Could not acquire lock (high contention) |

## Troubleshooting

### Duplicate Payments
- Check if distributed lock is being used
- Verify unique constraint exists in database
- Review logs for race conditions

### Slow Performance
- Check Redis connection
- Verify database indexes
- Monitor lock contention

### Stuck in Processing
- Check for operations older than 5 minutes
- Review application logs for crashes
- Verify lock timeout settings

## Next Steps

- See `../../03_PATTERNS.md` for more idempotency patterns
- See `../../04_BEST_PRACTICES.md` for production guidelines
- Check `../api_service/` for API-focused example
- Check `../message_queue/` for queue processing example
