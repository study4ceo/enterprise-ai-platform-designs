# AI-Powered Vehicle Damage Detection and Claim Platform - System Diagrams

**Date:** June 18, 2026  
**Version:** 1.0

---

## 1. Complete System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        MOBILE[Mobile App<br/>iOS/Android]
        WEB[Web Portal<br/>Next.js 16]
    end
    
    subgraph "API Gateway - Golang"
        GW[API Gateway<br/>Fiber]
        AUTH[PASETO Auth]
        RATE[Rate Limiter<br/>1000/min]
        VAL[Image Validator]
    end
    
    subgraph "AI Processing - Python"
        DETECT[Damage Detector<br/>GPT-5.5 + YOLOv8]
        SEVERITY[Severity Assessor<br/>ML Classifier]
        COST[Cost Estimator<br/>Parts DB + Labor]
        CLAIM[Claim Generator<br/>PDF + ACORD XML]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>RLS)]
        REDIS[(Redis<br/>Cache)]
        S3[(AWS S3<br/>Images)]
    end
    
    MOBILE --> GW
    WEB --> GW
    
    GW --> AUTH
    GW --> RATE
    GW --> VAL
    
    GW --> DETECT
    DETECT --> SEVERITY
    SEVERITY --> COST
    COST --> CLAIM
    
    DETECT --> PG
    SEVERITY --> PG
    COST --> PG
    CLAIM --> PG
    
    DETECT --> REDIS
    COST --> REDIS
    
    VAL --> S3
    CLAIM --> S3
```

---

## 2. Image Upload & Validation Flow

```mermaid
sequenceDiagram
    participant User
    participant Mobile
    participant Gateway
    participant Validator
    participant S3
    participant DB
    
    User->>Mobile: Take/select photo
    Mobile->>Mobile: Compress (if needed)
    Mobile->>Gateway: POST /api/v1/upload
    Gateway->>Gateway: Validate token
    Gateway->>Validator: Validate image
    
    Validator->>Validator: Check size (<20MB)
    Validator->>Validator: Check format (JPEG/PNG/WEBP)
    Validator->>Validator: Check resolution (≥800x600)
    Validator->>Validator: Check brightness
    Validator->>Validator: Check sharpness
    Validator->>Validator: Detect vehicle presence
    
    alt Image valid
        Validator-->>Gateway: Valid
        Gateway->>S3: Upload original
        S3-->>Gateway: S3 key
        Gateway->>DB: Save metadata
        Gateway-->>Mobile: Upload success
        Mobile-->>User: Ready for analysis
    else Image invalid
        Validator-->>Gateway: Invalid (reason)
        Gateway-->>Mobile: Error message
        Mobile-->>User: Please retake photo
    end
```

---

## 3. Damage Detection Pipeline

```mermaid
flowchart TD
    START([Image Uploaded]) --> YOLO[YOLOv8 Pre-screening<br/>Fast Detection]
    
    YOLO --> CHECK{Damage<br/>Found?}
    
    CHECK -->|No| NODAMAGE[Return: No Damage Detected]
    CHECK -->|Yes| GPT[GPT-5.5 Vision Analysis<br/>Detailed Classification]
    
    GPT --> CONF{Confidence<br/>> 0.7?}
    
    CONF -->|Yes| RESULT[Return Detection Result]
    CONF -->|No| CLAUDE[Claude Opus 4.8<br/>Second Opinion]
    
    CLAUDE --> ENSEMBLE[Ensemble Both Results]
    ENSEMBLE --> RESULT
    
    RESULT --> END([Damage Report])
    NODAMAGE --> END
```

---

## 4. Parallel Processing Architecture

```mermaid
graph TB
    INPUT[Multiple Images] --> SPLIT{Split}
    
    SPLIT --> IMG1[Image 1]
    SPLIT --> IMG2[Image 2]
    SPLIT --> IMG3[Image 3]
    
    IMG1 --> VAL1[Validate]
    IMG2 --> VAL2[Validate]
    IMG3 --> VAL3[Validate]
    
    VAL1 --> DET1[Detect Damage]
    VAL2 --> DET2[Detect Damage]
    VAL3 --> DET3[Detect Damage]
    
    DET1 --> MERGE{Merge}
    DET2 --> MERGE
    DET3 --> MERGE
    
    MERGE --> ALL_DAMAGES[All Damages]
    
    ALL_DAMAGES --> SPLIT2{Split by Damage}
    
    SPLIT2 --> SEV1[Assess Severity 1]
    SPLIT2 --> SEV2[Assess Severity 2]
    SPLIT2 --> SEV3[Assess Severity 3]
    
    SEV1 --> COST1[Estimate Cost 1]
    SEV2 --> COST2[Estimate Cost 2]
    SEV3 --> COST3[Estimate Cost 3]
    
    COST1 --> FINAL{Aggregate}
    COST2 --> FINAL
    COST3 --> FINAL
    
    FINAL --> REPORT[Generate Report]
