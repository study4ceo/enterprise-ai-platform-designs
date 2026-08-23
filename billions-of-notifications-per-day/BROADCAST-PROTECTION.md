# Broadcast Protection: Preventing System Overload

## The Problem

**Scenario**: Marketing clicks "Send to All Users" button
- System has 100M active users
- Button triggers 100M notifications instantly
- Kafka gets 100M messages in seconds
- Workers overwhelmed, lag explodes
- System crashes, ALL notifications stop (even critical ones)

**Real incident examples**:
- Uber: Accidental broadcast took down notification system (2019)
- Facebook: Test broadcast sent to millions (2018)
- Twitter: Mass DM feature caused cascading failures (2020)

## Protection Strategy

```
Defense in Depth:
├─ Layer 1: UI Confirmation (prevent accidents)
├─ Layer 2: API Rate Limiting (slow down ingestion)
├─ Layer 3: Broadcast Detector (identify patterns)
├─ Layer 4: Staged Rollout (gradual sending)
├─ Layer 5: Emergency Brake (kill switch)
└─ Layer 6: Resource Isolation (protect critical traffic)
```

## Layer 1: UI Confirmation

```typescript
// Frontend confirmation dialog
async function handleBroadcastClick() {
  const userCount = await getUserCount();
  
  if (userCount > 10000) {
    // Show scary confirmation
    const confirmed = await showDialog({
      title: "⚠️ BROADCAST TO LARGE AUDIENCE",
      message: `
        You are about to send to ${userCount.toLocaleString()} users.
        
        This will:
        - Take ${estimateTime(userCount)} to complete
        - Cost approximately ${estimateCost(userCount)}
        - Cannot be cancelled once started
        
        Are you absolutely sure?
      `,
      buttons: ["Cancel", "Yes, Send Broadcast"],
      dangerousAction: true,
      requiresTyping: "CONFIRM BROADCAST"  // Must type exact text
    });
    
    if (!confirmed) return;
  }
  
  // Require approval for > 1M users
  if (userCount > 1_000_000) {
    const approval = await requestManagerApproval({
      action: "broadcast",
      recipient_count: userCount,
      requester: currentUser.id
    });
    
    if (!approval.approved) {
      alert("Broadcast requires manager approval");
      return;
    }
  }
  
  await sendBroadcast();
}
```

## Layer 2: API Rate Limiting

```python
class BroadcastRateLimiter:
    """Limit how fast broadcasts can be submitted"""
    
    def __init__(self):
        self.max_per_second = 10000  # Max 10K requests/sec
        self.max_per_campaign = 1_000_000  # Max 1M per campaign initially
        self.rate_limiter = TokenBucket(rate=10000, capacity=50000)
    
    async def submit_broadcast(self, campaign):
        """Submit broadcast with rate limiting"""
        
        recipient_count = len(campaign.recipients)
        
        # Reject massive broadcasts upfront
        if recipient_count > 100_000_000:
            raise BroadcastTooLargeError(
                f"Cannot broadcast to {recipient_count} users. "
                f"Contact support for broadcasts > 100M"
            )
        
        # Large broadcast requires staged rollout
        if recipient_count > 1_000_000:
            return await self._staged_rollout(campaign)
        
        # Small broadcast - send directly (with rate limit)
        return await self._send_with_rate_limit(campaign)
    
    async def _send_with_rate_limit(self, campaign):
        """Send with rate limiting"""
        
        for recipient in campaign.recipients:
            # Rate limit each request
            await self.rate_limiter.acquire()
            
            # Send notification
            await self._send_single(recipient, campaign)
            
            # Track progress
            campaign.sent_count += 1
            
            if campaign.sent_count % 10000 == 0:
                logger.info(
                    f"Broadcast progress: {campaign.sent_count}/{campaign.total}",
                    extra={'campaign_id': campaign.id}
                )
```

## Layer 3: Broadcast Detector

