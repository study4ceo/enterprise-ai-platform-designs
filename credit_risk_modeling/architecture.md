# AI-Powered Credit Risk Modeling Platform - Architecture

**Date:** June 23, 2026  
**Version:** 1.0

---

## 1. System Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                          │
│   Web Dashboard (Next.js) | Mobile Apps | API Clients   │
└────────────────────┬─────────────────────────────────────┘
                     │
                HTTPS/REST
                     │
┌────────────────────▼─────────────────────────────────────┐
│            API GATEWAY (Golang + Fiber)                  │
│  PASETO Auth | Rate Limiting | Request Validation       │
└────────────────────┬─────────────────────────────────────┘
                     │
                   gRPC
                     │
┌────────────────────▼─────────────────────────────────────┐
│         BUSINESS SERVICES LAYER                          │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────┐ │
│  │ Credit Scoring │  │ Portfolio      │  │  Model    │ │
│  │ Engine         │  │ Monitor        │  │  Training │ │
│  │ (Python)       │  │ (Golang)       │  │  (Python) │ │
│  └────────────────┘  └────────────────┘  └───────────┘ │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│        DATA INTEGRATION PIPELINE (Python)                │
│  Credit Bureaus | Alternative Data | Bank APIs          │
└────────────────────┬─────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ PostgreSQL  │  │ TimescaleDB │  │   Redis     │
│  (Primary)  │  │(Time-Series)│  │  (Cache)    │
│   + RLS     │  │  Portfolio  │  │  Sessions   │
└─────────────┘  └─────────────┘  └─────────────┘
        │
        └───────────> S3/GCS (Model Artifacts, Reports)
```

---

## 2. Credit Assessment Pipeline Architecture

### **End-to-End Assessment Flow**

```python
class CreditAssessmentPipeline:
    """Complete credit assessment workflow with <1s latency"""
    
    async def execute(self, applicant_data: ApplicantData) -> AssessmentResult:
        """
        Pipeline stages:
        1. Data fetching (< 300ms)
        2. Feature engineering (< 100ms)
        3. Model ensemble prediction (< 400ms)
        4. Explainability generation (< 200ms)
        Total: < 1000ms (1 second)
        """
        
        start_time = time.time()
        
        # Stage 1: Parallel data fetching from multiple sources
        bureau_task = self.fetch_bureau_data(applicant_data.ssn)
        alt_data_task = self.fetch_alternative_data(applicant_data.id)
        bank_task = self.fetch_bank_data(applicant_data.id)
        
        bureau, alt_data, bank = await asyncio.gather(
            bureau_task, alt_data_task, bank_task,
            return_exceptions=True
        )
        
        # Stage 2: Feature engineering
        features = self.feature_engineer.transform(
            applicant=applicant_data,
            bureau=bureau,
            alt_data=alt_data,
            bank=bank
        )
        
        # Stage 3: Model ensemble (parallel predictions)
        xgb_task = self.models['xgboost'].predict_proba_async(features)
        lgb_task = self.models['lightgbm'].predict_proba_async(features)
        nn_task = self.models['neural_net'].predict_proba_async(features)
        
        predictions = await asyncio.gather(xgb_task, lgb_task, nn_task)
        
        # Weighted ensemble
        risk_score = self.ensemble_predictor.combine(
            predictions, weights={'xgboost': 0.4, 'lightgbm': 0.3, 'neural_net': 0.3}
        )
        
        # Stage 4: Generate explainability
        explanation = await self.explainability_engine.explain(
            features, risk_score
        )
        
        latency = (time.time() - start_time) * 1000  # Convert to ms
        
        return AssessmentResult(
            risk_score=risk_score,
            explanation=explanation,
            processing_time_ms=latency,
            model_versions=self.get_model_versions()
        )