```

---

## 5. Cost Estimation Flow

```mermaid
flowchart TD
    START([Damage Detected]) --> PARTS[Parts Database Lookup<br/>Make/Model/Year]
    
    PARTS --> AVAIL{Parts<br/>Available?}
    
    AVAIL -->|Yes| OEM[OEM Parts Price]
    AVAIL -->|No| ALT[Aftermarket Alternative]
    
    OEM --> LABOR[Labor Rate Lookup<br/>By Location]
    ALT --> LABOR
    
    LABOR --> HOURS[Calculate Labor Hours<br/>Based on Severity]
    
    HOURS --> MATERIALS[Materials Cost<br/>Paint, Supplies]
    
    MATERIALS --> REGIONAL[Apply Regional Factor<br/>+/- 20%]
    
    REGIONAL --> RANGE[Calculate Confidence Range<br/>+/- 15%]
    
    RANGE --> ESTIMATE[Final Cost Estimate<br/>Min, Max, Total]
    
    ESTIMATE --> END([Return to User])
```

---

## 6. Multi-Tenant Data Isolation

```mermaid
graph TB
    subgraph "Tenant A - Insurance Co"
        A_USER[User A1]
        A_DATA[Assessments: 1000<br/>Claims: 500<br/>Users: 50]
    end
    
    subgraph "Tenant B - Body Shop"
        B_USER[User B1]
        B_DATA[Assessments: 200<br/>Claims: 100<br/>Users: 10]
    end
    
    subgraph "Shared Platform"
        GW[API Gateway]
        AUTH[PASETO Validator]
        DB[(PostgreSQL + RLS)]
    end
    
    A_USER -->|Token: tenant_id=A| GW
    B_USER -->|Token: tenant_id=B| GW
    
    GW --> AUTH
    AUTH -->|Set context: A| DB
    AUTH -->|Set context: B| DB
    
    DB -->|RLS Filter: tenant_id=A| A_DATA
    DB -->|RLS Filter: tenant_id=B| B_DATA
    
    A_DATA -->|Only A's data| A_USER
    B_DATA -->|Only B's data| B_USER
```

---

## 7. Claim Generation Workflow

```mermaid
sequenceDiagram
    participant User
    participant System
    participant PDF
    participant ACORD
    participant Insurance
    
    User->>System: Request claim generation
    System->>System: Compile damage data
    
    par Generate All Formats
        System->>PDF: Generate PDF report
        and
        System->>ACORD: Generate ACORD XML
    end
    
    PDF-->>System: PDF with annotated images
    ACORD-->>System: ACORD XML document
    
    System->>User: Show preview
    User->>System: Confirm submission
    
    System->>Insurance: Submit ACORD XML
    Insurance-->>System: Claim accepted (ID: 12345)
    
    System->>User: Claim submitted<br/>Reference: 12345
```

---

## 8. Caching Strategy

```mermaid
graph TD
    REQUEST[API Request] --> CHECK_CACHE{Check Redis}
    
    CHECK_CACHE -->|Hit| RETURN_CACHE[Return Cached Result]
    CHECK_CACHE -->|Miss| PROCESS[Process Request]
    
    PROCESS --> PARTS_CACHE{Parts Cached?}
    PARTS_CACHE -->|Yes| USE_PARTS[Use Cached Parts]
    PARTS_CACHE -->|No| FETCH_PARTS[Fetch from DB]
    
    FETCH_PARTS --> CACHE_PARTS[Cache for 1 hour]
    CACHE_PARTS --> USE_PARTS
    
    USE_PARTS --> LABOR_CACHE{Labor Rate Cached?}
    LABOR_CACHE -->|Yes| USE_LABOR[Use Cached Rate]
    LABOR_CACHE -->|No| FETCH_LABOR[Fetch from Service]
    
    FETCH_LABOR --> CACHE_LABOR[Cache for 24 hours]
    CACHE_LABOR --> USE_LABOR
    
    USE_LABOR --> COMPUTE[Compute Estimate]
    COMPUTE --> CACHE_RESULT[Cache Result<br/>TTL: 30 min]
    CACHE_RESULT --> RETURN[Return to User]
    
    RETURN_CACHE --> DONE([Complete])
    RETURN --> DONE
