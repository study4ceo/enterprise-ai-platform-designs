# Priority System for Notifications

## Priority Levels

```
CRITICAL  - Security alerts, payment failures (< 100ms)
HIGH      - Messages, calls, time-sensitive (< 500ms)
MEDIUM    - Updates, reminders (< 5s)
LOW       - Marketing, newsletters (< 30s)
```

## Implementation

### 1. Separate Kafka Topics

```
notifications-critical  (100 partitions, 3 replicas)
notifications-high      (1000 partitions, 3 replicas)
notifications-medium    (5000 partitions, 2 replicas)
notifications-low       (4000 partitions, 2 replicas)
```

**Why separate topics?**
- Isolation: Low priority doesn't block critical
- Different SLAs per topic
- Independent scaling
- Easy to drop low priority during overload

### 2. Worker Allocation

```
Total workers: 1000

CRITICAL: 100 workers (10%)  - Always available
HIGH:     400 workers (40%)  - Primary focus
MEDIUM:   300 workers (30%)
LOW:      200 workers (20%)  - Scale down under load
```

**Auto-scaling rules**:
```
IF kafka_lag(critical) > 100 THEN scale_up(critical_workers)
IF kafka_lag(low) > 100K THEN pause(low_workers)
```

### 3. API Request

```json
POST /api/notifications
{
  "user_ids": [123, 456],
  "type": "push",
  "priority": "high",  // critical, high, medium, low
  "title": "New message",
  "body": "You have a new message",
  "ttl": 3600  // Time-to-live in seconds
}
```

### 4. Routing Logic

```python
def route_to_topic(notification):
    priority = notification.get('priority', 'medium')
    
    topic_map = {
        'critical': 'notifications-critical',
        'high': 'notifications-high',
        'medium': 'notifications-medium',
        'low': 'notifications-low'
    }
    
    return topic_map[priority]
```

### 5. Worker Processing Priority

Each worker consumes from multiple topics with priority:

```go
// Worker subscribes to topics with priority
consumer.Subscribe([]string{
    "notifications-critical",  // Weight: 50
    "notifications-high",      // Weight: 30
    "notifications-medium",    // Weight: 15
    "notifications-low",       // Weight: 5
})

// Kafka consumer will poll proportionally
```

## Priority-Based Features

### 1. TTL (Time-to-Live)

```python
if time.now() - notification.created_at > notification.ttl:
    # Drop expired notification
    metrics.increment('expired_notifications')
    return
```

**Default TTL by priority**:
- CRITICAL: 5 minutes
- HIGH: 1 hour
- MEDIUM: 24 hours
- LOW: 7 days

### 2. Rate Limiting by Priority

```
CRITICAL: No limit (always sent)
HIGH:     1000/min per user
MEDIUM:   100/min per user
LOW:      10/min per user
```

### 3. Retry Strategy by Priority

```
CRITICAL:
  Retry 1: Immediate
  Retry 2: +1s
  Retry 3: +5s
  Max: 3 attempts

HIGH:
  Retry 1: +5s
  Retry 2: +30s
  Retry 3: +5min
  Max: 3 attempts

MEDIUM/LOW:
  Retry 1: +1min
  Retry 2: +10min
  Max: 2 attempts
```

### 4. Dead Letter Queue by Priority

```
DLQ critical → Alert immediately → Page oncall
DLQ high     → Alert in 5 min
DLQ medium   → Log only
DLQ low      → Ignore
```

## Overload Protection

### Scenario: 10x traffic spike

**Strategy**:
1. **Maintain critical**: Always process
2. **Throttle low**: Drop or delay significantly
3. **Scale workers**: Add high/medium workers
4. **Shed load**: Reject low priority at API

```python
if system_load > 90%:
    if priority == 'low':
        return {"error": "Service overloaded", "retry_after": 3600}
```

## Monitoring by Priority

**Metrics per priority**:
- Messages/sec
- Kafka lag
- Processing latency (p50, p99)
- Success rate
- Drop rate

**Alerts**:
```
CRITICAL lag > 10      → Page immediately
HIGH lag > 1000        → Alert in 1 min
MEDIUM lag > 10000     → Alert in 5 min
LOW lag > 100000       → No alert
```

## Cost Optimization

**Resource allocation**:
- Critical: Over-provision (99.99% uptime)
- High: Right-sized (99.9% uptime)
- Medium: Under-provision (99% uptime)
- Low: Minimal resources (95% uptime)

**Kafka retention**:
- Critical: 7 days (compliance)
- High: 3 days
- Medium: 1 day
- Low: 12 hours

## Priority Examples

```
CRITICAL:
- "Your account was accessed from new device"
- "Payment failed for subscription"
- "Security alert: password changed"

HIGH:
- "New message from John"
- "Incoming call from Jane"
- "Your order is out for delivery"

MEDIUM:
- "Your post got 10 likes"
- "Reminder: Meeting in 1 hour"
- "Weekly summary ready"

LOW:
- "Check out our new features"
- "Here are some recommendations"
- "Monthly newsletter"
```

## Summary

**Key decisions**:
1. ✅ Separate Kafka topics per priority
2. ✅ Dedicated worker pools
3. ✅ Different SLAs and TTLs
4. ✅ Priority-based retry logic
5. ✅ Overload protection (drop low first)

**Trade-offs**:
- More complex (4 topics vs 1)
- Higher operational overhead
- Better user experience for critical notifications
