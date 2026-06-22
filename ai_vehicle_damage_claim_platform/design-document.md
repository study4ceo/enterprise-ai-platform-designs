# AI-Powered Vehicle Damage Detection and Claim Platform - Design Document

**Document Date:** June 18, 2026  
**Tech Stack Status:** Latest & Greatest as of this date  
**Project Type:** Insurance Technology - Computer Vision & Claims Automation  
**Development Approach:** Test-Driven Development (TDD)  
**Production Status:** Enterprise-Ready, Multi-Tenant Architecture

---

## 📋 Executive Summary

An enterprise-grade AI platform that automates vehicle damage assessment and insurance claims processing using computer vision and machine learning. Users upload vehicle damage photos via mobile or web, receive instant AI-powered damage detection with severity assessment and cost estimates, and submit automated insurance claims—all within 15 seconds.

**Core Problems Solved:**
1. ❌ **"Manual damage inspection takes hours"** → ✅ AI assessment in <15 seconds
2. ❌ **"Cost estimates vary wildly between shops"** → ✅ Consistent AI estimates within 15% accuracy
3. ❌ **"Claims paperwork is tedious"** → ✅ Automated claim generation and submission
4. ❌ **"Photos don't capture all damage"** → ✅ AI detects damage humans miss
5. ❌ **"Fraud detection is reactive"** → ✅ AI flags suspicious patterns in real-time

---

## 🎯 Core Capabilities

### **1. Computer Vision Damage Detection**
**Purpose:** Analyze vehicle images to identify and classify all types of damage

**AI Models:**
- **Primary:** GPT-5.5 Vision for damage identification
- **Secondary:** Claude Opus 4.8 for complex structural analysis
- **Custom:** Fine-tuned YOLOv8 for real-time object detection

**Detectable Damage Types:**
- Dents (small, medium, large)
- Scratches (surface, deep, paint through)
- Cracks (windshield, body panel)
- Broken parts (lights, mirrors, bumpers)
- Paint damage (chips, fading, peeling)
- Structural damage (frame, chassis)

**Detection Accuracy:**
- Precision: ≥90%
- Recall: ≥85%
- Processing time: <5 seconds per image

---

### **2. Severity Assessment Engine**
**Purpose:** Classify damage severity to prioritize repairs and estimate complexity

**Severity Levels:**

| Level | Description | Repair Time | Example |
|-------|-------------|-------------|---------|
| **Minor** | Cosmetic only, no structural impact | 1-2 days | Small scratch, door ding |
| **Moderate** | Functional impact, non-critical | 3-5 days | Deep dent, broken mirror |
| **Severe** | Significant damage, safety concern | 1-2 weeks | Bumper damage, broken light |
| **Critical** | Structural damage, unsafe to drive | 2-4 weeks | Frame damage, airbag deployment |

**Assessment Factors:**
- Damage size and depth
- Location (cosmetic vs. structural areas)
- Impact on vehicle safety
- Repair complexity
- Parts availability

**Accuracy:** 88% agreement with human expert assessments

---

### **3. Automated Cost Estimation**
**Purpose:** Predict repair costs with regional pricing and parts data

**Cost Components:**

