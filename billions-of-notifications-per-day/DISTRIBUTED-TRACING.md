# Distributed Tracing & Observability

## Why Trace Every Notification?

**Problem**: When a notification fails, need to answer:
- Where did it fail? (API → Kafka → Worker → Provider)
- How long did each step take?
- What was the exact payload at each stage?
- Which server processed it?

**Solution**: `trace_id` follows notification from entry to delivery receipt

## Trace ID Lifecycle

```
Client Request
    ↓ (Generate trace_id: "tr_abc123xyz")
API Gateway → Kafka → Worker → FCM/APNs → Delivery Receipt
    ↓            ↓        ↓         ↓              ↓
  Log entry   Log entry Log entry Log entry   Log final status
```

**Every log includes**:
- `trace_id` - Unique notification identifier
- `span_id` - Current operation identifier
- `parent_span_id` - Previous operation
- `timestamp` - Precise timing
- `service` - Which component logged this
- `status` - success/failure

## Implementation

### 1. Trace ID Generation (API Gateway)

```python
import uuid
from datetime import datetime
from contextvars import ContextVar

# Thread-safe context for trace_id
trace_context = ContextVar('trace_context', default=None)

class TraceContext:
    def __init__(self, trace_id=None, span_id=None, parent_span_id=None):
        self.trace_id = trace_id or self._generate_trace_id()
        self.span_id = span_id or self._generate_span_id()
        self.parent_span_id = parent_span_id
        self.start_time = datetime.utcnow()
    
    @staticmethod
    def _generate_trace_id():
        """Generate unique trace ID"""
        return f"tr_{uuid.uuid4().hex[:16]}"
    
    @staticmethod
    def _generate_span_id():
        """Generate span ID for current operation"""
        return f"sp_{uuid.uuid4().hex[:8]}"
    
    def create_child_span(self):
        """Create child span for downstream operation"""
        return TraceContext(
            trace_id=self.trace_id,
            span_id=self._generate_span_id(),
            parent_span_id=self.span_id
        )
    
    def to_dict(self):
        return {
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'parent_span_id': self.parent_span_id
        }

class APIGateway:
    async def handle_request(self, request):
        """Entry point - create trace context"""
        
        # Check if trace_id already exists (retry scenario)
        existing_trace_id = request.headers.get('X-Trace-ID')
        
        if existing_trace_id:
            # Client retry - reuse trace_id
            ctx = TraceContext(trace_id=existing_trace_id)
        else:
            # New request - generate trace_id
            ctx = TraceContext()
        
        # Set in context for all downstream operations
        trace_context.set(ctx)
        
        # Log entry
        logger.info(
            "API request received",
            extra={
                'trace_id': ctx.trace_id,
                'span_id': ctx.span_id,
                'service': 'api-gateway',
                'user_id': request.user_id,
                'priority': request.priority,
                'channel': request.channel
            }
        )
        
        try:
            # Process request
            result = await self._process_request(request, ctx)
            
            # Log success
            logger.info(
                "API request accepted",
                extra={
                    'trace_id': ctx.trace_id,
                    'span_id': ctx.span_id,
                    'service': 'api-gateway',
                    'status': 'accepted',
                    'duration_ms': (datetime.utcnow() - ctx.start_time).total_seconds() * 1000
                }
            )
            
            return {'trace_id': ctx.trace_id, 'status': 'queued'}
            
        except Exception as e:
            # Log error
            logger.error(
                "API request failed",
                extra={
                    'trace_id': ctx.trace_id,
                    'span_id': ctx.span_id,
                    'service': 'api-gateway',
                    'error': str(e),
                    'error_type': type(e).__name__
                },
                exc_info=True
            )
            raise
```

### 2. Kafka Message with Trace Context

