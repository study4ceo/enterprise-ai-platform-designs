"""Application configuration management."""

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://wifi_user:changeme@localhost:5432/wifi_monitor",
        alias="DATABASE_URL"
    )
    db_pool_size: int = Field(default=20, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    
    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        alias="ALLOWED_ORIGINS"
    )
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        alias="SECRET_KEY"
    )
    session_timeout_minutes: int = Field(default=30, alias="SESSION_TIMEOUT_MINUTES")
    bcrypt_work_factor: int = Field(default=12, alias="BCRYPT_WORK_FACTOR")
    
    # HTTPS
    https_enabled: bool = Field(default=False, alias="HTTPS_ENABLED")
    ssl_cert_file: Optional[str] = Field(default=None, alias="SSL_CERT_FILE")
    ssl_key_file: Optional[str] = Field(default=None, alias="SSL_KEY_FILE")
    
    # Scanning
    default_scan_interval_seconds: int = Field(
        default=30,
        alias="DEFAULT_SCAN_INTERVAL_SECONDS"
    )
    
    # Notifications
    browser_notifications_enabled: bool = Field(
        default=True,
        alias="BROWSER_NOTIFICATIONS_ENABLED"
    )
    email_notifications_enabled: bool = Field(
        default=False,
        alias="EMAIL_NOTIFICATIONS_ENABLED"
    )
    webhook_notifications_enabled: bool = Field(
        default=False,
        alias="WEBHOOK_NOTIFICATIONS_ENABLED"
    )
    
    # Email
    smtp_host: Optional[str] = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, alias="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from: str = Field(
        default="WiFi Monitor <noreply@example.com>",
        alias="SMTP_FROM"
    )
    email_recipients: List[str] = Field(default=[], alias="EMAIL_RECIPIENTS")
    
    # Webhook
    webhook_urls: List[str] = Field(default=[], alias="WEBHOOK_URLS")
    
    # Data Retention
    connection_history_retention_days: int = Field(
        default=90,
        alias="CONNECTION_HISTORY_RETENTION_DAYS"
    )


# Global settings instance
settings = Settings()