```python
class BroadcastDetector:
    """Detect if incoming traffic is a broadcast"""
    
    def __init__(self):
        self.window_size = 60  # 60 seconds
        self.request_counts = {}
        self.broadcast_threshold = 10000  # 10K requests/min from same source
    
    async def check_request(self, request):
        """Check if request is part of broadcast"""
        
        # Key: Who is sending (user_id, campaign_id)
        key = f"{request.user_id}:{request.get('campaign_id', 'none')}"
        
        # Count requests in window
        now = time.time()
        if key not in self.request_counts:
            self.request_counts[key] = []
        
        # Add current request
        self.request_counts[key].append(now)
        
        # Remove old requests outside window
        cutoff = now - self.window_size
        self.request_counts[key] = [
            t for t in self.request_counts[key] if t > cutoff
        ]
        
        request_count = len(self.request_counts[key])
        
        # Detect broadcast
        if request_count > self.broadcast_threshold:
            logger.warning(
                f"Broadcast detected: {request_count} requests/min",
                extra={
                    'user_id': request.user_id,
                    'campaign_id': request.get('campaign_id'),
                    'rate': request_count / self.window_size * 60
                }
            )
            
            # Flag as broadcast
            request.is_broadcast = True
            request.broadcast_size = request_count
            
            # Apply broadcast-specific handling
            await self._handle_broadcast(request)
        
        return request
    
    async def _handle_broadcast(self, request):
        """Special handling for broadcasts"""
        
        # Option 1: Slow down (apply stricter rate limit)
        request.rate_limit = 5000  # Reduce to 5K/sec
        
        # Option 2: Downgrade priority
        if request.priority == 'high':
            request.priority = 'medium'
            logger.info(f"Downgraded broadcast priority to medium")
        
        # Option 3: Force staged rollout
        if request.broadcast_size > 100000:
            raise RequiresStagedRolloutError(
                "Broadcasts > 100K must use staged rollout API"
            )
```

## Layer 4: Staged Rollout

```python
class StagedRollout:
    """Send broadcast in controlled waves"""
    
    def __init__(self):
        self.wave_size = 100000  # 100K per wave
        self.wave_delay = 300    # 5 min between waves
        self.max_concurrent_waves = 3
    
    async def execute_rollout(self, campaign):
        """Execute broadcast in stages"""
        
        recipients = campaign.recipients
        total = len(recipients)
        
        logger.info(
            f"Starting staged rollout: {total} recipients",
            extra={
                'campaign_id': campaign.id,
                'wave_size': self.wave_size,
                'estimated_duration': self._estimate_duration(total)
            }
        )
        
        # Split into waves
        waves = self._create_waves(recipients)
        
        # Track campaign state
        campaign.status = 'in_progress'
        campaign.waves_total = len(waves)
        campaign.waves_completed = 0
        
        for wave_num, wave in enumerate(waves):
            # Check if campaign was cancelled
            if await self._is_cancelled(campaign.id):
                logger.warning(f"Campaign {campaign.id} cancelled")
                campaign.status = 'cancelled'
                break
            
            # Send wave
            logger.info(
                f"Sending wave {wave_num + 1}/{len(waves)}",
                extra={
                    'campaign_id': campaign.id,
                    'wave_size': len(wave),
                    'progress': f"{campaign.sent_count}/{total}"
                }
            )
            
            # Send with rate limiting
            wave_results = await self._send_wave(wave, campaign)
            
            # Update progress
            campaign.waves_completed += 1
            campaign.sent_count += len(wave)
            
            # Check wave success rate
            success_rate = wave_results['success'] / len(wave)
            
            if success_rate < 0.90:
                # Wave had too many failures - pause campaign
                logger.error(
                    f"Wave {wave_num} success rate: {success_rate:.1%} - PAUSING",
                    extra={'campaign_id': campaign.id}
                )
                
                campaign.status = 'paused'
                await self._notify_admin(campaign, wave_results)
                break
            
            # Wait before next wave (unless last wave)
            if wave_num < len(waves) - 1:
                logger.info(f"Waiting {self.wave_delay}s before next wave")
                await asyncio.sleep(self.wave_delay)
        
        # Mark complete
        if campaign.status == 'in_progress':
            campaign.status = 'completed'
            logger.info(
                f"Campaign completed: {campaign.sent_count}/{total} sent",
                extra={'campaign_id': campaign.id}
            )
    
    def _create_waves(self, recipients):
        """Split recipients into waves"""
        waves = []
        for i in range(0, len(recipients), self.wave_size):
            waves.append(recipients[i:i + self.wave_size])
        return waves
    
    def _estimate_duration(self, total):
        """Estimate how long rollout will take"""
        waves = (total + self.wave_size - 1) // self.wave_size
        send_time = total / 10000  # 10K/sec throughput
        wave_delays = (waves - 1) * self.wave_delay
        return send_time + wave_delays
    
    async def _send_wave(self, wave, campaign):
        """Send single wave"""
        
        results = {'success': 0, 'failed': 0, 'errors': []}
        
        # Send with rate limiting
        for recipient in wave:
            try:
                await self.rate_limiter.acquire()
                await self._send_single(recipient, campaign)
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
                
                # Stop wave if too many errors
                if results['failed'] > len(wave) * 0.1:  # > 10% failure
                    logger.error(f"Wave failure rate too high, stopping wave")
                    break
        
        return results
```

