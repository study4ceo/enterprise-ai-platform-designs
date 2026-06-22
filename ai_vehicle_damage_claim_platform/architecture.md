# AI-Powered Vehicle Damage Detection and Claim Platform - Architecture

**Date:** June 18, 2026  
**Version:** 1.0

---

## 1. System Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│              CLIENT LAYER                            │
│  Mobile App (iOS/Android) | Web Portal (Next.js 16) │
└────────────────────┬─────────────────────────────────┘
                     │
                HTTPS/REST
                     │
┌────────────────────▼─────────────────────────────────┐
│       API GATEWAY (Golang + Fiber)                   │
│  PASETO Auth | Image Validation | Rate Limiting     │
└────────────────────┬─────────────────────────────────┘
                     │
                   gRPC
                     │
┌────────────────────▼─────────────────────────────────┐
│    AI PROCESSING LAYER (Python + FastAPI)            │
│  ┌────────────────────────────────────────────┐     │
│  │      Damage Detection Service              │     │
│  │  • GPT-5.5 Vision API                      │     │
│  │  • Claude Opus 4.8                         │     │
│  │  • YOLOv8 pre-screening                    │     │
│  └────────────┬───────────────────────────────┘     │
│               │                                      │
│  ┌────────────▼───────────────────────────────┐     │
│  │      Severity Assessment Service           │     │
│  │  • ML classification model                 │     │
│  │  • Structural analysis                     │     │
│  └────────────┬───────────────────────────────┘     │
│               │                                      │
│  ┌────────────▼───────────────────────────────┐     │
│  │      Cost Estimation Service               │     │
│  │  • Parts database                          │     │
│  │  • Regional pricing engine                 │     │
│  └────────────┬───────────────────────────────┘     │
│               │                                      │
│  ┌────────────▼───────────────────────────────┐     │
│  │      Claim Generation Service              │     │
│  │  • PDF generator                           │     │
│  │  • ACORD XML formatter                     │     │
│  └────────────────────────────────────────────┘     │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│              DATA LAYER                              │
│  ┌──────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ PostgreSQL   │  │   Redis    │  │  AWS S3    │  │

│  │  (RLS)       │  │   Cache    │  │   Images   │  │
│  └──────────────┘  └────────────┘  └────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## 2. Processing Pipeline Architecture

### **End-to-End Flow**

```python
class DamageAssessmentPipeline:
    """Complete damage assessment workflow"""
    
    async def execute(self, images: list[bytes], vehicle: VehicleInfo) -> AssessmentResult:
        """
        Pipeline stages:
        1. Image validation (< 2s)
        2. Damage detection (< 5s)
        3. Severity assessment (< 3s)
        4. Cost estimation (< 2s)
        5. Claim generation (< 5s)
        Total: < 15s
        """
        
        start_time = time.time()
        
        # Stage 1: Validation (parallel)
        validation_results = await asyncio.gather(
            *[self.validator.validate(img) for img in images]
        )
        valid_images = [img for img, valid in zip(images, validation_results) if valid['valid']]
        
        # Stage 2: Damage detection (parallel per image)
        damage_results = await asyncio.gather(
            *[self.detector.detect_damage(img) for img in valid_images]
        )
        all_damages = [d for damages in damage_results for d in damages]
        
        # Stage 3: Severity assessment (parallel per damage)
        severity_results = await asyncio.gather(
            *[self.severity_assessor.assess(d) for d in all_damages]
        )
        
        # Stage 4: Cost estimation (parallel per damage)
        cost_results = await asyncio.gather(
            *[self.cost_estimator.estimate(d, vehicle) for d in all_damages]
        )
        
        # Stage 5: Claim generation (single operation)
        claim = await self.claim_generator.generate(
            damages=all_damages,
            costs=cost_results,
            vehicle=vehicle,
            images=valid_images
        )
        
        processing_time = time.time() - start_time
        
        return AssessmentResult(
            damages=all_damages,
            costs=cost_results,
            claim=claim,
            processing_time_ms=processing_time * 1000
        )
```

---

## 3. Image Processing Architecture