```

---

## 3. Multi-Model Ensemble Architecture

### **Model Stack Configuration**

```python
class ModelEnsemble:
    """Ensemble of heterogeneous models for robust predictions"""
    
    def __init__(self):
        # Primary models (always executed)
        self.primary_models = {
            'xgboost': XGBoostModel(
                version='v2.1',
                max_depth=6,
                n_estimators=200,
                weight=0.40
            ),
            'lightgbm': LightGBMModel(
                version='v1.8',
                num_leaves=31,
                n_estimators=150,
                weight=0.30
            ),
            'neural_net': NeuralNetworkModel(
                version='v1.5',
                architecture='3-layer-MLP',
                weight=0.20
            )
        }
        
        # Fallback model (if primary fails)
        self.fallback_model = LogisticRegressionModel(
            version='v1.2',
            weight=0.10
        )
    
    async def predict(self, features: np.ndarray) -> RiskScore:
        """Execute ensemble prediction with fallback handling"""
        
        try:
            # Parallel predictions from all models
            predictions = await asyncio.gather(
                *[model.predict_proba(features) 
                  for model in self.primary_models.values()],
                return_exceptions=True
            )
            
            # Filter successful predictions
            valid_predictions = [
                (name, pred, model.weight)
                for name, pred, model in zip(
                    self.primary_models.keys(),
                    predictions,
                    self.primary_models.values()
                )
                if not isinstance(pred, Exception)
            ]
            
            # Re-normalize weights for valid predictions
            total_weight = sum(w for _, _, w in valid_predictions)
            weighted_prob = sum(
                pred * (w / total_weight)
                for _, pred, w in valid_predictions
            )
            
            # Convert to risk score (0-1000)
            risk_score = int(weighted_prob * 1000)
            
            return RiskScore(
                score=risk_score,
                default_probability=weighted_prob,
                confidence=self.calculate_confidence(valid_predictions),
                models_used=[name for name, _, _ in valid_predictions]
            )
            
        except Exception as e:
            logfire.error("ensemble_prediction_failed", error=str(e))
            # Use fallback model
            fallback_pred = self.fallback_model.predict_proba(features)
            return RiskScore(
                score=int(fallback_pred * 1000),
                default_probability=fallback_pred,
                confidence='low',
                models_used=['logistic_fallback']
            )
