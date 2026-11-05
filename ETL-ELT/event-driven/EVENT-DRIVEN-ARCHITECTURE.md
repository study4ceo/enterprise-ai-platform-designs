# Event-Driven Architecture with AWS

## Overview
Comprehensive guide to building event-driven systems using AWS EventBridge, SNS, SQS, Lambda, and Step Functions for reactive, scalable architectures.

---

## Event-Driven Patterns

### 1. Pub/Sub Pattern (SNS + SQS)

```
┌─────────────┐
│  Publisher  │
│  (Lambda/   │
│   Service)  │
└─────────────┘
       │
       │ Publish Event
       ↓
┌─────────────┐
│  SNS Topic  │
│             │
└─────────────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       ↓              ↓              ↓              ↓
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ SQS Queue│   │ SQS Queue│   │  Lambda  │   │  Email   │
│ Service A│   │ Service B│   │  Function│   │Subscription│
└──────────┘   └──────────┘   └──────────┘   └──────────┘
       │              │              │
       ↓              ↓              ↓
┌──────────┐   ┌──────────┐   ┌──────────┐
│Consumer A│   │Consumer B│   │Consumer C│
└──────────┘   └──────────┘   └──────────┘
```

### 2. Event Bus Pattern (EventBridge)

```
┌─────────────────────────────────────────────────────────────┐
│                    EventBridge Bus                           │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Rule 1  │  │  Rule 2  │  │  Rule 3  │  │  Rule 4  │   │
│  │order.*   │  │user.*    │  │payment.* │  │*.failed  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
       │              │              │              │
       ↓              ↓              ↓              ↓
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Lambda  │   │    SQS   │   │   Step   │   │   SNS    │
│ Function │   │  Queue   │   │ Functions│   │  Topic   │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
```

### 3. CQRS Pattern

```
┌─────────────┐
│   Command   │
│   Service   │
└─────────────┘
       │
       │ Write Event
       ↓
┌─────────────┐
│ Write Model │
│  (DynamoDB) │
└─────────────┘
       │
       │ Emit Event
       ↓
┌─────────────┐
│ Event Stream│
│  (Kinesis)  │
└─────────────┘
       │
       ├──────────────┬──────────────┐
       ↓              ↓              ↓
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Read Model│   │ Analytics│   │Materialized│
│   (RDS)  │   │  Store   │   │   View   │
└──────────┘   └──────────┘   └──────────┘
       │
       ↓
┌──────────┐
│  Query   │
│ Service  │
└──────────┘
```

---

## SNS (Simple Notification Service)

### Setup & Configuration

