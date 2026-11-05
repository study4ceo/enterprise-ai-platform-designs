# Customer Lifecycle Intelligence - Production ML Pipeline Plan

## Project Overview

**Goal:** Build an end-to-end production ML system for Customer Lifecycle Intelligence including CLV prediction, churn prediction, and buying propensity scoring.

**Tech Stack:**
- **Language:** Python 3.13+ (latest stable as of Nov 2026)
- **Data:** PostgreSQL + DuckDB (analytics), Redis (feature store)
- **ML:** scikit-learn, XGBoost, LightGBM, CatBoost
- **MLOps:** MLflow (experiment tracking & model registry)
- **API:** FastAPI
- **Orchestration:** Apache Airflow
- **Containerization:** Docker + Docker Compose
- **Monitoring:** Prometheus + Grafana
- **Tracing:** Jaeger (distributed tracing)
- **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana)
- **Cloud:** Multi-cloud support (AWS, GCP, Azure, IBM Cloud)
- **Testing:** pytest, Great Expectations

---

## Phase 1: Project Structure & Foundation

### Directory Structure
```
customer-lifecycle-ml-pipeline/
├── config/
│   ├── __init__.py
│   ├── config.yaml              # Main configuration
│   ├── features.yaml            # Feature definitions
│   ├── models.yaml              # Model configurations
│   └── data_quality.yaml        # Validation rules
│
├── data/
│   ├── raw/                     # Raw data dumps
│   ├── processed/               # Cleaned data
│   ├── features/                # Feature store snapshots
│   └── predictions/             # Model outputs
│
├── src/
│   ├── __init__.py
│   │
│   ├── data/                    # Data pipeline
│   │   ├── __init__.py
│   │   ├── connectors.py        # Database connections
│   │   ├── extractors.py        # Data extraction
│   │   ├── transformers.py      # Data transformation
│   │   └── validators.py        # Data quality checks
│   │
│   ├── features/                # Feature engineering
│   │   ├── __init__.py
│   │   ├── base.py              # Base feature class
│   │   ├── rfm_features.py      # RFM calculations
│   │   ├── behavioral_features.py
│   │   ├── temporal_features.py
│   │   └── feature_store.py     # Feature store interface
│   │
│   ├── models/                  # ML models
│   │   ├── __init__.py
│   │   ├── base_model.py        # Abstract base class
│   │   ├── clv_model.py         # CLV prediction
│   │   ├── churn_model.py       # Churn prediction
│   │   ├── propensity_model.py  # Buying propensity
│   │   └── ensemble.py          # Model ensembling
│   │
│   ├── training/                # Training pipeline
│   │   ├── __init__.py
│   │   ├── trainer.py           # Training orchestrator
│   │   ├── hyperparameter_tuning.py
│   │   ├── cross_validation.py
│   │   └── model_selection.py
│   │
│   ├── inference/               # Prediction service
│   │   ├── __init__.py
│   │   ├── predictor.py         # Prediction logic
│   │   ├── batch_scoring.py     # Batch predictions
│   │   └── online_scoring.py    # Real-time predictions
│   │
│   ├── evaluation/              # Model evaluation
│   │   ├── __init__.py
│   │   ├── metrics.py           # Custom metrics
│   │   ├── validation.py        # Model validation
│   │   └── reports.py           # Evaluation reports
│   │
│   ├── experimentation/         # A/B testing & causal inference
│   │   ├── __init__.py
│   │   ├── ab_testing.py        # A/B test framework
│   │   ├── sample_size.py       # Power analysis
│   │   ├── causal_inference.py  # DiD, PSM, etc.
│   │   └── incrementality.py    # Lift measurement
│   │
│   ├── monitoring/              # Model monitoring
│   │   ├── __init__.py
│   │   ├── data_drift.py        # Drift detection
│   │   ├── model_performance.py # Performance tracking
│   │   └── alerts.py            # Alerting system
│   │
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── logging_config.py
│       ├── database.py
│       └── helpers.py
│
├── api/                         # REST API
│   ├── __init__.py
│   ├── main.py                  # FastAPI app
│   ├── routes/
│   │   ├── predictions.py       # Prediction endpoints
│   │   ├── models.py            # Model management
│   │   └── health.py            # Health checks
│   ├── schemas.py               # Pydantic models
│   └── middleware.py
│
├── airflow/                     # Orchestration
│   ├── dags/
│   │   ├── data_pipeline_dag.py
│   │   ├── training_dag.py
│   │   ├── batch_prediction_dag.py
│   │   └── monitoring_dag.py
│   └── plugins/
│
├── notebooks/                   # Exploratory analysis
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_development.ipynb
│   └── 04_model_evaluation.ipynb
│
├── tests/                       # Testing
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.training
│   └── Dockerfile.airflow
│
├── scripts/
│   ├── setup_db.py
│   ├── generate_sample_data.py
│   ├── backfill_features.py
│   └── deploy_model.py
│
├── deployment/
│   ├── docker-compose.yml
│   ├── kubernetes/
│   └── terraform/
│
├── monitoring/
│   ├── prometheus.yml
│   ├── grafana/
│   │   └── dashboards/
│   └── alertmanager.yml
│
├── docs/
│   ├── architecture.md
│   ├── api_documentation.md
│   ├── model_cards/
│   └── runbooks/
│
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   ├── prod.txt
│   └── training.txt
│
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── Makefile
├── pyproject.toml
├── README.md
└── setup.py
```

---

## Phase 2: Data Pipeline Design

### 2.1 Data Sources
```yaml
sources:
  - name: transactional_db
    type: postgresql
    tables:
      - orders
      - customers
      - products
      - order_items
  
  - name: marketing_events
    type: s3
    path: s3://bucket/marketing_events/
    format: parquet
  
  - name: user_activity
    type: clickstream
    kafka_topic: user_events
```

### 2.2 Data Extraction Strategy
- **Full Load:** Initial historical data (1-2 years)
- **Incremental Load:** Daily/hourly new records
- **CDC (Change Data Capture):** Real-time updates for critical tables
- **Partitioning:** By date for efficient processing

### 2.3 Data Transformation Layers
```
Raw Layer → Cleaned Layer → Feature Layer → Model-Ready Layer
```

**Raw Layer:**
- As-is data from sources
- Timestamped ingestion
- Data lineage tracking

**Cleaned Layer:**
- Deduplication
- Type conversions
- NULL handling
- Outlier treatment
- Standardization

**Feature Layer:**
- Aggregated metrics
- Calculated features
- Time windows (7d, 30d, 90d, 365d)
- Feature versioning

**Model-Ready Layer:**
- Train/validation/test splits
- Feature scaling/encoding
- Target variable creation
- Snapshot management

### 2.4 Data Quality Framework
```python
# Example validation rules
quality_checks:
  - name: completeness
    columns: [customer_id, order_id, order_date]
    threshold: 0.95
  
  - name: uniqueness
    columns: [order_id]
    threshold: 1.0
  
  - name: timeliness
    max_delay_hours: 24
  
  - name: consistency
    rules:
      - order_date <= current_date
      - amount >= 0
      - status IN ('pending', 'completed', 'cancelled')
  
  - name: schema_validation
    enforce_schema: true
    allow_new_columns: false
```

---

## Phase 3: Feature Engineering Design

### 3.1 Feature Categories

#### A. RFM Features
```python
features:
  recency:
    - days_since_last_order
    - days_since_first_order
    - recency_score (1-5 quintile)
  
  frequency:
    - total_orders_lifetime
    - orders_last_30d
    - orders_last_90d
    - orders_last_365d
    - avg_days_between_orders
    - frequency_score (1-5 quintile)
  
  monetary:
    - total_spend_lifetime
    - spend_last_30d
    - spend_last_90d
    - spend_last_365d
    - avg_order_value
    - max_order_value
    - monetary_score (1-5 quintile)
```

#### B. Behavioral Features
```python
features:
  engagement:
    - login_frequency_30d
    - page_views_30d
    - time_on_site_avg
    - cart_abandonment_rate
    - wishlist_additions_30d
  
  product_affinity:
    - num_unique_categories_purchased
    - favorite_category
    - category_diversity_score
    - avg_products_per_order
  
  channel_preference:
    - mobile_vs_web_ratio
    - email_open_rate
    - sms_click_rate
    - preferred_channel
```

#### C. Temporal Features
```python
features:
  seasonality:
    - day_of_week_preference
    - hour_of_day_preference
    - month_of_year_trend
    - holiday_shopper_flag
  
  trends:
    - spend_trend_30d_vs_90d
    - order_frequency_trend
    - engagement_trend
    - declining_activity_flag
```

#### D. Lifecycle Features
```python
features:
  lifecycle_stage:
    - customer_age_days
    - lifecycle_stage (new, active, at_risk, dormant)
    - reactivation_count
    - churn_risk_score
  
  clv_components:
    - predicted_ltv
    - historical_value
    - value_percentile
```

### 3.2 Feature Store Design
```python
# Redis-based feature store
feature_store_schema:
  key: "customer:{customer_id}:features:{timestamp}"
  ttl: 7 days (for real-time), indefinite (for batch)
  
  value: {
    "customer_id": "C12345",
    "computed_at": "2026-11-01T10:00:00Z",
    "features": {
      "recency": 5,
      "frequency": 12,
      "monetary": 1250.50,
      "churn_risk": 0.15,
      # ... all features
    },
    "version": "v2.1"
  }
```

**Feature Store Operations:**
- **Write:** Batch updates (daily) + streaming updates (real-time)
- **Read:** Low-latency lookups for online scoring
- **Versioning:** Track feature schema versions
- **Backfill:** Historical feature reconstruction

---

## Phase 4: Model Development Design

### 4.1 Model Architecture

