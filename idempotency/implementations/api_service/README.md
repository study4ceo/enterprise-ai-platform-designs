# Idempotent API Service

Generic RESTful API service with automatic idempotency middleware.

## Features

✅ **Automatic Idempotency Middleware** - Handles idempotency transparently  
✅ **Multiple Resource Types** - Users and Orders examples  
✅ **All HTTP Methods** - GET, POST, PUT, DELETE with proper idempotency  
✅ **Redis Caching** - Fast duplicate detection  
✅ **Request Validation** - Detects conflicting payloads  
✅ **State Tracking** - Monitors processing status  

## How It Works

### Middleware Flow

```
POST Request
  ↓
Check Idempotency-Key header
  ↓
Cache lookup (Redis)
  ↓
Hit? → Return cached response
  ↓
Miss? → Validate request hash
  ↓
Mark as "processing"
  ↓
Execute endpoint handler
  ↓
Cache response
  ↓
Return response
```

### Endpoint Idempotency

| Method | Naturally Idempotent | Implementation |
|--------|---------------------|----------------|
| GET | ✅ Yes | Read-only, no changes |
| POST | ❌ No | Requires Idempotency-Key header |
| PUT | ✅ Yes | Sets absolute state |
| DELETE | ✅ Yes | First deletes, rest return 404 |
| PATCH | ⚠️ Depends | Conditional updates |

## Setup

### Start Redis
```bash
redis-server
```

### Run Service
```bash
python api_service.py
```

Service runs at `http://localhost:8001`

## Usage Examples

### 1. Create User (POST - Requires Idempotency-Key)

**First request**:
```bash
curl -X POST http://localhost:8001/api/users \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: user-create-001" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe"
  }'
```

**Response** (201 Created):
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-08-13T10:00:00"
}
```

**Duplicate request** (same key):
```bash
# Same request again
curl -X POST http://localhost:8001/api/users \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: user-create-001" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe"
  }'
```

**Response** (200 OK - cached):
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-08-13T10:00:00"
}
```

**Note**: Response includes `X-Idempotency: hit` header

### 2. Get User (GET - Naturally Idempotent)

```bash
curl http://localhost:8001/api/users/1
```

No idempotency key needed - GET is naturally idempotent.

### 3. Update User (PUT - Naturally Idempotent)

```bash
curl -X PUT http://localhost:8001/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Updated Doe",
    "email": "john.new@example.com"
  }'
```

Multiple calls with same data produce same result.

### 4. Delete User (DELETE - Naturally Idempotent)

```bash
# First call
curl -X DELETE http://localhost:8001/api/users/1

# Second call (already deleted)
curl -X DELETE http://localhost:8001/api/users/1
# Returns 404 - still idempotent
```

### 5. Create Order (POST - Requires Idempotency-Key)

```bash
curl -X POST http://localhost:8001/api/orders \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: order-create-001" \
  -d '{
    "user_id": 1,
    "items": [
      {"product_id": 101, "quantity": 2, "price": 29.99},
      {"product_id": 102, "quantity": 1, "price": 49.99}
    ],
    "total": 109.97
  }'
```

### 6. Confirm Order (POST - Idempotent State Transition)

```bash
curl -X POST http://localhost:8001/api/orders/1/confirm \
  -H "Idempotency-Key: order-confirm-001"
```

State transition is idempotent - if already confirmed, returns success.

### 7. Conflicting Request (422 Error)

```bash
curl -X POST http://localhost:8001/api/users \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: user-create-001" \
  -d '{
    "username": "different_user",
    "email": "different@example.com",
    "full_name": "Different Name"
  }'
```

**Response** (422 Unprocessable Entity):
```json
{
  "error": "Idempotency key reused with different payload"
}
```

### 8. View Statistics

```bash
curl http://localhost:8001/api/idempotency/stats
```

**Response**:
```json
{
  "total_cached_requests": 15,
  "processing": 0,
  "completed": 15,
  "cache_hit_potential": "100.0%"
}
```

## API Documentation

Visit `http://localhost:8001/docs` for interactive Swagger UI.

## Key Features Explained

### Automatic Middleware

The `IdempotencyMiddleware` automatically:
1. Checks for `Idempotency-Key` header
2. Looks up cached responses
3. Validates request payloads
4. Tracks processing state
5. Caches successful responses

**No code changes needed in endpoint handlers!**

