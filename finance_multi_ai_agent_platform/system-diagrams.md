# Finance Multi-AI-Agent Platform - System Diagrams

**Date:** June 18, 2026  
**Version:** 1.0

---

## 1. Complete System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Portal]
        MOBILE[Mobile App]
        API_CLIENT[API Client]
        ADMIN[Admin Console]
    end
    
    subgraph "API Gateway - Golang"
        GW[API Gateway<br/>Fiber]
        AUTH[Authentication<br/>Clerk]
        RATE[Rate Limiter]
        LOG[Compliance Logger]
    end
    
    subgraph "Agent Layer - Python"
        ROOT[Root Orchestrator<br/>FastAPI + LangChain]
        POLICY[Policy Agent<br/>Risk Scoring]
        CLAIMS[Claims Agent<br/>OCR + Vision]
        FRAUD[Fraud Agent<br/>Real-time Detection]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>RLS)]
        REDIS[(Redis<br/>Cache)]
        VECTOR[(pgvector<br/>Embeddings)]
    end
    
    WEB --> GW
    MOBILE --> GW
    API_CLIENT --> GW
    ADMIN --> GW
    
    GW --> AUTH
    GW --> RATE
    GW --> LOG
    
    GW --> ROOT
    
    ROOT --> POLICY
    ROOT --> CLAIMS
    ROOT --> FRAUD
    
    POLICY --> PG
    CLAIMS --> PG
    FRAUD --> PG
    
    POLICY --> REDIS
    FRAUD --> REDIS
    
    CLAIMS --> VECTOR
```

---

## 2. Sequential Workflow Pattern

```mermaid
sequenceDiagram
    participant User
    participant Gateway
    participant Root
    participant Policy
    participant Claims
    participant Fraud
    participant DB
    
    User->>Gateway: Submit insurance claim
    Gateway->>Gateway: Authenticate & log
    Gateway->>Root: Process claim request
    
    Root->>Policy: Step 1: Verify policy
    Policy->>DB: Check policy status
    DB-->>Policy: Policy active
    Policy-->>Root: Policy valid
    
    Root->>Claims: Step 2: Process claim
    Claims->>Claims: OCR documents
    Claims->>Claims: Assess damage
    Claims->>DB: Calculate settlement
    DB-->>Claims: Coverage info
    Claims-->>Root: Claim approved: $5000
    
    Root->>Fraud: Step 3: Fraud check
    Fraud->>DB: Get historical data
    DB-->>Fraud: Transaction history
    Fraud->>Fraud: Run ML model
    Fraud-->>Root: Low risk (0.15)
    
    Root->>Root: Aggregate results
    Root-->>Gateway: Final decision
    Gateway-->>User: Claim approved: $5000
```

---

## 3. Parallel Workflow Pattern

```mermaid
sequenceDiagram
    participant User
    participant Root
    participant Policy
    participant Claims
    participant Fraud
    
    User->>Root: Loan application
    
    par All Agents Execute
        Root->>Policy: Check creditworthiness
        and
        Root->>Claims: Verify documents
        and
        Root->>Fraud: Identity verification
    end
    
    Policy-->>Root: Credit score: 720
    Claims-->>Root: Documents verified
    Fraud-->>Root: Identity confirmed
    
    Root->>Root: Aggregate results
    Root-->>User: Loan approved
```

---

## 4. Peer-to-Peer Collaboration

```mermaid
graph TD
    USER[Complex Fraud Case]
    
    ROOT[Root Orchestrator]
    
    POLICY[Policy Agent]
    CLAIMS[Claims Agent]
    FRAUD[Fraud Agent]
    
    USER --> ROOT
    ROOT --> POLICY
    ROOT --> CLAIMS
    ROOT --> FRAUD
    
    POLICY <-->|Share findings| CLAIMS
    CLAIMS <-->|Share findings| FRAUD
    FRAUD <-->|Share findings| POLICY
    
    POLICY -->|Consensus| ROOT
    CLAIMS -->|Consensus| ROOT
    FRAUD -->|Consensus| ROOT
    
    ROOT --> DECISION[Final Decision]
