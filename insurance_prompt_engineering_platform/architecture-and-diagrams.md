# Zero-shot vs Few-shot Prompting Platform - Architecture & System Diagrams

**Date:** June 18, 2026  
**Version:** 1.0

---

## 1. Complete System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              USER INTERFACE LAYER                            │
│  Experiment Dashboard | Query Tester | Analytics Dashboard  │
│  Next.js 16 + React 19.2.7 + Chart.js                       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                    HTTPS/REST
                         │
┌────────────────────────▼─────────────────────────────────────┐
│       API GATEWAY (Golang + Fiber)                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Request Router                                    │     │
│  │  • Experiment routing                              │     │
│  │  • A/B test traffic split                         │     │
│  │  • Response collection                             │     │
│  └────────────────────┬───────────────────────────────┘     │
└────────────────────────┼─────────────────────────────────────┘
                         │
                       gRPC
                         │
┌────────────────────────▼─────────────────────────────────────┐
│      PROMPT ENGINE (Python + FastAPI)                        │
│  ┌────────────────────────────────────────────────────┐     │
│  │         Strategy Router                            │     │
│  │  ┌──────────────┐  ┌──────────────┐              │     │
│  │  │  Zero-shot   │  │  Few-shot    │              │     │
│  │  │  Handler     │  │  Handler     │              │     │
│  │  └──────────────┘  └──────────────┘              │     │
│  └──────────────────┬─────────────────────────────────┘     │
│                     │                                        │
│  ┌──────────────────▼─────────────────────────────────┐     │
│  │      Example Retrieval System                      │     │
│  │  • Vector similarity (pgvector)                    │     │
│  │  • Category filtering                              │     │
│  │  • Dynamic few-shot builder                        │     │
│  └──────────────────┬─────────────────────────────────┘     │
│                     │                                        │
│  ┌──────────────────▼─────────────────────────────────┐     │
│  │      AI Model Interface                            │     │
│  │  • GPT-5.5 API (OpenAI)                           │     │
│  │  • Claude Opus 4.8 (Anthropic)                    │     │
│  └──────────────────┬─────────────────────────────────┘     │
│                     │                                        │
│  ┌──────────────────▼─────────────────────────────────┐     │
│  │      Evaluation Engine                             │     │
│  │  • Automated scoring (AI-as-judge)                 │     │
│  │  • Metric calculation                              │     │
│  │  • Human evaluation queue                          │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│              DATA LAYER                                      │
│  ┌──────────────┐  ┌────────────┐  ┌────────────┐          │
│  │ PostgreSQL   │  │  pgvector  │  │   Redis    │          │
│  │ Experiments  │  │  Examples  │  │   Cache    │          │
│  └──────────────┘  └────────────┘  └────────────┘          │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Prompt Strategy Comparison Flow

```mermaid
sequenceDiagram
    participant User
    participant Gateway
    participant Router
    participant ZeroShot
    participant FewShot
    participant AI
    participant Evaluator
    participant DB
    
    User->>Gateway: Submit insurance query
    Gateway->>Router: Route to experiment
    
    par Parallel Strategy Execution
        Router->>ZeroShot: Execute zero-shot
        ZeroShot->>AI: Prompt without examples
        AI-->>ZeroShot: Response A
        
        and
        
        Router->>FewShot: Execute few-shot
        FewShot->>DB: Retrieve similar examples
        DB-->>FewShot: 5 examples
        FewShot->>AI: Prompt with examples
        AI-->>FewShot: Response B
    end
    
    ZeroShot->>Evaluator: Evaluate Response A
    FewShot->>Evaluator: Evaluate Response B
    
    Evaluator->>AI: Score both responses
    AI-->>Evaluator: Scores
    
    Evaluator->>DB: Store results
    Evaluator-->>Gateway: Both responses + scores
    Gateway-->>User: Display comparison
```

---

## 3. Zero-shot Prompting Architecture

```
┌──────────────────────────────────────────┐
│      Zero-shot Strategy                  │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────┐     │
│  │  System Prompt Builder         │     │
│  │  • Category-specific context   │     │
│  │  • Role definition             │     │
│  │  • Output format instructions  │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  User Query                    │     │
│  │  "Does my insurance cover X?"  │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  AI Model (GPT-5.5)            │     │
│  │  Temperature: 0.3              │     │
│  │  Max tokens: 500               │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Response                      │     │
│  │  • Answer text                 │     │
│  │  • Token count: ~150           │     │
│  │  • Latency: ~800ms             │     │
│  └────────────────────────────────┘     │
└──────────────────────────────────────────┘
```

---

## 4. Few-shot Prompting Architecture

