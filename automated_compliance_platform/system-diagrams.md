# AI-Powered Automated Compliance Platform - System Diagrams

**Date:** June 23, 2026  
**Version:** 1.0

---

## 1. Complete System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Dashboard<br/>Next.js 16]
        MOBILE[Mobile Apps<br/>iOS/Android]
        API_CLIENT[API Clients<br/>External Systems]
        KAFKA_CLIENT[Kafka Producers<br/>Real-time Events]
    end
    
    subgraph "API Gateway - Golang 1.26.4"
        GW[API Gateway<br/>Fiber 2.52]
        AUTH[OAuth 2.0 + JWT]
        RATE[Rate Limiter<br/>1000 req/min]
        CACHE[Response Cache<br/>Redis 7.4]
    end
    
    subgraph "Core Services"
        TX_MON[Transaction Monitor<br/>Golang 1.26.4]
        DOC_ANA[Document Analyzer<br/>Python 3.13 + LangChain 0.4]
        REPORT[Report Generator<br/>Golang 1.26.4]
        RISK[Risk Scorer<br/>Python 3.13 + XGBoost 2.1]
        WATCHLIST[Watchlist Screener<br/>Golang 1.26.4]
        POLICY[Policy Engine<br/>Golang 1.26.4]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL 17.2<br/>Primary + RLS)]
        TS[(TimescaleDB 2.18<br/>Audit Log)]
        QDRANT[(Qdrant 1.12<br/>Vector Store)]
        REDIS[(Redis 7.4<br/>Cluster)]
        S3[(S3/GCS<br/>Reports + Models)]
    end
    
    WEB --> GW
    MOBILE --> GW
    API_CLIENT --> GW
    KAFKA_CLIENT --> TX_MON
    
    GW --> AUTH
    GW --> RATE
    GW --> CACHE
    
    GW --> TX_MON
    GW --> DOC_ANA
    GW --> REPORT
    
    TX_MON --> WATCHLIST
    TX_MON --> RISK
    TX_MON --> POLICY
    
    TX_MON --> PG
    DOC_ANA --> QDRANT
    REPORT --> S3
    RISK --> PG
    
    TX_MON --> TS
    POLICY --> TS
    
    WATCHLIST --> REDIS
    RISK --> REDIS
```

---

## 2. Transaction Screening Flow

```mermaid
sequenceDiagram
    participant Client
    participant Gateway
    participant Monitor
    participant Watchlist
    participant RiskScorer
    participant Policy
    participant AuditLog
    participant DB
    
    Client->>Gateway: POST /transactions/screen
    Gateway->>Gateway: Validate OAuth token
    Gateway->>Gateway: Check rate limit
    
    Gateway->>Monitor: Screen transaction
    
    par Parallel Screening
        Monitor->>Watchlist: Screen entity (50ms)
        and
        Monitor->>RiskScorer: Calculate risk (40ms)
        and
        Monitor->>Policy: Evaluate policies (10ms)
    end
    
    Watchlist-->>Monitor: Match result (score: 0.0-1.0)
    RiskScorer-->>Monitor: Risk score (0-100)
    Policy-->>Monitor: Policy violations
    
    Monitor->>Monitor: Determine approval
    
    par Non-blocking Operations
        Monitor->>AuditLog: Log screening (async)
        and
        Monitor->>DB: Store transaction
    end
    
    Monitor-->>Gateway: Screening result
    Gateway-->>Client: Response (87ms total)
```

---

## 3. RAG Document Analysis Pipeline

```mermaid
flowchart TD
    START([User Query]) --> EMBED[Generate Query<br/>Embedding<br/>text-embedding-3-large]
    
    EMBED --> SEARCH[Vector Search<br/>Qdrant 1.12<br/>Top 10 Results]
    
    SEARCH --> FORMAT[Format Context<br/>from Chunks]
    
    FORMAT --> PARALLEL{Parallel<br/>LLM Calls}
    
    PARALLEL --> GPT[GPT-4o-2024-08-06<br/>Generate Answer]
    PARALLEL --> CLAUDE[Claude Opus 4.8<br/>Generate Answer]
    
    GPT --> COMBINE[Combine Responses]
    CLAUDE --> COMBINE
    
    COMBINE --> CITE[Extract Citations<br/>Regulation Sections]
    
    CITE --> CONF[Calculate Confidence<br/>Based on Scores]
    
    CONF --> RESULT([Return Answer<br/>+ Citations<br/>+ Confidence])
