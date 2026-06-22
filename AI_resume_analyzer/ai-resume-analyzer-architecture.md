# AI Resume Analyzer - Detailed Architecture Specification

**Document Date:** June 18, 2026  
**Version:** 1.0  
**Status:** Architecture Design  
**Tech Stack:** Golang + Python + Next.js 16

---

## 📐 System Architecture Overview

### **High-Level Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    Next.js 16 Application                     │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │ │
│  │  │Dashboard │  │  Upload  │  │ Analysis │  │Job Matching │ │ │
│  │  │   Page   │  │   Page   │  │   Page   │  │    Page     │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────────┘ │ │
│  │                                                              │ │
│  │  React 19.2.7 | Tailwind 4.x | shadcn/ui | Framer Motion  │ │
│  └──────────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                         HTTPS/REST
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                      API GATEWAY LAYER                              │
│                     (Golang + Fiber 2.x)                            │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │     Auth     │  │     Rate     │  │   Request    │            │
│  │  Middleware  │  │   Limiting   │  │   Routing    │            │
│  │   (Clerk)    │  │   (Unkey)    │  │  (Fiber)     │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │              Load Balancer (Round Robin)                      │ │
│  └──────────────────────────────────────────────────────────────┘ │
└─────────────┬────────────────┬────────────────┬────────────────────┘
              │                │                │
            gRPC             gRPC             gRPC
              │                │                │
┌─────────────▼────┐ ┌─────────▼────┐ ┌────────▼───────┐
│  Parser Service  │ │  AI Service  │ │ Matcher Service│
│    (Python)      │ │   (Python)   │ │    (Golang)    │
│   FastAPI 0.111  │ │  FastAPI +   │ │  Native Go     │
│                  │ │  LangChain   │ │                │
│  ┌────────────┐  │ │ ┌──────────┐ │ │ ┌────────────┐ │
│  │PDF Parser  │  │ │ │ GPT-5.5  │ │ │ │Vector      │ │
│  │DOCX Parser │  │ │ │ Opus 4.8 │ │ │ │Search      │ │
│  │Text Extract│  │ │ │ Embedder │ │ │ │Similarity  │ │
│  └────────────┘  │ │ └──────────┘ │ │ └────────────┘ │
└──────────────────┘ └──────────────┘ └────────────────┘
         │                   │                  │
         └───────────────────┼──────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
┌─────────────▼──────┐          ┌──────────▼─────────┐
│   Data Layer       │          │   AI Models Layer  │
│                    │          │                    │
│ ┌────────────────┐ │          │ ┌────────────────┐ │
│ │   PostgreSQL   │ │          │ │   GPT-5.5      │ │
│ │   (Primary)    │ │          │ │   (OpenAI)     │ │
│ └────────────────┘ │          │ └────────────────┘ │
│ ┌────────────────┐ │          │ ┌────────────────┐ │
│ │   PostgreSQL   │ │          │ │ Claude Opus    │ │
│ │ (Read Replica) │ │          │ │    4.8         │ │
│ └────────────────┘ │          │ └────────────────┘ │
│ ┌────────────────┐ │          └────────────────────┘
│ │     Redis      │ │
│ │   (Cache)      │ │          ┌────────────────────┐
│ └────────────────┘ │          │  Vector Database   │
│ ┌────────────────┐ │          │                    │
│ │   Pinecone     │ │          │ ┌────────────────┐ │
│ │   (Vectors)    │ │          │ │   Pinecone     │ │
│ └────────────────┘ │          │ │   (Primary)    │ │
└────────────────────┘          │ └────────────────┘ │
                                │ ┌────────────────┐ │
┌────────────────────┐          │ │ Upstash Vector │ │
│  Background Jobs   │          │ │  (Fallback)    │ │
│    (Golang)        │          │ └────────────────┘ │
│   Asynq + Redis    │          └────────────────────┘
│                    │
│ ┌────────────────┐ │          ┌────────────────────┐
│ │ Resume Parser  │ │          │   File Storage     │
│ │ File Processor │ │          │                    │
│ │ Email Sender   │ │          │ ┌────────────────┐ │
│ │ Report Gen     │ │          │ │ Vercel Blob    │ │
│ └────────────────┘ │          │ │  (Primary)     │ │
└────────────────────┘          │ └────────────────┘ │
                                │ ┌────────────────┐ │
                                │ │ Cloudflare R2  │ │
                                │ │  (Backup)      │ │
                                │ └────────────────┘ │
                                └────────────────────┘