```
┌──────────────────────────────────────────┐
│        Image Upload Handler              │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────┐     │
│  │  Format Validation             │     │
│  │  • JPEG, PNG, WEBP only        │     │

│  │  • Max 20MB size               │     │
│  │  • Min 800x600 resolution      │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Quality Checks                │     │
│  │  • Brightness (30-220)         │     │
│  │  • Sharpness (>0.4)            │     │
│  │  • Vehicle presence detection  │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Preprocessing                 │     │
│  │  • Orientation correction      │     │
│  │  • Noise reduction             │     │
│  │  • Contrast enhancement         │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Storage                       │     │
│  │  • Original → S3               │     │
│  │  • Metadata → PostgreSQL       │     │
│  │  • Thumbnail → S3              │     │
│  └────────────────────────────────┘     │
└──────────────────────────────────────────┘
```

---

## 4. AI Model Architecture

### **Damage Detection Model Stack**

```
┌─────────────────────────────────────┐
│      Detection Pipeline             │
├─────────────────────────────────────┤
│                                     │
│  Step 1: Fast Pre-screening        │
│  ┌──────────────────────────┐      │
│  │     YOLOv8 Model         │      │
│  │  • Real-time detection   │      │
│  │  • Bounding boxes        │      │
│  │  • < 1 second            │      │
│  └──────────────────────────┘      │
│               │                     │
│               ▼                     │
│  Step 2: Detailed Analysis         │
│  ┌──────────────────────────┐      │
│  │   GPT-5.5 Vision API     │      │
│  │  • Damage classification │      │
│  │  • Part identification   │      │
│  │  • Description           │      │
│  │  • 2-4 seconds           │      │
│  └──────────────────────────┘      │
│               │                     │
│               ▼                     │
│  Step 3: Complex Case Review       │
│  ┌──────────────────────────┐      │
│  │   Claude Opus 4.8        │      │
│  │  • Structural damage     │      │
│  │  • Second opinion        │      │
│  │  • Ensemble with GPT     │      │
│  │  • If confidence < 0.7   │      │
│  └──────────────────────────┘      │
└─────────────────────────────────────┘
```

---

## 5. Multi-Tenant Data Isolation

```python
# Tenant context per request
async def set_tenant_context(request: Request):

    """Set tenant context for Row-Level Security"""
    
    token = request.headers.get('Authorization')
    claims = verify_paseto_token(token)
    
    tenant_id = claims['tenant_id']
    
    # Set PostgreSQL session variable for RLS
    await db.execute(
        "SET app.tenant_id = $1",
        tenant_id
    )
    
    # All subsequent queries automatically filtered by tenant_id
    # No explicit WHERE tenant_id = X needed!
```

### **Tenant Isolation Layers**

1. **Database Level:** PostgreSQL RLS policies
2. **Storage Level:** S3 bucket prefixes per tenant
3. **Cache Level:** Redis key prefixes per tenant
4. **API Level:** Token validation enforces tenant context

---

## 6. Cost Estimation Engine

```
┌──────────────────────────────────────────┐
│      Cost Estimation Pipeline            │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────┐     │
│  │  Parts Database Lookup         │     │
│  │  • Make/Model/Year match       │     │
│  │  • OEM vs. Aftermarket         │     │
│  │  • Availability check          │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Labor Rate Calculator         │     │
│  │  • Regional rates              │     │
│  │  • Complexity multiplier       │     │
│  │  • Estimated hours             │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Materials Cost                │     │
│  │  • Paint matching              │     │
│  │  • Supplies & consumables      │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Regional Adjustment           │     │
│  │  • Location-based pricing      │     │
│  │  • +/- 20% variation           │     │
│  └────────────┬───────────────────┘     │
│               │                          │
│  ┌────────────▼───────────────────┐     │
│  │  Confidence Range              │     │
│  │  • Min/Max estimates           │     │
│  │  • +/- 15% confidence band     │     │
│  └────────────────────────────────┘     │
└──────────────────────────────────────────┘
```

---

## 7. Claim Generation Workflow

