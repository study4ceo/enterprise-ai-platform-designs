import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """RAG Evaluator Service Configuration"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL',
        'postgresql+asyncpg://postgres:postgres@localhost:5432/llm_evaluation'
    )
    
    # Redis
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # RabbitMQ
    RABBITMQ_URL: str = os.getenv('RABBITMQ_URL', 'amqp://admin:admin@localhost:5672/')
    
    # API Keys
    GROQ_API_KEY: str = os.getenv('GROQ_API_KEY', '')
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    
    # Embedding Model
    EMBEDDING_MODEL: str = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    
    # Service Config
    SERVICE_NAME: str = "rag-evaluator"
    SERVICE_PORT: int = int(os.getenv('SERVICE_PORT', '8004'))
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # RAG Evaluation Config
    DEFAULT_RELEVANCE_THRESHOLD: float = 0.3
    DEFAULT_LLM_MODEL: str = "llama-3.1-70b-versatile"  # Groq for speed
    CACHE_TTL: int = 3600  # 1 hour cache for evaluations
    
    class Config:
        env_file = '.env'


settings = Settings()
