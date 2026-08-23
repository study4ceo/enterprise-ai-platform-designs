# Azure AI/ML Interview Questions (50 Questions)

## Core Azure ML Services (Questions 1-10)

### Q1: What is Azure Machine Learning and its key components?

**Answer:**
**Azure Machine Learning** is a cloud-based platform for building, training, and deploying ML models.

**Key Components:**
- **Azure ML Studio**: Web-based IDE
- **Azure ML Workspace**: Central resource for ML projects
- **Azure ML Compute**: Training/inference compute clusters
- **Azure ML Datasets**: Data versioning and management
- **Azure ML Experiments**: Track training runs
- **Azure ML Pipelines**: ML workflow orchestration
- **Azure ML Models**: Model registry
- **Azure ML Endpoints**: Model deployment (real-time/batch)
- **Azure ML Designer**: Drag-and-drop ML pipeline builder
- **Automated ML**: AutoML capabilities

**Workspace Hierarchy:**
```
Subscription
  └─ Resource Group
      └─ ML Workspace
          ├─ Compute
          ├─ Datastores
          ├─ Datasets
          ├─ Experiments
          ├─ Models
          └─ Endpoints
```

**Example:**
```python
from azureml.core import Workspace, Experiment, ScriptRunConfig

# Connect to workspace
ws = Workspace.from_config()

# Create experiment
experiment = Experiment(workspace=ws, name='training-experiment')

# Configure training
config = ScriptRunConfig(
    source_directory='./src',
    script='train.py',
    compute_target='cpu-cluster',
    environment=Environment.from_conda_specification(
        name='ml-env',
        file_path='conda.yml'
    )
)

# Submit run
run = experiment.submit(config)
run.wait_for_completion(show_output=True)
```

---

### Q2: Explain Azure ML Compute types and when to use each.

**Answer:**

**1. Compute Instance (Development):**
- Personal cloud workstation
- Jupyter, VS Code, RStudio
- Always-on or scheduled shutdown
- Use: Development, prototyping

**2. Compute Cluster (Training):**
- Auto-scaling clusters
- CPU or GPU
- Scale to zero when idle
- Use: Training, batch inference

**3. Inference Cluster (AKS):**
- Azure Kubernetes Service
- Production workloads
- Auto-scaling
- Use: Real-time inference at scale

**4. Attached Compute:**
- Use existing VMs, Databricks, Synapse
- Bring your own compute
- Use: Integration with existing infrastructure

**Comparison:**

| Compute Type | Purpose | Scaling | Cost |
|--------------|---------|---------|------|
| Instance | Dev/test | Fixed size | Always running |
| Cluster | Training | Auto-scale 0-N | Pay per use |
| AKS | Production inference | Auto-scale | Running cluster |
| Attached | Existing resources | Managed elsewhere | Varies |

**Example:**
```python
from azureml.core.compute import ComputeTarget, AmlCompute

# Create compute cluster
compute_config = AmlCompute.provisioning_configuration(
    vm_size='STANDARD_D3_V2',
    min_nodes=0,
    max_nodes=4,
    idle_seconds_before_scaledown=1800
)

compute = ComputeTarget.create(ws, 'cpu-cluster', compute_config)
compute.wait_for_completion(show_output=True)
```

---

### Q3: What is Azure Automated ML and its capabilities?

**Answer:**

**Azure Automated ML (AutoML)** automatically builds and tunes ML models.

**Task Types:**
- Classification (binary, multiclass)
- Regression
- Time-series forecasting
- Computer Vision (image classification, object detection)
- NLP (text classification, NER)

**What AutoML Does:**
- Feature engineering (scaling, encoding, imputation)
- Algorithm selection (tries multiple algorithms)
- Hyperparameter tuning
- Ensemble model creation
- Model explainability
- Guardrails (prevent overfitting)

**Supported Algorithms:**
- LightGBM, XGBoost, Random Forest
- Logistic Regression, Linear Regression
- Neural networks (TabNet, DNN)

**Example:**
```python
from azureml.train.automl import AutoMLConfig

automl_config = AutoMLConfig(
    task='classification',
    primary_metric='accuracy',
    training_data=train_dataset,
    label_column_name='target',
    n_cross_validations=5,
    enable_early_stopping=True,
    experiment_timeout_hours=1,
    max_concurrent_iterations=4,
    featurization='auto',
    enable_voting_ensemble=True,
    enable_stack_ensemble=True
)

remote_run = experiment.submit(automl_config)
best_run, fitted_model = remote_run.get_output()
```

---

### Q4: Explain Azure ML Pipelines and their components.

**Answer:**

**Azure ML Pipelines** are workflows for ML tasks.

**Components:**

**1. Pipeline Steps:**

- PythonScriptStep: Run Python scripts
- ParallelRunStep: Batch processing
- AutoMLStep: Automated ML
- DataTransferStep: Move data between datastores
- EstimatorStep: Train with estimators

**2. Pipeline Data:**
- PipelineData: Intermediate data between steps
- Datasets: Input data references