#### Model 1: Customer Lifetime Value (CLV)
```yaml
model: clv_predictor
type: regression
target: ltv_next_12_months

approaches:
  - baseline: historical_average
  
  - traditional:
      - buy_till_you_die (BG/NBD + Gamma-Gamma)
      - survival_analysis (Cox, Weibull AFT)
  
  - ml_models:
      - xgboost_regressor
      - lightgbm_regressor
      - random_forest_regressor
      - neural_network (tabular)
  
  - ensemble:
      - stacking (meta-learner)
      - weighted_average

evaluation_metrics:
  - mae (Mean Absolute Error)
  - rmse (Root Mean Squared Error)
  - mape (Mean Absolute Percentage Error)
  - r2_score
  - business_metric: revenue_prediction_accuracy

segmentation:
  - train separate models per customer_segment (high/medium/low value)
  - or include segment as feature
```

#### Model 2: Churn Prediction
```yaml
model: churn_predictor
type: binary_classification
target: churned_next_90_days

definition:
  churn: no order in 90 days (for non-contractual)

approaches:
  - logistic_regression (interpretable baseline)
  - xgboost_classifier
  - lightgbm_classifier
  - catboost_classifier
  - random_forest
  - ensemble

evaluation_metrics:
  - roc_auc (primary)
  - precision_at_k (top 10%, 20%)
  - recall_at_k
  - f1_score
  - lift_at_decile
  - business_metric: cost_benefit_analysis

class_imbalance_handling:
  - smote (Synthetic Minority Oversampling)
  - class_weight adjustment
  - threshold optimization
  - stratified sampling

output:
  - churn_probability (0-1)
  - churn_risk_tier (low/medium/high/critical)
  - recommended_action (retention strategy)
```

#### Model 3: Buying Propensity
```yaml
model: propensity_scorer
type: binary_classification
target: purchase_next_30_days

variants:
  - purchase_propensity (any product)
  - category_propensity (by category)
  - upsell_propensity (premium products)
  - cross_sell_propensity (complementary products)

approaches:
  - logistic_regression
  - xgboost_classifier
  - lightgbm_classifier
  - calibrated_models (for probability accuracy)

evaluation_metrics:
  - roc_auc
  - precision_recall_curve
  - brier_score (calibration)
  - log_loss
  - lift_charts
  - business_metric: campaign_roi

output:
  - propensity_score (0-1)
  - propensity_decile (1-10)
  - next_best_action
  - optimal_contact_time
```

### 4.2 Training Pipeline Design

```python
training_pipeline:
  
  1. data_preparation:
      - extract features from feature store
      - create train/val/test splits (70/15/15)
      - handle class imbalance
      - feature scaling/encoding
  
  2. baseline_model:
      - simple heuristic or logistic regression
      - establish baseline metrics
  
  3. model_training:
      - train multiple candidate models
      - hyperparameter tuning (Optuna/Hyperopt)
      - cross-validation (5-fold stratified)
      - early stopping
  
  4. model_selection:
      - compare models on validation set
      - select best based on primary metric
      - perform statistical significance tests
  
  5. ensemble_creation:
      - create stacked ensemble if beneficial
      - weighted averaging of top 3 models
  
  6. final_evaluation:
      - test set evaluation (never seen before)
      - business metric calculation
      - fairness checks (by segment)
      - explainability analysis (SHAP values)
  
  7. model_registration:
      - log to MLflow
      - create model card
      - version bump
      - tag production candidate
  
  8. staging_deployment:
      - deploy to staging environment
      - shadow mode testing
      - A/B test preparation
```

### 4.3 Hyperparameter Tuning Strategy
```python
# Optuna configuration
hyperparameter_spaces:
  
  xgboost:
    n_estimators: [100, 500, 1000]
    max_depth: [3, 5, 7, 10]
    learning_rate: [0.01, 0.05, 0.1, 0.3]
    subsample: [0.6, 0.8, 1.0]
    colsample_bytree: [0.6, 0.8, 1.0]
    min_child_weight: [1, 3, 5]
    gamma: [0, 0.1, 0.5]
  
  lightgbm:
    num_leaves: [31, 63, 127]
    learning_rate: [0.01, 0.05, 0.1]
    n_estimators: [100, 500, 1000]
    max_depth: [-1, 5, 10, 15]
    min_child_samples: [20, 50, 100]

optimization:
  trials: 100
  cv_folds: 5
  objective: maximize_roc_auc
  pruning: enabled (median pruner)
  parallel: 4 jobs
```

---

## Phase 5: Inference Design

### 5.1 Batch Scoring
```yaml
batch_prediction_pipeline:
  
  schedule: daily at 2 AM
  
  steps:
    1. extract_customer_list:
        - active customers
        - last 90 days activity
    
    2. fetch_features:
        - get from feature store
        - compute missing features
    
    3. load_models:
        - load from MLflow registry
        - version: production
    
    4. predict:
        - batch size: 10,000
        - parallel processing
    
    5. post_process:
        - apply business rules
        - assign risk tiers
        - generate recommendations
    
    6. store_predictions:
        - write to predictions table
        - update CRM system
        - trigger marketing automation
    
    7. generate_reports:
        - daily prediction summary
        - segment-wise statistics
        - alert on anomalies

output_schema:
  customer_id: str
  prediction_date: date
  churn_probability: float
  churn_risk_tier: str
  clv_prediction: float
  clv_confidence_interval: tuple
  propensity_score: float
  recommended_action: str
  model_version: str
```

### 5.2 Online/Real-Time Scoring
```yaml
online_prediction_api:
  
  endpoint: POST /api/v1/predictions/customer/{customer_id}
  
  flow:
    1. receive_request:
        - validate customer_id
        - check rate limits
    
    2. fetch_features:
        - try Redis cache (fast path)
        - fallback to DB (slow path)
        - compute on-demand if missing
    
    3. predict:
        - load model from memory (cached)
        - inference latency < 50ms
    
    4. return_response:
        - predictions
        - feature importance (top 5)
        - confidence scores
  
  response_schema:
    {
      "customer_id": "C12345",
      "timestamp": "2026-11-01T10:30:00Z",
      "predictions": {
        "churn": {
          "probability": 0.23,
          "risk_tier": "medium",
          "confidence": 0.85
        },
        "clv": {
          "value": 1250.50,
          "confidence_interval": [1100, 1400]
        },
        "propensity": {
          "score": 0.67,
          "decile": 7
        }
      },
      "top_features": [
        {"name": "recency", "importance": 0.25},
        {"name": "frequency", "importance": 0.18}
      ],
      "model_version": "v2.3.1"
    }
  
  performance_requirements:
    - p50_latency: < 50ms
    - p99_latency: < 200ms
    - throughput: 1000 req/s
    - availability: 99.9%
```

---

## Phase 6: Experimentation & Causal Inference

### 6.1 A/B Testing Framework
```yaml
ab_test_platform:
  
  components:
    - sample_size_calculator
    - random_assignment_service
    - data_collection_pipeline
    - statistical_analysis_engine
    - visualization_dashboard
  
  test_types:
    - conversion_optimization
    - retention_campaigns
    - pricing_experiments
    - feature_rollouts
  
  statistical_methods:
    - frequentist (z-test, t-test, chi-square)
    - bayesian (Thompson sampling, beta distributions)
    - sequential_testing (with alpha spending)
  
  workflow:
    1. design:
        - define hypothesis
        - choose primary/secondary metrics
        - calculate sample size
        - set test duration
    
    2. setup:
        - create experiment config
        - implement randomization
        - set up tracking
    
    3. run:
        - monitor data collection
        - check for SRM (Sample Ratio Mismatch)
        - interim analysis (if sequential)
    
    4. analyze:
        - statistical significance test
        - confidence intervals
        - segment analysis
        - guardrail checks
    
    5. decision:
        - ship, iterate, or kill
        - document learnings
```

### 6.2 Causal Inference Toolkit
```yaml
causal_methods:
  
  1. propensity_score_matching:
      use_case: marketing campaign impact
      steps:
        - estimate propensity scores
        - match treated to control
        - balance check (SMD < 0.1)
        - estimate treatment effect
  
  2. difference_in_differences:
      use_case: regional campaign rollout
      steps:
        - identify treatment/control groups
        - pre/post period data
        - parallel trends test
        - DiD estimation
  
  3. regression_discontinuity:
      use_case: loyalty tier impact
      steps:
        - identify cutoff (e.g., spending threshold)
        - local polynomial regression
        - continuity checks
        - estimate local ATE
  
  4. instrumental_variables:
      use_case: price sensitivity
      steps:
        - find valid instrument
        - 2SLS estimation
        - test instrument validity
  
  5. synthetic_control:
      use_case: market-level interventions
      steps:
        - construct synthetic control
        - validate pre-treatment fit
        - estimate causal effect
        - permutation tests

output:
  - treatment_effect
  - confidence_intervals
  - p_values
  - visualizations
  - assumptions_validation
```

### 6.3 Incrementality Testing
```yaml
incrementality_framework:
  
  goal: measure true incremental value of marketing
  
  designs:
    - holdout_tests (PSA - Public Service Announcement)
    - geo_experiments
    - randomized_controlled_trials
  
  metrics:
    - incremental_conversions
    - incremental_revenue
    - return_on_ad_spend (iROAS)
    - cost_per_incremental_conversion
  
  example_geo_test:
    treatment_markets: [NYC, LA, Chicago]
    control_markets: [Houston, Phoenix, Philadelphia]
    duration: 4 weeks
    pre_period: 8 weeks
    
    analysis:
      - check pre-treatment similarity
      - difference-in-differences
      - calculate lift
      - extrapolate to full market
```

---

## Phase 7: MLOps & Production

### 7.1 Model Registry & Versioning
```yaml
mlflow_setup:
  
  tracking_server:
    host: mlflow.company.com
    backend_store: postgresql://mlflow_db
    artifact_store: s3://mlflow-artifacts/
  
  model_registry:
    models:
      - name: churn_predictor
        versions: [v1.0, v2.0, v2.1]
        stages: [Staging, Production, Archived]
      
      - name: clv_predictor
        versions: [v1.5, v2.0]
        stages: [Staging, Production]
      
      - name: propensity_scorer
        versions: [v1.8, v2.2]
        stages: [Staging, Production]
  
  model_metadata:
    - training_data_version
    - feature_schema_version
    - hyperparameters
    - training_metrics
    - validation_metrics
    - test_metrics
    - training_duration
    - model_size
    - dependencies
    - business_owner
    - approved_by
    - deployment_date
```

