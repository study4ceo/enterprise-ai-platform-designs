# AWS SQS & Dead Letter Queue (DLQ) Architecture

## Overview
Comprehensive guide to message queuing, dead letter queues, retry strategies, and async processing patterns using AWS SQS, SNS, and EventBridge.

---

## Core Concepts

### What is SQS?
Amazon Simple Queue Service (SQS) is a fully managed message queuing service for:
- **Decoupling**: Separate components of distributed systems
- **Buffering**: Handle traffic spikes and load smoothing
- **Async Processing**: Process tasks without blocking
- **Reliability**: Guaranteed message delivery with retries

### SQS Queue Types

#### 1. Standard Queue
- **Throughput**: Nearly unlimited
- **Ordering**: Best-effort ordering
- **Delivery**: At-least-once (possible duplicates)
- **Use Case**: High throughput, duplicates acceptable

#### 2. FIFO Queue
- **Throughput**: 300 TPS (3000 with batching)
- **Ordering**: Strict ordering guaranteed
- **Delivery**: Exactly-once processing
- **Use Case**: Order-critical operations

---

## Architecture Patterns

### Basic SQS Pattern

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  Producer   │────────>│  SQS Queue  │────────>│  Consumer   │
│  (Lambda)   │         │             │         │  (Lambda)   │
└─────────────┘         └─────────────┘         └─────────────┘
```

### SQS with Dead Letter Queue

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│  Producer   │────────>│  Main Queue │────────>│  Consumer   │
│             │         │             │         │             │
└─────────────┘         └─────────────┘         └─────────────┘
                               │                       │
                               │ (max retries)         │
                               ↓                       ↓
                        ┌─────────────┐         ┌─────────────┐
                        │     DLQ     │────────>│  DLQ Handler│
                        │             │         │  (Manual)   │
                        └─────────────┘         └─────────────┘
                               │
                               ↓
                        ┌─────────────┐
                        │  CloudWatch │
                        │   Alarms    │
                        └─────────────┘
```

### Fan-Out Pattern (SNS + SQS)

```
                        ┌─────────────┐
                        │  SNS Topic  │
                        │             │
                        └─────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ↓              ↓              ↓
         ┌───────────┐  ┌───────────┐  ┌───────────┐
         │ SQS Queue │  │ SQS Queue │  │ SQS Queue │
         │  Service A│  │  Service B│  │  Service C│
         └───────────┘  └───────────┘  └───────────┘
                │              │              │
                ↓              ↓              ↓
         ┌───────────┐  ┌───────────┐  ┌───────────┐
         │ Consumer A│  │ Consumer B│  │ Consumer C│
         └───────────┘  └───────────┘  └───────────┘
```

---

## Implementation Examples

### 1. Basic SQS Setup with Terraform

```hcl
# main.tf

# Main SQS Queue
resource "aws_sqs_queue" "main_queue" {
  name                       = "data-processing-queue"
  delay_seconds              = 0
  max_message_size           = 262144  # 256 KB
  message_retention_seconds  = 345600  # 4 days
  receive_wait_time_seconds  = 20      # Long polling
  visibility_timeout_seconds = 300     # 5 minutes
  
  # Dead Letter Queue configuration
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3  # Retry 3 times before DLQ
  })
  
  tags = {
    Environment = "production"
    Service     = "data-pipeline"
  }
}

# Dead Letter Queue
resource "aws_sqs_queue" "dlq" {
  name                      = "data-processing-dlq"
  message_retention_seconds = 1209600  # 14 days
  
  tags = {
    Environment = "production"
    Service     = "data-pipeline"
    Type        = "DLQ"
  }
}

# FIFO Queue (for ordered processing)
resource "aws_sqs_queue" "fifo_queue" {
  name                        = "data-processing-fifo.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  deduplication_scope         = "messageGroup"
  fifo_throughput_limit       = "perMessageGroupId"
  
  visibility_timeout_seconds = 300
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.fifo_dlq.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue" "fifo_dlq" {
  name       = "data-processing-dlq.fifo"
  fifo_queue = true
}

# CloudWatch Alarms for DLQ
resource "aws_cloudwatch_metric_alarm" "dlq_messages" {
  alarm_name          = "dlq-messages-alert"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Average"
  threshold           = 10
  alarm_description   = "Alert when DLQ has messages"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    QueueName = aws_sqs_queue.dlq.name
  }
}
```

