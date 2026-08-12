"""
Training Worker Configuration
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Training worker settings"""
    
    # Worker
    WORKER_ID: str = os.getenv("WORKER_ID", "worker-1")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://slm_user:slm_password@postgres:5432/slm_platform"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    REDIS_QUEUE_NAME: str = "training_jobs"
    
    # MinIO (S3)
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
    MINIO_BUCKET_MODELS: str = "models"
    MINIO_BUCKET_CHECKPOINTS: str = "checkpoints"
    MINIO_SECURE: bool = False
    
    # Paths
    MODELS_DIR: str = os.getenv("MODELS_DIR", "/app/models")
    DATASETS_DIR: str = os.getenv("DATASETS_DIR", "/app/datasets")
    CHECKPOINTS_DIR: str = os.getenv("CHECKPOINTS_DIR", "/app/checkpoints")
    LOGS_DIR: str = os.getenv("LOGS_DIR", "/app/logs")
    
    # Training defaults
    DEFAULT_LORA_RANK: int = int(os.getenv("DEFAULT_LORA_RANK", "16"))
    DEFAULT_LORA_ALPHA: int = int(os.getenv("DEFAULT_LORA_ALPHA", "32"))
    DEFAULT_LORA_DROPOUT: float = float(os.getenv("DEFAULT_LORA_DROPOUT", "0.05"))
    
    DEFAULT_LEARNING_RATE: float = float(os.getenv("DEFAULT_LEARNING_RATE", "2e-4"))
    DEFAULT_NUM_EPOCHS: int = int(os.getenv("DEFAULT_NUM_EPOCHS", "3"))
    DEFAULT_BATCH_SIZE: int = int(os.getenv("DEFAULT_BATCH_SIZE", "4"))
    DEFAULT_GRADIENT_ACCUMULATION_STEPS: int = int(os.getenv("DEFAULT_GRADIENT_ACCUMULATION_STEPS", "1"))
    DEFAULT_WARMUP_STEPS: int = int(os.getenv("DEFAULT_WARMUP_STEPS", "100"))
    DEFAULT_MAX_SEQ_LENGTH: int = int(os.getenv("DEFAULT_MAX_SEQ_LENGTH", "2048"))
    DEFAULT_SAVE_STEPS: int = int(os.getenv("DEFAULT_SAVE_STEPS", "500"))
    DEFAULT_EVAL_STEPS: int = int(os.getenv("DEFAULT_EVAL_STEPS", "100"))
    DEFAULT_LOGGING_STEPS: int = int(os.getenv("DEFAULT_LOGGING_STEPS", "10"))
    
    # Resource limits
    MAX_GPU_MEMORY_MB: Optional[int] = None
    ENABLE_GRADIENT_CHECKPOINTING: bool = True
    ENABLE_MIXED_PRECISION: bool = True
    
    # Monitoring
    UPDATE_DB_INTERVAL_SECONDS: int = 30
    LOG_METRICS_INTERVAL_STEPS: int = 10
    
    # WandB (optional)
    WANDB_ENABLED: bool = os.getenv("WANDB_ENABLED", "false").lower() == "true"
    WANDB_PROJECT: str = os.getenv("WANDB_PROJECT", "slm-training")
    WANDB_API_KEY: Optional[str] = os.getenv("WANDB_API_KEY")
    
    class Config:
        case_sensitive = True


settings = Settings()