```

---

## 🔄 Data Flow Diagrams

### **1. Resume Upload & Analysis Flow**

```
User                 Frontend              API Gateway           Parser Service         AI Service            Database
 │                      │                       │                      │                     │                   │
 │  Upload Resume       │                       │                      │                     │                   │
 ├─────────────────────>│                       │                      │                     │                   │
 │                      │  POST /api/upload     │                      │                     │                   │
 │                      ├──────────────────────>│                      │                     │                   │
 │                      │                       │  Auth Check          │                     │                   │
 │                      │                       ├──────────┐           │                     │                   │
 │                      │                       │          │           │                     │                   │
 │                      │                       │<─────────┘           │                     │                   │
 │                      │                       │  Upload to Blob      │                     │                   │
 │                      │                       ├──────────────────────────────────────────────────────────────>│
 │                      │                       │                      │                     │                   │
 │                      │                       │  Save Metadata       │                     │                   │
 │                      │                       ├──────────────────────────────────────────────────────────────>│
 │                      │                       │                      │                     │                   │
 │                      │                       │  Queue Parse Job     │                     │                   │
 │                      │                       ├──────────────────────>│                     │                   │
 │                      │  202 Accepted         │                      │                     │                   │
 │                      │<──────────────────────┤                      │                     │                   │
 │  Upload ID           │                       │                      │                     │                   │
 │<─────────────────────┤                       │                      │                     │                   │
 │                      │                       │                      │                     │                   │
 │                      │                       │        [Background Processing]              │                   │
 │                      │                       │                      │  Parse PDF/DOCX     │                   │
 │                      │                       │                      ├──────────┐          │                   │
 │                      │                       │                      │          │          │                   │
 │                      │                       │                      │<─────────┘          │                   │
 │                      │                       │                      │  Extract Text       │                   │
 │                      │                       │                      ├─────────────────────>│                   │
 │                      │                       │                      │                     │  Analyze (GPT)    │
 │                      │                       │                      │                     ├──────────┐        │
 │                      │                       │                      │                     │          │        │
 │                      │                       │                      │                     │<─────────┘        │
 │                      │                       │                      │                     │  Save Results     │
 │                      │                       │                      │                     ├──────────────────>│
 │                      │                       │                      │                     │                   │
 │                      │                       │        Status: Completed                   │                   │
 │                      │                       │<───────────────────────────────────────────┤                   │
 │                      │  WebSocket Update     │                      │                     │                   │
 │                      │<──────────────────────┤                      │                     │                   │
 │  Analysis Complete!  │                       │                      │                     │                   │
 │<─────────────────────┤                       │                      │                     │                   │
```

### **2. Job Matching Flow**

```
User                 Frontend              API Gateway           Matcher Service        Vector DB             Database
 │                      │                       │                      │                     │                   │
 │  Request Match       │                       │                      │                     │                   │
 ├─────────────────────>│                       │                      │                     │                   │
 │                      │  POST /api/match      │                      │                     │                   │
 │                      ├──────────────────────>│                      │                     │                   │
 │                      │                       │  Get Resume          │                     │                   │
 │                      │                       ├──────────────────────────────────────────────────────────────>│
 │                      │                       │                      │                     │    Resume Data    │
 │                      │                       │<──────────────────────────────────────────────────────────────┤
 │                      │                       │  Generate Embedding  │                     │                   │
 │                      │                       ├─────────────────────>│                     │                   │
 │                      │                       │                      │  Search Vectors     │                   │
 │                      │                       │                      ├────────────────────>│                   │
 │                      │                       │                      │     Top 10 Matches  │                   │
 │                      │                       │                      │<────────────────────┤                   │
 │                      │                       │  Calculate Scores    │                     │                   │
 │                      │                       │<─────────────────────┤                     │                   │
 │                      │  Match Results        │                      │                     │                   │
 │                      │<──────────────────────┤                      │                     │                   │
 │  Top Matches + Score │                       │                      │                     │                   │
 │<─────────────────────┤                       │                      │                     │                   │
```

---

## 🏛️ Service Architecture Details

### **API Gateway Service (Golang)**

```go
// Architecture Components

package main

type APIGateway struct {
    router      *fiber.App
    authClient  *clerk.Client
    rateLimiter *unkey.Client
    logger      *zap.Logger
    metrics     *prometheus.Registry
}

// Middleware Stack
// 1. CORS Handler
// 2. Logger (Axiom)
// 3. Auth Middleware (Clerk)
// 4. Rate Limiter (Unkey)
// 5. Request ID Generator
// 6. Error Handler
// 7. Metrics Collector

// Route Groups
// /api/v1/upload     - File upload endpoints
// /api/v1/resumes    - Resume CRUD operations
// /api/v1/analysis   - Analysis endpoints
// /api/v1/match      - Job matching endpoints
// /api/v1/users      - User management