```python
import boto3
import json
from datetime import datetime

sns = boto3.client('sns')
sqs = boto3.client('sqs')

class SNSEventPublisher:
    
    def __init__(self, topic_arn: str):
        self.sns = boto3.client('sns')
        self.topic_arn = topic_arn
    
    def publish_event(self, event_type: str, payload: dict, attributes: dict = None):
        """Publish event to SNS topic."""
        
        message = {
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'payload': payload
        }
        
        message_attributes = {
            'event_type': {
                'DataType': 'String',
                'StringValue': event_type
            },
            'timestamp': {
                'DataType': 'String',
                'StringValue': datetime.now().isoformat()
            }
        }
        
        if attributes:
            for key, value in attributes.items():
                message_attributes[key] = {
                    'DataType': 'String',
                    'StringValue': str(value)
                }
        
        try:
            response = self.sns.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(message),
                MessageAttributes=message_attributes,
                Subject=f'Event: {event_type}'
            )
            
            print(f"Published event: {event_type}, MessageId: {response['MessageId']}")
            return response['MessageId']
            
        except Exception as e:
            print(f"Error publishing event: {str(e)}")
            raise
    
    def publish_batch(self, events: list):
        """Publish multiple events (up to 10)."""
        
        entries = []
        for i, event in enumerate(events[:10]):
            entries.append({
                'Id': str(i),
                'Message': json.dumps({
                    'event_type': event['type'],
                    'timestamp': datetime.now().isoformat(),
                    'payload': event['payload']
                }),
                'MessageAttributes': {
                    'event_type': {
                        'DataType': 'String',
                        'StringValue': event['type']
                    }
                }
            })
        
        response = self.sns.publish_batch(
            TopicArn=self.topic_arn,
            PublishBatchRequestEntries=entries
        )
        
        return response

# Create SNS Topic with Terraform
"""
resource "aws_sns_topic" "events" {
  name = "application-events"
  
  tags = {
    Environment = "production"
  }
}

resource "aws_sns_topic_subscription" "sqs_subscription" {
  topic_arn = aws_sns_topic.events.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.event_queue.arn
  
  filter_policy = jsonencode({
    event_type = ["order.created", "order.updated"]
  })
}

resource "aws_sns_topic_subscription" "lambda_subscription" {
  topic_arn = aws_sns_topic.events.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.event_handler.arn
}

resource "aws_sns_topic_subscription" "email_subscription" {
  topic_arn = aws_sns_topic.events.arn
  protocol  = "email"
  endpoint  = "alerts@example.com"
  
  filter_policy = jsonencode({
    severity = ["critical", "high"]
  })
}
"""

# Usage
publisher = SNSEventPublisher('arn:aws:sns:us-east-1:123456789:application-events')

# Publish single event
publisher.publish_event(
    event_type='order.created',
    payload={
        'order_id': '12345',
        'customer_id': '67890',
        'amount': 99.99
    },
    attributes={
        'priority': 'high',
        'region': 'us-east-1'
    }
)

# Publish batch
events = [
    {'type': 'user.registered', 'payload': {'user_id': '1'}},
    {'type': 'user.verified', 'payload': {'user_id': '1'}},
]
publisher.publish_batch(events)
```

### Message Filtering

```python
# Subscribe with filter policy
def create_filtered_subscription(topic_arn: str, queue_arn: str, event_types: list):
    """Create SQS subscription with message filtering."""
    
    filter_policy = {
        'event_type': event_types
    }
    
    response = sns.subscribe(
        TopicArn=topic_arn,
        Protocol='sqs',
        Endpoint=queue_arn,
        Attributes={
            'FilterPolicy': json.dumps(filter_policy),
            'RawMessageDelivery': 'false'
        }
    )
    
    return response['SubscriptionArn']

# Advanced filtering
advanced_filter = {
    'event_type': ['order.created', 'order.updated'],
    'priority': ['high', 'critical'],
    'amount': [{'numeric': ['>=', 100]}],
    'region': [{'prefix': 'us-'}]
}

sns.set_subscription_attributes(
    SubscriptionArn=subscription_arn,
    AttributeName='FilterPolicy',
    AttributeValue=json.dumps(advanced_filter)
)
```

---

## EventBridge

### Event Bus Setup

