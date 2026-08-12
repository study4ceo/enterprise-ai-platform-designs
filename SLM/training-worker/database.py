"""
Database models for training worker (simplified version)
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, BigInteger, TIMESTAMP, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Model(Base):
    """Language models table"""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    local_path = Column(Text)


class Dataset(Base):
    """Training datasets table"""
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True)
    dataset_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    local_path = Column(Text)


class TrainingJob(Base):
    """Training jobs table"""
    __tablename__ = "training_jobs"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    model_id = Column(String(255))
    dataset_id = Column(String(255))
    
    training_method = Column(String(50))
    
    # LoRA params
    lora_rank = Column(Integer)
    lora_alpha = Column(Integer)
    lora_dropout = Column(Float)
    
    # Training params
    learning_rate = Column(Float)
    num_epochs = Column(Integer)
    batch_size = Column(Integer)
    gradient_accumulation_steps = Column(Integer)
    warmup_steps = Column(Integer)
    max_seq_length = Column(Integer)
    
    # Status
    status = Column(String(50))
    progress_percent = Column(Float, default=0.0)
    current_epoch = Column(Integer, default=0)
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer)
    
    # Metrics
    train_loss = Column(Float)
    eval_loss = Column(Float)
    
    # Resources
    gpu_type = Column(String(100))
    gpu_memory_used_mb = Column(Integer)
    
    # Outputs
    output_model_id = Column(String(255))
    
    # Timestamps
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Error
    error_message = Column(Text)


class TrainingMetric(Base):
    """Training metrics time series"""
    __tablename__ = "training_metrics"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(String(255))
    step = Column(Integer)
    epoch = Column(Integer)
    train_loss = Column(Float)
    eval_loss = Column(Float)
    learning_rate = Column(Float)
    tokens_per_second = Column(Float)
    gpu_memory_allocated_mb = Column(Integer)
    gpu_utilization_percent = Column(Float)
    custom_metrics = Column(JSON)
    timestamp = Column(TIMESTAMP, server_default=func.now())