// gRPC Clients
parserClient   *pb.ParserServiceClient
aiClient       *pb.AIServiceClient
matcherClient  *pb.MatcherServiceClient
```

**Key Responsibilities:**
- Request routing and load balancing
- Authentication & authorization
- Rate limiting & throttling
- Request/response logging
- Metrics collection
- Error handling & retry logic

**Performance Targets:**
- Request latency: p50 < 50ms, p95 < 200ms, p99 < 500ms
- Throughput: 10,000 req/sec per instance
- Connection pooling: 1000 concurrent connections
- Circuit breaker: 3 failures trigger open state

---

### **Parser Service (Python)**

```python
# Architecture Components

from fastapi import FastAPI
from pydantic import BaseModel

class ParserService:
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.text_cleaner = TextCleaner()
        self.cache = Redis()
    
    # Parsers
    # - pdf_parse: PyPDF2, pdfplumber
    # - docx_parse: python-docx, mammoth
    # - text_clean: regex, nltk
    
    # Endpoints
    # POST /parse - Parse document
    # GET /status/{job_id} - Check status
    # GET /result/{job_id} - Get result

# Processing Pipeline
# 1. Receive file from blob storage
# 2. Detect file type
# 3. Extract raw text
# 4. Clean and normalize text
# 5. Extract sections (header, experience, education, skills)
# 6. Return structured data
```

**Key Responsibilities:**
- PDF/DOCX/TXT parsing
- Text extraction & cleaning
- Section detection
- Format normalization

**Performance Targets:**
- Parse time: < 3s for PDF, < 2s for DOCX
- Accuracy: > 95% text extraction
- Memory: < 500MB per parse
- Concurrent jobs: 50 per instance

---

### **AI Service (Python)**

```python
# Architecture Components

from langchain import OpenAI, Anthropic
from pydantic import BaseModel

class AIService:
    def __init__(self):
        self.gpt_client = OpenAI(model="gpt-5.5")
        self.claude_client = Anthropic(model="claude-opus-4.8")
        self.embedder = OpenAIEmbeddings()
        self.cache = Redis()
    
    # AI Models
    # - GPT-5.5: Primary for structured extraction
    # - Claude Opus 4.8: Secondary for detailed analysis
    # - text-embedding-3-large: Vector embeddings
    
    # Endpoints
    # POST /analyze - Analyze resume
    # POST /extract - Extract structured data
    # POST /embed - Generate embeddings
    # POST /suggest - Get improvement suggestions

# Analysis Pipeline
# 1. Receive parsed text
# 2. Extract structured data (GPT-5.5)
# 3. Validate with Zod schema
# 4. Analyze quality (Claude Opus 4.8)
# 5. Generate suggestions
# 6. Calculate scores (ATS, overall)
# 7. Return results
```

**Key Responsibilities:**
- AI-powered resume analysis
- Structured data extraction
- Quality scoring
- Improvement suggestions
- Vector embedding generation

**Performance Targets:**
- Analysis time: < 10s per resume
- Accuracy: > 90% extraction accuracy
- API cost: < $0.05 per analysis
- Cache hit rate: > 70%

---

### **Matcher Service (Golang)**

```go
// Architecture Components

package matcher

type MatcherService struct {
    vectorDB    *pinecone.Client
    embedder    *openai.EmbeddingClient
    scorer      *SimilarityScorer
    cache       *redis.Client
}

// Matching Algorithms
// 1. Vector Similarity (Cosine)
// 2. Keyword Matching (TF-IDF)
// 3. Skill Overlap Score
// 4. Experience Level Match
// 5. Education Match

// Endpoints
// POST /match - Find matching jobs
// POST /score - Calculate match score
// GET /similar - Find similar resumes

// Scoring Formula
// Total Score = 
//   0.4 * Vector Similarity +
//   0.3 * Skill Overlap +
//   0.2 * Experience Match +
//   0.1 * Education Match
```

**Key Responsibilities:**
- Job-resume matching
- Similarity scoring
- Vector search operations
- Result ranking

**Performance Targets:**
- Match time: < 2s for top 100 results
- Accuracy: > 85% relevance score
- Vector search: < 100ms
- Throughput: 5,000 matches/sec

---

## 💾 Database Architecture

### **PostgreSQL Schema Design**

```sql
-- Partitioning Strategy
-- resumes table: Partitioned by created_at (monthly)
-- analyses table: Partitioned by created_at (monthly)

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_clerk_id ON users(clerk_id);
CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_status ON resumes(analysis_status);
CREATE INDEX idx_resumes_created_at ON resumes(created_at);
CREATE INDEX idx_analyses_resume_id ON analyses(resume_id);
CREATE INDEX idx_analyses_type ON analyses(type);

-- Read Replica Configuration
-- - Primary: Write operations
-- - Replica 1: Read operations (dashboard, analytics)
-- - Replica 2: Backup & reporting

