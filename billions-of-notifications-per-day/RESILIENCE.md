# Circuit Breakers & Backpressure

## Why Needed?

**Without protection**:
- FCM down → Workers keep retrying → Kafka lag grows → System overload
- Kafka slow → Workers pile up messages → Memory exhausted
- Cascading failures across entire system

**With protection**:
- Circuit breaker: Fail fast when downstream is down
- Backpressure: Slow down when system overloaded

## Circuit Breaker Pattern

### States

```
CLOSED (Normal)
  ↓ (failures > threshold)
OPEN (Failing fast)
  ↓ (after timeout)
HALF_OPEN (Testing)
  ↓ (success) → CLOSED
  ↓ (failure) → OPEN
```

### Implementation

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold=5,      # Open after 5 failures
        success_threshold=2,      # Close after 2 successes in half-open
        timeout=60,               # Try again after 60 seconds
        window_size=10            # Track last 10 requests
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.window_size = window_size
        
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None
        self.recent_requests = []
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.successes = 0
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise
    
    def _record_success(self):
        self.recent_requests.append(('success', datetime.now()))
        self._trim_window()
        
        if self.state == CircuitState.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failures = 0
        
        self.failures = 0  # Reset consecutive failures
    
    def _record_failure(self):
        self.recent_requests.append(('failure', datetime.now()))
        self._trim_window()
        
        self.failures += 1
        self.last_failure_time = datetime.now()
        
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self):
        if not self.last_failure_time:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.timeout
    
    def _trim_window(self):
        """Keep only recent requests in window"""
        if len(self.recent_requests) > self.window_size:
            self.recent_requests = self.recent_requests[-self.window_size:]
    
    def get_stats(self):
        recent_failures = sum(1 for r in self.recent_requests if r[0] == 'failure')
        return {
            'state': self.state.value,
            'failures': self.failures,
            'recent_failure_rate': recent_failures / max(len(self.recent_requests), 1)
        }
```

### Per-Provider Circuit Breakers

```python
class ProviderCircuitBreakers:
    """Circuit breaker for each provider"""
    
    def __init__(self):
        self.breakers = {
            'fcm': CircuitBreaker(failure_threshold=5, timeout=60),
            'apns': CircuitBreaker(failure_threshold=5, timeout=60),
            'sendgrid': CircuitBreaker(failure_threshold=3, timeout=30),
            'twilio': CircuitBreaker(failure_threshold=3, timeout=30)
        }
    
    async def send_with_breaker(self, provider, notification):
        breaker = self.breakers[provider]
        
        try:
            return breaker.call(self._send, provider, notification)
        except CircuitBreakerOpenError:
            # Circuit open - try fallback provider
            metrics.increment(f'{provider}_circuit_open')
            return await self._send_fallback(provider, notification)
    
    async def _send_fallback(self, primary_provider, notification):
        """Use fallback when primary circuit is open"""
        fallbacks = {
            'fcm': 'hms',
            'sendgrid': 'ses',
            'twilio': 'sns'
        }
        
        fallback_provider = fallbacks.get(primary_provider)
        if not fallback_provider:
            raise NoFallbackAvailableError()
        
        logger.warning(f"Using fallback {fallback_provider} for {primary_provider}")
        return await self._send(fallback_provider, notification)
