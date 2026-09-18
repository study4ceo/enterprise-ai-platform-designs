# Text-to-SQL Query Generator - Detailed Architecture Specification

**Document Date:** June 18, 2026  
**Version:** 1.0  
**Status:** Architecture Design  
**Tech Stack:** Golang + Python + Next.js 16

---

## 📐 System Architecture Overview

### **High-Level Architecture Diagram**

```
┌──────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Next.js 16 Application                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │  │
│  │  │ Query    │  │ Schema   │  │ Results  │  │   History    │ │  │
│  │  │ Builder  │  │ Explorer │  │ Viewer   │  │   Manager    │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘ │  │
│  │                                                               │  │
│  │  Monaco Editor | React Flow | Recharts | AG Grid            │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                          HTTPS/REST
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                      API GATEWAY LAYER                               │
│                     (Golang + Fiber 2.x)                             │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │     Auth     │  │     Rate     │  │   Request    │             │
│  │  Middleware  │  │   Limiting   │  │   Routing    │             │
│  │   (Clerk)    │  │   (Unkey)    │  │  (Fiber)     │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              Load Balancer (Weighted Round Robin)             │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────┬───────────────────┬───────────────────┬──────────────────┘
           │                   │                   │
         gRPC                gRPC                gRPC
           │                   │                   │
┌──────────▼────────┐ ┌────────▼────────┐ ┌───────▼─────────┐
│ SQL Generator     │ │  Executor       │ │   Schema        │
│   Service         │ │  Service        │ │   Service       │
│   (Python)        │ │  (Golang)       │ │   (Golang)      │
│  FastAPI +        │ │  Native Go      │ │   Native Go     │
│  LangChain        │ │  + pgx/mysql    │ │                 │
│                   │ │                 │ │                  │
│ ┌───────────────┐ │ │ ┌─────────────┐ │ │ ┌──────────────┐│
│ │ GPT-5.5       │ │ │ │ Connection  │ │ │ │  Introspect  ││
│ │ Claude 4.8    │ │ │ │ Pool Mgr    │ │ │ │  Analyzer    ││
│ │ RAG Engine    │ │ │ │ Query Exec  │ │ │ │  Cache Mgr   ││
│ └───────────────┘ │ │ └─────────────┘ │ │ └──────────────┘│
└───────────────────┘ └─────────────────┘ └──────────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
┌───────────▼──────────┐          ┌─────────────▼──────────┐
│   Data Layer         │          │   AI Models Layer      │
│                      │          │                        │
│ ┌──────────────────┐ │          │ ┌──────────────────┐  │
│ │   PostgreSQL     │ │          │ │   GPT-5.5        │  │
│ │  (Metadata DB)   │ │          │ │   (OpenAI)       │  │
│ └──────────────────┘ │          │ └──────────────────┘  │
│ ┌──────────────────┐ │          │ ┌──────────────────┐  │
│ │     Redis        │ │          │ │ Claude Opus 4.8  │  │
│ │  (Cache Layer)   │ │          │ │  (Anthropic)     │  │
│ └──────────────────┘ │          │ └──────────────────┘  │
│ ┌──────────────────┐ │          └────────────────────────┘
│ │ Upstash Vector   │ │
│ │  (RAG Storage)   │ │          ┌────────────────────────┐
│ └──────────────────┘ │          │  User Databases        │
└──────────────────────┘          │  (External)            │
                                  │                        │
                                  │ ┌──────────────────┐   │
                                  │ │   PostgreSQL     │   │
                                  │ │   MySQL          │   │
                                  │ │   SQL Server     │   │
                                  │ │   SQLite         │   │
                                  │ └──────────────────┘   │
                                  └────────────────────────┘
```

---

## 🔄 Data Flow Diagrams

### **1. Text-to-SQL Generation Flow**

```
User          Frontend       API Gateway    Generator       RAG Engine      AI Model      Database
 │               │                │             │               │              │            │
 │  Enter Query  │                │             │               │              │            │
 ├──────────────>│                │             │               │              │            │
 │               │  POST /generate│             │               │              │            │
 │               ├───────────────>│             │               │              │            │
 │               │                │  Auth Check │               │              │            │
 │               │                ├────────┐    │               │              │            │
 │               │                │        │    │               │              │            │
 │               │                │<───────┘    │               │              │            │
 │               │                │  Get Schema │               │              │            │
 │               │                ├─────────────────────────────────────────────────────────>│
 │               │                │             │               │              │  Schema    │
 │               │                │<─────────────────────────────────────────────────────────┤
 │               │                │  Fetch Examples             │              │            │
 │               │                ├──────────────────────────>│              │            │
 │               │                │             │   Similar Queries            │            │
 │               │                │<──────────────────────────┤              │            │
 │               │                │  Generate SQL              │              │            │
 │               │                ├────────────>│               │              │            │
 │               │                │             │  Build Prompt │              │            │
 │               │                │             ├───────────────────────────>│            │
 │               │                │             │               │   LLM Call   │            │
 │               │                │             │               │──────────────>│            │
 │               │                │             │               │   SQL Result │            │
 │               │                │             │<───────────────────────────────┤            │
 │               │                │  Validate SQL              │              │            │
 │               │                │<────────────┤               │              │            │
 │               │                │  Store Example             │              │            │
 │               │                ├──────────────────────────>│              │            │
 │               │  SQL + Metadata│             │               │              │            │
 │               │<───────────────┤             │               │              │            │
 │  Generated SQL│                │             │               │              │            │
 │<──────────────┤                │             │               │              │            │
```

### **2. Query Execution Flow**

```
User          Frontend       API Gateway    Executor        User DB        Metadata DB
 │               │                │            │               │                │
 │  Execute SQL  │                │            │               │                │
 ├──────────────>│                │            │               │                │
 │               │  POST /execute │            │               │                │
 │               ├───────────────>│            │               │                │
 │               │                │  Validate  │               │                │
 │               │                ├───────┐    │               │                │
 │               │                │       │    │               │                │
 │               │                │<──────┘    │               │                │
 │               │                │  Get Conn  │               │                │
 │               │                ├───────────>│               │                │
 │               │                │            │  EXPLAIN Query│                │
 │               │                │            ├──────────────>│                │
 │               │                │            │  Cost Estimate│                │
 │               │                │            │<──────────────┤                │
 │               │                │  Check OK? │               │                │
 │               │                │<───────────┤               │                │
 │               │                │            │  Execute SQL  │                │
 │               │                │            ├──────────────>│                │
 │               │                │            │    Results    │                │
 │               │                │            │<──────────────┤                │
 │               │                │  Log Query │               │                │
 │               │                ├─────────────────────────────────────────────>│
 │               │  Results       │            │               │                │
 │               │<───────────────┤            │               │                │
 │  Display Data │                │            │               │                │
 │<──────────────┤                │            │               │                │
```

---

## 🏛️ Service Architecture Details

### **SQL Generator Service (Python)**

```python
# Architecture Components

from fastapi import FastAPI
from langchain import OpenAI, Anthropic
from vanna.openai import OpenAI_Chat

class SQLGeneratorService:
    def __init__(self):
        self.gpt_client = OpenAI(model="gpt-5.5")
        self.claude_client = Anthropic(model="claude-opus-4.8")
        self.vanna = OpenAI_Chat()
        self.vector_store = UpstashVector()
        self.cache = Redis()
```

**Continue in next message...**
