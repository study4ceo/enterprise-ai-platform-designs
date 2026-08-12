import asyncio
import logging
from datetime import datetime
import sys
sys.path.append('../shared')

from shared.database import DatabaseManager, EvaluationJob, EvaluationTask
from shared.rabbitmq_client import RabbitMQClient, Queues
from shared.redis_client import RedisClient
from sqlalchemy import select, and_
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_manager = DatabaseManager(settings.DATABASE_URL)
rabbitmq = RabbitMQClient(settings.RABBITMQ_URL)
redis_client = RedisClient(settings.REDIS_URL)


class JobOrchestrator:
    """Orchestrates evaluation jobs and updates status"""
    
    def __init__(self):
        self.running = True
    
    async def start(self):
        """Start orchestrator"""
        await rabbitmq.connect()
        logger.info("Orchestrator started")
        
        # Start monitoring jobs
        asyncio.create_task(self.monitor_jobs())
        
        # Consume task completion messages
        await rabbitmq.consume(
            Queues.EVALUATION_TASKS + "_completed",
            self.handle_task_completed
        )
    
    async def monitor_jobs(self):
        """Monitor and update job statuses"""
        while self.running:
            try:
                async for session in db_manager.get_session():
                    # Get running jobs
                    result = await session.execute(
                        select(EvaluationJob).where(
                            EvaluationJob.status.in_(["queued", "running"])
                        )
                    )
                    jobs = result.scalars().all()
                    
                    for job in jobs:
                        await self.update_job_status(session, job)
                    
                    await session.commit()
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring jobs: {e}")
                await asyncio.sleep(10)
    
    async def update_job_status(self, session, job):
        """Update job status based on tasks"""
        # Count task statuses
        result = await session.execute(
            select(EvaluationTask).where(EvaluationTask.job_id == job.id)
        )
        tasks = result.scalars().all()
        
        completed = sum(1 for t in tasks if t.status == "completed")
        failed = sum(1 for t in tasks if t.status == "failed")
        running = sum(1 for t in tasks if t.status == "running")
        
        # Update job
        job.completed_tasks = completed
        job.failed_tasks = failed
        
        # Calculate total cost
        total_cost = sum(t.cost_usd or 0 for t in tasks)
        job.total_cost_usd = total_cost
        
        # Update job status
        if job.status == "queued" and running > 0:
            job.status = "running"
            job.started_at = datetime.utcnow()
        
        elif completed + failed == len(tasks):
            job.status = "completed" if failed == 0 else "failed"
            job.completed_at = datetime.utcnow()
        
        # Update Redis cache for real-time progress
        await redis_client.update_job_progress(
            str(job.id),
            completed + failed,
            len(tasks)
        )
        
        logger.info(
            f"Job {job.id}: {completed}/{len(tasks)} completed, "
            f"{failed} failed, ${total_cost:.4f} cost"
        )
    
    async def handle_task_completed(self, message: dict):
        """Handle task completion message"""
        task_id = message.get("task_id")
        status = message.get("status")
        
        logger.info(f"Task {task_id} completed with status: {status}")
        
        async for session in db_manager.get_session():
            result = await session.execute(
                select(EvaluationTask).where(EvaluationTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            
            if task:
                # Update job immediately
                job_result = await session.execute(
                    select(EvaluationJob).where(EvaluationJob.id == task.job_id)
                )
                job = job_result.scalar_one_or_none()
                
                if job:
                    await self.update_job_status(session, job)
                
                await session.commit()
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        await rabbitmq.close()
        await redis_client.close()
        await db_manager.close()
        logger.info("Orchestrator shut down")


async def main():
    orchestrator = JobOrchestrator()
    try:
        await orchestrator.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
