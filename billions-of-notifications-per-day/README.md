# Billions of Notifications Per Day - System Design

## Problem Statement
Design a system that sends **billions of notifications per day** across multiple channels (push, email, SMS) with high reliability and low latency.

## Scale Requirements
- **Volume**: 1-10 billion notifications/day
- **Throughput**: 11,500 - 115,000 req/sec (peak 10x)
- **Latency**: < 500ms p99
- **Channels**: Push, Email, SMS, In-app
- **Availability**: 99.95%

## High-Level Architecture

```
┌─────────────┐
│   Clients   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  API Gateway    │ ← Load Balancer
│  (Rate Limit)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Kafka Cluster  │ ← Partitioned by user_id
│  (Message Queue)│
└──────┬──────────┘
       │
       ▼
┌─────────────────────────────┐
│  Worker Pool (1000+ nodes)  │ ← Auto-scaling
│  - Fetch from Kafka         │
│  - Check preferences        │
│  - Send to channel          │
└──────┬──────────────────────┘
       │
       ├─────────────┬──────────────┬───────────┐
       ▼             ▼              ▼           ▼
   ┌──────┐    ┌────────┐    ┌──────┐   ┌─────────┐
   │ APNs │    │ FCM    │    │ SMTP │   │ Twilio  │
   │(iOS) │    │(Android)│   │(Email)│   │  (SMS)  │
   └──────┘    └────────┘    └──────┘   └─────────┘

   ┌──────────────────────────────────┐
   │  Supporting Services             │
   │  - Redis (Cache)                 │
   │  - Cassandra (User preferences)  │
   │  - Analytics DB                  │
   └──────────────────────────────────┘
```

## Core Components

### 1. API Gateway
- Receives notification requests
- Rate limiting (per user/tenant)
- Authentication
- Request validation

### 2. Message Queue (Kafka)
- Partitioned by `user_id`
- Retention: 7 days
- Replication factor: 3
- Handles 100K+ msg/sec

### 3. Worker Service
- Consumes from Kafka
- Fetches user preferences from cache
- Routes to appropriate channel
- Retries with exponential backoff
- Dead letter queue for failures

### 4. User Preference Store (Cassandra)
- Stores: channels, timezone, quiet hours, opt-outs
- Write-heavy, needs horizontal scaling
- Cache in Redis for reads

### 5. Delivery Services
- **Push**: APNs (iOS), FCM (Android)
- **Email**: SendGrid, AWS SES
- **SMS**: Twilio, AWS SNS

## Tech Stack

| Component | Technology | Why |
|-----------|------------|-----|
| Queue | Kafka | High throughput, partitioning |
| Database | Cassandra | Write-heavy, horizontal scaling |
| Cache | Redis | Low latency reads |
| Workers | Go/Java | High concurrency |
| Monitoring | Prometheus + Grafana | Metrics |
| Logging | ELK Stack | Debugging |

## Key Design Decisions

### Why Kafka over SQS/RabbitMQ?
- **Partitioning**: Ordered delivery per user
- **Throughput**: 100K+ msg/sec per broker
- **Replay**: Can reprocess messages
- **Retention**: Keep messages for debugging

### Why Cassandra over PostgreSQL?
- **Write throughput**: 10K+ writes/sec/node
- **Horizontal scaling**: Add nodes linearly
- **No single point of failure**: Distributed
- **Tunable consistency**: AP from CAP

### Why Redis Cache?
- **Speed**: < 1ms latency
- **Reduce DB load**: 90% cache hit rate
- **User preferences**: Hot data

## Scaling Strategy

### Horizontal Scaling
- **Workers**: Auto-scale based on Kafka lag
- **Kafka**: Add brokers/partitions
- **Cassandra**: Add nodes to ring
- **Redis**: Cluster mode

### Partitioning
- Kafka: Partition by `user_id` (10K partitions)
- Cassandra: Partition key = `user_id`

### Load Balancing
- API Gateway: Round-robin
- Workers: Consumer groups

## Monitoring & Alerts

**Key Metrics**:
- Messages/sec processed
- Kafka lag (< 1000 messages)
- Delivery success rate (> 99%)
- p99 latency (< 500ms)
- Worker CPU/memory

**Alerts**:
- Kafka lag > 10K
- Success rate < 95%
- Worker failures > 5%

## Failure Handling

**Retry Strategy**:
```
Attempt 1: Immediate
Attempt 2: +5 seconds
Attempt 3: +30 seconds
Attempt 4: +5 minutes
Then: Dead Letter Queue
```

**Circuit Breaker**: Fail fast if downstream unavailable

## Cost Estimation

For 5 billion notifications/day:
- Kafka: $5K/month (10 brokers)
- Workers: $20K/month (1000 instances)
- Cassandra: $10K/month (50 nodes)
- Redis: $2K/month (cluster)
- **Total**: ~$40K/month

## Next Steps
- Detailed component design
- Database schemas
- API specifications
- Deployment architecture