```

---

## 9. Error Handling & Circuit Breaker

```mermaid
stateDiagram-v2
    [*] --> Closed: Initial State
    
    Closed --> Open: 5 failures in 10 requests
    Open --> HalfOpen: 60 seconds timeout
    HalfOpen --> Closed: Success
    HalfOpen --> Open: Failure
    
    Closed: Circuit Closed<br/>Normal Operation
    Open: Circuit Open<br/>Fail Fast
    HalfOpen: Circuit Half-Open<br/>Test Recovery
    
    note right of Closed
        Requests pass through
        Track failures
    end note
    
    note right of Open
        Reject immediately
        Return fallback
    end note
    
    note right of HalfOpen
        Allow test request
        Check if recovered
    end note
```

---

## 10. Auto-Scaling Behavior

```mermaid
graph TB
    LOAD[Incoming Load] --> MEASURE[Measure Metrics]
    
    MEASURE --> CPU[CPU Usage]
    MEASURE --> MEMORY[Memory Usage]
    MEASURE --> QUEUE[Queue Depth]
    
    CPU --> CHECK{Threshold<br/>Exceeded?}
    MEMORY --> CHECK
    QUEUE --> CHECK
    
    CHECK -->|No| STABLE[Maintain Current<br/>Pod Count]
    CHECK -->|Yes| DIRECTION{Scale Up<br/>or Down?}
    
    DIRECTION -->|Up| INCREASE[Add Pods<br/>+1 every 30s]
    DIRECTION -->|Down| DECREASE[Remove Pods<br/>-1 every 5min]
    
    INCREASE --> LIMIT_UP{At Max<br/>Replicas?}
    DECREASE --> LIMIT_DOWN{At Min<br/>Replicas?}
    
    LIMIT_UP -->|No| SCALE_UP[Scale Up]
    LIMIT_UP -->|Yes| STABLE
    
    LIMIT_DOWN -->|No| SCALE_DOWN[Scale Down]
    LIMIT_DOWN -->|Yes| STABLE
    
    SCALE_UP --> WAIT[Wait 30s]
    SCALE_DOWN --> WAIT
    WAIT --> MEASURE
    
    STABLE --> MONITOR[Continue Monitoring]
    MONITOR --> MEASURE
```

---

## 11. Deployment Pipeline

```mermaid
flowchart LR
    DEV[Developer] --> COMMIT[Git Commit]
    COMMIT --> CI[CI Pipeline]
    
    CI --> TESTS[Run Tests<br/>85% Coverage]
    TESTS --> LINT[Linting<br/>Type Checks]
    LINT --> BUILD[Build Docker Image]
    
    BUILD --> PUSH[Push to Registry]
    PUSH --> STAGING[Deploy to Staging]
    
    STAGING --> SMOKE[Smoke Tests]
    SMOKE --> APPROVE{Manual<br/>Approval?}
    
    APPROVE -->|Yes| BLUE_GREEN[Blue-Green Deploy]
    APPROVE -->|No| ROLLBACK[Rollback]
    
    BLUE_GREEN --> GREEN[Deploy to Green]
    GREEN --> HEALTH[Health Checks]
    
    HEALTH --> SWITCH{All<br/>Healthy?}
    SWITCH -->|Yes| TRAFFIC[Switch Traffic]
    SWITCH -->|No| ROLLBACK
    
    TRAFFIC --> PROD[Production Live]
    PROD --> MONITOR[Monitor Metrics]
```

---

## 12. Data Architecture

```mermaid
graph TB
    subgraph "Hot Storage (< 30 days)"
        PG[(PostgreSQL<br/>Assessments, Claims)]
        REDIS[(Redis<br/>Cache, Sessions)]
        S3_HOT[(S3 Standard<br/>Recent Images)]
    end
    
    subgraph "Warm Storage (30-90 days)"
        S3_WARM[(S3 Intelligent-Tiering<br/>Older Images)]
        RDS_REPLICA[(RDS Read Replica<br/>Analytics)]
    end
    
    subgraph "Cold Storage (> 90 days)"
        S3_GLACIER[(S3 Glacier<br/>Archive Images)]
        RDS_BACKUP[(RDS Backups<br/>Point-in-Time)]
    end
    
    PG --> S3_HOT
    PG --> REDIS
    
    S3_HOT -->|30 days| S3_WARM
    PG -->|Daily| RDS_REPLICA
    
    S3_WARM -->|90 days| S3_GLACIER
    PG -->|Daily Backup| RDS_BACKUP
```

---

**Status:** ✅ Complete - 12 System Diagrams

**Usage:** Render with Mermaid (GitHub, GitLab, VS Code)