```python
class ClaimWorkflow:
    """Multi-format claim generation"""
    
    async def generate_all_formats(self, assessment: DamageAssessment) -> ClaimPackage:
        """Generate claim in all required formats"""
        
        # Parallel generation of all formats
        pdf_task = self.generate_pdf_report(assessment)
        json_task = self.generate_json(assessment)

        acord_task = self.generate_acord_xml(assessment)
        
        pdf, json, acord = await asyncio.gather(
            pdf_task,
            json_task,
            acord_task
        )
        
        return ClaimPackage(
            pdf_report=pdf,
            json_data=json,
            acord_xml=acord,
            claim_number=assessment.claim_number
        )
```

---

## 8. Caching Strategy

### **Redis Cache Layers**

```python
class CacheStrategy:
    """Multi-level caching for performance"""
    
    # Level 1: Parts pricing (1 hour TTL)
    async def get_parts_price(self, make: str, model: str, year: int, part: str):
        cache_key = f"parts:{make}:{model}:{year}:{part}"
        cached = await redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        price = await self.parts_db.lookup(make, model, year, part)
        await redis.setex(cache_key, 3600, json.dumps(price))
        return price
    
    # Level 2: Labor rates (24 hour TTL)
    async def get_labor_rate(self, location: str):
        cache_key = f"labor:{location}"
        cached = await redis.get(cache_key)
        
        if cached:
            return float(cached)
        
        rate = await self.labor_service.get_rate(location)
        await redis.setex(cache_key, 86400, str(rate))
        return rate
    
    # Level 3: ML model results (session TTL)
    async def cache_detection_result(self, image_hash: str, result: dict):
        cache_key = f"detection:{image_hash}"
        await redis.setex(cache_key, 1800, json.dumps(result))
```

---

## 9. Error Handling & Recovery

### **Circuit Breaker Pattern**

```python
from circuitbreaker import circuit

class AIServiceClient:
    @circuit(failure_threshold=5, recovery_timeout=60)
    async def call_gpt_vision(self, image: bytes) -> dict:
        """Call GPT-5.5 Vision with circuit breaker"""
        
        try:
            response = await self.gpt_client.analyze(image, timeout=10)
            return response
        except TimeoutError:
            # Fallback to cached result or YOLOv8 only
            return self.get_fallback_result(image)
        except Exception as e:
            logfire.error("gpt_vision_failed", error=str(e))
            raise
```

### **Retry Strategy**

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def upload_to_s3(file: bytes, key: str):
    """Upload with exponential backoff retry"""
    await s3_client.put_object(Bucket=BUCKET, Key=key, Body=file)
```

---

## 10. Observability Architecture

```
┌──────────────────────────────────────────┐
│       Observability Stack                │
├──────────────────────────────────────────┤
│                                          │
│  ┌────────────────────────────────┐     │
│  │  Distributed Tracing           │     │

│  │  • Logfire spans               │     │
│  │  • Request correlation IDs     │     │
│  │  • Cross-service tracing       │     │
│  └────────────────────────────────┘     │
│                                          │
│  ┌────────────────────────────────┐     │
│  │  Metrics Collection            │     │
│  │  • API response times          │     │
│  │  • AI model latency            │     │
│  │  • Error rates                 │     │
│  │  • Resource utilization        │     │
│  └────────────────────────────────┘     │
│                                          │
│  ┌────────────────────────────────┐     │
│  │  Logging                       │     │
│  │  • Structured JSON logs        │     │
│  │  • Log levels (info/warn/error)│     │
│  │  • 7-year retention            │     │
│  └────────────────────────────────┘     │
│                                          │
│  ┌────────────────────────────────┐     │
│  │  Alerting                      │     │
│  │  • Error rate > 5%             │     │
│  │  • P95 latency > 15s           │     │
│  │  • AI model failures           │     │
│  └────────────────────────────────┘     │
└──────────────────────────────────────────┘
```

---

## 11. Scalability Design

### **Horizontal Scaling**

```
Load Balancer
    │
    ├─ API Gateway Pod 1 ────┐
    ├─ API Gateway Pod 2 ────┤
    └─ API Gateway Pod 3 ────┤
                             │
                        gRPC Pool
                             │
    ┌─ ML Service Pod 1 ─────┤
    ├─ ML Service Pod 2 ─────┤
    ├─ ML Service Pod 3 ─────┤
    ├─ ML Service Pod 4 ─────┤
    └─ ML Service Pod 5 ─────┘
