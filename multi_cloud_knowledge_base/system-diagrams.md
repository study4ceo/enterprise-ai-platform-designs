# Universal Knowledge Hub - System Diagrams

**Document Date:** June 18, 2026  
**Version:** 1.0  
**Purpose:** Visual architecture and data flow diagrams

---

## 1. Complete System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web App<br/>Next.js 16]
        SLACK_BOT[Slack Bot]
        EXT[Browser Extension]
    end
    
    subgraph "API Layer"
        GATEWAY[API Gateway<br/>Golang + Fiber]
        AUTH[Clerk Auth]
        RATE[Unkey Rate Limit]
    end
    
    subgraph "Core Services"
        SEARCH[Search Service<br/>Golang]
        AI[AI Service<br/>Python + LangChain]
        INDEX[Indexing Service<br/>Python]
        ANALYTICS[Analytics Service<br/>Golang]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>+ pgvector)]
        REDIS[(Redis Cache)]
    end
    
    subgraph "Connector Layer"
        HUB[Connector Hub<br/>Golang]
        QUEUE[RabbitMQ]
        WEBHOOK[Webhook Server]
    end
    
    subgraph "Data Sources"
        SLACK[Slack]
        JIRA[Jira]
        GMAIL[Gmail]
        S3[AWS S3]
        GITHUB[GitHub]
        OTHERS[... 20+ more]
    end
    
    subgraph "Observability"
        LOGFIRE[Logfire]
        PROM[Prometheus]
        GRAF[Grafana]
        SENTRY[Sentry]
    end
    
    WEB --> GATEWAY
    SLACK_BOT --> GATEWAY
    EXT --> GATEWAY
    
    GATEWAY --> AUTH
    GATEWAY --> RATE
    GATEWAY --> SEARCH
    GATEWAY --> AI
    GATEWAY --> INDEX
    GATEWAY --> ANALYTICS
    
    SEARCH --> PG
    SEARCH --> REDIS
    AI --> PG
    AI --> REDIS
    INDEX --> PG
    ANALYTICS --> PG
    
    HUB --> QUEUE
    HUB --> WEBHOOK
    QUEUE --> INDEX
    
    SLACK --> HUB
    JIRA --> HUB
    GMAIL --> HUB
    S3 --> HUB
    GITHUB --> HUB
    OTHERS --> HUB
    
    GATEWAY --> LOGFIRE
    SEARCH --> PROM
    AI --> LOGFIRE
    INDEX --> LOGFIRE
    
    PROM --> GRAF
    GATEWAY --> SENTRY
```

---

## 2. Search Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Gateway
    participant Search
    participant Cache
    participant DB
    participant AI
    
    User->>Gateway: POST /api/v1/search<br/>{query: "deploy process"}
    Gateway->>Gateway: Authenticate
    Gateway->>Gateway: Check rate limit
    Gateway->>Search: gRPC SearchRequest
    
    Search->>Cache: Check cache
    alt Cache Hit
        Cache-->>Search: Cached results
    else Cache Miss
        Search->>AI: Generate embedding
        AI-->>Search: Vector [3072-dim]
        
        par Vector Search
            Search->>DB: Vector similarity search
            DB-->>Search: Top 50 results
        and Full-Text Search
            Search->>DB: Full-text search
            DB-->>Search: Top 50 results
        end
        
        Search->>Search: Hybrid ranking (RRF)
        Search->>Search: Permission filter
        Search->>Cache: Store in cache
    end
    
    Search-->>Gateway: Search results
    Gateway-->>User: JSON response<br/>{results: [...]}
```

---

## 3. AI Q&A (RAG) Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Gateway
    participant AI
    participant Search
    participant DB
    participant LLM as OpenAI/Claude
    
    User->>Gateway: POST /api/v1/qa<br/>{question: "How do we deploy?"}
    Gateway->>AI: gRPC QARequest
    
    AI->>AI: Query understanding
    AI->>AI: Generate embedding
    
    AI->>Search: Hybrid search (top 50)
    Search->>DB: Vector + full-text
    DB-->>Search: 50 documents
    Search-->>AI: Search results
    
    AI->>AI: Re-rank by relevance (top 10)
    AI->>AI: Build context window
    AI->>AI: Engineer prompt
    
    AI->>LLM: Generate answer with citations
    
    loop Streaming Response
        LLM-->>AI: Token stream
        AI-->>Gateway: Stream chunk
        Gateway-->>User: SSE chunk
    end
    
    AI->>DB: Store Q&A history
    AI->>AI: Calculate confidence
    
    AI-->>Gateway: Complete response
    Gateway-->>User: {answer, sources, confidence}
