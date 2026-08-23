# Idempotent Message Queue Handler

Demonstrates idempotent message processing for queue-based systems.

## Features

✅ **Automatic Deduplication** - Prevents duplicate message processing  
✅ **At-Least-Once Delivery** - Handles message redelivery safely  
✅ **State Tracking** - Monitors processing status  
✅ **Retry Logic** - Configurable retry with exponential backoff  
✅ **Dead Letter Queue** - Failed messages after max retries  
✅ **Multiple Handlers** - Order processing, email notifications  
✅ **Batch Processing** - Efficient batch operations  

## Architecture

```
Message Queue (SQS/RabbitMQ)
  ↓
Consumer polls for messages
  ↓
Check if message_id processed (Redis)
  ↓
Already processed? → Skip (idempotent)
  ↓
Not processed? → Mark as processing
  ↓
Process message (business logic)
  ↓
Success? → Mark completed, remove from queue
  ↓
Failure? → Retry or send to DLQ
```

## Problem: Duplicate Messages

Message queues often deliver messages multiple times:

1. **Network timeout**: Consumer processed but didn't acknowledge
2. **Visibility timeout**: Message reappears in queue
3. **Queue redelivery**: At-least-once delivery guarantees

**Without idempotency**:
- Order processed twice → double inventory deduction
- Email sent twice → duplicate notifications
- Payment charged twice → angry customers

**With idempotency**:
- Second delivery detected and skipped
- Safe to retry indefinitely
- Consistent system state

## Setup

### Start Redis
```bash
redis-server
```

### Run Handler
```bash
python message_handler.py
```

## Usage

### Basic Handler Implementation

```python
from message_handler import IdempotentMessageHandler, Message

class MyHandler(IdempotentMessageHandler):
    def __init__(self):
        super().__init__(
            handler_name="my_handler",
            dedup_window=3600  # 1 hour
        )
    
    def process_message(self, message: Message) -> None:
        """Your business logic here"""
        print(f"Processing: {message.body}")
        
        # Do work...
        # Idempotency handled automatically!
```

### Publishing Messages

```python
from message_handler import SQSConsumer, OrderMessageHandler

# Create handler and consumer
handler = OrderMessageHandler()
consumer = SQSConsumer("orders", handler)

# Publish message
consumer.publish_message("msg-001", {
    "event_type": "order_created",
    "order_id": "ORD-123",
    "user_id": 1,
    "total": 99.99
})

# Publish duplicate (will be detected)
consumer.publish_message("msg-001", {
    "event_type": "order_created",
    "order_id": "ORD-123",
    "user_id": 1,
    "total": 99.99
})
```

### Consuming Messages

```python
# Start consuming
consumer.consume()

# Output:
# Processing message msg-001
# Order ORD-123 created
# Message msg-001 already processed, skipping
```

### Batch Processing

```python
from message_handler import BatchMessageProcessor, Message

processor = BatchMessageProcessor(handler)

messages = [
    Message("msg-001", {"event": "data1"}),
    Message("msg-002", {"event": "data2"}),
    Message("msg-001", {"event": "data1"}),  # Duplicate
]

stats = processor.process_batch(messages)
print(stats)
# {
#   "total": 3,
#   "processed": 2,
#   "skipped": 1,  # Duplicate detected
#   "failed": 0
# }
```

## Example Handlers

### 1. Order Processing Handler

Handles order lifecycle events idempotently:

```python
handler = OrderMessageHandler()
consumer = SQSConsumer("orders", handler)

# Create order
consumer.publish_message("order-create-001", {
    "event_type": "order_created",
    "order_id": "ORD-123",
    "user_id": 1,
    "total": 99.99
})

# Update order status (idempotent - sets absolute state)
consumer.publish_message("order-update-001", {
    "event_type": "order_updated",
    "order_id": "ORD-123",
    "status": "shipped"
})

# Cancel order (idempotent - already cancelled = no-op)
consumer.publish_message("order-cancel-001", {
    "event_type": "order_cancelled",
    "order_id": "ORD-123"
})
```