### 7.2 CI/CD Pipeline
```yaml
ci_cd_workflow:
  
  on: [push, pull_request]
  
  stages:
    1. code_quality:
        - linting (flake8, black, mypy)
        - security scan (bandit)
        - dependency check
    
    2. testing:
        - unit tests (pytest)
        - integration tests
        - data validation tests
        - model quality tests
        - performance tests
        - coverage > 80%
    
    3. build:
        - build Docker images
        - tag with commit SHA
        - push to registry
    
    4. staging_deployment:
        - deploy to staging environment
        - run smoke tests
        - performance benchmarks
    
    5. production_deployment:
        - manual approval required
        - blue-green deployment
        - canary release (10% → 50% → 100%)
        - monitor key metrics
        - automatic rollback on errors
    
    6. post_deployment:
        - update documentation
        - notify stakeholders
        - create deployment ticket
```

### 7.3 Monitoring & Alerting

## Complete Observability Stack: Metrics + Logs + Traces

### The Three Pillars of Observability

```yaml
observability_stack:
  
  1. metrics (Prometheus + Grafana):
      - Time-series data
      - Aggregated system health
      - Alerting on thresholds
  
  2. logs (ELK Stack):
      - Elasticsearch: Storage & search
      - Logstash/Fluentd: Log aggregation
      - Kibana: Visualization
  
  3. traces (Jaeger):
      - Distributed tracing
      - Request flow tracking
      - Latency bottleneck identification
```

### 7.3.1 Jaeger - Distributed Tracing

**Why Jaeger for ML Pipelines:**
- Track requests across microservices (API → Feature Store → Model → DB)
- Identify latency bottlenecks in inference pipeline
- Debug production issues with full request context
- Monitor model prediction latency breakdown

**Implementation:**
```python
# Install
pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi
pip install opentelemetry-exporter-jaeger

# api/main.py - FastAPI with Jaeger tracing
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

# Setup Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

# Configure tracer
provider = TracerProvider()
processor = BatchSpanProcessor(jaeger_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Create FastAPI app
app = FastAPI(title="Customer Lifecycle ML API")

# Auto-instrument FastAPI
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()
RedisInstrumentor().instrument()

# Manual tracing for ML operations
tracer = trace.get_tracer(__name__)

@app.post("/predict/churn/{customer_id}")
async def predict_churn(customer_id: str):
    with tracer.start_as_current_span("predict_churn") as span:
        span.set_attribute("customer_id", customer_id)
        
        # Fetch features (auto-traced via RedisInstrumentor)
        with tracer.start_as_current_span("fetch_features"):
            features = await feature_store.get(customer_id)
            span.set_attribute("feature_count", len(features))
        
        # Model inference
        with tracer.start_as_current_span("model_inference") as model_span:
            model_span.set_attribute("model_version", model.version)
            prediction = model.predict(features)
            model_span.set_attribute("churn_probability", float(prediction))
        
        # Log prediction (auto-traced via DB instrumentation)
        with tracer.start_as_current_span("log_prediction"):
            await db.log_prediction(customer_id, prediction)
        
        return {"customer_id": customer_id, "churn_probability": prediction}
```

**Trace Visualization in Jaeger:**
```
Request: POST /predict/churn/C12345
│
├─ predict_churn (100ms total)
│  │
│  ├─ fetch_features (20ms)
│  │  ├─ redis_get (15ms)
│  │  └─ fallback_db_query (5ms)
│  │
│  ├─ model_inference (60ms)
│  │  ├─ feature_preprocessing (10ms)
│  │  ├─ xgboost_predict (45ms)
│  │  └─ postprocessing (5ms)
│  │
│  └─ log_prediction (20ms)
│     └─ postgres_insert (18ms)
```

**Key Traces to Monitor:**
- End-to-end prediction latency
- Feature store lookup time
- Model inference time
- Database write latency
- Cache hit/miss patterns

### 7.3.2 Metrics (Prometheus + Grafana)

```yaml
monitoring_stack:
  
  infrastructure:
    - prometheus (metrics collection)
    - grafana (dashboards)
    - alertmanager (alerts)
  
  metrics_to_track:
    
    model_performance:
      - prediction_accuracy (online evaluation)
      - auc_roc (if ground truth available)
      - precision_recall_at_k
      - calibration_score
      - prediction_distribution_shift
    
    data_quality:
      - feature_distribution_drift (KL divergence)
      - missing_value_rate
      - schema_violations
      - data_freshness
      - feature_correlation_changes
    
    system_metrics:
      - api_latency (p50, p95, p99)
      - throughput (requests/second)
      - error_rate
      - cpu_usage
      - memory_usage
      - disk_io
      - cache_hit_rate
    
    business_metrics:
      - prediction_adoption_rate
      - marketing_campaign_performance
      - revenue_impact
      - customer_retention_rate

# Custom Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# Counters
prediction_counter = Counter(
    'ml_predictions_total', 
    'Total predictions made',
    ['model_name', 'model_version']
)

error_counter = Counter(
    'ml_prediction_errors_total',
    'Total prediction errors',
    ['model_name', 'error_type']
)

# Histograms (for latency)
prediction_latency = Histogram(
    'ml_prediction_duration_seconds',
    'Prediction latency in seconds',
    ['model_name', 'percentile'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

# Gauges
model_accuracy = Gauge(
    'ml_model_accuracy',
    'Current model accuracy',
    ['model_name', 'model_version']
)

data_drift_score = Gauge(
    'ml_data_drift_score',
    'Data drift score (0-1)',
    ['feature_name']
)
```

### 7.3.3 Logging (ELK Stack)

```yaml
logging_stack:
  
  components:
    - filebeat: Log shipper (collect from containers)
    - logstash: Log processing & enrichment
    - elasticsearch: Storage & indexing
    - kibana: Visualization & search
  
  log_structure:
    timestamp: ISO8601
    level: DEBUG|INFO|WARNING|ERROR|CRITICAL
    service: api|training|batch_scoring
    trace_id: from Jaeger (correlation)
    span_id: from Jaeger
    message: log message
    context:
      customer_id: optional
      model_version: optional
      prediction: optional
      features: optional
      error: optional

# Structured logging with trace correlation
import logging
import json
from opentelemetry import trace

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def log(self, level, message, **kwargs):
        # Get current trace context
        span = trace.get_current_span()
        trace_id = span.get_span_context().trace_id
        span_id = span.get_span_context().span_id
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "service": "ml_api",
            "trace_id": format(trace_id, '032x') if trace_id else None,
            "span_id": format(span_id, '016x') if span_id else None,
            "message": message,
            **kwargs
        }
        
        self.logger.log(
            getattr(logging, level),
            json.dumps(log_entry)
        )

logger = StructuredLogger(__name__)

# Usage
logger.log("INFO", "Prediction made", 
    customer_id="C12345",
    model_version="v2.1",
    churn_probability=0.23,
    latency_ms=45
)
```

### 7.3.4 Unified Observability Dashboard

**Grafana Dashboard Panels:**
```yaml
dashboard_name: "ML Pipeline Observability"

rows:
  
  1. system_health:
      - API uptime (%)
      - Request rate (req/s)
      - Error rate (%)
      - P95/P99 latency
  
  2. model_performance:
      - Predictions per hour
      - Model accuracy trend
      - Churn risk distribution
      - CLV prediction distribution
  
  3. data_quality:
      - Feature drift alerts
      - Missing value rate
      - Schema violations
      - Data freshness (minutes)
  
  4. trace_metrics (from Jaeger):
      - Average request duration
      - Slowest endpoints (top 10)
      - Error traces (last 1 hour)
      - Service dependency graph
  
  5. business_metrics:
      - Marketing campaign ROI
      - Customer retention rate
      - Revenue impact ($)
      - Model adoption rate (%)
```

### 7.3.5 Alert Configuration
```yaml
monitoring_stack:
  
  infrastructure:
    - prometheus (metrics collection)
    - grafana (dashboards)
    - alertmanager (alerts)
    - ELK stack (logs)
  
  metrics_to_track:
    
    model_performance:
      - prediction_accuracy (online evaluation)
      - auc_roc (if ground truth available)
      - precision_recall_at_k
      - calibration_score
      - prediction_distribution_shift
    
    data_quality:
      - feature_distribution_drift (KL divergence)
      - missing_value_rate
      - schema_violations
      - data_freshness
      - feature_correlation_changes
    
    system_metrics:
      - api_latency (p50, p95, p99)
      - throughput (requests/second)
      - error_rate
      - cpu_usage
      - memory_usage
      - disk_io
    
    business_metrics:
      - prediction_adoption_rate
      - marketing_campaign_performance
      - revenue_impact
      - customer_retention_rate
  
  alerts:
    - model_performance_degradation:
        condition: auc_roc < 0.75
        severity: critical
        notify: ml_team, product_owner
        jaeger_trace: include last 100 failed predictions
    
    - data_drift_detected:
        condition: drift_score > 0.3
        severity: warning
        notify: ml_team
        kibana_logs: feature drift details
    
    - api_latency_high:
        condition: p99_latency > 500ms
        severity: critical
        notify: sre_team, ml_team
        jaeger_trace: slowest 10 traces
    
    - prediction_volume_anomaly:
        condition: predictions < 1000/hour
        severity: warning
        notify: ml_team
        logs: check error logs in Kibana
    
    - model_inference_slow:
        condition: model_inference_time > 100ms (from Jaeger span)
        severity: warning
        notify: ml_team
        action: investigate trace in Jaeger
    
    - feature_store_latency:
        condition: redis_get_time > 50ms (from Jaeger span)
        severity: warning
        notify: infra_team
        action: check Redis performance
```