```

---

## 4. ML Risk Scoring Architecture

```mermaid
flowchart LR
    TX[Transaction<br/>Input] --> FEAT[Feature Engineering<br/>50+ Features]
    
    FEAT --> ENS{Ensemble<br/>Models}
    
    ENS --> XGB[XGBoost 2.1<br/>Weight: 0.50]
    ENS --> LGB[LightGBM 4.5<br/>Weight: 0.35]
    ENS --> RF[Random Forest<br/>Weight: 0.15]
    
    XGB --> WEIGHTED[Weighted<br/>Combination]
    LGB --> WEIGHTED
    RF --> WEIGHTED
    
    WEIGHTED --> SCORE[Risk Score<br/>0-100]
    
    XGB --> SHAP[SHAP Explainer<br/>Top 5 Factors]
    
    SCORE --> OUTPUT([Risk Score<br/>+ Explanation<br/>+ Confidence])
    SHAP --> OUTPUT
```

---

## 5. Watchlist Screening Flow

```mermaid
flowchart TD
    ENTITY[Entity Name] --> NORM[Normalize Name<br/>Lowercase + Trim]
    
    NORM --> CACHE{Redis Cache?}
    
    CACHE -->|Hit| RETURN_CACHE[Return Cached<br/>Result]
    CACHE -->|Miss| PARALLEL{Parallel<br/>Screening}
    
    PARALLEL --> OFAC[Screen OFAC<br/>Fuzzy Match]
    PARALLEL --> UN[Screen UN<br/>Fuzzy Match]
    PARALLEL --> EU[Screen EU<br/>Fuzzy Match]
    PARALLEL --> UK[Screen UK<br/>Fuzzy Match]
    
    OFAC --> COLLECT[Collect Matches<br/>Score >= 0.50]
    UN --> COLLECT
    EU --> COLLECT
    UK --> COLLECT
    
    COLLECT --> SORT[Sort by Score<br/>Descending]
    
    SORT --> RISK{Highest<br/>Score?}
    
    RISK -->|>= 0.85| HIGH[High Risk<br/>Block Transaction]
    RISK -->|0.50-0.85| REVIEW[Manual Review<br/>Required]
    RISK -->|< 0.50| PASS[Pass<br/>No Match]
    
    HIGH --> CACHE_STORE[Cache Result<br/>1 hour TTL]
    REVIEW --> CACHE_STORE
    PASS --> CACHE_STORE
    
    CACHE_STORE --> RESULT([Return Result])
    RETURN_CACHE --> RESULT
```

---

## 6. Cryptographic Audit Trail

```mermaid
flowchart TD
    EVENT[Compliance Event] --> CREATE[Create Audit Record<br/>ID, Timestamp, Details]
    
    CREATE --> PREV[Include Previous<br/>Record Hash]
    
    PREV --> HASH[Calculate SHA-256<br/>Hash]
    
    HASH --> SIGN[Sign with ECDSA<br/>P-256 Curve]
    
    SIGN --> STORE[Store in TimescaleDB<br/>Immutable Hypertable]
    
    STORE --> UPDATE[Update Last Hash<br/>for Chain]
    
    UPDATE --> DONE([Audit Record<br/>Written])
    
    style STORE fill:#90EE90
    style SIGN fill:#FFB6C1
