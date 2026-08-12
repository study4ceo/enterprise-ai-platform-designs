# 📚 RAG Evaluation - Implementation Plan

## 🎯 Why Start with RAG?

RAG (Retrieval-Augmented Generation) evaluation is the **highest value** addition because:

1. **Most Requested**: 80% of production LLM apps use RAG
2. **Clear Metrics**: Well-defined evaluation criteria
3. **Builds on Existing**: Uses current LLM evaluation infrastructure
4. **Immediate Value**: Helps teams improve RAG quality today
5. **Market Gap**: Few good RAG evaluation tools exist

**Time to MVP**: 1 week for basic metrics, 2-3 weeks for complete

---

## 📊 RAG Evaluation Metrics (What to Measure)

### Core Metrics (Week 1 - MVP)

```python
1. Faithfulness (Most Critical!)
   - Is the answer grounded in retrieved context?
   - Prevents hallucinations
   - Method: Check if claims are supported by docs
   - Tool: Use Groq for fast evaluation
   
2. Answer Relevance
   - Does the answer address the question?
   - Checks if response is on-topic
   - Method: Semantic similarity + LLM judge
   
3. Context Relevance
   - Are retrieved docs relevant to query?
   - Measures retrieval quality
   - Method: Check doc relevance to query
   
4. Correctness (if ground truth available)
   - Is the answer factually correct?
   - Gold standard metric
   - Method: Compare with reference answer
```

### Advanced Metrics (Week 2-3)

```python
5. Context Recall
   - Did retrieval find all relevant docs?
   - Measures completeness
   
6. Context Precision
   - Are top-k results most relevant?
   - Measures ranking quality
   
7. Hallucination Rate
   - Information not in context
   - Critical for trust
   
8. Answer Completeness
   - Does it fully answer the question?
   
9. Citation Accuracy
   - Are source citations correct?
   
10. Noise Robustness
    - Performance with irrelevant docs
```

---

## 🏗️ Architecture Design

### New Components to Add

```
Current System:
├── LLM Workers ✅
├── Metrics Service ✅
└── Dashboard ✅

Add for RAG:
├── rag-evaluator/          # 🆕 New service
│   ├── main.py             # RAG evaluation API
│   ├── faithfulness.py     # Faithfulness checker
│   ├── relevance.py        # Relevance scorer
│   ├── hallucination.py    # Hallucination detector
│   └── rag_metrics.py      # All metrics
│
├── dashboard/app/rag/      # 🆕 New UI
│   ├── page.tsx            # RAG evaluation page
│   └── components/         # RAG-specific components
│
└── shared/models.py        # 🆕 Add RAG models
```

---

## 📝 Database Schema

