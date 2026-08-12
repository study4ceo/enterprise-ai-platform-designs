"""
Database models and connection management
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, 
    BigInteger, TIMESTAMP, JSON, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
from config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ========== DATABASE MODELS ==========

class Model(Base):
    """Language models table"""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    size = Column(String(50))
    parameters = Column(BigInteger)
    architecture = Column(String(100))
    source = Column(String(50), default="huggingface")
    huggingface_id = Column(String(255))
    local_path = Column(Text)
    quantization = Column(String(50))
    disk_size_mb = Column(Integer)
    download_status = Column(String(50), default="not_downloaded")
    is_finetuned = Column(Boolean, default=False)
    base_model_id = Column(String(255))
    description = Column(Text)
    capabilities = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Dataset(Base):
    """Training datasets table"""
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    format = Column(String(50))
    num_samples = Column(Integer)
    size_mb = Column(Float)
    source = Column(String(50))
    local_path = Column(Text)
    split_config = Column(JSON)
    schema_info = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class TrainingJob(Base):
    """Training jobs table"""
    __tablename__ = "training_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    model_id = Column(String(255), ForeignKey("models.model_id"))
    dataset_id = Column(String(255), ForeignKey("datasets.dataset_id"))
    
    # Training configuration
    training_method = Column(String(50))
    config = Column(JSON)
    
    # LoRA specific
    lora_rank = Column(Integer)
    lora_alpha = Column(Integer)
    lora_dropout = Column(Float)
    target_modules = Column(JSON)
    
    # Training parameters
    learning_rate = Column(Float)
    num_epochs = Column(Integer)
    batch_size = Column(Integer)
    gradient_accumulation_steps = Column(Integer)
    warmup_steps = Column(Integer)
    max_seq_length = Column(Integer)
    
    # Status
    status = Column(String(50), default="queued", index=True)
    progress_percent = Column(Float, default=0.0)
    current_epoch = Column(Integer, default=0)
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer)
    
    # Metrics
    train_loss = Column(Float)
    eval_loss = Column(Float)
    best_eval_loss = Column(Float)
    learning_rate_current = Column(Float)
    tokens_per_second = Column(Float)
    
    # Resources
    gpu_type = Column(String(100))
    gpu_memory_used_mb = Column(Integer)
    estimated_time_remaining_minutes = Column(Integer)
    
    # Outputs
    output_model_id = Column(String(255))
    checkpoint_paths = Column(JSON)
    logs_path = Column(Text)
    tensorboard_path = Column(Text)
    
    # Timestamps
    queued_at = Column(TIMESTAMP, server_default=func.now())
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    duration_minutes = Column(Integer)
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class TrainingMetric(Base):
    """Training metrics time series"""
    __tablename__ = "training_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(255), ForeignKey("training_jobs.job_id"))
    step = Column(Integer, nullable=False)
    epoch = Column(Integer)
    
    # Loss metrics
    train_loss = Column(Float)
    eval_loss = Column(Float)
    
    # Learning rate
    learning_rate = Column(Float)
    
    # Performance
    tokens_per_second = Column(Float)
    samples_per_second = Column(Float)
    gpu_memory_allocated_mb = Column(Integer)
    gpu_utilization_percent = Column(Float)
    
    # Time
    timestamp = Column(TIMESTAMP, server_default=func.now())
    
    # Additional metrics
    custom_metrics = Column(JSON)
    
    __table_args__ = (
        Index('idx_training_metrics_job_step', 'job_id', 'step'),
    )


class ModelEvaluation(Base):
    """Model evaluations table"""
    __tablename__ = "model_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    eval_id = Column(String(255), unique=True, nullable=False)
    model_id = Column(String(255), ForeignKey("models.model_id"))
    
    # Benchmark info
    benchmark_name = Column(String(100))
    dataset_name = Column(String(255))
    num_samples = Column(Integer)
    
    # Results
    accuracy = Column(Float)
    perplexity = Column(Float)
    score = Column(Float)
    detailed_results = Column(JSON)
    
    # Performance
    avg_latency_ms = Column(Float)
    tokens_per_second = Column(Float)
    memory_used_mb = Column(Integer)
    
    created_at = Column(TIMESTAMP, server_default=func.now())


class InferenceLog(Base):
    """Inference logs table"""
    __tablename__ = "inference_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(255), unique=True, nullable=False)
    model_id = Column(String(255), ForeignKey("models.model_id"))
    
    # Request
    prompt = Column(Text)
    prompt_tokens = Column(Integer)
    
    # Response
    response = Column(Text)
    response_tokens = Column(Integer)
    
    # Performance
    latency_ms = Column(Integer)
    tokens_per_second = Column(Float)
    
    # Config
    temperature = Column(Float)
    max_tokens = Column(Integer)
    top_p = Column(Float)
    
    timestamp = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        Index('idx_inference_logs_model_time', 'model_id', 'timestamp'),
    )


class Experiment(Base):
    """Experiments table"""
    __tablename__ = "experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Models to compare
    model_ids = Column(JSON)
    
    # Test dataset
    test_dataset_id = Column(String(255))
    num_samples = Column(Integer)
    
    # Results
    results = Column(JSON)
    winner_model_id = Column(String(255))
    
    status = Column(String(50), default="pending")
    created_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(TIMESTAMP)


class SystemMetric(Base):
    """System metrics table"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Resource usage
    cpu_usage_percent = Column(Float)
    memory_used_mb = Column(Integer)
    memory_total_mb = Column(Integer)
    disk_used_gb = Column(Float)
    disk_total_gb = Column(Float)
    
    # GPU metrics
    gpu_name = Column(String(255))
    gpu_memory_used_mb = Column(Integer)
    gpu_memory_total_mb = Column(Integer)
    gpu_utilization_percent = Column(Float)
    gpu_temperature_c = Column(Float)
    
    # Network
    network_in_mb = Column(Float)
    network_out_mb = Column(Float)
    
    timestamp = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        Index('idx_system_metrics_timestamp', 'timestamp'),
    )


# Initialize database
async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