-- Connection Pooling
-- - Max connections: 100
-- - Min connections: 10
-- - Idle timeout: 5 minutes
-- - Max lifetime: 30 minutes
```

### **Redis Architecture**

```
Redis Cluster (3 nodes)
│
├── Node 1 (Master) - Slots 0-5460
│   ├── Cache Layer
│   │   ├── Resume metadata (TTL: 1 hour)
│   │   ├── Analysis results (TTL: 24 hours)
│   │   └── User sessions (TTL: 7 days)
│   └── Replica 1 (Slave)
│
├── Node 2 (Master) - Slots 5461-10922
│   ├── Job Queue (Asynq)
│   │   ├── Parse jobs
│   │   ├── Analysis jobs
│   │   └── Email jobs
│   └── Replica 2 (Slave)
│
└── Node 3 (Master) - Slots 10923-16383
    ├── Rate Limiting
    │   ├── User limits
    │   ├── IP limits
    │   └── API key limits
    └── Replica 3 (Slave)
```

---

## 🔐 Security Architecture

### **Defense in Depth Strategy**

```
Layer 7: Application
│  - Input validation (Zod)
│  - Output encoding
│  - CSRF tokens
│  - XSS protection
│
Layer 6: API Gateway
│  - Authentication (Clerk + PASETO)
│  - Authorization (RBAC)
│  - Rate limiting (Unkey)
│  - Request validation
│
Layer 5: Network
│  - WAF (Cloudflare)
│  - DDoS protection
│  - TLS 1.3
│  - IP whitelisting
│
Layer 4: Data
│  - Encryption at rest (AES-256)
│  - Encryption in transit (TLS)
│  - Secret management (Vault)
│  - PII masking
│
Layer 3: Infrastructure
│  - VPC isolation
│  - Security groups
│  - Private subnets
│  - Bastion hosts
│
Layer 2: Monitoring
│  - SIEM (Sentry)
│  - Audit logging
│  - Anomaly detection
│  - Alert system
│
Layer 1: Compliance
│  - SOC2 Type II
│  - GDPR compliance
│  - HIPAA ready
│  - Regular audits
```

---

## 📊 Monitoring & Observability

### **Metrics Collection**

```
Prometheus Metrics

# API Gateway
http_request_duration_seconds
http_requests_total
http_request_size_bytes
http_response_size_bytes

# Services
grpc_request_duration_seconds
grpc_requests_total
grpc_errors_total

# Database
db_connections_active
db_query_duration_seconds
db_transactions_total

# Redis
redis_commands_total
redis_keyspace_hits_total
redis_keyspace_misses_total

# Background Jobs
asynq_processed_total
asynq_failed_total
asynq_retry_total
```

### **Logging Strategy**

```json
{
  "timestamp": "2026-06-18T10:30:45Z",
  "level": "info",
  "service": "api-gateway",
  "trace_id": "abc123",
  "user_id": "user_xyz",
  "method": "POST",
  "path": "/api/v1/upload",
  "status": 202,
  "duration_ms": 45,
  "ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

### **Tracing (OpenTelemetry)**

```
Request Flow Trace

Frontend → API Gateway → Parser Service → AI Service → Database
   │           │              │               │            │
  [1ms]      [5ms]         [200ms]        [8000ms]      [50ms]
                                                           │
                                              Total: 8,256ms
```

---

## 🚀 Deployment Architecture

### **Kubernetes Deployment**

```yaml
# Cluster Configuration
Cluster: Production (us-east-1)
├── Namespace: resume-analyzer
│   ├── API Gateway (3 replicas)
│   │   ├── Resources: 2 CPU, 4GB RAM
│   │   ├── HPA: Min 3, Max 10
│   │   └── Strategy: Rolling Update
│   ├── Parser Service (2 replicas)
│   │   ├── Resources: 1 CPU, 2GB RAM
│   │   ├── HPA: Min 2, Max 5
│   │   └── Strategy: Rolling Update
│   ├── AI Service (2 replicas)
│   │   ├── Resources: 2 CPU, 4GB RAM
│   │   ├── HPA: Min 2, Max 8
│   │   └── Strategy: Rolling Update
│   ├── Matcher Service (2 replicas)
│   │   ├── Resources: 2 CPU, 4GB RAM
│   │   ├── HPA: Min 2, Max 6
│   │   └── Strategy: Rolling Update
│   └── Worker Service (3 replicas)
│       ├── Resources: 1 CPU, 2GB RAM
│       ├── HPA: Min 3, Max 10
│       └── Strategy: Rolling Update
│
├── Ingress
│   ├── Nginx Ingress Controller
│   ├── SSL/TLS Termination
│   └── Rate Limiting
│
└── Storage
    ├── PostgreSQL (StatefulSet)
    ├── Redis (StatefulSet)
    └── Persistent Volumes
```

---

**End of Architecture Document**

**Next Steps:**
1. Review and validate architecture
2. Create deployment scripts
3. Set up monitoring dashboards
4. Conduct load testing
5. Security audit
6. Cost estimation
