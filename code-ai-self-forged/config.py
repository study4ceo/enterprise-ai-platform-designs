"""Configuration management for Code-AI-Self-Forged."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # LLM Provider (anthropic or ollama)
    llm_provider: str = Field(default="anthropic", env="LLM_PROVIDER")
    
    # Anthropic API (for cloud mode)
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    model_name: str = Field(default="claude-sonnet-4.6", env="MODEL_NAME")
    # Options: claude-sonnet-4.6 (balanced), claude-opus-4.7 (max power)
    
    # Ollama Configuration (for offline mode)
    ollama_model: str = Field(default="llama3.1:8b", env="OLLAMA_MODEL")
    # Options: llama3.1:8b, codellama:34b, qwen2.5-coder:32b
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    
    # Common settings
    max_tokens: int = Field(default=8000, env="MAX_TOKENS")
    temperature: float = Field(default=0.7, env="TEMPERATURE")

    # Execution
    execution_timeout: int = Field(default=30, env="EXECUTION_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    enable_docker: bool = Field(default=False, env="ENABLE_DOCKER")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Paths
    project_root: Path = Path(__file__).parent
    workspace_dir: Path = project_root / "workspace"
    logs_dir: Path = project_root / "logs"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories
        self.workspace_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Validate configuration
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY required when LLM_PROVIDER=anthropic")


# Global settings instance
settings = Settings()
