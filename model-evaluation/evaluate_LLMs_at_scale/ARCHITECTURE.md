# System Architecture - LLM Evaluation at Scale

## 🏗️ Architecture Overview

This system follows a **microservices architecture** with clear separation of concerns, designed for production-scale LLM evaluation.

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                             │
│                                                                     │
│   ┌───────────────────────────────────────────────────────────┐   │
│   │              Next.js Dashboard (Port 3001)                 │   │
│   │  - Job Management UI                                       │   │
│   │  - Real-time Monitoring                                    │   │
│   │  - Analytics Chat (Gemini-powered)                         │   │
│   │  - Deployment Readiness Reports                            │   │
│   └───────────────────────────────────────────────────────────┘   │
│                              ↓ HTTP/REST                           │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         API LAYER                                   │
│                                                                     │
│   ┌──────────────────────┐        ┌──────────────────────┐        │
│   │   API Gateway        │        │  Analytics Service   │        │
│   │   (Port 8000)        │        │   (Port 8003)        │        │
│   │                      │        │                      │        │
│   │ - Auth (JWT)         │        │ - Statistics         │        │
│   │ - Job CRUD           │        │ - Model Comparison   │        │
│   │ - Rate Limiting      │        │ - Cost Analysis      │        │
│   │ - Health Checks      │        │ - Chat Queries       │        │
│   └──────────────────────┘        │ - Deployment Score   │        │
│            ↓                       └──────────────────────┘        │
│            ↓                                 ↓                      │
└─────────────────────────────────────────────────────────────────────┘
                         ↓                     ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      MESSAGE QUEUE LAYER                            │
│                                                                     │
│   ┌───────────────────────────────────────────────────────────┐   │
│   │                  RabbitMQ (Port 5672)                     │   │
│   │                                                            │   │
│   │  Queues:                                                   │   │
│   │  ├─ llm_tasks (Priority Queue)                            │   │
│   │  ├─ metrics_calculation                                   │   │
│   │  └─ dead_letter_queue (Failed tasks)                      │   │
│   └───────────────────────────────────────────────────────────┘   │
│                              ↓                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION LAYER                            │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────┐    │
│   │              Orchestrator (Port 8001)                     │    │
│   │                                                            │    │
│   │  - Job Status Monitoring (every 5s)                       │    │
│   │  - Task Completion Tracking                               │    │
│   │  - Cost Calculation                                       │    │
│   │  - Progress Updates (Redis)                               │    │
│   │  - Auto Status Transitions                                │    │
│   └──────────────────────────────────────────────────────────┘    │
│                              ↓                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                       WORKER LAYER                                  │
│                                                                     │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐            │
│   │   Gemini    │   │     GPT     │   │   Claude    │            │
│   │   Worker    │   │   Worker    │   │   Worker    │            │
│   │             │   │             │   │             │            │
│   │ - Gemini API│   │ - OpenAI API│   │ - Anthropic │            │
│   │ - Caching   │   │ - Caching   │   │ - Caching   │            │
│   │ - Retry     │   │ - Retry     │   │ - Retry     │            │
│   │ - Cost      │   │ - Cost      │   │ - Cost      │            │
│   └─────────────┘   └─────────────┘   └─────────────┘            │
│         ↓                  ↓                  ↓                     │
│         └──────────────────┴──────────────────┘                    │
│                            ↓                                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                       METRICS LAYER                                 │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────┐    │
│   │              Metrics Service (Port 8002)                  │    │
│   │                                                            │    │
│   │  Calculators:                                              │    │
│   │  ├─ BLEU, ROUGE, BERTScore                                │    │
│   │  ├─ Exact Match                                            │    │
│   │  ├─ Hallucination Detection                               │    │
│   │  ├─ Toxicity, Bias, PII                                   │    │
│   │  └─ Deployment Readiness (4-pillar)                       │    │
│   └──────────────────────────────────────────────────────────┘    │
│                              ↓                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                    │
│                                                                     │
│   ┌──────────────┐  ┌───────────┐  ┌─────────────────────────┐   │
│   │  PostgreSQL  │  │   Redis   │  │        MinIO            │   │
│   │  (Port 5432) │  │(Port 6379)│  │   (Port 9000/9001)      │   │
│   │              │  │           │  │                         │   │
│   │ - Users      │  │ - Cache   │  │ - Large Responses       │   │
│   │ - Jobs       │  │ - Session │  │ - Exported Reports      │   │
│   │ - Tasks      │  │ - Progress│  │ - Model Artifacts       │   │
│   │ - Results    │  │ - Rate    │  │ - Backups               │   │
│   │ - Metrics    │  │   Limit   │  │                         │   │
│   │              │  │           │  │                         │   │
│   │ + pgvector   │  └───────────┘  └─────────────────────────┘   │
│   │ + TimescaleDB│                                                │
│   └──────────────┘                                                │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    MONITORING LAYER                                 │
│                                                                     │
│   ┌────────────────┐              ┌────────────────┐              │
│   │   Prometheus   │     ←←←←     │    Grafana     │              │
│   │  (Port 9090)   │              │  (Port 3000)   │              │
│   │                │              │                │              │
│   │ - Metrics      │              │ - Dashboards   │              │
│   │ - Alerts       │              │ - Alerts UI    │              │
│   └────────────────┘              └────────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### 1. Job Creation Flow
```
User (Dashboard)
  → POST /api/v1/jobs (API Gateway)
    → Create Job in PostgreSQL
    → Create Tasks (one per model × prompt)
    → Publish to RabbitMQ (llm_tasks queue)
    ← Return Job ID
  ← Display Job in UI
```