```

## Backpressure Mechanisms

### 1. Kafka Lag Monitoring & Auto-scaling

**Consumer lag** = Messages in topic - Messages consumed

```python
class KafkaLagMonitor:
    """Monitor consumer lag and trigger auto-scaling"""
    
    def __init__(self, consumer_group='notification-workers'):
        self.consumer_group = consumer_group
        self.kafka_admin = KafkaAdminClient()
        self.auto_scaler = WorkerAutoScaler()
        
        # Thresholds
        self.lag_warning = 1000      # Scale up
        self.lag_critical = 10000    # Scale up aggressively + backpressure
        self.lag_emergency = 100000  # Emergency mode
    
    async def monitor_loop(self):
        """Continuously monitor lag"""
        while True:
            lag_stats = await self.get_consumer_lag()
            await self.handle_lag(lag_stats)
            await asyncio.sleep(10)  # Check every 10 seconds
    
    async def get_consumer_lag(self):
        """Get lag for all partitions"""
        lag_by_partition = {}
        
        # Get committed offsets
        committed = self.kafka_admin.list_consumer_group_offsets(
            self.consumer_group
        )
        
        # Get high watermark (latest offset)
        watermarks = self.kafka_admin.get_topic_watermarks('notifications')
        
        total_lag = 0
        for partition, offset in committed.items():
            high_water = watermarks[partition]['high']
            lag = high_water - offset
            lag_by_partition[partition] = lag
            total_lag += lag
        
        return {
            'total_lag': total_lag,
            'avg_lag': total_lag / len(lag_by_partition),
            'max_lag': max(lag_by_partition.values()),
            'by_partition': lag_by_partition
        }
    
    async def handle_lag(self, lag_stats):
        """Take action based on lag"""
        total_lag = lag_stats['total_lag']
        
        if total_lag < self.lag_warning:
            # Normal operation
            metrics.gauge('kafka_lag', total_lag, tags=['status:ok'])
            return
        
        elif total_lag < self.lag_critical:
            # Warning - scale up gradually
            logger.warning(f"Kafka lag: {total_lag}, scaling up")
            await self.auto_scaler.scale_up(factor=1.2)  # Add 20% workers
            metrics.gauge('kafka_lag', total_lag, tags=['status:warning'])
        
        elif total_lag < self.lag_emergency:
            # Critical - scale up aggressively + signal backpressure
            logger.error(f"Critical lag: {total_lag}, scaling up aggressively")
            await self.auto_scaler.scale_up(factor=2.0)  # Double workers
            await self.signal_backpressure_upstream()
            metrics.gauge('kafka_lag', total_lag, tags=['status:critical'])
        
        else:
            # Emergency - max scale + drop low priority
            logger.critical(f"Emergency lag: {total_lag}, emergency mode")
            await self.auto_scaler.scale_to_max()
            await self.signal_backpressure_upstream(aggressive=True)
            await self.enable_load_shedding()
            metrics.gauge('kafka_lag', total_lag, tags=['status:emergency'])
    
    async def signal_backpressure_upstream(self, aggressive=False):
        """Signal API gateway to slow down"""
        if aggressive:
            # Drop low priority at API level
            await api_gateway.set_rate_limit('low', rate=0)
            await api_gateway.set_rate_limit('medium', rate=100)
        else:
            # Reduce all priorities
            await api_gateway.reduce_rate_limit(factor=0.5)
        
        logger.warning("Backpressure signal sent to API gateway")
```

### 2. Worker Auto-scaling

```python
class WorkerAutoScaler:
    """Auto-scale workers based on Kafka lag"""
    
    def __init__(self):
        self.current_workers = 1000
        self.min_workers = 500
        self.max_workers = 5000
        self.scaling_cooldown = 60  # seconds
        self.last_scale_time = 0
    
    async def scale_up(self, factor=1.5):
        """Scale up by factor"""
        if not self._can_scale():
            logger.info("In cooldown period, skipping scale")
            return
        
        new_count = min(
            int(self.current_workers * factor),
            self.max_workers
        )
        
        if new_count > self.current_workers:
            await self._execute_scale(new_count)
    
    async def scale_down(self, factor=0.8):
        """Scale down by factor"""
        if not self._can_scale():
            return
        
        new_count = max(
            int(self.current_workers * factor),
            self.min_workers
        )
        
        if new_count < self.current_workers:
            await self._execute_scale(new_count)
    
    async def scale_to_max(self):
        """Emergency scale to maximum"""
        logger.critical("Scaling to maximum workers")
        await self._execute_scale(self.max_workers, ignore_cooldown=True)
    
    async def _execute_scale(self, new_count, ignore_cooldown=False):
        """Execute scaling via Kubernetes/ECS"""
        if not ignore_cooldown and not self._can_scale():
            return
        
        logger.info(f"Scaling from {self.current_workers} to {new_count}")
        
        # Kubernetes example
        await k8s_client.scale_deployment(
            name='notification-workers',
            replicas=new_count
        )
        
        self.current_workers = new_count
        self.last_scale_time = time.time()
        
        metrics.gauge('worker_count', new_count)
        metrics.increment('scaling_events')
    
    def _can_scale(self):
        """Check if cooldown period has passed"""
        elapsed = time.time() - self.last_scale_time
        return elapsed >= self.scaling_cooldown
    
    async def get_optimal_worker_count(self, lag, processing_rate):
        """Calculate optimal workers based on lag"""
        # Processing rate: messages per worker per second
        # Target: Clear lag in 5 minutes
        
        target_clear_time = 300  # 5 minutes
        required_rate = lag / target_clear_time
        required_workers = required_rate / processing_rate
        
        return min(int(required_workers * 1.2), self.max_workers)  # 20% buffer
