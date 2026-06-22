# JEE Shortcut Solutions Platform - Architecture & System Diagrams

**Date:** June 18, 2026  
**Version:** 1.0

---

## 1. Complete System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│           STUDENT INTERFACE                                  │
│  Chat Input | Dual-Pane Viewer | Practice Mode | Analytics  │
│  Next.js 16 + React 19.2.7 + KaTeX/MathJax                 │
└────────────────────────┬─────────────────────────────────────┘
                         │
                    HTTPS/REST
                         │
┌────────────────────────▼─────────────────────────────────────┐
│       API GATEWAY (Golang + Fiber)                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Request Router                                    │     │
│  │  • Problem submission                              │     │
│  │  • Solution requests                               │     │
│  │  • Practice sessions                               │     │
│  └────────────────────┬───────────────────────────────┘     │
└────────────────────────┼─────────────────────────────────────┘
                         │
                       gRPC
                         │
┌────────────────────────▼─────────────────────────────────────┐
│      AI SOLUTION ENGINE (Python + FastAPI)                   │
│  ┌────────────────────────────────────────────────────┐     │
│  │         Problem Analyzer                           │     │
│  │  • Subject detection (Physics/Chem/Math)          │     │
│  │  • Topic identification                            │     │
│  │  • Difficulty assessment                           │     │
│  │  • Pattern recognition                             │     │
│  └──────────────────┬─────────────────────────────────┘     │
│                     │                                        │
│  ┌──────────────────▼─────────────────────────────────┐     │
│  │      Traditional Solution Generator                │     │
│  │  • GPT-5.5 for step-by-step                       │     │
│  │  • Claude Opus 4.8 for physics reasoning         │     │
│  │  • SymPy for symbolic math                        │     │
│  └──────────────────┬─────────────────────────────────┘     │
│                     │                                        │
│  ┌──────────────────▼─────────────────────────────────┐     │
│  │      Shortcut Solution Generator                   │     │
│  │  • Pattern matching                                │     │
│  │  • Shortcut database lookup (pgvector)            │     │
│  │  • Time estimation                                 │     │
│  └──────────────────┬─────────────────────────────────┘     │
│                     │                                        │
│  ┌──────────────────▼─────────────────────────────────┐     │
│  │      Step Alignment Engine                         │     │
│  │  • Synchronize traditional & shortcut steps       │     │
│  │  • Highlight differences                           │     │
│  │  • Generate side-by-side view                      │     │
│  └──────────────────┬─────────────────────────────────┘     │
│                     │                                        │
│  ┌──────────────────▼─────────────────────────────────┐     │
│  │      LaTeX Renderer                                │     │
│  │  • Mathematical notation                           │     │
│  │  • Chemical structures                             │     │
│  │  • Diagrams & figures                              │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│              DATA LAYER                                      │
│  ┌──────────────┐  ┌────────────┐  ┌────────────┐          │
│  │ PostgreSQL   │  │  pgvector  │  │   Redis    │          │
│  │ Problems     │  │  Shortcuts │  │   Cache    │          │
│  └──────────────┘  └────────────┘  └────────────┘          │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Dual-Pane Solution Flow

```mermaid
sequenceDiagram
    participant Student
    participant Chat
    participant Analyzer
    participant Traditional
    participant Shortcut
    participant Aligner
    participant UI
    
    Student->>Chat: Submit JEE problem
    Chat->>Analyzer: Parse problem
    Analyzer->>Analyzer: Detect subject, topic, difficulty
    
    par Generate Both Solutions
        Analyzer->>Traditional: Generate traditional solution
        Traditional->>Traditional: Step-by-step derivation
        
        and
        
        Analyzer->>Shortcut: Find applicable shortcuts
        Shortcut->>Shortcut: Pattern matching
        Shortcut->>Shortcut: Generate shortcut steps
    end
    
    Traditional-->>Aligner: Traditional steps
    Shortcut-->>Aligner: Shortcut steps
    
    Aligner->>Aligner: Align corresponding steps
    Aligner->>Aligner: Calculate time for each step
    Aligner->>Aligner: Highlight differences
    
    Aligner-->>UI: Aligned dual-pane solution
    UI-->>Student: Display side-by-side
    
    Note over Student,UI: Student can scroll both panes in sync
```