```

### **Auto-Scaling Rules**

```yaml
# Kubernetes HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-service
  minReplicas: 5
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: queue_depth
      target:
        type: AverageValue
        averageValue: "100"
```

---

## 12. Database Optimization

### **Connection Pooling**

```python
# asyncpg connection pool
from asyncpg import create_pool

db_pool = await create_pool(
    host=DB_HOST,
    port=5432,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    min_size=10,
    max_size=50,

    command_timeout=60
)
```

### **Indexing Strategy**

```sql
-- Performance indexes
CREATE INDEX idx_assessments_tenant_created 
    ON damage_assessments(tenant_id, created_at DESC);

CREATE INDEX idx_damages_assessment 
    ON damages(assessment_id);

CREATE INDEX idx_images_assessment 
    ON images(assessment_id);

CREATE INDEX idx_claims_status 
    ON claims(status) WHERE status != 'draft';

-- Partial index for active assessments
CREATE INDEX idx_assessments_processing 
    ON damage_assessments(tenant_id, id) 
    WHERE status = 'processing';
```

---

## 13. Deployment Architecture

### **Kubernetes Deployment**

```
┌─────────────────────────────────────────┐
│         Production Cluster              │
├─────────────────────────────────────────┤
│                                         │
│  Namespace: vehicle-damage-platform     │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  API Gateway                   │    │
│  │  • 3-10 pods (CPU autoscale)   │    │
│  │  • 2 CPU, 4GB RAM per pod      │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  ML Service                    │    │
│  │  • 5-50 pods (queue autoscale) │    │
│  │  • 4 CPU, 16GB RAM, 1 GPU      │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  Background Workers            │    │
│  │  • 2-10 pods (queue depth)     │    │
│  │  • 2 CPU, 8GB RAM per pod      │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Data Services                   │
├─────────────────────────────────────────┤
│                                         │
│  PostgreSQL:                            │
│  • Primary (r6g.2xlarge)                │
│  • Read Replica 1 (r6g.xlarge)          │
│  • Read Replica 2 (r6g.xlarge)          │
│                                         │
│  Redis:                                 │
│  • 3-node cluster (cache.r6g.large)    │
│                                         │
│  S3:                                    │
│  • Standard storage (images)            │
│  • Intelligent tiering (old images)     │
└─────────────────────────────────────────┘
```

---

## 14. Disaster Recovery

### **Backup Strategy**

```python
# Automated backup schedule
class BackupStrategy:
    FULL_BACKUP_SCHEDULE = "0 2 * * *"  # Daily at 2 AM
    INCREMENTAL_SCHEDULE = "0 */6 * * *"  # Every 6 hours
    
    async def backup_database(self):
        """Full database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_full_{timestamp}.sql"
        
        await execute_command(
            f"pg_dump {DB_NAME} | gzip > {backup_file}.gz"
        )
        
        # Upload to S3
        await s3_client.upload_file(
            f"{backup_file}.gz",
            BACKUP_BUCKET,
            f"database/full/{backup_file}.gz"
        )
```

### **Recovery Objectives**

- **RPO (Recovery Point Objective):** 1 hour
- **RTO (Recovery Time Objective):** 4 hours
- **Backup Retention:** 30 days (hot), 1 year (cold)

---

## 15. Security Architecture

### **Defense in Depth**

```
Layer 1: Network
  • WAF (Web Application Firewall)
  • DDoS protection
  • VPC isolation

Layer 2: Application
  • PASETO authentication
  • Rate limiting (1000 req/min)
  • Input validation

Layer 3: Data
  • TLS 1.3 in transit
  • AES-256 at rest
  • Row-Level Security

Layer 4: Monitoring
  • Intrusion detection
  • Anomaly detection
  • Audit logging
```

---

**Status:** ✅ Complete

**Version:** 1.0  
**Date:** June 18, 2026