```python
class KafkaProducer:
    async def send_notification(self, notification, trace_ctx):
        """Send to Kafka with trace context embedded"""
        
        # Create child span for Kafka operation
        kafka_ctx = trace_ctx.create_child_span()
        
        # Embed trace context in message
        message = {
            'notification': notification,
            'trace_context': kafka_ctx.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log before sending
        logger.info(
            "Sending to Kafka",
            extra={
                'trace_id': kafka_ctx.trace_id,
                'span_id': kafka_ctx.span_id,
                'parent_span_id': kafka_ctx.parent_span_id,
                'service': 'kafka-producer',
                'topic': 'notifications',
                'partition': self._get_partition(notification)
            }
        )
        
        try:
            # Send to Kafka
            metadata = await self.producer.send(
                topic='notifications',
                value=message,
                key=notification['user_id']
            )
            
            # Log success
            logger.info(
                "Message sent to Kafka",
                extra={
                    'trace_id': kafka_ctx.trace_id,
                    'span_id': kafka_ctx.span_id,
                    'service': 'kafka-producer',
                    'status': 'sent',
                    'partition': metadata.partition,
                    'offset': metadata.offset
                }
            )
            
        except Exception as e:
            logger.error(
                "Kafka send failed",
                extra={
                    'trace_id': kafka_ctx.trace_id,
                    'span_id': kafka_ctx.span_id,
                    'service': 'kafka-producer',
                    'error': str(e)
                }
            )
            raise
```

### 3. Worker Processing with Trace Propagation

```python
class NotificationWorker:
    async def process_message(self, kafka_message):
        """Process with trace context from Kafka"""
        
        # Extract trace context from message
        trace_data = kafka_message['trace_context']
        ctx = TraceContext(
            trace_id=trace_data['trace_id'],
            span_id=trace_data['span_id'],
            parent_span_id=trace_data['parent_span_id']
        )
        
        # Set in current context
        trace_context.set(ctx)
        
        # Create span for worker processing
        worker_ctx = ctx.create_child_span()
        
        # Log start processing
        logger.info(
            "Worker processing started",
            extra={
                'trace_id': worker_ctx.trace_id,
                'span_id': worker_ctx.span_id,
                'parent_span_id': worker_ctx.parent_span_id,
                'service': 'notification-worker',
                'worker_id': self.worker_id,
                'kafka_offset': kafka_message['offset'],
                'kafka_partition': kafka_message['partition']
            }
        )
        
        try:
            notification = kafka_message['notification']
            
            # Send via provider (propagate trace_id)
            result = await self._send_to_provider(notification, worker_ctx)
            
            # Log completion
            logger.info(
                "Worker processing completed",
                extra={
                    'trace_id': worker_ctx.trace_id,
                    'span_id': worker_ctx.span_id,
                    'service': 'notification-worker',
                    'status': 'completed',
                    'provider': notification['channel'],
                    'duration_ms': (datetime.utcnow() - worker_ctx.start_time).total_seconds() * 1000
                }
            )
            
            # Commit offset
            await self.consumer.commit()
            
        except Exception as e:
            logger.error(
                "Worker processing failed",
                extra={
                    'trace_id': worker_ctx.trace_id,
                    'span_id': worker_ctx.span_id,
                    'service': 'notification-worker',
                    'error': str(e),
                    'retry_count': notification.get('retry_count', 0)
                }
            )
            raise
```

### 4. Provider Adapter with Trace Context

```python
class FCMAdapter:
    async def send(self, notification, trace_ctx):
        """Send via FCM with trace context"""
        
        # Create span for FCM operation
        fcm_ctx = trace_ctx.create_child_span()
        
        # Log before provider call
        logger.info(
            "Sending to FCM",
            extra={
                'trace_id': fcm_ctx.trace_id,
                'span_id': fcm_ctx.span_id,
                'parent_span_id': fcm_ctx.parent_span_id,
                'service': 'fcm-adapter',
                'provider': 'fcm',
                'device_token': notification['device_token'][:10] + '...'  # Truncate for privacy
            }
        )
        
        try:
            # Include trace_id in FCM payload for correlation
            fcm_message = {
                'token': notification['device_token'],
                'notification': {
                    'title': notification['title'],
                    'body': notification['body']
                },
                'data': {
                    'trace_id': fcm_ctx.trace_id,  # For client-side correlation
                    'custom_data': notification.get('data', {})
                }
            }
            
            # Send via FCM
            start = datetime.utcnow()
            response = await self.fcm_client.send(fcm_message)
            duration = (datetime.utcnow() - start).total_seconds() * 1000
            
            # Log success
            logger.info(
                "FCM send successful",
                extra={
                    'trace_id': fcm_ctx.trace_id,
                    'span_id': fcm_ctx.span_id,
                    'service': 'fcm-adapter',
                    'provider': 'fcm',
                    'status': 'sent',
                    'fcm_message_id': response.message_id,
                    'duration_ms': duration
                }
            )
            
            return {'status': 'sent', 'provider_message_id': response.message_id}
            
        except Exception as e:
            # Log provider error
            logger.error(
                "FCM send failed",
                extra={
                    'trace_id': fcm_ctx.trace_id,
                    'span_id': fcm_ctx.span_id,
                    'service': 'fcm-adapter',
                    'provider': 'fcm',
                    'error': str(e),
                    'error_code': getattr(e, 'code', None)
                }
            )
            raise
```