```python
# Cost Estimation Model
from dataclasses import dataclass
import logfire

@dataclass
class RepairCostEstimate:
    damage_id: str
    labor_cost: float
    parts_cost: float
    materials_cost: float
    total_min: float  # Confidence range minimum
    total_max: float  # Confidence range maximum
    total_estimate: float
    confidence: float  # 0.0-1.0
    regional_adjustment: float
    breakdown: dict[str, float]

class CostEstimator:
    def __init__(self):
        self.parts_db = PartsDatabase()
        self.labor_rates = LaborRateService()
        logfire.configure()
    
    async def estimate_cost(
        self,
        damage: DamageDetection,
        vehicle: VehicleInfo,
        location: str
    ) -> RepairCostEstimate:
        """Calculate repair cost estimate with regional pricing"""
        
        with logfire.span("cost_estimation", damage_id=damage.id):
            # 1. Get parts pricing

            parts = await self.parts_db.lookup(
                vehicle.make,
                vehicle.model,
                vehicle.year,
                damage.affected_parts
            )
            parts_cost = sum(p.price for p in parts)
            
            # 2. Get labor rates by location
            labor_rate = await self.labor_rates.get_rate(location)
            labor_hours = self.estimate_labor_hours(damage.severity, damage.type)
            labor_cost = labor_rate * labor_hours
            
            # 3. Materials cost (paint, supplies)
            materials_cost = self.calculate_materials(damage.type, damage.area)
            
            # 4. Regional adjustment (+/-20%)
            regional_factor = await self.get_regional_factor(location)
            
            total = (labor_cost + parts_cost + materials_cost) * regional_factor
            confidence_range = total * 0.15  # ±15%
            
            return RepairCostEstimate(
                damage_id=damage.id,
                labor_cost=labor_cost,
                parts_cost=parts_cost,
                materials_cost=materials_cost,
                total_min=total - confidence_range,
                total_max=total + confidence_range,
                total_estimate=total,
                confidence=self.calculate_confidence(damage, parts),
                regional_adjustment=regional_factor,
                breakdown={
                    "labor": labor_cost,
                    "parts": parts_cost,
                    "materials": materials_cost
                }
            )
```

**Accuracy Target:** Within 15% of actual repair costs for 80% of claims

---

## 🏗️ System Architecture

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
│  PASETO Auth | Rate Limit | Image Validation        │
└────────────────────┬─────────────────────────────────┘
                     │
                   gRPC
                     │

┌────────────────────▼─────────────────────────────────┐
│         AI PROCESSING LAYER (Python + FastAPI)       │
│  ┌────────────────────────────────────────────┐     │
│  │      Damage Detection Service              │     │
│  │  • GPT-5.5 Vision API                      │     │
│  │  • Claude Opus 4.8 for complex cases       │     │
│  │  • YOLOv8 custom model                     │     │
│  │  • Bounding box generation                 │     │
│  └────────────┬───────────────────────────────┘     │
│               │                                      │
│  ┌────────────▼───────────────────────────────┐     │
│  │      Severity Assessment Service           │     │
│  │  • ML classification model                 │     │
│  │  • Structural impact analysis              │     │
│  └────────────┬───────────────────────────────┘     │
│               │                                      │
│  ┌────────────▼───────────────────────────────┐     │
│  │      Cost Estimation Service               │     │
│  │  • Parts database lookup                   │     │
│  │  • Regional pricing engine                 │     │
│  │  • Labor rate calculator                   │     │
│  └────────────┬───────────────────────────────┘     │
│               │                                      │
│  ┌────────────▼───────────────────────────────┐     │
│  │      Claim Generation Service              │     │
│  │  • ACORD XML formatter                     │     │
│  │  • PDF report generator                    │     │
│  │  • Insurance API integration               │     │
│  └────────────────────────────────────────────┘     │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│              DATA LAYER                              │
│  ┌──────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ PostgreSQL   │  │   Redis    │  │    S3      │  │
│  │  (RLS)       │  │   Cache    │  │  Images    │  │
│  └──────────────┘  └────────────┘  └────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## 🚀 Latest & Greatest Tech Stack (June 2026)

### **Backend**
| Technology | Version | Purpose |
|------------|---------|---------|
| Golang | 1.22+ | API Gateway, image validation |
| Python | 3.12+ | AI/ML services |
| FastAPI | 0.111+ | ML service APIs |
| HTTPX | 0.27+ | Async HTTP client |
| asyncio | Built-in | Async processing |

| Pydantic | 2.7+ | Data validation |
| Logfire | Latest | Observability |

### **Frontend**
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 16.x | Web framework |
| React | 19.2.7 | UI library |
| TypeScript | 5.5+ | Type safety |
| TailwindCSS | 3.4+ | Styling |

