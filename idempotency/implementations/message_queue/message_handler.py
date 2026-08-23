"""
Idempotent Message Queue Handler

Demonstrates:
- Handling duplicate messages
- At-least-once delivery semantics
- Message deduplication
- Multiple queue backends (SQS, RabbitMQ simulation)
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import redis
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis client for tracking processed messages
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


class MessageStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class Message:
    """Message structure"""
    message_id: str
    body: Dict
    attempt_count: int = 0
    received_at: Optional[str] = None
    metadata: Optional[Dict] = None


class IdempotentMessageHandler:
    """
    Base class for idempotent message processing
    
    Features:
    - Automatic deduplication
    - Retry logic
    - Dead letter queue
    - State tracking
    """
    
    def __init__(self, handler_name: str, dedup_window: int = 3600):
        self.handler_name = handler_name
        self.dedup_window = dedup_window  # 1 hour default
        self.max_retries = 3
    
    def is_processed(self, message_id: str) -> bool:
        """Check if message was already processed"""
        key = f"msg:processed:{self.handler_name}:{message_id}"
        return redis_client.exists(key) > 0
    
    def mark_processing(self, message_id: str) -> bool:
        """Mark message as being processed"""
        key = f"msg:state:{self.handler_name}:{message_id}"
        
        # Try to set processing state (atomic)
        result = redis_client.set(
            key,
            MessageStatus.PROCESSING,
            nx=True,  # Only if not exists
            ex=300  # 5 minute timeout
        )
        
        return result is not None
    
    def mark_completed(self, message_id: str) -> None:
        """Mark message as successfully processed"""
        # Remove processing state
        redis_client.delete(f"msg:state:{self.handler_name}:{message_id}")
        
        # Mark as processed (with TTL for cleanup)
        key = f"msg:processed:{self.handler_name}:{message_id}"
        redis_client.setex(key, self.dedup_window, "1")
        
        logger.info(f"Message {message_id} marked as completed")
    
    def mark_failed(self, message_id: str, error: str) -> None:
        """Mark message as failed"""
        key = f"msg:state:{self.handler_name}:{message_id}"
        redis_client.setex(key, 3600, MessageStatus.FAILED)
        
        # Store error details
        error_key = f"msg:error:{self.handler_name}:{message_id}"
        redis_client.setex(error_key, 86400, json.dumps({
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        logger.error(f"Message {message_id} failed: {error}")
    
    def process_message(self, message: Message) -> None:
        """
        Process a message idempotently
        
        Override this method with your business logic
        """
        raise NotImplementedError("Subclass must implement process_message()")
    
    def handle(self, message: Message) -> bool:
        """
        Main handler with idempotency logic
        
        Returns:
            True if processed successfully, False otherwise
        """
        message_id = message.message_id
        
        # 1. Check if already processed
        if self.is_processed(message_id):
            logger.info(f"Message {message_id} already processed, skipping")
            return True
        
        # 2. Try to mark as processing (prevents concurrent processing)
        if not self.mark_processing(message_id):
            logger.warning(f"Message {message_id} already being processed")
            return False
        
        # 3. Process message
        try:
            logger.info(f"Processing message {message_id}")
            self.process_message(message)
            
            # 4. Mark as completed
            self.mark_completed(message_id)
            return True
            
        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}", exc_info=True)
            
            # 5. Handle failure
            message.attempt_count += 1
            
            if message.attempt_count >= self.max_retries:
                # Send to dead letter queue
                self.send_to_dlq(message, str(e))
                self.mark_failed(message_id, str(e))
            else:
                # Allow retry (remove processing lock)
                redis_client.delete(f"msg:state:{self.handler_name}:{message_id}")
            
            return False
    
    def send_to_dlq(self, message: Message, error: str) -> None:
        """Send message to dead letter queue"""
        dlq_key = f"dlq:{self.handler_name}"
        dlq_message = {
            "message_id": message.message_id,
            "body": message.body,
            "error": error,
            "attempt_count": message.attempt_count,
            "failed_at": datetime.utcnow().isoformat()
        }
        
        redis_client.lpush(dlq_key, json.dumps(dlq_message))
        logger.warning(f"Message {message.message_id} sent to DLQ after {message.attempt_count} attempts")


# Example: Order Processing Handler
class OrderMessageHandler(IdempotentMessageHandler):
    """Handle order-related messages"""
    
    def __init__(self):
        super().__init__("order_handler", dedup_window=7200)  # 2 hours
        self.orders_db = {}  # Simulate database
    
    def process_message(self, message: Message) -> None:
        """Process order message"""
        body = message.body
        event_type = body.get('event_type')
        
        if event_type == 'order_created':
            self._handle_order_created(body)
        elif event_type == 'order_updated':
            self._handle_order_updated(body)
        elif event_type == 'order_cancelled':
            self._handle_order_cancelled(body)
        else:
            raise ValueError(f"Unknown event type: {event_type}")
    
    def _handle_order_created(self, data: Dict) -> None:
        """Handle order creation"""
        order_id = data['order_id']
        
        # Idempotent check: if order exists, skip
        if order_id in self.orders_db:
            logger.info(f"Order {order_id} already exists, skipping creation")
            return
        
        # Create order
        self.orders_db[order_id] = {
            "order_id": order_id,
            "user_id": data['user_id'],
            "total": data['total'],
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Order {order_id} created")
    
    def _handle_order_updated(self, data: Dict) -> None:
        """Handle order update"""
        order_id = data['order_id']
        
        if order_id not in self.orders_db:
            raise ValueError(f"Order {order_id} not found")
        
        # Idempotent update: set to specific state
        self.orders_db[order_id]['status'] = data['status']
        logger.info(f"Order {order_id} updated to {data['status']}")
    
    def _handle_order_cancelled(self, data: Dict) -> None:
        """Handle order cancellation"""
        order_id = data['order_id']
        
        if order_id not in self.orders_db:
            logger.warning(f"Order {order_id} not found, nothing to cancel")
            return
        
        # Idempotent: if already cancelled, no-op
        if self.orders_db[order_id]['status'] == 'cancelled':
            logger.info(f"Order {order_id} already cancelled")
            return
        
        self.orders_db[order_id]['status'] = 'cancelled'
        logger.info(f"Order {order_id} cancelled")


# Example: Email Notification Handler
class EmailNotificationHandler(IdempotentMessageHandler):
    """Handle email notification messages"""
    
    def __init__(self):
        super().__init__("email_handler", dedup_window=86400)  # 24 hours
        self.sent_emails = set()
    
    def process_message(self, message: Message) -> None:
        """Send email notification"""
        body = message.body
        email_to = body['email']
        subject = body['subject']
        content = body['content']
        
        # Generate email fingerprint
        fingerprint = hashlib.sha256(
            f"{email_to}{subject}{content}".encode()
        ).hexdigest()
        
        # Check if exact email already sent
        if fingerprint in self.sent_emails:
            logger.info(f"Email to {email_to} already sent, skipping")
            return
        
        # Send email (simulated)
        self._send_email(email_to, subject, content)
        
        # Track sent email
        self.sent_emails.add(fingerprint)
        logger.info(f"Email sent to {email_to}: {subject}")
    
    def _send_email(self, to: str, subject: str, content: str) -> None:
        """Simulate sending email"""
        time.sleep(0.1)  # Simulate email service call
        logger.debug(f"[EMAIL] To: {to}, Subject: {subject}")


# Simulated Queue Consumers
class SQSConsumer:
    """Simulate AWS SQS consumer with idempotent handling"""
    
    def __init__(self, queue_name: str, handler: IdempotentMessageHandler):
        self.queue_name = queue_name
        self.handler = handler
        self.queue_key = f"queue:{queue_name}"
    
    def publish_message(self, message_id: str, body: Dict) -> None:
        """Publish message to queue (for testing)"""
        message = {
            "message_id": message_id,
            "body": body,
            "timestamp": datetime.utcnow().isoformat()
        }
        redis_client.lpush(self.queue_key, json.dumps(message))
        logger.info(f"Published message {message_id} to {self.queue_name}")
    
    def consume(self, batch_size: int = 10, wait_time: int = 5) -> None:
        """
        Consume messages from queue
        
        Simulates SQS long polling and message processing
        """
        logger.info(f"Starting consumer for {self.queue_name}")
        
        while True:
            # Long poll for messages
            result = redis_client.brpop(self.queue_key, timeout=wait_time)
            
            if not result:
                logger.debug("No messages, continuing...")
                continue
            
            _, message_data = result
            message_dict = json.loads(message_data)
            
            message = Message(
                message_id=message_dict['message_id'],
                body=message_dict['body'],
                received_at=datetime.utcnow().isoformat()
            )
            
            # Process with idempotency
            success = self.handler.handle(message)
            
            if success:
                logger.info(f"Message {message.message_id} processed successfully")
            else:
                # Requeue for retry (simulating visibility timeout)
                logger.warning(f"Message {message.message_id} failed, will retry")
                time.sleep(1)  # Backoff
                self.publish_message(message.message_id, message.body)


# Batch Message Processor
class BatchMessageProcessor:
    """Process messages in batches with idempotency"""
    
    def __init__(self, handler: IdempotentMessageHandler):
        self.handler = handler
    
    def process_batch(self, messages: List[Message]) -> Dict[str, int]:
        """
        Process batch of messages idempotently
        
        Returns:
            Statistics about processing
        """
        stats = {
            "total": len(messages),
            "processed": 0,
            "skipped": 0,
            "failed": 0
        }
        
        for message in messages:
            # Check if already processed before attempting
            if self.handler.is_processed(message.message_id):
                stats["skipped"] += 1
                continue
            
            success = self.handler.handle(message)
            if success:
                stats["processed"] += 1
            else:
                stats["failed"] += 1
        
        return stats


# Monitoring and Utilities
def get_processing_stats(handler_name: str) -> Dict:
    """Get statistics for a handler"""
    # Count processed messages
    cursor = 0
    processed_count = 0
    
    while True:
        cursor, keys = redis_client.scan(
            cursor,
            match=f"msg:processed:{handler_name}:*",
            count=100
        )
        processed_count += len(keys)
        
        if cursor == 0:
            break
    
    # Count messages in processing state
    cursor = 0
    processing_count = 0
    
    while True:
        cursor, keys = redis_client.scan(
            cursor,
            match=f"msg:state:{handler_name}:*",
            count=100
        )
        processing_count += len(keys)
        
        if cursor == 0:
            break
    
    # Count DLQ messages
    dlq_count = redis_client.llen(f"dlq:{handler_name}")
    
    return {
        "handler_name": handler_name,
        "processed_messages": processed_count,
        "currently_processing": processing_count,
        "dead_letter_queue": dlq_count
    }


def cleanup_old_processed_messages(handler_name: str, older_than_hours: int = 24):
    """
    Cleanup processed message records older than specified hours
    
    Note: Redis TTL handles this automatically, but this can be used
    for manual cleanup if needed
    """
    cutoff = time.time() - (older_than_hours * 3600)
    cursor = 0
    deleted = 0
    
    while True:
        cursor, keys = redis_client.scan(
            cursor,
            match=f"msg:processed:{handler_name}:*",
            count=100
        )
        
        for key in keys:
            ttl = redis_client.ttl(key)
            if ttl == -1 or ttl > older_than_hours * 3600:
                # No TTL or TTL too long, delete
                redis_client.delete(key)
                deleted += 1
        
        if cursor == 0:
            break
    
    logger.info(f"Cleaned up {deleted} old processed message records for {handler_name}")


# Example usage and testing
if __name__ == "__main__":
    # Setup handlers
    order_handler = OrderMessageHandler()
    email_handler = EmailNotificationHandler()
    
    # Setup consumers
    order_consumer = SQSConsumer("orders", order_handler)
    email_consumer = SQSConsumer("emails", email_handler)
    
    # Publish test messages
    print("Publishing test messages...")
    
    # Order messages
    order_consumer.publish_message("order-001", {
        "event_type": "order_created",
        "order_id": "ORD-123",
        "user_id": 1,
        "total": 99.99
    })
    
    # Duplicate order message (will be deduplicated)
    order_consumer.publish_message("order-001", {
        "event_type": "order_created",
        "order_id": "ORD-123",
        "user_id": 1,
        "total": 99.99
    })
    
    # Email messages
    email_consumer.publish_message("email-001", {
        "email": "user@example.com",
        "subject": "Order Confirmation",
        "content": "Your order ORD-123 has been confirmed"
    })
    
    # Duplicate email (will be deduplicated)
    email_consumer.publish_message("email-001", {
        "email": "user@example.com",
        "subject": "Order Confirmation",
        "content": "Your order ORD-123 has been confirmed"
    })
    
    print("\nProcessing messages...")
    
    # Process in single-threaded mode for demo
    import threading
    
    def run_consumer(consumer):
        """Run consumer in thread"""
        try:
            consumer.consume()
        except KeyboardInterrupt:
            pass
    
    # Start consumers (press Ctrl+C to stop)
    order_thread = threading.Thread(target=run_consumer, args=(order_consumer,), daemon=True)
    email_thread = threading.Thread(target=run_consumer, args=(email_consumer,), daemon=True)
    
    order_thread.start()
    email_thread.start()
    
    # Let them process
    time.sleep(5)
    
    # Show stats
    print("\n" + "="*50)
    print("Processing Statistics")
    print("="*50)
    print(json.dumps(get_processing_stats("order_handler"), indent=2))
    print(json.dumps(get_processing_stats("email_handler"), indent=2))