```sql
-- RAG Evaluations Table
CREATE TABLE rag_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    
    -- Query
    query_text TEXT NOT NULL,
    query_type VARCHAR(50),  -- "factoid", "multi_hop", "comparison"
    
    -- Retrieved Context
    num_docs_retrieved INTEGER,
    retrieval_method VARCHAR(100),  -- "vector_search", "hybrid", "bm25"
    retrieval_params JSONB,
    
    -- Generated Answer
    generated_answer TEXT NOT NULL,
    reference_answer TEXT,  -- Ground truth (if available)
    llm_model VARCHAR(100),
    
    -- Core Metrics
    faithfulness_score FLOAT,
    answer_relevance_score FLOAT,
    context_relevance_score FLOAT,
    correctness_score FLOAT,
    
    -- Advanced Metrics
    context_recall FLOAT,
    context_precision FLOAT,
    hallucination_rate FLOAT,
    answer_completeness FLOAT,
    citation_accuracy FLOAT,
    
    -- Performance
    retrieval_time_ms INTEGER,
    generation_time_ms INTEGER,
    total_time_ms INTEGER,
    total_cost_usd DECIMAL(10, 6),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Retrieved Documents Table
CREATE TABLE retrieved_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evaluation_id UUID REFERENCES rag_evaluations(id) ON DELETE CASCADE,
    
    doc_id VARCHAR(255),
    content TEXT NOT NULL,
    similarity_score FLOAT,
    rank INTEGER,
    
    -- Evaluation
    is_relevant BOOLEAN,  -- Manual or automated relevance judgment
    relevance_score FLOAT,  -- Automated relevance score (0-1)
    
    -- Source
    source_url TEXT,
    source_metadata JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- RAG Test Sets Table
CREATE TABLE rag_test_sets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Configuration
    domain VARCHAR(100),  -- "general", "medical", "legal", etc.
    difficulty VARCHAR(50),  -- "easy", "medium", "hard"
    num_questions INTEGER,
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    is_public BOOLEAN DEFAULT FALSE
);

-- RAG Test Questions Table
CREATE TABLE rag_test_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_set_id UUID REFERENCES rag_test_sets(id) ON DELETE CASCADE,
    
    question TEXT NOT NULL,
    expected_answer TEXT,
    relevant_doc_ids TEXT[],  -- IDs of docs that should be retrieved
    
    difficulty VARCHAR(50),
    requires_multi_hop BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_rag_eval_user ON rag_evaluations(user_id);
CREATE INDEX idx_rag_eval_created ON rag_evaluations(created_at);
CREATE INDEX idx_rag_eval_model ON rag_evaluations(llm_model);
CREATE INDEX idx_retrieved_docs_eval ON retrieved_documents(evaluation_id);
CREATE INDEX idx_test_questions_set ON rag_test_questions(test_set_id);
```

---

## 🔧 Implementation (Step-by-Step)

### Week 1: MVP (Core Metrics)

#### Day 1-2: Data Models & API

```python
# services/shared/models.py - Add RAG models

class RAGEvaluationCreate(BaseModel):
    query_text: str
    retrieved_docs: List[RetrievedDocInput]
    generated_answer: str
    reference_answer: Optional[str] = None
    llm_model: str
    retrieval_method: str = "vector_search"

class RetrievedDocInput(BaseModel):
    doc_id: str
    content: str
    similarity_score: float
    rank: int

class RAGEvaluationResponse(BaseModel):
    id: UUID
    query_text: str
    generated_answer: str
    
    # Core Metrics
    faithfulness_score: float
    answer_relevance_score: float
    context_relevance_score: float
    correctness_score: Optional[float]
    
    # Performance
    total_time_ms: int
    total_cost_usd: float
    
    created_at: datetime
```

#### Day 3-4: Faithfulness Checker (Most Important!)

```python
# services/rag-evaluator/faithfulness.py

from groq import Groq
import asyncio

groq_client = Groq(api_key=settings.GROQ_API_KEY)

async def check_faithfulness(answer: str, contexts: List[str]) -> float:
    """
    Check if answer claims are supported by context
    Uses Groq Llama 3.1 70B for fast evaluation
    """
    
    # Step 1: Extract claims from answer
    claims = await extract_claims(answer)
    
    # Step 2: Check each claim against context
    supported_claims = 0
    
    for claim in claims:
        is_supported = await verify_claim(claim, contexts)
        if is_supported:
            supported_claims += 1
    
    # Faithfulness = supported claims / total claims
    faithfulness = supported_claims / len(claims) if claims else 1.0
    
    return faithfulness

async def extract_claims(answer: str) -> List[str]:
    """Extract factual claims from answer using LLM"""
    
    prompt = f"""Extract all factual claims from this answer as a numbered list.
Only include statements that can be verified as true or false.

Answer: {answer}

Claims (one per line):"""
    
    response = groq_client.chat.completions.create(
        model="llama-3.1-70b-versatile",  # Fast and accurate!
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    claims_text = response.choices[0].message.content
    claims = [c.strip() for c in claims_text.split('\n') if c.strip()]
    
    return claims

async def verify_claim(claim: str, contexts: List[str]) -> bool:
    """Check if claim is supported by any context"""
    
    context_text = "\n\n".join(contexts)
    
    prompt = f"""Context: {context_text}

Claim: {claim}

Is this claim directly supported by the context above?
Answer with only "YES" or "NO".

Answer:"""
    
    response = groq_client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    verdict = response.choices[0].message.content.strip().upper()
    return "YES" in verdict
```