## Layer 5: Emergency Brake (Kill Switch)

```python
class EmergencyBrake:
    """Kill switch to stop broadcasts"""
    
    def __init__(self):
        self.redis = redis.Redis()
        self.brake_key = "emergency_brake:active"
        self.cancelled_campaigns = set()
    
    async def check_brake(self):
        """Check if emergency brake is active"""
        return await self.redis.get(self.brake_key) == "1"
    
    async def activate_brake(self, reason):
        """EMERGENCY: Stop all broadcasts"""
        
        logger.critical(
            f"🚨 EMERGENCY BRAKE ACTIVATED: {reason}",
            extra={'activated_by': 'system', 'reason': reason}
        )
        
        # Set brake flag
        await self.redis.set(self.brake_key, "1")
        
        # Stop accepting new broadcasts
        await self._stop_broadcast_api()
        
        # Cancel all in-progress campaigns
        campaigns = await self._get_active_campaigns()
        for campaign in campaigns:
            await self.cancel_campaign(campaign.id)
        
        # Notify ops team
        await self._page_oncall("Emergency brake activated")
        
        # Metrics
        metrics.increment('emergency_brake_activated')
    
    async def deactivate_brake(self):
        """Release emergency brake"""
        
        logger.warning("Emergency brake deactivated")
        await self.redis.delete(self.brake_key)
    
    async def cancel_campaign(self, campaign_id):
        """Cancel specific campaign"""
        
        logger.warning(f"Cancelling campaign {campaign_id}")
        self.cancelled_campaigns.add(campaign_id)
        
        # Mark as cancelled in DB
        await db.update(
            'campaigns',
            {'id': campaign_id},
            {'status': 'cancelled'}
        )
        
        metrics.increment('campaign_cancelled', tags={'campaign_id': campaign_id})

# Use in worker
class BroadcastAwareWorker:
    async def process(self, message):
        # Check emergency brake before processing
        if await emergency_brake.check_brake():
            logger.warning("Emergency brake active - rejecting broadcast message")
            return  # Don't process
        
        # Check if campaign cancelled
        campaign_id = message.get('campaign_id')
        if campaign_id and campaign_id in emergency_brake.cancelled_campaigns:
            logger.info(f"Campaign {campaign_id} cancelled - skipping")
            return
        
        # Process normally
        await self._send(message)
```

## Layer 6: Resource Isolation

```python
class ResourceIsolation:
    """Isolate broadcast traffic from critical traffic"""
    
    def __init__(self):
        # Separate Kafka topics
        self.topics = {
            'critical': 'notifications-critical',
            'high': 'notifications-high',
            'broadcast': 'notifications-broadcast',  # Separate topic!
            'low': 'notifications-low'
        }
        
        # Separate worker pools
        self.worker_pools = {
            'critical': 100,   # Always available
            'high': 400,
            'broadcast': 200,  # Dedicated broadcast workers
            'low': 300
        }
    
    def route_message(self, notification):
        """Route to appropriate topic"""
        
        # Detect broadcast
        if notification.get('is_broadcast') or notification.get('campaign_id'):
            topic = self.topics['broadcast']
        else:
            topic = self.topics[notification['priority']]
        
        return topic
    
    async def handle_overload(self):
        """If broadcast overloading, shed load"""
        
        broadcast_lag = await self._get_topic_lag('notifications-broadcast')
        
        if broadcast_lag > 1_000_000:
            logger.critical(
                f"Broadcast topic overloaded: {broadcast_lag} lag",
                extra={'action': 'pausing_broadcasts'}
            )
            
            # Pause broadcast workers
            await self._pause_workers('broadcast')
            
            # Activate emergency brake
            await emergency_brake.activate_brake("Broadcast topic overload")
            
            # Scale up broadcast workers
            await self._scale_workers('broadcast', factor=2.0)
```

## Real-Time Monitoring

