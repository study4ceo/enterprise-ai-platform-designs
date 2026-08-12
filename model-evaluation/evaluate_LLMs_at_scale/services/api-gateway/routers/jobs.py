from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List
from uuid import UUID
import sys
sys.path.append('../../shared')

from shared.database import User, EvaluationJob, EvaluationTask
from shared.models import JobCreate, JobResponse, JobListResponse, TaskResponse
from shared.rabbitmq_client import RabbitMQClient, Queues
from shared.models import EvaluationTaskMessage
from database import get_db
from routers.auth import get_current_user
from config import settings

router = APIRouter()
rabbitmq = RabbitMQClient(settings.RABBITMQ_URL)


@router.on_event("startup")
async def startup():
    await rabbitmq.connect()


@router.on_event("shutdown")
async def shutdown():
    await rabbitmq.close()


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new evaluation job"""
    
    # Create job
    total_tasks = len(job_data.models) * len(job_data.prompts)
    
    job = EvaluationJob(
        user_id=current_user.id,
        name=job_data.name,
        priority=job_data.priority,
        total_tasks=total_tasks,
        metadata=job_data.metadata
    )
    db.add(job)
    await db.flush()
    
    # Create tasks
    tasks = []
    for model in job_data.models:
        for i, prompt in enumerate(job_data.prompts):
            reference = job_data.references[i] if job_data.references and i < len(job_data.references) else None
            
            task = EvaluationTask(
                job_id=job.id,
                model=model,
                prompt=prompt,
                reference=reference
            )
            db.add(task)
            tasks.append(task)
    
    await db.commit()
    await db.refresh(job)
    
    # Publish tasks to queue
    for task in tasks:
        message = EvaluationTaskMessage(
            task_id=task.id,
            job_id=job.id,
            model=task.model,
            prompt=task.prompt,
            reference=task.reference,
            metrics=job_data.metrics
        )
        await rabbitmq.publish(
            Queues.EVALUATION_TASKS,
            message.dict(),
            priority=job_data.priority
        )
    
    return job


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's evaluation jobs"""
    
    # Build query
    query = select(EvaluationJob).where(EvaluationJob.user_id == current_user.id)
    
    if status:
        query = query.where(EvaluationJob.status == status)
    
    # Count total
    count_query = select(func.count()).select_from(EvaluationJob).where(
        EvaluationJob.user_id == current_user.id
    )
    if status:
        count_query = count_query.where(EvaluationJob.status == status)
    
    total = await db.scalar(count_query)
    
    # Paginate
    query = query.order_by(EvaluationJob.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return JobListResponse(
        jobs=jobs,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get job details"""
    
    result = await db.execute(
        select(EvaluationJob).where(
            and_(
                EvaluationJob.id == job_id,
                EvaluationJob.user_id == current_user.id
            )
        )
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a job"""
    
    result = await db.execute(
        select(EvaluationJob).where(
            and_(
                EvaluationJob.id == job_id,
                EvaluationJob.user_id == current_user.id
            )
        )
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {job.status}"
        )
    
    job.status = "cancelled"
    await db.commit()


@router.get("/{job_id}/tasks", response_model=List[TaskResponse])
async def get_job_tasks(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks for a job"""
    
    # Verify job ownership
    job_result = await db.execute(
        select(EvaluationJob).where(
            and_(
                EvaluationJob.id == job_id,
                EvaluationJob.user_id == current_user.id
            )
        )
    )
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get tasks
    result = await db.execute(
        select(EvaluationTask).where(EvaluationTask.job_id == job_id)
    )
    tasks = result.scalars().all()
    
    return tasks


@router.get("/{job_id}/results")
async def get_job_results(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get aggregated results for a job"""
    
    # Verify job ownership
    job_result = await db.execute(
        select(EvaluationJob).where(
            and_(
                EvaluationJob.id == job_id,
                EvaluationJob.user_id == current_user.id
            )
        )
    )
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get tasks with results
    query = """
        SELECT 
            t.model,
            COUNT(*) as total_tasks,
            AVG(t.cost_usd) as avg_cost,
            AVG(t.latency_ms) as avg_latency,
            AVG(r.score) as avg_score
        FROM evaluation_tasks t
        LEFT JOIN evaluation_results r ON t.id = r.task_id
        WHERE t.job_id = :job_id
        GROUP BY t.model
    """
    
    result = await db.execute(query, {"job_id": str(job_id)})
    results = result.fetchall()
    
    return {
        "job_id": str(job_id),
        "job_name": job.name,
        "status": job.status,
        "total_cost_usd": job.total_cost_usd,
        "results_by_model": [
            {
                "model": row[0],
                "total_tasks": row[1],
                "avg_cost_usd": float(row[2]) if row[2] else 0,
                "avg_latency_ms": float(row[3]) if row[3] else 0,
                "avg_score": float(row[4]) if row[4] else 0
            }
            for row in results
        ]
    }
