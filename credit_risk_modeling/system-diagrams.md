# AI-Powered Credit Risk Modeling Platform - System Diagrams

**Date:** June 23, 2026  
**Version:** 1.0

---

## 1. Complete System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Dashboard<br/>Next.js 16]
        MOBILE[Mobile Apps<br/>iOS/Android]
        API_CLIENT[API Clients<br/>3rd Party]
    end
    
    subgraph "API Gateway - Golang/Fiber"
        GW[API Gateway]
        AUTH[PASETO Auth]
        RATE[Rate Limiter<br/>Per-Tenant]
        CACHE[Response Cache<br/>Redis]
    end
    
    subgraph "Business Services"
        SCORING[Credit Scoring<br/>Engine<br/>Python/FastAPI]
        PORTFOLIO[Portfolio Monitor<br/>Golang]
        TRAINING[Model Training<br/>Python]
    end
    
    subgraph "Data Integration"
        BUREAUS[Credit Bureaus<br/>Equifax/Experian/TransUnion]
        ALT_DATA[Alternative Data<br/>Plaid/Utility/Rent]
        BANK[Bank APIs<br/>Transactions]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>RLS Enabled)]
        TS[(TimescaleDB<br/>Time-Series)]
        REDIS[(Redis<br/>Cache/Sessions)]
        S3[(S3/GCS<br/>Models/Reports)]
    end
    
    WEB --> GW
    MOBILE --> GW
    API_CLIENT --> GW
    
    GW --> AUTH
    GW --> RATE
    GW --> CACHE
    
    GW --> SCORING
    GW --> PORTFOLIO
    GW --> TRAINING
    
    SCORING --> BUREAUS
    SCORING --> ALT_DATA
    SCORING --> BANK
    
    SCORING --> PG
    PORTFOLIO --> PG
    TRAINING --> PG
    
    PORTFOLIO --> TS
    
    SCORING --> REDIS
    PORTFOLIO --> REDIS
    
    TRAINING --> S3
```

---

## 2. Credit Assessment Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant Gateway
    participant Cache
    participant Scoring
    participant DataPipeline
    participant Explainer
    participant DB
    
    Client->>Gateway: POST /api/v1/assessments
    Gateway->>Gateway: Validate PASETO token
    Gateway->>Gateway: Check rate limit
    Gateway->>Cache: Check cache
    
    alt Cache Hit
        Cache-->>Gateway: Cached result
        Gateway-->>Client: Return result (< 50ms)
    else Cache Miss
        Gateway->>Scoring: Score applicant
        
        par Parallel Data Fetch
            Scoring->>DataPipeline: Fetch bureau data
            and
            Scoring->>DataPipeline: Fetch alt data
            and
            Scoring->>DataPipeline: Fetch bank data
        end
        
        DataPipeline-->>Scoring: Merged data
        
        Scoring->>Scoring: Feature engineering
        
        par Parallel Model Prediction
            Scoring->>Scoring: XGBoost predict
            and
            Scoring->>Scoring: LightGBM predict
            and
            Scoring->>Scoring: Neural Net predict
        end
        
        Scoring->>Scoring: Ensemble combination
        Scoring->>Explainer: Generate explanation
        Explainer-->>Scoring: SHAP + GPT explanation
        
        Scoring->>DB: Store assessment
        Scoring->>Cache: Cache result (5min TTL)
        Scoring-->>Gateway: Risk score + explanation
        Gateway-->>Client: Return result (< 1000ms)
    end
```

---

## 3. Model Ensemble Architecture

```mermaid
flowchart TD
    INPUT[Applicant Features<br/>150+ features] --> PREPROCESS[Feature Preprocessing<br/>Normalization]
    
    PREPROCESS --> SPLIT{Parallel Prediction}
    
    SPLIT --> XGB[XGBoost Model<br/>Weight: 0.40]
    SPLIT --> LGB[LightGBM Model<br/>Weight: 0.30]
    SPLIT --> NN[Neural Network<br/>Weight: 0.20]
    SPLIT --> LR[Logistic Regression<br/>Weight: 0.10]
    
    XGB --> COMBINE[Weighted Ensemble<br/>Combination]
    LGB --> COMBINE
    NN --> COMBINE
    LR --> COMBINE
    
    COMBINE --> SCORE[Risk Score<br/>0-1000]
    SCORE --> CONFIDENCE{Confidence<br/>> 0.7?}
    
    CONFIDENCE -->|Yes| OUTPUT[Final Risk Score]
    CONFIDENCE -->|No| FALLBACK[Use Logistic Fallback]
    FALLBACK --> OUTPUT
    
    OUTPUT --> SHAP[SHAP Explainability]
    SHAP --> GPT[GPT-5.5 NL Explanation]
    GPT --> RESULT[Risk Assessment<br/>+ Explanation]
```

