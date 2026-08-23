# Batch Processing Pipeline

## Why Batching?

**Without batching**:
- 10B notifications = 10B individual API calls
- FCM allows 1000/request → Waste of 999 potential slots
- Network overhead per request
- Rate limits hit faster

**With batching**:
- 10B notifications = 10M batch API calls (1000× reduction)
- Better throughput
- Lower latency overall
- Cost savings

## Batch Sizes by Provider

| Provider | Max Batch Size | Recommendation |
|----------|---------------|----------------|
| FCM (Android) | 1000 | 500-1000 |
| APNs (iOS) | 5000/connection | 1000-2000 |
| SendGrid (Email) | 1000 | 1000 |
| SES (Email) | 50 | 50 |
| Twilio (SMS) | 1 (no batch) | N/A |
| SNS (SMS) | 10 | 10 |

## Batch Processing Architecture

```
Kafka → Worker → Batch Aggregator → Batch Sender → Provider
          ↓            ↓                  ↓
      (consumes)  (groups by)        (flushes)
      100 msgs    provider/region    every 1s or
                                     when full
```

## Implementation

### 1. Batch Aggregator

```python
class BatchAggregator:
    """Collects notifications into batches before sending"""
    
    def __init__(self, max_batch_size=1000, max_wait_seconds=1.0):
        self.max_batch_size = max_batch_size
        self.max_wait_seconds = max_wait_seconds
        
        # Batches organized by provider and region
        self.batches = defaultdict(lambda: {
            'notifications': [],
            'first_added_at': None
        })
    
    async def add(self, notification):
        """Add notification to appropriate batch"""
        key = self._get_batch_key(notification)
        batch = self.batches[key]
        
        if not batch['first_added_at']:
            batch['first_added_at'] = time.time()
        
        batch['notifications'].append(notification)
        
        # Flush if batch full or timeout
        if len(batch['notifications']) >= self.max_batch_size:
            await self._flush_batch(key)
        elif time.time() - batch['first_added_at'] >= self.max_wait_seconds:
            await self._flush_batch(key)
    
    def _get_batch_key(self, notification):
        """Group by provider, platform, and region"""
        return f"{notification.channel}:{notification.platform}:{notification.region}"
    
    async def _flush_batch(self, key):
        """Send batch to provider"""
        batch = self.batches[key]
        if not batch['notifications']:
            return
        
        notifications = batch['notifications']
        batch['notifications'] = []
        batch['first_added_at'] = None
        
        await self._send_batch(key, notifications)
    
    async def _send_batch(self, key, notifications):
        channel, platform, region = key.split(':')
        adapter = adapter_factory.get_adapter(channel, platform, region)
        
        if adapter.supports_batch():
            await adapter.send_batch(notifications)
        else:
            # Send individually for non-batch providers
            await asyncio.gather(*[adapter.send(n) for n in notifications])
```

### 2. Worker with Batching

```python
class BatchWorker:
    """Worker that consumes from Kafka and batches before sending"""
    
    def __init__(self):
        self.kafka_consumer = KafkaConsumer('notifications')
        self.batch_aggregator = BatchAggregator(
            max_batch_size=1000,
            max_wait_seconds=1.0
        )
        self.running = True
    
    async def run(self):
        # Start flush timer
        asyncio.create_task(self._periodic_flush())
        
        while self.running:
            # Consume in mini-batches from Kafka
            messages = self.kafka_consumer.poll(
                timeout_ms=100,
                max_records=500
            )
            
            for message in messages:
                notification = parse_notification(message)
                await self.batch_aggregator.add(notification)
            
            # Commit offsets after processing
            self.kafka_consumer.commit()
    
    async def _periodic_flush(self):
        """Flush batches periodically to avoid timeout"""
        while self.running:
            await asyncio.sleep(0.5)  # Check every 500ms
            await self.batch_aggregator.flush_all()
```

### 3. FCM Batch Adapter

```python
class FCMBatchAdapter:
    """FCM adapter with batch support"""
    
    def __init__(self):
        self.url = 'https://fcm.googleapis.com/v1/projects/PROJECT/messages:send'
        self.max_batch_size = 1000
    
    async def send_batch(self, notifications):
        """Send up to 1000 notifications in one request"""
        
        # FCM batch format
        requests = []
        for notif in notifications[:self.max_batch_size]:
            requests.append({
                'message': {
                    'token': notif.device_token,
                    'notification': {
                        'title': notif.title,
                        'body': notif.body
                    },
                    'data': notif.data
                }
            })
        
        # Send batch request
        response = await self.http_client.post(
            f'{self.url}/batch',
            json={'requests': requests}
        )
        
        return self._parse_batch_response(response)
    
    def _parse_batch_response(self, response):
        """Handle partial failures in batch"""
        results = []
        for i, result in enumerate(response.json()['responses']):
            if result.get('error'):
                # Individual failure - retry or DLQ
                results.append({
                    'index': i,
                    'success': False,
                    'error': result['error']
                })
            else:
                results.append({
                    'index': i,
                    'success': True,
                    'message_id': result['name']
                })
        
        return results
```

### 4. APNs Batch Adapter

