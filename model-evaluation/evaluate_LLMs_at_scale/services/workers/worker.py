import asyncio
import logging
import sys
import time
from datetime import datetime
sys.path.append('../shared')

from shared.database import DatabaseManager, EvaluationTask
from shared.rabbitmq_client import RabbitMQClient, Queues
from shared.redis_client import RedisClient
from shared.models import EvaluationTaskMessage, MetricsCalculationMessage
from sqlalchemy import select
from gemini_client import GeminiClient
from gpt_client import GPTClient
from claude_client import ClaudeClient
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_manager = DatabaseManager(settings.DATABASE_URL)
rabbitmq = RabbitMQClient(settings.RABBITMQ_URL)
redis_client = RedisClient(settings.REDIS_URL)


class EvaluationWorker:
    """Worker for processing LLM evaluation tasks"""
    
    def __init__(self, worker_type: str):
        self.worker_type = worker_type
        self.client = self._get_client()
    
    def _get_client(self):
        """Get appropriate LLM client"""
        if self.worker_type == "gemini":
            return GeminiClient(settings.GEMINI_API_KEY)
        elif self.worker_type == "gpt":
            return GPTClient(settings.OPENAI_API_KEY)
        elif self.worker_type == "claude":
            return ClaudeClient(settings.ANTHROPIC_API_KEY)
        else:
            raise ValueError(f"Unknown worker type: {self.worker_type}")
    
    async def start(self):
        """Start worker"""
        await rabbitmq.connect()
        logger.info(f"{self.worker_type.upper()} worker started")
        
        await rabbitmq.consume(
            Queues.EVALUATION_TASKS,
            self.process_task
        )
    
    async def process_task(self, message: dict):
        """Process a single evaluation task"""
        task_msg = EvaluationTaskMessage(**message)
        
        logger.info(f"Processing task {task_msg.task_id} for model {task_msg.model}")
        
        # Skip if not for this worker
        if not self._should_process(task_msg.model):
            logger.debug(f"Skipping task for model {task_msg.model}")
            return
        
        async for session in db_manager.get_session():
            result = await session.execute(
                select(EvaluationTask).where(EvaluationTask.id == task_msg.task_id)
            )
            task = result.scalar_one_or_none()
            
            if not task:
                logger.error(f"Task {task_msg.task_id} not found")
                return
            
            # Update status
            task.status = "running"
            task.started_at = datetime.utcnow()
            await session.commit()
            
            try:
                # Check cache
                cached = await redis_client.get_cached_response(
                    task_msg.model,
                    task_msg.prompt
                )
                
                if cached:
                    logger.info(f"Cache hit for task {task_msg.task_id}")
                    response = cached["response"]
                    tokens_used = cached["tokens_used"]
                    cost_usd = cached["cost_usd"]
                    latency_ms = 0  # Cached, instant
                
                else:
                    # Call LLM API
                    start_time = time.time()
                    
                    result = await self.client.generate(
                        prompt=task_msg.prompt,
                        model=task_msg.model
                    )
                    
                    latency_ms = int((time.time() - start_time) * 1000)
                    response = result["response"]
                    tokens_used = result["tokens_used"]
                    cost_usd = result["cost_usd"]
                    
                    # Cache response
                    await redis_client.cache_response(
                        task_msg.model,
                        task_msg.prompt,
                        {
                            "response": response,
                            "tokens_used": tokens_used,
                            "cost_usd": cost_usd
                        }
                    )
                
                # Update task
                task.response = response
                task.tokens_used = tokens_used
                task.cost_usd = cost_usd
                task.latency_ms = latency_ms
                task.status = "completed"
                task.completed_at = datetime.utcnow()
                await session.commit()
                
                logger.info(
                    f"Task {task_msg.task_id} completed: "
                    f"{tokens_used} tokens, ${cost_usd:.6f}, {latency_ms}ms"
                )
                
                # Publish to metrics queue
                metrics_msg = MetricsCalculationMessage(
                    task_id=task_msg.task_id,
                    response=response,
                    reference=task_msg.reference,
                    metrics=task_msg.metrics
                )
                await rabbitmq.publish(
                    Queues.METRICS_CALCULATION,
                    metrics_msg.dict()
                )
                
                # Notify completion
                await rabbitmq.publish(
                    Queues.EVALUATION_TASKS + "_completed",
                    {"task_id": str(task_msg.task_id), "status": "completed"}
                )
                
            except Exception as e:
                logger.error(f"Error processing task {task_msg.task_id}: {e}")
                
                task.status = "failed"
                task.error_message = str(e)
                task.retry_count += 1
                task.completed_at = datetime.utcnow()
                await session.commit()
                
                # Retry or send to DLQ
                if task.retry_count < task.max_retries:
                    logger.info(f"Retrying task {task_msg.task_id} ({task.retry_count}/{task.max_retries})")
                    await rabbitmq.publish(
                        Queues.EVALUATION_TASKS,
                        message,
                        priority=task_msg.dict().get("priority", 1)
                    )
                else:
                    logger.warning(f"Task {task_msg.task_id} sent to DLQ after {task.retry_count} retries")
                
                # Notify failure
                await rabbitmq.publish(
                    Queues.EVALUATION_TASKS + "_completed",
                    {"task_id": str(task_msg.task_id), "status": "failed"}
                )
    
    def _should_process(self, model: str) -> bool:
        """Check if this worker should process the model"""
        model_lower = model.lower()
        
        if self.worker_type == "gemini":
            return "gemini" in model_lower
        elif self.worker_type == "gpt":
            return "gpt" in model_lower or "openai" in model_lower
        elif self.worker_type == "claude":
            return "claude" in model_lower or "anthropic" in model_lower
        
        return False
    
    async def shutdown(self):
        """Graceful shutdown"""
        await rabbitmq.close()
        await redis_client.close()
        await db_manager.close()
        logger.info(f"{self.worker_type.upper()} worker shut down")


async def main():
    if len(sys.argv) < 2:
        print("Usage: python worker.py <gemini|gpt|claude>")
        sys.exit(1)
    
    worker_type = sys.argv[1]
    worker = EvaluationWorker(worker_type)
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await worker.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