```python
import boto3
import json

eventbridge = boto3.client('events')

class EventBridgePublisher:
    
    def __init__(self, event_bus_name: str = 'default'):
        self.eventbridge = boto3.client('events')
        self.event_bus_name = event_bus_name
    
    def put_event(self, source: str, detail_type: str, detail: dict):
        """Put single event on EventBridge."""
        
        response = self.eventbridge.put_events(
            Entries=[
                {
                    'Source': source,
                    'DetailType': detail_type,
                    'Detail': json.dumps(detail),
                    'EventBusName': self.event_bus_name
                }
            ]
        )
        
        if response['FailedEntryCount'] > 0:
            raise Exception(f"Failed to put event: {response['Entries']}")
        
        return response['Entries'][0]['EventId']
    
    def put_events_batch(self, events: list):
        """Put multiple events (up to 10)."""
        
        entries = []
        for event in events[:10]:
            entries.append({
                'Source': event['source'],
                'DetailType': event['detail_type'],
                'Detail': json.dumps(event['detail']),
                'EventBusName': self.event_bus_name
            })
        
        response = self.eventbridge.put_events(Entries=entries)
        
        return {
            'successful': len(entries) - response['FailedEntryCount'],
            'failed': response['FailedEntryCount']
        }

# Create EventBridge Rules with Terraform
"""
resource "aws_cloudwatch_event_bus" "application" {
  name = "application-events"
}

resource "aws_cloudwatch_event_rule" "order_events" {
  name           = "order-events"
  description    = "Capture all order events"
  event_bus_name = aws_cloudwatch_event_bus.application.name
  
  event_pattern = jsonencode({
    source      = ["com.myapp.orders"]
    detail-type = ["Order Created", "Order Updated", "Order Cancelled"]
  })
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule           = aws_cloudwatch_event_rule.order_events.name
  event_bus_name = aws_cloudwatch_event_bus.application.name
  arn            = aws_lambda_function.order_processor.arn
}

resource "aws_cloudwatch_event_target" "sqs" {
  rule           = aws_cloudwatch_event_rule.order_events.name
  event_bus_name = aws_cloudwatch_event_bus.application.name
  arn            = aws_sqs_queue.order_queue.arn
}

resource "aws_cloudwatch_event_rule" "scheduled_task" {
  name                = "daily-report"
  description         = "Trigger daily report generation"
  schedule_expression = "cron(0 9 * * ? *)"  # 9 AM UTC daily
  event_bus_name      = aws_cloudwatch_event_bus.application.name
}
"""

# Usage
publisher = EventBridgePublisher('application-events')

# Publish event
event_id = publisher.put_event(
    source='com.myapp.orders',
    detail_type='Order Created',
    detail={
        'order_id': '12345',
        'customer_id': '67890',
        'amount': 99.99,
        'items': [
            {'sku': 'ABC123', 'quantity': 2}
        ]
    }
)

print(f"Event published: {event_id}")
```

### Event Pattern Matching

```python
# Simple pattern
simple_pattern = {
    "source": ["com.myapp.orders"],
    "detail-type": ["Order Created"]
}

# Advanced pattern with filtering
advanced_pattern = {
    "source": ["com.myapp.orders"],
    "detail-type": ["Order Created", "Order Updated"],
    "detail": {
        "amount": [{"numeric": [">", 100]}],
        "status": ["pending", "processing"],
        "customer": {
            "tier": ["premium", "enterprise"]
        }
    }
}

# Prefix matching
prefix_pattern = {
    "source": [{"prefix": "com.myapp"}],
    "detail-type": [{"prefix": "Order"}]
}

# Create rule with pattern
def create_event_rule(rule_name: str, pattern: dict, targets: list):
    """Create EventBridge rule with pattern."""
    
    # Create rule
    eventbridge.put_rule(
        Name=rule_name,
        EventPattern=json.dumps(pattern),
        State='ENABLED',
        Description=f'Rule for {rule_name}'
    )
    
    # Add targets
    eventbridge.put_targets(
        Rule=rule_name,
        Targets=targets
    )

# Usage
create_event_rule(
    rule_name='high-value-orders',
    pattern=advanced_pattern,
    targets=[
        {
            'Id': '1',
            'Arn': 'arn:aws:lambda:us-east-1:123456789:function:process-high-value-order'
        },
        {
            'Id': '2',
            'Arn': 'arn:aws:sqs:us-east-1:123456789:high-value-orders'
        }
    ]
)
```

### Event Archive & Replay