### 2. Producer (Publishing Messages)

```python
import boto3
import json
import uuid
from datetime import datetime

sqs = boto3.client('sqs')
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123456789/data-processing-queue'

class SQSProducer:
    
    def __init__(self, queue_url: str):
        self.sqs = boto3.client('sqs')
        self.queue_url = queue_url
    
    def send_message(self, message_body: dict, delay_seconds: int = 0):
        """Send a single message to SQS."""
        
        try:
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body),
                DelaySeconds=delay_seconds,
                MessageAttributes={
                    'MessageType': {
                        'StringValue': message_body.get('type', 'default'),
                        'DataType': 'String'
                    },
                    'Priority': {
                        'StringValue': message_body.get('priority', 'normal'),
                        'DataType': 'String'
                    },
                    'Timestamp': {
                        'StringValue': datetime.now().isoformat(),
                        'DataType': 'String'
                    }
                }
            )
            
            print(f"Message sent: {response['MessageId']}")
            return response['MessageId']
            
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            raise
    
    def send_batch(self, messages: list):
        """Send multiple messages in batch (up to 10)."""
        
        entries = []
        for i, msg in enumerate(messages[:10]):  # Max 10 per batch
            entries.append({
                'Id': str(i),
                'MessageBody': json.dumps(msg),
                'MessageAttributes': {
                    'MessageType': {
                        'StringValue': msg.get('type', 'default'),
                        'DataType': 'String'
                    }
                }
            })
        
        try:
            response = self.sqs.send_message_batch(
                QueueUrl=self.queue_url,
                Entries=entries
            )
            
            successful = len(response.get('Successful', []))
            failed = len(response.get('Failed', []))
            
            print(f"Batch sent: {successful} successful, {failed} failed")
            
            if failed > 0:
                print(f"Failed messages: {response['Failed']}")
            
            return response
            
        except Exception as e:
            print(f"Error sending batch: {str(e)}")
            raise
    
    def send_fifo_message(self, message_body: dict, message_group_id: str, deduplication_id: str = None):
        """Send message to FIFO queue."""
        
        if deduplication_id is None:
            deduplication_id = str(uuid.uuid4())
        
        try:
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body),
                MessageGroupId=message_group_id,
                MessageDeduplicationId=deduplication_id
            )
            
            return response['MessageId']
            
        except Exception as e:
            print(f"Error sending FIFO message: {str(e)}")
            raise

# Usage
producer = SQSProducer(QUEUE_URL)

# Single message
message = {
    'type': 'data_processing',
    'priority': 'high',
    'data': {
        'user_id': '12345',
        'action': 'purchase',
        'amount': 99.99
    }
}
producer.send_message(message)

# Batch messages
messages = [
    {'type': 'data_processing', 'data': {'id': i}} 
    for i in range(10)
]
producer.send_batch(messages)

# FIFO message
fifo_producer = SQSProducer('https://sqs.us-east-1.amazonaws.com/123456789/queue.fifo')
fifo_producer.send_fifo_message(
    message_body={'order_id': '12345', 'status': 'pending'},
    message_group_id='order-12345'
)
```

### 3. Consumer (Processing Messages)