```

### 3. Kubernetes HPA (Horizontal Pod Autoscaler)

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: notification-worker-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: notification-workers
  minReplicas: 500
  maxReplicas: 5000
  metrics:
  - type: External
    external:
      metric:
        name: kafka_consumer_lag
        selector:
          matchLabels:
            topic: notifications
      target:
        type: AverageValue
        averageValue: 1000  # Target lag per worker
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
      - type: Percent
        value: 100        # Can double quickly
        periodSeconds: 30
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
      - type: Percent
        value: 20         # Scale down slowly
        periodSeconds: 60
```

### 4. API Gateway Rate Limiting (Backpressure Signal)

```python
class BackpressureAwareAPIGateway:
    """API Gateway that responds to backpressure signals"""
    
    def __init__(self):
        self.base_rate_limits = {
            'critical': float('inf'),  # Unlimited
            'high': 10000,             # 10K/sec
            'medium': 5000,
            'low': 1000
        }
        self.current_rate_limits = self.base_rate_limits.copy()
        self.backpressure_active = False
    
    async def handle_request(self, request):
        """Check rate limit before accepting request"""
        priority = request.priority
        
        # Check current rate limit
        if not await self._check_rate_limit(priority):
            return Response(
                status=429,
                body={'error': 'Rate limit exceeded', 'retry_after': 60}
            )
        
        # Enqueue to Kafka
        await kafka_producer.send('notifications', request)
        return Response(status=202, body={'status': 'queued'})
    
    async def apply_backpressure(self, factor=0.5):
        """Reduce rate limits due to backpressure"""
        logger.warning(f"Applying backpressure: {factor}x reduction")
        
        for priority in ['low', 'medium', 'high']:
            self.current_rate_limits[priority] = int(
                self.base_rate_limits[priority] * factor
            )
        
        self.backpressure_active = True
        metrics.gauge('backpressure_factor', factor)
    
    async def release_backpressure(self):
        """Restore normal rate limits"""
        logger.info("Releasing backpressure")
        self.current_rate_limits = self.base_rate_limits.copy()
        self.backpressure_active = False
        metrics.gauge('backpressure_factor', 1.0)
    
    async def drop_priority(self, priority):
        """Completely drop requests of certain priority"""
        logger.critical(f"Dropping all {priority} priority requests")
        self.current_rate_limits[priority] = 0
```

### 5. Kafka Consumer Backpressure

```python
class BackpressureAwareConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer('notifications')
        self.max_pending = 1000  # Max unprocessed messages
        self.pending_count = 0
        self.paused = False
    
    async def consume(self):
        while True:
            # Check if we should pause consumption
            if self.pending_count > self.max_pending and not self.paused:
                self.consumer.pause()
                self.paused = True
                logger.warning("Consumer PAUSED - too many pending messages")
                metrics.increment('consumer_paused')
            
            # Resume if queue is draining
            if self.pending_count < self.max_pending * 0.5 and self.paused:
                self.consumer.resume()
                self.paused = False
                logger.info("Consumer RESUMED")
                metrics.increment('consumer_resumed')
            
            # Poll messages
            messages = self.consumer.poll(timeout_ms=100, max_records=100)
            
            for message in messages:
                self.pending_count += 1
                await self._process_message(message)
                self.pending_count -= 1
    
    async def _process_message(self, message):
        """Process with backpressure awareness"""
        await process_notification(message)
```

### 5. Kafka Consumer Backpressure

```python
class BackpressureAwareConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer('notifications')
        self.max_pending = 1000  # Max unprocessed messages
        self.pending_count = 0
        self.paused = False
        self.lag_monitor = KafkaLagMonitor()
    
    async def consume(self):
        # Start lag monitoring in background
        asyncio.create_task(self.lag_monitor.monitor_loop())
        
        while True:
            # Check local backpressure
            if self.pending_count > self.max_pending and not self.paused:
                self.consumer.pause()
                self.paused = True
                logger.warning("Consumer PAUSED - too many pending messages")
                metrics.increment('consumer_paused')
            
            # Resume if queue is draining
            if self.pending_count < self.max_pending * 0.5 and self.paused:
                self.consumer.resume()
                self.paused = False
                logger.info("Consumer RESUMED")
                metrics.increment('consumer_resumed')
            
            # Poll messages
            messages = self.consumer.poll(timeout_ms=100, max_records=100)
            
            for message in messages:
                self.pending_count += 1
                await self._process_message(message)
                self.pending_count -= 1
    
    async def _process_message(self, message):
        """Process with backpressure awareness"""
        await process_notification(message)
```