```
┌──────────────────────────────────────────┐
│      Few-shot Strategy                   │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────┐     │
│  │  Query Embedding               │     │
│  │  sentence-transformers         │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Vector Search (pgvector)      │     │
│  │  • Find 5 similar examples     │     │
│  │  • Category filter: 'policy'   │     │
│  │  • Min similarity: 0.7         │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Prompt Construction           │     │
│  │  • System prompt               │     │
│  │  • 5 example Q&A pairs         │     │
│  │  • User query                  │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  AI Model (GPT-5.5)            │     │
│  │  Temperature: 0.3              │     │
│  │  Max tokens: 500               │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Response                      │     │
│  │  • Answer text                 │     │
│  │  • Token count: ~650           │     │
│  │  • Latency: ~1400ms            │     │
│  └────────────────────────────────┘     │
└──────────────────────────────────────────┘
```

---

## 5. Example Retrieval Flow

```mermaid
flowchart TD
    START([User Query]) --> EMBED[Generate Query Embedding<br/>sentence-transformers]
    
    EMBED --> VECTOR[Vector Similarity Search<br/>pgvector]
    
    VECTOR --> FILTER{Filter by<br/>Category?}
    
    FILTER -->|Yes| CATEGORY[Apply Category Filter<br/>e.g., 'claims']
    FILTER -->|No| RANK
    
    CATEGORY --> RANK[Rank by Similarity<br/>Cosine distance]
    
    RANK --> TOP[Select Top N Examples<br/>N = 3, 5, or 10]
    
    TOP --> VERIFY{Only<br/>Verified?}
    
    VERIFY -->|Yes| VERIFIED[Filter verified=true]
    VERIFY -->|No| FORMAT
    
    VERIFIED --> FORMAT[Format Examples<br/>Q&A pairs]
    
    FORMAT --> END([Return Examples])
```

---

## 6. A/B Testing Experiment Flow

```mermaid
flowchart TD
    CREATE[Create Experiment] --> CONFIG[Configure]
    
    CONFIG --> STRATEGIES[Define Strategies<br/>zero_shot vs few_shot_5]
    
    STRATEGIES --> QUERIES[Add Test Queries<br/>20-100 queries]
    
    QUERIES --> LAUNCH[Launch Experiment]
    
    LAUNCH --> SPLIT{Traffic Split}
    
    SPLIT -->|50%| ZERO[Zero-shot Path]
    SPLIT -->|50%| FEW[Few-shot Path]
    
    ZERO --> EVAL_A[Automated Evaluation]
    FEW --> EVAL_B[Automated Evaluation]
    
    EVAL_A --> HUMAN_A{Human Review<br/>Needed?}
    EVAL_B --> HUMAN_B{Human Review<br/>Needed?}
    
    HUMAN_A -->|Yes| QUEUE_A[Add to Review Queue]
    HUMAN_A -->|No| METRICS
    
    HUMAN_B -->|Yes| QUEUE_B[Add to Review Queue]
    HUMAN_B -->|No| METRICS
    
    QUEUE_A --> METRICS[Calculate Metrics]
    QUEUE_B --> METRICS
    
    METRICS --> COMPARE[Compare Strategies]
    
    COMPARE --> WINNER[Determine Winner<br/>Based on accuracy + cost]
    
    WINNER --> REPORT[Generate Report]
    
    REPORT --> END([Experiment Complete])
```

---

## 7. Evaluation Pipeline

```
┌──────────────────────────────────────────┐
│      Evaluation Pipeline                 │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────┐     │
│  │  Response Collection           │     │
│  │  • Query text                  │     │
│  │  • Response text               │     │
│  │  • Strategy used               │     │
│  │  • Token count                 │     │
│  │  • Latency                     │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Automated Evaluation          │     │
│  │  AI-as-Judge (GPT-5.5)         │     │
│  │  ┌──────────────────────┐      │     │
│  │  │ Accuracy: 0.85       │      │     │
│  │  │ Relevance: 0.92      │      │     │
│  │  │ Completeness: 0.88   │      │     │
│  │  │ Tone: 0.90           │      │     │
│  │  └──────────────────────┘      │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Confidence Check              │     │
│  │  If automated score < 0.7:     │     │
│  │  → Flag for human review       │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Human Evaluation (Optional)   │     │
│  │  • Expert insurance adjusters  │     │
│  │  • Side-by-side comparison     │     │
│  │  • Final scores override       │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Aggregate Metrics             │     │
│  │  • Strategy performance        │     │
│  │  • Cost analysis               │     │
│  │  • Latency benchmarks          │     │
│  └────────────────────────────────┘     │
└──────────────────────────────────────────┘
```

---

## 8. Data Architecture

