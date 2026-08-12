# LLM Evaluation at Scale - Design Document

## Overview

A high-performance, scalable system for evaluating multiple LLM models concurrently using modern metrics and best practices.

## Goals

1. **Evaluate multiple LLMs** (Gemini, GPT, Claude, Llama) on diverse tasks
2. **Scale efficiently** - Handle 1000+ evaluations concurrently
3. **Multiple metrics** - BLEU, ROUGE, BERTScore, Human-as-Judge, LLM-as-Judge
4. **Real-time monitoring** - Track progress, costs, and performance
5. **Cost optimization** - Minimize API costs through batching and caching
6. **Results analysis** - Compare models, generate reports, visualizations

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Evaluation Orchestrator                  │
│                    (Python + asyncio)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│   Gemini     │ │    GPT     │ │   Claude   │
│   Workers    │ │  Workers   │ │  Workers   │
│ (errgroup)   │ │(errgroup)  │ │(errgroup)  │
└───────┬──────┘ └─────┬──────┘ └─────┬──────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │      Metrics Calculator        │
        │  - BLEU, ROUGE, BERTScore     │
        │  - LLM-as-Judge               │
        └───────────────┬───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │       Results Storage          │
        │  - SQLite (local)              │
        │  - JSON exports                │
        │  - CSV reports                 │
        └────────────────────────────────┘
```

---

## System Components

### 1. Evaluation Orchestrator
**File:** `orchestrator.py`

**Responsibilities:**
- Load test dataset (prompts, references)
- Distribute work across model workers
- Manage concurrency limits per model
- Track progress and costs
- Handle errors and retries

**Key Features:**
- Asyncio-based for high concurrency
- Rate limiting per model (avoid API limits)
- Exponential backoff for retries
- Progress tracking with tqdm
- Cost estimation and tracking

**Pattern:**
```python
async def orchestrate_evaluation(
    dataset: List[TestCase],
    models: List[ModelConfig],
    metrics: List[str]
) -> EvaluationResults:
    # Use asyncio.gather for concurrent execution
    # errgroup pattern for error handling
    # Rate limiting per model
```

---

### 2. Model Workers
**Files:** `models/gemini_worker.py`, `models/gpt_worker.py`, `models/claude_worker.py`

**Responsibilities:**
- API integration for each LLM provider
- Request/response handling
- Token counting and cost tracking
- Caching responses (avoid duplicate API calls)
- Error handling and retries

**Gemini Worker Example:**
```python
import google.generativeai as genai
from typing import List, Dict
import asyncio

class GeminiWorker:
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.rate_limiter = RateLimiter(requests_per_minute=60)
        
    async def generate(self, prompt: str) -> Dict:
        await self.rate_limiter.acquire()
        
        response = await self.model.generate_content_async(prompt)
        
        return {
            "text": response.text,
            "tokens": self.count_tokens(response),
            "cost": self.calculate_cost(response)
        }
```

---

### 3. Metrics Calculator
**File:** `metrics/calculator.py`

**Responsibilities:**
- Calculate automatic metrics (BLEU, ROUGE, BERTScore)
- Implement LLM-as-Judge pattern
- Support custom evaluation criteria
- Parallel metric calculation
- Result aggregation

**Supported Metrics:**
- **BLEU** - Machine translation quality
- **ROUGE** - Summarization quality
- **BERTScore** - Semantic similarity
- **Exact Match** - Binary correctness
- **LLM-as-Judge** - Use Gemini to evaluate quality

**Interface:**
```python
class MetricsCalculator:
    async def calculate_all(
        self,
        candidate: str,
        reference: str,
        metrics: List[str]
    ) -> Dict[str, float]:
        # Calculate all requested metrics in parallel