### 7.3.6 Docker Compose - Complete Observability Stack

```yaml
# docker-compose.observability.yml
version: '3.8'

services:
  # Jaeger - Distributed Tracing
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "5775:5775/udp"   # zipkin.thrift compact
      - "6831:6831/udp"   # jaeger.thrift compact
      - "6832:6832/udp"   # jaeger.thrift binary
      - "5778:5778"       # serve configs
      - "16686:16686"     # UI
      - "14268:14268"     # jaeger.thrift HTTP
      - "14250:14250"     # gRPC
      - "9411:9411"       # zipkin compatible
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
      - COLLECTOR_OTLP_ENABLED=true
    networks:
      - ml-network

  # Prometheus - Metrics
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - ml-network

  # Grafana - Dashboards
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
      - jaeger
    networks:
      - ml-network

  # Elasticsearch - Log storage
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - ml-network

  # Kibana - Log visualization
  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - ml-network

  # Logstash - Log processing
  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    ports:
      - "5000:5000/tcp"
      - "5000:5000/udp"
      - "9600:9600"
    volumes:
      - ./monitoring/logstash/pipeline:/usr/share/logstash/pipeline
    environment:
      - "LS_JAVA_OPTS=-Xmx256m -Xms256m"
    depends_on:
      - elasticsearch
    networks:
      - ml-network

  # Alert Manager
  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
    networks:
      - ml-network

volumes:
  prometheus-data:
  grafana-data:
  elasticsearch-data:

networks:
  ml-network:
    driver: bridge
```

### 7.3.7 Benefits of Complete Observability

**Metrics (Prometheus/Grafana):**
- ✅ Aggregated system health
- ✅ Alerting on thresholds
- ✅ Historical trends
- ❌ Hard to debug specific requests

**Logs (ELK):**
- ✅ Detailed error messages
- ✅ Full context per event
- ✅ Searchable
- ❌ Hard to correlate across services

**Traces (Jaeger):**
- ✅ Request flow visualization
- ✅ Latency breakdown
- ✅ Service dependencies
- ✅ Root cause analysis
- ❌ No business context

**Together = Complete Picture:**
1. Alert fires in Prometheus (high latency)
2. Check Jaeger trace (which service is slow?)
3. View Kibana logs (what error occurred?)
4. Correlate via trace_id across all three!

### 7.3.8 Observability in Action - Debugging Scenario

```
Scenario: P99 latency spike from 50ms → 500ms

Step 1: Grafana Alert
  → "API P99 latency > 200ms for 5 minutes"

Step 2: Check Prometheus Metrics
  → Identify: model_inference_duration increased

Step 3: Open Jaeger UI
  → Filter: duration > 200ms, last 1 hour
  → Find trace: predict_churn request took 450ms
  → Breakdown:
     - fetch_features: 20ms ✓
     - model_inference: 400ms ✗ (normally 50ms)
     - log_prediction: 30ms ✓

Step 4: Kibana Logs (filtered by trace_id)
  → Find log: "Model inference timeout, retrying..."
  → Error: "XGBoost model loaded from disk (cache miss)"
  → Root cause: Redis cache expired, model reloading on every request

Step 5: Fix
  → Increase Redis TTL for model cache
  → Add model preloading on API startup
  → Deploy fix

Step 6: Verify in Jaeger
  → model_inference span back to 50ms
  → P99 latency back to normal
```

---
    - model_performance_degradation:
        condition: auc_roc < 0.75
        severity: critical
        notify: ml_team, product_owner
    
    - data_drift_detected:
        condition: drift_score > 0.3
        severity: warning
        notify: ml_team
    
    - api_latency_high:
        condition: p99_latency > 500ms
        severity: critical
        notify: sre_team, ml_team
    
    - prediction_volume_anomaly:
        condition: predictions < 1000/hour
        severity: warning
        notify: ml_team
```

---

## Phase 8: Deployment Architecture

### 8.0 Reliability & Disaster Recovery

#### 8.0.1 Idempotency Design

**Principle:** Operations can be repeated safely without side effects.

```python
# All operations must be idempotent at every layer

1. data_ingestion:
    # Problem: Running twice loads duplicate data
    # Solution: Upsert with unique keys
    
    INSERT INTO orders (order_id, customer_id, amount, ingested_at)
    VALUES (?, ?, ?, ?)
    ON CONFLICT (order_id) 
    DO UPDATE SET 
        amount = EXCLUDED.amount,
        ingested_at = EXCLUDED.ingested_at;

2. feature_computation:
    # Problem: Recomputing features creates duplicates
    # Solution: Versioned features with timestamps
    
    feature_key = f"customer:{customer_id}:features:{date}:v{version}"
    redis.set(feature_key, features, ex=7*24*3600)  # 7 day TTL
    
    # Always compute from source data, not incremental
    recency = (today - orders.max(order_date)).days  # Idempotent
    # NOT: recency = previous_recency + 1  # Not idempotent!

3. model_training:
    # Problem: Training twice with same params creates duplicate models
    # Solution: Check MLflow before training
    
    def train_model_idempotent(params, data_version):
        # Generate unique run ID from params + data
        run_id = hashlib.sha256(
            f"{params}_{data_version}".encode()
        ).hexdigest()[:16]
        
        # Check if already trained
        existing_run = mlflow.get_run(run_id)
        if existing_run and existing_run.status == "FINISHED":
            logger.info(f"Model already trained: {run_id}")
            return existing_run.info.run_id
        
        # Train new model
        with mlflow.start_run(run_id=run_id):
            model = train(params)
            mlflow.log_model(model, "model")
        
        return run_id

4. batch_predictions:
    # Problem: Predicting twice creates duplicate records
    # Solution: Upsert with (customer_id, prediction_date) key
    
    CREATE TABLE predictions (
        customer_id VARCHAR,
        prediction_date DATE,
        churn_probability FLOAT,
        clv_prediction FLOAT,
        model_version VARCHAR,
        predicted_at TIMESTAMP,
        PRIMARY KEY (customer_id, prediction_date)
    );
    
    # Upsert predictions
    INSERT INTO predictions VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT (customer_id, prediction_date)
    DO UPDATE SET
        churn_probability = EXCLUDED.churn_probability,
        clv_prediction = EXCLUDED.clv_prediction,
        model_version = EXCLUDED.model_version,
        predicted_at = EXCLUDED.predicted_at;

5. airflow_dags:
    # Built-in idempotency
    - Each task execution has unique task_instance_id
    - Retries don't duplicate data if tasks are idempotent
    - Can safely clear and re-run tasks

6. api_endpoints:
    # POST predictions with idempotency keys
    
    @app.post("/predict")
    async def predict(
        customer_id: str,
        idempotency_key: str = Header(None)
    ):
        # Check if already processed
        if idempotency_key:
            cached = await redis.get(f"prediction:{idempotency_key}")
            if cached:
                return json.loads(cached)
        
        # Make prediction
        result = model.predict(customer_id)
        
        # Cache result for 24 hours
        if idempotency_key:
            await redis.setex(
                f"prediction:{idempotency_key}",
                86400,  # 24 hours
                json.dumps(result)
            )
        
        return result
```

**Idempotency Checklist:**
- ✅ All database writes use UPSERT (INSERT ON CONFLICT)
- ✅ Feature computation is deterministic (no increments)
- ✅ Model training checks for existing runs
- ✅ Batch jobs can be re-run safely
- ✅ API endpoints support idempotency keys
- ✅ Airflow tasks are designed for retries

---

#### 8.0.2 RTO & RPO Requirements

**Definitions:**
- **RTO (Recovery Time Objective):** Maximum acceptable downtime
- **RPO (Recovery Point Objective):** Maximum acceptable data loss

```yaml
disaster_recovery_objectives:
  
  service_tier_1 (Critical - Real-time API):
    components:
      - prediction_api
      - feature_store (Redis)
    
    rto: 15 minutes
    rpo: 1 hour
    
    strategy:
      - active-active multi-region deployment
      - Redis replication (master-replica)
      - automated failover
      - health checks every 30 seconds
      - traffic routing via load balancer
    
    recovery_steps:
      1. Load balancer detects unhealthy region (30 sec)
      2. Traffic routes to healthy region (15 sec)
      3. Alert sent to on-call engineer (1 min)
      4. Manual verification (5 min)
      5. Total RTO: 6.5 minutes (within 15 min target)
  
  service_tier_2 (Important - Batch Predictions):
    components:
      - batch_scoring_pipeline
      - data_warehouse
      - mlflow_registry
    
    rto: 4 hours
    rpo: 24 hours
    
    strategy:
      - daily backups
      - automated pipeline restart
      - data stored in S3 (11 9s durability)
      - cross-region replication
    
    recovery_steps:
      1. Detect batch job failure (Airflow alert)
      2. Check last successful run timestamp
      3. Restore from S3 backup if needed (30 min)
      4. Re-run pipeline from last checkpoint (2 hours)
      5. Validate output data (30 min)
      6. Total RTO: 3 hours (within 4 hour target)
  
  service_tier_3 (Standard - Model Training):
    components:
      - training_pipeline
      - experiment_tracking
    
    rto: 24 hours
    rpo: 7 days
    
    strategy:
      - weekly backups
      - training data in S3
      - models versioned in MLflow
      - can retrain from scratch if needed
    
    recovery_steps:
      1. Identify training data backup (1 hour)
      2. Provision training infrastructure (2 hours)
      3. Re-run training pipeline (12 hours)
      4. Validation and deployment (4 hours)
      5. Total RTO: 19 hours (within 24 hour target)