```python
class BroadcastMonitor:
    """Monitor broadcast health"""
    
    async def monitor_loop(self):
        while True:
            metrics = await self._collect_metrics()
            
            # Check for anomalies
            if metrics['incoming_rate'] > 50000:  # > 50K/sec
                logger.warning(
                    f"High incoming rate: {metrics['incoming_rate']}/sec",
                    extra=metrics
                )
                
                # Auto-activate rate limiting
                await self._activate_strict_rate_limit()
            
            if metrics['kafka_lag_broadcast'] > 500000:
                logger.error(f"Broadcast lag critical: {metrics['kafka_lag_broadcast']}")
                
                # Consider emergency brake
                await self._evaluate_emergency_brake(metrics)
            
            await asyncio.sleep(10)
    
    async def _evaluate_emergency_brake(self, metrics):
        """Decide if emergency brake needed"""
        
        # Criteria for emergency brake
        conditions = [
            metrics['kafka_lag_broadcast'] > 1_000_000,
            metrics['worker_utilization'] > 0.95,
            metrics['success_rate'] < 0.85,
            metrics['critical_lag'] > 10000  # Critical traffic affected
        ]
        
        if sum(conditions) >= 3:  # At least 3 conditions met
            await emergency_brake.activate_brake(
                f"Multiple critical conditions: {conditions}"
            )
```

## API Design

```python
# Good: Explicit broadcast API with safeguards
@app.post("/api/v1/broadcasts")
async def create_broadcast(broadcast: BroadcastRequest):
    """Create broadcast campaign (staged rollout)"""
    
    # Validate
    if len(broadcast.recipients) > 100_000_000:
        raise HTTPException(400, "Max 100M recipients")
    
    # Require approval for large broadcasts
    if len(broadcast.recipients) > 1_000_000:
        if not broadcast.approval_token:
            raise HTTPException(403, "Requires manager approval")
        
        if not await verify_approval(broadcast.approval_token):
            raise HTTPException(403, "Invalid approval token")
    
    # Create campaign
    campaign = await db.create_campaign({
        'user_id': current_user.id,
        'recipients': broadcast.recipients,
        'message': broadcast.message,
        'status': 'pending',
        'staged_rollout': True
    })
    
    # Start staged rollout (async)
    background_tasks.add_task(
        staged_rollout.execute_rollout,
        campaign
    )
    
    return {
        'campaign_id': campaign.id,
        'status': 'scheduled',
        'estimated_duration': staged_rollout._estimate_duration(len(broadcast.recipients)),
        'recipients': len(broadcast.recipients),
        'waves': (len(broadcast.recipients) + 100000 - 1) // 100000
    }

# Get campaign status
@app.get("/api/v1/broadcasts/{campaign_id}")
async def get_campaign_status(campaign_id: str):
    campaign = await db.get_campaign(campaign_id)
    
    return {
        'campaign_id': campaign.id,
        'status': campaign.status,  # pending, in_progress, paused, completed, cancelled
        'sent': campaign.sent_count,
        'total': campaign.total_count,
        'progress': campaign.sent_count / campaign.total_count,
        'waves_completed': campaign.waves_completed,
        'waves_total': campaign.waves_total,
        'estimated_completion': campaign.estimated_completion
    }

# Cancel campaign
@app.post("/api/v1/broadcasts/{campaign_id}/cancel")
async def cancel_campaign(campaign_id: str):
    await emergency_brake.cancel_campaign(campaign_id)
    return {'status': 'cancelled'}
```

## Configuration Limits

```yaml
# config/broadcast-limits.yaml
broadcast_protection:
  # Rate limits
  max_requests_per_second: 10000
  max_requests_per_campaign: 100_000_000
  
  # Staged rollout
  staged_rollout_threshold: 1_000_000  # > 1M requires staged
  wave_size: 100000                     # 100K per wave
  wave_delay_seconds: 300               # 5 min between waves
  
  # Approval requirements
  requires_approval_above: 1_000_000
  requires_admin_approval_above: 10_000_000
  
  # Emergency brake
  auto_brake_conditions:
    kafka_lag_threshold: 1_000_000
    failure_rate_threshold: 0.15      # > 15% failures
    critical_lag_threshold: 10000     # If critical traffic affected
  
  # Resource isolation
  separate_topic: true
  dedicated_workers: 200
  max_broadcast_workers: 1000
```

## Big Red Cancel Button

**Purpose**: Give operators instant panic button to stop broadcasts

### UI Implementation