```

---

## 7. Report Generation Workflow

```mermaid
sequenceDiagram
    participant System
    participant Generator
    participant DB
    participant Validator
    participant S3
    participant Audit
    participant Authority
    
    System->>Generator: Trigger SAR/CTR/MiFID Report
    Generator->>DB: Fetch transaction data
    Generator->>DB: Fetch entity data
    Generator->>DB: Fetch historical data
    
    DB-->>Generator: Complete dataset
    
    Generator->>Generator: Build report structure
    Generator->>Generator: Populate all fields
    
    Generator->>Validator: Validate schema
    
    alt Validation Passes
        Validator-->>Generator: Valid
        Generator->>Generator: Generate PDF
        Generator->>S3: Store report
        Generator->>Audit: Log generation
        
        opt Automatic Submission
            Generator->>Authority: Submit electronically
            Authority-->>Generator: Confirmation
        end
        
        Generator-->>System: Success
    else Validation Fails
        Validator-->>Generator: Errors
        Generator-->>System: Validation failed
    end
```

---

## 8. Multi-Jurisdiction Compliance

```mermaid
graph TB
    TX[Transaction] --> DETECT[Detect Jurisdictions<br/>Origin + Destination]
    
    DETECT --> US{US<br/>Involved?}
    DETECT --> EU{EU<br/>Involved?}
    DETECT --> UK{UK<br/>Involved?}
    DETECT --> ASIA{Asia<br/>Involved?}
    
    US --> US_RULES[Apply US Rules<br/>BSA, PATRIOT Act<br/>FinCEN]
    EU --> EU_RULES[Apply EU Rules<br/>AML Directives<br/>MiFID II]
    UK --> UK_RULES[Apply UK Rules<br/>FCA Requirements]
    ASIA --> ASIA_RULES[Apply Asia Rules<br/>MAS, HKMA]
    
    US_RULES --> AGGREGATE[Aggregate All<br/>Requirements]
    EU_RULES --> AGGREGATE
    UK_RULES --> AGGREGATE
    ASIA_RULES --> AGGREGATE
    
    AGGREGATE --> CONFLICT{Rules<br/>Conflict?}
    
    CONFLICT -->|Yes| MOST_STRICT[Apply Most<br/>Restrictive Rule]
    CONFLICT -->|No| APPLY[Apply All Rules]
    
    MOST_STRICT --> RESULT[Compliance<br/>Decision]
    APPLY --> RESULT
```

---

## 9. Exception Management Flow

```mermaid
stateDiagram-v2
    [*] --> Flagged: Transaction flagged
    
    Flagged --> Assigned: Auto-assign to reviewer
    
    Assigned --> UnderReview: Reviewer starts review
    
    UnderReview --> Approved: Approve with justification
    UnderReview --> Rejected: Reject with reason
    UnderReview --> Escalated: 4 hours elapsed
    
    Escalated --> SeniorReview: Senior officer assigned
    
    SeniorReview --> Approved: Senior approves
    SeniorReview --> Rejected: Senior rejects
    
    Approved --> AuditLogged: Log decision
    Rejected --> AuditLogged: Log decision
    
    AuditLogged --> NotifyOriginator: Notify within 60s
    
    NotifyOriginator --> [*]
    
    note right of Escalated
        Automatic escalation
        Email + SMS alerts
    end note
    
    note right of AuditLogged
        Immutable audit record
        Includes justification
    end note
```

---

## 10. Caching Strategy

```mermaid
graph TB
    REQUEST[API Request] --> L1{L1: Redis<br/>Cluster Cache}
    
    L1 -->|Hit| RETURN[Return Cached]
    L1 -->|Miss| COMPUTE[Compute Result]
    
    COMPUTE --> WATCHLIST_CACHE{Need Watchlist?}
    WATCHLIST_CACHE -->|Cached| USE_WATCHLIST[Use Cached<br/>1 hour TTL]
    WATCHLIST_CACHE -->|Miss| FETCH_WATCHLIST[Fetch from DB]
    
    FETCH_WATCHLIST --> CACHE_WATCHLIST[Cache 1 hour]
    CACHE_WATCHLIST --> USE_WATCHLIST
    
    USE_WATCHLIST --> RISK_CACHE{Need Risk Score?}
    
    RISK_CACHE -->|Cached| USE_RISK[Use Cached<br/>5 min TTL]
    RISK_CACHE -->|Miss| CALC_RISK[Calculate Risk]
    
    CALC_RISK --> CACHE_RISK[Cache 5 min]
    CACHE_RISK --> USE_RISK
    
    USE_RISK --> FINAL[Final Result]
    FINAL --> CACHE_RESULT[Cache Result<br/>1 min TTL]
    CACHE_RESULT --> RETURN
    
    style RETURN fill:#90EE90
    style FETCH_WATCHLIST fill:#FFB6C1
    style CALC_RISK fill:#FFB6C1