```python
import boto3
import json
import time
from typing import Callable
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQSConsumer:
    
    def __init__(self, queue_url: str, max_messages: int = 10):
        self.sqs = boto3.client('sqs')
        self.queue_url = queue_url
        self.max_messages = max_messages
        self.running = False
    
    def process_message(self, message: dict) -> bool:
        """
        Process a single message.
        Override this method with your processing logic.
        Return True if successful, False to retry.
        """
        try:
            body = json.loads(message['Body'])
            logger.info(f"Processing message: {body}")
            
            # Your processing logic here
            # Example: Call ML model, transform data, etc.
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return False
    
    def start_polling(self, process_func: Callable = None):
        """Start long polling for messages."""
        
        if process_func is None:
            process_func = self.process_message
        
        self.running = True
        logger.info(f"Starting consumer for queue: {self.queue_url}")
        
        while self.running:
            try:
                # Receive messages (long polling)
                response = self.sqs.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=self.max_messages,
                    WaitTimeSeconds=20,  # Long polling
                    MessageAttributeNames=['All'],
                    AttributeNames=['All']
                )
                
                messages = response.get('Messages', [])
                
                if not messages:
                    logger.info("No messages received, continuing...")
                    continue
                
                logger.info(f"Received {len(messages)} messages")
                
                # Process messages
                for message in messages:
                    try:
                        # Process the message
                        success = process_func(message)
                        
                        if success:
                            # Delete message from queue
                            self.sqs.delete_message(
                                QueueUrl=self.queue_url,
                                ReceiptHandle=message['ReceiptHandle']
                            )
                            logger.info(f"Message deleted: {message['MessageId']}")
                        else:
                            # Let visibility timeout expire, message will be retried
                            logger.warning(f"Message processing failed, will retry: {message['MessageId']}")
                    
                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
                        # Message will be retried after visibility timeout
            
            except Exception as e:
                logger.error(f"Error in polling loop: {str(e)}")
                time.sleep(5)  # Wait before retrying
    
    def stop_polling(self):
        """Stop the polling loop."""
        self.running = False
        logger.info("Stopping consumer...")
    
    def process_batch(self, messages: list) -> dict:
        """Process messages in batch and delete successful ones."""
        
        successful = []
        failed = []
        
        for message in messages:
            try:
                success = self.process_message(message)
                
                if success:
                    successful.append({
                        'Id': message['MessageId'],
                        'ReceiptHandle': message['ReceiptHandle']
                    })
                else:
                    failed.append(message['MessageId'])
            
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                failed.append(message['MessageId'])
        
        # Batch delete successful messages
        if successful:
            try:
                delete_response = self.sqs.delete_message_batch(
                    QueueUrl=self.queue_url,
                    Entries=successful
                )
                
                deleted_count = len(delete_response.get('Successful', []))
                logger.info(f"Deleted {deleted_count} messages")
                
            except Exception as e:
                logger.error(f"Error deleting messages: {str(e)}")
        
        return {
            'successful': len(successful),
            'failed': len(failed)
        }

# Usage
consumer = SQSConsumer(QUEUE_URL)

# Define custom processing function
def custom_processor(message: dict) -> bool:
    """Custom message processing logic."""
    try:
        body = json.loads(message['Body'])
        
        # Example: Process data with ML model
        if body['type'] == 'data_processing':
            # Call your ML model
            result = process_with_ml_model(body['data'])
            
            # Store result
            store_result(result)
            
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return False

# Start consuming
consumer.start_polling(custom_processor)
```

### 4. Lambda Consumer with Error Handling