```tsx
// Campaign monitoring dashboard
function CampaignMonitor({ campaign }) {
  const [cancelling, setCancelling] = useState(false);
  
  return (
    <div className="campaign-dashboard">
      {/* Campaign status */}
      <div className="campaign-header">
        <h1>Campaign: {campaign.name}</h1>
        <span className={`status status-${campaign.status}`}>
          {campaign.status.toUpperCase()}
        </span>
      </div>
      
      {/* Progress */}
      <div className="progress-section">
        <ProgressBar 
          current={campaign.sent_count} 
          total={campaign.total_count}
          label={`${campaign.sent_count.toLocaleString()} / ${campaign.total_count.toLocaleString()}`}
        />
        
        <div className="stats">
          <Stat label="Wave" value={`${campaign.waves_completed} / ${campaign.waves_total}`} />
          <Stat label="Success Rate" value={`${(campaign.success_rate * 100).toFixed(1)}%`} />
          <Stat label="Est. Completion" value={formatTime(campaign.estimated_completion)} />
        </div>
      </div>
      
      {/* THE BIG RED BUTTON */}
      {campaign.status === 'in_progress' && (
        <div className="danger-zone">
          <button
            className="btn-emergency-cancel"
            onClick={() => handleEmergencyCancel(campaign.id)}
            disabled={cancelling}
          >
            {cancelling ? (
              <>
                <Spinner /> CANCELLING...
              </>
            ) : (
              <>
                <StopIcon /> EMERGENCY CANCEL
              </>
            )}
          </button>
          <p className="warning-text">
            ⚠️ This will immediately stop the campaign. 
            Already sent notifications cannot be recalled.
          </p>
        </div>
      )}
      
      {/* Live metrics */}
      <div className="live-metrics">
        <MetricCard 
          title="Sending Rate" 
          value={`${campaign.current_rate.toLocaleString()}/sec`}
          trend={campaign.rate_trend}
        />
        <MetricCard 
          title="Kafka Lag" 
          value={campaign.kafka_lag.toLocaleString()}
          status={campaign.kafka_lag > 10000 ? 'critical' : 'ok'}
        />
        <MetricCard 
          title="Failed" 
          value={campaign.failed_count.toLocaleString()}
          status={campaign.success_rate < 0.90 ? 'warning' : 'ok'}
        />
      </div>
    </div>
  );
}

async function handleEmergencyCancel(campaignId) {
  // Confirmation dialog
  const confirmed = await showConfirmDialog({
    title: "🚨 EMERGENCY CANCEL",
    message: "Are you sure you want to IMMEDIATELY STOP this campaign?",
    confirmText: "YES, STOP NOW",
    cancelText: "Continue Campaign",
    danger: true
  });
  
  if (!confirmed) return;
  
  setCancelling(true);
  
  try {
    // Call cancel API
    const response = await fetch(`/api/v1/broadcasts/${campaignId}/cancel`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (response.ok) {
      showNotification({
        type: 'success',
        title: 'Campaign Cancelled',
        message: 'The campaign has been stopped. No more messages will be sent.'
      });
      
      // Refresh campaign status
      await refreshCampaign();
    } else {
      throw new Error('Cancel failed');
    }
  } catch (error) {
    showNotification({
      type: 'error',
      title: 'Cancel Failed',
      message: 'Could not cancel campaign. Contact support immediately.'
    });
  } finally {
    setCancelling(false);
  }
}
```

**CSS for Big Red Button**:
```css
.btn-emergency-cancel {
  width: 100%;
  padding: 20px 40px;
  font-size: 24px;
  font-weight: bold;
  color: white;
  background: linear-gradient(135deg, #d32f2f 0%, #c62828 100%);
  border: 3px solid #b71c1c;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(211, 47, 47, 0.4);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.btn-emergency-cancel:hover:not(:disabled) {
  background: linear-gradient(135deg, #c62828 0%, #b71c1c 100%);
  box-shadow: 0 6px 20px rgba(211, 47, 47, 0.6);
  transform: translateY(-2px);
}

.btn-emergency-cancel:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(211, 47, 47, 0.4);
}

.btn-emergency-cancel:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.danger-zone {
  margin: 40px 0;
  padding: 30px;
  background: rgba(211, 47, 47, 0.05);
  border: 2px solid rgba(211, 47, 47, 0.2);
  border-radius: 8px;
}

.warning-text {
  margin-top: 12px;
  text-align: center;
  color: #d32f2f;
  font-weight: 500;
}
```

### Backend Cancel Implementation

