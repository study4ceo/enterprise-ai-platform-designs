# Implementation Guide - Which One to Use?

## Quick Comparison

| Feature | Payment Service | API Service | Message Queue |
|---------|----------------|-------------|---------------|
| **Best For** | Critical operations | General REST APIs | Async processing |
| **Complexity** | High | Medium | Medium |
| **Storage** | Redis + PostgreSQL | Redis only | Redis only |
| **Durability** | High (DB backed) | Medium (cache) | Medium (cache) |
| **Locking** | Explicit distributed locks | Implicit state tracking | Atomic processing marks |
| **Setup Time** | 15 minutes | 5 minutes | 5 minutes |
| **Dependencies** | PostgreSQL + Redis | Redis | Redis |
| **Use Cases** | Payments, transfers | CRUD APIs | Event processing |

## Decision Tree

```
Do you need database durability and audit trails?
├─ YES → Payment Service
└─ NO → Is it synchronous or asynchronous?
    ├─ Synchronous (REST API) → API Service
    └─ Asynchronous (queue) → Message Queue
```

## Detailed Comparison

### Payment Service (`implementations/payment_service/`)

**When to use**:
- ✅ Financial transactions (payments, transfers)
- ✅ Critical operations requiring audit trail
- ✅ Need strong consistency guarantees
- ✅ Compliance requirements (SOC2, PCI-DSS)
- ✅ Operations that absolutely cannot duplicate

**Features**:
- Hybrid Redis + PostgreSQL storage
- Explicit distributed locking
- Request hash validation
- Comprehensive state tracking
- Database as source of truth

**Code snippet**:
```python
with DistributedLock(idempotency_key):
    # Check cache
    if redis.exists(key):
        return redis.get(key)
    
    # Check database
    if db.exists(key):
        return db.get(key)
    
    # Process and store
    result = process_payment()
    db.insert(key, result)
    redis.cache(key, result)
    return result
```

**Pros**:
- Strongest guarantees
- Durable storage
- Full audit trail
- Production-proven patterns

**Cons**:
- More setup (PostgreSQL required)
- Slightly slower (database writes)
- More complex code

**Example use cases**:
- Payment processing
- Bank transfers
- Order creation (e-commerce)
- Account creation
- Subscription management

---

### API Service (`implementations/api_service/`)

**When to use**:
- ✅ General REST APIs
- ✅ CRUD operations
- ✅ Want automatic idempotency
- ✅ Multiple similar endpoints
- ✅ Rapid development
- ✅ Non-critical operations

**Features**:
- Automatic middleware (zero code changes)
- Redis-only storage
- Handles all HTTP methods correctly
- Built-in statistics endpoint
- Lightweight and fast

**Code snippet**:
```python
# Middleware handles everything automatically!
@app.post("/api/orders")
def create_order(order: OrderRequest):
    # Just write normal endpoint code
    # Idempotency handled by middleware
    return process_order(order)
```

**Pros**:
- Automatic (no manual idempotency code)
- Fast setup (5 minutes)
- Easy to understand
- Minimal dependencies

**Cons**:
- Redis only (no durability beyond TTL)
- No explicit locks (relies on state tracking)
- Not suitable for critical financial operations

**Example use cases**:
- User management APIs
- Product catalog APIs
- Blog post creation
- Comment systems
- Any CRUD API

---

### Message Queue (`implementations/message_queue/`)

**When to use**:
- ✅ Processing messages from queues (SQS, RabbitMQ)
- ✅ Event-driven architecture
- ✅ At-least-once delivery semantics
- ✅ Async background jobs
- ✅ Need retry logic and DLQ

**Features**:
- Automatic deduplication by message ID
- Built-in retry logic
- Dead letter queue support
- Batch processing
- Multiple handler examples

**Code snippet**:
```python
class MyHandler(IdempotentMessageHandler):
    def process_message(self, message: Message):
        # Your business logic
        # Deduplication handled automatically
        process_order(message.body)

# Usage
handler = MyHandler()
consumer = SQSConsumer("queue", handler)
consumer.consume()  # Handles duplicates automatically
```

**Pros**:
- Built for queue semantics
- Automatic retry with backoff
- DLQ handling
- Batch processing support