```python
class EventBridgeArchive:
    
    def __init__(self, event_bus_name: str):
        self.eventbridge = boto3.client('events')
        self.event_bus_name = event_bus_name
    
    def create_archive(self, archive_name: str, retention_days: int = 365):
        """Create event archive."""
        
        response = self.eventbridge.create_archive(
            ArchiveName=archive_name,
            EventSourceArn=f'arn:aws:events:us-east-1:123456789:event-bus/{self.event_bus_name}',
            RetentionDays=retention_days,
            Description=f'Archive for {self.event_bus_name}'
        )
        
        return response['ArchiveArn']
    
    def replay_events(self, archive_name: str, start_time: datetime, end_time: datetime):
        """Replay events from archive."""
        
        response = self.eventbridge.start_replay(
            ReplayName=f'replay-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
            EventSourceArn=f'arn:aws:events:us-east-1:123456789:archive/{archive_name}',
            EventStartTime=start_time,
            EventEndTime=end_time,
            Destination={
                'Arn': f'arn:aws:events:us-east-1:123456789:event-bus/{self.event_bus_name}'
            }
        )
        
        return response['ReplayArn']
    
    def get_replay_status(self, replay_arn: str):
        """Get replay status."""
        
        response = self.eventbridge.describe_replay(
            ReplayName=replay_arn.split('/')[-1]
        )
        
        return {
            'state': response['State'],
            'events_replayed': response.get('EventReplayedCount', 0),
            'start_time': response.get('EventStartTime'),
            'end_time': response.get('EventEndTime')
        }

# Usage
archive = EventBridgeArchive('application-events')

# Create archive
archive_arn = archive.create_archive('orders-archive', retention_days=365)

# Replay events
from datetime import datetime, timedelta

replay_arn = archive.replay_events(
    archive_name='orders-archive',
    start_time=datetime.now() - timedelta(days=7),
    end_time=datetime.now()
)

# Check status
status = archive.get_replay_status(replay_arn)
print(f"Replay status: {status}")
```

---

## Event Sourcing Pattern

```python
from typing import List, Dict
import uuid

class EventStore:
    """Event store implementation using DynamoDB."""
    
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        self.eventbridge = boto3.client('events')
    
    def append_event(self, aggregate_id: str, event_type: str, event_data: dict):
        """Append event to store."""
        
        event = {
            'aggregate_id': aggregate_id,
            'event_id': str(uuid.uuid4()),
            'event_type': event_type,
            'event_data': event_data,
            'timestamp': datetime.now().isoformat(),
            'version': self.get_current_version(aggregate_id) + 1
        }
        
        # Store event
        self.table.put_item(
            Item=event,
            ConditionExpression='attribute_not_exists(event_id)'
        )
        
        # Publish event
        self.publish_event(event)
        
        return event['event_id']
    
    def get_events(self, aggregate_id: str) -> List[Dict]:
        """Get all events for an aggregate."""
        
        response = self.table.query(
            KeyConditionExpression='aggregate_id = :id',
            ExpressionAttributeValues={':id': aggregate_id},
            ScanIndexForward=True  # Order by sort key ascending
        )
        
        return response['Items']
    
    def get_current_version(self, aggregate_id: str) -> int:
        """Get current version of aggregate."""
        
        response = self.table.query(
            KeyConditionExpression='aggregate_id = :id',
            ExpressionAttributeValues={':id': aggregate_id},
            ScanIndexForward=False,  # Descending
            Limit=1
        )
        
        items = response.get('Items', [])
        return items[0]['version'] if items else 0
    
    def publish_event(self, event: dict):
        """Publish event to EventBridge."""
        
        self.eventbridge.put_events(
            Entries=[{
                'Source': 'com.myapp.eventstore',
                'DetailType': event['event_type'],
                'Detail': json.dumps(event)
            }]
        )
    
    def rebuild_aggregate(self, aggregate_id: str) -> dict:
        """Rebuild aggregate state from events."""
        
        events = self.get_events(aggregate_id)
        
        # Apply events to rebuild state
        state = {}
        for event in events:
            state = self.apply_event(state, event)
        
        return state
    
    def apply_event(self, state: dict, event: dict) -> dict:
        """Apply event to state (implement based on your domain)."""
        
        event_type = event['event_type']
        event_data = event['event_data']
        
        if event_type == 'OrderCreated':
            state = {
                'order_id': event_data['order_id'],
                'status': 'created',
                'items': event_data['items'],
                'total': event_data['total']
            }
        elif event_type == 'OrderPaid':
            state['status'] = 'paid'
            state['payment_id'] = event_data['payment_id']
        elif event_type == 'OrderShipped':
            state['status'] = 'shipped'
            state['tracking_number'] = event_data['tracking_number']
        
        return state

# DynamoDB Table for Event Store (Terraform)
"""
resource "aws_dynamodb_table" "event_store" {
  name           = "event-store"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "aggregate_id"
  range_key      = "version"
  
  attribute {
    name = "aggregate_id"
    type = "S"
  }
  
  attribute {
    name = "version"
    type = "N"
  }
  
  attribute {
    name = "event_type"
    type = "S"
  }
  
  global_secondary_index {
    name            = "event_type_index"
    hash_key        = "event_type"
    range_key       = "timestamp"
    projection_type = "ALL"
  }
  
  point_in_time_recovery {
    enabled = true
  }
  
  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"
}
"""

# Usage
event_store = EventStore('event-store')

# Create order
event_store.append_event(
    aggregate_id='order-123',
    event_type='OrderCreated',
    event_data={
        'order_id': 'order-123',
        'customer_id': 'customer-456',
        'items': [{'sku': 'ABC', 'quantity': 2}],
        'total': 99.99
    }
)

# Pay order
event_store.append_event(
    aggregate_id='order-123',
    event_type='OrderPaid',
    event_data={
        'payment_id': 'payment-789',
        'amount': 99.99
    }
)

# Rebuild current state
current_state = event_store.rebuild_aggregate('order-123')
print(current_state)
```

