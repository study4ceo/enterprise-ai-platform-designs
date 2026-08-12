from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
import sys
sys.path.append('../shared')

from shared.database import DatabaseManager, Job, EvaluationTask, EvaluationResult, JobStatus
from shared.models import DeploymentReadinessReport
from shared.redis_client import RedisClient
from config import settings
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Analytics Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_manager = DatabaseManager(settings.DATABASE_URL)
redis_client = RedisClient(settings.REDIS_URL)

# Configure Gemini for chat
genai.configure(api_key=settings.GEMINI_API_KEY)
chat_model = genai.GenerativeModel('gemini-pro')


@app.on_event("startup")
async def startup():
    await redis_client.connect()
    logger.info("Analytics service started")


@app.on_event("shutdown")
async def shutdown():
    await redis_client.close()
    await db_manager.close()
    logger.info("Analytics service stopped")


async def get_session():
    async for session in db_manager.get_session():
        yield session


@app.get("/api/v1/dashboard/stats")
async def get_dashboard_stats(session: AsyncSession = Depends(get_session)):
    """Get dashboard statistics"""
    
    # Total jobs
    total_jobs_query = select(func.count(Job.id))
    total_jobs = await session.scalar(total_jobs_query)
    
    # Active jobs
    active_jobs_query = select(func.count(Job.id)).where(
        Job.status.in_([JobStatus.RUNNING, JobStatus.QUEUED])
    )
    active_jobs = await session.scalar(active_jobs_query)
    
    # Completed today
    today = datetime.now().date()
    completed_today_query = select(func.count(Job.id)).where(
        and_(
            Job.status == JobStatus.COMPLETED,
            func.date(Job.completed_at) == today
        )
    )
    completed_today = await session.scalar(completed_today_query)
    
    # Total cost
    total_cost_query = select(func.sum(Job.total_cost_usd))
    total_cost = await session.scalar(total_cost_query) or 0.0
    
    # Average latency
    avg_latency_query = select(func.avg(EvaluationTask.latency_ms)).where(
        EvaluationTask.latency_ms.isnot(None)
    )
    avg_latency = await session.scalar(avg_latency_query) or 0
    
    # Success rate
    total_tasks_query = select(func.count(EvaluationTask.id))
    total_tasks = await session.scalar(total_tasks_query) or 1
    
    completed_tasks_query = select(func.count(EvaluationTask.id)).where(
        EvaluationTask.status == "completed"
    )
    completed_tasks = await session.scalar(completed_tasks_query) or 0
    
    success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return {
        "totalJobs": total_jobs or 0,
        "activeJobs": active_jobs or 0,
        "completedToday": completed_today or 0,
        "totalCost": float(total_cost),
        "avgLatency": float(avg_latency),
        "successRate": float(success_rate)
    }