### 2. Task Execution Flow
```
Worker (Gemini/GPT/Claude)
  → Consume from RabbitMQ (llm_tasks)
  → Check Redis cache for response
  → If cache miss:
      → Call LLM API
      → Store response in PostgreSQL
      → Cache in Redis
      → Calculate cost
  → Publish to metrics_calculation queue
  → Update task status
```

### 3. Metrics Calculation Flow
```
Metrics Service
  → Consume from metrics_calculation queue
  → Check Redis cache for metrics
  → If cache miss:
      → Calculate BLEU, ROUGE, BERTScore
      → Detect hallucination, toxicity, bias, PII
      → Store results in PostgreSQL
      → Cache in Redis
  → Update completion status
```

### 4. Orchestration Flow
```
Orchestrator (Background Loop - every 5s)
  → Query all active jobs from PostgreSQL
  → For each job:
      → Count completed/failed tasks
      → Calculate total cost
      → Update progress in Redis
      → If all tasks done:
          → Update job status to completed
          → Calculate final metrics
```

### 5. Analytics & Chat Flow
```
User (Dashboard Chat)
  → POST /api/v1/chat/query (Analytics Service)
    → Fetch current statistics from PostgreSQL
    → Build context for Gemini
    → Send query to Gemini API
    → Parse response
    → Return answer + relevant data
  ← Display in chat UI
```

## 📊 Database Schema

### PostgreSQL Tables

#### users
```sql
- id (UUID, PK)
- email (String, unique)
- hashed_password (String)
- created_at (Timestamp)
```

#### jobs
```sql
- id (UUID, PK)
- user_id (UUID, FK → users)
- name (String)
- status (Enum: queued, running, completed, failed, cancelled)
- priority (Integer: 1-3)
- total_tasks (Integer)
- completed_tasks (Integer)
- failed_tasks (Integer)
- total_cost_usd (Decimal)
- metadata (JSONB)
- created_at (Timestamp)
- started_at (Timestamp)
- completed_at (Timestamp)
```

#### evaluation_tasks
```sql
- id (UUID, PK)
- job_id (UUID, FK → jobs)
- model (String)
- prompt (Text)
- response (Text)
- reference (Text, nullable)
- status (Enum: queued, running, completed, failed, retrying)
- retry_count (Integer)
- error_message (Text, nullable)
- tokens_used (Integer)
- cost_usd (Decimal)
- latency_ms (Integer)
- created_at (Timestamp)
- completed_at (Timestamp)
```

#### evaluation_results
```sql
- id (UUID, PK)
- task_id (UUID, FK → evaluation_tasks)
- metric_type (String: bleu, rouge, etc.)
- score (Float)
- metrics (JSONB)
- embedding (Vector(1536)) -- pgvector
- created_at (Timestamp) -- TimescaleDB hypertable
```

#### dead_letter_queue
```sql
- id (UUID, PK)
- task_id (UUID)
- error_type (String)
- error_message (Text)
- retry_count (Integer)
- original_message (JSONB)
- created_at (Timestamp)
```

## 🔐 Security Architecture

### Authentication & Authorization
- **JWT tokens** for API authentication
- Token expiry: 24 hours
- Refresh token support (planned)
- Rate limiting per user