---

## Saga Pattern (Distributed Transactions)

```python
from enum import Enum

class SagaStatus(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    COMPENSATING = 'compensating'
    COMPENSATED = 'compensated'

class SagaOrchestrator:
    """Orchestrate distributed transactions using Step Functions."""
    
    def __init__(self, state_machine_arn: str):
        self.stepfunctions = boto3.client('stepfunctions')
        self.state_machine_arn = state_machine_arn
        self.dynamodb = boto3.resource('dynamodb')
        self.saga_table = self.dynamodb.Table('saga-state')
    
    def start_saga(self, saga_id: str, input_data: dict):
        """Start saga execution."""
        
        # Record saga start
        self.saga_table.put_item(Item={
            'saga_id': saga_id,
            'status': SagaStatus.PENDING.value,
            'input_data': json.dumps(input_data),
            'started_at': datetime.now().isoformat()
        })
        
        # Start Step Functions execution
        response = self.stepfunctions.start_execution(
            stateMachineArn=self.state_machine_arn,
            name=saga_id,
            input=json.dumps({
                'saga_id': saga_id,
                **input_data
            })
        )
        
        return response['executionArn']
    
    def update_saga_status(self, saga_id: str, status: SagaStatus, details: dict = None):
        """Update saga status."""
        
        update_expr = 'SET #status = :status, updated_at = :timestamp'
        expr_values = {
            ':status': status.value,
            ':timestamp': datetime.now().isoformat()
        }
        
        if details:
            update_expr += ', details = :details'
            expr_values[':details'] = json.dumps(details)
        
        self.saga_table.update_item(
            Key={'saga_id': saga_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues=expr_values
        )
    
    def compensate_saga(self, saga_id: str):
        """Trigger saga compensation."""
        
        # Get saga state
        response = self.saga_table.get_item(Key={'saga_id': saga_id})
        saga = response['Item']
        
        # Update status
        self.update_saga_status(saga_id, SagaStatus.COMPENSATING)
        
        # Trigger compensation workflow
        input_data = json.loads(saga['input_data'])
        
        self.stepfunctions.start_execution(
            stateMachineArn=self.state_machine_arn.replace('-saga', '-compensation'),
            name=f"{saga_id}-compensation",
            input=json.dumps({
                'saga_id': saga_id,
                **input_data
            })
        )

# Step Functions Saga Definition (Terraform)
"""
resource "aws_sfn_state_machine" "order_saga" {
  name     = "order-saga"
  role_arn = aws_iam_role.step_functions_role.arn
  
  definition = jsonencode({
    Comment = "Order processing saga"
    StartAt = "ReserveInventory"
    States = {
      ReserveInventory = {
        Type = "Task"
        Resource = aws_lambda_function.reserve_inventory.arn
        Catch = [{
          ErrorEquals = ["States.ALL"]
          Next = "CompensateAll"
        }]
        Next = "ProcessPayment"
      }
      ProcessPayment = {
        Type = "Task"
        Resource = aws_lambda_function.process_payment.arn
        Catch = [{
          ErrorEquals = ["States.ALL"]
          Next = "ReleaseInventory"
        }]
        Next = "CreateShipment"
      }
      CreateShipment = {
        Type = "Task"
        Resource = aws_lambda_function.create_shipment.arn
        Catch = [{
          ErrorEquals = ["States.ALL"]
          Next = "RefundPayment"
        }]
        Next = "Success"
      }
      Success = {
        Type = "Succeed"
      }
      CompensateAll = {
        Type = "Pass"
        Next = "Failed"
      }
      ReleaseInventory = {
        Type = "Task"
        Resource = aws_lambda_function.release_inventory.arn
        Next = "Failed"
      }
      RefundPayment = {
        Type = "Task"
        Resource = aws_lambda_function.refund_payment.arn
        Next = "ReleaseInventory"
      }
      Failed = {
        Type = "Fail"
        Error = "SagaFailed"
        Cause = "One or more steps failed"
      }
    }
  })
}
"""

# Usage
orchestrator = SagaOrchestrator('arn:aws:states:us-east-1:123456789:stateMachine:order-saga')

# Start saga
execution_arn = orchestrator.start_saga(
    saga_id='saga-12345',
    input_data={
        'order_id': 'order-123',
        'customer_id': 'customer-456',
        'items': [{'sku': 'ABC', 'quantity': 2}],
        'payment_method': 'credit_card'
    }
)

print(f"Saga started: {execution_arn}")
```