```python
import json
import boto3
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

# DLQ URL for manual intervention
DLQ_URL = 'https://sqs.us-east-1.amazonaws.com/123456789/data-processing-dlq'

def lambda_handler(event, context):
    """
    Lambda function to consume SQS messages.
    Automatically handles retries and DLQ routing.
    """
    
    successful = 0
    failed = 0
    
    for record in event['Records']:
        try:
            # Parse message
            message_id = record['messageId']
            body = json.loads(record['body'])
            
            logger.info(f"Processing message {message_id}: {body}")
            
            # Check retry count
            attributes = record.get('attributes', {})
            receive_count = int(attributes.get('ApproximateReceiveCount', 0))
            
            logger.info(f"Message receive count: {receive_count}")
            
            # Process message
            result = process_message(body)
            
            if result['success']:
                successful += 1
                logger.info(f"Message processed successfully: {message_id}")
                
                # Log to DynamoDB
                log_successful_processing(message_id, body, result)
            else:
                failed += 1
                logger.error(f"Message processing failed: {message_id}")
                
                # If approaching max retries, add extra context
                if receive_count >= 2:  # Max is 3
                    logger.error(f"Message approaching DLQ: {message_id}")
                    send_dlq_alert(message_id, body, result.get('error'))
                
                # Raise exception to trigger retry
                raise Exception(result.get('error', 'Processing failed'))
        
        except Exception as e:
            failed += 1
            logger.error(f"Error processing message: {str(e)}")
            
            # Log error details
            log_processing_error(record, str(e))
            
            # Re-raise to trigger SQS retry mechanism
            raise
    
    # Log metrics
    log_metrics(successful, failed)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'successful': successful,
            'failed': failed
        })
    }

def process_message(body: dict) -> dict:
    """Main message processing logic."""
    try:
        # Example: Data transformation
        data = body.get('data', {})
        message_type = body.get('type')
        
        if message_type == 'data_processing':
            # Process data
            result = transform_data(data)
            
            # Store in DynamoDB
            store_data(result)
            
            return {'success': True, 'result': result}
        
        elif message_type == 'ml_inference':
            # Call ML model
            prediction = call_ml_model(data)
            
            # Store prediction
            store_prediction(prediction)
            
            return {'success': True, 'prediction': prediction}
        
        else:
            return {'success': False, 'error': f'Unknown message type: {message_type}'}
    
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return {'success': False, 'error': str(e)}

def transform_data(data: dict) -> dict:
    """Transform data."""
    # Your transformation logic
    return {
        'transformed': True,
        'timestamp': datetime.now().isoformat(),
        **data
    }

def call_ml_model(data: dict) -> dict:
    """Call ML model for inference."""
    # Example: Call SageMaker endpoint
    sagemaker_runtime = boto3.client('sagemaker-runtime')
    
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName='my-model-endpoint',
        ContentType='application/json',
        Body=json.dumps(data)
    )
    
    result = json.loads(response['Body'].read())
    return result

def store_data(data: dict):
    """Store processed data in DynamoDB."""
    table = dynamodb.Table('processed-data')
    
    table.put_item(Item={
        'id': str(uuid.uuid4()),
        'data': data,
        'processed_at': datetime.now().isoformat()
    })

def log_successful_processing(message_id: str, body: dict, result: dict):
    """Log successful processing to DynamoDB."""
    table = dynamodb.Table('message-processing-log')
    
    table.put_item(Item={
        'message_id': message_id,
        'status': 'success',
        'body': json.dumps(body),
        'result': json.dumps(result),
        'timestamp': datetime.now().isoformat()
    })

def log_processing_error(record: dict, error: str):
    """Log processing error to DynamoDB."""
    table = dynamodb.Table('message-processing-log')
    
    table.put_item(Item={
        'message_id': record['messageId'],
        'status': 'error',
        'body': record['body'],
        'error': error,
        'receive_count': record.get('attributes', {}).get('ApproximateReceiveCount', '0'),
        'timestamp': datetime.now().isoformat()
    })

def send_dlq_alert(message_id: str, body: dict, error: str):
    """Send alert when message is about to move to DLQ."""
    sns = boto3.client('sns')
    
    sns.publish(
        TopicArn='arn:aws:sns:us-east-1:123456789:dlq-alerts',
        Subject=f'Message approaching DLQ: {message_id}',
        Message=json.dumps({
            'message_id': message_id,
            'body': body,
            'error': error,
            'timestamp': datetime.now().isoformat()
        }, indent=2)
    )

def log_metrics(successful: int, failed: int):
    """Log metrics to CloudWatch."""
    cloudwatch.put_metric_data(
        Namespace='SQS/Processing',
        MetricData=[
            {
                'MetricName': 'SuccessfulMessages',
                'Value': successful,
                'Unit': 'Count',
                'Timestamp': datetime.now()
            },
            {
                'MetricName': 'FailedMessages',
                'Value': failed,
                'Unit': 'Count',
                'Timestamp': datetime.now()
            }
        ]
    )
```

### 5. DLQ Handler (Manual Intervention)