### 5. Delivery Receipt Processing

```python
class DeliveryReceiptHandler:
    async def handle_receipt(self, receipt):
        """Process delivery receipt from FCM/APNs"""
        
        # Extract trace_id from receipt
        trace_id = receipt.get('trace_id')
        
        if not trace_id:
            logger.warning("Delivery receipt without trace_id", extra={'receipt': receipt})
            return
        
        # Create context for receipt processing
        ctx = TraceContext(trace_id=trace_id)
        
        # Log delivery status
        logger.info(
            "Delivery receipt received",
            extra={
                'trace_id': ctx.trace_id,
                'span_id': ctx.span_id,
                'service': 'delivery-receipt-handler',
                'provider': receipt['provider'],
                'status': receipt['status'],  # delivered, failed, etc.
                'provider_message_id': receipt.get('message_id'),
                'delivered_at': receipt.get('timestamp'),
                'error_code': receipt.get('error_code')
            }
        )
        
        # Store in database for analytics
        await self._store_receipt(trace_id, receipt)
```

## Structured Logging Format

**All logs follow this schema**:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "service": "notification-worker",
  "trace_id": "tr_a1b2c3d4e5f6g7h8",
  "span_id": "sp_12345678",
  "parent_span_id": "sp_abcdefgh",
  "message": "Worker processing completed",
  "duration_ms": 234,
  "status": "completed",
  "provider": "fcm",
  "worker_id": "worker-42",
  "kafka_partition": 5,
  "kafka_offset": 123456,
  "user_id": "user_789",
  "priority": "high",
  "region": "us-east-1"
}
```

## Complete Trace Example

**Request**: Send push notification to user_123

```json
// 1. API Gateway receives request
{
  "timestamp": "2024-01-15T10:30:45.000Z",
  "service": "api-gateway",
  "trace_id": "tr_abc123",
  "span_id": "sp_001",
  "message": "API request received",
  "user_id": "user_123",
  "priority": "high",
  "channel": "push"
}

// 2. API Gateway sends to Kafka
{
  "timestamp": "2024-01-15T10:30:45.050Z",
  "service": "kafka-producer",
  "trace_id": "tr_abc123",
  "span_id": "sp_002",
  "parent_span_id": "sp_001",
  "message": "Message sent to Kafka",
  "partition": 5,
  "offset": 123456
}

// 3. Worker picks up from Kafka
{
  "timestamp": "2024-01-15T10:30:45.200Z",
  "service": "notification-worker",
  "trace_id": "tr_abc123",
  "span_id": "sp_003",
  "parent_span_id": "sp_002",
  "message": "Worker processing started",
  "worker_id": "worker-42",
  "kafka_partition": 5,
  "kafka_offset": 123456
}

// 4. FCM adapter sends
{
  "timestamp": "2024-01-15T10:30:45.300Z",
  "service": "fcm-adapter",
  "trace_id": "tr_abc123",
  "span_id": "sp_004",
  "parent_span_id": "sp_003",
  "message": "Sending to FCM",
  "provider": "fcm"
}

// 5. FCM responds
{
  "timestamp": "2024-01-15T10:30:45.534Z",
  "service": "fcm-adapter",
  "trace_id": "tr_abc123",
  "span_id": "sp_004",
  "message": "FCM send successful",
  "status": "sent",
  "fcm_message_id": "fcm_xyz789",
  "duration_ms": 234
}

// 6. Worker completes
{
  "timestamp": "2024-01-15T10:30:45.600Z",
  "service": "notification-worker",
  "trace_id": "tr_abc123",
  "span_id": "sp_003",
  "message": "Worker processing completed",
  "status": "completed",
  "duration_ms": 400
}