### 6. Complete Backpressure Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Backpressure Flow                        │
└─────────────────────────────────────────────────────────────┘

Kafka Lag > 10K
    ↓
Workers detect lag
    ↓
┌───────────────────────────┬────────────────────────────┐
│   Scale Up Workers        │   Signal Upstream          │
│   (Auto-scaler)           │   (API Gateway)            │
└───────────────────────────┴────────────────────────────┘
    ↓                              ↓
More workers consume          Reduce API rate limits
    ↓                              ↓
Lag decreases                 Less load on Kafka
    ↓                              ↓
When lag < 1K: Scale down + Release backpressure upstream
```

### 7. Lag-Based Metrics & Alerts

```python
class LagMetrics:
    """Comprehensive lag monitoring"""
    
    def collect_metrics(self):
        lag_stats = lag_monitor.get_consumer_lag()
        
        return {
            # Lag metrics
            'kafka.lag.total': lag_stats['total_lag'],
            'kafka.lag.avg_per_partition': lag_stats['avg_lag'],
            'kafka.lag.max_partition': lag_stats['max_lag'],
            
            # Processing metrics
            'processing.rate': self._get_processing_rate(),
            'processing.time_to_clear': self._estimate_clear_time(lag_stats),
            
            # Worker metrics
            'workers.current_count': auto_scaler.current_workers,
            'workers.utilization': self._get_worker_utilization(),
            
            # Backpressure status
            'backpressure.active': api_gateway.backpressure_active,
            'backpressure.paused_partitions': self._count_paused_partitions()
        }
    
    def _estimate_clear_time(self, lag_stats):
        """Estimate time to clear current lag"""
        total_lag = lag_stats['total_lag']
        processing_rate = self._get_processing_rate()
        
        if processing_rate == 0:
            return float('inf')
        
        return total_lag / processing_rate  # seconds
```

**Alert Rules**:
```yaml
alerts:
  - name: KafkaLagWarning
    condition: kafka.lag.total > 1000
    severity: warning
    actions:
      - auto_scale_workers: factor=1.2
    message: "Kafka lag {lag}, scaling up workers"
  
  - name: KafkaLagCritical
    condition: kafka.lag.total > 10000
    severity: critical
    actions:
      - auto_scale_workers: factor=2.0
      - apply_backpressure: factor=0.5
    message: "Critical lag {lag}, scaling + backpressure"
  
  - name: KafkaLagEmergency
    condition: kafka.lag.total > 100000
    severity: emergency
    actions:
      - scale_to_max_workers
      - apply_backpressure: factor=0.1
      - enable_load_shedding
      - page_oncall
    message: "EMERGENCY: Lag {lag}, all actions triggered"
  
  - name: LagCleared
    condition: kafka.lag.total < 500
    severity: info
    actions:
      - release_backpressure
      - scale_down_workers: factor=0.8
    message: "Lag cleared, releasing backpressure"