---

## 4. Data Integration Pipeline

```mermaid
flowchart LR
    START([Applicant SSN]) --> TRIGGER{Parallel Fetch}
    
    TRIGGER --> EQ[Equifax API<br/>Timeout: 5s]
    TRIGGER --> EX[Experian API<br/>Timeout: 5s]
    TRIGGER --> TU[TransUnion API<br/>Timeout: 5s]
    
    EQ --> NORM[Normalize Bureau Data]
    EX --> NORM
    TU --> NORM
    
    NORM --> ALT{Fetch Alt Data}
    
    ALT --> PLAID[Plaid<br/>Bank Transactions]
    ALT --> BOOST[Experian Boost<br/>Utility Payments]
    ALT --> RENT[RentTrack<br/>Rental History]
    
    PLAID --> MERGE[Merge All Sources]
    BOOST --> MERGE
    RENT --> MERGE
    
    MERGE --> VALIDATE{Data Quality<br/>Check}
    
    VALIDATE -->|Pass| ENRICH[Feature Engineering<br/>150+ features]
    VALIDATE -->|Fail| ERROR[Insufficient Data<br/>Error]
    
    ENRICH --> OUTPUT([Credit Data<br/>Ready for Scoring])
```

---

## 5. Multi-Tenant Data Isolation

```mermaid
graph TB
    subgraph "Tenant A - Big Bank"
        A_USER[User A1]
        A_DATA[Data: 10K assessments]
    end
    
    subgraph "Tenant B - Fintech"
        B_USER[User B1]
        B_DATA[Data: 2K assessments]
    end
    
    subgraph "Tenant C - Credit Union"
        C_USER[User C1]
        C_DATA[Data: 500 assessments]
    end
    
    subgraph "Shared Platform"
        GW[API Gateway]
        AUTH[Token Validator]
        DB[(PostgreSQL<br/>Row-Level Security)]
    end
    
    A_USER -->|Token: tenant_id=A| GW
    B_USER -->|Token: tenant_id=B| GW
    C_USER -->|Token: tenant_id=C| GW
    
    GW --> AUTH
    
    AUTH -->|SET tenant_id=A| DB
    AUTH -->|SET tenant_id=B| DB
    AUTH -->|SET tenant_id=C| DB
    
    DB -->|RLS Filter: A| A_DATA
    DB -->|RLS Filter: B| B_DATA
    DB -->|RLS Filter: C| C_DATA
    
    A_DATA -->|Only A's data| A_USER
    B_DATA -->|Only B's data| B_USER
    C_DATA -->|Only C's data| C_USER
```

---

## 6. Portfolio Risk Monitoring Flow

```mermaid
sequenceDiagram
    participant Scheduler
    participant PortfolioMonitor
    participant DB
    participant TimescaleDB
    participant AlertService
    
    Scheduler->>PortfolioMonitor: Trigger (every 15 min)
    
    loop For Each Tenant
        PortfolioMonitor->>DB: Fetch active loans
        DB-->>PortfolioMonitor: Loan data
        
        PortfolioMonitor->>PortfolioMonitor: Calculate metrics
        PortfolioMonitor->>PortfolioMonitor: Detect concentration
        
        PortfolioMonitor->>TimescaleDB: Store time-series
        
        alt Risk Threshold Exceeded
            PortfolioMonitor->>AlertService: Send alert
            AlertService-->>PortfolioMonitor: Alert sent
        end
    end
    
    PortfolioMonitor-->>Scheduler: Complete
```

---

## 7. Model Training & Deployment Pipeline