// 7. Delivery receipt (from FCM webhook)
{
  "timestamp": "2024-01-15T10:30:46.123Z",
  "service": "delivery-receipt-handler",
  "trace_id": "tr_abc123",
  "span_id": "sp_005",
  "message": "Delivery receipt received",
  "status": "delivered",
  "provider": "fcm",
  "delivered_at": "2024-01-15T10:30:46.000Z"
}
```

**Total journey**: 1.123 seconds from API to delivery confirmation

## Query Traces in Logs

### Find all logs for a trace

```bash
# Using grep
grep "tr_abc123" /var/log/notifications/*.log

# Using Elasticsearch
GET /logs/_search
{
  "query": {
    "term": { "trace_id": "tr_abc123" }
  },
  "sort": [{ "timestamp": "asc" }]
}

# Using CloudWatch Logs Insights
fields @timestamp, service, message, duration_ms, status
| filter trace_id = "tr_abc123"
| sort @timestamp asc
```

### Find failed notifications

```bash
# Elasticsearch
GET /logs/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "service": "fcm-adapter" }},
        { "match": { "status": "failed" }}
      ]
    }
  }
}
```

### Calculate average latency per service

```bash
# CloudWatch Logs Insights
stats avg(duration_ms) by service
| filter trace_id = "tr_abc123"
```

## Tracing with OpenTelemetry

**For more advanced tracing** (optional):

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger import JaegerExporter

# Setup tracer
tracer_provider = TracerProvider()
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831
)
tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

class TracedWorker:
    async def process(self, notification):
        # Create span
        with tracer.start_as_current_span(
            "process_notification",
            attributes={
                "user_id": notification['user_id'],
                "priority": notification['priority']
            }
        ) as span:
            
            # Add events
            span.add_event("Started processing")
            
            result = await self._send(notification)
            
            span.set_attribute("provider", result['provider'])
            span.set_attribute("status", result['status'])
            
            return result
```

## Trace Storage & Retention

**Storage strategy**:

| Data | Storage | Retention |
|------|---------|-----------|
| Hot traces (recent) | Elasticsearch | 7 days |
| Warm traces | S3 (compressed) | 90 days |
| Aggregated metrics | TimescaleDB | 1 year |
| Failed traces | S3 (uncompressed) | 1 year |

**Storage cost** (10B notifications/day):
- 10B × 2KB per trace = 20TB/day
- Compressed (5:1) = 4TB/day
- 7 days hot = 28TB in ES (~$10K/month)
- 90 days warm = 360TB in S3 (~$8K/month)

## Trace-Based Debugging

**Common queries**:

```python
# 1. Find trace by user_id
traces = search_traces(user_id="user_123", last_hours=24)

# 2. Find slow notifications (> 1 second)
slow = search_traces(duration_ms__gt=1000, last_hours=1)

# 3. Find all failures for a provider
failures = search_traces(
    service="fcm-adapter",
    status="failed",
    last_hours=24
)

# 4. Trace a specific notification
trace = get_full_trace("tr_abc123")
print(trace.timeline())  # Shows all spans with timing

# 5. Find traces with specific error
errors = search_traces(
    error_type="ConnectionTimeout",
    provider="fcm"
)
```

## Monitoring Dashboard

**Real-time trace visualization**:

```
Trace Timeline for tr_abc123 (Total: 1.123s)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[0ms]      API Gateway      [50ms]     ✓
           └─ Validation: 20ms
           └─ Auth: 15ms
           └─ Kafka send: 15ms

[200ms]    Worker Pickup    [400ms]    ✓
           └─ Dequeue: 150ms (lag)
           └─ Transform: 30ms
           └─ Send: 220ms

[300ms]    FCM Adapter      [534ms]    ✓
           └─ HTTP call: 234ms

[600ms]    Worker Complete  [600ms]    ✓

[1123ms]   Delivery Receipt [1123ms]   ✓
           └─ Device delivered

Status: SUCCESS
Bottleneck: Worker dequeue (150ms lag)
```

## Alerts Based on Traces

```yaml
alerts:
  - name: HighLatencyTrace
    condition: duration_ms > 5000
    frequency: 1m
    action: page_oncall
    message: "Trace {trace_id} took {duration_ms}ms"
  
  - name: TraceWithoutDeliveryReceipt
    condition: |
      service = "notification-worker" 
      AND status = "completed"
      AND no delivery receipt after 60s
    action: investigate
  
  - name: FailedTraceSpike
    condition: failed_traces > 100/min
    action: auto_scale_workers
```

## Summary

**Trace ID Benefits**:
- ✅ End-to-end visibility (API → delivery)
- ✅ Debug failures quickly (find exact failure point)
- ✅ Calculate latency per component
- ✅ Correlate client and server events
- ✅ Track retries and duplicates
- ✅ SLA monitoring per trace

**Every log includes**: `trace_id`, `span_id`, `service`, `timestamp`, `status`

**Cost**: ~$18K/month for 10B notifications/day (7d hot + 90d warm storage)