#### Day 5: Answer & Context Relevance

```python
# services/rag-evaluator/relevance.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load embedding model once
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast & good

async def check_answer_relevance(query: str, answer: str) -> float:
    """Check if answer is relevant to query"""
    
    # Method 1: Embedding similarity (fast)
    query_emb = embedding_model.encode([query])
    answer_emb = embedding_model.encode([answer])
    similarity = cosine_similarity(query_emb, answer_emb)[0][0]
    
    # Method 2: LLM judge (more accurate)
    llm_score = await llm_relevance_judge(query, answer)
    
    # Combine both (weighted average)
    final_score = 0.4 * similarity + 0.6 * llm_score
    
    return float(final_score)

async def llm_relevance_judge(query: str, answer: str) -> float:
    """Use LLM to judge relevance"""
    
    prompt = f"""Query: {query}

Answer: {answer}

Does the answer directly address the query?
Rate from 1-5 where:
1 = Completely irrelevant
2 = Somewhat related but doesn't answer
3 = Partially answers
4 = Good answer
5 = Perfect answer

Rating (just the number):"""
    
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Fast enough for this
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    rating_text = response.choices[0].message.content.strip()
    try:
        rating = int(rating_text)
        return rating / 5.0  # Normalize to 0-1
    except:
        return 0.5  # Default if parsing fails

async def check_context_relevance(query: str, contexts: List[str]) -> float:
    """Check if retrieved contexts are relevant to query"""
    
    relevant_count = 0
    
    for context in contexts:
        is_relevant = await is_context_relevant(query, context)
        if is_relevant:
            relevant_count += 1
    
    relevance = relevant_count / len(contexts) if contexts else 0.0
    
    return relevance

async def is_context_relevant(query: str, context: str) -> bool:
    """Check if single context is relevant to query"""
    
    # Use embedding similarity threshold
    query_emb = embedding_model.encode([query])
    context_emb = embedding_model.encode([context])
    similarity = cosine_similarity(query_emb, context_emb)[0][0]
    
    # Threshold at 0.3 (tunable)
    return similarity > 0.3
```

#### Day 6-7: API & Integration