```mermaid
flowchart TD
    START([Training Triggered]) --> LOAD[Load Historical Data<br/>Min 100K records]
    
    LOAD --> SPLIT[Train/Val/Test Split<br/>70/15/15]
    
    SPLIT --> TRAIN[Train Model<br/>XGBoost/LightGBM/NN]
    
    TRAIN --> VALIDATE[Validate on Val Set<br/>Calculate AUC, Gini]
    
    VALIDATE --> THRESHOLD{AUC > 0.70?}
    
    THRESHOLD -->|No| REJECT[Reject Model<br/>Log failure]
    THRESHOLD -->|Yes| TEST[Test Set Evaluation]
    
    TEST --> VERSION[Version Model<br/>v2.2.0]
    
    VERSION --> CANARY[Deploy Canary<br/>10% traffic]
    
    CANARY --> MONITOR[Monitor 10K requests]
    
    MONITOR --> COMPARE{Better than<br/>Production?}
    
    COMPARE -->|No| ROLLBACK[Rollback]
    COMPARE -->|Yes| DEPLOY[Full Deployment<br/>100% traffic]
    
    DEPLOY --> REGISTRY[Update Model Registry]
    ROLLBACK --> END([Complete])
    REGISTRY --> END
    REJECT --> END
```

---

## 8. Explainability Generation Pipeline

```mermaid
flowchart LR
    START([Risk Score: 720]) --> SHAP[Calculate SHAP Values<br/>TreeExplainer]
    
    SHAP --> FEATURES[Extract Top 10<br/>Feature Importance]
    
    FEATURES --> FILTER[Filter Protected<br/>Attributes<br/>FCRA Compliance]
    
    FILTER --> GPT[GPT-5.5 Generate<br/>Natural Language<br/>Explanation]
    
    GPT --> DECISION{Score < 620?}
    
    DECISION -->|Yes| ADVERSE[Generate Adverse<br/>Action Codes]
    DECISION -->|No| PACKAGE[Package Explanation]
    
    ADVERSE --> PACKAGE
    
    PACKAGE --> OUTPUT([Explanation:<br/>- Summary text<br/>- Top factors<br/>- Adverse codes<br/>- Confidence])
```

---

## 9. Caching Strategy

```mermaid
graph TD
    REQUEST[API Request] --> CACHE_CHECK{Redis Cache?}
    
    CACHE_CHECK -->|Hit| RETURN_CACHE[Return Cached<br/>< 50ms]
    CACHE_CHECK -->|Miss| PROCESS[Process Request]
    
    PROCESS --> BUREAU_CACHE{Bureau Data<br/>Cached?}
    BUREAU_CACHE -->|Yes| USE_BUREAU[Use Cached]
    BUREAU_CACHE -->|No| FETCH_BUREAU[Fetch from APIs]
    
    FETCH_BUREAU --> STORE_BUREAU[Cache 1 hour]
    STORE_BUREAU --> USE_BUREAU
    
    USE_BUREAU --> COMPUTE[Compute Score]
    
    COMPUTE --> STORE_RESULT[Cache Result<br/>5 min TTL]
    
    STORE_RESULT --> RETURN[Return to Client]
    
    RETURN_CACHE --> DONE([Complete])
    RETURN --> DONE
    
    style RETURN_CACHE fill:#90EE90
    style FETCH_BUREAU fill:#FFB6C1
```

---

## 10. Circuit Breaker Pattern

```mermaid
stateDiagram-v2
    [*] --> Closed
    
    Closed --> Open: 5 failures<br/>in 10 requests
    Open --> HalfOpen: 60s timeout
    HalfOpen --> Closed: Success
    HalfOpen --> Open: Failure
    
    Closed: Circuit Closed<br/>✓ Normal Operation<br/>✓ Track failures
    
    Open: Circuit Open<br/>✗ Reject immediately<br/>✓ Return fallback<br/>⏰ Wait 60s
    
    HalfOpen: Circuit Half-Open<br/>⚠ Test with 1 request<br/>⚠ Evaluate success
```

---

## 11. Auto-Scaling Behavior

```mermaid
flowchart TD
    MONITOR[Monitor Metrics] --> CPU{CPU > 80%<br/>OR<br/>Memory > 85%}
    
    CPU -->|No| STABLE[Maintain Current<br/>Pod Count]
    CPU -->|Yes| SCALE_UP{At Max<br/>Replicas?}
    
    SCALE_UP -->|No| ADD[Add 1 Pod<br/>Every 15s]
    SCALE_UP -->|Yes| STABLE
    
    ADD --> WAIT[Wait 60s<br/>Stabilization]
    
    WAIT --> RECHECK{Still Above<br/>Threshold?}
    
    RECHECK -->|Yes| SCALE_UP
    RECHECK -->|No| STABLE
    
    STABLE --> LOW{CPU < 50%<br/>AND<br/>Memory < 60%}
    
    LOW -->|Yes| SCALE_DOWN{At Min<br/>Replicas?}
    LOW -->|No| MONITOR
    
    SCALE_DOWN -->|No| REMOVE[Remove 1 Pod<br/>Every 5 min]
    SCALE_DOWN -->|Yes| MONITOR
    
    REMOVE --> MONITOR
```