```python
import boto3
import json
from datetime import datetime

class DLQHandler:
    
    def __init__(self, dlq_url: str, main_queue_url: str):
        self.sqs = boto3.client('sqs')
        self.dlq_url = dlq_url
        self.main_queue_url = main_queue_url
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('dlq-analysis')
    
    def analyze_dlq_messages(self) -> list:
        """Analyze messages in DLQ to understand failure patterns."""
        
        all_messages = []
        
        while True:
            response = self.sqs.receive_message(
                QueueUrl=self.dlq_url,
                MaxNumberOfMessages=10,
                MessageAttributeNames=['All'],
                AttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            if not messages:
                break
            
            for message in messages:
                try:
                    body = json.loads(message['Body'])
                    
                    analysis = {
                        'message_id': message['MessageId'],
                        'body': body,
                        'attributes': message.get('Attributes', {}),
                        'message_attributes': message.get('MessageAttributes', {}),
                        'first_received': message['Attributes'].get('ApproximateFirstReceiveTimestamp'),
                        'receive_count': message['Attributes'].get('ApproximateReceiveCount')
                    }
                    
                    all_messages.append(analysis)
                    
                    # Store analysis
                    self.store_analysis(analysis)
                
                except Exception as e:
                    print(f"Error analyzing message: {str(e)}")
        
        return all_messages
    
    def store_analysis(self, analysis: dict):
        """Store DLQ message analysis."""
        self.table.put_item(Item={
            'message_id': analysis['message_id'],
            'body': json.dumps(analysis['body']),
            'analyzed_at': datetime.now().isoformat(),
            'receive_count': analysis.get('receive_count', '0'),
            'status': 'pending_review'
        })
    
    def replay_message(self, message_id: str, fix_data: dict = None):
        """
        Replay a message from DLQ back to main queue.
        Optionally apply fixes to the message data.
        """
        
        # Get message from DLQ
        response = self.sqs.receive_message(
            QueueUrl=self.dlq_url,
            MaxNumberOfMessages=10,
            MessageAttributeNames=['All']
        )
        
        for message in response.get('Messages', []):
            if message['MessageId'] == message_id:
                body = json.loads(message['Body'])
                
                # Apply fixes if provided
                if fix_data:
                    body.update(fix_data)
                
                # Send to main queue
                self.sqs.send_message(
                    QueueUrl=self.main_queue_url,
                    MessageBody=json.dumps(body),
                    MessageAttributes=message.get('MessageAttributes', {})
                )
                
                # Delete from DLQ
                self.sqs.delete_message(
                    QueueUrl=self.dlq_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                
                print(f"Message {message_id} replayed to main queue")
                
                # Update analysis
                self.table.update_item(
                    Key={'message_id': message_id},
                    UpdateExpression='SET #status = :status, replayed_at = :timestamp',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':status': 'replayed',
                        ':timestamp': datetime.now().isoformat()
                    }
                )
                
                return True
        
        return False
    
    def purge_dlq(self):
        """Purge all messages from DLQ (use with caution!)."""
        try:
            self.sqs.purge_queue(QueueUrl=self.dlq_url)
            print("DLQ purged successfully")
        except Exception as e:
            print(f"Error purging DLQ: {str(e)}")
    
    def get_dlq_stats(self) -> dict:
        """Get statistics about DLQ."""
        response = self.sqs.get_queue_attributes(
            QueueUrl=self.dlq_url,
            AttributeNames=['All']
        )
        
        attributes = response['Attributes']
        
        return {
            'approximate_messages': int(attributes.get('ApproximateNumberOfMessages', 0)),
            'approximate_messages_delayed': int(attributes.get('ApproximateNumberOfMessagesDelayed', 0)),
            'approximate_messages_not_visible': int(attributes.get('ApproximateNumberOfMessagesNotVisible', 0)),
            'created_timestamp': attributes.get('CreatedTimestamp'),
            'last_modified_timestamp': attributes.get('LastModifiedTimestamp'),
            'message_retention_period': attributes.get('MessageRetentionPeriod')
        }

# Usage
dlq_handler = DLQHandler(
    dlq_url='https://sqs.us-east-1.amazonaws.com/123456789/data-processing-dlq',
    main_queue_url='https://sqs.us-east-1.amazonaws.com/123456789/data-processing-queue'
)

# Analyze DLQ messages
messages = dlq_handler.analyze_dlq_messages()
print(f"Found {len(messages)} messages in DLQ")

# Get stats
stats = dlq_handler.get_dlq_stats()
print(f"DLQ Stats: {stats}")

# Replay a message with fixes
dlq_handler.replay_message(
    message_id='abc-123',
    fix_data={'retry_count': 0, 'fix_applied': True}
)
```

