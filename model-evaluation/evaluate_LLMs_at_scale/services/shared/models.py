from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


# Auth schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# Job schemas
class JobCreate(BaseModel):
    name: str
    models: List[str] = Field(..., min_items=1)
    prompts: List[str] = Field(..., min_items=1)
    references: Optional[List[str]] = None
    metrics: List[str] = ["bleu", "rouge", "bertscore"]
    priority: int = Field(default=1, ge=1, le=3)
    metadata: Dict[str, Any] = {}


class JobResponse(BaseModel):
    id: UUID
    name: str
    status: JobStatus
    priority: int
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_cost_usd: float
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    page_size: int


# Task schemas
class TaskResponse(BaseModel):
    id: UUID
    job_id: UUID
    model: str
    prompt: str
    response: Optional[str]
    reference: Optional[str]
    status: TaskStatus
    retry_count: int
    error_message: Optional[str]
    tokens_used: Optional[int]
    cost_usd: Optional[float]
    latency_ms: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Metrics schemas
class MetricResult(BaseModel):
    metric_name: str
    score: float
    details: Optional[Dict[str, Any]] = None


class TaskMetrics(BaseModel):
    task_id: UUID
    metrics: List[MetricResult]
    overall_score: float


# Deployment Readiness schemas
class PerformanceMetrics(BaseModel):
    bertscore: float
    rouge_l: float
    exact_match: float
    perplexity: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    requests_per_sec: float


class BusinessMetrics(BaseModel):
    cost_per_query_usd: float
    monthly_cost_usd: float
    roi_percentage: float
    win_rate: float
    user_rating: float
    completion_rate: float


class SafetyMetrics(BaseModel):
    hallucination_rate: float
    toxicity_score: float
    bias_score: float
    pii_leakage: float
    refusal_rate: float
    error_rate: float
    factuality: float
    groundedness: float
    adversarial_pass_rate: float
    edge_case_handling: float
    consistency: float


class OperationalReadiness(BaseModel):
    prometheus_configured: bool
    dashboards_ready: bool
    alerts_configured: bool
    logs_configured: bool
    rollback_plan: bool
    deployment_strategy: bool
    ab_test_ready: bool
    api_docs: bool
    runbook: bool
    troubleshooting: bool


class DeploymentReadinessReport(BaseModel):
    model_name: str
    evaluated_at: datetime
    performance: PerformanceMetrics
    business: BusinessMetrics
    safety: SafetyMetrics
    operational: OperationalReadiness
    performance_score: float
    business_score: float
    safety_score: float
    operational_score: float
    overall_score: float
    deployment_ready: bool
    status: str  # APPROVED, CONDITIONAL, REJECTED
    critical_issues: List[str]
    warnings: List[str]
    recommendations: List[str]


# Worker message schemas
class EvaluationTaskMessage(BaseModel):
    task_id: UUID
    job_id: UUID
    model: str
    prompt: str
    reference: Optional[str]
    metrics: List[str]
    retry_count: int = 0


class MetricsCalculationMessage(BaseModel):
    task_id: UUID
    response: str
    reference: Optional[str]
    metrics: List[str]


# ========== RAG EVALUATION MODELS ==========

class RetrievedDocument(BaseModel):
    """A single retrieved document for RAG"""
    doc_id: str
    content: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    rank: int = Field(..., ge=1)
    metadata: Optional[Dict[str, Any]] = {}


class RAGEvaluationRequest(BaseModel):
    """Request to evaluate a RAG response"""
    query_text: str = Field(..., min_length=1)
    retrieved_docs: List[RetrievedDocument] = Field(..., min_items=1)
    generated_answer: str = Field(..., min_length=1)
    reference_answer: Optional[str] = None
    llm_model: str = "llama-3.1-70b-versatile"
    retrieval_method: str = "vector_search"
    metadata: Optional[Dict[str, Any]] = {}


class RAGEvaluationResponse(BaseModel):
    """Response from RAG evaluation"""
    evaluation_id: UUID
    query_text: str
    generated_answer: str
    reference_answer: Optional[str]
    num_retrieved_docs: int
    
    # Core metrics
    faithfulness_score: float = Field(..., ge=0.0, le=1.0)
    answer_relevance_score: float = Field(..., ge=0.0, le=1.0)
    context_relevance_score: float = Field(..., ge=0.0, le=1.0)
    context_precision_score: float = Field(..., ge=0.0, le=1.0)
    
    # Performance
    total_time_ms: int
    total_cost_usd: float
    
    timestamp: datetime
    
    class Config:
        from_attributes = True


class RAGEvaluationDetailed(RAGEvaluationResponse):
    """Detailed RAG evaluation with breakdowns"""
    faithfulness_detail: Dict[str, Any]
    answer_relevance_detail: Dict[str, Any]
    context_relevance_detail: Dict[str, Any]


class RAGEvaluationListResponse(BaseModel):
    """List of RAG evaluations with pagination"""
    evaluations: List[RAGEvaluationResponse]
    total: int
    skip: int
    limit: int


class RAGStatsResponse(BaseModel):
    """Aggregate RAG statistics"""
    total_evaluations: int
    avg_faithfulness: float
    avg_answer_relevance: float
    avg_context_relevance: float
    avg_evaluation_time_ms: int
    total_cost_usd: float


class RAGTestQuestion(BaseModel):
    """A test question for RAG evaluation"""
    question_id: UUID
    question: str
    expected_answer: str
    relevant_doc_ids: List[str]
    difficulty: str = "medium"  # easy, medium, hard
    requires_multi_hop: bool = False
    metadata: Optional[Dict[str, Any]] = {}


class RAGTestSet(BaseModel):
    """A test dataset for RAG evaluation"""
    test_set_id: UUID
    name: str
    description: Optional[str]
    domain: str = "general"  # general, medical, legal, etc.
    num_questions: int
    questions: List[RAGTestQuestion]
    created_at: datetime
    is_public: bool = False


class RAGComparisonRequest(BaseModel):
    """Compare two RAG configurations"""
    config_a_name: str
    config_a_results: List[RAGEvaluationResponse]
    config_b_name: str
    config_b_results: List[RAGEvaluationResponse]


class RAGComparisonResponse(BaseModel):
    """Comparison results between two RAG configurations"""
    config_a_name: str
    config_b_name: str
    
    # Average scores
    config_a_avg_faithfulness: float
    config_b_avg_faithfulness: float
    config_a_avg_relevance: float
    config_b_avg_relevance: float
    
    # Statistical significance
    faithfulness_p_value: float
    relevance_p_value: float
    
    # Winner
    winner: str  # config_a, config_b, or tie
    confidence: float
    recommendation: str