```

### 8. Worker Self-Monitoring

```python
class SelfMonitoringWorker:
    """Worker that monitors its own performance"""
    
    def __init__(self):
        self.consumer = KafkaConsumer('notifications')
        self.my_partition_lag = {}
        self.processing_rate = 0
        self.health_status = 'healthy'
    
    async def run(self):
        asyncio.create_task(self._health_check_loop())
        
        while True:
            # Measure processing rate
            start_time = time.time()
            processed_count = 0
            
            messages = self.consumer.poll(timeout_ms=1000, max_records=100)
            
            for message in messages:
                await self._process(message)
                processed_count += 1
            
            elapsed = time.time() - start_time
            self.processing_rate = processed_count / elapsed if elapsed > 0 else 0
            
            # Check my partition lag
            await self._check_my_lag()
    
    async def _check_my_lag(self):
        """Check lag for partitions assigned to this worker"""
        assigned_partitions = self.consumer.assignment()
        
        for partition in assigned_partitions:
            committed = self.consumer.committed(partition)
            high_water = self.consumer.highwater(partition)
            
            if committed and high_water:
                lag = high_water - committed
                self.my_partition_lag[partition.partition] = lag
                
                # Report to central monitoring
                metrics.gauge(
                    'worker_partition_lag',
                    lag,
                    tags={
                        'worker_id': self.worker_id,
                        'partition': partition.partition
                    }
                )
    
    async def _health_check_loop(self):
        """Periodic health check"""
        while True:
            await asyncio.sleep(30)
            
            # Check if I'm falling behind
            my_total_lag = sum(self.my_partition_lag.values())
            
            if my_total_lag > 5000:
                self.health_status = 'unhealthy'
                logger.error(f"Worker unhealthy: lag={my_total_lag}")
                
                # Signal need for more workers
                await self._signal_need_help()
            else:
                self.health_status = 'healthy'
            
            # Report health
            metrics.gauge('worker_health', 
                         1 if self.health_status == 'healthy' else 0,
                         tags={'worker_id': self.worker_id})
    
    async def _signal_need_help(self):
        """Signal that this worker needs help (more workers needed)"""
        await central_monitor.report_worker_overload(self.worker_id)
```

### 9. Proactive Scaling Based on Predictions

```python
class PredictiveScaler:
    """Scale based on predicted load, not just reactive"""
    
    def __init__(self):
        self.historical_data = []
        self.auto_scaler = WorkerAutoScaler()
    
    async def predict_and_scale(self):
        """Predict upcoming load and scale proactively"""
        
        # Analyze historical patterns
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        # Historical average for this time
        historical_load = self._get_historical_load(current_hour, current_day)
        current_load = self._get_current_load()
        
        # Predict next 5 minutes
        predicted_load = self._predict_load(historical_load, current_load)
        
        # Scale proactively
        if predicted_load > current_load * 1.5:
            logger.info(f"Predicted spike: {predicted_load}, scaling up proactively")
            await self.auto_scaler.scale_up(factor=1.3)
    
    def _predict_load(self, historical, current):
        """Simple prediction: weighted average"""
        return 0.7 * historical + 0.3 * current