### API Security
- CORS configured for dashboard origin
- Input validation with Pydantic
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection in frontend

### Secrets Management
- API keys in environment variables
- Never logged or exposed
- Separate keys per environment
- Key rotation supported

## 🚀 Scalability Design

### Horizontal Scaling
- **Workers**: Scale to N instances per model
  ```bash
  docker-compose up -d --scale worker-gemini=10
  ```
- **API Gateway**: Behind load balancer
- **Orchestrator**: Single instance (leader election planned)

### Vertical Scaling
- PostgreSQL: Read replicas for analytics
- Redis: Cluster mode for high availability
- RabbitMQ: Cluster with mirrored queues

### Performance Optimizations
- **Response Caching**: 24-hour TTL in Redis
- **Connection Pooling**: Database connections reused
- **Batch Processing**: Metrics calculated in batches
- **Async I/O**: All services use async/await
- **Priority Queues**: High-priority jobs processed first

## 💾 Data Retention

### Hot Data (Fast Access)
- Recent 7 days in PostgreSQL main tables
- Redis cache: 24 hours
- Real-time metrics in memory

### Warm Data (Archive)
- 8-90 days in TimescaleDB compressed chunks
- MinIO for large responses
- Aggregated metrics only

### Cold Data (Long-term)
- 90+ days in S3/MinIO with compression
- Only job metadata and final results
- Raw responses deleted

## 🔄 Deployment Strategy

### Blue-Green Deployment
1. Deploy new version (green)
2. Run smoke tests
3. Switch traffic gradually
4. Monitor for issues
5. Rollback if needed

### Rolling Updates
- Workers updated first (no downtime)
- Services updated one at a time
- Database migrations run before deployment
- Health checks ensure readiness

### Disaster Recovery
- Database backups: Daily to MinIO
- Redis persistence: AOF + RDB
- RabbitMQ: Durable queues
- Recovery time objective: < 1 hour

## 📈 Monitoring & Observability

### Metrics (Prometheus)
- Request rate, latency, errors
- Queue depth and processing time
- Database connection pool usage
- Cache hit rates
- Cost per job/task

### Logs
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized in ELK stack (planned)

### Traces
- Distributed tracing with OpenTelemetry (planned)
- Request ID propagation
- Cross-service call tracking

### Alerts
- High error rate (>5%)
- Queue depth growing (>1000)
- Database connection exhaustion
- High latency (P95 >1s)
- Cost spike (>$100/hour)

## 🎯 Design Decisions

### Why Microservices?
- **Independent Scaling**: Scale workers separately from API
- **Technology Flexibility**: Different languages if needed
- **Fault Isolation**: One service failure doesn't crash system
- **Team Autonomy**: Teams can work on services independently

### Why RabbitMQ?
- **Reliability**: Guaranteed message delivery with DLQ
- **Priority Queues**: High-priority jobs processed first
- **Dead Letter Queue**: Failed tasks don't block queue
- **Mature**: Battle-tested in production

### Why PostgreSQL + Extensions?
- **pgvector**: Semantic search without separate vector DB
- **TimescaleDB**: Time-series metrics without separate DB
- **ACID**: Strong consistency for job state
- **Rich Queries**: Complex analytics queries

### Why Redis?
- **Speed**: Sub-millisecond latency
- **Versatility**: Cache, sessions, rate limiting, progress
- **Pub/Sub**: Real-time updates (planned)
- **Simple**: Easy to operate

### Why Next.js?
- **Server-Side Rendering**: Fast initial load
- **React**: Rich component ecosystem
- **TypeScript**: Type safety in frontend
- **API Routes**: BFF pattern if needed

## 🔮 Future Enhancements

### Short-term (1-3 months)
- [ ] Complete all 16 metrics
- [ ] Grafana dashboards
- [ ] WebSocket for real-time updates
- [ ] Multi-user team support

### Medium-term (3-6 months)
- [ ] A/B testing framework
- [ ] Model fine-tuning integration
- [ ] Automated deployment gates
- [ ] Advanced cost optimization

### Long-term (6-12 months)
- [ ] Multi-region deployment
- [ ] Custom metric plugins
- [ ] ML-powered anomaly detection
- [ ] Self-healing infrastructure

---

**Architecture Version**: 2.0  
**Last Updated**: Current Session  
**Status**: Production-Ready ✅
