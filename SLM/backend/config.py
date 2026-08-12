"""
Configuration management for SLM Platform Backend
"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "4"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://slm_user:slm_password@postgres:5432/slm_platform"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")
    REDIS_QUEUE_NAME: str = "training_jobs"
    
    # MinIO
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
    MINIO_BUCKET: str = os.getenv("MINIO_BUCKET", "slm-models")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"
    
    # Model Manager
    MAX_LOADED_MODELS: int = int(os.getenv("MAX_LOADED_MODELS", "2"))
    
    # Paths
    MODELS_DIR: str = os.getenv("MODELS_DIR", "/models")
    DATASETS_DIR: str = os.getenv("DATASETS_DIR", "/datasets")
    CHECKPOINTS_DIR: str = os.getenv("CHECKPOINTS_DIR", "/checkpoints")
    LOGS_DIR: str = os.getenv("LOGS_DIR", "/logs")
    
    # HuggingFace
    HUGGINGFACE_TOKEN: str = os.getenv("HUGGINGFACE_TOKEN", "")
    
    # Training Defaults
    DEFAULT_LEARNING_RATE: float = float(os.getenv("DEFAULT_LEARNING_RATE", "2e-4"))
    DEFAULT_BATCH_SIZE: int = int(os.getenv("DEFAULT_BATCH_SIZE", "4"))
    DEFAULT_NUM_EPOCHS: int = int(os.getenv("DEFAULT_NUM_EPOCHS", "3"))
    DEFAULT_MAX_SEQ_LENGTH: int = int(os.getenv("DEFAULT_MAX_SEQ_LENGTH", "2048"))
    DEFAULT_GRADIENT_ACCUMULATION_STEPS: int = int(os.getenv("DEFAULT_GRADIENT_ACCUMULATION_STEPS", "1"))
    DEFAULT_WARMUP_STEPS: int = int(os.getenv("DEFAULT_WARMUP_STEPS", "100"))
    
    # LoRA Defaults
    DEFAULT_LORA_RANK: int = int(os.getenv("DEFAULT_LORA_RANK", "16"))
    DEFAULT_LORA_ALPHA: int = int(os.getenv("DEFAULT_LORA_ALPHA", "32"))
    DEFAULT_LORA_DROPOUT: float = float(os.getenv("DEFAULT_LORA_DROPOUT", "0.05"))
    
    # Resource Limits
    MAX_CONCURRENT_TRAININGS: int = int(os.getenv("MAX_CONCURRENT_TRAININGS", "1"))
    MAX_GPU_MEMORY_FRACTION: float = float(os.getenv("MAX_GPU_MEMORY_FRACTION", "0.9"))
    ENABLE_GRADIENT_CHECKPOINTING: bool = os.getenv("ENABLE_GRADIENT_CHECKPOINTING", "true").lower() == "true"
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-to-a-secure-random-string")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))
    ENABLE_TENSORBOARD: bool = os.getenv("ENABLE_TENSORBOARD", "true").lower() == "true"
    
    # Model Defaults
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "mistral-7b")
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("DEFAULT_MAX_TOKENS", "512"))
    DEFAULT_TOP_P: float = float(os.getenv("DEFAULT_TOP_P", "0.9"))
    
    # GPU Configuration
    CUDA_VISIBLE_DEVICES: str = os.getenv("CUDA_VISIBLE_DEVICES", "0")
    
    # Quantization
    ENABLE_QLORA: bool = os.getenv("ENABLE_QLORA", "true").lower() == "true"
    LOAD_IN_4BIT: bool = os.getenv("LOAD_IN_4BIT", "false").lower() == "true"
    LOAD_IN_8BIT: bool = os.getenv("LOAD_IN_8BIT", "false").lower() == "true"
    
    # Optimization
    USE_FLASH_ATTENTION: bool = os.getenv("USE_FLASH_ATTENTION", "true").lower() == "true"
    ENABLE_CPU_OFFLOAD: bool = os.getenv("ENABLE_CPU_OFFLOAD", "false").lower() == "true"
    USE_BETTER_TRANSFORMER: bool = os.getenv("USE_BETTER_TRANSFORMER", "true").lower() == "true"
    
    # Experiment Tracking
    TRACK_EXPERIMENTS: bool = os.getenv("TRACK_EXPERIMENTS", "true").lower() == "true"
    EXPERIMENT_BACKEND: str = os.getenv("EXPERIMENT_BACKEND", "tensorboard")
    WANDB_API_KEY: str = os.getenv("WANDB_API_KEY", "")
    
    # Development
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