```

---

### 4. Dataset Manager
**File:** `dataset/manager.py`

**Responsibilities:**
- Load datasets from various formats (JSON, CSV, JSONL)
- Support multiple dataset types (QA, summarization, translation)
- Stratified sampling for cost optimization
- Dataset validation

**Dataset Format:**
```json
{
  "test_cases": [
    {
      "id": "test_001",
      "category": "qa",
      "prompt": "What is the capital of France?",
      "reference": "Paris",
      "metadata": {
        "difficulty": "easy",
        "domain": "geography"
      }
    }
  ]
}
```

---

### 5. Results Storage
**Files:** `storage/sqlite_store.py`, `storage/exporter.py`

**Responsibilities:**
- Store evaluation results in SQLite
- Export to JSON, CSV, Markdown
- Query historical results
- Generate comparison reports

**Schema:**
```sql
CREATE TABLE evaluations (
    id TEXT PRIMARY KEY,
    model TEXT NOT NULL,
    test_case_id TEXT NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    reference TEXT,
    metrics JSON NOT NULL,
    tokens_used INTEGER,
    cost_usd REAL,
    latency_ms INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Technology Stack

### Core
- **Python 3.11+** - Modern async/await, performance
- **asyncio** - Concurrent execution
- **aiohttp** - Async HTTP requests

### LLM APIs
- **google-generativeai** - Gemini API
- **openai** - GPT models
- **anthropic** - Claude models (optional)

### Metrics
- **nltk** - BLEU score
- **rouge-score** - ROUGE metrics
- **bert-score** - BERTScore
- **sentence-transformers** - Embeddings

### Storage & Analysis
- **sqlite3** - Results database
- **pandas** - Data analysis
- **matplotlib/plotly** - Visualizations
- **rich** - Terminal UI

### Utilities
- **pydantic** - Data validation
- **python-dotenv** - Environment management
- **tqdm** - Progress bars
- **loguru** - Logging

---

## Concurrency Strategy

### Rate Limiting Per Model

```python
from asyncio import Semaphore
from collections import defaultdict

class RateLimiter:
    def __init__(self, requests_per_minute: int):
        self.rate = requests_per_minute
        self.semaphore = Semaphore(requests_per_minute)
        self.reset_interval = 60  # seconds
        
    async def acquire(self):
        await self.semaphore.acquire()
        # Auto-release after reset_interval
```

### Concurrent Evaluation Pattern

```python
import asyncio
from typing import List

async def evaluate_all_models(
    test_cases: List[TestCase],
    models: List[ModelWorker]
) -> List[Result]:
    
    # Create tasks for all model x test_case combinations
    tasks = []
    for model in models:
        for test_case in test_cases:
            task = evaluate_single(model, test_case)
            tasks.append(task)
    
    # Execute with concurrency limit
    semaphore = asyncio.Semaphore(50)  # Max 50 concurrent
    
    async def bounded_task(task):
        async with semaphore:
            return await task
    
    results = await asyncio.gather(
        *[bounded_task(t) for t in tasks],
        return_exceptions=True
    )
    
    return results
```

---

## Error Handling Strategy

### Retry Logic

```python
import asyncio
from functools import wraps

def async_retry(max_retries=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff_factor ** attempt
                    await asyncio.sleep(wait_time)
            
        return wrapper
    return decorator

@async_retry(max_retries=3)
async def call_api(prompt: str):
    # API call with automatic retry
    pass
```

### Error Categories

1. **Transient Errors** - Retry with backoff
   - Rate limits (429)
   - Timeouts
   - Network errors

2. **Permanent Errors** - Log and skip
   - Invalid API key (401)
   - Invalid request (400)
   - Content policy violation

3. **Critical Errors** - Stop evaluation
   - Out of quota
   - System errors

---

## Cost Optimization

### 1. Response Caching

```python
import hashlib
import json

class ResponseCache:
    def __init__(self, cache_file="cache.json"):
        self.cache = self.load_cache(cache_file)
        
    def get_key(self, model: str, prompt: str) -> str:
        return hashlib.md5(
            f"{model}:{prompt}".encode()
        ).hexdigest()
    
    def get(self, model: str, prompt: str):
        key = self.get_key(model, prompt)
        return self.cache.get(key)
    
    def set(self, model: str, prompt: str, response: dict):
        key = self.get_key(model, prompt)
        self.cache[key] = response
```

### 2. Stratified Sampling

```python
def sample_dataset(
    dataset: List[TestCase],
    sample_size: int,
    stratify_by: str = "difficulty"
) -> List[TestCase]:
    """
    Sample dataset while maintaining distribution
    of categories (e.g., easy/medium/hard)
    """
    from sklearn.model_selection import train_test_split
    # Implementation
```

### 3. Cost Tracking

```python
class CostTracker:
    PRICING = {
        "gemini-pro": {"input": 0.00025, "output": 0.0005},  # per 1K tokens
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
    }
    
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