---

## Complete Event-Driven System

```python
class EventDrivenSystem:
    """Complete event-driven system with SNS, SQS, EventBridge."""
    
    def __init__(self):
        self.sns = boto3.client('sns')
        self.sqs = boto3.client('sqs')
        self.eventbridge = boto3.client('events')
        self.dynamodb = boto3.resource('dynamodb')
        
        # Configuration
        self.sns_topic_arn = 'arn:aws:sns:us-east-1:123456789:application-events'
        self.event_bus_name = 'application-events'
        self.event_store = EventStore('event-store')
    
    def publish_domain_event(self, aggregate_id: str, event_type: str, event_data: dict):
        """Publish domain event to all channels."""
        
        # 1. Store in event store (event sourcing)
        event_id = self.event_store.append_event(aggregate_id, event_type, event_data)
        
        # 2. Publish to SNS (fan-out to multiple subscribers)
        self.sns.publish(
            TopicArn=self.sns_topic_arn,
            Message=json.dumps({
                'event_id': event_id,
                'event_type': event_type,
                'aggregate_id': aggregate_id,
                'data': event_data,
                'timestamp': datetime.now().isoformat()
            }),
            MessageAttributes={
                'event_type': {'DataType': 'String', 'StringValue': event_type},
                'aggregate_type': {'DataType': 'String', 'StringValue': aggregate_id.split('-')[0]}
            }
        )
        
        # 3. Publish to EventBridge (pattern matching and routing)
        self.eventbridge.put_events(
            Entries=[{
                'Source': f'com.myapp.{aggregate_id.split("-")[0]}',
                'DetailType': event_type,
                'Detail': json.dumps({
                    'event_id': event_id,
                    'aggregate_id': aggregate_id,
                    **event_data
                }),
                'EventBusName': self.event_bus_name
            }]
        )
        
        return event_id
    
    def handle_event(self, event: dict):
        """Generic event handler."""
        
        event_type = event['event_type']
        
        # Route to specific handler
        handlers = {
            'OrderCreated': self.handle_order_created,
            'OrderPaid': self.handle_order_paid,
            'OrderShipped': self.handle_order_shipped,
            'UserRegistered': self.handle_user_registered
        }
        
        handler = handlers.get(event_type)
        if handler:
            handler(event)
        else:
            print(f"No handler for event type: {event_type}")
    
    def handle_order_created(self, event: dict):
        """Handle order created event."""
        order_data = event['data']
        
        # Send confirmation email
        self.send_email(
            to=order_data['customer_email'],
            subject='Order Confirmation',
            body=f"Your order {order_data['order_id']} has been created"
        )
        
        # Update analytics
        self.update_analytics('order_created', order_data)
        
        # Trigger inventory check
        self.check_inventory(order_data['items'])
    
    def handle_order_paid(self, event: dict):
        """Handle order paid event."""
        # Trigger fulfillment process
        self.trigger_fulfillment(event['aggregate_id'])
    
    def handle_order_shipped(self, event: dict):
        """Handle order shipped event."""
        # Send tracking info
        self.send_tracking_info(event['data'])
    
    def handle_user_registered(self, event: dict):
        """Handle user registered event."""
        # Send welcome email
        # Create initial user preferences
        # Trigger onboarding workflow
        pass

# Deploy as Lambda function
def lambda_handler(event, context):
    """Lambda handler for events."""
    
    system = EventDrivenSystem()
    
    # Handle SNS message
    if 'Records' in event and event['Records'][0].get('EventSource') == 'aws:sns':
        for record in event['Records']:
            message = json.loads(record['Sns']['Message'])
            system.handle_event(message)
    
    # Handle EventBridge event
    elif 'detail-type' in event:
        system.handle_event({
            'event_type': event['detail-type'],
            'data': event['detail']
        })
    
    # Handle SQS message
    elif 'Records' in event and event['Records'][0].get('eventSource') == 'aws:sqs':
        for record in event['Records']:
            message = json.loads(record['body'])
            system.handle_event(message)
    
    return {'statusCode': 200}
```

---

## Best Practices

### 1. Event Design
- ✅ Use past tense for event names (OrderCreated, not CreateOrder)
- ✅ Make events immutable
- ✅ Include correlation IDs for tracing
- ✅ Version your events
- ✅ Keep events small and focused
- ✅ Include timestamp and source

### 2. Error Handling
- ✅ Use DLQ for failed messages
- ✅ Implement idempotent handlers
- ✅ Log all events and errors
- ✅ Monitor DLQ depth
- ✅ Implement retry with exponential backoff
- ✅ Have compensation logic ready

### 3. Performance
- ✅ Batch events when possible
- ✅ Use async processing
- ✅ Implement caching for frequent queries
- ✅ Monitor event processing latency
- ✅ Scale consumers based on queue depth

### 4. Security
- ✅ Encrypt events at rest and in transit
- ✅ Use IAM roles for access control
- ✅ Validate event schemas
- ✅ Audit event access
- ✅ Implement least privilege

### 5. Monitoring
- ✅ Track event throughput
- ✅ Monitor processing latency
- ✅ Alert on DLQ messages
- ✅ Use distributed tracing
- ✅ Log all event flows

---

This comprehensive guide covers all event-driven patterns and best practices for AWS!