### Request Hash Validation

```python
# Middleware calculates hash of request body
request_hash = hashlib.sha256(body).hexdigest()

# Compares with stored hash
if stored_hash and stored_hash != request_hash:
    return 422 error
```

Prevents malicious key reuse with different data.

### State Tracking

States:
- `processing` - Currently executing
- `completed` - Successfully finished
- `failed` - Execution failed

Prevents duplicate processing while request is in flight.

### TTL Configuration

Default: 1 hour (3600 seconds)

```python
self.ttl = 3600  # Configure in IdempotencyMiddleware.__init__
```

Adjust based on your use case:
- Short-lived sessions: 1 hour
- Payment-like operations: 24 hours
- Webhooks: 7 days

## Testing

### Test Basic Idempotency
```bash
# Create user twice with same key
KEY="test-$(date +%s)"

curl -X POST http://localhost:8001/api/users \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $KEY" \
  -d '{"username": "test", "email": "test@test.com", "full_name": "Test"}' \
  | jq .

curl -X POST http://localhost:8001/api/users \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $KEY" \
  -d '{"username": "test", "email": "test@test.com", "full_name": "Test"}' \
  | jq .
```

Both should return same user ID.

### Test Conflict Detection
```bash
KEY="conflict-test"

# First request
curl -X POST http://localhost:8001/api/orders \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $KEY" \
  -d '{"user_id": 1, "items": [], "total": 100}'

# Different data, same key
curl -X POST http://localhost:8001/api/orders \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $KEY" \
  -d '{"user_id": 1, "items": [], "total": 200}'
```

Second should return 422.

### Test Concurrent Requests

```python
import concurrent.futures
import requests

def create_user(key):
    return requests.post(
        "http://localhost:8001/api/users",
        headers={"Idempotency-Key": key},
        json={"username": "concurrent", "email": "test@test.com", "full_name": "Test"}
    )

with concurrent.futures.ThreadPoolExecutor(10) as executor:
    futures = [executor.submit(create_user, "concurrent-test") for _ in range(10)]
    results = [f.result() for f in futures]

# All should return same user ID
print([r.json()['id'] for r in results])
```

## Comparison with Payment Service

| Feature | Payment Service | API Service |
|---------|----------------|-------------|
| Idempotency | Manual in each endpoint | Automatic middleware |
| Storage | Hybrid (Redis + PostgreSQL) | Redis only |
| Locking | Explicit distributed locks | Implicit via state tracking |
| Use Case | Critical financial operations | General API endpoints |
| Complexity | Higher (more guarantees) | Lower (easier to use) |

## When to Use This Pattern

✅ **Use for**:
- General REST APIs
- Non-critical operations
- Rapid development
- Multiple similar endpoints

❌ **Consider payment_service for**:
- Financial transactions
- Critical operations requiring DB durability
- Audit trail requirements
- Explicit lock control needed

## Customization

### Custom TTL per Endpoint

```python
# Add route-specific TTL
TTL_CONFIG = {
    "/api/users": 3600,       # 1 hour
    "/api/orders": 7200,      # 2 hours
    "/api/payments": 86400,   # 24 hours
}

# In middleware:
ttl = TTL_CONFIG.get(request.url.path, self.ttl)
```

### Custom Storage Backend

Replace Redis with database:

```python
class DatabaseIdempotencyStorage:
    def get(self, key):
        return db.query("SELECT * FROM idempotency WHERE key = ?", key)
    
    def set(self, key, value, ttl):
        db.insert("idempotency", {"key": key, "value": value, "expires_at": now() + ttl})
```

### Exclude Endpoints

```python
EXCLUDED_PATHS = ["/health", "/metrics", "/docs"]

if request.url.path in EXCLUDED_PATHS:
    return await call_next(request)
```

## Production Considerations

1. **Connection Pooling**: Use Redis connection pool
2. **Error Handling**: Add retry logic for Redis failures
3. **Monitoring**: Add metrics for cache hits/misses
4. **Security**: Validate idempotency key format
5. **Rate Limiting**: Prevent abuse of same keys
6. **Logging**: Log all idempotency events

## Next Steps

- See `../payment_service/` for database-backed example
- See `../message_queue/` for async processing
- See `../../03_PATTERNS.md` for more patterns
- See `../../04_BEST_PRACTICES.md` for production guidelines
