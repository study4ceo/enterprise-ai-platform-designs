"""Configuration management."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # LLM Provider (anthropic, groq, or ollama)
    llm_provider: str = Field(default="ollama", env="LLM_PROVIDER")
    
    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    model_name: str = Field(default="claude-sonnet-4.6", env="MODEL_NAME")
    
    # Groq (fast cloud inference)
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", env="GROQ_MODEL")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1", env="GROQ_BASE_URL")
    
    # Ollama
    ollama_model: str = Field(default="llama3.1:8b", env="OLLAMA_MODEL")
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    
    # Generation
    max_tokens: int = Field(default=2000, env="MAX_TOKENS")
    temperature: float = Field(default=0.0, env="TEMPERATURE")
    
    # Paths
    project_root: Path = Path(__file__).parent
    db_path: Path = project_root / "demo_db.sqlite"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