@app.get("/api/v1/jobs/{job_id}/analytics")
async def get_job_analytics(
    job_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get detailed analytics for a job"""
    
    # Get job
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get tasks
    tasks_query = select(EvaluationTask).where(EvaluationTask.job_id == job_id)
    tasks_result = await session.execute(tasks_query)
    tasks = tasks_result.scalars().all()
    
    # Calculate statistics
    total_tasks = len(tasks)
    completed = sum(1 for t in tasks if t.status == "completed")
    failed = sum(1 for t in tasks if t.status == "failed")
    
    latencies = [t.latency_ms for t in tasks if t.latency_ms]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    costs = [t.cost_usd for t in tasks if t.cost_usd]
    total_cost = sum(costs)
    
    # Get metrics
    metrics_query = select(EvaluationResult).where(
        EvaluationResult.task_id.in_([t.id for t in tasks])
    )
    metrics_result = await session.execute(metrics_query)
    metrics = metrics_result.scalars().all()
    
    # Aggregate metrics by type
    metrics_by_type = {}
    for metric in metrics:
        metric_type = metric.metric_type
        if metric_type not in metrics_by_type:
            metrics_by_type[metric_type] = []
        metrics_by_type[metric_type].append(metric.score)
    
    avg_metrics = {
        metric_type: sum(scores) / len(scores)
        for metric_type, scores in metrics_by_type.items()
    }
    
    return {
        "job_id": str(job_id),
        "total_tasks": total_tasks,
        "completed": completed,
        "failed": failed,
        "success_rate": (completed / total_tasks * 100) if total_tasks > 0 else 0,
        "avg_latency_ms": avg_latency,
        "total_cost_usd": total_cost,
        "metrics": avg_metrics,
        "latency_distribution": {
            "p50": sorted(latencies)[len(latencies)//2] if latencies else 0,
            "p95": sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0,
            "p99": sorted(latencies)[int(len(latencies)*0.99)] if latencies else 0
        }
    }


@app.get("/api/v1/models/comparison")
async def get_model_comparison(
    session: AsyncSession = Depends(get_session)
):
    """Compare performance across models"""
    
    # Get all tasks grouped by model
    tasks_query = select(EvaluationTask)
    tasks_result = await session.execute(tasks_query)
    tasks = tasks_result.scalars().all()
    
    models_data = {}
    
    for task in tasks:
        model = task.model
        if model not in models_data:
            models_data[model] = {
                "model": model,
                "total_tasks": 0,
                "completed": 0,
                "failed": 0,
                "total_cost": 0,
                "total_latency": 0,
                "latencies": [],
                "metrics": {}
            }
        
        data = models_data[model]
        data["total_tasks"] += 1
        
        if task.status == "completed":
            data["completed"] += 1
        elif task.status == "failed":
            data["failed"] += 1
        
        if task.cost_usd:
            data["total_cost"] += task.cost_usd
        
        if task.latency_ms:
            data["total_latency"] += task.latency_ms
            data["latencies"].append(task.latency_ms)
    
    # Get metrics for each model
    for model, data in models_data.items():
        task_ids = [t.id for t in tasks if t.model == model]
        
        metrics_query = select(EvaluationResult).where(
            EvaluationResult.task_id.in_(task_ids)
        )
        metrics_result = await session.execute(metrics_query)
        metrics = metrics_result.scalars().all()
        
        metrics_by_type = {}
        for metric in metrics:
            metric_type = metric.metric_type
            if metric_type not in metrics_by_type:
                metrics_by_type[metric_type] = []
            metrics_by_type[metric_type].append(metric.score)
        
        data["metrics"] = {
            metric_type: sum(scores) / len(scores)
            for metric_type, scores in metrics_by_type.items()
        }
    
    # Calculate aggregates
    comparison = []
    for model, data in models_data.items():
        latencies = data["latencies"]
        comparison.append({
            "model": model,
            "total_tasks": data["total_tasks"],
            "success_rate": (data["completed"] / data["total_tasks"] * 100) if data["total_tasks"] > 0 else 0,
            "avg_cost_per_task": data["total_cost"] / data["total_tasks"] if data["total_tasks"] > 0 else 0,
            "avg_latency_ms": data["total_latency"] / data["completed"] if data["completed"] > 0 else 0,
            "p95_latency_ms": sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0,
            "metrics": data["metrics"]
        })
    
    return {"models": comparison}


@app.get("/api/v1/costs/breakdown")
async def get_cost_breakdown(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """Get cost breakdown by model and time"""
    
    query = select(
        EvaluationTask.model,
        func.date(EvaluationTask.created_at).label('date'),
        func.sum(EvaluationTask.cost_usd).label('total_cost'),
        func.count(EvaluationTask.id).label('task_count')
    ).group_by(
        EvaluationTask.model,
        func.date(EvaluationTask.created_at)
    )
    
    if start_date:
        query = query.where(EvaluationTask.created_at >= start_date)
    if end_date:
        query = query.where(EvaluationTask.created_at <= end_date)
    
    result = await session.execute(query)
    rows = result.all()
    
    breakdown = []
    for row in rows:
        breakdown.append({
            "model": row.model,
            "date": str(row.date),
            "total_cost": float(row.total_cost or 0),
            "task_count": row.task_count
        })
    
    return {"breakdown": breakdown}


@app.get("/api/v1/deployment/readiness")
async def get_deployment_readiness(
    session: AsyncSession = Depends(get_session)
):
    """Get deployment readiness for all models"""
    
    # This would typically query from a deployment_readiness table
    # For now, we'll calculate it from metrics
    
    models_comparison = await get_model_comparison(session=session)
    
    readiness_reports = []
    
    for model_data in models_comparison["models"]:
        # Calculate scores (simplified example)
        metrics = model_data["metrics"]
        
        # Performance score (25%)
        bertscore = metrics.get("bertscore", 0) * 100
        rouge = metrics.get("rouge", 0) * 100
        performance_score = (bertscore + rouge) / 2
        
        # Business score (25%)
        cost_per_task = model_data["avg_cost_per_task"]
        cost_score = max(0, 100 - (cost_per_task * 10000))  # Lower cost = higher score
        business_score = cost_score
        
        # Safety score (35%)
        toxicity = 1 - metrics.get("toxicity", 0)
        hallucination = 1 - metrics.get("hallucination", 0)
        safety_score = ((toxicity + hallucination) / 2) * 100
        
        # Operational score (15%)
        success_rate = model_data["success_rate"]
        operational_score = success_rate
        
        # Overall score (weighted)
        overall_score = (
            performance_score * 0.25 +
            business_score * 0.25 +
            safety_score * 0.35 +
            operational_score * 0.15
        )
        
        # Determine status
        if overall_score >= 80:
            status = "APPROVED"
        elif overall_score >= 60:
            status = "CONDITIONAL"
        else:
            status = "REJECTED"
        
        deployment_ready = overall_score >= 70
        
        readiness_reports.append({
            "model_name": model_data["model"],
            "overall_score": overall_score,
            "performance_score": performance_score,
            "business_score": business_score,
            "safety_score": safety_score,
            "operational_score": operational_score,
            "deployment_ready": deployment_ready,
            "status": status,
            "critical_issues": [] if deployment_ready else ["Overall score below threshold"],
            "warnings": [],
            "recommendations": [],
            "evaluated_at": datetime.now().isoformat(),
            "performance": model_data,
            "business": {"cost_per_task": cost_per_task},
            "safety": metrics,
            "operational": {"success_rate": success_rate}
        })
    
    return readiness_reports


@app.post("/api/v1/chat/query")
async def chat_query(
    request: Dict[str, Any],
    session: AsyncSession = Depends(get_session)
):
    """Handle natural language queries about evaluation data"""
    
    query = request.get("query", "")
    
    # Get context data
    stats = await get_dashboard_stats(session=session)
    models = await get_model_comparison(session=session)
    
    # Build context for LLM
    context = f"""
You are an analytics assistant for an LLM evaluation system. Answer questions about the evaluation data.

Current Statistics:
- Total Jobs: {stats['totalJobs']}
- Active Jobs: {stats['activeJobs']}
- Total Cost: ${stats['totalCost']:.2f}
- Success Rate: {stats['successRate']:.1f}%

Models Performance:
{chr(10).join([f"- {m['model']}: {m['success_rate']:.1f}% success, ${m['avg_cost_per_task']:.4f} per task, {m['avg_latency_ms']:.0f}ms latency" for m in models['models']])}

User Question: {query}

Provide a helpful, concise answer based on the data above.
"""
    
    try:
        # Query Gemini
        chat = chat_model.start_chat(history=[])
        response = chat.send_message(context)
        
        return {
            "answer": response.text,
            "data": {
                "stats": stats,
                "models": models["models"]
            }
        }
    except Exception as e:
        logger.error(f"Chat query failed: {e}")
        return {
            "answer": "I encountered an error processing your query. Please try rephrasing your question.",
            "data": None
        }


@app.get("/api/v1/export/{job_id}")
async def export_job(
    job_id: str,
    format: str = Query("json", regex="^(json|csv|pdf)$"),
    session: AsyncSession = Depends(get_session)
):
    """Export job results"""
    
    analytics = await get_job_analytics(job_id, session=session)
    
    if format == "json":
        return analytics
    elif format == "csv":
        # Simple CSV export (would use pandas in real implementation)
        return {"message": "CSV export not yet implemented"}
    elif format == "pdf":
        # PDF export (would use reportlab in real implementation)
        return {"message": "PDF export not yet implemented"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "analytics"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