```

---

#### 8.0.3 Backup & Recovery Strategy

```yaml
backup_strategy:
  
  1. databases (PostgreSQL):
      frequency: 
        - full backup: daily at 2 AM UTC
        - incremental: every 4 hours
        - WAL archiving: continuous
      
      retention:
        - daily backups: 30 days
        - weekly backups: 90 days
        - monthly backups: 1 year
      
      storage: S3 Standard → Glacier after 90 days
      
      recovery_procedures:
        - point_in_time_recovery: last 30 days
        - cross_region_restore: replicated to us-west-2
      
      testing: monthly restore drills
      
      automation:
        ```bash
        # Automated backup script
        #!/bin/bash
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="postgres_backup_${TIMESTAMP}.sql.gz"
        
        # Dump with compression
        pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE
        
        # Upload to S3 with encryption
        aws s3 cp $BACKUP_FILE \
          s3://ml-pipeline-backups/postgres/ \
          --server-side-encryption AES256 \
          --storage-class STANDARD_IA
        
        # Cleanup local file
        rm $BACKUP_FILE
        
        # Prune old backups (>30 days)
        aws s3 ls s3://ml-pipeline-backups/postgres/ | \
          awk '{print $4}' | \
          xargs -I {} bash -c \
            'if [[ $(date -d "30 days ago" +%s) -gt $(date -d {} +%s) ]]; then
              aws s3 rm s3://ml-pipeline-backups/postgres/{}
            fi'
        ```
  
  2. feature_store (Redis):
      frequency:
        - RDB snapshot: every 6 hours
        - AOF (Append Only File): every second
      
      retention:
        - snapshots: 7 days
      
      storage: S3 + local disk
      
      recovery:
        - restore from latest RDB + replay AOF
        - recompute features if corruption detected
      
      replication:
        - master-replica setup
        - automatic failover with Sentinel
  
  3. ml_models (MLflow):
      frequency: continuous (every model training)
      
      storage:
        - artifacts: S3 (versioned bucket)
        - metadata: PostgreSQL (backed up with DB)
      
      versioning: 
        - all models kept indefinitely
        - can rollback to any version
      
      recovery:
        - restore model from S3 by version
        - redeploy via MLflow API
  
  4. data_lake (S3):
      versioning: enabled on all buckets
      
      replication:
        - cross_region: us-east-1 → us-west-2
        - lifecycle_policy:
            - Standard: 0-30 days
            - Standard-IA: 30-90 days  
            - Glacier: 90-365 days
            - Deep Archive: >365 days
      
      recovery:
        - point_in_time: restore any version
        - cross_region: failover to us-west-2
  
  5. configuration (Git):
      repository: GitHub (Enterprise)
      
      backup:
        - GitHub automatic backups
        - manual export: weekly
      
      recovery:
        - clone from GitHub
        - restore from weekly export
  
  6. logs_and_metrics:
      storage:
        - Elasticsearch: 30 days hot
        - S3: archive after 30 days, keep 1 year
        - Prometheus: 90 days
      
      recovery:
        - restore from S3 if needed
        - not critical (can rebuild from source)
```

---

#### 8.0.4 Disaster Recovery Scenarios

```yaml
disaster_scenarios:
  
  1. region_outage (AWS region failure):
      impact: All services in us-east-1 unavailable
      
      recovery_plan:
        - auto_failover: Load balancer → us-west-2 (5 min)
        - dns_update: Route53 health check failover (2 min)
        - database: Read from cross-region replica (immediate)
        - models: Serve from S3 in us-west-2 (immediate)
        - feature_store: Promote replica to master (2 min)
        - rto_achieved: 10 minutes
      
      data_loss: 
        - predictions: up to 1 hour (RPO)
        - training_data: 0 (S3 replicated)
  
  2. database_corruption:
      impact: PostgreSQL data corrupted
      
      recovery_plan:
        1. stop_writes: prevent further corruption (1 min)
        2. assess_damage: check backup timestamps (5 min)
        3. restore: point-in-time recovery (30 min)
        4. validate: data integrity checks (15 min)
        5. resume_services: bring API back online (5 min)
        total: 56 minutes (within 4 hour RTO)
      
      data_loss:
        - up to last backup interval (4 hours)
        - WAL replay minimizes to minutes
  
  3. model_performance_degradation:
      impact: Model accuracy drops below threshold
      
      recovery_plan:
        1. detect: monitoring alert (5 min)
        2. diagnose: check data drift (10 min)
        3. rollback: deploy previous model version (5 min)
        4. investigate: root cause analysis (parallel)
        5. retrain: trigger emergency retraining (4 hours)
        total: 20 minutes to rollback, 4 hours to fix
      
      business_impact: minimized by quick rollback
  
  4. ransomware_attack:
      impact: Production systems encrypted
      
      recovery_plan:
        1. isolate: disconnect affected systems (10 min)
        2. assess: identify encrypted resources (30 min)
        3. restore: from immutable S3 backups (2 hours)
        4. rebuild: fresh infrastructure (4 hours)
        5. validate: security scan + testing (2 hours)
        total: 8.5 hours
      
      protection:
        - immutable S3 backups (object lock)
        - MFA delete protection
        - separate backup account
        - no programmatic delete access
  
  5. data_pipeline_failure:
      impact: No new data ingested for 12 hours
      
      recovery_plan:
        1. detect: Airflow alert (immediate)
        2. check_upstream: verify source systems (10 min)
        3. backfill: re-run pipeline for missing hours (2 hours)
        4. validate: data quality checks (30 min)
        total: 2.5 hours
      
      data_loss: 0 (can backfill from source)
  
  6. feature_store_failure:
      impact: Real-time predictions unavailable
      
      recovery_plan:
        1. detect: API health check (30 sec)
        2. failover: promote Redis replica (1 min)
        3. fallback: compute features on-demand from DB (immediate)
        4. restore: repair master Redis (30 min, parallel)
        total: 1.5 minutes to serve predictions (degraded)
      
      degraded_mode:
        - predictions work but slower (200ms → 500ms)
        - acceptable for RTO
```

---

#### 8.0.5 High Availability Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     LOAD BALANCER (Multi-AZ)                │
│                  Health Checks Every 30 Sec                 │
└──────────────┬──────────────────────────┬───────────────────┘
               │                          │
    ┌──────────▼────────┐      ┌─────────▼─────────┐
    │   REGION 1        │      │   REGION 2        │
    │   us-east-1       │      │   us-west-2       │
    │   (Primary)       │      │   (Standby)       │
    └───────────────────┘      └───────────────────┘
               │                          │
    ┌──────────▼────────┐      ┌─────────▼─────────┐
    │  API Cluster      │      │  API Cluster      │
    │  - Auto-scaling   │      │  - Auto-scaling   │
    │  - Min 2 nodes    │      │  - Min 1 node     │
    └──────────┬────────┘      └─────────┬─────────┘
               │                          │
    ┌──────────▼────────┐      ┌─────────▼─────────┐
    │  Redis Cluster    │◄────►│  Redis Replica    │
    │  - Master         │ Sync │  - Read-only      │
    │  - Sentinel HA    │      │  - Auto-promote   │
    └──────────┬────────┘      └─────────┬─────────┘
               │                          │
    ┌──────────▼────────┐      ┌─────────▼─────────┐
    │  PostgreSQL       │◄────►│  PostgreSQL       │
    │  - Master         │ WAL  │  - Standby        │
    │  - Streaming Rep  │      │  - Hot standby    │
    └──────────┬────────┘      └─────────┬─────────┘
               │                          │
               └──────────┬───────────────┘
                          │
                   ┌──────▼──────┐
                   │  S3 Bucket  │
                   │  - Versioned│
                   │  - Replicated│
                   └─────────────┘
```

**Redundancy at Every Layer:**
- Load Balancer: Multi-AZ (AWS ALB)
- API: Multiple instances per region
- Redis: Master-Replica with Sentinel
- PostgreSQL: Streaming replication
- S3: Cross-region replication
- Models: Multi-region artifact storage

---

#### 8.0.6 Recovery Testing Schedule

```yaml
testing_schedule:
  
  monthly:
    - database_restore_drill:
        - restore from latest backup
        - validate data integrity
        - measure recovery time
        - document any issues
    
    - failover_test:
        - simulate region outage
        - verify automatic failover
        - check RTO/RPO compliance
        - update runbooks
  
  quarterly:
    - full_disaster_recovery:
        - complete region failover
        - restore all services
        - end-to-end testing
        - measure actual RTO/RPO
    
    - chaos_engineering:
        - random service failures
        - network partitions
        - latency injection
        - verify system resilience
  
  annually:
    - tabletop_exercise:
        - simulate major incidents
        - team coordination practice
        - update incident response plans
        - train new team members
    
    - compliance_audit:
        - verify backup integrity
        - test restore procedures
        - document compliance
        - external audit if required
```

---

#### 8.0.7 Monitoring for Reliability

```python
# Reliability metrics to track

reliability_metrics:
  
  availability:
    - uptime_percentage: 99.9% SLA (8.76 hours downtime/year)
    - mtbf (Mean Time Between Failures): > 30 days
    - mttr (Mean Time To Recovery): < 15 minutes
  
  backup_health:
    - backup_success_rate: 100%
    - backup_size_trend: monitor growth
    - backup_duration: < 30 minutes
    - restore_test_success: 100%
  
  replication_lag:
    - redis_replication_lag: < 1 second
    - postgres_replication_lag: < 10 seconds
    - s3_replication_lag: < 15 minutes
  
  alerts:
    - backup_failed (critical)
    - replication_lag_high (warning)
    - failover_triggered (critical)
    - rto_exceeded (critical)
    - restore_test_failed (critical)
```

---