---

## Advanced Patterns

### 1. Priority Queue Pattern

```python
class PriorityQueueSystem:
    """Implement priority queues using multiple SQS queues."""
    
    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.queues = {
            'critical': 'https://sqs.../critical-queue',
            'high': 'https://sqs.../high-priority-queue',
            'normal': 'https://sqs.../normal-queue',
            'low': 'https://sqs.../low-priority-queue'
        }
    
    def send_message(self, message: dict, priority: str = 'normal'):
        """Send message to appropriate priority queue."""
        
        queue_url = self.queues.get(priority, self.queues['normal'])
        
        self.sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
            MessageAttributes={
                'Priority': {
                    'StringValue': priority,
                    'DataType': 'String'
                }
            }
        )
    
    def consume_by_priority(self):
        """Consume messages respecting priority order."""
        
        priority_order = ['critical', 'high', 'normal', 'low']
        
        for priority in priority_order:
            queue_url = self.queues[priority]
            
            response = self.sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=1  # Short wait for high priority
            )
            
            messages = response.get('Messages', [])
            if messages:
                # Process high priority messages first
                for message in messages:
                    self.process_message(message)
                    self.sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                
                # Continue to next priority level
                continue
```

### 2. Delay Queue Pattern

```python
def send_delayed_message(queue_url: str, message: dict, delay_seconds: int):
    """Send message with delay (0-900 seconds)."""
    
    sqs = boto3.client('sqs')
    
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message),
        DelaySeconds=min(delay_seconds, 900)  # Max 15 minutes
    )

# For longer delays, use Step Functions or EventBridge
def schedule_message_with_step_functions(message: dict, delay_seconds: int):
    """Schedule message delivery using Step Functions."""
    
    stepfunctions = boto3.client('stepfunctions')
    
    stepfunctions.start_execution(
        stateMachineArn='arn:aws:states:...',
        input=json.dumps({
            'wait_seconds': delay_seconds,
            'message': message,
            'queue_url': QUEUE_URL
        })
    )

# Step Functions definition
step_function_definition = {
    "Comment": "Delayed message delivery",
    "StartAt": "Wait",
    "States": {
        "Wait": {
            "Type": "Wait",
            "SecondsPath": "$.wait_seconds",
            "Next": "SendMessage"
        },
        "SendMessage": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:...:send-to-sqs",
            "End": True
        }
    }
}
```

### 3. Circuit Breaker Pattern

```python
class CircuitBreaker:
    """Implement circuit breaker for SQS consumers."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
                print("Circuit breaker: HALF_OPEN, trying again")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
                print("Circuit breaker: CLOSED")
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                print(f"Circuit breaker: OPEN (failures: {self.failure_count})")
            
            raise

# Usage with SQS consumer
circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

def consume_with_circuit_breaker():
    """Consume messages with circuit breaker."""
    
    def process():
        response = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=10)
        messages = response.get('Messages', [])
        
        for message in messages:
            # Process message
            process_message(message)
    
    try:
        circuit_breaker.call(process)
    except Exception as e:
        print(f"Circuit breaker prevented execution: {str(e)}")
        time.sleep(60)  # Wait before retrying
```

---

## Monitoring & Observability

### CloudWatch Dashboards