---

## 3. Problem Analysis Pipeline

```
┌──────────────────────────────────────────┐
│      Problem Input                       │
│  "A particle of mass m is attached..."  │
└────────────────┬─────────────────────────┘
                 │
    ┌────────────▼────────────┐
    │  Subject Detection      │
    │  GPT-5.5 classifier     │
    │  ✓ Physics              │
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────┐
    │  Topic Identification   │
    │  • Mechanics            │
    │  • Simple Harmonic      │
    │    Motion               │
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────┐
    │  Pattern Recognition    │
    │  • Spring-mass system   │
    │  • Energy conservation  │
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────┐
    │  Difficulty Assessment  │
    │  Based on:              │
    │  • Concepts required    │
    │  • Calculation steps    │
    │  • Past year data       │
    │  → Medium (6/10)        │
    └────────────┬────────────┘
                 │
    ┌────────────▼────────────┐
    │  Shortcut Matching      │
    │  Vector search →        │
    │  Energy method shortcut │
    └─────────────────────────┘
```

---

## 4. Shortcut Recommendation Engine

```mermaid
flowchart TD
    START([New Problem]) --> EMBED[Generate Problem Embedding<br/>sentence-transformers]
    
    EMBED --> VECTOR[Vector Similarity Search<br/>pgvector shortcuts]
    
    VECTOR --> FILTER{Filter by<br/>Subject & Topic}
    
    FILTER -->|Match Found| RANK[Rank Shortcuts by<br/>1. Similarity<br/>2. Success rate<br/>3. Time saved]
    FILTER -->|No Match| GENERAL[Use General Methods]
    
    RANK --> TOP[Select Top 3 Shortcuts]
    
    TOP --> VALIDATE{Validate<br/>Applicability}
    
    VALIDATE -->|Applicable| RECOMMEND[Recommend Shortcut]
    VALIDATE -->|Not Applicable| GENERAL
    
    RECOMMEND --> GENERATE[Generate Shortcut Solution]
    GENERAL --> STANDARD[Generate Standard Solution]
    
    GENERATE --> END([Display Both])
    STANDARD --> END
```

---

## 5. Dual-Pane UI Layout

```
┌─────────────────────────────────────────────────────────┐
│  JEE Shortcut Solutions                    [Settings]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Problem: A particle of mass 2kg is attached to...     │
│  Subject: Physics | Topic: SHM | Difficulty: Medium    │
│                                                         │
├────────────────────┬────────────────────────────────────┤
│                    │                                    │
│  📚 Traditional    │  ⚡ Shortcut Method               │
│  (480 seconds)     │  (120 seconds)                     │
│                    │                                    │
│  ─────────────────────────────────────────────────     │
│                    │                                    │
│  Step 1:           │  Step 1:                          │
│  Write down the    │  Use energy conservation          │
│  equation of       │  directly:                        │
│  motion:           │                                    │
│  F = -kx           │  ½mv² + ½kx² = constant          │
│                    │                                    │
│  Step 2:           │  Step 2:                          │
│  F = ma            │  Differentiate to get ω:          │
│  -kx = m(d²x/dt²)  │  ω = √(k/m)                       │
│                    │                                    │
│  Step 3:           │  Step 3:                          │
│  This is SHM with  │  Period T = 2π/ω                  │
│  ω² = k/m          │  T = 2π√(m/k)                     │
│                    │                                    │
│  Step 4:           │  Done! ✓                          │
│  ω = √(k/m)        │  💡 Why this works:               │
│                    │  Energy method skips              │
│  Step 5:           │  differential equations           │
│  Period T = 2π/ω   │                                    │
│  T = 2π√(m/k)      │  ⏱️ Saved: 6 minutes              │
│                    │                                    │
├────────────────────┴────────────────────────────────────┤
│  [◀ Previous Problem]  [Practice This]  [Next ▶]       │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Shortcut Database Structure

```mermaid
graph TB
    subgraph "Physics Shortcuts"
        P1[Dimensional Analysis]
        P2[Limiting Cases]
        P3[Symmetry Arguments]
        P4[Energy Conservation]
        P5[COM Methods]
    end
    
    subgraph "Chemistry Shortcuts"
        C1[Periodic Trends]
        C2[VEDANTU Rule]
        C3[Electron Counting]
        C4[Quick pKa Estimates]
    end
    
    subgraph "Mathematics Shortcuts"
        M1[Option Elimination]
        M2[AM-GM Inequality]
        M3[Discriminant Tricks]
        M4[Graph Analysis]
        M5[Symmetry in Integration]
    end
    
    subgraph "Metadata"
        META[Embedding Vector<br/>Success Rate<br/>Time Saved<br/>When to Use]
    end
    
    P1 --> META
    P2 --> META
    C1 --> META
    M1 --> META
    
    META --> SEARCH[(pgvector<br/>Similarity Search)]
