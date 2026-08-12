import aio_pika
import json
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)


class RabbitMQClient:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None
        
    async def connect(self):
        """Establish connection to RabbitMQ"""
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)
        logger.info("Connected to RabbitMQ")
    
    async def close(self):
        """Close connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Closed RabbitMQ connection")
    
    async def declare_queue(self, queue_name: str, durable: bool = True):
        """Declare a queue"""
        return await self.channel.declare_queue(
            queue_name,
            durable=durable,
            arguments={
                "x-dead-letter-exchange": "dlx",
                "x-dead-letter-routing-key": f"{queue_name}.dlq"
            }
        )
    
    async def declare_dlq(self, queue_name: str):
        """Declare dead letter queue"""
        dlx_exchange = await self.channel.declare_exchange(
            "dlx",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )
        
        dlq = await self.channel.declare_queue(
            f"{queue_name}.dlq",
            durable=True
        )
        
        await dlq.bind(dlx_exchange, routing_key=f"{queue_name}.dlq")
        return dlq
    
    async def publish(
        self,
        queue_name: str,
        message: Dict[str, Any],
        priority: int = 1
    ):
        """Publish message to queue"""
        await self.declare_queue(queue_name)
        
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                priority=priority
            ),
            routing_key=queue_name
        )
        logger.debug(f"Published message to {queue_name}")
    
    async def consume(
        self,
        queue_name: str,
        callback: Callable,
        auto_ack: bool = False
    ):
        """Consume messages from queue"""
        queue = await self.declare_queue(queue_name)
        await self.declare_dlq(queue_name)
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(ignore_processed=True):
                    try:
                        body = json.loads(message.body.decode())
                        await callback(body)
                        
                        if not auto_ack:
                            await message.ack()
                        
                        logger.debug(f"Processed message from {queue_name}")
                    
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        
                        # Check retry count
                        headers = message.headers or {}
                        retry_count = headers.get("x-retry-count", 0)
                        
                        if retry_count < 3:
                            # Retry with backoff
                            headers["x-retry-count"] = retry_count + 1
                            await self.publish(
                                queue_name,
                                json.loads(message.body.decode()),
                                priority=message.priority
                            )
                            await message.ack()
                        else:
                            # Send to DLQ
                            await message.reject(requeue=False)
                            logger.warning(f"Message sent to DLQ after {retry_count} retries")


# Queue names constants
class Queues:
    EVALUATION_TASKS = "evaluation_tasks"
    METRICS_CALCULATION = "metrics_calculation"
    DEPLOYMENT_CHECK = "deployment_check"
    NOTIFICATIONS = "notifications"
