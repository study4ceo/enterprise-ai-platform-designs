# Global Multi-Region Architecture

## Why Multi-Region?

1. **Latency**: Users in Asia shouldn't hit US servers
2. **Compliance**: GDPR requires EU data in EU
3. **Availability**: Regional failures don't affect global service
4. **Scale**: Distribute load across continents

## Global Setup

```
                    ┌─────────────────┐
                    │   Route 53      │
                    │   (GeoDNS)      │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   US-EAST    │  │   EU-WEST    │  │  ASIA-PAC    │
    │   (Primary)  │  │  (Secondary) │  │  (Secondary) │
    └──────────────┘  └──────────────┘  └──────────────┘
         │                 │                  │
         └─────────────────┴──────────────────┘
                           │
                    Cross-Region
                    Replication
```

## Regional Architecture

Each region has **independent stack**:

```
Region: US-EAST
├── API Gateway (Load Balanced)
├── Kafka Cluster (3 brokers minimum)
├── Worker Pool (Auto-scaling)
├── Redis Cluster (3 nodes)
├── Cassandra Cluster (RF=3)
└── Monitoring Stack
```

## GeoDNS Routing (Route 53)

**Routing Policy**: Geolocation + Latency

```
api.notifications.com

Geolocation Rules:
- US traffic      → us-east.api.notifications.com
- EU traffic      → eu-west.api.notifications.com
- Asia traffic    → asia-pac.api.notifications.com
- Latency-based   → Closest region

Health Checks:
- /health endpoint
- Failover to next closest region if down
```

## Global Load Balancer

**Per Region**:
```
Route 53 → CloudFront (CDN) → ALB → API Gateway instances

CloudFront:
- Edge locations globally
- DDoS protection (AWS Shield)
- SSL termination

ALB (Application Load Balancer):
- Distributes across AZs
- Health checks
- Auto-scaling trigger
```

## Data Strategy

### 1. User Data (Cassandra)

**Strategy**: Write to local region, replicate async

```
Write Path:
User in EU → EU Cassandra (primary) → Replicate to US/Asia (async)

Read Path:
User in EU → EU Cassandra (local read)
```

**Cassandra Multi-DC Setup**:
```
Datacenter: us-east (RF=3)
Datacenter: eu-west (RF=3)
Datacenter: asia-pac (RF=3)

Consistency Level:
- Write: LOCAL_QUORUM (fast)
- Read: LOCAL_ONE (fast)
```

### 2. Kafka (Independent per Region)

**No cross-region replication** for Kafka because:
- Notifications are regional (APNs/FCM servers are regional)
- Real-time processing doesn't need global consistency
- Simpler operations

**Exception**: Analytics data replicated to central data warehouse

### 3. Redis (Regional)

**No replication** - Cache is ephemeral
- Each region has own cache
- Cache miss? Read from local Cassandra

## Notification Routing by Region

```
User in US:
API (US) → Kafka (US) → Worker (US) → APNs (US) → User

User in EU:
API (EU) → Kafka (EU) → Worker (EU) → APNs (EU) → User

User travels US → EU:
- API detects region from IP
- Routes to EU infrastructure
- Preferences fetched from local Cassandra replica
```

## Cross-Region Scenarios

### Scenario 1: Regional Failure

```
EU region down
├── Route 53 detects health check failure
├── Routes EU traffic to US-EAST
├── Slightly higher latency (acceptable)
└── Auto-alert + recovery process
```

### Scenario 2: Data Compliance (GDPR)

```
EU user data must stay in EU:
- Write to EU Cassandra ONLY
- Mark user as "data_region: EU"
- Block replication to US/Asia
- Serve from EU even if user travels
```

### Scenario 3: Global Campaign

```
Send to 100M users globally:
- API accepts request in any region
- Splits by user region
- Routes to respective regional Kafka
- Each region processes independently
```

## Latency Goals by Region

| Source | Target | Latency | Path |
|--------|--------|---------|------|
| US → US | User | 50ms | Local region |
| EU → EU | User | 50ms | Local region |
| US → EU | User | 150ms | Cross-region (failover) |
| Asia → US | User | 200ms | Cross-region (failover) |

## Disaster Recovery

**RTO (Recovery Time Objective)**: 5 minutes
**RPO (Recovery Point Objective)**: 0 (no data loss)

**Strategy**:
1. **Active-Active**: All regions active
2. **Automatic failover**: Route 53 health checks
3. **Data replication**: Cassandra multi-DC
4. **Backups**: Daily snapshots to S3 (cross-region)

## Cost Optimization

**Per Region**:
- API Gateway: $500/month
- Kafka: $5K/month
- Workers: $20K/month
- Cassandra: $10K/month
- Redis: $2K/month
- Load Balancer: $500/month
**Subtotal**: $38K/month

**3 Regions**: ~$115K/month

**Global Services**:
- Route 53: $100/month
- CloudFront: $2K/month
- Cross-region data transfer: $5K/month

**Total**: ~$122K/month

## Monitoring Global System

**Centralized Dashboard** (Grafana Cloud):
```
Global Overview:
├── Requests/sec per region (map)
├── Success rate per region (bar chart)
├── Latency per region (line chart)
└── Active regions (status lights)

Regional Drill-down:
├── US-EAST metrics
├── EU-WEST metrics
└── ASIA-PAC metrics
```

**Alerts**:
```
CRITICAL: Region completely down
WARNING: Region latency > 500ms
INFO: Traffic spike in region
```

## Traffic Distribution Estimate

Assuming 10B notifications/day globally:

| Region | % Traffic | Notifications/day | Peak req/sec |
|--------|-----------|-------------------|--------------|
| US-EAST | 40% | 4B | 46K |
| EU-WEST | 35% | 3.5B | 40K |
| ASIA-PAC | 25% | 2.5B | 29K |

## Deployment Strategy

**Rollout**:
```
Phase 1: Deploy to US-EAST (canary)
Phase 2: Deploy to EU-WEST (24h later)
Phase 3: Deploy to ASIA-PAC (24h later)
Phase 4: Monitor for 48h
```

**Rollback**: Instant via traffic shifting (Route 53 weight changes)

## Summary

**Key Decisions**:
1. ✅ GeoDNS (Route 53) - Automatic region routing
2. ✅ Multi-region active-active - No single point of failure
3. ✅ Independent Kafka per region - Simpler, faster
4. ✅ Cassandra multi-DC - Global consistency where needed
5. ✅ Regional caching - Low latency
6. ✅ Automatic failover - High availability

**Trade-offs**:
- 3x infrastructure cost
- More operational complexity
- Better latency and availability
- Regulatory compliance
