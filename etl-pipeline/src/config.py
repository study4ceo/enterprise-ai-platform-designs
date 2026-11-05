"""
Configuration management for ETL pipeline.
Loads settings from environment variables with sensible defaults.
"""
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration for ETL pipeline."""
    
    # Database
    DB_PATH: str = os.getenv("DB_PATH", "orders.duckdb")
    
    # Data Paths
    RAW_DATA_PATH: Path = Path(os.getenv("RAW_DATA_PATH", "./data/raw"))
    PROCESSED_DATA_PATH: Path = Path(os.getenv("PROCESSED_DATA_PATH", "./data/processed"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_PATH: Path = Path(os.getenv("LOG_PATH", "./logs/pipeline.log"))
    
    # Required Columns
    REQUIRED_COLUMNS: List[str] = os.getenv(
        "REQUIRED_COLUMNS", 
        "order_id,customer_id,order_date,amount,status"
    ).split(",")
    
    # Validation Rules
    MIN_AMOUNT: float = float(os.getenv("MIN_AMOUNT", "0.0"))
    VALID_STATUSES: List[str] = os.getenv(
        "VALID_STATUSES", 
        "pending,completed,cancelled,refunded,shipped"
    ).split(",")
    
    # Column Mapping (handle variations in CSV column names)
    COLUMN_MAPPING: dict = {
        "order_id": ["order_id", "OrderID", "order_number", "id"],
        "customer_id": ["customer_id", "CustomerID", "cust_id", "client_id"],
        "order_date": ["order_date", "OrderDate", "date", "order_datetime", "Date"],
        "amount": ["amount", "Amount", "TotalAmount", "total", "order_total", "price", "Total"],
        "status": ["status", "Status", "OrderStatus", "order_status", "state", "State"]
    }
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        cls.RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)
        cls.PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)
        cls.LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


# Initialize directories on module import
Config.ensure_directories()
