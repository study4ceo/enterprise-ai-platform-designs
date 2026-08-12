"""
SLM Platform - Main FastAPI Application
"""

import os
import sys
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
import redis

from config import settings
from database import get_db, init_db, Model, Dataset, TrainingJob, SystemMetric
from schemas import (
    ModelResponse, ModelListResponse, ModelDownload, ModelCreate,
    DatasetResponse, DatasetListResponse, DatasetUpload,
    TrainingJobCreate, TrainingJobResponse, TrainingJobListResponse,
    TrainingMetricsResponse, TrainingMetricsListResponse,
    ChatRequest, ChatResponse, GenerateRequest, GenerateResponse,
    EvaluationRequest, EvaluationResponse,
    SystemMetricsResponse, HealthResponse, DashboardStats,
    ErrorResponse
)
from model_manager import model_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis client for task queue
redis_client = None


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    global redis_client
    
    # Startup
    logger.info("Starting SLM Platform API...")
    await init_db()
    
    # Connect to Redis
    try:
        redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        redis_client.ping()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")
        redis_client = None
    
    logger.info(f"API started successfully on {settings.API_HOST}:{settings.API_PORT}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SLM Platform API...")
    if redis_client:
        redis_client.close()


# Create FastAPI app
app = FastAPI(
    title="SLM Platform API",
    description="API for Small Language Models Training & Deployment",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== HEALTH & STATUS ==========

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    
    # Check database
    try:
        await db.execute(select(1))
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    # Check GPU
    import torch
    gpu_available = torch.cuda.is_available()
    gpu_count = torch.cuda.device_count() if gpu_available else 0
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        version="1.0.0",
        database=db_status,
        redis="healthy",  # TODO: Implement redis check
        minio="healthy",  # TODO: Implement minio check
        gpu_available=gpu_available,
        gpu_count=gpu_count,
        timestamp=datetime.utcnow()
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "SLM Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# ========== MODELS API ==========

@app.get("/api/v1/models", response_model=ModelListResponse, tags=["Models"])
async def list_models(
    page: int = 1,
    page_size: int = 20,
    size: str = None,
    is_finetuned: bool = None,
    db: AsyncSession = Depends(get_db)
):
    """List all models with filtering and pagination"""
    
    query = select(Model)
    
    # Apply filters
    if size:
        query = query.where(Model.size == size)
    if is_finetuned is not None:
        query = query.where(Model.is_finetuned == is_finetuned)
    
    # Get total count
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    models = result.scalars().all()
    
    return ModelListResponse(
        models=[ModelResponse.from_orm(m) for m in models],
        total=total,
        page=page,
        page_size=page_size
    )


@app.get("/api/v1/models/{model_id}", response_model=ModelResponse, tags=["Models"])
async def get_model(model_id: str, db: AsyncSession = Depends(get_db)):
    """Get model details by ID"""
    
    result = await db.execute(
        select(Model).where(Model.model_id == model_id)
    )
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return ModelResponse.from_orm(model)


@app.post("/api/v1/models/download", tags=["Models"])
async def download_model(
    request: ModelDownload,
    db: AsyncSession = Depends(get_db)
):
    """Download a model from HuggingFace"""
    
    # Check if model exists
    result = await db.execute(
        select(Model).where(Model.model_id == request.model_id)
    )
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if model.download_status == "downloaded":
        return {"message": "Model already downloaded", "model_id": request.model_id}
    
    # Update status to downloading
    model.download_status = "downloading"
    await db.commit()
    
    # TODO: Implement actual download logic (background task)
    # For now, just return a message
    
    return {
        "message": "Model download started",
        "model_id": request.model_id,
        "status": "downloading"
    }


@app.delete("/api/v1/models/{model_id}", tags=["Models"])
async def delete_model(model_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a model"""
    
    result = await db.execute(
        select(Model).where(Model.model_id == model_id)
    )
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Don't allow deleting base models
    if not model.is_finetuned:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete base models"
        )
    
    await db.delete(model)
    await db.commit()
    
    return {"message": "Model deleted successfully", "model_id": model_id}


# ========== DATASETS API ==========

@app.get("/api/v1/datasets", response_model=DatasetListResponse, tags=["Datasets"])
async def list_datasets(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """List all datasets"""
    
    query = select(Dataset)
    
    # Get total count
    total_result = await db.execute(select(func.count()).select_from(Dataset))
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    datasets = result.scalars().all()
    
    return DatasetListResponse(
        datasets=[DatasetResponse.from_orm(d) for d in datasets],
        total=total,
        page=page,
        page_size=page_size
    )


@app.get("/api/v1/datasets/{dataset_id}", response_model=DatasetResponse, tags=["Datasets"])
async def get_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    """Get dataset details"""
    
    result = await db.execute(
        select(Dataset).where(Dataset.dataset_id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return DatasetResponse.from_orm(dataset)


@app.post("/api/v1/datasets/upload", tags=["Datasets"])
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = None,
    description: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Upload a new dataset"""
    
    # Generate dataset ID
    import uuid
    dataset_id = f"dataset-{uuid.uuid4().hex[:8]}"
    
    # Save file
    file_path = os.path.join(settings.DATASETS_DIR, f"{dataset_id}.{file.filename.split('.')[-1]}")
    
    # TODO: Implement actual file upload
    # For now, just create database entry
    
    dataset = Dataset(
        dataset_id=dataset_id,
        name=name or file.filename,
        description=description,
        format=file.filename.split('.')[-1],
        source="upload",
        local_path=file_path
    )
    
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    
    return {
        "message": "Dataset uploaded successfully",
        "dataset_id": dataset_id,
        "dataset": DatasetResponse.from_orm(dataset)
    }


@app.delete("/api/v1/datasets/{dataset_id}", tags=["Datasets"])
async def delete_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a dataset"""
    
    result = await db.execute(
        select(Dataset).where(Dataset.dataset_id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    await db.delete(dataset)
    await db.commit()
    
    return {"message": "Dataset deleted successfully", "dataset_id": dataset_id}


# ========== TRAINING API ==========

@app.post("/api/v1/training/start", response_model=TrainingJobResponse, tags=["Training"])
async def start_training(
    request: TrainingJobCreate,
    db: AsyncSession = Depends(get_db)
):
    """Start a new training job"""
    
    # Validate model exists
    model_result = await db.execute(
        select(Model).where(Model.model_id == request.model_id)
    )
    model = model_result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Validate dataset exists
    dataset_result = await db.execute(
        select(Dataset).where(Dataset.dataset_id == request.dataset_id)
    )
    dataset = dataset_result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Generate job ID
    import uuid
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    
    # Create training job
    lora_config = request.lora_config or {}
    training_config = request.training_config or {}
    
    job = TrainingJob(
        job_id=job_id,
        name=request.name,
        model_id=request.model_id,
        dataset_id=request.dataset_id,
        training_method=request.training_method.value,
        lora_rank=lora_config.rank if lora_config else settings.DEFAULT_LORA_RANK,
        lora_alpha=lora_config.alpha if lora_config else settings.DEFAULT_LORA_ALPHA,
        lora_dropout=lora_config.dropout if lora_config else settings.DEFAULT_LORA_DROPOUT,
        learning_rate=training_config.learning_rate if training_config else settings.DEFAULT_LEARNING_RATE,
        num_epochs=training_config.num_epochs if training_config else settings.DEFAULT_NUM_EPOCHS,
        batch_size=training_config.batch_size if training_config else settings.DEFAULT_BATCH_SIZE,
        gradient_accumulation_steps=training_config.gradient_accumulation_steps if training_config else settings.DEFAULT_GRADIENT_ACCUMULATION_STEPS,
        warmup_steps=training_config.warmup_steps if training_config else settings.DEFAULT_WARMUP_STEPS,
        max_seq_length=training_config.max_seq_length if training_config else settings.DEFAULT_MAX_SEQ_LENGTH,
        status="queued"
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Send job to training worker via Redis queue
    if redis_client:
        try:
            job_data = {
                "job_id": job_id,
                "model_id": request.model_id,
                "dataset_id": request.dataset_id,
                "training_method": request.training_method.value
            }
            redis_client.rpush(
                settings.REDIS_QUEUE_NAME,
                json.dumps(job_data)
            )
            logger.info(f"Job {job_id} added to training queue")
        except Exception as e:
            logger.error(f"Failed to queue job: {e}")
            # Update job status to failed
            job.status = "failed"
            job.error_message = f"Failed to queue job: {str(e)}"
            await db.commit()
            raise HTTPException(status_code=500, detail="Failed to queue training job")
    else:
        logger.warning("Redis not available. Job queued in database only.")
    
    return TrainingJobResponse.from_orm(job)


@app.get("/api/v1/training/{job_id}", response_model=TrainingJobResponse, tags=["Training"])
async def get_training_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Get training job status"""
    
    result = await db.execute(
        select(TrainingJob).where(TrainingJob.job_id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    return TrainingJobResponse.from_orm(job)


@app.get("/api/v1/training", response_model=TrainingJobListResponse, tags=["Training"])
async def list_training_jobs(
    page: int = 1,
    page_size: int = 20,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List all training jobs"""
    
    query = select(TrainingJob)
    
    if status:
        query = query.where(TrainingJob.status == status)
    
    # Get total
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    
    # Pagination
    query = query.order_by(TrainingJob.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return TrainingJobListResponse(
        jobs=[TrainingJobResponse.from_orm(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size
    )


@app.post("/api/v1/training/{job_id}/cancel", tags=["Training"])
async def cancel_training_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Cancel a training job"""
    
    result = await db.execute(
        select(TrainingJob).where(TrainingJob.job_id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    if job.status not in ["queued", "running"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {job.status}"
        )
    
    job.status = "cancelled"
    await db.commit()
    
    # TODO: Send cancel signal to training worker
    
    return {"message": "Training job cancelled", "job_id": job_id}


# ========== INFERENCE API ==========

@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Inference"])
async def chat_completion(request: ChatRequest):
    """Chat completion endpoint"""
    
    try:
        # Convert messages to dict format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Use model manager for inference
        result = await model_manager.chat(
            model_id=request.model_id,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stream=request.stream
        )
        
        import uuid
        request_id = f"req-{uuid.uuid4().hex[:8]}"
        
        return ChatResponse(
            request_id=request_id,
            model_id=request.model_id,
            response=result["response"],
            prompt_tokens=result["prompt_tokens"],
            response_tokens=result["response_tokens"],
            total_tokens=result["total_tokens"],
            latency_ms=result["latency_ms"],
            tokens_per_second=result["tokens_per_second"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat completion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate", response_model=GenerateResponse, tags=["Inference"])
async def text_generation(request: GenerateRequest):
    """Text generation endpoint"""
    
    try:
        # Use model manager for inference
        result = await model_manager.generate(
            model_id=request.model_id,
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            stop_sequences=request.stop_sequences,
            stream=False
        )
        
        import uuid
        request_id = f"req-{uuid.uuid4().hex[:8]}"
        
        return GenerateResponse(
            request_id=request_id,
            model_id=request.model_id,
            generated_text=result["generated_text"],
            tokens_generated=result["generated_tokens"],
            latency_ms=result["latency_ms"],
            tokens_per_second=result["tokens_per_second"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Text generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========== DASHBOARD API ==========

@app.get("/api/v1/dashboard/stats", response_model=DashboardStats, tags=["Dashboard"])
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics"""
    
    # Count models
    total_models = await db.execute(select(func.count()).select_from(Model))
    total_models = total_models.scalar()
    
    downloaded_models = await db.execute(
        select(func.count()).select_from(Model).where(Model.download_status == "downloaded")
    )
    downloaded_models = downloaded_models.scalar()
    
    finetuned_models = await db.execute(
        select(func.count()).select_from(Model).where(Model.is_finetuned == True)
    )
    finetuned_models = finetuned_models.scalar()
    
    # Count datasets
    total_datasets = await db.execute(select(func.count()).select_from(Dataset))
    total_datasets = total_datasets.scalar()
    
    # Count training jobs
    total_jobs = await db.execute(select(func.count()).select_from(TrainingJob))
    total_jobs = total_jobs.scalar()
    
    active_jobs = await db.execute(
        select(func.count()).select_from(TrainingJob).where(
            TrainingJob.status.in_(["queued", "running"])
        )
    )
    active_jobs = active_jobs.scalar()
    
    completed_jobs = await db.execute(
        select(func.count()).select_from(TrainingJob).where(TrainingJob.status == "completed")
    )
    completed_jobs = completed_jobs.scalar()
    
    failed_jobs = await db.execute(
        select(func.count()).select_from(TrainingJob).where(TrainingJob.status == "failed")
    )
    failed_jobs = failed_jobs.scalar()
    
    # Disk space (mock for now)
    import shutil
    disk = shutil.disk_usage("/")
    
    return DashboardStats(
        total_models=total_models,
        downloaded_models=downloaded_models,
        finetuned_models=finetuned_models,
        total_datasets=total_datasets,
        total_training_jobs=total_jobs,
        active_training_jobs=active_jobs,
        completed_training_jobs=completed_jobs,
        failed_training_jobs=failed_jobs,
        total_disk_space_gb=disk.total / (1024**3),
        used_disk_space_gb=disk.used / (1024**3),
        models_disk_space_gb=0.0,  # TODO: Calculate actual
        datasets_disk_space_gb=0.0  # TODO: Calculate actual
    )


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
