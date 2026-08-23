# Detailed Architecture

## Request Flow

```
1. Client → API Gateway
   POST /api/notifications
   {
     "user_ids": [123, 456],
     "type": "push",
     "title": "New message",
     "body": "You have a new message",
     "priority": "high"
   }

2. API Gateway → Kafka
   - Validate request
   - Rate limit check
   - Enrich with metadata
   - Publish to topic: "notifications"
   - Partition by user_id

3. Kafka → Workers
   - Workers consume in batches
   - Parallel processing (1000s of workers)

4. Worker Processing:
   a. Fetch user preferences (Redis cache)
   b. Check opt-out status
   c. Check quiet hours (timezone aware)
   d. Format notification for channel
   e. Send to delivery service
   f. Log result
   g. Commit offset to Kafka

5. Delivery Service → User Device
   - APNs, FCM, SMTP, Twilio
   - Track delivery status
```

## Components Deep Dive

### 1. API Gateway

**Responsibilities**:
- Authentication (JWT)
- Rate limiting (token bucket: 1000 req/min per tenant)
- Request validation
- Async response (returns immediately)

**Endpoints**:
```
POST   /api/notifications          # Send notification
POST   /api/notifications/bulk     # Batch send
GET    /api/notifications/{id}     # Get status
POST   /api/preferences            # Update user preferences
```

**Response**:
```json
{
  "notification_id": "abc-123",
  "status": "queued",
  "queued_at": "2024-08-13T10:00:00Z"
}
```

### 2. Kafka Setup

**Topics**:
- `notifications` - Incoming requests (10K partitions)
- `notifications-dlq` - Failed messages
- `analytics` - Delivery metrics

**Configuration**:
```
Partitions: 10,000 (for parallelism)
Replication: 3
Retention: 7 days
Compression: LZ4
Batch size: 100 KB
```

**Partition Key**: `hash(user_id) % 10000`

### 3. Worker Service

**Architecture**:
```
Worker Instance (1 of 1000s)
├── Kafka Consumer (consumer group)
├── Redis Client (connection pool)
├── Cassandra Client (connection pool)
├── HTTP Clients (APNs, FCM, etc.)
└── Metrics Reporter
```

**Pseudo-code**:
```python
while True:
    messages = kafka.consume(batch_size=100, timeout=1s)
    
    for msg in messages:
        user_id = msg.user_id
        
        # Check cache
        prefs = redis.get(f"prefs:{user_id}")
        if not prefs:
            prefs = cassandra.get(user_id)
            redis.setex(f"prefs:{user_id}", 3600, prefs)
        
        # Check eligibility
        if should_send(prefs, msg):
            send_notification(msg, prefs)
        
    kafka.commit_offsets()
```

**Concurrency**: 100 goroutines per worker

### 4. User Preferences Schema

**Cassandra Table**:
```sql
CREATE TABLE user_preferences (
    user_id bigint PRIMARY KEY,
    channels set<text>,           -- ['push', 'email']
    timezone text,                 -- 'America/New_York'
    quiet_hours_start int,         -- 22 (10 PM)
    quiet_hours_end int,           -- 8 (8 AM)
    opt_out_all boolean,
    opt_out_marketing boolean,
    device_tokens map<text, text>, -- {'ios': 'token1', 'android': 'token2'}
    email text,
    phone text,
    updated_at timestamp
);
```

**Redis Cache**:
```
Key: "prefs:{user_id}"
Value: JSON serialized preferences
TTL: 1 hour
```

### 5. Delivery Services

**Push Notifications**:
```
APNs (iOS):
- Endpoint: api.push.apple.com
- Auth: JWT token
- Batch: 5000/connection
- Retry: 3 attempts

FCM (Android):
- Endpoint: fcm.googleapis.com
- Auth: API key
- Batch: 1000/request
- Retry: Exponential backoff
```

**Email**:
```
SendGrid API:
- Batch: 1000 emails/request
- Rate: 10K/second
- Retry: 5 attempts
```

**SMS**:
```
Twilio API:
- Rate: 100/second per account
- Retry: 3 attempts
- Fallback: AWS SNS
```

## Data Flow Diagrams

### Happy Path
```
API → Kafka → Worker → Redis (cache hit) → FCM → Device
Time: ~100ms
```

### Cache Miss Path
```
API → Kafka → Worker → Redis (miss) → Cassandra → Redis (set) → FCM → Device
Time: ~200ms
```

### Failure Path
```
API → Kafka → Worker → FCM (fail) → Retry Queue → Worker → FCM (success)
Time: ~5s (with retry)
```

## Scaling Numbers

**Per Worker**:
- Processes: 100 msg/sec
- Memory: 512 MB
- CPU: 0.5 core

**For 100K msg/sec**:
- Workers needed: 1000 instances
- Kafka brokers: 10 (10K msg/sec each)
- Redis: 3-node cluster
- Cassandra: 30 nodes (write-heavy)

## Failure Scenarios

| Scenario | Impact | Mitigation |
|----------|--------|------------|
| Kafka broker down | Messages buffered | Replication (3x) |
| Worker crash | Kafka rebalances | Consumer groups |
| Redis down | Higher latency | Read from Cassandra |
| Cassandra node down | Partial unavailability | RF=3, tunable consistency |
| APNs/FCM down | Push delivery fails | Retry queue, circuit breaker |

## Optimization Strategies

### 1. Batching
- API: Accept bulk requests (1000 users)
- Kafka: Batch produce (100 KB)
- Delivery: Batch to FCM (1000/req)

### 2. Caching
- User preferences: 90% cache hit rate
- Device tokens: Cache in Redis
- Templates: Cache formatted messages

### 3. Connection Pooling
- HTTP: Keep-alive connections
- Cassandra: 100 connections/worker
- Redis: 10 connections/worker

### 4. Compression
- Kafka: LZ4 compression (3x)
- Payload: Gzip for large messages

## Monitoring Dashboards

**Real-time Metrics**:
- Messages/sec (line chart)
- Kafka lag (gauge)
- Success rate (percentage)
- Latency (p50, p95, p99)
- Worker CPU/Memory (heat map)

**Alerts**:
- Kafka lag > 10K (critical)
- Success rate < 95% (warning)
- Worker error rate > 5% (warning)
- Latency p99 > 1s (warning)