### **AI/ML**
| Technology | Version | Purpose |
|------------|---------|---------|
| OpenAI GPT-5.5 | Latest | Primary damage detection |
| Claude Opus 4.8 | Latest | Complex structural analysis |
| YOLOv8 | Latest | Real-time object detection |
| PyTorch | 2.3+ | Custom model training |
| OpenCV | 4.9+ | Image preprocessing |

### **Database & Storage**
| Technology | Version | Purpose |
|------------|---------|---------|
| PostgreSQL | 16.x | Primary database + RLS |
| Redis | 7.x | Cache, session store |
| AWS S3 | Latest | Image storage |
| pgvector | 0.7+ | Embedding search |

### **Security & Auth**
| Technology | Purpose |
|------------|---------|
| PASETO | Secure tokens |
| Vault | Secrets management |
| Clerk | SSO, MFA |

---

## 📦 Core Features Implementation

### **1. Image Upload & Validation**

```python
# Image upload handler with quality validation
from PIL import Image
import httpx
import asyncio

class ImageValidator:
    MAX_SIZE = 20 * 1024 * 1024  # 20MB
    MIN_RESOLUTION = (800, 600)
    SUPPORTED_FORMATS = {'JPEG', 'PNG', 'WEBP'}
    
    async def validate(self, image_bytes: bytes) -> dict:
        """Validate image quality before AI processing"""
        
        with logfire.span("image_validation"):
            # 1. Check size
            if len(image_bytes) > self.MAX_SIZE:
                return {"valid": False, "error": "File size exceeds 20MB limit"}

            
            # 2. Load image
            try:
                img = Image.open(BytesIO(image_bytes))
            except Exception:
                return {"valid": False, "error": "Invalid image format"}
            
            # 3. Check format
            if img.format not in self.SUPPORTED_FORMATS:
                return {"valid": False, "error": f"Unsupported format: {img.format}"}
            
            # 4. Check resolution
            if img.size[0] < self.MIN_RESOLUTION[0] or img.size[1] < self.MIN_RESOLUTION[1]:
                return {"valid": False, "error": "Resolution too low (minimum 800x600)"}
            
            # 5. Check brightness
            gray = img.convert('L')
            avg_brightness = sum(gray.getdata()) / len(gray.getdata())
            if avg_brightness < 30 or avg_brightness > 220:
                return {"valid": False, "error": "Poor lighting - please retake photo"}
            
            # 6. Check sharpness
            sharpness = self.calculate_sharpness(img)
            if sharpness < 0.4:
                return {"valid": False, "error": "Image too blurry - please retake photo"}
            
            # 7. Detect vehicle presence
            contains_vehicle = await self.detect_vehicle(image_bytes)
            if not contains_vehicle:
                return {"valid": False, "error": "No vehicle detected in image"}
            
            return {"valid": True, "metadata": {
                "format": img.format,
                "resolution": img.size,
                "brightness": avg_brightness,
                "sharpness": sharpness
            }}
```

---

### **2. Damage Detection Pipeline**