```

---

## 4. Document Indexing Flow Diagram

```mermaid
sequenceDiagram
    participant Source as Data Source<br/>(Slack/Jira/etc)
    participant Connector
    participant Queue as RabbitMQ
    participant Indexing
    participant AI
    participant DB
    
    Source->>Connector: Webhook: New message
    Connector->>Connector: Validate & transform
    Connector->>Queue: Publish event
    
    Queue->>Indexing: Consume event
    
    alt File Document
        Indexing->>Source: Download file
        Source-->>Indexing: File content
        Indexing->>Indexing: Extract text (PDF/DOCX)
    end
    
    Indexing->>Indexing: Clean & normalize text
    Indexing->>Indexing: Semantic chunking<br/>(512 tokens, 50 overlap)
    
    par Generate Embeddings
        loop For each chunk
            Indexing->>AI: Generate embedding
            AI-->>Indexing: Vector [3072-dim]
        end
    end
    
    Indexing->>DB: BEGIN TRANSACTION
    Indexing->>DB: INSERT document
    Indexing->>DB: INSERT chunks
    Indexing->>DB: INSERT embeddings
    Indexing->>DB: COMMIT
    
    Indexing->>Connector: Update sync status
```

---

## 5. Connector Sync Architecture

```mermaid
graph TB
    subgraph "Connector Hub"
        MGR[Connector Manager]
        SYNC[Sync Scheduler]
        RATE[Rate Limiter]
        RETRY[Retry Handler]
    end
    
    subgraph "Connector Types"
        direction LR
        FULL[Full Sync]
        INCR[Incremental Sync]
        RT[Real-time Sync]
    end
    
    subgraph "Individual Connectors"
        C1[Slack Connector]
        C2[Jira Connector]
        C3[Gmail Connector]
        C4[S3 Connector]
        CMORE[... 21 more ...]
    end
    
    subgraph "Event Queue"
        QUEUE[RabbitMQ]
        WEBHOOK[Webhook Server]
    end
    
    MGR --> SYNC
    MGR --> RATE
    MGR --> RETRY
    
    SYNC --> FULL
    SYNC --> INCR
    SYNC --> RT
    
    FULL --> C1
    FULL --> C2
    INCR --> C3
    RT --> C4
    
    C1 --> QUEUE
    C2 --> QUEUE
    C3 --> QUEUE
    C4 --> WEBHOOK
    CMORE --> QUEUE
    
    WEBHOOK --> QUEUE
```

---

## 6. Security Architecture Layers

```mermaid
graph TD
    subgraph "Layer 7: Application"
        INPUT[Input Validation]
        OUTPUT[Output Sanitization]
        XSS[XSS Protection]
    end
    
    subgraph "Layer 6: API Gateway"
        AUTH[Authentication<br/>Clerk + PASETO]
        AUTHZ[Authorization<br/>RBAC]
        RATE2[Rate Limiting<br/>Unkey]
    end
    
    subgraph "Layer 5: Data Access"
        RLS[Row-Level Security]
        PERM[Permission Queries]
        AUDIT[Audit Logging]
    end
    
    subgraph "Layer 4: Network"
        TLS[TLS 1.3]
        WAF[WAF Cloudflare]
        DDOS[DDoS Protection]
    end
    
    subgraph "Layer 3: Data Protection"
        ENC_REST[Encryption at Rest<br/>AES-256]
        ENC_TRANSIT[Encryption in Transit]
        VAULT[Secrets Vault]
    end
    
    subgraph "Layer 2: Infrastructure"
        VPC[VPC Isolation]
        SG[Security Groups]
        PRIV[Private Subnets]
    end
    
    subgraph "Layer 1: Monitoring"
        SIEM[SIEM Logfire]
        COMP[Compliance SOC2]
        SCAN[Security Scanning]
    end
    
    INPUT --> AUTH
    XSS --> AUTH
    AUTH --> RLS
    AUTHZ --> PERM
    RLS --> TLS
    TLS --> ENC_REST
    ENC_TRANSIT --> VPC
    VPC --> SIEM
    AUDIT --> SIEM