```python
def create_sqs_dashboard():
    """Create comprehensive SQS monitoring dashboard."""
    
    cloudwatch = boto3.client('cloudwatch')
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/SQS", "NumberOfMessagesSent", {"stat": "Sum"}],
                        [".", "NumberOfMessagesReceived", {"stat": "Sum"}],
                        [".", "NumberOfMessagesDeleted", {"stat": "Sum"}]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "us-east-1",
                    "title": "Message Flow"
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/SQS", "ApproximateNumberOfMessagesVisible"],
                        [".", "ApproximateNumberOfMessagesNotVisible"],
                        [".", "ApproximateNumberOfMessagesDelayed"]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "Queue Depth"
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/SQS", "ApproximateAgeOfOldestMessage"]
                    ],
                    "period": 300,
                    "stat": "Maximum",
                    "region": "us-east-1",
                    "title": "Message Age",
                    "yAxis": {
                        "left": {
                            "label": "Seconds"
                        }
                    }
                }
            }
        ]
    }
    
    cloudwatch.put_dashboard(
        DashboardName='SQS-Monitoring',
        DashboardBody=json.dumps(dashboard_body)
    )
```

### Custom Metrics

```python
def publish_custom_metrics(queue_name: str, processing_time: float, success: bool):
    """Publish custom processing metrics."""
    
    cloudwatch = boto3.client('cloudwatch')
    
    cloudwatch.put_metric_data(
        Namespace='Custom/SQS',
        MetricData=[
            {
                'MetricName': 'ProcessingTime',
                'Value': processing_time,
                'Unit': 'Seconds',
                'Dimensions': [
                    {'Name': 'QueueName', 'Value': queue_name}
                ]
            },
            {
                'MetricName': 'ProcessingSuccess',
                'Value': 1 if success else 0,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'QueueName', 'Value': queue_name}
                ]
            }
        ]
    )
```

---

## Best Practices

### 1. Queue Configuration
- ✅ Set appropriate visibility timeout (6x processing time)
- ✅ Enable long polling (WaitTimeSeconds > 0)
- ✅ Configure DLQ with appropriate maxReceiveCount (3-5)
- ✅ Set message retention based on requirements
- ✅ Use FIFO queues only when ordering is critical
- ✅ Enable server-side encryption

### 2. Message Design
- ✅ Keep messages < 256 KB (use S3 for larger payloads)
- ✅ Make messages idempotent
- ✅ Include message versioning
- ✅ Add correlation IDs for tracing
- ✅ Use message attributes for filtering
- ✅ Include retry metadata

### 3. Consumer Design
- ✅ Process messages idempotently
- ✅ Implement exponential backoff
- ✅ Delete messages only after successful processing
- ✅ Handle partial batch failures
- ✅ Implement circuit breakers
- ✅ Log all processing attempts

### 4. DLQ Management
- ✅ Monitor DLQ depth with alarms
- ✅ Investigate DLQ messages promptly
- ✅ Implement DLQ replay mechanism
- ✅ Store DLQ analysis for trends
- ✅ Set longer retention for DLQ (14 days)
- ✅ Alert on first message in DLQ

### 5. Performance
- ✅ Use batch operations (send/receive/delete)
- ✅ Adjust max messages per receive (1-10)
- ✅ Use multiple consumers for high throughput
- ✅ Implement connection pooling
- ✅ Monitor queue age and depth
- ✅ Scale consumers based on queue depth

### 6. Security
- ✅ Use IAM roles (no hardcoded credentials)
- ✅ Enable encryption at rest and in transit
- ✅ Use VPC endpoints for private access
- ✅ Implement least privilege access
- ✅ Audit queue access with CloudTrail
- ✅ Validate message content

### 7. Cost Optimization
- ✅ Use long polling to reduce API calls
- ✅ Batch operations where possible
- ✅ Set appropriate message retention
- ✅ Monitor and optimize queue count
- ✅ Use FIFO only when necessary (higher cost)
- ✅ Archive old DLQ messages to S3

---

## Troubleshooting Guide

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Messages not being processed | Consumer not polling | Check consumer is running and has permissions |
| Messages stuck in flight | Visibility timeout too short | Increase visibility timeout |
| Duplicate processing | Not deleting after processing | Always delete after successful processing |
| Messages going to DLQ | Processing failures | Check logs, fix code, replay from DLQ |
| High latency | Not using long polling | Enable long polling (WaitTimeSeconds) |
| Queue depth growing | Consumers can't keep up | Add more consumers or optimize processing |

---

This comprehensive guide covers all aspects of SQS, DLQ, and async messaging patterns!