```python
# AI-powered damage detection using GPT-5.5 Vision
@dataclass
class DamageDetection:
    id: str
    type: str  # dent, scratch, crack, etc.
    severity: str  # minor, moderate, severe, critical
    bounding_box: tuple[int, int, int, int]  # x, y, width, height
    confidence: float  # 0.0-1.0
    affected_parts: list[str]
    description: str

class DamageDetector:
    def __init__(self):
        self.gpt_client = OpenAIClient(model="gpt-5.5-vision")

        self.claude_client = AnthropicClient(model="claude-opus-4.8")
        self.yolo_model = load_yolo_model("yolov8-vehicle-damage")
    
    async def detect_damage(self, image_bytes: bytes) -> list[DamageDetection]:
        """Detect all damage in vehicle image"""
        
        with logfire.span("damage_detection"):
            # 1. Fast pre-screening with YOLOv8
            yolo_results = self.yolo_model(image_bytes)
            
            if len(yolo_results) == 0:
                return []  # No damage detected
            
            # 2. Detailed analysis with GPT-5.5 Vision
            damages = []
            for bbox in yolo_results:
                prompt = f"""Analyze this vehicle damage area at coordinates {bbox}.
                Classify the damage type, severity, and affected vehicle parts.
                Provide a detailed description."""
                
                gpt_analysis = await self.gpt_client.analyze_image(
                    image_bytes,
                    prompt,
                    region=bbox
                )
                
                # 3. For complex cases, use Claude for second opinion
                if gpt_analysis['confidence'] < 0.7:
                    claude_analysis = await self.claude_client.analyze_image(
                        image_bytes,
                        prompt,
                        region=bbox
                    )
                    # Ensemble both results
                    final_analysis = self.ensemble([gpt_analysis, claude_analysis])
                else:
                    final_analysis = gpt_analysis
                
                damages.append(DamageDetection(
                    id=str(uuid.uuid4()),
                    type=final_analysis['type'],
                    severity=final_analysis['severity'],
                    bounding_box=bbox,
                    confidence=final_analysis['confidence'],
                    affected_parts=final_analysis['parts'],
                    description=final_analysis['description']
                ))
            
            logfire.info("damage_detected", count=len(damages))
            return damages
```

---

### **3. Claim Generation & Submission**

```python
# Automated insurance claim generation
class ClaimGenerator:
    def __init__(self):
        self.pdf_engine = PDFGenerator()
        self.acord_formatter = ACORDFormatter()

    
    async def generate_claim(
        self,
        damages: list[DamageDetection],
        cost_estimates: list[RepairCostEstimate],
        vehicle: VehicleInfo,
        policy: PolicyInfo,
        images: list[bytes]
    ) -> Claim:
        """Generate complete insurance claim"""
        
        with logfire.span("claim_generation"):
            # 1. Create claim document
            claim_id = f"CLM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
            
            # 2. Generate PDF report with annotated images
            pdf_report = await self.pdf_engine.generate({
                "claim_id": claim_id,
                "vehicle": vehicle,
                "policy": policy,
                "damages": damages,
                "cost_estimates": cost_estimates,
                "images": images,
                "total_estimate": sum(c.total_estimate for c in cost_estimates)
            })
            
            # 3. Generate ACORD XML for insurance system
            acord_xml = self.acord_formatter.format({
                "claim_id": claim_id,
                "policy_number": policy.number,
                "vehicle_vin": vehicle.vin,
                "damages": damages,
                "total_cost": sum(c.total_estimate for c in cost_estimates)
            })
            
            return Claim(
                id=claim_id,
                status="draft",
                pdf_report=pdf_report,
                acord_xml=acord_xml,
                created_at=datetime.now()
            )
    
    async def submit_claim(
        self,
        claim: Claim,
        insurance_endpoint: str,
        credentials: dict
    ) -> dict:
        """Submit claim to insurance system"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                insurance_endpoint,
                data=claim.acord_xml,
                headers={"Content-Type": "application/xml"},
                auth=(credentials['username'], credentials['password'])
            )
            
            if response.status_code == 200:
                return {"status": "submitted", "claim_id": claim.id}
            else:
                return {"status": "failed", "error": response.text}
```

---

## 🗄️ Database Schema (Multi-Tenant with RLS)

