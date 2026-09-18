# Retries and Backoff Strategies
## Comprehensive Guide to Resilient Data Pipelines

---

## Table of Contents
1. [Introduction](#introduction)
2. [Why Retries Matter](#why-retries)
3. [Retry Strategies](#retry-strategies)
4. [Backoff Algorithms](#backoff-algorithms)
5. [Implementation Patterns](#implementation)
6. [Circuit Breakers](#circuit-breakers)
7. [Dead Letter Queues](#dlq)
8. [Best Practices](#best-practices)
9. [Anti-Patterns](#anti-patterns)
10. [Real-World Examples](#examples)

---

## 1. Introduction {#introduction}

**Retries** and **backoff strategies** are essential for building resilient data pipelines that can handle transient failures gracefully.

### Key Concepts

```
Failure Occurs
    ↓
Wait (Backoff)
    ↓
Retry Operation
    ↓
Success? → Continue
    ↓
No? → Repeat (with increasing backoff)
    ↓
Max Retries Reached? → Send to DLQ / Alert
```

---

## 2. Why Retries Matter {#why-retries}

### Common Transient Failures

**Network Issues:**
```
- Connection timeouts
- DNS resolution failures
- Temporary network partitions
- Load balancer issues
```

**Service Unavailability:**
```
- Database connection pool exhausted
- API rate limiting (429 errors)
- Service restarts/deployments
- Cloud service throttling
```

**Resource Constraints:**
```
- Memory pressure causing GC pauses
- CPU saturation
- Disk I/O bottlenecks
- Thread pool exhaustion
```

### Without Retries (❌ Brittle)

```python
def process_data():
    try:
        result = api.call()  # Fails once
        save_to_db(result)
    except Exception as e:
        # Pipeline fails completely!
        raise

# Single network blip = complete failure
```

### With Retries (✅ Resilient)

```python
@retry(max_attempts=3, backoff=exponential_backoff)
def process_data():
    result = api.call()
    save_to_db(result)
    return result

# Handles transient failures automatically
```

---

## 3. Retry Strategies {#retry-strategies}

### Strategy 1: Fixed Retry Count

**Simple, predictable retry behavior**

```python
def fixed_retry(func, max_attempts=3):
    """
    Retry function with fixed number of attempts
    """
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            print(f"Attempt {attempt + 1} failed: {e}")
    
# Usage
result = fixed_retry(lambda: api.call(), max_attempts=5)
```

**When to use:**
- Simple operations
- Fast-failing operations
- Development/testing

---

### Strategy 2: Retry with Timeout

**Prevent infinite waiting**

```python
import time
from datetime import datetime, timedelta

def retry_with_timeout(func, max_duration_seconds=60, retry_interval=1):
    """
    Retry until timeout or success
    """
    end_time = datetime.now() + timedelta(seconds=max_duration_seconds)
    
    while datetime.now() < end_time:
        try:
            return func()
        except Exception as e:
            if datetime.now() >= end_time:
                raise TimeoutError(f"Retry timeout after {max_duration_seconds}s")
            time.sleep(retry_interval)
    
    raise TimeoutError("Retry timeout exceeded")

# Usage
result = retry_with_timeout(
    lambda: connect_to_database(),
    max_duration_seconds=30
)
```

---

### Strategy 3: Retry Specific Exceptions

**Only retry transient errors**

```python
from requests.exceptions import ConnectionError, Timeout

def retry_transient_errors(func, max_attempts=3, retryable_exceptions=None):
    """
    Retry only specific exception types
    """
    if retryable_exceptions is None:
        retryable_exceptions = (ConnectionError, Timeout)
    
    for attempt in range(max_attempts):
        try:
            return func()
        except retryable_exceptions as e:
            if attempt == max_attempts - 1:
                raise
            print(f"Transient error on attempt {attempt + 1}: {e}")
        except Exception as e:
            # Non-retryable error - fail immediately
            print(f"Non-retryable error: {e}")
            raise

# Usage
result = retry_transient_errors(
    lambda: requests.get('https://api.example.com'),
    retryable_exceptions=(ConnectionError, Timeout, requests.HTTPError)
)
```

---

### Strategy 4: Conditional Retry

**Retry based on response/error details**

```python
def should_retry(exception):
    """
    Determine if exception is retryable
    """
    # Retry on specific HTTP status codes
    if hasattr(exception, 'response'):
        status = exception.response.status_code
        return status in [408, 429, 500, 502, 503, 504]
    
    # Retry on specific error messages
    error_msg = str(exception).lower()
    retryable_keywords = ['timeout', 'connection', 'temporary', 'unavailable']
    return any(keyword in error_msg for keyword in retryable_keywords)

def conditional_retry(func, max_attempts=3):
    """
    Retry based on condition
    """
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if not should_retry(e) or attempt == max_attempts - 1:
                raise
            print(f"Retryable error on attempt {attempt + 1}: {e}")

# Usage
result = conditional_retry(lambda: api_call())
```

---

## 4. Backoff Algorithms {#backoff-algorithms}

### Algorithm 1: Fixed Backoff

**Constant wait time between retries**

```python
import time

def fixed_backoff(func, max_attempts=3, delay=1.0):
    """
    Retry with fixed delay between attempts
    
    Retry pattern:
    - Attempt 1: immediate
    - Wait 1 second
    - Attempt 2
    - Wait 1 second
    - Attempt 3
    """
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            print(f"Attempt {attempt + 1} failed. Waiting {delay}s...")
            time.sleep(delay)

# Usage
result = fixed_backoff(api_call, max_attempts=5, delay=2.0)
```

**Pros:**
- Simple to understand
- Predictable timing
- Easy to calculate total time

**Cons:**
- Can overwhelm recovering services
- No adaptation to load
- Inefficient for rate-limited APIs

---

### Algorithm 2: Linear Backoff

**Linearly increasing wait time**

```python
def linear_backoff(func, max_attempts=5, base_delay=1.0):
    """
    Retry with linearly increasing delay
    
    Retry pattern:
    - Attempt 1: immediate
    - Wait 1 second
    - Attempt 2
    - Wait 2 seconds
    - Attempt 3
    - Wait 3 seconds
    - Attempt 4
    """
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            
            delay = base_delay * (attempt + 1)
            print(f"Attempt {attempt + 1} failed. Waiting {delay}s...")
            time.sleep(delay)

# Usage
result = linear_backoff(api_call, max_attempts=5, base_delay=1.0)
# Total wait time: 1 + 2 + 3 + 4 = 10 seconds
```

---

### Algorithm 3: Exponential Backoff

**Exponentially increasing wait time (Most common)**

```python
def exponential_backoff(func, max_attempts=5, base_delay=1.0, max_delay=60.0):
    """
    Retry with exponential backoff
    
    Retry pattern:
    - Attempt 1: immediate
    - Wait 1 second (2^0 * base)
    - Attempt 2
    - Wait 2 seconds (2^1 * base)
    - Attempt 3
    - Wait 4 seconds (2^2 * base)
    - Attempt 4
    - Wait 8 seconds (2^3 * base)
    - Attempt 5
    """
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            
            # Calculate exponential delay: base * 2^attempt
            delay = min(base_delay * (2 ** attempt), max_delay)
            print(f"Attempt {attempt + 1} failed. Waiting {delay}s...")
            time.sleep(delay)

# Usage
result = exponential_backoff(api_call, max_attempts=6, base_delay=1.0)
# Wait times: 1, 2, 4, 8, 16, 32 seconds
```

**Pros:**
- Adapts to service recovery time
- Reduces load on failing services
- Industry standard (AWS, Google, etc.)

**Cons:**
- Can lead to very long waits
- Need max_delay cap

---

### Algorithm 4: Exponential Backoff with Jitter

**Randomized wait time to prevent thundering herd**

```python
import random

def exponential_backoff_with_jitter(
    func, 
    max_attempts=5, 
    base_delay=1.0, 
    max_delay=60.0
):
    """
    Retry with exponential backoff and jitter
    
    Jitter prevents multiple clients from retrying simultaneously
    (thundering herd problem)
    """
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            
            # Calculate exponential delay
            exponential_delay = base_delay * (2 ** attempt)
            
            # Add jitter (random variation)
            # Full jitter: random between 0 and exponential_delay
            jittered_delay = random.uniform(0, exponential_delay)
            
            # Cap at max_delay
            delay = min(jittered_delay, max_delay)
            
            print(f"Attempt {attempt + 1} failed. Waiting {delay:.2f}s...")
            time.sleep(delay)

# Usage
result = exponential_backoff_with_jitter(api_call)
```

**Jitter Strategies:**

```python
# 1. Full Jitter (Recommended by AWS)
delay = random.uniform(0, min(max_delay, base * 2^attempt))

# 2. Equal Jitter
temp = min(max_delay, base * 2^attempt)
delay = temp / 2 + random.uniform(0, temp / 2)

# 3. Decorrelated Jitter
delay = random.uniform(base, previous_delay * 3)
```

---

### Algorithm 5: Fibonacci Backoff

**Fibonacci sequence for delays**

```python
def fibonacci_backoff(func, max_attempts=7, base_delay=1.0):
    """
    Retry with Fibonacci sequence delays
    
    Delays: 1, 1, 2, 3, 5, 8, 13 seconds
    """
    fib = [1, 1]
    for i in range(2, max_attempts):
        fib.append(fib[i-1] + fib[i-2])
    
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            
            delay = fib[attempt] * base_delay
            print(f"Attempt {attempt + 1} failed. Waiting {delay}s...")
            time.sleep(delay)

# Usage
result = fibonacci_backoff(api_call, max_attempts=7)
```

---

## 5. Implementation Patterns {#implementation}

### Pattern 1: Decorator-Based Retry

```python
import functools
import time
import logging

logger = logging.getLogger(__name__)

def retry(
    max_attempts=3,
    delay=1.0,
    backoff=2.0,
    exceptions=(Exception,),
    on_retry=None
):
    """
    Decorator for retry logic with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay (exponential backoff)
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Callback function called on each retry
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts"
                        )
                        raise
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(attempt, e)
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception
        
        return wrapper
    return decorator

# Usage
@retry(max_attempts=5, delay=1.0, backoff=2.0)
def fetch_data_from_api():
    response = requests.get('https://api.example.com/data')
    response.raise_for_status()
    return response.json()

@retry(
    max_attempts=3,
    delay=2.0,
    exceptions=(ConnectionError, TimeoutError),
    on_retry=lambda attempt, error: send_alert(f"Retry {attempt}: {error}")
)
def connect_to_database():
    return psycopg2.connect(DATABASE_URL)
```

---

### Pattern 2: Class-Based Retry Handler

```python
from dataclasses import dataclass
from typing import Callable, Tuple, Optional
import time

@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    jitter: bool = True
    retryable_exceptions: Tuple = (Exception,)

class RetryHandler:
    """
    Flexible retry handler with multiple strategies
    """
    
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
    
    def execute(self, func: Callable, *args, **kwargs):
        """
        Execute function with retry logic
        """
        for attempt in range(self.config.max_attempts):
            try:
                return func(*args, **kwargs)
                
            except self.config.retryable_exceptions as e:
                if attempt == self.config.max_attempts - 1:
                    raise
                
                delay = self._calculate_delay(attempt)
                self._log_retry(func.__name__, attempt, e, delay)
                time.sleep(delay)
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter"""
        # Exponential backoff
        delay = self.config.base_delay * (self.config.backoff_multiplier ** attempt)
        
        # Cap at max delay
        delay = min(delay, self.config.max_delay)
        
        # Add jitter if enabled
        if self.config.jitter:
            import random
            delay = random.uniform(0, delay)
        
        return delay
    
    def _log_retry(self, func_name: str, attempt: int, error: Exception, delay: float):
        """Log retry attempt"""
        logger.warning(
            f"Function '{func_name}' failed on attempt {attempt + 1}: {error}. "
            f"Retrying in {delay:.2f}s..."
        )

# Usage
config = RetryConfig(
    max_attempts=5,
    base_delay=1.0,
    max_delay=30.0,
    backoff_multiplier=2.0,
    jitter=True,
    retryable_exceptions=(ConnectionError, TimeoutError)
)

retry_handler = RetryHandler(config)

# Execute with retries
result = retry_handler.execute(fetch_data_from_api)
```

---

### Pattern 3: Async/Await Retry (Python asyncio)

```python
import asyncio
import aiohttp
from typing import Callable, TypeVar, Any

T = TypeVar('T')

async def async_retry(
    func: Callable[..., T],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> T:
    """
    Async retry with exponential backoff
    """
    current_delay = base_delay
    
    for attempt in range(max_attempts):
        try:
            return await func()
            
        except exceptions as e:
            if attempt == max_attempts - 1:
                raise
            
            logger.warning(
                f"Async attempt {attempt + 1} failed: {e}. "
                f"Retrying in {current_delay}s..."
            )
            
            await asyncio.sleep(current_delay)
            current_delay *= backoff

# Usage
async def fetch_async():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.example.com') as response:
            return await response.json()

# Execute with retries
result = await async_retry(fetch_async, max_attempts=5)
```

---

### Pattern 4: Library Integration (tenacity)

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=60),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def robust_api_call():
    """API call with intelligent retry using tenacity"""
    response = requests.get('https://api.example.com/data')
    response.raise_for_status()
    return response.json()

# Advanced: Custom retry conditions
from tenacity import retry_if_result

@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_result(lambda x: x is None),  # Retry if result is None
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_until_not_none():
    result = get_data()
    return result
```

---

## 6. Circuit Breakers {#circuit-breakers}

### What is a Circuit Breaker?

**Prevent cascading failures by "opening" circuit after repeated failures**

```
States:
┌─────────┐  Failures    ┌──────┐
│ CLOSED  │──────────────>│ OPEN │
│(Normal) │              │(Skip)│
└─────────┘              └──────┘
     ^                        │
     │                        │ Timeout
     │  Success               │
     │                        v
     │                   ┌──────────┐
     └───────────────────│HALF-OPEN │
                        │  (Test)  │
                        └──────────┘
```

### Implementation

```python
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject immediately
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    """
    
    def __init__(
        self,
        failure_threshold=5,
        timeout_seconds=60,
        expected_exception=Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.expected_exception = expected_exception
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
    
    def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection
        """
        # Check if circuit should transition from OPEN to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if datetime.now() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            # After 3 successes, close circuit
            if self.success_count >= 3:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        else:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN

# Usage
breaker = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

def api_call_with_breaker():
    return breaker.call(requests.get, 'https://api.example.com')

# Automatic protection against cascading failures
for i in range(100):
    try:
        result = api_call_with_breaker()
    except Exception as e:
        print(f"Call {i} failed: {e}")
```

---

## 7. Dead Letter Queues {#dlq}

### What is a DLQ?

**Storage for messages that fail after all retry attempts**

```
Message → Process → Success ✅
             ↓
          Failure
             ↓
          Retry 1 → Failure
             ↓
          Retry 2 → Failure
             ↓
          Retry 3 → Failure
             ↓
       Send to DLQ ❌
```

### Implementation

```python
from confluent_kafka import Producer
import json
import logging

logger = logging.getLogger(__name__)

class DeadLetterQueue:
    """
    Handle failed messages after max retries
    """
    
    def __init__(self, kafka_bootstrap_servers, dlq_topic='dead-letter-queue'):
        self.producer = Producer({
            'bootstrap.servers': kafka_bootstrap_servers
        })
        self.dlq_topic = dlq_topic
    
    def send_to_dlq(self, original_message, error, metadata=None):
        """
        Send failed message to Dead Letter Queue
        """
        dlq_message = {
            'original_message': original_message,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.producer.produce(
            self.dlq_topic,
            value=json.dumps(dlq_message).encode('utf-8')
        )
        
        self.producer.flush()
        
        logger.error(
            f"Message sent to DLQ: {dlq_message['error_message']}"
        )

# Usage with retries
dlq = DeadLetterQueue('localhost:9092')

@retry(max_attempts=3)
def process_message(message):
    try:
        # Process message
        result = transform(message)
        save_to_database(result)
        
    except Exception as e:
        # If all retries fail, send to DLQ
        if current_attempt == max_attempts:
            dlq.send_to_dlq(
                original_message=message,
                error=e,
                metadata={'attempts': max_attempts}
            )
        raise
```

---

## 8. Best Practices {#best-practices}

### ✅ DO

1. **Use exponential backoff with jitter**
```python
@retry(backoff=exponential_with_jitter)
def api_call():
    pass
```

2. **Retry only transient errors**
```python
@retry(exceptions=(ConnectionError, Timeout))
def db_query():
    pass
```

3. **Set maximum retry limits**
```python
@retry(max_attempts=5, max_delay=60)
def operation():
    pass
```

4. **Log retry attempts**
```python
@retry(on_retry=lambda attempt, error: logger.warning(f"Retry {attempt}: {error}"))
def operation():
    pass
```

5. **Use circuit breakers for external services**
```python
breaker = CircuitBreaker()
result = breaker.call(external_api)
```

6. **Implement Dead Letter Queues**
```python
try:
    process(message)
except MaxRetriesExceeded:
    dlq.send(message)
```

7. **Make operations idempotent**
```python
@retry
@idempotent  # Safe to retry
def upsert_record(id, data):
    pass
```

### ❌ DON'T

1. **Don't retry non-transient errors**
```python
# ❌ Bad: Retry validation errors
@retry
def validate_input(data):
    if not data:
        raise ValueError("Data is empty")  # Not retryable!
```

2. **Don't use infinite retries**
```python
# ❌ Bad: Could retry forever
while True:
    try:
        operation()
        break
    except:
        pass
```

3. **Don't ignore retry failures**
```python
# ❌ Bad: Silent failures
try:
    retry_operation()
except:
    pass  # Lost data!
```

4. **Don't retry without backoff**
```python
# ❌ Bad: Hammers failing service
for i in range(100):
    try:
        api_call()
    except:
        pass  # Immediate retry!
```

---

## 9. Anti-Patterns {#anti-patterns}

### Anti-Pattern 1: Retry Storm (Thundering Herd)

```python
# ❌ Problem: All clients retry simultaneously
@retry(delay=1.0)  # Fixed delay, no jitter
def api_call():
    pass

# 1000 clients all retry at same time
# → Service gets 1000 requests every second
# → Overwhelms recovering service

# ✅ Solution: Add jitter
@retry(delay=random.uniform(0.5, 1.5))
def api_call():
    pass
```

### Anti-Pattern 2: Cascading Failures

```python
# ❌ Problem: Long retry chains
@retry(max_attempts=10)
def service_a():
    return service_b()

@retry(max_attempts=10)
def service_b():
    return service_c()

@retry(max_attempts=10)
def service_c():
    return database_query()

# Total retries: 10 * 10 * 10 = 1000!

# ✅ Solution: Use circuit breakers
breaker = CircuitBreaker()

def service_a():
    return breaker.call(service_b)
```

### Anti-Pattern 3: Retry Without Idempotency

```python
# ❌ Problem: Non-idempotent operation
@retry(max_attempts=3)
def transfer_money(amount):
    balance -= amount  # Not idempotent!
    # If retry happens, money deducted multiple times

# ✅ Solution: Make idempotent
@retry(max_attempts=3)
def transfer_money(transaction_id, amount):
    if transaction_id not in processed_transactions:
        balance -= amount
        processed_transactions.add(transaction_id)
```

---

## 10. Real-World Examples {#examples}

### Example 1: Kafka Consumer with Retries

```python
from confluent_kafka import Consumer, KafkaError
import time

class ResilientKafkaConsumer:
    """
    Kafka consumer with retry and DLQ
    """
    
    def __init__(self, config, dlq_handler):
        self.consumer = Consumer(config)
        self.dlq = dlq_handler
        self.max_retries = 3
    
    @retry(
        max_attempts=3,
        delay=1.0,
        backoff=2.0,
        exceptions=(ConnectionError, TimeoutError)
    )
    def connect(self):
        """Connect to Kafka with retries"""
        self.consumer.subscribe(['my-topic'])
    
    def consume(self):
        """Consume messages with retry logic"""
        while True:
            msg = self.consumer.poll(1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(f"Kafka error: {msg.error()}")
                    continue
            
            # Process message with retries
            self.process_with_retry(msg)
    
    def process_with_retry(self, msg):
        """Process message with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                # Process message
                self.process_message(msg.value())
                
                # Commit offset on success
                self.consumer.commit(msg)
                return
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    # Max retries exceeded, send to DLQ
                    self.dlq.send(msg, error=e)
                    self.consumer.commit(msg)  # Commit to move forward
                else:
                    delay = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Retry {attempt + 1} in {delay}s: {e}")
                    time.sleep(delay)
    
    def process_message(self, value):
        """Actual message processing logic"""
        # Your processing code here
        pass
```

### Example 2: HTTP API with Circuit Breaker

```python
import requests
from circuitbreaker import circuit

class ResilientAPIClient:
    """
    HTTP client with retries and circuit breaker
    """
    
    @circuit(failure_threshold=5, recovery_timeout=60)
    @retry(
        max_attempts=3,
        delay=1.0,
        backoff=2.0,
        exceptions=(requests.exceptions.RequestException,)
    )
    def get(self, url, **kwargs):
        """GET request with retries and circuit breaker"""
        response = requests.get(url, timeout=10, **kwargs)
        response.raise_for_status()
        return response.json()
    
    @circuit(failure_threshold=5, recovery_timeout=60)
    @retry(max_attempts=3)
    def post(self, url, data=None, **kwargs):
        """POST request with retries and circuit breaker"""
        response = requests.post(url, json=data, timeout=10, **kwargs)
        response.raise_for_status()
        return response.json()

# Usage
client = ResilientAPIClient()

try:
    data = client.get('https://api.example.com/data')
except CircuitBreakerError:
    logger.error("Circuit breaker is open, service is down")
except MaxRetriesExceeded:
    logger.error("All retries failed")
```

---

## Summary

**Key Takeaways:**

1. **Always use retries** for transient failures
2. **Exponential backoff with jitter** is the industry standard
3. **Set reasonable limits** (max attempts, max delay)
4. **Only retry transient errors** (network, timeouts, 5xx)
5. **Use circuit breakers** to prevent cascading failures
6. **Implement DLQs** for failed messages
7. **Make operations idempotent** before adding retries
8. **Monitor and alert** on retry rates

**Retry Decision Tree:**

```
Error occurred
    ↓
Is it transient? (network, timeout, 5xx)
    ↓ Yes                      ↓ No
Use retry            Don't retry (fail fast)
    ↓
Is operation idempotent?
    ↓ Yes                      ↓ No
Safe to retry        Make idempotent first
    ↓
Add exponential backoff + jitter
    ↓
Set max attempts (3-5)
    ↓
Implement DLQ for final failures
    ↓
Add circuit breaker for external services
```

---

**Document Complete** ✅
