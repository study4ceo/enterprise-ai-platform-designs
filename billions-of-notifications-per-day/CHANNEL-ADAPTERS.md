# Channel Adapters

## Why Adapters?

**Problems without adapters**:
- Different APIs for each provider (APNs, FCM, Twilio)
- Hard to switch providers
- Difficult to add new channels
- Testing nightmare

**Solution**: Adapter pattern - unified interface

## Adapter Architecture

```
Worker
  ↓
ChannelRouter
  ↓
  ├─→ PushAdapter ──→ [APNsAdapter, FCMAdapter, HMSAdapter]
  ├─→ EmailAdapter ──→ [SendGridAdapter, SESAdapter, MailgunAdapter]
  ├─→ SMSAdapter ──→ [TwilioAdapter, SNSAdapter, VonageAdapter]
  └─→ InAppAdapter ──→ [WebSocketAdapter, PollingAdapter]
```

## Base Interface

```python
class NotificationAdapter(ABC):
    """Base adapter interface"""
    
    @abstractmethod
    async def send(self, notification: Notification) -> Result:
        pass
    
    @abstractmethod
    def validate_token(self, token: str) -> bool:
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        pass
    
    @abstractmethod
    def supports_batch(self) -> bool:
        pass
```

## Push Adapters

### APNs Adapter (iOS)

```python
class APNsAdapter(NotificationAdapter):
    def __init__(self):
        self.client = aioapns.APNs(
            key='path/to/key.p8',
            key_id='KEY_ID',
            team_id='TEAM_ID',
            topic='com.app.bundle'
        )
    
    async def send(self, notification):
        payload = {
            'aps': {
                'alert': {
                    'title': notification.title,
                    'body': notification.body
                },
                'badge': notification.badge,
                'sound': notification.sound or 'default',
                'content-available': 1
            },
            'custom_data': notification.data
        }
        
        return await self.client.send_notification(
            token_hex=notification.device_token,
            notification=payload,
            priority=10 if notification.priority == 'high' else 5,
            expiration=int(time.time()) + notification.ttl
        )
    
    def supports_batch(self) -> bool:
        return True  # Up to 5000/connection
```

### FCM Adapter (Android)

```python
class FCMAdapter(NotificationAdapter):
    def __init__(self):
        self.url = 'https://fcm.googleapis.com/v1/projects/PROJECT_ID/messages:send'
        self.credentials = service_account.Credentials.from_service_account_file('key.json')
    
    async def send(self, notification):
        message = {
            'token': notification.device_token,
            'notification': {
                'title': notification.title,
                'body': notification.body,
                'image': notification.image_url
            },
            'data': notification.data,
            'android': {
                'priority': 'high' if notification.priority == 'high' else 'normal',
                'ttl': f'{notification.ttl}s'
            }
        }
        
        response = await self.http_client.post(self.url, json={'message': message})
        return self._parse_response(response)
    
    def supports_batch(self) -> bool:
        return True  # Up to 1000/request
```

### HMS Adapter (Huawei)

```python
class HMSAdapter(NotificationAdapter):
    """For devices without Google services"""
    
    async def send(self, notification):
        message = {
            'notification': {
                'title': notification.title,
                'body': notification.body
            },
            'android': {
                'fast_app_target': 1,
                'urgency': 'HIGH' if notification.priority == 'high' else 'NORMAL'
            },
            'token': [notification.device_token]
        }
        
        return await self.hms_client.send(message)
```

## Email Adapters

### SendGrid Adapter

```python
class SendGridAdapter(NotificationAdapter):
    def __init__(self):
        self.client = SendGridAPIClient(api_key='SENDGRID_KEY')
    
    async def send(self, notification):
        message = Mail(
            from_email='noreply@company.com',
            to_emails=notification.recipient_email,
            subject=notification.title,
            html_content=notification.html_body
        )
        
        # Custom headers
        message.add_header('X-Priority', str(notification.priority))
        
        response = await self.client.send(message)
        return response
    
    def supports_batch(self) -> bool:
        return True  # Up to 1000/request
```

### SES Adapter (AWS)

```python
class SESAdapter(NotificationAdapter):
    def __init__(self):
        self.client = boto3.client('ses', region_name='us-east-1')
    
    async def send(self, notification):
        response = self.client.send_email(
            Source='noreply@company.com',
            Destination={'ToAddresses': [notification.recipient_email]},
            Message={
                'Subject': {'Data': notification.title},
                'Body': {'Html': {'Data': notification.html_body}}
            }
        )
        return response
```

## SMS Adapters

### Twilio Adapter

```python
class TwilioAdapter(NotificationAdapter):
    def __init__(self):
        self.client = Client(account_sid='SID', auth_token='TOKEN')
    
    async def send(self, notification):
        message = self.client.messages.create(
            to=notification.phone_number,
            from_='+1234567890',
            body=notification.body
        )
        return message
    
    def supports_batch(self) -> bool:
        return False  # Twilio doesn't support batch
```

### SNS Adapter (AWS)

```python
class SNSAdapter(NotificationAdapter):
    def __init__(self):
        self.client = boto3.client('sns')
    
    async def send(self, notification):
        response = self.client.publish(
            PhoneNumber=notification.phone_number,
            Message=notification.body
        )
        return response
```