```mermaid
graph TB
    subgraph "Operational Data"
        EXP[(Experiments<br/>PostgreSQL)]
        QUERIES[(Test Queries<br/>PostgreSQL)]
        RESP[(Responses<br/>PostgreSQL)]
    end
    
    subgraph "Example Library"
        EXAMPLES[(Insurance Examples<br/>PostgreSQL)]
        VECTORS[(Embeddings<br/>pgvector)]
    end
    
    subgraph "Evaluation Data"
        AUTO_EVAL[(Automated Scores<br/>PostgreSQL)]
        HUMAN_EVAL[(Human Scores<br/>PostgreSQL)]
    end
    
    subgraph "Cache Layer"
        REDIS[(Redis<br/>Response Cache)]
    end
    
    subgraph "Analytics"
        METRICS[(Aggregated Metrics<br/>PostgreSQL)]
        REPORTS[Report Generator]
    end
    
    EXP --> QUERIES
    QUERIES --> RESP
    RESP --> AUTO_EVAL
    AUTO_EVAL --> HUMAN_EVAL
    
    EXAMPLES --> VECTORS
    VECTORS --> RESP
    
    RESP --> REDIS
    
    AUTO_EVAL --> METRICS
    HUMAN_EVAL --> METRICS
    METRICS --> REPORTS
```

---

## 9. Insurance Query Categories

```mermaid
mindmap
  root((Insurance Queries))
    Policy Coverage
      What's covered
      Exclusions
      Limits
      Deductibles
    Claims Processing
      How to file
      Documentation
      Timelines
      Status tracking
    Underwriting
      Eligibility
      Risk factors
      Pricing
      Application process
    Customer Support
      Policy changes
      Billing questions
      Contact info
      General inquiries
```

---

## 10. Performance Metrics Dashboard

```mermaid
graph LR
    subgraph "Accuracy Metrics"
        ACC[Accuracy Score<br/>0.0 - 1.0]
        REL[Relevance Score<br/>0.0 - 1.0]
        COMP[Completeness<br/>0.0 - 1.0]
    end
    
    subgraph "Cost Metrics"
        TOK[Token Usage<br/>per query]
        COST[Cost per Query<br/>USD]
    end
    
    subgraph "Performance Metrics"
        LAT[Latency<br/>milliseconds]
        THROUGH[Throughput<br/>queries/sec]
    end
    
    subgraph "Comparison"
        WINNER[Strategy Winner<br/>Weighted Score]
    end
    
    ACC --> WINNER
    REL --> WINNER
    COMP --> WINNER
    TOK --> WINNER
    COST --> WINNER
    LAT --> WINNER
    
    WINNER --> DECISION{Deploy?}
```

---

## 11. Example Library Growth

```mermaid
flowchart TD
    START[Example Sources] --> MANUAL[Manual Curation<br/>Insurance experts]
    START --> EXTRACT[Extract from Claims<br/>Historical data]
    START --> SYNTHETIC[AI-Generated<br/>Synthetic examples]
    
    MANUAL --> VERIFY[Human Verification]
    EXTRACT --> VERIFY
    SYNTHETIC --> VERIFY
    
    VERIFY --> EMBED[Generate Embeddings]
    
    EMBED --> STORE[(Example Database)]
    
    STORE --> USE[Use in Few-shot Prompts]
    
    USE --> FEEDBACK[Collect Performance Data]
    
    FEEDBACK --> UPDATE{Update<br/>Example?}
    
    UPDATE -->|Low performance| REMOVE[Mark for review/removal]
    UPDATE -->|High performance| PROMOTE[Mark as verified]
    
    PROMOTE --> STORE
    REMOVE --> REVIEW[Human Review]
    REVIEW --> STORE
```

---

## 12. Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Production Cluster              │
├─────────────────────────────────────────┤
│                                         │
│  Namespace: prompt-engineering          │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  API Gateway                   │    │
│  │  • 3-5 pods (CPU autoscale)    │    │
│  │  • 2 CPU, 4GB RAM per pod      │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  Prompt Engine                 │    │
│  │  • 5-10 pods (queue autoscale) │    │
│  │  • 4 CPU, 8GB RAM per pod      │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  Evaluation Service            │    │
│  │  • 2-5 pods (queue autoscale)  │    │
│  │  • 2 CPU, 4GB RAM per pod      │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Data Services                   │
├─────────────────────────────────────────┤
│                                         │
│  PostgreSQL + pgvector:                 │
│  • Primary (r6g.xlarge)                 │
│  • Read Replica (r6g.large)             │
│                                         │
│  Redis:                                 │
│  • 2-node cluster (cache.r6g.large)    │
│                                         │
│  External APIs:                         │
│  • OpenAI GPT-5.5                       │
│  • Anthropic Claude Opus 4.8           │
└─────────────────────────────────────────┘
```

---

**Status:** ✅ Complete - Architecture & 12 System Diagrams

**Version:** 1.0  
**Date:** June 18, 2026

**Usage:** Render with Mermaid (GitHub, GitLab, VS Code)