---

## 12. Database Connection Pooling

```mermaid
graph TB
    subgraph "Application Servers"
        APP1[App Server 1]
        APP2[App Server 2]
        APP3[App Server 3]
    end
    
    subgraph "Connection Pool"
        POOL[asyncpg Pool<br/>Min: 10 Max: 50]
    end
    
    subgraph "PostgreSQL"
        PRIMARY[(Primary<br/>Write)]
        REPLICA1[(Replica 1<br/>Read)]
        REPLICA2[(Replica 2<br/>Read)]
    end
    
    APP1 --> POOL
    APP2 --> POOL
    APP3 --> POOL
    
    POOL -->|Writes| PRIMARY
    POOL -->|Reads| REPLICA1
    POOL -->|Reads| REPLICA2
    
    PRIMARY -->|Replication| REPLICA1
    PRIMARY -->|Replication| REPLICA2
```

---

## 13. Disaster Recovery Architecture

```mermaid
graph TB
    subgraph "Production Region (us-east-1)"
        PROD_APP[App Servers]
        PROD_DB[(Primary DB)]
        PROD_REDIS[(Redis Primary)]
    end
    
    subgraph "DR Region (us-west-2)"
        DR_APP[Standby App]
        DR_DB[(Standby DB)]
        DR_REDIS[(Redis Replica)]
    end
    
    subgraph "Backup Storage"
        S3[(S3 Backups<br/>Daily + PITR)]
    end
    
    PROD_DB -->|Streaming<br/>Replication| DR_DB
    PROD_REDIS -->|Async<br/>Replication| DR_REDIS
    
    PROD_DB -->|Daily Backup| S3
    
    DR_DB -->|Read-Only<br/>Queries| DR_APP
    
    PROD_APP -->|Failover<br/>< 60s| DR_APP
```

---

## 14. Security Architecture Layers

```mermaid
graph TB
    INTERNET[Internet] --> WAF[WAF<br/>DDoS Protection]
    
    WAF --> LB[Load Balancer<br/>TLS 1.3]
    
    LB --> API[API Gateway<br/>PASETO Auth<br/>Rate Limiting]
    
    API --> SERVICE[Business Services<br/>Input Validation<br/>RBAC]
    
    SERVICE --> DB[(Database<br/>RLS + Encryption<br/>AES-256)]
    
    SERVICE --> REDIS[(Redis<br/>Encrypted<br/>Connection)]
    
    DB --> AUDIT[Audit Logs<br/>7-year Retention]
    
    style WAF fill:#FF6B6B
    style API fill:#FFA07A
    style SERVICE fill:#FFD700
    style DB fill:#90EE90
```

---

## 15. Observability & Monitoring Stack

```mermaid
graph TB
    subgraph "Application Layer"
        APP[App Servers<br/>Instrumented]
    end
    
    subgraph "Collection Layer"
        LOGFIRE[Logfire Agent]
        PROMETHEUS[Prometheus]
    end
    
    subgraph "Storage Layer"
        LOGFIRE_DB[(Logfire DB<br/>Traces + Logs)]
        PROM_DB[(Prometheus<br/>Metrics)]
    end
    
    subgraph "Visualization"
        GRAFANA[Grafana<br/>Dashboards]
        ALERTS[Alert Manager]
    end
    
    APP --> LOGFIRE
    APP --> PROMETHEUS
    
    LOGFIRE --> LOGFIRE_DB
    PROMETHEUS --> PROM_DB
    
    LOGFIRE_DB --> GRAFANA
    PROM_DB --> GRAFANA
    
    PROM_DB --> ALERTS
    
    ALERTS -->|Email/Slack| TEAM[Dev Team]
```

---

**Status:** ✅ Complete - 15 System Diagrams

**Usage:** Render with Mermaid (GitHub, GitLab, VS Code, Notion)