**3. Pipeline Parameters:**
- Runtime inputs (hyperparameters, file paths)

**Benefits:**
- Reusable workflows
- Parallel execution
- Scheduled runs
- CI/CD integration
- Cost optimization (caching)

**Example:**
```python
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.pipeline.steps import PythonScriptStep

# Intermediate data
processed_data = PipelineData('processed', datastore=ws.get_default_datastore())

# Step 1: Preprocess
preprocess_step = PythonScriptStep(
    name='preprocess',
    script_name='preprocess.py',
    arguments=['--output', processed_data],
    outputs=[processed_data],
    compute_target='cpu-cluster'
)

# Step 2: Train
train_step = PythonScriptStep(
    name='train',
    script_name='train.py',
    arguments=['--input', processed_data],
    inputs=[processed_data],
    compute_target='gpu-cluster'
)

# Create pipeline
pipeline = Pipeline(workspace=ws, steps=[preprocess_step, train_step])
pipeline_run = experiment.submit(pipeline)

# Publish for reuse
published_pipeline = pipeline.publish(name='ml-pipeline')

# Schedule
from azureml.pipeline.core.schedule import Schedule
Schedule.create(ws, name='daily-training', 
                pipeline_id=published_pipeline.id,
                experiment_name='scheduled-training',
                recurrence=ScheduleRecurrence(frequency='Day', interval=1))
```

---

### Q5-10: Core Azure ML Quick Reference

### Q5: **What are Azure ML Datasets?**
Versioned data references. Tabular or File datasets. Track lineage. Monitor data drift. Registered in workspace.

### Q6: **Azure ML Model Registry features?**
Central repository. Version control. Tagging and metadata. Model profiles. Deployment tracking. CI/CD integration.

### Q7: **What are Azure ML Environments?**
Docker-based. Define Python packages, env variables. Curated (Microsoft-maintained) or custom. Reproducible training/inference.

### Q8: **Explain Azure ML MLflow integration.**
Track experiments, log metrics, artifacts. Model registry. Deploy MLflow models. Cross-platform compatibility.

### Q9: **What is Azure ML Designer?**
Drag-and-drop interface. No-code ML pipelines. Pre-built modules. Visual workflow. Export to Python SDK.

### Q10: **Azure ML Responsible AI Dashboard?**
Model debugging, fairness assessment, error analysis, model interpretability, counterfactual what-if, causal analysis.

---

## Azure Cognitive Services (Questions 11-20)

### Q11: Compare Azure Computer Vision, Custom Vision, and Face API.

**Answer:**

**Computer Vision:**
- Pre-built image analysis
- OCR, object detection, image tagging
- Adult content detection
- Spatial analysis
- No training needed

**Custom Vision:**
- Train custom image models
- Classification and object detection
- Upload labeled images
- Export models (ONNX, TensorFlow)
- Use: Brand-specific recognition

**Face API:**
- Face detection and recognition
- Age, emotion, attributes
- Face verification (1:1)
- Face identification (1:N)
- Use: Security, attendance systems

### Q12-20: Azure Cognitive Services Quick Reference

**Q12: Azure Speech Services capabilities?**
Speech-to-text, text-to-speech, speech translation, speaker recognition. Custom models. Real-time and batch.

**Q13: Language Understanding (LUIS) vs CLU?**
LUIS (legacy): Intent recognition. CLU (Conversational Language Understanding): Modern, better performance, multilingual.

**Q14: Azure Translator features?**
90+ languages. Document translation. Custom translation models. Real-time translation API.

**Q15: Text Analytics capabilities?**
Sentiment analysis, key phrase extraction, NER, PII detection, language detection, opinion mining.

**Q16: QnA Maker vs Question Answering?**
QnA Maker (legacy). Question Answering (part of Language Service): Better, integrated, improved ranking.

