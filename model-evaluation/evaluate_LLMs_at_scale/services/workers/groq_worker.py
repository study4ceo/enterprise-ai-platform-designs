import asyncio
import logging
import sys
import time
import hashlib
sys.path.append('../shared')

from groq import Groq
from shared.database import DatabaseManager, EvaluationTask
from shared.rabbitmq_client import RabbitMQClient, Queues
from shared.redis_client import RedisClient
from shared.models import EvaluationTaskMessage, MetricsCalculationMessage
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
groq_client = Groq(api_key=settings.GROQ_API_KEY)
db_manager = DatabaseManager(settings.DATABASE_URL)
rabbitmq = RabbitMQClient(settings.RABBITMQ_URL)
redis_client = RedisClient(settings.REDIS_URL)

# Groq pricing per 1M tokens (input, output)
GROQ_PRICING = {
    "llama-3.1-405b-reasoning": (0.0, 0.0),  # Currently free during preview
    "llama-3.1-70b-versatile": (0.59, 0.79),
    "llama-3.1-8b-instant": (0.05, 0.08),
    "llama-3.2-90b-vision-preview": (0.90, 0.90),
    "llama-3.2-11b-vision-preview": (0.18, 0.18),
    "llama-3.2-3b-preview": (0.06, 0.06),
    "llama-3.2-1b-preview": (0.04, 0.04),
    "mixtral-8x7b-32768": (0.24, 0.24),
    "gemma2-9b-it": (0.20, 0.20),
    "gemma-7b-it": (0.07, 0.07),
}

# Rate limits (requests per minute for free tier)
FREE_TIER_RPM = 30
FREE_TIER_TPM = 14400


class GroqWorker:
    """Worker for processing LLM tasks using Groq API"""
    
    def __init__(self):
        self.request_count = 0
        self.last_reset = time.time()
    
    async def start(self):
        """Start the Groq worker"""
        await rabbitmq.connect()
        logger.info("Groq worker started - Lightning fast inference! ⚡")
        logger.info(f"Free tier limits: {FREE_TIER_RPM} req/min, {FREE_TIER_TPM} tokens/min")
        
        await rabbitmq.consume(
            Queues.LLM_TASKS,
            self.process_task
        )
    
    def _get_cache_key(self, model: str, prompt: str) -> str:
        """Generate cache key for response"""
        content = f"{model}:{prompt}"
        return f"groq:{hashlib.md5(content.encode()).hexdigest()}"
    
    async def _check_rate_limit(self):
        """Simple rate limiting for free tier"""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.last_reset >= 60:
            self.request_count = 0
            self.last_reset = current_time
        
        # Check if we're at the limit
        if self.request_count >= FREE_TIER_RPM:
            wait_time = 60 - (current_time - self.last_reset)
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.last_reset = time.time()
        
        self.request_count += 1
    
    async def process_task(self, message: dict):
        """Process a single evaluation task"""
        msg = EvaluationTaskMessage(**message)
        
        logger.info(f"Processing task {msg.task_id} with model {msg.model}")
        
        # Update task status to running
        async for session in db_manager.get_session():
            task = await session.get(EvaluationTask, msg.task_id)
            if not task:
                logger.error(f"Task {msg.task_id} not found")
                return
            
            task.status = "running"
            await session.commit()
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(msg.model, msg.prompt)
            cached_response = await redis_client.get_cached_response(cache_key)
            
            if cached_response:
                logger.info(f"Cache hit for task {msg.task_id}")
                response_text = cached_response
                tokens_used = 0
                cost = 0.0
                latency_ms = 0
            else:
                # Check rate limit
                await self._check_rate_limit()
                
                # Call Groq API
                start_time = time.time()
                
                logger.info(f"Calling Groq API with model {msg.model}")
                
                response = groq_client.chat.completions.create(
                    model=msg.model,
                    messages=[
                        {
                            "role": "user",
                            "content": msg.prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2048,
                    top_p=1,
                    stream=False
                )
                
                latency_ms = int((time.time() - start_time) * 1000)
                
                # Extract response
                response_text = response.choices[0].message.content
                
                # Calculate tokens and cost
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                tokens_used = input_tokens + output_tokens
                
                # Get pricing for model
                pricing = GROQ_PRICING.get(msg.model, (0.5, 0.5))
                cost = (
                    (input_tokens / 1_000_000 * pricing[0]) +
                    (output_tokens / 1_000_000 * pricing[1])
                )
                
                logger.info(
                    f"Task {msg.task_id} completed: "
                    f"{tokens_used} tokens, "
                    f"${cost:.6f}, "
                    f"{latency_ms}ms (⚡ Groq speed!)"
                )
                
                # Cache the response
                await redis_client.cache_response(cache_key, response_text)
            
            # Update task with results
            async for session in db_manager.get_session():
                task = await session.get(EvaluationTask, msg.task_id)
                if task:
                    task.status = "completed"
                    task.response = response_text
                    task.tokens_used = tokens_used
                    task.cost_usd = cost
                    task.latency_ms = latency_ms
                    task.completed_at = db_manager.utcnow()
                    await session.commit()
            
            # Publish to metrics queue
            if msg.metrics and len(msg.metrics) > 0:
                metrics_msg = MetricsCalculationMessage(
                    task_id=msg.task_id,
                    response=response_text,
                    reference=msg.reference,
                    metrics=msg.metrics
                )
                await rabbitmq.publish(
                    Queues.METRICS_CALCULATION,
                    metrics_msg.dict()
                )
            
            logger.info(f"Task {msg.task_id} completed successfully")
        
        except Exception as e:
            logger.error(f"Error processing task {msg.task_id}: {e}")
            
            # Update task with error
            async for session in db_manager.get_session():
                task = await session.get(EvaluationTask, msg.task_id)
                if task:
                    task.retry_count += 1
                    
                    if task.retry_count >= 3:
                        task.status = "failed"
                        task.error_message = str(e)
                        
                        # Send to dead letter queue
                        await rabbitmq.publish(
                            Queues.DEAD_LETTER,
                            {
                                "task_id": str(msg.task_id),
                                "error": str(e),
                                "retry_count": task.retry_count,
                                "original_message": message
                            }
                        )
                    else:
                        task.status = "retrying"
                        
                        # Re-queue with delay
                        await asyncio.sleep(2 ** task.retry_count)
                        await rabbitmq.publish(
                            Queues.LLM_TASKS,
                            message,
                            priority=msg.retry_count
                        )
                    
                    await session.commit()
    
    async def shutdown(self):
        """Graceful shutdown"""
        await rabbitmq.close()
        await redis_client.close()
        await db_manager.close()
        logger.info("Groq worker shut down")


async def main():
    worker = GroqWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await worker.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