```python
class CampaignCanceller:
    """Handle immediate campaign cancellation"""
    
    def __init__(self):
        self.redis = redis.Redis()
        self.cancelled_campaigns = set()
    
    async def cancel_campaign(self, campaign_id, cancelled_by):
        """IMMEDIATELY cancel campaign - stop all processing"""
        
        # Log cancellation
        logger.critical(
            f"🚨 CAMPAIGN CANCELLED: {campaign_id}",
            extra={
                'campaign_id': campaign_id,
                'cancelled_by': cancelled_by,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        # Step 1: Mark as cancelled in Redis (fast, immediate effect)
        await self._mark_cancelled_redis(campaign_id)
        
        # Step 2: Stop the staged rollout loop
        await self._stop_rollout_loop(campaign_id)
        
        # Step 3: Update database
        campaign = await self._update_campaign_status(campaign_id, 'cancelled')
        
        # Step 4: Purge pending messages from Kafka (if possible)
        await self._purge_pending_messages(campaign_id)
        
        # Step 5: Log final stats
        await self._log_cancellation_stats(campaign)
        
        # Step 6: Notify stakeholders
        await self._notify_cancellation(campaign, cancelled_by)
        
        return {
            'status': 'cancelled',
            'sent_before_cancel': campaign.sent_count,
            'remaining': campaign.total_count - campaign.sent_count,
            'cancelled_at': datetime.utcnow().isoformat()
        }
    
    async def _mark_cancelled_redis(self, campaign_id):
        """Mark in Redis for instant worker awareness"""
        
        # Set cancellation flag (expires in 24h)
        await self.redis.setex(
            f"campaign:cancelled:{campaign_id}",
            86400,  # 24 hours
            "1"
        )
        
        # Add to cancelled set
        await self.redis.sadd("cancelled_campaigns", campaign_id)
        
        # Publish to Redis pub/sub for instant notification
        await self.redis.publish(
            "campaign:cancellations",
            json.dumps({
                'campaign_id': campaign_id,
                'action': 'cancel',
                'timestamp': datetime.utcnow().isoformat()
            })
        )
        
        logger.info(f"Campaign {campaign_id} marked cancelled in Redis")
    
    async def _stop_rollout_loop(self, campaign_id):
        """Stop the staged rollout background task"""
        
        # Signal to running rollout task
        await self.redis.set(
            f"rollout:stop:{campaign_id}",
            "1"
        )
        
        logger.info(f"Signaled rollout loop to stop for {campaign_id}")
    
    async def _update_campaign_status(self, campaign_id, status):
        """Update campaign in database"""
        
        campaign = await db.campaigns.find_one({'id': campaign_id})
        
        await db.campaigns.update_one(
            {'id': campaign_id},
            {
                '$set': {
                    'status': status,
                    'cancelled_at': datetime.utcnow(),
                    'final_sent_count': campaign['sent_count']
                }
            }
        )
        
        return campaign
    
    async def _purge_pending_messages(self, campaign_id):
        """Try to remove unsent messages from Kafka (not always possible)"""
        
        # Note: Kafka doesn't support message deletion easily
        # Instead, workers will check cancellation flag before processing
        
        logger.info(
            f"Cannot purge Kafka messages for {campaign_id}. "
            f"Workers will skip cancelled messages."
        )
    
    async def _log_cancellation_stats(self, campaign):
        """Log what happened before cancellation"""
        
        stats = {
            'campaign_id': campaign['id'],
            'total_planned': campaign['total_count'],
            'sent': campaign['sent_count'],
            'remaining': campaign['total_count'] - campaign['sent_count'],
            'waves_completed': campaign['waves_completed'],
            'waves_total': campaign['waves_total'],
            'success_rate': campaign.get('success_rate', 0),
            'duration_seconds': (
                datetime.utcnow() - campaign['started_at']
            ).total_seconds() if campaign.get('started_at') else 0
        }
        
        logger.info(
            "Campaign cancellation stats",
            extra=stats
        )
        
        # Store in analytics
        await analytics.record_cancellation(stats)
    
    async def _notify_cancellation(self, campaign, cancelled_by):
        """Notify relevant people"""
        
        # Notify campaign creator
        await notifications.send({
            'user_id': campaign['created_by'],
            'title': 'Campaign Cancelled',
            'body': f"Your campaign '{campaign['name']}' was cancelled by {cancelled_by}",
            'priority': 'high'
        })
        
        # Notify ops team
        await slack.post_message(
            channel='#ops-alerts',
            text=f"🚨 Campaign {campaign['id']} cancelled by {cancelled_by}. "
                 f"{campaign['sent_count']}/{campaign['total_count']} sent before cancel."
        )

# Worker checks cancellation before processing
class CancellationAwareWorker:
    def __init__(self):
        self.redis = redis.Redis()
        self.local_cancelled_cache = set()
        
        # Subscribe to cancellation events
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('campaign:cancellations')
        
        # Start listening for cancellations
        asyncio.create_task(self._listen_cancellations())
    
    async def _listen_cancellations(self):
        """Listen for real-time cancellation events"""
        
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                campaign_id = data['campaign_id']
                
                logger.info(f"Received cancellation event: {campaign_id}")
                self.local_cancelled_cache.add(campaign_id)
    
    async def process_message(self, message):
        """Process with cancellation check"""
        
        campaign_id = message.get('campaign_id')
        
        if not campaign_id:
            # Not a campaign message, process normally
            return await self._send(message)
        
        # Check local cache first (fastest)
        if campaign_id in self.local_cancelled_cache:
            logger.info(f"Skipping cancelled campaign {campaign_id} (local cache)")
            metrics.increment('messages_skipped_cancelled')
            return
        
        # Check Redis (authoritative)
        is_cancelled = await self.redis.exists(f"campaign:cancelled:{campaign_id}")
        
        if is_cancelled:
            logger.info(f"Skipping cancelled campaign {campaign_id} (Redis)")
            self.local_cancelled_cache.add(campaign_id)
            metrics.increment('messages_skipped_cancelled')
            return
        
        # Not cancelled, process normally
        return await self._send(message)
```