```python
class APNsBatchAdapter:
    """APNs uses HTTP/2 multiplexing for batch"""
    
    def __init__(self):
        self.connections = []  # Pool of HTTP/2 connections
        self.max_per_connection = 5000
    
    async def send_batch(self, notifications):
        """Send using HTTP/2 multiplexing"""
        
        # Split into chunks per connection
        chunk_size = self.max_per_connection
        chunks = [notifications[i:i+chunk_size] 
                  for i in range(0, len(notifications), chunk_size)]
        
        tasks = []
        for chunk in chunks:
            connection = self._get_connection()
            tasks.append(self._send_chunk(connection, chunk))
        
        results = await asyncio.gather(*tasks)
        return [r for sublist in results for r in sublist]
    
    async def _send_chunk(self, connection, notifications):
        """Send multiple notifications over one connection"""
        # HTTP/2 allows concurrent requests
        tasks = [
            self._send_single(connection, notif)
            for notif in notifications
        ]
        return await asyncio.gather(*tasks)
```

## Batching Strategies

### Strategy 1: Time-based Batching

```python
# Flush every 1 second regardless of batch size
await asyncio.sleep(1.0)
flush_batch()
```

**Use**: Low volume, latency not critical

### Strategy 2: Size-based Batching

```python
# Flush when batch reaches 1000
if len(batch) >= 1000:
    flush_batch()
```

**Use**: High volume, maximize throughput

### Strategy 3: Hybrid (Recommended)

```python
# Flush if full OR after 1 second
if len(batch) >= 1000 or time_since_first_add >= 1.0:
    flush_batch()
```

**Use**: Balance latency and throughput

### Strategy 4: Priority-aware Batching

```python
# Critical: Batch of 100 or 100ms
# High: Batch of 500 or 500ms
# Medium: Batch of 1000 or 1s
# Low: Batch of 1000 or 5s

def get_batch_params(priority):
    params = {
        'critical': (100, 0.1),
        'high': (500, 0.5),
        'medium': (1000, 1.0),
        'low': (1000, 5.0)
    }
    return params[priority]
```

## Pipeline Flow

```
Stage 1: Kafka Consumer
├── Poll 500 messages
├── Takes 10ms
└── Rate: 50K msg/sec per worker

Stage 2: Batch Aggregator
├── Group by provider/region/platform
├── Hold for max 1 second
└── Batch size: 1000

Stage 3: Batch Sender
├── Send to provider API
├── Takes 50-100ms per batch
└── Throughput: 10-20K notifications/sec per batch

Total Pipeline:
├── 1000 workers
├── Each processes 10K msg/sec
└── Total: 10M msg/sec (864B per day)
```

## Handling Partial Failures

```python
class PartialFailureHandler:
    """Handle when some notifications in batch fail"""
    
    async def handle_batch_response(self, batch, results):
        successes = []
        failures = []
        
        for i, result in enumerate(results):
            if result['success']:
                successes.append(batch[i])
            else:
                failures.append({
                    'notification': batch[i],
                    'error': result['error']
                })
        
        # Log successes
        metrics.increment('batch_success', len(successes))
        
        # Retry failures individually
        for failure in failures:
            await self._retry_single(failure['notification'])
    
    async def _retry_single(self, notification):
        """Retry failed notification individually"""
        notification.attempt_count += 1
        
        if notification.attempt_count <= 3:
            # Re-add to batch queue
            await batch_aggregator.add(notification)
        else:
            # Send to DLQ
            await dlq.send(notification)
```

## Batch Metrics

```python
# Track batch efficiency
metrics = {
    'batch_size_histogram': [100, 500, 1000],  # Distribution
    'batch_wait_time_p99': 950,  # milliseconds
    'batch_utilization': 0.85,   # 85% of max batch size
    'partial_failure_rate': 0.02 # 2% of batches have failures
}
```

**Alerts**:
```
WARN: batch_utilization < 0.5  (Batches too small)
WARN: batch_wait_time_p99 > 2000  (Batches waiting too long)
CRITICAL: partial_failure_rate > 0.1  (10% batches failing)
```

## Optimization Tips

### 1. Pre-sorting for Better Batching

```python
# Kafka partitioning by platform increases batch efficiency
partition_key = f"{user_id}:{platform}"  # Same platform together
```

### 2. Dynamic Batch Sizing

```python
def get_dynamic_batch_size(current_load):
    """Adjust batch size based on system load"""
    if current_load > 0.9:
        return 1000  # Max throughput
    elif current_load < 0.3:
        return 100   # Lower latency
    else:
        return 500   # Balanced
```

### 3. Connection Pooling

```python
# Reuse HTTP/2 connections for batches
connection_pool = ConnectionPool(
    max_connections=100,
    max_requests_per_connection=5000
)
```

## Cost Savings

**Example calculation**:
```
Without batching:
- 10B notifications
- 10B API calls
- Network overhead: 1KB/request
- Total data: 10TB
- Cost: $900 (egress) + API costs

With batching (1000/batch):
- 10B notifications
- 10M API calls (1000× less)
- Network overhead: 1KB/batch + 0.1KB/notification
- Total data: 1GB + 1TB = 1.01TB
- Cost: $90 (egress) + API costs

Savings: $810 in network costs
```

## Summary

**Batching strategy**:
1. ✅ **Hybrid approach** - Size (1000) OR Time (1s)
2. ✅ **Priority-aware** - Critical smaller batches, faster
3. ✅ **Provider-specific** - FCM 1000, APNs 5000
4. ✅ **Partial failure handling** - Retry individual failures
5. ✅ **Dynamic sizing** - Adjust based on load

**Performance**:
- **Throughput**: 50K msg/sec → 10M msg/sec (200× improvement)
- **Latency**: p99 < 1s (acceptable for most notifications)
- **Cost**: 90% reduction in network overhead

**Trade-off**: Slight latency increase (max 1s) for massive throughput gain