```python
# services/rag-evaluator/main.py

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import sys
sys.path.append('../shared')

from shared.database import DatabaseManager, RAGEvaluation
from shared.models import RAGEvaluationCreate, RAGEvaluationResponse
from faithfulness import check_faithfulness
from relevance import check_answer_relevance, check_context_relevance
from config import settings

app = FastAPI(title="RAG Evaluator", version="1.0.0")
db_manager = DatabaseManager(settings.DATABASE_URL)

@app.post("/api/v1/rag/evaluate", response_model=RAGEvaluationResponse)
async def evaluate_rag(
    request: RAGEvaluationCreate,
    session: AsyncSession = Depends(get_session)
):
    """Evaluate a RAG response"""
    
    start_time = time.time()
    
    # Extract contexts
    contexts = [doc.content for doc in request.retrieved_docs]
    
    # Calculate metrics in parallel for speed
    faithfulness, answer_rel, context_rel = await asyncio.gather(
        check_faithfulness(request.generated_answer, contexts),
        check_answer_relevance(request.query_text, request.generated_answer),
        check_context_relevance(request.query_text, contexts)
    )
    
    # Calculate correctness if reference answer provided
    correctness = None
    if request.reference_answer:
        correctness = await check_correctness(
            request.generated_answer,
            request.reference_answer
        )
    
    total_time_ms = int((time.time() - start_time) * 1000)
    
    # Store in database
    evaluation = RAGEvaluation(
        user_id=current_user.id,
        query_text=request.query_text,
        generated_answer=request.generated_answer,
        reference_answer=request.reference_answer,
        llm_model=request.llm_model,
        num_docs_retrieved=len(request.retrieved_docs),
        retrieval_method=request.retrieval_method,
        faithfulness_score=faithfulness,
        answer_relevance_score=answer_rel,
        context_relevance_score=context_rel,
        correctness_score=correctness,
        total_time_ms=total_time_ms,
        total_cost_usd=0.01  # Estimate based on Groq usage
    )
    
    session.add(evaluation)
    await session.commit()
    
    # Store retrieved docs
    for doc in request.retrieved_docs:
        retrieved_doc = RetrievedDocument(
            evaluation_id=evaluation.id,
            doc_id=doc.doc_id,
            content=doc.content,
            similarity_score=doc.similarity_score,
            rank=doc.rank
        )
        session.add(retrieved_doc)
    
    await session.commit()
    
    return RAGEvaluationResponse(
        id=evaluation.id,
        query_text=evaluation.query_text,
        generated_answer=evaluation.generated_answer,
        faithfulness_score=faithfulness,
        answer_relevance_score=answer_rel,
        context_relevance_score=context_rel,
        correctness_score=correctness,
        total_time_ms=total_time_ms,
        total_cost_usd=0.01,
        created_at=evaluation.created_at
    )

@app.get("/api/v1/rag/evaluations")
async def list_evaluations(
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session)
):
    """List RAG evaluations"""
    
    query = select(RAGEvaluation).offset(skip).limit(limit).order_by(
        RAGEvaluation.created_at.desc()
    )
    result = await session.execute(query)
    evaluations = result.scalars().all()
    
    return {"evaluations": evaluations}

@app.get("/api/v1/rag/stats")
async def get_rag_stats(session: AsyncSession = Depends(get_session)):
    """Get aggregate RAG statistics"""
    
    stats_query = select(
        func.count(RAGEvaluation.id).label('total'),
        func.avg(RAGEvaluation.faithfulness_score).label('avg_faithfulness'),
        func.avg(RAGEvaluation.answer_relevance_score).label('avg_relevance'),
        func.avg(RAGEvaluation.context_relevance_score).label('avg_context_rel')
    )
    
    result = await session.execute(stats_query)
    stats = result.one()
    
    return {
        "total_evaluations": stats.total,
        "avg_faithfulness": float(stats.avg_faithfulness or 0),
        "avg_relevance": float(stats.avg_relevance or 0),
        "avg_context_relevance": float(stats.avg_context_rel or 0)
    }
```

---

## 🎨 Dashboard UI (Week 1)

### RAG Evaluation Page

```typescript
// services/dashboard/app/rag/page.tsx

'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { api } from '@/lib/api'

export default function RAGEvalPage() {
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState('')
  const [contexts, setContexts] = useState([''])
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleEvaluate = async () => {
    setLoading(true)
    try {
      const response = await api.evaluateRAG({
        query_text: query,
        generated_answer: answer,
        retrieved_docs: contexts.map((content, idx) => ({
          doc_id: `doc_${idx}`,
          content,
          similarity_score: 0.9 - idx * 0.1,
          rank: idx + 1
        })),
        llm_model: 'llama-3.1-70b-versatile',
        retrieval_method: 'vector_search'
      })
      setResult(response)
    } catch (error) {
      console.error('Evaluation failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">RAG Evaluation</h1>
      
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle>Evaluate RAG Response</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Query */}
          <div>
            <label className="block text-sm font-medium mb-2">Query</label>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full p-2 border rounded"
              placeholder="What is the capital of France?"
            />
          </div>

          {/* Generated Answer */}
          <div>
            <label className="block text-sm font-medium mb-2">Generated Answer</label>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              className="w-full p-2 border rounded"
              rows={3}
              placeholder="The capital of France is Paris..."
            />
          </div>

          {/* Retrieved Contexts */}
          <div>
            <label className="block text-sm font-medium mb-2">Retrieved Contexts</label>
            {contexts.map((context, idx) => (
              <textarea
                key={idx}
                value={context}
                onChange={(e) => {
                  const newContexts = [...contexts]
                  newContexts[idx] = e.target.value
                  setContexts(newContexts)
                }}
                className="w-full p-2 border rounded mb-2"
                rows={2}
                placeholder={`Context ${idx + 1}...`}
              />
            ))}
            <Button
              variant="outline"
              onClick={() => setContexts([...contexts, ''])}
            >
              + Add Context
            </Button>
          </div>

          <Button onClick={handleEvaluate} disabled={loading}>
            {loading ? 'Evaluating...' : 'Evaluate'}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Evaluation Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <MetricCard
                title="Faithfulness"
                score={result.faithfulness_score}
                description="Answer grounded in context"
              />
              <MetricCard
                title="Answer Relevance"
                score={result.answer_relevance_score}
                description="Addresses the query"
              />
              <MetricCard
                title="Context Relevance"
                score={result.context_relevance_score}
                description="Retrieved docs relevant"
              />
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

const MetricCard = ({ title, score, description }: any) => (
  <div className="p-4 bg-gray-50 rounded-lg">
    <h3 className="font-medium text-gray-900">{title}</h3>
    <div className="text-3xl font-bold mt-2">
      {(score * 100).toFixed(0)}%
    </div>
    <p className="text-xs text-gray-500 mt-1">{description}</p>
    <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
      <div
        className={`h-2 rounded-full ${
          score > 0.8 ? 'bg-green-600' :
          score > 0.6 ? 'bg-yellow-600' :
          'bg-red-600'
        }`}
        style={{ width: `${score * 100}%` }}
      />
    </div>
  </div>
)
```