### Cancel API Endpoint

```python
@app.post("/api/v1/broadcasts/{campaign_id}/cancel")
async def cancel_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user)
):
    """EMERGENCY CANCEL - Stop campaign immediately"""
    
    # Get campaign
    campaign = await db.campaigns.find_one({'id': campaign_id})
    
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    # Check permissions
    if campaign['created_by'] != current_user.id and not current_user.is_admin:
        raise HTTPException(403, "Not authorized to cancel this campaign")
    
    # Check if already cancelled/completed
    if campaign['status'] in ['cancelled', 'completed']:
        return {
            'message': f"Campaign already {campaign['status']}",
            'status': campaign['status']
        }
    
    # Execute cancellation
    result = await campaign_canceller.cancel_campaign(
        campaign_id,
        cancelled_by=current_user.email
    )
    
    # Audit log
    await audit_log.record({
        'action': 'campaign_cancelled',
        'campaign_id': campaign_id,
        'user_id': current_user.id,
        'timestamp': datetime.utcnow(),
        'sent_before_cancel': result['sent_before_cancel']
    })
    
    return result
```

### Global Emergency Brake (Cancel All Broadcasts)

```python
@app.post("/api/v1/emergency/brake")
async def activate_emergency_brake(
    reason: str,
    current_user: User = Depends(get_current_user)
):
    """GLOBAL KILL SWITCH - Stop ALL broadcasts"""
    
    # Require admin
    if not current_user.is_admin:
        raise HTTPException(403, "Requires admin privileges")
    
    # Activate brake
    logger.critical(
        f"🚨🚨🚨 GLOBAL EMERGENCY BRAKE ACTIVATED 🚨🚨🚨",
        extra={
            'activated_by': current_user.email,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    # Cancel ALL active campaigns
    active_campaigns = await db.campaigns.find({
        'status': 'in_progress'
    }).to_list(None)
    
    cancelled_count = 0
    for campaign in active_campaigns:
        await campaign_canceller.cancel_campaign(
            campaign['id'],
            cancelled_by=f"EMERGENCY_BRAKE:{current_user.email}"
        )
        cancelled_count += 1
    
    # Set global brake flag
    await redis.set("emergency_brake:active", "1")
    
    # Notify everyone
    await slack.post_message(
        channel='#critical-alerts',
        text=f"🚨🚨🚨 EMERGENCY BRAKE ACTIVATED 🚨🚨🚨\n"
             f"By: {current_user.email}\n"
             f"Reason: {reason}\n"
             f"Cancelled: {cancelled_count} campaigns"
    )
    
    return {
        'status': 'emergency_brake_active',
        'cancelled_campaigns': cancelled_count,
        'activated_by': current_user.email,
        'reason': reason
    }
```