```

---

## 5. Policy Agent Flow

```mermaid
flowchart TD
    START([Underwriting Request]) --> EXTRACT[Extract Features<br/>Age, Income, History]
    
    EXTRACT --> RISK[ML Risk Scoring Model]
    
    RISK --> SCORE{Risk Score}
    
    SCORE -->|0-40| LOW[Low Risk<br/>Standard Premium]
    SCORE -->|41-60| MEDIUM[Medium Risk<br/>Higher Premium]
    SCORE -->|61-80| HIGH[High Risk<br/>Conditions Required]
    SCORE -->|81-100| CRITICAL[Critical Risk<br/>Decline]
    
    LOW --> CALC[Calculate Premium]
    MEDIUM --> CALC
    HIGH --> CALC
    
    CALC --> APPROVE[Approve Policy]
    CRITICAL --> DECLINE[Decline Application]
    
    APPROVE --> END([Policy Issued])
    DECLINE --> END
```

---

## 6. Claims Agent Flow

```mermaid
flowchart TD
    START([Claim Submitted]) --> DOCS[Process Documents<br/>OCR + AI]
    
    DOCS --> VERIFY{Documents<br/>Valid?}
    
    VERIFY -->|No| REJECT1[Reject: Invalid Documents]
    VERIFY -->|Yes| DAMAGE[Assess Damage<br/>Computer Vision]
    
    DAMAGE --> ESTIMATE[Estimate Repair Cost]
    
    ESTIMATE --> COVERAGE{Within<br/>Coverage?}
    
    COVERAGE -->|No| REJECT2[Reject: Exceeds Coverage]
    COVERAGE -->|Yes| FRAUD_CHECK[Fraud Check]
    
    FRAUD_CHECK --> FRAUD_RISK{Fraud<br/>Risk?}
    
    FRAUD_RISK -->|High| MANUAL[Flag for Manual Review]
    FRAUD_RISK -->|Low| APPROVE[Approve Claim]
    
    APPROVE --> SETTLE[Calculate Settlement]
    SETTLE --> END([Payment Initiated])
    
    REJECT1 --> END
    REJECT2 --> END
    MANUAL --> END
```

---

## 7. Fraud Agent Real-Time Detection

```mermaid
flowchart TD
    START([Transaction Initiated]) --> PARALLEL{Parallel Checks}
    
    PARALLEL --> VELOCITY[Velocity Check<br/>Unusual frequency?]
    PARALLEL --> AMOUNT[Amount Check<br/>10x higher than usual?]
    PARALLEL --> LOCATION[Location Check<br/>Unusual location?]
    PARALLEL --> DEVICE[Device Check<br/>New device?]
    PARALLEL --> NETWORK[Network Analysis<br/>Fraud ring?]
    
    VELOCITY --> SCORE[Calculate Fraud Score]
    AMOUNT --> SCORE
    LOCATION --> SCORE
    DEVICE --> SCORE
    NETWORK --> SCORE
    
    SCORE --> ML[ML Model Inference]
    
    ML --> PROB{Fraud<br/>Probability?}
    
    PROB -->|< 0.5| ALLOW[Allow Transaction<br/>Low Risk]
    PROB -->|0.5-0.7| FLAG[Flag for Review<br/>Medium Risk]
    PROB -->|0.7-0.9| AUTH[Require Additional Auth<br/>High Risk]
    PROB -->|> 0.9| BLOCK[Block Transaction<br/>Critical Risk]
    
    ALLOW --> LOG[Log to Database]
    FLAG --> LOG
    AUTH --> LOG
    BLOCK --> LOG
    
    LOG --> END([Complete])
```

---

## 8. Multi-Tenant Data Isolation

```mermaid
graph TB
    subgraph "Tenant A"
        A_REQ[Request with Token A]
        A_DATA[Data: org_id = A]
    end
    
    subgraph "Tenant B"
        B_REQ[Request with Token B]
        B_DATA[Data: org_id = B]
    end
    
    subgraph "Shared Infrastructure"
        GW[API Gateway]
        DB[(PostgreSQL with RLS)]
    end
    
    A_REQ -->|Set context: org_id=A| GW
    B_REQ -->|Set context: org_id=B| GW
    
    GW -->|Query with context A| DB
    GW -->|Query with context B| DB
    
    DB -->|RLS filters: org_id=A| A_DATA
    DB -->|RLS filters: org_id=B| B_DATA
    
    A_DATA -->|Only Tenant A data| A_REQ
    B_DATA -->|Only Tenant B data| B_REQ
