# Proximity-Based Optimization

## Why Proximity Matters

**Problems with ignoring proximity**:
- US server → Asia user = 200ms+ latency
- APNs/FCM servers are regional
- Network hops increase failure rate
- Cross-region data transfer costs $$$

**Goal**: Process notification closest to user's location

## Regional Provider Endpoints

### APNs (iOS)

```
Production:
- api.push.apple.com (US)
- api.push.apple.com.cn (China - different)

Development:
- api.development.push.apple.com
```

**Issue**: APNs routes globally but faster from US

### FCM (Android)

```
Global: fcm.googleapis.com (anycast - routes to nearest Google datacenter)

Regional optimization:
- US users → us-central1
- EU users → europe-west1
- Asia users → asia-east1
```

### SMS/Email Providers

```
Twilio:
- US: api.twilio.com
- EU: api.eu1.twilio.com
- AU: api.au1.twilio.com

SendGrid:
- Global API (routes automatically)
```

## Implementation Strategy

### 1. User Location Detection

```python
class UserLocationService:
    def get_user_region(self, user_id):
        # Priority order:
        # 1. User's timezone preference
        # 2. Last known IP location
        # 3. Device registration location
        # 4. Phone number country code
        
        user_prefs = get_user_preferences(user_id)
        
        if user_prefs.timezone:
            return self._timezone_to_region(user_prefs.timezone)
        
        if user_prefs.last_ip:
            return self._ip_to_region(user_prefs.last_ip)
        
        if user_prefs.device_country:
            return self._country_to_region(user_prefs.device_country)
        
        return 'us-east'  # Default
    
    def _timezone_to_region(self, timezone):
        mapping = {
            'America/New_York': 'us-east',
            'America/Los_Angeles': 'us-west',
            'Europe/London': 'eu-west',
            'Asia/Tokyo': 'asia-pac',
            'Asia/Singapore': 'asia-pac'
        }
        return mapping.get(timezone, 'us-east')
```

### 2. Request Routing at API Gateway

```python
@app.post("/api/notifications")
async def send_notification(request, user_id: int):
    # Detect user region
    user_region = user_location_service.get_user_region(user_id)
    current_region = get_current_region()  # Where API runs
    
    if user_region != current_region:
        # Forward to correct region
        return await forward_to_region(user_region, request)
    
    # Process locally
    return await process_notification(request)

async def forward_to_region(target_region, request):
    """Forward request to regional API"""
    regional_endpoints = {
        'us-east': 'https://us-east.api.company.com',
        'eu-west': 'https://eu-west.api.company.com',
        'asia-pac': 'https://asia-pac.api.company.com'
    }
    
    url = regional_endpoints[target_region]
    response = await http_client.post(f"{url}/api/notifications", json=request)
    return response
```

### 3. Worker Placement Strategy

```
Region: US-EAST
├── Workers: 400 instances
├── Handles: US, Canada, South America users
└── Connects to: APNs/FCM US endpoints

Region: EU-WEST
├── Workers: 350 instances
├── Handles: EU, Africa, Middle East users
└── Connects to: APNs/FCM EU endpoints

Region: ASIA-PAC
├── Workers: 250 instances
├── Handles: Asia, Australia, Oceania users
└── Connects to: APNs/FCM Asia endpoints
```

### 4. Smart Adapter Selection

```python
class ProximityAwareAdapter:
    def __init__(self):
        self.regional_endpoints = {
            'us-east': {
                'fcm': 'https://fcm.googleapis.com',
                'twilio': 'https://api.twilio.com',
                'sendgrid': 'https://api.sendgrid.com'
            },
            'eu-west': {
                'fcm': 'https://fcm.googleapis.com',  # Same (anycast)
                'twilio': 'https://api.eu1.twilio.com',
                'sendgrid': 'https://api.eu.sendgrid.com'
            },
            'asia-pac': {
                'fcm': 'https://fcm.googleapis.com',  # Same (anycast)
                'twilio': 'https://api.au1.twilio.com',
                'sendgrid': 'https://api.sendgrid.com'
            }
        }
    
    def get_adapter(self, channel, region):
        endpoints = self.regional_endpoints[region]
        
        if channel == 'push':
            return FCMAdapter(endpoint=endpoints['fcm'])
        elif channel == 'sms':
            return TwilioAdapter(endpoint=endpoints['twilio'])
        elif channel == 'email':
            return SendGridAdapter(endpoint=endpoints['sendgrid'])
```

## Latency Optimization

### Measured Latencies