**Idempotency guarantees**:
- Duplicate "order_created" → No-op (order exists)
- Duplicate "order_updated" → Sets to same state
- Duplicate "order_cancelled" → No-op (already cancelled)

### 2. Email Notification Handler

Prevents duplicate email sends:

```python
handler = EmailNotificationHandler()
consumer = SQSConsumer("emails", handler)

# Send email
consumer.publish_message("email-001", {
    "email": "user@example.com",
    "subject": "Order Confirmation",
    "content": "Your order has been confirmed"
})

# Duplicate message (same email won't be sent twice)
consumer.publish_message("email-001", {
    "email": "user@example.com",
    "subject": "Order Confirmation",
    "content": "Your order has been confirmed"
})
```

**Deduplication**:
- By message_id: Prevents duplicate processing
- By content fingerprint: Prevents identical emails even with different message IDs

## Key Components

### IdempotentMessageHandler

Base class providing:
- `is_processed()` - Check if message was processed
- `mark_processing()` - Atomic processing lock
- `mark_completed()` - Mark successful processing
- `mark_failed()` - Track failures
- `handle()` - Main entry point with full idempotency logic

### Message States

- **PENDING**: Not yet processed
- **PROCESSING**: Currently being processed (locked)
- **COMPLETED**: Successfully processed
- **FAILED**: Processing failed (max retries exceeded)
- **DEAD_LETTER**: Moved to DLQ

### Deduplication Window

How long to remember processed messages:

```python
IdempotentMessageHandler(
    handler_name="my_handler",
    dedup_window=3600  # 1 hour
)
```

**Guidelines**:
- Short-lived events: 1 hour
- Important operations: 24 hours
- Critical operations: 7 days

After window expires, message ID can be reused (rare in practice).

### Retry Logic

```python
self.max_retries = 3  # Configurable

# On failure:
if attempt_count >= max_retries:
    send_to_dlq()  # Give up
else:
    # Requeue for retry
```

### Dead Letter Queue (DLQ)

Messages that fail after max retries:

```python
def send_to_dlq(self, message: Message, error: str):
    dlq_message = {
        "message_id": message.message_id,
        "body": message.body,
        "error": error,
        "attempt_count": message.attempt_count,
        "failed_at": datetime.utcnow().isoformat()
    }
    redis_client.lpush(f"dlq:{handler_name}", json.dumps(dlq_message))
```

Inspect DLQ:
```python
dlq_messages = redis_client.lrange("dlq:order_handler", 0, -1)
for msg in dlq_messages:
    print(json.loads(msg))
```

## Monitoring

### Get Processing Statistics

```python
from message_handler import get_processing_stats

stats = get_processing_stats("order_handler")
print(stats)
# {
#   "handler_name": "order_handler",
#   "processed_messages": 150,
#   "currently_processing": 2,
#   "dead_letter_queue": 3
# }
```

### Cleanup Old Records

```python
from message_handler import cleanup_old_processed_messages

# Remove records older than 24 hours
cleanup_old_processed_messages("order_handler", older_than_hours=24)
```

## Testing

### Test Deduplication

```python
import pytest
from message_handler import OrderMessageHandler, Message

def test_duplicate_message_handling():
    handler = OrderMessageHandler()
    
    message = Message("test-001", {
        "event_type": "order_created",
        "order_id": "TEST-123",
        "user_id": 1,
        "total": 99.99
    })
    
    # First processing
    result1 = handler.handle(message)
    assert result1 == True
    
    # Second processing (duplicate)
    result2 = handler.handle(message)
    assert result2 == True  # Skipped but returns success
    
    # Verify only one order created
    assert len(handler.orders_db) == 1
```

### Test Concurrent Processing

```python
import concurrent.futures

def test_concurrent_message_processing():
    handler = OrderMessageHandler()
    message = Message("concurrent-001", {
        "event_type": "order_created",
        "order_id": "CONC-123",
        "user_id": 1,
        "total": 99.99
    })
    
    # Process same message concurrently
    with concurrent.futures.ThreadPoolExecutor(10) as executor:
        futures = [executor.submit(handler.handle, message) for _ in range(10)]
        results = [f.result() for f in futures]
    
    # One succeeded, others skipped
    assert sum(results) >= 1
    # Only one order created
    assert len(handler.orders_db) == 1
```