### 8.1 System Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                             │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL  │  S3 (Parquet)  │  Kafka (Events)  │  APIs        │
└────────┬─────────────┬─────────────┬───────────────┬─────────────┘
         │             │             │               │
         └─────────────┴─────────────┴───────────────┘
                           │
         ┌─────────────────▼──────────────────┐
         │     APACHE AIRFLOW (Orchestration) │
         │  - Data Pipeline DAG               │
         │  - Training DAG                    │
         │  - Batch Prediction DAG            │
         └─────────────┬──────────────────────┘
                       │
         ┌─────────────▼──────────────────┐
         │      DATA LAKE / WAREHOUSE     │
         │    (DuckDB + S3 / PostgreSQL)  │
         └─────────────┬──────────────────┘
                       │
         ┌─────────────▼──────────────────┐
         │   FEATURE ENGINEERING PIPELINE │
         └─────────────┬──────────────────┘
                       │
         ┌─────────────▼──────────────────┐
         │      FEATURE STORE (Redis)     │
         │  - Real-time features          │
         │  - Batch features              │
         └────────┬────────────┬──────────┘
                  │            │
     ┌────────────▼────┐  ┌───▼──────────────────┐
     │ TRAINING        │  │  INFERENCE           │
     │ PIPELINE        │  │  SERVICE             │
     │ - Model Train   │  │  - Batch Scoring     │
     │ - HPO           │  │  - Online API        │
     │ - Evaluation    │  │                      │
     └────────┬────────┘  └───┬──────────────────┘
              │               │
     ┌────────▼───────────────▼──────┐
     │     MLflow (Registry)         │
     │   - Model Versioning          │
     │   - Experiment Tracking       │
     └────────┬──────────────────────┘
              │
     ┌────────▼──────────────────────┐
     │   PREDICTION SERVICE (FastAPI)│
     │   - REST API                  │
     │   - Load Balancer             │
     │   - Rate Limiting             │
     └────────┬──────────────────────┘
              │
     ┌────────▼──────────────────────┐
     │   MONITORING & ALERTING       │
     │   - Prometheus + Grafana      │
     │   - Data Drift Detection      │
     │   - Model Performance         │
     └───────────────────────────────┘
```

### 8.2 Deployment Options

#### Option A: Docker Compose (Development/Small Scale)
```yaml
services:
  - postgres (data warehouse)
  - redis (feature store)
  - mlflow (tracking + registry)
  - airflow (orchestration)
  - api (FastAPI prediction service)
  - prometheus (monitoring)
  - grafana (dashboards)
```

#### Option B: Kubernetes (Production/Large Scale)
```yaml
deployments:
  - api-deployment (replicas: 3, autoscaling)
  - training-job (CronJob)
  - batch-scoring-job (CronJob)
  - feature-pipeline (CronJob)
  - monitoring-stack

services:
  - api-service (LoadBalancer)
  - mlflow-service
  - redis-cluster
  - postgres-cluster
```

#### Option C: Multi-Cloud Deployment Strategy

**Cloud-Agnostic Design Principles:**
- Use containerization (Docker/Kubernetes) for portability
- Abstract cloud services behind interfaces
- Store data in cloud-agnostic formats (Parquet, Delta Lake)
- Use Terraform for infrastructure as code
- Implement multi-cloud monitoring

---

## Phase 8.4: Multi-Cloud Architecture

### Cloud Service Mapping

```yaml
service_comparison:
  
  object_storage:
    aws: S3
    gcp: Cloud Storage (GCS)
    azure: Blob Storage
    ibm: Cloud Object Storage
    abstraction: Use fsspec or boto3-compatible libraries
  
  data_warehouse:
    aws: Redshift, RDS PostgreSQL, Athena
    gcp: BigQuery, Cloud SQL
    azure: Synapse Analytics, Azure SQL
    ibm: Db2 Warehouse on Cloud
    recommendation: Self-hosted PostgreSQL + DuckDB (portable)
  
  ml_platform:
    aws: SageMaker
    gcp: Vertex AI
    azure: Azure ML
    ibm: Watson Studio
    recommendation: MLflow (open-source, portable)
  
  container_orchestration:
    aws: EKS (Elastic Kubernetes Service)
    gcp: GKE (Google Kubernetes Engine)
    azure: AKS (Azure Kubernetes Service)
    ibm: IKS (IBM Kubernetes Service)
    recommendation: Kubernetes (standard across all)
  
  api_hosting:
    aws: ECS/Fargate, Lambda, EC2
    gcp: Cloud Run, Cloud Functions, GCE
    azure: Container Instances, Functions, VMs
    ibm: Code Engine, Cloud Functions, VMs
    recommendation: Kubernetes + FastAPI (portable)
  
  redis_cache:
    aws: ElastiCache for Redis
    gcp: Memorystore for Redis
    azure: Azure Cache for Redis
    ibm: IBM Cloud Databases for Redis
    recommendation: Self-hosted Redis on Kubernetes (portable)
  
  monitoring:
    aws: CloudWatch
    gcp: Cloud Monitoring
    azure: Azure Monitor
    ibm: IBM Cloud Monitoring
    recommendation: Prometheus + Grafana (cloud-agnostic)
  
  secrets_management:
    aws: Secrets Manager, Parameter Store
    gcp: Secret Manager
    azure: Key Vault
    ibm: Secrets Manager
    recommendation: HashiCorp Vault or Kubernetes Secrets
```

---

### Deployment Option C1: AWS (Amazon Web Services)

```yaml
aws_architecture:
  
  compute:
    - EKS: Kubernetes cluster for API and batch jobs
    - Lambda: Serverless functions for lightweight tasks
    - EC2: Training instances (GPU p3/p4 for deep learning)
  
  storage:
    - S3: Data lake (raw, processed, models, backups)
    - EBS: Persistent volumes for databases
    - EFS: Shared file system for distributed training
  
  database:
    - RDS PostgreSQL: Transactional data, MLflow backend
    - ElastiCache Redis: Feature store, caching
    - Athena: Ad-hoc SQL queries on S3
  
  ml_services:
    - SageMaker: Optional managed training/deployment
    - SageMaker Feature Store: Optional managed feature store
    - SageMaker Pipelines: Optional ML workflow orchestration
    - Bedrock: Foundation models (Claude, Llama, etc.)
    - Bedrock Agents: Agentic AI orchestration with actions
    - Bedrock Knowledge Bases: RAG for ML documentation
  
  networking:
    - VPC: Isolated network
    - ALB: Application Load Balancer
    - Route53: DNS and health checks
    - CloudFront: CDN for API endpoints (optional)
  
  orchestration:
    - Managed Workflows for Apache Airflow (MWAA)
    - Or self-hosted Airflow on EKS
  
  monitoring:
    - CloudWatch: Logs and basic metrics
    - X-Ray: Distributed tracing (alternative to Jaeger)
    - Prometheus on EKS + Grafana
  
  security:
    - IAM: Identity and access management
    - KMS: Encryption key management
    - Secrets Manager: API keys, DB credentials
    - WAF: Web application firewall

# Terraform example
resource "aws_eks_cluster" "ml_pipeline" {
  name     = "customer-lifecycle-ml"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.28"

  vpc_config {
    subnet_ids = aws_subnet.private[*].id
  }
}