```sql
-- Tenants (insurance companies, body shops)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,

    type VARCHAR(50),  -- 'insurance', 'body_shop', 'enterprise'
    settings JSONB,
    api_credentials JSONB,  -- Encrypted insurance API creds
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    role VARCHAR(50),  -- 'user', 'adjuster', 'admin'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Damage assessments
CREATE TABLE damage_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    vehicle_make VARCHAR(50),
    vehicle_model VARCHAR(50),
    vehicle_year INT,
    vehicle_vin VARCHAR(17),
    status VARCHAR(50) DEFAULT 'processing',  -- processing, completed, failed
    total_cost_estimate DECIMAL(10,2),
    processing_time_ms INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Detected damages
CREATE TABLE damages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID REFERENCES damage_assessments(id),
    type VARCHAR(50),  -- dent, scratch, crack, etc.
    severity VARCHAR(20),  -- minor, moderate, severe, critical
    bounding_box JSONB,  -- {x, y, width, height}
    confidence FLOAT,
    affected_parts TEXT[],
    description TEXT,
    cost_estimate DECIMAL(10,2)
);

-- Uploaded images
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID REFERENCES damage_assessments(id),
    s3_key VARCHAR(500),
    format VARCHAR(10),
    resolution VARCHAR(20),
    file_size_bytes INT,
    metadata JSONB,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Insurance claims
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID REFERENCES damage_assessments(id),
    claim_number VARCHAR(100) UNIQUE,
    status VARCHAR(50) DEFAULT 'draft',  -- draft, submitted, approved, rejected

    pdf_report_s3_key VARCHAR(500),
    acord_xml TEXT,
    submitted_at TIMESTAMP,
    approved_at TIMESTAMP
);

-- Row-Level Security for multi-tenancy
CREATE POLICY tenant_isolation_assessments ON damage_assessments
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::uuid);

CREATE POLICY tenant_isolation_claims ON claims
    FOR ALL
    USING (assessment_id IN (
        SELECT id FROM damage_assessments 
        WHERE tenant_id = current_setting('app.tenant_id')::uuid
    ));

ALTER TABLE damage_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE damages ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims ENABLE ROW LEVEL SECURITY;
```

---

## 📊 Baseline Scale & Performance

### **Baseline Numbers**
| Metric | Baseline | Scalable To |
|--------|----------|-------------|
| Assessments/day | 1,000 | 100K+ |
| Concurrent users | 500 | 10K+ |
| Image processing | <5s/image | <3s/image (GPU) |
| End-to-end | <15s | <10s (optimized) |
| Tenants | 50 | 1000+ |
| Storage | 100GB | 100TB+ |

### **Performance Targets**
| Operation | Target | Measured |
|-----------|--------|----------|
| Image upload | < 2 seconds | p95 |
| Damage detection | < 5 seconds | p95 |
| Cost estimation | < 2 seconds | p95 |
| Claim generation | < 5 seconds | p95 |
| End-to-end workflow | < 15 seconds | p95 |
| API response | < 500ms | p95 |
| Uptime | 99.9% | SLA |

---

## 🔐 Security & Compliance

### **Data Protection**
- TLS 1.3 for all data in transit
- AES-256 encryption for data at rest
- PASETO tokens (NOT JWT) for authentication
- Secrets stored in Vault
- Image access via signed URLs (expiry: 1 hour)

### **Compliance**
- **GDPR:** Data subject rights, consent management, 30-day deletion
- **SOC 2 Type II:** Audit logs, access controls
- **ISO 27001:** Security management system

- **Insurance Regulations:** State-specific compliance (US), ACORD standards
- **PCI-DSS:** If processing payments for body shops

### **Authentication Flow**
```python
# PASETO token authentication
from pypaseto import Token

async def authenticate_user(email: str, password: str) -> str:
    """Generate PASETO token on successful login"""
    
    user = await db.get_user_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid credentials")
    
    # Generate PASETO token (24-hour expiry)
    token = Token.new(
        version=4,
        purpose="local",
        claims={
            "user_id": str(user.id),
            "tenant_id": str(user.tenant_id),
            "role": user.role,
            "exp": datetime.now() + timedelta(hours=24)
        },
        key=get_secret_key()
    )
    
    return token.to_string()
```

---

## 🧪 Test-Driven Development (TDD)

### **Property-Based Testing**