### Test Retry Logic

```python
def test_retry_and_dlq():
    class FailingHandler(IdempotentMessageHandler):
        def __init__(self):
            super().__init__("failing_handler")
            self.max_retries = 2
            self.attempt = 0
        
        def process_message(self, message):
            self.attempt += 1
            if self.attempt < 3:
                raise Exception("Simulated failure")
            # Success on 3rd attempt
    
    handler = FailingHandler()
    message = Message("retry-001", {"data": "test"})
    
    # First attempt - fails
    result1 = handler.handle(message)
    assert result1 == False
    
    # Second attempt - fails
    result2 = handler.handle(message)
    assert result2 == False
    
    # Third attempt - exceeds max_retries, goes to DLQ
    result3 = handler.handle(message)
    assert result3 == False
    
    # Check DLQ
    dlq_count = redis_client.llen("dlq:failing_handler")
    assert dlq_count == 1
```

## Comparison with Other Implementations

| Feature | Message Queue | Payment Service | API Service |
|---------|--------------|-----------------|-------------|
| Primary Use | Async message processing | Synchronous payments | REST API endpoints |
| Deduplication | By message ID | By idempotency key | By idempotency key |
| Storage | Redis (TTL-based) | Redis + PostgreSQL | Redis only |
| Retry Logic | Built-in with DLQ | Manual retry | Automatic (middleware) |
| Batch Support | Yes | No | No |
| State Tracking | Processing/Completed/Failed | Processing/Completed/Failed | Processing/Completed |

## Real-World Scenarios

### Scenario 1: Order Processing Pipeline

```
Order Created Event
  ↓
Order Handler (idempotent)
  → Create order record
  → Reserve inventory
  → Emit "OrderReserved" event
  ↓
Payment Handler (idempotent)
  → Process payment
  → Emit "PaymentCompleted" event
  ↓
Notification Handler (idempotent)
  → Send confirmation email
  → Send SMS
```

Each handler is idempotent - safe to replay entire pipeline.

### Scenario 2: Event Sourcing

```python
class EventSourcingHandler(IdempotentMessageHandler):
    def process_message(self, message: Message) -> None:
        event_id = message.message_id
        
        # Event IDs are naturally idempotent
        if self.event_store.exists(event_id):
            return  # Already applied
        
        # Apply event
        self.apply_event(message.body)
        self.event_store.save(event_id, message.body)
```

### Scenario 3: Webhook Processing

```python
class WebhookHandler(IdempotentMessageHandler):
    def process_message(self, message: Message) -> None:
        webhook_data = message.body
        
        # Process webhook idempotently
        self.process_webhook(webhook_data)
        
        # Send acknowledgment (only once)
        self.send_ack(webhook_data['callback_url'])
```

## Best Practices

1. **Always use message IDs**: Ensure unique, stable IDs
2. **Set appropriate dedup window**: Balance memory vs safety
3. **Monitor DLQ**: Alert on DLQ growth
4. **Idempotent business logic**: State transitions, not increments
5. **Handle failures gracefully**: Retry with backoff
6. **Test with duplicates**: Simulate redelivery scenarios
7. **Clean up old records**: Prevent memory leaks

## Production Considerations

1. **Visibility Timeout**: Set longer than processing time
2. **Batch Size**: Balance throughput vs latency
3. **Concurrency**: Run multiple consumers for scale
4. **Monitoring**: Track processing rates, errors, DLQ size
5. **Alerting**: Alert on high DLQ or stuck messages
6. **Backpressure**: Handle slow consumers gracefully

## Next Steps

- See `../payment_service/` for synchronous idempotency
- See `../api_service/` for REST API patterns
- See `../../03_PATTERNS.md` for more patterns
- See `../../04_BEST_PRACTICES.md` for production guidelines