## Channel Router

```python
class ChannelRouter:
    def __init__(self):
        self.adapters = {
            'push': {
                'ios': APNsAdapter(),
                'android': FCMAdapter(),
                'huawei': HMSAdapter()
            },
            'email': {
                'sendgrid': SendGridAdapter(),
                'ses': SESAdapter()
            },
            'sms': {
                'twilio': TwilioAdapter(),
                'sns': SNSAdapter()
            }
        }
        
        # Primary providers
        self.primary_providers = {
            'push': 'fcm',
            'email': 'sendgrid',
            'sms': 'twilio'
        }
    
    async def send(self, notification):
        channel = notification.channel  # 'push', 'email', 'sms'
        
        # Get adapter
        adapter = self._get_adapter(channel, notification)
        
        try:
            result = await adapter.send(notification)
            return result
        except Exception as e:
            # Fallback to secondary provider
            return await self._fallback_send(channel, notification, e)
    
    def _get_adapter(self, channel, notification):
        if channel == 'push':
            platform = notification.device_platform  # 'ios', 'android'
            return self.adapters['push'][platform]
        
        provider = self.primary_providers[channel]
        return self.adapters[channel][provider]
    
    async def _fallback_send(self, channel, notification, error):
        """Try secondary provider if primary fails"""
        if channel == 'email':
            fallback = self.adapters['email']['ses']
        elif channel == 'sms':
            fallback = self.adapters['sms']['sns']
        else:
            raise error
        
        logger.warning(f"Primary provider failed, using fallback: {error}")
        return await fallback.send(notification)
```

## Provider Configuration

```yaml
# config/providers.yaml

push:
  apns:
    enabled: true
    key_path: /keys/apns.p8
    key_id: ABC123
    team_id: DEF456
    topic: com.company.app
    max_connections: 100
    
  fcm:
    enabled: true
    credentials_path: /keys/fcm.json
    project_id: company-app
    batch_size: 1000
    
  hms:
    enabled: true
    app_id: HMS_APP_ID
    app_secret: HMS_SECRET

email:
  sendgrid:
    enabled: true
    api_key: SENDGRID_KEY
    from_email: noreply@company.com
    batch_size: 1000
    rate_limit: 10000  # per second
    
  ses:
    enabled: true
    region: us-east-1
    from_email: noreply@company.com
    
sms:
  twilio:
    enabled: true
    account_sid: TWILIO_SID
    auth_token: TWILIO_TOKEN
    from_number: +1234567890
    
  sns:
    enabled: true
    region: us-east-1
```

## Provider Selection Strategy

```python
class ProviderSelector:
    """Smart provider selection based on cost, performance, availability"""
    
    def select_provider(self, channel, region, priority):
        if priority == 'critical':
            # Use most reliable (cost doesn't matter)
            return 'primary'
        
        if region == 'US':
            # Twilio better in US
            return 'twilio' if channel == 'sms' else 'primary'
        
        if region == 'EU':
            # GDPR compliant providers
            return 'eu_provider'
        
        # Cost optimization for low priority
        if priority == 'low':
            return 'cheapest'
        
        return 'primary'
```

## Retry & Circuit Breaker

```python
class AdapterWithResilience:
    def __init__(self, adapter):
        self.adapter = adapter
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
    
    @retry(max_attempts=3, backoff=exponential_backoff)
    async def send(self, notification):
        if self.circuit_breaker.is_open():
            raise CircuitBreakerOpenError(f"{self.adapter.get_provider_name()} unavailable")
        
        try:
            result = await self.adapter.send(notification)
            self.circuit_breaker.record_success()
            return result
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise
```

## Batch Processing

```python
class BatchAdapter:
    """Wrapper for batch-capable adapters"""
    
    def __init__(self, adapter, batch_size=1000):
        self.adapter = adapter
        self.batch_size = batch_size
        self.pending_batch = []
    
    async def add_to_batch(self, notification):
        self.pending_batch.append(notification)
        
        if len(self.pending_batch) >= self.batch_size:
            await self.flush()
    
    async def flush(self):
        if not self.pending_batch:
            return
        
        results = await self.adapter.send_batch(self.pending_batch)
        self.pending_batch = []
        return results
```

## Testing Adapters

```python
class MockAdapter(NotificationAdapter):
    """For testing without hitting real APIs"""
    
    def __init__(self):
        self.sent_notifications = []
    
    async def send(self, notification):
        self.sent_notifications.append(notification)
        return {'status': 'success', 'message_id': f'mock_{uuid.uuid4()}'}
    
    def get_sent_count(self):
        return len(self.sent_notifications)
```

## Summary

**Key Benefits**:
1. ✅ **Unified interface** - Same code for all providers
2. ✅ **Easy provider switch** - Change config, not code
3. ✅ **Fallback support** - Auto-switch if primary fails
4. ✅ **Testing** - Mock adapters for unit tests
5. ✅ **Provider-specific features** - Wrapped in adapter

**Adapters**:
- Push: APNs, FCM, HMS
- Email: SendGrid, SES, Mailgun
- SMS: Twilio, SNS, Vonage

**Pattern**: Strategy + Adapter + Factory