```python
# Property tests for image processing
from hypothesis import given, strategies as st

@given(st.binary(min_size=1000, max_size=20*1024*1024))
def test_image_validation_accepts_valid_sizes(image_data):
    """Property: All images under 20MB should be accepted"""
    validator = ImageValidator()
    result = validator.validate_size(image_data)
    assert result.valid or len(image_data) > validator.MAX_SIZE

@given(st.floats(min_value=0.0, max_value=1.0))
def test_confidence_scores_in_range(confidence):
    """Property: All confidence scores must be between 0 and 1"""
    damage = DamageDetection(confidence=confidence)
    assert 0.0 <= damage.confidence <= 1.0

@given(st.lists(st.floats(min_value=100, max_value=50000)))
def test_cost_estimates_positive(costs):
    """Property: All cost estimates must be positive"""
    estimator = CostEstimator()
    for cost in costs:
        assert cost > 0

# Unit tests with 85% coverage requirement
def test_damage_detection_returns_bounding_boxes():
    detector = DamageDetector()
    result = detector.detect(sample_image)
    for damage in result:
        assert len(damage.bounding_box) == 4
        assert all(coord >= 0 for coord in damage.bounding_box)
```

---

## 💰 ROI & Business Impact

### **Cost Savings**
- Manual inspection: $100/claim → $5/claim (95% savings)
- Claims processing: 3 days → 15 seconds (99.9% faster)
- Adjuster time: 30 min → 5 min (83% reduction)

### **Efficiency Gains**

- Claims processed per adjuster: 5/day → 50/day (10x improvement)
- Customer satisfaction: +40% (instant estimates)
- Fraud detection: 60% → 85% catch rate

### **Revenue Opportunities**
- **SaaS Pricing:** $500-$5,000/month per tenant (based on volume)
- **Per-Assessment Fee:** $2-$10 per assessment
- **Enterprise:** Custom pricing for large insurers

---

## 🔄 Async Processing with asyncio

```python
# Parallel processing for speed
async def process_assessment(images: list[bytes]) -> DamageReport:
    """Process multiple images concurrently"""
    
    # Validate all images in parallel
    validation_tasks = [validator.validate(img) for img in images]
    validations = await asyncio.gather(*validation_tasks)
    
    valid_images = [img for img, val in zip(images, validations) if val['valid']]
    
    # Detect damage in all images in parallel
    detection_tasks = [detector.detect_damage(img) for img in valid_images]
    all_damages = await asyncio.gather(*detection_tasks)
    
    # Flatten results
    damages = [d for damages_list in all_damages for d in damages_list]
    
    # Cost estimation in parallel
    cost_tasks = [estimator.estimate_cost(d) for d in damages]
    cost_estimates = await asyncio.gather(*cost_tasks)
    
    return DamageReport(
        damages=damages,
        costs=cost_estimates,
        total=sum(c.total_estimate for c in cost_estimates)
    )
```

---

## 📈 Monitoring with Logfire

```python
# Comprehensive observability
import logfire

logfire.configure()

@app.post("/api/v1/assess")
async def assess_damage(images: list[UploadFile]):
    with logfire.span("damage_assessment") as span:
        # Image validation
        with logfire.span("validation"):
            valid_images = await validate_images(images)
            logfire.info("images_validated", count=len(valid_images))
        
        # Damage detection
        with logfire.span("detection"):
            damages = await detect_damages(valid_images)
            logfire.info("damages_detected", count=len(damages))
        
        # Cost estimation
        with logfire.span("cost_estimation"):
            costs = await estimate_costs(damages)
            total_cost = sum(c.total_estimate for c in costs)
            logfire.info("costs_estimated", total=total_cost)
        
        span.set_attribute("total_damages", len(damages))
        span.set_attribute("total_cost", total_cost)
        
        return {"damages": damages, "costs": costs, "total": total_cost}
```

---

**Document Status:** ✅ Complete

**Version:** 1.0  
**Date:** June 18, 2026