---

## 📦 Docker Configuration

```yaml
# docker-compose.yml - Add RAG evaluator

  rag-evaluator:
    build: ./services/rag-evaluator
    container_name: llm-eval-rag-evaluator
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/llm_evaluation
      - REDIS_URL=redis://redis:6379
      - GROQ_API_KEY=${GROQ_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - postgres
      - redis
    ports:
      - "8004:8004"
    volumes:
      - ./services/rag-evaluator:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8004
```

---

## 🧪 Testing

### Sample Test Cases

```python
# Test Case 1: Perfect RAG Response
test_case_1 = {
    "query": "What is the capital of France?",
    "contexts": [
        "Paris is the capital and largest city of France.",
        "France is a country in Western Europe."
    ],
    "answer": "The capital of France is Paris.",
    "expected_faithfulness": 1.0,  # Perfect
    "expected_relevance": 1.0      # Perfect
}

# Test Case 2: Hallucination
test_case_2 = {
    "query": "What is the capital of France?",
    "contexts": [
        "France is a country in Western Europe."
    ],
    "answer": "The capital of France is Paris, which has 10 million people.",
    "expected_faithfulness": 0.5,  # Population not in context
    "expected_relevance": 0.9      # Still relevant
}

# Test Case 3: Irrelevant Answer
test_case_3 = {
    "query": "What is the capital of France?",
    "contexts": [
        "Paris is the capital of France."
    ],
    "answer": "France is known for its wine and cheese.",
    "expected_faithfulness": 1.0,  # Technically grounded
    "expected_relevance": 0.2      # Doesn't answer question
}
```

---

## 🚀 Deployment

### Week 1 Deliverables

```
✅ RAG evaluation API (3 core metrics)
✅ Faithfulness checker (using Groq)
✅ Answer & context relevance
✅ Database schema
✅ Basic dashboard UI
✅ Docker configuration
✅ API documentation
✅ Test cases
```

### Success Metrics

```
Performance:
- Evaluation time: < 5 seconds per query
- Cost: ~$0.01 per evaluation (using Groq!)
- Accuracy: 85%+ correlation with human judgment

Usage:
- 10+ evaluations/day (first week)
- 100+ evaluations/day (first month)
```

---

## 📈 Future Enhancements (Week 2-3)

### Week 2: Advanced Metrics
- Context Recall
- Context Precision
- Hallucination Rate (detailed)
- Citation Accuracy

### Week 3: Production Features
- Batch evaluation
- Test set management
- A/B testing for RAG configs
- Trend analysis dashboard

---

**Implementation Status**: Ready to start  
**Time to MVP**: 1 week  
**Value**: Immediate RAG quality improvement  
**Cost**: Minimal (Groq for evaluation!)  

---

*Let's build the best RAG evaluation tool!* 🚀