```

---

## 7. Data Flow: User Query to Answer

```mermaid
flowchart TD
    START([User asks:<br/>"How do we deploy?"]) --> AUTH{Authenticated?}
    
    AUTH -->|No| ERR1[401 Unauthorized]
    AUTH -->|Yes| RATE{Rate limit OK?}
    
    RATE -->|No| ERR2[429 Too Many Requests]
    RATE -->|Yes| EMBED[Generate Query Embedding<br/>OpenAI API]
    
    EMBED --> VSEARCH[Vector Search<br/>pgvector]
    EMBED --> FTSEARCH[Full-Text Search<br/>PostgreSQL]
    
    VSEARCH --> MERGE[Hybrid Ranking<br/>RRF Algorithm]
    FTSEARCH --> MERGE
    
    MERGE --> PERM{User has<br/>permission?}
    
    PERM -->|No| FILTER[Filter out restricted docs]
    PERM -->|Yes| KEEP[Keep authorized docs]
    
    FILTER --> TOP50[Top 50 Results]
    KEEP --> TOP50
    
    TOP50 --> RERANK[Re-rank by Relevance<br/>Semantic similarity]
    
    RERANK --> TOP10[Select Top 10]
    
    TOP10 --> CONTEXT[Build Context Window<br/>Format for LLM]
    
    CONTEXT --> PROMPT[Engineer Prompt<br/>Add instructions]
    
    PROMPT --> LLM[Call GPT-5.5/Claude<br/>Generate answer]
    
    LLM --> EXTRACT[Extract Citations<br/>Calculate confidence]
    
    EXTRACT --> STORE[Store in Q&A History]
    
    STORE --> RESPONSE[Return Answer + Sources]
    
    RESPONSE --> END([User receives answer<br/>with citations])
```

---

## 8. Deployment Architecture (Kubernetes)

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[AWS ALB]
    end
    
    subgraph "Kubernetes Cluster - Production"
        subgraph "Namespace: knowledge-hub"
            subgraph "API Gateway Pods"
                GW1[api-gateway-1]
                GW2[api-gateway-2]
                GW3[api-gateway-3]
            end
            
            subgraph "Search Service Pods"
                S1[search-1]
                S2[search-2]
                S3[search-3]
            end
            
            subgraph "AI Service Pods"
                AI1[ai-service-1]
                AI2[ai-service-2]
            end
            
            subgraph "Indexing Service Pods"
                I1[indexing-1]
                I2[indexing-2]
            end
            
            subgraph "Connector Hub Pods"
                C1[connector-hub-1]
                C2[connector-hub-2]
            end
        end
        
        HPA[Horizontal Pod<br/>Autoscaler]
    end
    
    subgraph "Data Layer - AWS RDS"
        PG_PRIMARY[(PostgreSQL<br/>Primary)]
        PG_REPLICA1[(PostgreSQL<br/>Replica 1)]
        PG_REPLICA2[(PostgreSQL<br/>Replica 2)]
    end
    
    subgraph "Cache Layer - ElastiCache"
        REDIS_M[(Redis Master)]
        REDIS_S1[(Redis Slave 1)]
        REDIS_S2[(Redis Slave 2)]
    end
    
    subgraph "Message Queue"
        RMQ[RabbitMQ Cluster]
    end
    
    LB --> GW1
    LB --> GW2
    LB --> GW3
    
    GW1 --> S1
    GW2 --> S2
    GW3 --> S3
    
    GW1 --> AI1
    GW2 --> AI2
    
    S1 --> PG_PRIMARY
    S2 --> PG_REPLICA1
    S3 --> PG_REPLICA2
    
    AI1 --> PG_REPLICA1
    AI2 --> PG_REPLICA2
    
    I1 --> PG_PRIMARY
    I2 --> PG_PRIMARY
    
    S1 --> REDIS_M
    S2 --> REDIS_S1
    S3 --> REDIS_S2
    
    C1 --> RMQ
    C2 --> RMQ
    
    RMQ --> I1
    RMQ --> I2
    
    HPA -.-> GW1
    HPA -.-> S1
    HPA -.-> AI1
```