### Global Emergency UI

```tsx
// Global emergency brake button (for admins only)
function GlobalEmergencyBrake() {
  const [active, setActive] = useState(false);
  const [activating, setActivating] = useState(false);
  
  return (
    <div className="global-emergency-section">
      <h2>🚨 Global Emergency Controls</h2>
      
      <div className="emergency-brake-container">
        <button
          className="btn-global-emergency"
          onClick={handleGlobalBrake}
          disabled={activating || active}
        >
          {activating ? (
            'ACTIVATING...'
          ) : active ? (
            '✓ EMERGENCY BRAKE ACTIVE'
          ) : (
            '🚨 ACTIVATE EMERGENCY BRAKE'
          )}
        </button>
        
        <p className="emergency-description">
          ⚠️ WARNING: This will IMMEDIATELY STOP ALL active broadcast campaigns.
          Use only in system emergency.
        </p>
        
        {active && (
          <button
            className="btn-deactivate-brake"
            onClick={handleDeactivateBrake}
          >
            Deactivate Emergency Brake
          </button>
        )}
      </div>
      
      {/* Active campaigns list */}
      <ActiveCampaignsList />
    </div>
  );
}

async function handleGlobalBrake() {
  const reason = await promptForReason();
  
  if (!reason) return;
  
  const confirmed = await showConfirmDialog({
    title: "🚨 GLOBAL EMERGENCY BRAKE",
    message: `
      This will STOP ALL active broadcast campaigns immediately.
      
      Reason: ${reason}
      
      This action is logged and will notify all stakeholders.
      
      Are you ABSOLUTELY SURE?
    `,
    confirmText: "YES, ACTIVATE EMERGENCY BRAKE",
    danger: true
  });
  
  if (!confirmed) return;
  
  setActivating(true);
  
  try {
    await fetch('/api/v1/emergency/brake', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason })
    });
    
    setActive(true);
    showNotification({
      type: 'critical',
      title: 'Emergency Brake Activated',
      message: 'All broadcasts have been stopped.'
    });
  } catch (error) {
    showNotification({
      type: 'error',
      title: 'Activation Failed',
      message: 'Could not activate emergency brake!'
    });
  } finally {
    setActivating(false);
  }
}
```

### Cancellation Timing

**How fast does cancel work?**

```
User clicks "Cancel" button
    ↓
< 50ms: API receives request
    ↓
< 100ms: Redis flag set (workers start checking)
    ↓
< 500ms: All workers aware via Redis pub/sub
    ↓
< 1s: Staged rollout loop stops
    ↓
< 5s: Database updated
    ↓
Result: No messages sent after ~1 second
```

**Messages already in flight**:
- In Kafka queue: Will be skipped by workers (check cancel flag)
- Being sent to FCM/APNs: Cannot be recalled (already sent)
- In FCM/APNs queue: Cannot be recalled (out of our control)

**Typical cancellation**:
- Campaign: 10M recipients
- Sent: 2M (before cancel)
- In Kafka: 500K (will be skipped)
- Already delivered: 1.5M (cannot recall)
- Successfully prevented: 8M+ 🎯

## Summary

**Protection Layers**:

| Layer | Protection | Impact |
|-------|-----------|--------|
| 1. UI Confirmation | Require typing "CONFIRM BROADCAST" | Prevent accidents |
| 2. Rate Limiting | Max 10K/sec ingestion | Slow down ingestion |
| 3. Broadcast Detector | Detect > 10K/min from same source | Auto-apply limits |
| 4. Staged Rollout | 100K per wave, 5 min delay | Controlled sending |
| 5. Emergency Brake | Kill switch to cancel all | Stop disasters |
| 6. Resource Isolation | Separate Kafka topic + workers | Protect critical traffic |

**Safe Broadcast Flow**:
```
Marketing → "Send to All" Button
    ↓
UI shows: "Send to 50M users? Type CONFIRM"
    ↓
API: Create campaign (staged rollout)
    ↓
Wave 1: Send 100K users → Wait 5 min → Check success rate
    ↓
Wave 2: Send 100K users → Wait 5 min → Check success rate
    ↓ (continues...)
Wave 500: Send 100K users → Campaign complete
```

**Emergency Brake Triggers**:
- Kafka lag > 1M
- Success rate < 85%
- Critical traffic lag > 10K
- Manual activation by ops

**Result**: Cannot take down system with broadcast button ✅