```

---

## 11. Deployment Architecture

```mermaid
graph TB
    subgraph "Production Cluster - Kubernetes 1.32"
        subgraph "API Layer"
            GW1[Gateway Pod 1]
            GW2[Gateway Pod 2]
            GW3[Gateway Pod 3]
            LB[Load Balancer<br/>Nginx]
        end
        
        subgraph "Service Layer"
            TX1[Monitor Pod 1-5]
            TX2[Monitor Pod 6-10]
            DOC1[Analyzer Pod 1-3]
            RISK1[Risk Scorer Pod 1-5]
        end
        
        subgraph "Data Layer"
            PG_PRIMARY[(PostgreSQL 17.2<br/>Primary)]
            PG_REPLICA1[(PostgreSQL<br/>Replica 1)]
            PG_REPLICA2[(PostgreSQL<br/>Replica 2)]
            TS[(TimescaleDB 2.18)]
            REDIS_CLUSTER[(Redis 7.4<br/>Cluster 3 nodes)]
            QDRANT[(Qdrant 1.12)]
        end
    end
    
    LB --> GW1
    LB --> GW2
    LB --> GW3
    
    GW1 --> TX1
    GW2 --> TX2
    GW3 --> DOC1
    
    TX1 --> RISK1
    TX2 --> RISK1
    
    TX1 --> PG_PRIMARY
    TX2 --> PG_PRIMARY
    RISK1 --> PG_REPLICA1
    DOC1 --> QDRANT
    
    PG_PRIMARY -->|Streaming| PG_REPLICA1
    PG_PRIMARY -->|Streaming| PG_REPLICA2
    
    TX1 --> TS
    TX2 --> TS
    
    TX1 --> REDIS_CLUSTER
    RISK1 --> REDIS_CLUSTER
```

---

## 12. Auto-Scaling Behavior

```mermaid
flowchart TD
    MONITOR[Monitor Metrics<br/>CPU, Memory, Queue] --> CHECK{Thresholds<br/>Exceeded?}
    
    CHECK -->|No| STABLE[Maintain<br/>Current Pods]
    CHECK -->|Yes| DIRECTION{Scale<br/>Direction?}
    
    DIRECTION -->|Up| CPU_CHECK{CPU > 70%<br/>OR<br/>Queue > 100?}
    DIRECTION -->|Down| IDLE_CHECK{CPU < 30%<br/>AND<br/>Queue < 20?}
    
    CPU_CHECK -->|Yes| MAX_CHECK{At Max<br/>Replicas?}
    CPU_CHECK -->|No| STABLE
    
    MAX_CHECK -->|No| SCALE_UP[Add Pods<br/>+2 every 15s]
    MAX_CHECK -->|Yes| ALERT[Alert Admin<br/>Need More Capacity]
    
    IDLE_CHECK -->|Yes| MIN_CHECK{At Min<br/>Replicas?}
    IDLE_CHECK -->|No| STABLE
    
    MIN_CHECK -->|No| SCALE_DOWN[Remove Pods<br/>-1 every 60s]
    MIN_CHECK -->|Yes| STABLE
    
    SCALE_UP --> WAIT[Wait 60s<br/>Stabilization]
    SCALE_DOWN --> WAIT
    
    WAIT --> MONITOR
    STABLE --> MONITOR
    ALERT --> MONITOR