```
Same Region (Worker → Provider):
- US worker → APNs US: 10-20ms
- EU worker → APNs US: 80-120ms
- Asia worker → APNs US: 150-250ms

Optimized (Worker → Regional Provider):
- US worker → APNs US: 10-20ms
- EU worker → FCM EU: 15-25ms
- Asia worker → FCM Asia: 15-30ms
```

**Savings**: 100-200ms per notification

### Cost Optimization

```
Data Transfer Pricing (AWS):
- Same region: FREE
- Cross-region (US-EU): $0.02/GB
- Internet egress: $0.09/GB

Example:
10B notifications/day × 5KB avg = 50TB/day

Same region: $0
Cross-region: $1,000/day = $30K/month
Internet: $4,500/day = $135K/month

Savings: $100K+/month with regional processing
```

## Kafka Partitioning by Geography

```python
class GeographicPartitioner:
    """Custom Kafka partitioner based on user region"""
    
    def partition(self, key, all_partitions, available_partitions):
        user_id = key  # Assuming key is user_id
        user_region = self.get_user_region(user_id)
        
        # Assign partitions to regions
        region_partitions = {
            'us-east': range(0, 4000),      # 40% of partitions
            'eu-west': range(4000, 7500),   # 35%
            'asia-pac': range(7500, 10000)  # 25%
        }
        
        partition_range = region_partitions[user_region]
        return hash(user_id) % len(partition_range) + partition_range.start
```

**Benefit**: Workers in each region consume their region's partitions

## Device Token Storage Strategy

```sql
-- Store tokens with regional hint
CREATE TABLE device_tokens (
    user_id BIGINT,
    platform VARCHAR(10),  -- 'ios', 'android'
    token TEXT,
    region VARCHAR(20),    -- 'us-east', 'eu-west', 'asia-pac'
    registered_at TIMESTAMP,
    last_used_at TIMESTAMP,
    ip_country VARCHAR(2),
    PRIMARY KEY (user_id, platform)
);

-- Query optimization: filter by region first
SELECT token FROM device_tokens 
WHERE region = 'eu-west' AND user_id IN (...)
```

## Edge Cases

### 1. User Traveling

```python
def handle_traveling_user(user_id, current_ip):
    """User in different region than registered"""
    
    registered_region = get_user_registered_region(user_id)
    current_region = ip_to_region(current_ip)
    
    if registered_region != current_region:
        # User is traveling
        # Strategy: Send from current region for lower latency
        return current_region
    
    return registered_region
```

### 2. Multi-Region Users

```python
def handle_multi_region_user(user_id):
    """User has devices in multiple regions"""
    
    devices = get_user_devices(user_id)
    device_regions = [d.region for d in devices]
    
    if len(set(device_regions)) > 1:
        # Has devices in multiple regions
        # Send from each region to respective devices
        return 'multi-region'
    
    return device_regions[0]
```

### 3. China Special Case

```python
class ChinaSpecialHandling:
    """China has different infrastructure"""
    
    def should_use_china_infrastructure(self, user_id):
        user_region = get_user_region(user_id)
        return user_region == 'cn-north' or user_region == 'cn-south'
    
    def get_china_adapter(self, channel):
        if channel == 'push':
            # Use Huawei HMS, Xiaomi, Oppo push services
            return HMSAdapter()
        
        # Email/SMS need ICP license
        return ChinaCompliantAdapter()
```

## Monitoring Regional Performance

```python
# Metrics per region
metrics = {
    'us-east': {
        'notifications_sent': 4_000_000_000,
        'avg_latency_ms': 25,
        'success_rate': 99.5,
        'cost_per_million': 15
    },
    'eu-west': {
        'notifications_sent': 3_500_000_000,
        'avg_latency_ms': 30,
        'success_rate': 99.3,
        'cost_per_million': 18
    },
    'asia-pac': {
        'notifications_sent': 2_500_000_000,
        'avg_latency_ms': 35,
        'success_rate': 99.0,
        'cost_per_million': 20
    }
}
```

**Dashboard**: Map view showing real-time metrics per region

## Summary

**Key Optimizations**:
1. ✅ **Regional worker placement** - Workers in user's region
2. ✅ **Proximity-aware routing** - Route requests to nearest region
3. ✅ **Regional provider endpoints** - Use local provider APIs
4. ✅ **Geographic Kafka partitioning** - Region-specific partitions
5. ✅ **Cost savings** - Avoid cross-region data transfer

**Latency improvements**:
- Before: 150-250ms (cross-region)
- After: 15-35ms (same region)
- **Improvement**: 85-90% reduction

**Cost savings**: $100K+/month in data transfer

**Trade-off**: More infrastructure complexity