resource "aws_s3_bucket" "data_lake" {
  bucket = "ml-pipeline-data-lake"
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    enabled = true
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

---

### Deployment Option C2: GCP (Google Cloud Platform)

```yaml
gcp_architecture:
  
  compute:
    - GKE: Kubernetes cluster (Autopilot mode recommended)
    - Cloud Run: Serverless containers for API
    - Cloud Functions: Event-driven functions
    - Vertex AI Workbench: Managed Jupyter notebooks
  
  storage:
    - Cloud Storage: Data lake (Standard/Nearline/Coldline)
    - Persistent Disk: Database volumes
    - Filestore: NFS for distributed workloads
  
  database:
    - Cloud SQL PostgreSQL: Transactional data
    - Memorystore Redis: Feature store, caching
    - BigQuery: Data warehouse for analytics
  
  ml_services:
    - Vertex AI: Managed ML platform
    - Vertex AI Feature Store: Managed feature store
    - Vertex AI Pipelines: Kubeflow-based orchestration
    - AutoML: Automated model training
  
  networking:
    - VPC: Network isolation
    - Cloud Load Balancing: Global load balancer
    - Cloud CDN: Content delivery
    - Cloud Armor: DDoS protection
  
  orchestration:
    - Cloud Composer: Managed Apache Airflow
    - Or self-hosted on GKE
  
  monitoring:
    - Cloud Logging: Centralized logs
    - Cloud Monitoring: Metrics and dashboards
    - Cloud Trace: Distributed tracing
    - Cloud Profiler: Performance profiling
  
  security:
    - IAM: Access control
    - Cloud KMS: Key management
    - Secret Manager: Secrets storage
    - Binary Authorization: Container security

# Terraform example
resource "google_container_cluster" "ml_pipeline" {
  name     = "customer-lifecycle-ml"
  location = "us-central1"
  
  enable_autopilot = true  # Fully managed
  
  release_channel {
    channel = "STABLE"
  }
}

resource "google_storage_bucket" "data_lake" {
  name     = "ml-pipeline-data-lake"
  location = "US"
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 90
    }
  }
}

---

### Deployment Option C3: Azure (Microsoft Azure)

```yaml
azure_architecture:
  
  compute:
    - AKS: Azure Kubernetes Service
    - Container Instances: Serverless containers
    - Functions: Serverless functions
    - Virtual Machines: Custom compute (GPU NV/NC series)
  
  storage:
    - Blob Storage: Data lake (Hot/Cool/Archive tiers)
    - Managed Disks: VM storage
    - Azure Files: SMB file shares
  
  database:
    - Azure Database for PostgreSQL: Managed PostgreSQL
    - Azure Cache for Redis: Managed Redis
    - Azure Synapse Analytics: Data warehouse
  
  ml_services:
    - Azure Machine Learning: End-to-end ML platform
    - Azure ML Feature Store: Managed features
    - Azure ML Pipelines: Workflow orchestration
    - Azure Databricks: Spark-based ML
  
  networking:
    - Virtual Network (VNet): Network isolation
    - Application Gateway: Load balancer + WAF
    - Front Door: Global CDN and load balancer
    - Private Link: Secure connectivity
  
  orchestration:
    - Azure Data Factory: ETL/ELT pipelines
    - Or self-hosted Airflow on AKS
  
  monitoring:
    - Azure Monitor: Metrics and logs
    - Application Insights: APM and tracing
    - Log Analytics: Query and analysis
    - Azure Sentinel: SIEM (security)
  
  security:
    - Azure Active Directory: Identity
    - Key Vault: Secrets and keys
    - Azure Policy: Governance
    - Defender for Cloud: Security posture

# Terraform example
resource "azurerm_kubernetes_cluster" "ml_pipeline" {
  name                = "customer-lifecycle-ml"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "ml-pipeline"
  
  default_node_pool {
    name       = "default"
    node_count = 3
    vm_size    = "Standard_D4s_v3"
  }
  
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_storage_account" "data_lake" {
  name                     = "mlpipelinedatalake"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  
  blob_properties {
    versioning_enabled = true
  }
}

---

### Deployment Option C4: IBM Cloud

```yaml
ibm_cloud_architecture:
  
  compute:
    - IBM Kubernetes Service (IKS): Managed Kubernetes
    - Code Engine: Serverless containers
    - Cloud Functions: Event-driven functions
    - Virtual Servers: Custom compute (GPU available)
  
  storage:
    - Cloud Object Storage: S3-compatible object storage
    - Block Storage: Persistent volumes
    - File Storage: NFS-based shared storage
  
  database:
    - Databases for PostgreSQL: Managed PostgreSQL
    - Databases for Redis: Managed Redis
    - Db2 Warehouse: Data warehouse
  
  ml_services:
    - Watson Studio: ML development platform
    - Watson Machine Learning: Model deployment
    - Watson OpenScale: Model monitoring
    - AutoAI: Automated ML
  
  networking:
    - Virtual Private Cloud (VPC): Network isolation
    - Load Balancer: Application load balancing
    - Cloud Internet Services: CDN + DDoS
    - Direct Link: Private connectivity
  
  orchestration:
    - Self-hosted Airflow on IKS
    - Or Watson Studio Pipelines
  
  monitoring:
    - IBM Cloud Monitoring: Sysdig-based monitoring
    - Log Analysis: LogDNA-based logging
    - Activity Tracker: Audit logs
  
  security:
    - IAM: Identity and access management
    - Key Protect: Key management (FIPS 140-2)
    - Secrets Manager: Secrets storage
    - Security and Compliance Center: Governance

# Terraform example
resource "ibm_container_cluster" "ml_pipeline" {
  name              = "customer-lifecycle-ml"
  datacenter        = "dal13"
  machine_type      = "b3c.4x16"
  hardware          = "shared"
  kube_version      = "1.28"
  default_pool_size = 3
}

resource "ibm_cos_bucket" "data_lake" {
  bucket_name          = "ml-pipeline-data-lake"
  resource_instance_id = ibm_resource_instance.cos.id
  region_location      = "us-south"
  storage_class        = "standard"
  
  archive_rule {
    rule_id = "archive-90-days"
    enable  = true
    days    = 90
    type    = "GLACIER"
  }
}
```

---

## Phase 8.5: Agentic AI Integration (AWS Bedrock Agents)

### Why Add Agentic AI to ML Pipeline?

**Use Cases:**
1. **Conversational ML Insights:** Ask questions about model predictions
2. **Automated Model Selection:** Agent chooses best model based on requirements
3. **Intelligent Feature Engineering:** Agent suggests new features
4. **Campaign Optimization:** Agent analyzes customer segments and recommends actions
5. **Anomaly Investigation:** Agent digs into data drift alerts

---

### AWS Bedrock Agents Architecture

```yaml
bedrock_agents_overview:
  
  what_is_it:
    - Managed service for building agentic AI applications
    - Orchestrates LLM calls, actions, and knowledge bases
    - Handles conversation state and memory
    - Integrates with Lambda for custom actions
  
  key_components:
    - foundation_models: Claude 3.5 Sonnet, Llama 3, etc.
    - agents: Orchestrate tasks with reasoning
    - actions: Lambda functions the agent can call
    - knowledge_bases: RAG over S3 documents
    - guardrails: Safety and content filtering
  
  benefits:
    - No need to manage LLM infrastructure
    - Built-in conversation memory
    - Automatic prompt optimization
    - Action orchestration (agent decides when to call functions)
    - RAG integration for domain knowledge
```

**Integration Pattern Example:**
```
User: "Which customers should we target for retention?"
  ↓
Bedrock Agent (Claude 3.5)
  ↓
Calls Lambda Action: get_high_risk_customers()
  ↓
Lambda queries PostgreSQL predictions table
  ↓
Returns: 156 high-risk, high-value customers
  ↓
Agent analyzes and recommends campaign
  ↓
Returns: "Target these 156 customers with VIP retention offer"
```

---

### Multi-Cloud Decision Matrix

```yaml
choose_aws_if:
  - Most mature ML services (SageMaker)
  - Largest ecosystem and community
  - Need widest range of services
  - Team already familiar with AWS
  - Global presence required (most regions)
  
  pros:
    - ✅ Most comprehensive ML services
    - ✅ Best documentation and community
    - ✅ Widest third-party integrations
    - ✅ 33 regions worldwide
  
  cons:
    - ❌ Can be complex (many overlapping services)
    - ❌ Vendor lock-in risk

choose_gcp_if:
  - BigQuery for analytics workloads
  - Best-in-class Kubernetes (GKE)
  - Need tight integration with Google services
  - Data science/ML focused (Vertex AI)
  - Prefer simplicity over options
  
  pros:
    - ✅ Superior BigQuery for analytics
    - ✅ Best Kubernetes experience (GKE Autopilot)
    - ✅ Clean, modern UI
    - ✅ Strong AI/ML focus
  
  cons:
    - ❌ Fewer regions than AWS
    - ❌ Smaller ecosystem
    - ❌ Some services less mature

choose_azure_if:
  - Enterprise Microsoft stack (AD, Office 365)
  - .NET applications or Windows workloads
  - Hybrid cloud requirements
  - Strong compliance needs (government, healthcare)
  - Existing Microsoft enterprise agreement
  
  pros:
    - ✅ Best Microsoft integration
    - ✅ Strong hybrid cloud (Azure Arc)
    - ✅ Excellent enterprise support
    - ✅ Good compliance certifications
  
  cons:
    - ❌ ML services less mature than AWS/GCP
    - ❌ Documentation can be fragmented
    - ❌ Some services behind competitors

choose_ibm_cloud_if:
  - Existing IBM enterprise relationship
  - Regulated industries (banking, healthcare)
  - Need highest security (FIPS 140-2 Level 4)
  - Legacy system integration (mainframe)
  - Want Watson AI capabilities
  
  pros:
    - ✅ Strongest security certifications
    - ✅ Excellent for regulated industries
    - ✅ Watson AI services
    - ✅ Good hybrid/multi-cloud tools
  
  cons:
    - ❌ Smaller cloud market share
    - ❌ Limited ML service maturity
    - ❌ Smaller community and ecosystem
```

---

### Cloud-Agnostic Implementation

**Abstraction Layer Design:**

```python
# src/cloud/storage.py
from abc import ABC, abstractmethod
from typing import BinaryIO, List
import boto3
from google.cloud import storage as gcs
from azure.storage.blob import BlobServiceClient

class CloudStorage(ABC):
    """Abstract base class for cloud storage."""
    
    @abstractmethod
    def upload_file(self, local_path: str, cloud_path: str) -> None:
        pass
    
    @abstractmethod
    def download_file(self, cloud_path: str, local_path: str) -> None:
        pass
    
    @abstractmethod
    def list_files(self, prefix: str) -> List[str]:
        pass


class S3Storage(CloudStorage):
    """AWS S3 implementation."""
    
    def __init__(self, bucket_name: str):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name
    
    def upload_file(self, local_path: str, cloud_path: str) -> None:
        self.s3.upload_file(local_path, self.bucket, cloud_path)
    
    def download_file(self, cloud_path: str, local_path: str) -> None:
        self.s3.download_file(self.bucket, cloud_path, local_path)
    
    def list_files(self, prefix: str) -> List[str]:
        response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return [obj['Key'] for obj in response.get('Contents', [])]


class GCSStorage(CloudStorage):
    """GCP Cloud Storage implementation."""
    
    def __init__(self, bucket_name: str):
        self.client = gcs.Client()
        self.bucket = self.client.bucket(bucket_name)
    
    def upload_file(self, local_path: str, cloud_path: str) -> None:
        blob = self.bucket.blob(cloud_path)
        blob.upload_from_filename(local_path)
    
    def download_file(self, cloud_path: str, local_path: str) -> None:
        blob = self.bucket.blob(cloud_path)
        blob.download_to_filename(local_path)
    
    def list_files(self, prefix: str) -> List[str]:
        blobs = self.client.list_blobs(self.bucket, prefix=prefix)
        return [blob.name for blob in blobs]


class AzureBlobStorage(CloudStorage):
    """Azure Blob Storage implementation."""
    
    def __init__(self, connection_string: str, container_name: str):
        self.blob_service = BlobServiceClient.from_connection_string(connection_string)
        self.container = container_name
    
    def upload_file(self, local_path: str, cloud_path: str) -> None:
        blob_client = self.blob_service.get_blob_client(
            container=self.container, blob=cloud_path
        )
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
    
    def download_file(self, cloud_path: str, local_path: str) -> None:
        blob_client = self.blob_service.get_blob_client(
            container=self.container, blob=cloud_path
        )
        with open(local_path, "wb") as file:
            file.write(blob_client.download_blob().readall())
    
    def list_files(self, prefix: str) -> List[str]:
        container_client = self.blob_service.get_container_client(self.container)
        return [blob.name for blob in container_client.list_blobs(name_starts_with=prefix)]


# Factory pattern
def get_storage_client(provider: str, **kwargs) -> CloudStorage:
    """Factory to get cloud storage client."""
    if provider == "aws":
        return S3Storage(kwargs['bucket_name'])
    elif provider == "gcp":
        return GCSStorage(kwargs['bucket_name'])
    elif provider == "azure":
        return AzureBlobStorage(kwargs['connection_string'], kwargs['container_name'])
    else:
        raise ValueError(f"Unknown provider: {provider}")


# Usage in config
# config.yaml
cloud:
  provider: aws  # or gcp, azure, ibm
  storage:
    bucket_name: ml-pipeline-data-lake
  
# Application code
storage = get_storage_client(
    provider=config.cloud.provider,
    **config.cloud.storage
)

# Now code is cloud-agnostic!
storage.upload_file("model.pkl", "models/churn_v2.pkl")
```

---

### Cost Comparison (Medium Scale)

---
```yaml
services:
  - RDS PostgreSQL (data warehouse)
  - ElastiCache Redis (feature store)
  - S3 (data lake, artifacts)
  - SageMaker (training, hosting)
  - Lambda (batch scoring)
  - API Gateway + Lambda or ECS (API)
  - CloudWatch (monitoring)
  - Step Functions (orchestration)
```

---

## Phase 9: Testing Strategy

### 9.1 Testing Pyramid
```yaml
testing_levels:
  
  unit_tests: (60% coverage)
    scope: individual functions/methods
    tools: pytest, unittest
    examples:
      - feature calculation correctness
      - data transformation logic
      - model prediction format
      - utility functions
  
  integration_tests: (30% coverage)
    scope: component interactions
    tools: pytest, testcontainers
    examples:
      - database connection + query
      - feature store read/write
      - MLflow logging + retrieval
      - API endpoint + model inference
  
  end_to_end_tests: (10% coverage)
    scope: full pipeline
    tools: pytest, docker-compose
    examples:
      - data pipeline → features → training → prediction
      - API request → feature fetch → prediction → response
      - retraining trigger → model update → deployment
  
  performance_tests:
    tools: locust, pytest-benchmark
    tests:
      - api_latency_under_load
      - batch_prediction_throughput
      - model_inference_time
  
  data_quality_tests:
    tools: great_expectations, pandera
    tests:
      - schema validation
      - data distribution checks
      - feature value ranges
      - null rate thresholds
```

### 9.2 Model Testing
```yaml
model_quality_tests:
  
  1. smoke_tests:
      - model loads successfully
      - prediction shape correct
      - no NaN predictions
      - probabilities in [0, 1]
  
  2. invariance_tests:
      - small feature perturbations → small prediction changes
      - duplicate inputs → identical predictions
  
  3. directional_tests:
      - increasing recency → decreasing churn
      - higher spend → higher CLV
      - more frequency → lower churn
  
  4. minimum_performance_tests:
      - auc_roc > 0.70 (or baseline + 5%)
      - precision@10% > 2x random
      - no performance degradation on key segments
  
  5. fairness_tests:
      - demographic parity (if applicable)
      - equal opportunity
      - no disparate impact
  
  6. explainability_tests:
      - SHAP values computed
      - top features make business sense
      - no suspicious feature importance
```

---

## Phase 10: Documentation & Knowledge Transfer

### 10.1 Documentation Requirements
```yaml
documentation_artifacts:
  
  1. technical_documentation:
      - architecture_diagram.md
      - api_reference.md
      - database_schema.md
      - feature_catalog.md
      - deployment_guide.md
  
  2. model_cards:
      - model_objective
      - training_data
      - performance_metrics
      - limitations
      - ethical_considerations
      - maintenance_schedule
  
  3. runbooks:
      - incident_response.md
      - model_retraining_guide.md
      - deployment_procedures.md
      - rollback_procedures.md
      - troubleshooting_guide.md
  
  4. business_documentation:
      - executive_summary.md
      - user_guide_for_stakeholders.md
      - roi_analysis.md
      - success_metrics.md
  
  5. api_documentation:
      - openapi_spec.yaml (Swagger/ReDoc)
      - authentication_guide.md
      - rate_limits.md
      - error_codes.md
      - example_requests.md
```

---

## Phase 11: Timeline & Milestones

### Week 1-2: Setup & Data Pipeline
- [ ] Project structure setup
- [ ] Database schema design
- [ ] Data extraction pipeline
- [ ] Data quality framework
- [ ] Initial EDA notebooks

### Week 3-4: Feature Engineering
- [ ] RFM features implementation
- [ ] Behavioral features
- [ ] Temporal features
- [ ] Feature store setup (Redis)
- [ ] Feature backfill

### Week 5-6: Model Development (CLV)
- [ ] Target variable definition
- [ ] Baseline model
- [ ] ML model training
- [ ] Hyperparameter tuning
- [ ] Model evaluation

### Week 7-8: Model Development (Churn)
- [ ] Churn definition
- [ ] Baseline model
- [ ] ML model training
- [ ] Class imbalance handling
- [ ] Model evaluation

### Week 9-10: Model Development (Propensity)
- [ ] Target definition
- [ ] Model training
- [ ] Calibration
- [ ] Ensemble creation
- [ ] Final evaluation

### Week 11-12: Inference & API
- [ ] Batch scoring pipeline
- [ ] FastAPI development
- [ ] API testing
- [ ] Performance optimization
- [ ] Documentation

### Week 13-14: MLOps Setup
- [ ] MLflow configuration
- [ ] CI/CD pipeline
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Monitoring setup

### Week 15-16: Experimentation Framework
- [ ] A/B testing platform
- [ ] Causal inference toolkit
- [ ] Sample size calculators
- [ ] Visualization dashboards

### Week 17-18: Testing & QA
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests
- [ ] E2E tests
- [ ] Performance tests
- [ ] Security audit

### Week 19-20: Deployment & Launch
- [ ] Staging deployment
- [ ] Production deployment (canary)
- [ ] Monitoring validation
- [ ] Stakeholder training
- [ ] Documentation finalization

---

## Phase 12: Success Metrics

### Technical KPIs
- **Model Performance:**
  - Churn AUC-ROC > 0.80
  - CLV MAPE < 20%
  - Propensity AUC-ROC > 0.75
  
- **System Performance:**
  - API Latency p99 < 200ms
  - Uptime > 99.9%
  - Batch pipeline completion < 2 hours
  
- **Data Quality:**
  - Feature completeness > 95%
  - Data freshness < 24 hours
  - Zero schema violations

### Business KPIs
- **Revenue Impact:**
  - +10% increase in customer retention
  - +15% marketing campaign ROI
  - +20% upsell conversion rate
  
- **Operational Efficiency:**
  - 50% reduction in manual segmentation time
  - 80% reduction in ad spend waste (incrementality)
  - Automated daily predictions for 100% of customers

### Adoption Metrics
- % of marketing campaigns using predictions
- % of CSRs accessing churn scores
- Number of API calls per day
- Stakeholder satisfaction score

---

## Phase 13: Risks & Mitigation

### Technical Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data quality issues | High | Medium | Implement robust validation, Great Expectations |
| Model performance degradation | High | Medium | Continuous monitoring, automated retraining |
| Scalability bottlenecks | Medium | Low | Load testing, horizontal scaling, caching |
| Feature store latency | Medium | Medium | Redis optimization, CDN, fallback to batch |
| Dependency vulnerabilities | Medium | Medium | Automated security scans, regular updates |

### Business Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Low stakeholder adoption | High | Medium | Change management, training, clear ROI demos |
| Privacy/compliance issues | High | Low | GDPR compliance review, data anonymization |
| Misaligned incentives | Medium | Medium | Clear success metrics, stakeholder alignment |
| Model bias/fairness | Medium | Low | Fairness tests, diverse training data |

---

## Phase 14: Team & Resources

### Team Composition
- **ML Engineer / Data Scientist (You):** End-to-end ownership
- **Data Engineer (0.5 FTE):** Data pipeline support
- **Backend Engineer (0.3 FTE):** API development support
- **DevOps/SRE (0.3 FTE):** Infrastructure & monitoring
- **Product Manager (0.2 FTE):** Requirements & prioritization
- **Marketing Stakeholder:** Business validation

### Infrastructure Requirements
```yaml
development:
  - local machine (32GB RAM, GPU optional)
  - PostgreSQL (local or cloud)
  - Docker Desktop

staging:
  - 2x API servers (4 vCPU, 16GB RAM)
  - 1x Redis cluster (3 nodes)
  - 1x PostgreSQL (8 vCPU, 32GB RAM)
  - 1x Airflow (4 vCPU, 16GB RAM)
  - 1x MLflow (2 vCPU, 8GB RAM)

production:
  - 5x API servers (autoscaling)
  - 1x Redis cluster (HA, 3 nodes)
  - 1x PostgreSQL (HA, read replicas)
  - 1x Airflow (HA setup)
  - 1x MLflow (HA setup)
  - Monitoring stack (Prometheus + Grafana)
```

---

## Next Steps

1. **Review & Approval:** Stakeholder alignment on scope and timeline
2. **Environment Setup:** Provision infrastructure (dev → staging → prod)
3. **Data Access:** Secure database credentials, S3 buckets
4. **Kickoff:** Implement Phase 1 (project structure + data pipeline)

---

## Appendix: Key Technologies Summary

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.11+ | ML ecosystem, team expertise |
| Data Warehouse | PostgreSQL / DuckDB | Structured data, SQL analytics |
| Feature Store | Redis | Low-latency key-value store |
| ML Framework | scikit-learn, XGBoost, LightGBM | Industry standard, proven |
| Experiment Tracking | MLflow | Open-source, model registry |
| API | FastAPI | High performance, async, auto docs |
| Orchestration | Apache Airflow | Complex DAG support, monitoring |
| Containerization | Docker + Kubernetes | Portability, scalability |
| Monitoring | Prometheus + Grafana | Metrics collection, visualization |
| Testing | pytest, Great Expectations | Comprehensive testing |
| CI/CD | GitHub Actions | Integrated with repo |

---

**Document Version:** 1.0  
**Last Updated:** November 1, 2026  
**Owner:** ML Engineering Team  
**Status:** Plan - Awaiting Approval