```

---

## 13. Disaster Recovery Flow

```mermaid
sequenceDiagram
    participant Primary as Primary Region<br/>(AWS us-east-1)
    participant Monitor as Health Monitor
    participant DR as DR Region<br/>(GCP us-central1)
    participant DNS
    participant Client
    
    Primary->>Monitor: Heartbeat (every 10s)
    
    alt Normal Operation
        Monitor->>Primary: Healthy
        Client->>DNS: Resolve domain
        DNS-->>Client: Primary IP
        Client->>Primary: Requests
    end
    
    alt Failure Detected
        Primary-xMonitor: No heartbeat (30s)
        Monitor->>Monitor: Confirm failure (3 checks)
        Monitor->>DR: Activate DR region
        DR->>DR: Promote replicas to primary
        DR->>DR: Start all services
        Monitor->>DNS: Update to DR IP
        DNS-->>Client: DR IP
        Client->>DR: Requests (60s failover)
        
        Note over Monitor,DR: Send alerts<br/>to on-call team
    end
    
    alt Recovery
        Primary->>Monitor: Restored
        Monitor->>Monitor: Verify stability (10 min)
        Monitor->>Primary: Sync data from DR
        Primary->>Primary: Catch up replication
        Monitor->>DNS: Failback to Primary
        DNS-->>Client: Primary IP
        Client->>Primary: Requests
        Monitor->>DR: Return to standby
    end
```

---

## 14. Security Architecture Layers

```mermaid
graph TB
    INTERNET[Internet Traffic] --> WAF[WAF + DDoS<br/>Protection]
    
    WAF --> TLS[TLS 1.3<br/>Termination]
    
    TLS --> LB[Load Balancer<br/>with SSL]
    
    LB --> AUTH[OAuth 2.0 + JWT<br/>Authentication]
    
    AUTH --> RBAC[RBAC Authorization<br/>Least Privilege]
    
    RBAC --> SERVICES[Application Services<br/>Input Validation]
    
    SERVICES --> ENCRYPT[Field-Level<br/>Encryption]
    
    ENCRYPT --> DB[(Database<br/>AES-256 at Rest)]
    
    DB --> AUDIT[Audit Logger<br/>ECDSA Signatures]
    
    AUDIT --> IMMUTABLE[(Immutable Storage<br/>10-year Retention)]
    
    style WAF fill:#FF6B6B
    style AUTH fill:#FFA07A
    style RBAC fill:#FFD700
    style ENCRYPT fill:#90EE90
    style IMMUTABLE fill:#87CEEB
```

---

## 15. Monitoring & Observability

```mermaid
graph TB
    subgraph "Application Layer"
        APP1[Transaction Monitor]
        APP2[Document Analyzer]
        APP3[Risk Scorer]
        APP4[Report Generator]
    end
    
    subgraph "Collection Layer"
        LOGFIRE[Logfire Agent<br/>Traces + Logs]
        PROM[Prometheus<br/>Metrics]
        SENTRY[Sentry<br/>Errors]
    end
    
    subgraph "Storage Layer"
        LOGFIRE_DB[(Logfire Backend)]
        PROM_DB[(Prometheus TSDB)]
        SENTRY_DB[(Sentry Backend)]
    end
    
    subgraph "Visualization"
        GRAFANA[Grafana Dashboards]
        ALERTS[Alert Manager]
    end
    
    APP1 --> LOGFIRE
    APP2 --> LOGFIRE
    APP3 --> LOGFIRE
    APP4 --> LOGFIRE
    
    APP1 --> PROM
    APP2 --> PROM
    APP3 --> PROM
    APP4 --> PROM
    
    APP1 --> SENTRY
    APP2 --> SENTRY
    APP3 --> SENTRY
    APP4 --> SENTRY
    
    LOGFIRE --> LOGFIRE_DB
    PROM --> PROM_DB
    SENTRY --> SENTRY_DB
    
    LOGFIRE_DB --> GRAFANA
    PROM_DB --> GRAFANA
    
    PROM_DB --> ALERTS
    
    ALERTS -->|Email/Slack/PagerDuty| TEAM[On-Call Team]
```

---

**Status:** ✅ Complete - 15 System Diagrams

**Usage:** Render with Mermaid (GitHub, GitLab, VS Code, Notion)

**Technology Versions:** Updated to June 2026 latest
- Golang 1.26.4
- Python 3.13
- PostgreSQL 17.2
- TimescaleDB 2.18
- Redis 7.4
- Kafka 3.8
- Kubernetes 1.32
- Next.js 16
- XGBoost 2.1
- LangChain 0.4
