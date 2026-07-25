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

    # Anthropic API
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    model_name: str = Field(default="claude-sonnet-4.6", env="MODEL_NAME")
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


# Global settings instance
settings = Settings()