```

---

## 7. Practice Mode Flow

```mermaid
stateDiagram-v2
    [*] --> ProblemPresented: Start Practice
    
    ProblemPresented --> MethodChoice: Student chooses
    
    MethodChoice --> Traditional: Use Traditional
    MethodChoice --> Shortcut: Use Shortcut
    MethodChoice --> ViewBoth: View Both First
    
    Traditional --> Solving: Student attempts
    Shortcut --> Solving: Student attempts
    ViewBoth --> MethodChoice: Then choose
    
    Solving --> Submit: Submit Answer
    
    Submit --> Correct: Correct ✓
    Submit --> Incorrect: Incorrect ✗
    
    Correct --> ShowComparison: Show both methods
    Incorrect --> ShowSolution: Show correct solution
    
    ShowComparison --> Analytics: Update stats
    ShowSolution --> Analytics: Update stats
    
    Analytics --> NextProblem: Continue?
    
    NextProblem --> ProblemPresented: Yes
    NextProblem --> [*]: No (End session)
    
    note right of Correct
        Track time taken
        Award time-saved points
    end note
    
    note right of Analytics
        Update:
        - Accuracy
        - Time saved
        - Shortcuts learned
    end note
```

---

## 8. Time Comparison Visualization

```mermaid
gantt
    title Time Comparison: Traditional vs Shortcut (8min vs 2min)
    dateFormat YYYY-MM-DD HH:mm:ss
    axisFormat %M:%S
    
    section Traditional Method (480s)
    Read Problem (30s)          :done, t1, 2024-01-01 00:00:00, 30s
    Identify Concepts (30s)     :done, t2, 2024-01-01 00:00:30, 30s
    Write Equations (60s)       :done, t3, 2024-01-01 00:01:00, 60s
    Solve Step-by-Step (240s)   :done, t4, 2024-01-01 00:02:00, 240s
    Verify Answer (60s)         :done, t5, 2024-01-01 00:06:00, 60s
    
    section Shortcut Method (120s)
    Read Problem (30s)          :crit, s1, 2024-01-01 00:00:00, 30s
    Recognize Pattern (15s)     :crit, s2, 2024-01-01 00:00:30, 15s
    Apply Shortcut (45s)        :crit, s3, 2024-01-01 00:00:45, 45s
    Calculate Directly (15s)    :crit, s4, 2024-01-01 00:01:30, 15s
    Verify Answer (15s)         :crit, s5, 2024-01-01 00:01:45, 15s
```

---

## 9. Subject-Specific Architectures

### **Physics Problem Solving**

```
Problem Input
     │
     ├─→ Mechanics? ─→ [Energy/Momentum shortcuts]
     │
     ├─→ Electromagnetism? ─→ [Symmetry/Gauss Law shortcuts]
     │
     ├─→ Waves? ─→ [Boundary condition shortcuts]
     │
     └─→ Modern Physics? ─→ [Formula-based shortcuts]