**Cons**:
- Queue-specific (not for REST APIs)
- Redis dependency
- Requires understanding of message queues

**Example use cases**:
- Order processing pipeline
- Email notifications
- Webhook processing
- Event sourcing
- Data synchronization
- ETL jobs

---

## Real-World Scenarios

### Scenario 1: E-commerce Platform

**Order Creation API** → Use **Payment Service**
- Critical operation
- Money involved
- Need audit trail
- Must prevent duplicates

**Product Catalog API** → Use **API Service**
- CRUD operations
- Not critical if cached
- Many similar endpoints
- Speed matters

**Order Status Updates** → Use **Message Queue**
- Event-driven
- Async processing
- Multiple systems consuming
- Retry important

### Scenario 2: Banking Application

**Money Transfer** → Use **Payment Service**
- Absolutely critical
- Regulatory compliance
- Audit trail required
- Cannot duplicate

**Account Info API** → Use **API Service**
- Read operations mostly
- Some updates (profile)
- Standard REST patterns

**Transaction Notifications** → Use **Message Queue**
- Async email/SMS
- Event-driven
- Retry on failure

### Scenario 3: SaaS Application

**Subscription Payment** → Use **Payment Service**
- Recurring charges
- Cannot double-charge
- Need payment history

**User Management API** → Use **API Service**
- CRUD for users
- Fast development
- Many endpoints

**Usage Analytics** → Use **Message Queue**
- Async event processing
- High volume
- Can tolerate delays

---

## Migration Path

### Start Simple → Scale Up

**Phase 1**: API Service
- Quick to implement
- Covers 80% of endpoints
- Learn idempotency patterns

**Phase 2**: Add Payment Service
- For critical operations
- When audit trail needed
- As compliance requires

**Phase 3**: Add Message Queue
- When going event-driven
- For async processing
- As scale increases

### Or Start Critical

**Phase 1**: Payment Service
- For critical-first approach
- When starting with payments
- Compliance from day 1

**Phase 2**: Add API Service
- For non-critical endpoints
- Faster development
- Better DX for most APIs

**Phase 3**: Add Message Queue
- When adding async features
- Event-driven architecture
- Background jobs

---

## Mixing Approaches

You can (and should) use multiple implementations:

```python
# Critical payment endpoint - Payment Service pattern
@app.post("/api/payments")
def create_payment(...):
    with DistributedLock(key):
        return payment_service.process(key, data)

# Regular CRUD - API Service middleware
@app.post("/api/users")
def create_user(...):
    # Middleware handles it
    return user_service.create(data)

# Async processing - Message Queue
def process_order_events():
    handler = OrderHandler()
    consumer = SQSConsumer("orders", handler)
    consumer.consume()
```

---

## Quick Start Guide

### 1. Install Dependencies

All implementations:
```bash
pip install fastapi uvicorn redis
```

Payment Service only:
```bash
pip install psycopg2-binary
```

### 2. Start Redis

```bash
redis-server
```

### 3. Choose and Run

**Payment Service**:
```bash
cd implementations/payment_service
psql -U postgres -f schema.sql
python payment_service.py
# → http://localhost:8000
```

**API Service**:
```bash
cd implementations/api_service
python api_service.py
# → http://localhost:8001
```

**Message Queue**:
```bash
cd implementations/message_queue
python message_handler.py
```

---

## Summary

| If you need... | Use this |
|----------------|----------|
| Payment processing | Payment Service |
| Bank transfers | Payment Service |
| Critical operations | Payment Service |
| Audit trail / compliance | Payment Service |
| REST APIs (general) | API Service |
| CRUD operations | API Service |
| Fast development | API Service |
| Many similar endpoints | API Service |
| Queue message processing | Message Queue |
| Event-driven architecture | Message Queue |
| Async background jobs | Message Queue |
| Webhook handling | Message Queue |

**Default recommendation**: Start with **API Service** for most endpoints, use **Payment Service** for critical operations, add **Message Queue** when going async.

---

For more details, see each implementation's README:
- `implementations/payment_service/README.md`
- `implementations/api_service/README.md`
- `implementations/message_queue/README.md`