```

## Summary (Updated)

**Backpressure with Lag Monitoring**:
- ✅ Workers monitor Kafka lag every 10s
- ✅ Auto-scale up when lag > 1K (20% increase)
- ✅ Aggressive scale when lag > 10K (2x workers)
- ✅ Signal API Gateway to slow down upstream
- ✅ Emergency mode at lag > 100K (max scale + drop low priority)

**Auto-scaling Triggers**:
| Lag | Workers | API Rate | Load Shedding |
|-----|---------|----------|---------------|
| < 1K | Normal (1000) | 100% | Off |
| 1K-10K | +20% (1200) | 100% | Off |
| 10K-100K | +100% (2000) | 50% | Medium |
| > 100K | Max (5000) | 10% | Aggressive |

**Cooldown**: 60s between scale operations (except emergency)

```python
class TokenBucket:
    """Rate limiting using token bucket algorithm"""
    
    def __init__(self, rate, capacity):
        self.rate = rate           # Tokens per second
        self.capacity = capacity   # Max tokens
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self, tokens=1):
        """Acquire tokens, wait if not available"""
        async with self.lock:
            # Refill tokens based on time passed
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            # Wait if not enough tokens
            if self.tokens < tokens:
                wait_time = (tokens - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= tokens
    
    def available(self):
        """Check available tokens without acquiring"""
        now = time.time()
        elapsed = now - self.last_update
        return min(self.capacity, self.tokens + elapsed * self.rate)
```

### 3. Worker Pool with Backpressure

```python
class BackpressureWorkerPool:
    """Worker pool that slows down when overloaded"""
    
    def __init__(self, max_workers=100):
        self.max_workers = max_workers
        self.active_workers = 0
        self.queue = asyncio.Queue(maxsize=1000)  # Bounded queue
        self.rate_limiter = TokenBucket(rate=10000, capacity=50000)  # 10K/sec
    
    async def submit(self, notification):
        """Submit notification with backpressure"""
        
        # Queue blocks when full (backpressure)
        await self.queue.put(notification)
        
        # Rate limiting
        await self.rate_limiter.acquire()
    
    async def worker(self):
        """Worker that processes from queue"""
        while True:
            notification = await self.queue.get()
            
            try:
                self.active_workers += 1
                await self._process(notification)
            finally:
                self.active_workers -= 1
                self.queue.task_done()
    
    def get_load(self):
        """Current system load"""
        return {
            'active_workers': self.active_workers,
            'queue_size': self.queue.qsize(),
            'queue_capacity': self.queue.maxsize,
            'utilization': self.active_workers / self.max_workers
        }
```

### 4. Adaptive Rate Limiting

```python
class AdaptiveRateLimiter:
    """Adjusts rate based on system health"""
    
    def __init__(self):
        self.current_rate = 10000  # Start at 10K/sec
        self.min_rate = 1000
        self.max_rate = 50000
    
    def adjust_rate(self, metrics):
        """Adjust rate based on metrics"""
        
        # Metrics: success_rate, latency_p99, kafka_lag
        
        if metrics['success_rate'] < 0.95:
            # Too many failures - slow down
            self.current_rate = max(self.min_rate, self.current_rate * 0.8)
            logger.warning(f"Rate reduced to {self.current_rate}/sec")
        
        elif metrics['latency_p99'] > 1000:
            # High latency - slow down
            self.current_rate = max(self.min_rate, self.current_rate * 0.9)
        
        elif metrics['kafka_lag'] > 10000:
            # Kafka lagging - we're too fast
            self.current_rate = max(self.min_rate, self.current_rate * 0.7)
        
        else:
            # All good - try to speed up
            self.current_rate = min(self.max_rate, self.current_rate * 1.1)
        
        return self.current_rate
```

## Bulkhead Pattern

**Isolate failures**: Separate resource pools per priority

```python
class Bulkhead:
    """Isolate resources for different priorities"""
    
    def __init__(self):
        self.pools = {
            'critical': WorkerPool(max_workers=100, max_queue=500),
            'high': WorkerPool(max_workers=400, max_queue=2000),
            'medium': WorkerPool(max_workers=300, max_queue=5000),
            'low': WorkerPool(max_workers=200, max_queue=10000)
        }
    
    async def process(self, notification):
        """Route to appropriate pool"""
        priority = notification['priority']
        pool = self.pools[priority]
        
        try:
            await pool.submit(notification)
        except QueueFullError:
            # Pool overloaded - reject or downgrade priority
            if priority == 'low':
                raise RejectedError("Low priority queue full")
            else:
                # Downgrade and retry
                notification['priority'] = self._downgrade(priority)
                await self.process(notification)
    
    def _downgrade(self, priority):
        """Downgrade priority level"""
        downgrades = {'critical': 'high', 'high': 'medium', 'medium': 'low'}
        return downgrades.get(priority, 'low')
```

## Monitoring Dashboard

**Key Metrics**:

```
Circuit Breakers Status:
├─ FCM: CLOSED ✓ (Failures: 0/5)
├─ APNs: HALF_OPEN ⚠ (Testing: 1/2)
├─ SendGrid: CLOSED ✓
└─ Twilio: OPEN ✗ (Retry in: 45s)

Kafka Lag:
├─ Total: 5,234 (Status: Warning)
├─ Avg per partition: 261
├─ Max partition: 892
└─ Time to clear: ~8.7 minutes

Worker Status:
├─ Current workers: 1,200 (Target: 1,200)
├─ Utilization: 78%
├─ Scaling state: Stable
└─ Last scaled: 2m ago

Backpressure:
├─ Status: Active (50% reduction)
├─ API rate limits: 50% of baseline
├─ Paused consumers: 0
└─ Load shedding: Off

Processing Rate:
├─ Successful: 9,823/sec
├─ Failed: 177/sec (1.8%)
├─ Success rate: 98.2%
└─ Avg latency: 234ms
```

## Emergency Procedures

**When Kafka lag > 100K**:
1. Auto-scale to max workers (5,000)
2. Drop all low priority notifications
3. Reduce medium priority by 90%
4. Page on-call engineer
5. Consider: Pause non-critical traffic at source

**When provider circuit opens**:
1. Automatic fallback to backup provider
2. Alert team
3. Monitor fallback provider health
4. If all providers down: Queue for retry

**When memory/CPU at 90%**:
1. Stop accepting new low priority
2. Scale horizontally
3. Enable aggressive GC
4. Shed load if necessaryue=10000)
        }
    
    async def submit(self, notification):
        pool = self.pools[notification.priority]
        
        if pool.is_full():
            # Pool full - reject or downgrade priority
            if notification.priority == 'critical':
                raise ResourceExhaustedError("Critical pool full")
            else:
                # Drop low priority when overloaded
                metrics.increment('dropped_notifications', 
                                  tags={'priority': notification.priority})
                return
        
        await pool.submit(notification)
```

## Load Shedding

**Drop work when overloaded**

```python
class LoadShedder:
    """Intelligent load shedding"""
    
    def __init__(self):
        self.load_threshold = 0.9  # 90% capacity
    
    def should_accept(self, notification, current_load):
        """Decide whether to accept notification"""
        
        if current_load < self.load_threshold:
            return True  # Accept all
        
        # Overloaded - prioritize
        if notification.priority == 'critical':
            return True  # Always accept critical
        
        if notification.priority == 'low':
            return False  # Drop all low priority
        
        # Accept high/medium probabilistically
        accept_probability = {
            'high': 0.8,
            'medium': 0.5
        }
        
        return random.random() < accept_probability.get(notification.priority, 0)
```

## Monitoring & Alerts

```python
class ResilienceMetrics:
    """Track resilience metrics"""
    
    def collect(self):
        return {
            'circuit_breakers': {
                'fcm': circuit_breakers.breakers['fcm'].get_stats(),
                'apns': circuit_breakers.breakers['apns'].get_stats(),
                'sendgrid': circuit_breakers.breakers['sendgrid'].get_stats()
            },
            'backpressure': {
                'kafka_paused': consumer.paused,
                'pending_messages': consumer.pending_count,
                'queue_utilization': worker_pool.queue.qsize() / worker_pool.queue.maxsize
            },
            'rate_limiting': {
                'current_rate': rate_limiter.current_rate,
                'available_tokens': rate_limiter.tokens
            },
            'load_shedding': {
                'dropped_count': metrics.get('dropped_notifications'),
                'accept_rate': metrics.get('accepted') / metrics.get('total')
            }
        }
```

**Alerts**:
```yaml
alerts:
  - name: CircuitBreakerOpen
    condition: circuit_breaker.state == 'open'
    severity: warning
    message: "Circuit breaker open for {provider}"
  
  - name: HighBackpressure
    condition: queue_utilization > 0.9
    severity: warning
    message: "Queue utilization {utilization}%"
  
  - name: RateLimitHit
    condition: available_tokens < 100
    severity: info
    message: "Rate limit approaching"
  
  - name: LoadSheddingActive
    condition: dropped_count > 1000
    severity: critical
    message: "Dropping {count} notifications/sec"
```

## Combined Strategy

```python
class ResilientNotificationService:
    """Combines all resilience patterns"""
    
    def __init__(self):
        self.circuit_breakers = ProviderCircuitBreakers()
        self.backpressure_consumer = BackpressureAwareConsumer()
        self.rate_limiter = AdaptiveRateLimiter()
        self.bulkhead = Bulkhead()
        self.load_shedder = LoadShedder()
    
    async def send_notification(self, notification):
        # 1. Check load shedding
        current_load = self._get_current_load()
        if not self.load_shedder.should_accept(notification, current_load):
            metrics.increment('load_shed')
            return {'status': 'dropped', 'reason': 'load_shedding'}
        
        # 2. Apply backpressure
        await self.rate_limiter.acquire()
        
        # 3. Use bulkhead (isolated pools)
        pool = self.bulkhead.pools[notification.priority]
        
        # 4. Send with circuit breaker
        try:
            result = await self.circuit_breakers.send_with_breaker(
                notification.provider,
                notification
            )
            return result
        except Exception as e:
            logger.error(f"Send failed: {e}")
            return {'status': 'failed', 'error': str(e)}
```

## Summary

**Circuit Breaker**:
- ✅ Fail fast when provider is down
- ✅ Automatic recovery after timeout
- ✅ Fallback to secondary provider

**Backpressure**:
- ✅ Pause Kafka consumer when overloaded
- ✅ Bounded queues (block when full)
- ✅ Adaptive rate limiting

**Load Shedding**:
- ✅ Drop low priority when overloaded
- ✅ Protect critical notifications
- ✅ Graceful degradation

**Bulkhead**:
- ✅ Isolated resource pools per priority
- ✅ Failures don't cascade

**Result**: System stays stable even when:
- Providers go down (circuit breaker)
- Traffic spikes 10× (backpressure + load shedding)
- Individual components fail (bulkhead)