```

---

## 9. Compliance Architecture

```mermaid
graph TD
    subgraph "Compliance Layer"
        GDPR[GDPR Module<br/>Data Privacy]
        SOX[SOX Module<br/>Financial Controls]
        PCI[PCI-DSS Module<br/>Payment Security]
        AML[AML Module<br/>Money Laundering]
    end
    
    subgraph "Enforcement Points"
        API[API Gateway]
        AGENTS[Agent Layer]
        DB[Database]
    end
    
    subgraph "Audit & Reporting"
        LOGS[Audit Logs<br/>Immutable]
        REPORTS[Compliance Reports<br/>Automated]
        ALERTS[Violation Alerts]
    end
    
    GDPR --> API
    SOX --> API
    PCI --> API
    AML --> AGENTS
    
    API --> LOGS
    AGENTS --> LOGS
    DB --> LOGS
    
    LOGS --> REPORTS
    LOGS --> ALERTS
```

---

## 10. Fraud Detection Network Analysis

```mermaid
graph TB
    subgraph "Known Fraud Network"
        F1[Fraudster 1]
        F2[Fraudster 2]
        F3[Fraudster 3]
    end
    
    subgraph "Suspicious Connections"
        U1[User A]
        U2[User B]
    end
    
    subgraph "Legitimate Users"
        L1[User X]
        L2[User Y]
    end
    
    F1 <-->|Same IP| F2
    F2 <-->|Same device| F3
    F1 <-->|Same card| F3
    
    U1 <-->|Same IP| F1
    U2 <-->|Transfers to| F2
    
    U1 -.Flag as suspicious.-> ALERT[Fraud Alert]
    U2 -.Flag as suspicious.-> ALERT
    
    L1 --> NORMAL[Normal Activity]
    L2 --> NORMAL
```

---

## 11. Data Architecture

```mermaid
graph TB
    subgraph "Operational Data"
        PG[(PostgreSQL<br/>Policies, Claims, Fraud)]
        REDIS[(Redis<br/>Cache)]
    end
    
    subgraph "ML Data"
        VECTOR[(pgvector<br/>Document Embeddings)]
        TRAIN[(Training Data<br/>Historical)]
    end
    
    subgraph "Compliance Data"
        AUDIT[(Audit Logs<br/>Immutable)]
        ARCHIVE[(Archived Data<br/>7 year retention)]
    end
    
    subgraph "Analytics"
        BI[Business Intelligence<br/>Dashboards]
        ML_PIPELINE[ML Training Pipeline]
    end
    
    PG --> REDIS
    PG --> VECTOR
    PG --> AUDIT
    
    AUDIT --> ARCHIVE
    
    PG --> BI
    TRAIN --> ML_PIPELINE
    ML_PIPELINE --> VECTOR
```

---

## 12. Deployment Architecture

```mermaid
graph TB
    subgraph "Production - Multi-Region"
        subgraph "US-East"
            K8S_E[Kubernetes<br/>3 nodes]
            DB_E[(PostgreSQL<br/>Primary)]
        end
        
        subgraph "EU-West"
            K8S_W[Kubernetes<br/>3 nodes]
            DB_W[(PostgreSQL<br/>Read Replica)]
        end
    end
    
    subgraph "Services"
        GW1[API Gateway × 3]
        AGENT1[Agent Runtime × 5]
        REDIS_C[(Redis Cluster)]
    end
    
    LB[Load Balancer]
    
    LB --> K8S_E
    LB --> K8S_W
    
    K8S_E --> GW1
    K8S_E --> AGENT1
    K8S_W --> GW1
    K8S_W --> AGENT1
    
    AGENT1 --> DB_E
    AGENT1 --> DB_W
    AGENT1 --> REDIS_C
    
    DB_E -.Replication.-> DB_W
```

---

**Status:** ✅ Complete - 12 System Diagrams

**Usage:** Render with Mermaid (GitHub, GitLab, VS Code)
