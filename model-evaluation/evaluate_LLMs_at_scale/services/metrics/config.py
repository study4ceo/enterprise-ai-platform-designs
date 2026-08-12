import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Metrics Service Configuration"""
    
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
    
    # Service Config
    SERVICE_NAME: str = "metrics-service"
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    class Config:
        env_file = '.env'


settings = Settings()