---

## 9. CI/CD Pipeline

```mermaid
flowchart LR
    START([Git Push to main]) --> TRIGGER[GitHub Actions<br/>Triggered]
    
    TRIGGER --> CHECKOUT[Checkout Code]
    
    CHECKOUT --> PARALLEL{Parallel Jobs}
    
    PARALLEL --> TEST_GO[Go Unit Tests]
    PARALLEL --> TEST_PY[Python Unit Tests]
    PARALLEL --> LINT[Linting<br/>Go: golangci-lint<br/>Python: ruff]
    PARALLEL --> SECURITY[Security Scan<br/>Go: govulncheck<br/>Python: safety]
    
    TEST_GO --> BUILD
    TEST_PY --> BUILD
    LINT --> BUILD
    SECURITY --> BUILD
    
    BUILD[Build Docker Images] --> PUSH[Push to Registry<br/>ghcr.io]
    
    PUSH --> DEPLOY{Deploy to<br/>Environment}
    
    DEPLOY --> STAGING[Staging<br/>Auto-deploy]
    DEPLOY --> PROD[Production<br/>Manual approval]
    
    STAGING --> SMOKE1[Smoke Tests]
    PROD --> SMOKE2[Smoke Tests]
    
    SMOKE1 --> SUCCESS1{Tests Pass?}
    SMOKE2 --> SUCCESS2{Tests Pass?}
    
    SUCCESS1 -->|Yes| NOTIFY1[Slack Notification]
    SUCCESS1 -->|No| ROLLBACK1[Rollback]
    
    SUCCESS2 -->|Yes| NOTIFY2[Slack Notification]
    SUCCESS2 -->|No| ROLLBACK2[Rollback]
    
    NOTIFY1 --> END1([Staging Deployed])
    NOTIFY2 --> END2([Production Deployed])
    
    ROLLBACK1 --> ERR1([Deploy Failed])
    ROLLBACK2 --> ERR2([Deploy Failed])
```

---

## 10. Monitoring & Observability Stack

```mermaid
graph TD
    subgraph "Application Services"
        API[API Gateway]
        SEARCH[Search Service]
        AI_SVC[AI Service]
        INDEX[Indexing Service]
    end
    
    subgraph "Metrics Collection"
        PROM[Prometheus]
        NODE[Node Exporter]
        KUBE[Kube State Metrics]
    end
    
    subgraph "Logging"
        LOGFIRE[Logfire<br/>Structured Logs]
        FLUENTD[Fluentd]
    end
    
    subgraph "Tracing"
        OTEL[OpenTelemetry]
        JAEGER[Jaeger]
    end
    
    subgraph "Visualization"
        GRAFANA[Grafana Dashboards]
    end
    
    subgraph "Alerting"
        ALERT_MGR[Alertmanager]
        PAGER[PagerDuty]
        SLACK_ALERT[Slack Alerts]
    end
    
    subgraph "Error Tracking"
        SENTRY[Sentry]
    end
    
    API --> PROM
    SEARCH --> PROM
    AI_SVC --> LOGFIRE
    INDEX --> LOGFIRE
    
    API --> OTEL
    SEARCH --> OTEL
    AI_SVC --> OTEL
    
    API --> SENTRY
    
    NODE --> PROM
    KUBE --> PROM
    
    PROM --> GRAFANA
    LOGFIRE --> GRAFANA
    OTEL --> JAEGER
    JAEGER --> GRAFANA
    
    PROM --> ALERT_MGR
    ALERT_MGR --> PAGER
    ALERT_MGR --> SLACK_ALERT
```

---

**Document Status:** ✅ Complete - 10 comprehensive system diagrams

**Usage:** These diagrams can be rendered using Mermaid-compatible tools (GitHub, GitLab, VS Code, draw.io, etc.)