```

### **Chemistry Problem Solving**

```
Problem Input
     │
     ├─→ Organic? ─→ [Mechanism/Product shortcuts]
     │
     ├─→ Inorganic? ─→ [Periodic trend shortcuts]
     │
     ├─→ Physical? ─→ [Graph analysis shortcuts]
     │
     └─→ Numerical? ─→ [Approximation shortcuts]
```

### **Mathematics Problem Solving**

```
Problem Input
     │
     ├─→ Calculus? ─→ [Limit/Graph shortcuts]
     │
     ├─→ Algebra? ─→ [Discriminant/AM-GM shortcuts]
     │
     ├─→ Trigonometry? ─→ [Identity/Angle shortcuts]
     │
     └─→ Coordinate Geometry? ─→ [Symmetry shortcuts]
```

---

## 10. Analytics Dashboard

```mermaid
graph TB
    subgraph "Student Analytics"
        A1[Total Problems: 247]
        A2[Shortcuts Learned: 42]
        A3[Total Time Saved: 18.5 hours]
        A4[Accuracy: 78%]
    end
    
    subgraph "Subject Breakdown"
        S1[Physics: 95 problems<br/>Time saved: 7.2h]
        S2[Chemistry: 82 problems<br/>Time saved: 5.8h]
        S3[Mathematics: 70 problems<br/>Time saved: 5.5h]
    end
    
    subgraph "Top Shortcuts Used"
        T1[Dimensional Analysis: 23×]
        T2[Energy Conservation: 18×]
        T3[Option Elimination: 15×]
    end
    
    subgraph "Weak Areas"
        W1[Organic Mechanisms: 45% accuracy]
        W2[Complex Integration: 52% accuracy]
    end
    
    A1 --> S1
    A2 --> T1
    A3 --> S1
    A4 --> W1
```

---

## 11. Caching Strategy

```
┌─────────────────────────────────────┐
│      Request: Solve Problem X       │
└────────────────┬────────────────────┘
                 │
    ┌────────────▼────────────┐
    │  Check Redis Cache      │
    │  Key: problem_hash      │
    └────────────┬────────────┘
                 │
         ┌───────┴───────┐
         │               │
      Hit │            Miss│
         │               │
    ┌────▼────┐   ┌──────▼──────┐
    │ Return  │   │  Generate   │
    │ Cached  │   │  Solution   │
    │Solution │   └──────┬──────┘
    └─────────┘          │
                    ┌────▼────┐
                    │  Cache  │
                    │ (24hr)  │
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │ Return  │
                    │Solution │
                    └─────────┘
```

**Cache Layers:**
1. **L1 - Browser Cache**: Recently viewed solutions (10 problems)
2. **L2 - Redis**: Generated solutions (24 hour TTL)
3. **L3 - Database**: All historical solutions (permanent)

---

## 12. Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Production Cluster              │
├─────────────────────────────────────────┤
│                                         │
│  Namespace: jee-shortcuts               │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  Web Frontend                  │    │
│  │  • 3-5 pods (CDN + SSR)        │    │
│  │  • Next.js 16                  │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  API Gateway                   │    │
│  │  • 3-5 pods (CPU autoscale)    │    │
│  │  • 2 CPU, 4GB RAM              │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  AI Solution Engine            │    │
│  │  • 5-10 pods (queue autoscale) │    │
│  │  • 4 CPU, 8GB RAM              │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Data Services                   │
├─────────────────────────────────────────┤
│                                         │
│  PostgreSQL + pgvector:                 │
│  • Primary (r6g.xlarge)                 │
│  • 10,000+ problems                     │
│  • 500+ shortcuts                       │
│                                         │
│  Redis:                                 │
│  • 2-node cluster (cache.r6g.large)    │
│  • 24-hour solution cache               │
│                                         │
│  CDN:                                   │
│  • Static assets (images, PDFs)         │
│  • LaTeX-rendered formulas              │
└─────────────────────────────────────────┘
```

---

**Status:** ✅ Complete - Architecture & 12 System Diagrams

**Version:** 1.0  
**Date:** June 18, 2026

**Usage:** Render with Mermaid (GitHub, GitLab, VS Code)