**Q17: Azure Bot Service framework?**
Build chatbots. SDK (C#, Python, JavaScript). Channels: Teams, Slack, Web Chat. LUIS/CLU integration.

**Q18: Form Recognizer capabilities?**
Extract text, tables, key-value pairs. Pre-built models: Invoice, Receipt, ID, Business Card. Custom models.

**Q19: Anomaly Detector use cases?**
Time-series anomaly detection. Detect spikes, dips, trends. IoT monitoring, fraud detection.

**Q20: Personalizer service?**
Reinforcement learning for personalization. Content recommendations. A/B testing. Learn from user actions.

---

## Azure ML Advanced Topics (Questions 21-50)

### Q21: **What is Azure ML CLI v2?**
Command-line interface. YAML-based job definitions. CI/CD integration. Simpler than v1.

### Q22: **Explain Azure ML online vs batch endpoints.**
Online: Real-time, low latency, REST API. Batch: Large datasets, scheduled, async processing.

### Q23: **Azure ML managed online endpoints vs AKS?**
Managed: Serverless, auto-scaling, simpler. AKS: More control, existing clusters, networking options.

### Q24: **What is Azure ML Model Monitoring?**
Data drift detection. Model performance tracking. Alerts on degradation. Integration with App Insights.

### Q25: **Azure ML Feature Store (preview)?**
Centralized feature management. Online and offline serving. Feature versioning. Point-in-time join.

### Q26: **Explain Azure ML parallel job.**
Batch processing at scale. Process files in parallel. Auto-partitioning. Use: Scoring, ETL.

### Q27: **Azure ML sweep job?**
Hyperparameter tuning. Grid, random, Bayesian search. Early termination policies.

### Q28: **What is Azure ML Registry?**
Share models, environments, components across workspaces. Multi-workspace, multi-region.

### Q29: **Azure ML managed endpoints blue-green deployment?**
Deploy new version without downtime. Test before switching traffic. Instant rollback.

### Q30: **Explain Azure ML component.**
Reusable pipeline building blocks. Define interface (inputs, outputs). Share across teams.

### Q31: **Azure ML private link/VNet integration?**
Secure workspace behind VNet. Private endpoints. No public internet access. Workspace isolation.

### Q32: **What are Azure ML curated environments?**
Microsoft-maintained. TensorFlow, PyTorch, scikit-learn. Pre-tested, optimized. Regular updates.

### Q33: **Azure ML distributed training options?**
Horovod, PyTorch DDP, TensorFlow MultiWorkerMirroredStrategy, DeepSpeed. Multi-node GPU training.

### Q34: **Explain Azure ML model profiling.**
Predict resource requirements. Recommend instance type. Estimate latency. Cost optimization.

### Q35: **Azure ML cost estimation tools?**
Cost calculator. Usage tracking. Budget alerts. Optimize: spot VMs, auto-shutdown, right-sizing.

### Q36: **What is Azure ML studio (classic)?**
Legacy. Drag-and-drop interface. Being retired. Migrate to Azure ML Designer.

### Q37: **Azure ML integration with Azure Synapse?**
Linked services. Train on Synapse Spark pools. Access Synapse data. Unified analytics + ML.

### Q38: **Azure ML integration with Databricks?**
Attached compute. MLflow tracking. Deploy models. Use Databricks for data prep + training.

### Q39: **Explain Azure ML RunConfig vs ScriptRunConfig.**
RunConfig (legacy). ScriptRunConfig: Simplified, recommended. Define training script + compute.

### Q40: **Azure ML model interpretation techniques?**
SHAP, LIME, Permutation Feature Importance. Mimic explainer. Integrated with Responsible AI.

### Q41: **What is Azure ML model fairness assessment?**
Fairness Metrics. Disparity analysis. Mitigation algorithms. Part of Responsible AI Dashboard.

### Q42: **Azure ML differential privacy?**
SmartNoise toolkit. Privacy-preserving analytics. Add noise to protect individual data.

### Q43: **Explain Azure ML workspace diagnostics.**
Health checks. Connectivity tests. Dependency validation. Troubleshooting tool.

### Q44: **Azure ML geo-distributed training?**
Train across multiple regions. Data sovereignty compliance. Reduce data transfer.

### Q45: **What are Azure ML low-priority VMs?**
Up to 80% cost savings. Preemptible. Use for non-critical training. Checkpointing recommended.

### Q46: **Azure ML model packaging formats?**
ONNX, TensorFlow SavedModel, PyTorch, scikit-learn pickle. Supports most frameworks.

### Q47: **Explain Azure ML inference schema.**
Define input/output format. Auto-generate Swagger. Client SDK generation. API documentation.

### Q48: **Azure ML model versioning strategies?**
Semantic versioning. Tag latest, production. Immutable versions. Track deployment history.

### Q49: **What is Azure ML prompt flow (preview)?**
Build LLM applications. Chain prompts. Test and evaluate. Deploy as endpoint.

### Q50: **Azure ML integration with GitHub?**
GitHub Actions for CI/CD. Trigger training on commit. Automated model deployment. Version control for code + models.

---

## Summary: Azure ML Services Comparison

| Service | Purpose | Use Case |
|---------|---------|----------|
| **Azure ML** | Full ML platform | Custom models, MLOps |
| **Automated ML** | AutoML | Quick model building |
| **Computer Vision** | Image analysis | OCR, object detection |
| **Custom Vision** | Custom image models | Brand-specific recognition |
| **Face API** | Face recognition | Security, attendance |
| **Speech Services** | Speech processing | Transcription, TTS |
| **Language Service** | Text understanding | NER, sentiment |
| **Translator** | Translation | Multi-language content |
| **Bot Service** | Chatbots | Customer service |
| **Form Recognizer** | Document extraction | Invoice processing |
| **Anomaly Detector** | Anomaly detection | IoT monitoring |
| **Personalizer** | RL personalization | Content recommendations |

**Key Strengths:**
- Enterprise integration (Active Directory, VNet)
- Strong MLOps capabilities
- Responsible AI toolkit
- Hybrid cloud support
- Azure ecosystem integration
