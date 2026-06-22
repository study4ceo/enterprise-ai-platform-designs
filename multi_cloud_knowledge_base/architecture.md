# Universal Knowledge Hub - Architecture Document

**Document Date:** June 18, 2026  
**Version:** 1.0  
**Status:** Production-Ready Architecture  
**Project:** Enterprise-Wide Unified Knowledge Search & AI Q&A Platform

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [High-Level Architecture](#high-level-architecture)
4. [Service Architecture](#service-architecture)
5. [Data Architecture](#data-architecture)
6. [Security Architecture](#security-architecture)
7. [Deployment Architecture](#deployment-architecture)
8. [Integration Architecture](#integration-architecture)
9. [Scalability & Performance](#scalability--performance)
10. [Disaster Recovery](#disaster-recovery)

---

## 🎯 System Overview

### **Purpose**
Universal Knowledge Hub aggregates and indexes information from 25+ enterprise data sources (Slack, Jira, Gmail, S3, GitHub, etc.) and provides:
- Unified vector + full-text hybrid search
- AI-powered Q&A with RAG (Retrieval-Augmented Generation)
- Real-time data synchronization
- Permission-aware access control

### **Core Architecture Decisions**

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Backend Language** | Golang + Python | Go for performance (API, search, connectors), Python for AI/ML |
| **Frontend** | Next.js 16 + React 19.2.7 | Latest features, Server Components, streaming |
| **Database** | PostgreSQL 16 + pgvector | Vector search + relational data + full-text search in one |
| **Cache** | Redis 7.x | High-performance caching, pub/sub for real-time updates |
| **Message Queue** | RabbitMQ | Reliable message delivery for connector events |
| **AI Models** | GPT-5.5 + Claude Opus 4.8 | Best-in-class reasoning and long context |
| **Orchestration** | Kubernetes (EKS) | Industry standard, auto-scaling, self-healing |
| **Observability** | Logfire + Prometheus + Grafana | Modern stack with structured logging |

---

## 🏛️ Architecture Principles

### **1. Microservices Architecture**
- Each service has a single responsibility
- Services communicate via gRPC (internal) and REST (external)
- Independent deployment and scaling
- Language-agnostic interfaces (protobuf)

### **2. Event-Driven Design**
- Connector events flow through RabbitMQ
- Asynchronous processing for indexing
- Real-time updates via webhooks
- Decoupled producer-consumer pattern

### **3. Domain-Driven Design**
- Core domains: Search, Indexing, AI, Connectors, Auth
- Bounded contexts with clear interfaces
- Ubiquitous language across team

### **4. Cloud-Native**
- Containerized services (Docker)
- Kubernetes for orchestration
- Stateless services (12-factor app)
- Infrastructure as Code (Terraform)

### **5. Security by Design**
- Zero-trust architecture
- End-to-end encryption
- Row-level security in database
- Principle of least privilege

### **6. Test-Driven Development**
- Write tests first
- 85%+ code coverage
- Automated CI/CD pipeline
- Property-based testing for critical paths

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │   Web App    │  │  Slack Bot   │  │   Browser    │                 │
│  │  (Next.js)   │  │              │  │  Extension   │                 │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
└─────────┼──────────────────┼──────────────────┼──────────────────────────┘
          │                  │                  │
          │            HTTPS/REST               │
          └──────────────────┼──────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (Golang + Fiber)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │    Auth     │  │Rate Limiting│  │   Routing   │  │Load Balance │  │
│  │   (Clerk)   │  │   (Unkey)   │  │             │  │             │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
└────────────┬────────────────┬────────────────┬────────────────┬─────────┘
             │                │                │                │
           gRPC             gRPC             gRPC             gRPC
             │                │                │                │
    ┌────────▼────────┐  ┌───▼──────────┐  ┌─▼──────────┐  ┌─▼──────────┐
    │  Search Service │  │  AI Service  │  │  Indexing  │  │ Analytics  │
    │    (Golang)     │  │   (Python)   │  │  Service   │  │  Service   │
    │                 │  │              │  │  (Python)  │  │  (Golang)  │
    │ • Vector Search │  │ • RAG        │  │ • Chunking │  │ • Metrics  │
    │ • Full-text     │  │ • Q&A Gen    │  │ • Embed    │  │ • Reports  │
    │ • Hybrid Rank   │  │ • Re-rank    │  │ • Storage  │  │ • Insights │
    └────────┬────────┘  └───┬──────────┘  └─┬──────────┘  └─┬──────────┘
             │                │                │                │
             │                │                │                │
             └────────────────┼────────────────┼────────────────┘
                              │                │
                    ┌─────────▼────────────────▼─────────┐
                    │       DATA LAYER                   │
                    │  ┌──────────────┐  ┌────────────┐ │
                    │  │ PostgreSQL   │  │   Redis    │ │
                    │  │  + pgvector  │  │   Cache    │ │
                    │  └──────────────┘  └────────────┘ │
                    └─────────┬──────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  CONNECTOR HUB    │
                    │     (Golang)      │
                    │  Orchestrates all │
                    │  data connectors  │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌──────▼──────┐
│  RabbitMQ      │   │  Event Queue    │   │  Webhooks   │
│  Message Queue │   │  Distribution   │   │   Server    │
└───────┬────────┘   └────────┬────────┘   └──────┬──────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────────┐
    │                         │                             │
┌───▼──────┐  ┌──────────┐  ┌▼────────┐  ┌────────┐  ┌────▼────┐
│  Slack   │  │  Jira    │  │ Gmail   │  │   S3   │  │ GitHub  │
│Connector │  │Connector │  │Connector│  │Connector│ │Connector│
└──────────┘  └──────────┘  └─────────┘  └────────┘  └─────────┘
     ...20 more connectors (Teams, Asana, Confluence, etc.)...

                              │
                    ┌─────────▼─────────┐
                    │  OBSERVABILITY    │
                    │                   │
                    │  ┌─────────────┐  │
                    │  │  Logfire    │  │
                    │  │ (Pydantic)  │  │
                    │  └─────────────┘  │
                    │  ┌─────────────┐  │
                    │  │ Prometheus  │  │
                    │  └─────────────┘  │
                    │  ┌─────────────┐  │
                    │  │  Grafana    │  │
                    │  └─────────────┘  │
                    │  ┌─────────────┐  │
                    │  │   Sentry    │  │
                    │  └─────────────┘  │
                    └───────────────────┘
```

---

## 🎛️ Service Architecture

### **1. API Gateway (Golang + Fiber)**

**Responsibilities:**
- Request routing to backend services
- Authentication (Clerk integration)
- Authorization (RBAC)
- Rate limiting (Unkey)
- Request/response transformation
- Load balancing
- Circuit breaking

**Technology Stack:**
- **Language:** Golang 1.22+
- **Framework:** Fiber 2.x
- **Communication:** gRPC client to backend services
- **Protocols:** REST (external), gRPC (internal)

**Key Endpoints:**
```
POST   /api/v1/search          - Unified search
POST   /api/v1/qa              - AI Q&A generation
GET    /api/v1/documents/:id   - Get document details
POST   /api/v1/sources         - Connect data source
GET    /api/v1/sources         - List connected sources
DELETE /api/v1/sources/:id     - Disconnect source
GET    /api/v1/health          - Health check
GET    /api/v1/metrics         - Prometheus metrics
```

**Performance Targets:**
- Latency: p95 < 50ms (routing overhead)
- Throughput: 10,000 req/s
- Availability: 99.99%

---

### **2. Search Service (Golang)**

**Responsibilities:**
- Vector similarity search (pgvector)
- Full-text search (PostgreSQL tsvector)
- Hybrid ranking (RRF - Reciprocal Rank Fusion)
- Result filtering and pagination
- Search history tracking
- Query optimization

**Technology Stack:**
- **Language:** Golang 1.22+
- **Database Driver:** pgx v5 (PostgreSQL)
- **Cache:** go-redis v9
- **Vector Search:** pgvector extension

**Architecture:**
```
┌──────────────────────────────────────────────────────┐
│            Search Service                            │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐         ┌──────────────┐         │
│  │   Vector     │         │  Full-Text   │         │
│  │   Search     │         │    Search    │         │
│  │   Engine     │         │    Engine    │         │
│  └──────┬───────┘         └──────┬───────┘         │
│         │                        │                  │
│         └────────────┬───────────┘                  │
│                      ↓                               │
│           ┌──────────────────┐                      │
│           │  Hybrid Ranker   │                      │
│           │  (RRF Algorithm) │                      │
│           └──────────────────┘                      │
│                      ↓                               │
│           ┌──────────────────┐                      │
│           │ Permission Filter│                      │
│           │   (Row-Level)    │                      │
│           └──────────────────┘                      │
│                      ↓                               │
│           ┌──────────────────┐                      │
│           │  Result Ranker   │                      │
│           │  & Paginator     │                      │
│           └──────────────────┘                      │
└──────────────────────────────────────────────────────┘
```

**Key Algorithms:**
```go
// Reciprocal Rank Fusion (RRF)
func hybridRank(vectorResults, ftsResults []Document, k float64) []Document {
    scores := make(map[string]float64)
    
    // Score from vector search
    for i, doc := range vectorResults {
        scores[doc.ID] += 1.0 / (k + float64(i+1))
    }
    
    // Score from full-text search
    for i, doc := range ftsResults {
        scores[doc.ID] += 1.0 / (k + float64(i+1))
    }
    
    // Sort by combined score
    return sortByScore(scores)
}
```

**Performance Targets:**
- Vector search (100K docs): < 100ms
- Full-text search: < 50ms
- Hybrid search: < 200ms
- Cache hit rate: > 70%

---

### **3. AI Service (Python + FastAPI)**

**Responsibilities:**
- RAG (Retrieval-Augmented Generation) pipeline
- Embedding generation (OpenAI text-embedding-3-large)
- Q&A generation (GPT-5.5, Claude Opus 4.8)
- Re-ranking search results by relevance
- Answer confidence scoring
- Token usage tracking

**Technology Stack:**
- **Language:** Python 3.12+
- **Framework:** FastAPI 0.111+
- **HTTP Client:** HTTPX 0.27+ (async)
- **AI Framework:** LangChain 0.2.x
- **LLM APIs:** OpenAI, Anthropic
- **Observability:** Logfire

**RAG Pipeline:**
```
┌────────────────────────────────────────────────────────────┐
│                   AI Service RAG Pipeline                  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  User Query: "How do we deploy to production?"            │
│       ↓                                                    │
│  ┌─────────────────────────────┐                          │
│  │ 1. Query Understanding       │                          │
│  │    • Intent classification   │                          │
│  │    • Entity extraction       │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  ┌─────────────────────────────┐                          │
│  │ 2. Embedding Generation      │                          │
│  │    • OpenAI text-embedding   │                          │
│  │    • 3072-dim vector         │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  ┌─────────────────────────────┐                          │
│  │ 3. Retrieval (via Search)    │                          │
│  │    • Vector search (top 50)  │                          │
│  │    • Full-text search        │                          │
│  │    • Hybrid ranking          │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  ┌─────────────────────────────┐                          │
│  │ 4. Re-Ranking                │                          │
│  │    • Semantic similarity     │                          │
│  │    • Recency boost           │                          │
│  │    • Source authority        │                          │
│  │    • Select top 10           │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  ┌─────────────────────────────┐                          │
│  │ 5. Context Building          │                          │
│  │    • Chunk docs for context  │                          │
│  │    • Add metadata            │                          │
│  │    • Format for LLM          │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  ┌─────────────────────────────┐                          │
│  │ 6. Prompt Engineering        │                          │
│  │    • System prompt           │                          │
│  │    • Context injection       │                          │
│  │    • Citation instructions   │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  ┌─────────────────────────────┐                          │
│  │ 7. LLM Call                  │                          │
│  │    • GPT-5.5 or Claude       │                          │
│  │    • Streaming response      │                          │
│  │    • Token tracking          │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  ┌─────────────────────────────┐                          │
│  │ 8. Post-Processing           │                          │
│  │    • Extract citations       │                          │
│  │    • Calculate confidence    │                          │
│  │    • Format response         │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  Answer: "We use GitHub Actions for CI/CD..."             │
│  Sources: [Slack #devops, docs/deploy.md, JIRA-123]      │
└────────────────────────────────────────────────────────────┘
```

**Key Implementation:**
```python
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
import logfire

@dataclass
class RAGAnswer:
    answer: str
    sources: list[dict]
    confidence: float
    tokens_used: int
    model: str

async def rag_pipeline(query: str, user_id: str) -> RAGAnswer:
    """Complete RAG pipeline"""
    
    with logfire.span("rag_pipeline", query=query):
        # 1. Generate query embedding
        embedding = await generate_embedding(query)
        
        # 2. Retrieve relevant documents
        search_results = await search_service.hybrid_search(
            embedding=embedding,
            query=query,
            user_id=user_id,
            limit=50
        )
        
        # 3. Re-rank by relevance
        top_docs = await rerank_documents(search_results, query, limit=10)
        
        # 4. Build context
        context = build_context(top_docs)
        
        # 5. Generate answer
        llm = ChatOpenAI(model="gpt-5.5", temperature=0.2)
        answer = await llm.ainvoke(create_prompt(query, context))
        
        return RAGAnswer(
            answer=answer.content,
            sources=extract_sources(top_docs),
            confidence=calculate_confidence(answer, top_docs),
            tokens_used=answer.usage.total_tokens,
            model="gpt-5.5"
        )
```

**Performance Targets:**
- Embedding generation: < 200ms
- Re-ranking: < 300ms
- LLM call: < 3s (streaming starts in < 500ms)
- Total RAG pipeline: p95 < 5s

---

### **4. Indexing Service (Python + FastAPI)**

**Responsibilities:**
- Document ingestion from connector events
- Text extraction (PDF, DOCX, etc.)
- Document chunking (semantic chunks)
- Embedding generation (batch processing)
- Database storage
- Sync job management

**Technology Stack:**
- **Language:** Python 3.12+
- **Framework:** FastAPI 0.111+
- **HTTP Client:** HTTPX (async)
- **Document Processing:** pdfplumber, python-docx, beautifulsoup4
- **Background Jobs:** Celery 5.4+
- **Message Queue:** RabbitMQ

**Indexing Pipeline:**
```
┌────────────────────────────────────────────────────────────┐
│              Indexing Service Pipeline                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Connector Event → RabbitMQ                               │
│       ↓                                                    │
│  ┌─────────────────────────────┐                          │
│  │ 1. Event Consumer            │                          │
│  │    • Consume from queue      │                          │
│  │    • Validate event          │                          │
│  │    • Deduplication check     │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  ┌─────────────────────────────┐                          │
│  │ 2. Content Extraction        │                          │
│  │    • Download file (if URL)  │                          │
│  │    • Extract text            │                          │
│  │    • Handle formats (PDF,    │                          │
│  │      DOCX, HTML, etc.)       │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  ┌─────────────────────────────┐                          │
│  │ 3. Text Processing           │                          │
│  │    • Clean & normalize       │                          │
│  │    • Language detection      │                          │
│  │    • Metadata extraction     │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  ┌─────────────────────────────┐                          │
│  │ 4. Semantic Chunking         │                          │
│  │    • Chunk size: 512 tokens  │                          │
│  │    • Overlap: 50 tokens      │                          │
│  │    • Preserve context        │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  ┌─────────────────────────────┐                          │
│  │ 5. Embedding Generation      │                          │
│  │    • Batch processing        │                          │
│  │    • OpenAI API call         │                          │
│  │    • 3072-dim vectors        │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  ┌─────────────────────────────┐                          │
│  │ 6. Database Storage          │                          │
│  │    • Store document          │                          │
│  │    • Store chunks            │                          │
│  │    • Store embeddings        │                          │
│  │    • Update indexes          │                          │
│  └─────────────┬────────────────┘                          │
│                ↓                                           │
│  ┌─────────────────────────────┐                          │
│  │ 7. Post-Processing           │                          │
│  │    • Update sync status      │                          │
│  │    • Send notifications      │                          │
│  │    • Trigger analytics       │                          │
│  └─────────────────────────────┘                          │
└────────────────────────────────────────────────────────────┘
```

**Chunking Strategy:**
```python
from dataclasses import dataclass
from typing import list

@dataclass
class Chunk:
    content: str
    index: int
    token_count: int
    start_char: int
    end_char: int

def semantic_chunking(
    text: str,
    chunk_size: int = 512,
    overlap: int = 50
) -> list[Chunk]:
    """
    Semantic chunking that preserves paragraph boundaries
    and maintains context with overlapping windows
    """
    chunks = []
    tokens = tokenize(text)
    
    start_idx = 0
    chunk_idx = 0
    
    while start_idx < len(tokens):
        end_idx = min(start_idx + chunk_size, len(tokens))
        
        # Extend to sentence boundary if possible
        if end_idx < len(tokens):
            end_idx = find_sentence_boundary(tokens, end_idx)
        
        chunk_tokens = tokens[start_idx:end_idx]
        chunk_text = detokenize(chunk_tokens)
        
        chunks.append(Chunk(
            content=chunk_text,
            index=chunk_idx,
            token_count=len(chunk_tokens),
            start_char=get_char_position(tokens, start_idx),
            end_char=get_char_position(tokens, end_idx)
        ))
        
        # Move forward with overlap
        start_idx = end_idx - overlap
        chunk_idx += 1
    
    return chunks
```

**Performance Targets:**
- Simple document (text): < 500ms
- Complex document (PDF): < 2s
- Throughput: 100 documents/sec
- Queue processing delay: < 30s

---

### **5. Connector Hub (Golang)**

**Responsibilities:**
- Orchestrate all data source connectors
- Manage connector lifecycle
- Handle OAuth flows
- Rate limit API calls
- Retry logic and error handling
- Webhook server for real-time updates

**Technology Stack:**
- **Language:** Golang 1.22+
- **Connectors:** 25+ microservices
- **Message Queue:** RabbitMQ client
- **SDKs:** slack-go, go-github, google-api-go-client, aws-sdk-go-v2

**Connector Architecture:**
```
┌────────────────────────────────────────────────────────────┐
│                  Connector Hub                             │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │         Connector Manager                        │    │
│  │  • Lifecycle management                          │    │
│  │  • Health monitoring                             │    │
│  │  • Error recovery                                │    │
│  └────────────────┬─────────────────────────────────┘    │
│                   │                                        │
│         ┌─────────┼─────────┐                             │
│         │         │         │                             │
│  ┌──────▼───┐ ┌──▼──────┐ ┌▼───────────┐                │
│  │ Sync     │ │ Webhook │ │ Rate       │                │
│  │ Manager  │ │ Server  │ │ Limiter    │                │
│  └──────┬───┘ └──┬──────┘ └┬───────────┘                │
│         │        │         │                             │
│         └────────┼─────────┘                             │
│                  │                                        │
│  ┌───────────────▼────────────────────────────────┐     │
│  │          Individual Connectors                 │     │
│  ├─────────────────────────────────────────────────┤     │
│  │                                                 │     │
│  │  ┌──────┐  ┌──────┐  ┌───────┐  ┌───────┐    │     │
│  │  │Slack │  │ Jira │  │ Gmail │  │  S3   │    │     │
│  │  └──────┘  └──────┘  └───────┘  └───────┘    │     │
│  │                                                 │     │
│  │  ┌──────┐  ┌──────┐  ┌───────┐  ┌───────┐    │     │
│  │  │GitHub│  │ Teams│  │Conflue│  │Notion │    │     │
│  │  └──────┘  └──────┘  └───────┘  └───────┘    │     │
│  │                                                 │     │
│  │  ... 17 more connectors ...                    │     │
│  └─────────────────────────────────────────────────┘     │
│                  │                                        │
│  ┌───────────────▼────────────────┐                      │
│  │      RabbitMQ Publisher        │                      │
│  │   (sends events to indexing)   │                      │
│  └────────────────────────────────┘                      │
└────────────────────────────────────────────────────────────┘
```

**Connector Interface:**
```go
// Common interface for all connectors
type Connector interface {
    // Initialize connector with user credentials
    Initialize(config ConnectorConfig) error
    
    // Start full sync (initial import)
    FullSync(ctx context.Context) error
    
    // Start incremental sync (updates only)
    IncrementalSync(ctx context.Context, since time.Time) error
    
    // Start real-time sync (webhooks/websockets)
    RealtimeSync(ctx context.Context) error
    
    // Health check
    HealthCheck(ctx context.Context) error
    
    // Get sync status
    GetStatus() ConnectorStatus
    
    // Stop connector
    Stop() error
}

type ConnectorConfig struct {
    UserID      string
    SourceID    string
    Credentials map[string]string
    Settings    map[string]interface{}
}

type ConnectorStatus struct {
    State           string    // "idle", "syncing", "error"
    LastSync        time.Time
    DocumentsS