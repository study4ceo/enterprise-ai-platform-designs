import asyncio
import logging
import sys
sys.path.append('../shared')

from shared.database import DatabaseManager, EvaluationResult
from shared.rabbitmq_client import RabbitMQClient, Queues
from shared.redis_client import RedisClient
from shared.models import MetricsCalculationMessage
from calculators.bleu import calculate_bleu
from calculators.rouge import calculate_rouge
from calculators.bertscore import calculate_bertscore
from calculators.exact_match import calculate_exact_match
from calculators.toxicity import calculate_toxicity
from calculators.hallucination import detect_hallucination
from calculators.bias import detect_bias
from calculators.pii import detect_pii
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_manager = DatabaseManager(settings.DATABASE_URL)
rabbitmq = RabbitMQClient(settings.RABBITMQ_URL)
redis_client = RedisClient(settings.REDIS_URL)


class MetricsService:
    """Service for calculating evaluation metrics"""
    
    def __init__(self):
        self.calculators = {
            "bleu": calculate_bleu,
            "rouge": calculate_rouge,
            "bertscore": calculate_bertscore,
            "exact_match": calculate_exact_match,
            "toxicity": calculate_toxicity,
            "hallucination": detect_hallucination,
            "bias": detect_bias,
            "pii": detect_pii,
        }
    
    async def start(self):
        """Start metrics service"""
        await rabbitmq.connect()
        logger.info("Metrics service started")
        
        await rabbitmq.consume(
            Queues.METRICS_CALCULATION,
            self.calculate_metrics
        )
    
    async def calculate_metrics(self, message: dict):
        """Calculate all requested metrics for a task"""
        msg = MetricsCalculationMessage(**message)
        
        logger.info(f"Calculating metrics for task {msg.task_id}")
        
        # Check cache
        cached = await redis_client.get_cached_metrics(str(msg.task_id))
        if cached:
            logger.info(f"Metrics cache hit for task {msg.task_id}")
            return
        
        results = []
        
        for metric_name in msg.metrics:
            try:
                calculator = self.calculators.get(metric_name.lower())
                if not calculator:
                    logger.warning(f"Unknown metric: {metric_name}")
                    continue
                
                # Calculate metric
                score = await calculator(
                    candidate=msg.response,
                    reference=msg.reference
                )
                
                results.append({
                    "metric_name": metric_name,
                    "score": score,
                    "task_id": str(msg.task_id)
                })
                
                logger.info(f"Task {msg.task_id} - {metric_name}: {score:.4f}")
            
            except Exception as e:
                logger.error(f"Error calculating {metric_name}: {e}")
                results.append({
                    "metric_name": metric_name,
                    "score": 0.0,
                    "error": str(e),
                    "task_id": str(msg.task_id)
                })
        
        # Store results in database
        async for session in db_manager.get_session():
            for result in results:
                eval_result = EvaluationResult(
                    task_id=msg.task_id,
                    metrics=result,
                    metric_type=result["metric_name"],
                    score=result["score"]
                )
                session.add(eval_result)
            
            await session.commit()
        
        # Cache results
        await redis_client.cache_metrics(
            str(msg.task_id),
            {"metrics": results}
        )
        
        logger.info(f"Stored {len(results)} metrics for task {msg.task_id}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        await rabbitmq.close()
        await redis_client.close()
        await db_manager.close()
        logger.info("Metrics service shut down")


async def main():
    service = MetricsService()
    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