```

---

## 4. Data Integration Architecture

### **Multi-Source Data Fetching with Retry Logic**

```python
class DataIntegrationLayer:
    """Fetch and normalize data from multiple sources"""
    
    def __init__(self):
        self.bureaus = {
            'equifax': EquifaxClient(timeout=5.0),
            'experian': ExperianClient(timeout=5.0),
            'transunion': TransUnionClient(timeout=5.0)
        }
        
        self.alt_sources = {
            'plaid': PlaidClient(),  # Bank transactions
            'experian_boost': ExperianBoostClient(),  # Utility payments
            'renttrack': RentTrackClient()  # Rental history
        }
        
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
    async def fetch_bureau_data(self, ssn: str) -> CreditBureauData:
        """Fetch from all 3 bureaus with retry logic"""
        
        tasks = [
            self.circuit_breaker.call(
                self.bureaus[name].get_report, ssn
            )
            for name in ['equifax', 'experian', 'transunion']
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Normalize data from different bureau formats
        normalized = self.normalize_bureau_data(results)
        
        return normalized
```

---

## 5. Feature Engineering Pipeline

```python
class FeatureEngineer:
    """Transform raw data into ML-ready features"""
    
    def transform(self, applicant, bureau, alt_data, bank) -> pd.DataFrame:
        """Generate 150+ features for credit risk assessment"""
        
        features = {}
        
        # Credit bureau features (40 features)
        features.update(self.extract_bureau_features(bureau))
        
        # Alternative data features (30 features)
        features.update(self.extract_alternative_features(alt_data))
        
        # Bank transaction features (40 features)
        features.update(self.extract_bank_features(bank))
        
        # Applicant demographic features (20 features)
        features.update(self.extract_applicant_features(applicant))
        
        # Derived/engineered features (20 features)
        features.update(self.engineer_derived_features(features))
        
        return pd.DataFrame([features])
    
    def extract_bureau_features(self, bureau) -> dict:
        """Extract features from credit bureau data"""
        return {
            'credit_score': bureau.get('score', 0),
            'total_accounts': bureau.get('total_accounts', 0),
            'open_accounts': bureau.get('open_accounts', 0),
            'delinquent_accounts': bureau.get('delinquent_accounts', 0),
            'total_credit_limit': bureau.get('total_credit_limit', 0),
            'total_balance': bureau.get('total_balance', 0),
            'credit_utilization': self.calculate_utilization(bureau),
            'payment_history_score': bureau.get('payment_history_score', 0),
            'age_of_oldest_account_months': bureau.get('oldest_account_age', 0),
            'recent_inquiries_6m': bureau.get('inquiries_6m', 0),
            'bankruptcies': bureau.get('bankruptcies', 0),
            'collections': bureau.get('collections', 0),
            # ... 28 more bureau features
        }
```

---

## 6. SHAP Explainability Architecture

```python
import shap
from langchain_openai import ChatOpenAI

class ExplainabilityEngine:
    """Generate SHAP-based model explanations with GPT-5.5"""
    
    def __init__(self, scoring_engine):
        self.scoring_engine = scoring_engine
        self.explainer = shap.TreeExplainer(
            scoring_engine.models['xgboost']
        )
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        
        # FCRA-compliant feature names (no protected attributes)
        self.allowed_features = self.load_allowed_features()
    
    async def explain(self, features: pd.DataFrame, risk_score: RiskScore) -> Explanation:
        """Generate comprehensive explanation with SHAP + GPT-5.5"""
        
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(features)
        
        # Get top N features by absolute SHAP value
        feature_importance = self.get_feature_importance(
            shap_values, features, top_n=10
        )
        
        # Filter protected characteristics for FCRA compliance
        fcra_compliant_features = self.filter_protected_attributes(
            feature_importance
        )
        
        # Generate natural language explanation
        explanation_text = await self.generate_explanation(
            risk_score, fcra_compliant_features
        )
        
        # Generate adverse action codes if needed
        adverse_codes = None
        if risk_score.score < 620:  # Denial threshold
            adverse_codes = self.generate_adverse_action_codes(
                fcra_compliant_features
            )
        
        return Explanation(
            risk_score=risk_score,
            top_features=fcra_compliant_features,
            explanation_text=explanation_text,
            adverse_action_codes=adverse_codes,
            confidence_interval=(risk_score.score - 25, risk_score.score + 25)
        )
    
    async def generate_explanation(self, risk_score, features) -> str:
        """Use GPT-5.5 to generate consumer-friendly explanation"""
        
        prompt = f"""Generate a clear, consumer-friendly explanation for this credit decision:

Risk Score: {risk_score.score}/1000
Default Probability: {risk_score.default_probability:.2%}

Top Contributing Factors:
{self.format_features_for_prompt(features)}

Requirements:
1. Use simple, non-technical language
2. Explain what the score means
3. List the main factors affecting the score (positive and negative)
4. Suggest actions to improve the score
5. Be FCRA-compliant (suitable for adverse action notices)
6. Keep it under 200 words

Format as clear paragraphs."""

        response = await self.llm.ainvoke(prompt)
        return response.content
```

---

## 7. Caching Architecture

### **Multi-Layer Redis Caching Strategy**

```python
class CacheManager:
    """Intelligent caching for performance optimization"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        
        # Cache TTLs by data type
        self.ttls = {
            'bureau_data': 3600,  # 1 hour
            'model_prediction': 300,  # 5 minutes
            'parts_pricing': 3600,  # 1 hour  
            'labor_rates': 86400,  # 24 hours
            'features': 1800,  # 30 minutes
        }
    
    async def get_or_compute(
        self,
        key: str,
        compute_fn: Callable,
        cache_type: str,
        **kwargs
    ):
        """Get from cache or compute and store"""
        
        # Try cache first
        cached = await self.redis.get(key)
        if cached:
            logfire.info("cache_hit", key=key, type=cache_type)
            return json.loads(cached)
        
        # Cache miss - compute
        logfire.info("cache_miss", key=key, type=cache_type)
        result = await compute_fn(**kwargs)
        
        # Store in cache
        ttl = self.ttls.get(cache_type, 300)
        await self.redis.setex(key, ttl, json.dumps(result))
        
        return result
    
    def generate_cache_key(self, *args, **kwargs) -> str:
        """Generate deterministic cache key from inputs"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        key_string = ":".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
```

---

## 8. Multi-Tenant Row-Level Security

### **PostgreSQL RLS Implementation**

```sql
-- Enable RLS on all tenant tables
ALTER TABLE applicants ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE loans ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for tenant isolation
CREATE POLICY tenant_isolation_policy ON applicants
    USING (tenant_id = current_setting('app.current_tenant')::UUID);

CREATE POLICY tenant_isolation_policy ON credit_assessments
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

### **Tenant Context Middleware (Golang)**

```go
func TenantContextMiddleware(c *fiber.Ctx) error {
    // Extract tenant from PASETO token
    token := c.Get("Authorization")
    claims, err := ValidatePasetoToken(token)
    if err != nil {
        return c.Status(401).JSON(fiber.Map{"error": "unauthorized"})
    }
    
    tenantID := claims["tenant_id"].(string)
    
    // Set tenant context in request
    c.Locals("tenant_id", tenantID)
    
    // Set PostgreSQL session variable for RLS
    db.Exec("SET app.current_tenant = $1", tenantID)
    
    return c.Next()
}
```

---

## 9. Portfolio Risk Monitoring Architecture

```go
type PortfolioMonitor struct {
    db           *sql.DB
    tsdb         *timescaledb.Client
    alertService *AlertService
    riskEngine   *RiskCalculator
}

func (pm *PortfolioMonitor) CalculateRiskMetrics(
    ctx context.Context,
    tenantID string,
) (*PortfolioMetrics, error) {
    // Query active loans
    loans, err := pm.fetchActiveLoans(ctx, tenantID)
    if err != nil {
        return nil, err
    }
    
    // Calculate aggregate metrics
    metrics := &PortfolioMetrics{
        TenantID:      tenantID,
        TotalExposure: 0.0,
        TotalLoans:    len(loans),
    }
    
    var riskScores []float64
    for _, loan := range loans {
        metrics.TotalExposure += loan.OutstandingBalance
        metrics.AvgRiskScore += loan.RiskScore
        riskScores = append(riskScores, loan.RiskScore)
    }
    
    metrics.AvgRiskScore /= float64(len(loans))
    
    // Calculate portfolio-level default probability
    metrics.DefaultProbability = pm.riskEngine.CalculatePortfolioDefaultProb(
        riskScores,
    )
    
    // Detect risk concentration
    metrics.Concentration = pm.calculateRiskConcentration(loans)
    
    // Store time-series data
    pm.storeTimeSeriesMetrics(ctx, metrics)
    
    // Check alert thresholds
    pm.checkAlertThresholds(ctx, metrics)
    
    return metrics, nil
}
```

---

## 10. Model Training & Deployment Pipeline

```python
class ModelTrainingPipeline:
    """Automated model training and deployment"""
    
    def __init__(self):
        self.model_registry = ModelRegistry()
        self.min_auc_threshold = 0.70
        self.min_gini_threshold = 0.40
    
    async def train_and_deploy(self, model_type: str) -> TrainedModel:
        """Complete training pipeline"""
        
        # Step 1: Load training data (minimum 100K records)
        data = await self.load_training_data(min_records=100000)
        
        logfire.info("training_data_loaded", 
                     records=len(data), 
                     positives=data.labels.sum())
        
        # Step 2: Split data
        X_train, X_temp, y_train, y_temp = train_test_split(
            data.features, data.labels, 
            test_size=0.3, 
            stratify=data.labels,
            random_state=42
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, 
            test_size=0.5, 
            stratify=y_temp,
            random_state=42
        )
        
        # Step 3: Train model
        model = self.instantiate_model(model_type)
        model.fit(X_train, y_train)
        
        # Step 4: Validate performance
        y_pred_proba = model.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, y_pred_proba)
        gini = 2 * auc - 1
        
        logfire.info("model_trained", 
                     model_type=model_type, 
                     auc=auc, 
                     gini=gini)
        
        # Step 5: Reject if below threshold
        if auc < self.min_auc_threshold:
            raise ModelPerformanceException(
                f"AUC {auc:.3f} below threshold {self.min_auc_threshold}"
            )
        
        # Step 6: Test set evaluation
        test_metrics = self.evaluate_on_test(model, X_test, y_test)
        
        # Step 7: Save model version
        version = self.model_registry.get_next_version(model_type)
        artifact_path = self.save_model(model, version)
        
        # Step 8: Deploy with A/B test
        await self.deploy_with_ab_test(model, version, test_metrics)
        
        return TrainedModel(
            model_type=model_type,
            version=version,
            artifact_path=artifact_path,
            metrics={'auc': auc, 'gini': gini, **test_metrics}
        )
```

---

## 11. Circuit Breaker & Error Handling

```python
from circuitbreaker import circuit

class CreditBureauClient:
    """Client with circuit breaker for external API calls"""
    
    @circuit(failure_threshold=5, recovery_timeout=60, expected_exception=APIException)
    async def get_credit_report(self, ssn: str) -> dict:
        """Call credit bureau API with circuit breaker protection"""
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    self.api_url,
                    json={'ssn': ssn},
                    headers=self.get_auth_headers()
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logfire.error("bureau_timeout", bureau=self.name, ssn_hash=hash(ssn))
            raise APIException("Timeout calling credit bureau")
            
        except httpx.HTTPStatusError as e:
            logfire.error("bureau_http_error", 
                         bureau=self.name, 
                         status=e.response.status_code)
            raise APIException(f"HTTP {e.response.status_code}")
```

---

## 12. Database Connection Pooling

```python
import asyncpg

class DatabasePool:
    """PostgreSQL connection pool with optimal settings"""
    
    async def initialize(self):
        """Create connection pool"""
        
        self.pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=5432,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            
            # Pool settings
            min_size=10,      # Minimum connections
            max_size=50,      # Maximum connections
            max_queries=50000,  # Max queries per connection
            max_inactive_connection_lifetime=300,  # 5 minutes
            
            # Timeout settings
            command_timeout=60,  # Query timeout
            timeout=30,  # Connection timeout
            
            # Performance settings
            server_settings={
                'application_name': 'credit-risk-platform',
                'jit': 'off',  # Disable JIT for faster queries
            }
        )
    
    async def execute_with_tenant_context(
        self, 
        query: str, 
        tenant_id: str, 
        *args
    ):
        """Execute query with tenant RLS context"""
        
        async with self.pool.acquire() as conn:
            # Set tenant context
            await conn.execute(
                "SET app.current_tenant = $1", 
                tenant_id
            )
            
            # Execute query (RLS automatically applied)
            result = await conn.fetch(query, *args)
            
            return result
```

---

## 13. Observability & Monitoring

```python
import logfire

class ObservabilityManager:
    """Centralized observability with Logfire"""
    
    def __init__(self):
        logfire.configure(
            service_name="credit-risk-platform",
            environment="production"
        )
    
    @logfire.instrument("credit_assessment")
    async def assess_credit(self, applicant_data: ApplicantData):
        """Instrumented credit assessment with automatic tracing"""
        
        with logfire.span("data_fetching"):
            bureau_data = await self.fetch_bureau_data(applicant_data.ssn)
        
        with logfire.span("feature_engineering"):
            features = self.engineer_features(applicant_data, bureau_data)
        
        with logfire.span("model_prediction"):
            risk_score = await self.predict(features)
        
        with logfire.span("explainability"):
            explanation = await self.explain(features, risk_score)
        
        logfire.info("assessment_complete",
                     risk_score=risk_score.score,
                     confidence=risk_score.confidence)
        
        return AssessmentResult(risk_score, explanation)
```

---

## 14. Auto-Scaling Configuration

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: credit-scoring-engine-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: credit-scoring-engine
  minReplicas: 3
  maxReplicas: 15
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 85
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 60
```

---

## 15. Disaster Recovery & Backup

```python
class DisasterRecoveryManager:
    """Automated backup and recovery orchestration"""
    
    async def execute_backup(self, backup_type: str = "full"):
        """Execute database backup"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{backup_type}_{timestamp}.sql.gz"
        
        # PostgreSQL backup
        await execute_command(
            f"pg_dump -Fc {DB_NAME} | gzip > {backup_file}"
        )
        
        # Upload to S3 with versioning
        await s3_client.upload_file(
            backup_file,
            BACKUP_BUCKET,
            f"database/{backup_type}/{backup_file}"
        )
        
        # Store metadata
        await self.store_backup_metadata({
            'file': backup_file,
            'type': backup_type,
            'timestamp': datetime.now(),
            'size_mb': os.path.getsize(backup_file) / 1024 / 1024
        })
        
        logfire.info("backup_complete", 
                     type=backup_type, 
                     file=backup_file)
    
    async def point_in_time_recovery(self, target_time: datetime):
        """Restore database to specific point in time"""
        
        # Find closest backup before target time
        backup = await self.find_closest_backup(target_time)
        
        # Download from S3
        await s3_client.download_file(
            BACKUP_BUCKET,
            backup.s3_key,
            f"/tmp/{backup.filename}"
        )
        
        # Restore database
        await execute_command(
            f"pg_restore -d {DB_NAME} /tmp/{backup.filename}"
        )
        
        logfire.info("recovery_complete", target_time=target_time)
```

---

**Status:** ✅ Complete  
**Version:** 1.0  
**Date:** June 23, 2026
