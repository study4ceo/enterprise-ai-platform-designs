"""
Training Worker - Orchestrates training jobs from Redis queue
"""

import os
import sys
import json
import logging
import asyncio
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

import redis
import torch
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from config import settings
from lora_trainer import LoRATrainer, LoRATrainingConfig
from qlora_trainer import QLoRATrainer, QLoRATrainingConfig

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrainingWorker:
    """
    Training Worker - Consumes training jobs from Redis queue and executes them.
    """
    
    def __init__(self):
        """Initialize training worker"""
        self.worker_id = settings.WORKER_ID
        self.redis_client = None
        self.db_engine = None
        self.db_session_factory = None
        self.current_job_id = None
        self.should_stop = False
        
        logger.info(f"Training Worker {self.worker_id} initializing...")
        
        # Check GPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Device: {self.device}")
        
        if self.device == "cuda":
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            logger.info(f"GPU: {gpu_name}")
            logger.info(f"GPU Memory: {gpu_memory:.2f} GB")
        else:
            logger.warning("No GPU detected. Training will be very slow on CPU.")
    
    async def setup(self):
        """Setup connections to Redis and database"""
        try:
            # Connect to Redis
            self.redis_client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Connected to Redis")
            
            # Setup database
            self.db_engine = create_async_engine(
                settings.DATABASE_URL,
                pool_size=5,
                max_overflow=10
            )
            self.db_session_factory = async_sessionmaker(
                self.db_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            logger.info("Connected to database")
            
            logger.info(f"Worker {self.worker_id} ready to process jobs")
            
        except Exception as e:
            logger.error(f"Failed to setup worker: {e}", exc_info=True)
            raise
    
    async def get_job_from_queue(self) -> Optional[Dict[str, Any]]:
        """
        Get next training job from Redis queue (blocking with timeout).
        
        Returns:
            Job dictionary or None if timeout
        """
        try:
            # BLPOP blocks until a job is available or timeout
            result = self.redis_client.blpop(
                settings.REDIS_QUEUE_NAME,
                timeout=30  # 30 second timeout
            )
            
            if result:
                queue_name, job_json = result
                job_data = json.loads(job_json)
                logger.info(f"Retrieved job from queue: {job_data.get('job_id')}")
                return job_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting job from queue: {e}", exc_info=True)
            return None
    
    async def update_job_status(
        self,
        job_id: str,
        status: str,
        **kwargs
    ):
        """
        Update job status in database.
        
        Args:
            job_id: Training job ID
            status: New status
            **kwargs: Additional fields to update
        """
        try:
            async with self.db_session_factory() as session:
                # Build update query dynamically
                from database import TrainingJob
                
                update_data = {"status": status, "updated_at": datetime.utcnow()}
                
                # Add optional fields
                if status == "running" and "started_at" not in kwargs:
                    update_data["started_at"] = datetime.utcnow()
                elif status in ["completed", "failed", "cancelled"]:
                    if "completed_at" not in kwargs:
                        update_data["completed_at"] = datetime.utcnow()
                    
                    # Calculate duration
                    result = await session.execute(
                        select(TrainingJob).where(TrainingJob.job_id == job_id)
                    )
                    job = result.scalar_one_or_none()
                    if job and job.started_at:
                        duration = (datetime.utcnow() - job.started_at).total_seconds() / 60
                        update_data["duration_minutes"] = int(duration)
                
                update_data.update(kwargs)
                
                # Execute update
                stmt = (
                    update(TrainingJob)
                    .where(TrainingJob.job_id == job_id)
                    .values(**update_data)
                )
                
                await session.execute(stmt)
                await session.commit()
                
                logger.info(f"Updated job {job_id} status to {status}")
                
        except Exception as e:
            logger.error(f"Failed to update job status: {e}", exc_info=True)
    
    async def log_training_metric(
        self,
        job_id: str,
        step: int,
        metrics: Dict[str, Any]
    ):
        """
        Log training metrics to database.
        
        Args:
            job_id: Training job ID
            step: Training step
            metrics: Metrics dictionary
        """
        try:
            async with self.db_session_factory() as session:
                from database import TrainingMetric
                
                metric = TrainingMetric(
                    job_id=job_id,
                    step=step,
                    epoch=metrics.get("epoch"),
                    train_loss=metrics.get("train_loss"),
                    eval_loss=metrics.get("eval_loss"),
                    learning_rate=metrics.get("learning_rate"),
                    tokens_per_second=metrics.get("tokens_per_second"),
                    gpu_memory_allocated_mb=metrics.get("gpu_memory_allocated_mb"),
                    gpu_utilization_percent=metrics.get("gpu_utilization_percent"),
                    custom_metrics=metrics.get("custom_metrics")
                )
                
                session.add(metric)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Failed to log training metric: {e}", exc_info=True)
    
    async def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full job details from database.
        
        Args:
            job_id: Training job ID
        
        Returns:
            Job details dictionary
        """
        try:
            async with self.db_session_factory() as session:
                from database import TrainingJob, Model, Dataset
                
                # Get job
                result = await session.execute(
                    select(TrainingJob).where(TrainingJob.job_id == job_id)
                )
                job = result.scalar_one_or_none()
                
                if not job:
                    logger.error(f"Job {job_id} not found in database")
                    return None
                
                # Get model
                model_result = await session.execute(
                    select(Model).where(Model.model_id == job.model_id)
                )
                model = model_result.scalar_one_or_none()
                
                # Get dataset
                dataset_result = await session.execute(
                    select(Dataset).where(Dataset.dataset_id == job.dataset_id)
                )
                dataset = dataset_result.scalar_one_or_none()
                
                return {
                    "job": job,
                    "model": model,
                    "dataset": dataset
                }
                
        except Exception as e:
            logger.error(f"Failed to get job details: {e}", exc_info=True)
            return None
    
    async def execute_training_job(self, job_data: Dict[str, Any]):
        """
        Execute a training job.
        
        Args:
            job_data: Job data from queue
        """
        job_id = job_data.get("job_id")
        self.current_job_id = job_id
        
        logger.info(f"Starting training job {job_id}")
        
        try:
            # Update status to running
            await self.update_job_status(job_id, "running")
            
            # Get full job details from database
            details = await self.get_job_details(job_id)
            if not details:
                raise ValueError(f"Job {job_id} not found")
            
            job = details["job"]
            model = details["model"]
            dataset = details["dataset"]
            
            # Validate
            if not model:
                raise ValueError(f"Model {job.model_id} not found")
            if not dataset:
                raise ValueError(f"Dataset {job.dataset_id} not found")
            if not model.local_path or not os.path.exists(model.local_path):
                raise ValueError(f"Model path not found: {model.local_path}")
            if not dataset.local_path or not os.path.exists(dataset.local_path):
                raise ValueError(f"Dataset path not found: {dataset.local_path}")
            
            # Prepare output directory
            output_dir = os.path.join(
                settings.CHECKPOINTS_DIR,
                job_id
            )
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate output model ID
            output_model_id = f"{model.model_id}-finetuned-{job_id[:8]}"
            
            # Choose trainer based on training method
            training_method = job.training_method.lower()
            
            if training_method == "qlora":
                # QLoRA (4-bit quantized)
                config = QLoRATrainingConfig(
                    model_path=model.local_path,
                    output_dir=output_dir,
                    lora_rank=job.lora_rank or settings.DEFAULT_LORA_RANK,
                    lora_alpha=job.lora_alpha or settings.DEFAULT_LORA_ALPHA,
                    lora_dropout=job.lora_dropout or settings.DEFAULT_LORA_DROPOUT,
                    learning_rate=job.learning_rate or settings.DEFAULT_LEARNING_RATE,
                    num_epochs=job.num_epochs or settings.DEFAULT_NUM_EPOCHS,
                    batch_size=job.batch_size or settings.DEFAULT_BATCH_SIZE,
                    gradient_accumulation_steps=job.gradient_accumulation_steps or settings.DEFAULT_GRADIENT_ACCUMULATION_STEPS,
                    warmup_steps=job.warmup_steps or settings.DEFAULT_WARMUP_STEPS,
                    max_seq_length=job.max_seq_length or settings.DEFAULT_MAX_SEQ_LENGTH,
                    eval_steps=settings.DEFAULT_EVAL_STEPS,
                    save_steps=settings.DEFAULT_SAVE_STEPS,
                    logging_steps=settings.DEFAULT_LOGGING_STEPS,
                    wandb_project=settings.WANDB_PROJECT if settings.WANDB_ENABLED else None,
                    wandb_run_name=f"{job.name}-{job_id[:8]}"
                )
                
                trainer = QLoRATrainer(config)
                
            elif training_method == "lora":
                # Standard LoRA
                config = LoRATrainingConfig(
                    model_path=model.local_path,
                    output_dir=output_dir,
                    lora_rank=job.lora_rank or settings.DEFAULT_LORA_RANK,
                    lora_alpha=job.lora_alpha or settings.DEFAULT_LORA_ALPHA,
                    lora_dropout=job.lora_dropout or settings.DEFAULT_LORA_DROPOUT,
                    learning_rate=job.learning_rate or settings.DEFAULT_LEARNING_RATE,
                    num_epochs=job.num_epochs or settings.DEFAULT_NUM_EPOCHS,
                    batch_size=job.batch_size or settings.DEFAULT_BATCH_SIZE,
                    gradient_accumulation_steps=job.gradient_accumulation_steps or settings.DEFAULT_GRADIENT_ACCUMULATION_STEPS,
                    warmup_steps=job.warmup_steps or settings.DEFAULT_WARMUP_STEPS,
                    max_seq_length=job.max_seq_length or settings.DEFAULT_MAX_SEQ_LENGTH,
                    eval_steps=settings.DEFAULT_EVAL_STEPS,
                    save_steps=settings.DEFAULT_SAVE_STEPS,
                    logging_steps=settings.DEFAULT_LOGGING_STEPS,
                    wandb_project=settings.WANDB_PROJECT if settings.WANDB_ENABLED else None,
                    wandb_run_name=f"{job.name}-{job_id[:8]}"
                )
                
                trainer = LoRATrainer(config)
            
            else:
                raise ValueError(f"Unsupported training method: {training_method}")
            
            # Load model
            logger.info("Loading model...")
            trainer.load_model()
            
            # Update job with GPU info
            if self.device == "cuda":
                gpu_type = torch.cuda.get_device_name(0)
                gpu_memory = int(torch.cuda.memory_allocated() / (1024**2))
                await self.update_job_status(
                    job_id,
                    "running",
                    gpu_type=gpu_type,
                    gpu_memory_used_mb=gpu_memory
                )
            
            # Prepare dataset
            logger.info("Preparing dataset...")
            train_dataset, eval_dataset = trainer.prepare_dataset(
                dataset.local_path
            )
            
            # Calculate total steps
            total_steps = (len(train_dataset) // config.batch_size) * config.num_epochs
            await self.update_job_status(
                job_id,
                "running",
                total_steps=total_steps
            )
            
            # Train
            logger.info("Starting training...")
            metrics = trainer.train(train_dataset, eval_dataset)
            
            # Update final metrics
            await self.update_job_status(
                job_id,
                "completed",
                output_model_id=output_model_id,
                train_loss=metrics.get("train_loss"),
                eval_loss=metrics.get("eval_loss"),
                progress_percent=100.0
            )
            
            # Cleanup
            trainer.cleanup()
            
            logger.info(f"Job {job_id} completed successfully")
            
            # TODO: Upload model to MinIO
            # TODO: Register fine-tuned model in database
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            
            # Update status to failed
            error_message = f"{type(e).__name__}: {str(e)}\n\n{traceback.format_exc()}"
            await self.update_job_status(
                job_id,
                "failed",
                error_message=error_message
            )
        
        finally:
            self.current_job_id = None
    
    async def run(self):
        """Main worker loop"""
        logger.info(f"Worker {self.worker_id} starting main loop")
        
        while not self.should_stop:
            try:
                # Get next job from queue (blocking with timeout)
                job_data = await self.get_job_from_queue()
                
                if job_data:
                    # Execute training job
                    await self.execute_training_job(job_data)
                else:
                    # No job available, wait and retry
                    await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal. Stopping...")
                self.should_stop = True
                break
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                await asyncio.sleep(5)
        
        logger.info(f"Worker {self.worker_id} stopped")
    
    async def cleanup(self):
        """Cleanup connections"""
        if self.redis_client:
            self.redis_client.close()
        
        if self.db_engine:
            await self.db_engine.dispose()
        
        logger.info("Worker cleanup complete")


async def main():
    """Main entry point"""
    worker = TrainingWorker()
    
    try:
        await worker.setup()
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await worker.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
