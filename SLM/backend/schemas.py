"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ========== ENUMS ==========

class ModelSize(str, Enum):
    SMALL_1B = "1B"
    SMALL_3B = "3B"
    MEDIUM_7B = "7B"
    LARGE_10B = "10B"


class TrainingMethod(str, Enum):
    LORA = "lora"
    QLORA = "qlora"
    FULL = "full"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DownloadStatus(str, Enum):
    NOT_DOWNLOADED = "not_downloaded"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    FAILED = "failed"


# ========== MODEL SCHEMAS ==========

class ModelBase(BaseModel):
    model_id: str
    name: str
    size: Optional[str] = None
    parameters: Optional[int] = None
    architecture: Optional[str] = None
    description: Optional[str] = None


class ModelCreate(ModelBase):
    huggingface_id: str
    source: str = "huggingface"


class ModelDownload(BaseModel):
    model_id: str
    quantization: Optional[str] = None  # "fp16", "int8", "int4"


class ModelResponse(ModelBase):
    id: int
    source: str
    huggingface_id: Optional[str]
    local_path: Optional[str]
    quantization: Optional[str]
    disk_size_mb: Optional[int]
    download_status: str
    is_finetuned: bool
    base_model_id: Optional[str]
    capabilities: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ModelListResponse(BaseModel):
    models: List[ModelResponse]
    total: int
    page: int = 1
    page_size: int = 20


# ========== DATASET SCHEMAS ==========

class DatasetBase(BaseModel):
    dataset_id: str
    name: str
    description: Optional[str] = None
    format: str = "json"


class DatasetCreate(DatasetBase):
    source: str = "upload"


class DatasetUpload(BaseModel):
    name: str
    description: Optional[str] = None
    format: str = "json"


class DatasetResponse(DatasetBase):
    id: int
    num_samples: Optional[int]
    size_mb: Optional[float]
    source: str
    local_path: Optional[str]
    split_config: Optional[Dict[str, float]]
    schema_info: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DatasetListResponse(BaseModel):
    datasets: List[DatasetResponse]
    total: int
    page: int = 1
    page_size: int = 20


# ========== TRAINING SCHEMAS ==========

class LoRAConfig(BaseModel):
    """LoRA-specific configuration"""
    rank: int = Field(default=16, ge=1, le=256)
    alpha: int = Field(default=32, ge=1)
    dropout: float = Field(default=0.05, ge=0.0, le=1.0)
    target_modules: List[str] = ["q_proj", "v_proj", "k_proj", "o_proj"]


class TrainingConfig(BaseModel):
    """Training hyperparameters"""
    learning_rate: float = Field(default=2e-4, gt=0.0)
    num_epochs: int = Field(default=3, ge=1)
    batch_size: int = Field(default=4, ge=1)
    gradient_accumulation_steps: int = Field(default=1, ge=1)
    warmup_steps: int = Field(default=100, ge=0)
    max_seq_length: int = Field(default=2048, ge=128)
    eval_steps: int = Field(default=100, ge=1)
    save_steps: int = Field(default=500, ge=1)
    logging_steps: int = Field(default=10, ge=1)


class TrainingJobCreate(BaseModel):
    """Create a new training job"""
    name: str
    model_id: str
    dataset_id: str
    training_method: TrainingMethod = TrainingMethod.LORA
    lora_config: Optional[LoRAConfig] = None
    training_config: Optional[TrainingConfig] = None


class TrainingJobResponse(BaseModel):
    """Training job response"""
    id: int
    job_id: str
    name: str
    model_id: str
    dataset_id: str
    training_method: str
    
    # Configuration
    lora_rank: Optional[int]
    lora_alpha: Optional[int]
    lora_dropout: Optional[float]
    learning_rate: Optional[float]
    num_epochs: Optional[int]
    batch_size: Optional[int]
    
    # Status
    status: str
    progress_percent: float
    current_epoch: int
    current_step: int
    total_steps: Optional[int]
    
    # Metrics
    train_loss: Optional[float]
    eval_loss: Optional[float]
    best_eval_loss: Optional[float]
    tokens_per_second: Optional[float]
    
    # Resources
    gpu_type: Optional[str]
    gpu_memory_used_mb: Optional[int]
    estimated_time_remaining_minutes: Optional[int]
    
    # Outputs
    output_model_id: Optional[str]
    logs_path: Optional[str]
    
    # Timestamps
    queued_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_minutes: Optional[int]
    
    # Error
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class TrainingJobListResponse(BaseModel):
    jobs: List[TrainingJobResponse]
    total: int
    page: int = 1
    page_size: int = 20


class TrainingMetricsResponse(BaseModel):
    """Training metrics time series"""
    step: int
    epoch: Optional[int]
    train_loss: Optional[float]
    eval_loss: Optional[float]
    learning_rate: Optional[float]
    tokens_per_second: Optional[float]
    gpu_memory_allocated_mb: Optional[int]
    gpu_utilization_percent: Optional[float]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class TrainingMetricsListResponse(BaseModel):
    metrics: List[TrainingMetricsResponse]
    total: int


# ========== INFERENCE SCHEMAS ==========

class ChatMessage(BaseModel):
    role: str = "user"  # user, assistant, system
    content: str


class ChatRequest(BaseModel):
    model_id: str
    messages: List[ChatMessage]
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=512, ge=1, le=4096)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    stream: bool = False


class ChatResponse(BaseModel):
    request_id: str
    model_id: str
    response: str
    prompt_tokens: int
    response_tokens: int
    total_tokens: int
    latency_ms: int
    tokens_per_second: float


class GenerateRequest(BaseModel):
    model_id: str
    prompt: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=512, ge=1, le=4096)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    stop_sequences: Optional[List[str]] = None


class GenerateResponse(BaseModel):
    request_id: str
    model_id: str
    generated_text: str
    tokens_generated: int
    latency_ms: int
    tokens_per_second: float


# ========== EVALUATION SCHEMAS ==========

class EvaluationRequest(BaseModel):
    model_id: str
    benchmark_name: str  # "mmlu", "gsm8k", "hellaswag"
    num_samples: Optional[int] = 100


class EvaluationResponse(BaseModel):
    eval_id: str
    model_id: str
    benchmark_name: str
    accuracy: Optional[float]
    perplexity: Optional[float]
    score: float
    detailed_results: Optional[Dict[str, Any]]
    avg_latency_ms: float
    tokens_per_second: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== SYSTEM SCHEMAS ==========

class SystemMetricsResponse(BaseModel):
    cpu_usage_percent: float
    memory_used_mb: int
    memory_total_mb: int
    memory_usage_percent: float
    disk_used_gb: float
    disk_total_gb: float
    disk_usage_percent: float
    gpu_name: Optional[str]
    gpu_memory_used_mb: Optional[int]
    gpu_memory_total_mb: Optional[int]
    gpu_memory_usage_percent: Optional[float]
    gpu_utilization_percent: Optional[float]
    gpu_temperature_c: Optional[float]
    timestamp: datetime


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
    minio: str
    gpu_available: bool
    gpu_count: int
    timestamp: datetime


# ========== ERROR SCHEMAS ==========

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str]
    timestamp: datetime


# ========== STATISTICS SCHEMAS ==========

class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_models: int
    downloaded_models: int
    finetuned_models: int
    total_datasets: int
    total_training_jobs: int
    active_training_jobs: int
    completed_training_jobs: int
    failed_training_jobs: int
    total_disk_space_gb: float
    used_disk_space_gb: float
    models_disk_space_gb: float
    datasets_disk_space_gb: float
