# AI SRE Stack - Deployment Guide

Complete guide to deploying the AI SRE Stack across different platforms and environments.

---

## Table of Contents

1. [Deployment Options Overview](#deployment-options-overview)
2. [Kubernetes Deployment](#kubernetes-deployment)
3. [AWS Deployment](#aws-deployment)
4. [Azure Deployment](#azure-deployment)
5. [Google Cloud Deployment](#google-cloud-deployment)
6. [Docker Deployment](#docker-deployment)
7. [VM/Bare Metal Deployment](#vmbare-metal-deployment)
8. [Serverless Deployment](#serverless-deployment)
9. [Production Best Practices](#production-best-practices)

---

## Deployment Options Overview

### ✅ Recommended: Kubernetes

**Best for**: Production deployments, scalability, high availability

**Pros**:
- Native integration with Kubernetes MCP
- Easy scaling and updates
- Health checks and auto-restart
- Secrets management via K8s secrets
- Resource limits and monitoring

**Cons**:
- Requires Kubernetes cluster
- More complex setup

---

### ✅ Good: AWS (EC2, ECS, Lambda)

**Best for**: AWS-heavy infrastructure, serverless needs

**Pros**:
- Native AWS MCP integration
- Multiple deployment options
- Easy IAM integration
- Managed services available

**Cons**:
- AWS vendor lock-in
- Cost considerations

---

### ✅ Good: Docker Container

**Best for**: Portable deployments, development, testing

**Pros**:
- Runs anywhere Docker runs
- Consistent environment
- Easy to version and rollback
- Lightweight

**Cons**:
- Requires container orchestration for HA
- Manual scaling

---

### ✅ Good: VM or Bare Metal

**Best for**: On-premise deployments, existing infrastructure

**Pros**:
- Full control
- No vendor lock-in
- Works with existing systems

**Cons**:
- Manual setup and maintenance
- Need to handle HA yourself

---

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (1.20+)
- kubectl configured
- Secrets management (Sealed Secrets or External Secrets Operator)

### Deployment Files

#### 1. Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-sre-stack
  labels:
    app: ai-sre-stack
```

#### 2. Secrets
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-sre-secrets
  namespace: ai-sre-stack
type: Opaque
stringData:
  ANTHROPIC_API_KEY: "sk-ant-your-key"
  AWS_ACCESS_KEY_ID: "your-aws-key"
  AWS_SECRET_ACCESS_KEY: "your-aws-secret"
  DATADOG_API_KEY: "your-datadog-key"
  DATADOG_APP_KEY: "your-datadog-app-key"
  SLACK_BOT_TOKEN: "xoxb-your-token"
  GITHUB_TOKEN: "ghp_your-token"
  PAGERDUTY_API_KEY: "your-pd-key"
  VAULT_TOKEN: "your-vault-token"
```

**⚠️ Security Note**: Use Sealed Secrets or External Secrets Operator in production!

#### 3. ConfigMap
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-sre-config
  namespace: ai-sre-stack
data:
  # Orchestration settings
  OBSERVATION_INTERVAL: "60"
  DRY_RUN: "false"
  AUTO_REMEDIATION: "true"
  
  # Security controls
  SECURITY_ENABLE_ACTION_WHITELIST: "true"
  SECURITY_ENABLE_RATE_LIMITING: "true"
  SECURITY_ENABLE_AUDIT_LOGGING: "true"
  SECURITY_ENABLE_APPROVAL_WORKFLOW: "true"
  
  # Rate limits
  SECURITY_MAX_ACTIONS_PER_MINUTE: "10"
  SECURITY_MAX_ACTIONS_PER_HOUR: "100"
  SECURITY_MAX_ACTIONS_PER_DAY: "500"
  
  # Slack
  SLACK_CHANNEL: "#sre-alerts"
  
  # Kubernetes
  K8S_NAMESPACE: "default"
  
  # AWS
  AWS_REGION: "us-east-1"
  
  # Vault
  VAULT_URL: "http://vault.vault.svc.cluster.local:8200"
  VAULT_MOUNT_POINT: "secret"
```

#### 4. Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-sre-orchestrator
  namespace: ai-sre-stack
  labels:
    app: ai-sre-orchestrator
spec:
  replicas: 1  # Single instance for now (stateful)
  selector:
    matchLabels:
      app: ai-sre-orchestrator
  template:
    metadata:
      labels:
        app: ai-sre-orchestrator
    spec:
      serviceAccountName: ai-sre-sa
      containers:
      - name: orchestrator
        image: your-registry/ai-sre-stack:latest
        imagePullPolicy: Always
        
        env:
        # Load from ConfigMap
        - name: OBSERVATION_INTERVAL
          valueFrom:
            configMapKeyRef:
              name: ai-sre-config
              key: OBSERVATION_INTERVAL
        
        # Load from Secrets
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-sre-secrets
              key: ANTHROPIC_API_KEY
        
        # Add all other env vars from ConfigMap and Secrets
        # ... (abbreviated for brevity)
        
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        
        volumeMounts:
        - name: audit-logs
          mountPath: /app/logs
        - name: kubeconfig
          mountPath: /app/.kube
          readOnly: true
        
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 60
          periodSeconds: 60
        
        readinessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 30
          periodSeconds: 30
      
      volumes:
      - name: audit-logs
        persistentVolumeClaim:
          claimName: audit-logs-pvc
      - name: kubeconfig
        secret:
          secretName: kubeconfig-secret
```

#### 5. ServiceAccount & RBAC
```yaml
# k8s/rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ai-sre-sa
  namespace: ai-sre-stack
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ai-sre-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "events", "namespaces"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch", "patch", "update"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ai-sre-binding
subjects:
- kind: ServiceAccount
  name: ai-sre-sa
  namespace: ai-sre-stack
roleRef:
  kind: ClusterRole
  name: ai-sre-role
  apiGroup: rbac.authorization.k8s.io
```

#### 6. PersistentVolume for Audit Logs
```yaml
# k8s/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: audit-logs-pvc
  namespace: ai-sre-stack
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets (use Sealed Secrets in production!)
kubectl apply -f k8s/secrets.yaml

# Create ConfigMap
kubectl apply -f k8s/configmap.yaml

# Create RBAC
kubectl apply -f k8s/rbac.yaml

# Create PVC
kubectl apply -f k8s/pvc.yaml

# Deploy application
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods -n ai-sre-stack
kubectl logs -f deployment/ai-sre-orchestrator -n ai-sre-stack
```

### Scale Up (Future)
```bash
# When ready for HA (requires state synchronization)
kubectl scale deployment ai-sre-orchestrator -n ai-sre-stack --replicas=3
```

---

## AWS Deployment

### Option 1: EC2 Instance

**Best for**: Simple deployment, full control

#### Setup
```bash
# 1. Launch EC2 instance (Amazon Linux 2 or Ubuntu)
# Instance type: t3.medium or larger
# Storage: 20GB+ EBS

# 2. SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# 3. Install dependencies
sudo yum update -y
sudo yum install python3 python3-pip git -y

# 4. Clone or copy project
git clone your-repo-url
cd ai-sre-stack

# 5. Install Python packages
pip3 install -r requirements.txt

# 6. Configure environment
cp .env.example .env
nano .env  # Edit with your credentials

# 7. Run as systemd service
sudo cp deployment/ai-sre-stack.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-sre-stack
sudo systemctl start ai-sre-stack

# 8. Check logs
sudo journalctl -u ai-sre-stack -f
```

#### Systemd Service File
```ini
# deployment/ai-sre-stack.service
[Unit]
Description=AI SRE Stack Orchestrator
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/ai-sre-stack
ExecStart=/usr/bin/python3 /home/ec2-user/ai-sre-stack/sre_orchestrator.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

---

### Option 2: ECS (Elastic Container Service)

**Best for**: Container-based deployment, AWS integration

#### Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Run orchestrator
CMD ["python", "sre_orchestrator.py"]
```

#### Build and Push
```bash
# Build image
docker build -t ai-sre-stack:latest .

# Tag for ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker tag ai-sre-stack:latest your-account.dkr.ecr.us-east-1.amazonaws.com/ai-sre-stack:latest

# Push to ECR
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/ai-sre-stack:latest
```

#### ECS Task Definition
```json
{
  "family": "ai-sre-stack",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "orchestrator",
      "image": "your-account.dkr.ecr.us-east-1.amazonaws.com/ai-sre-stack:latest",
      "essential": true,
      "environment": [
        {"name": "AWS_REGION", "value": "us-east-1"},
        {"name": "DRY_RUN", "value": "false"}
      ],
      "secrets": [
        {
          "name": "ANTHROPIC_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:account:secret:ai-sre/anthropic-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-sre-stack",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "orchestrator"
        }
      }
    }
  ]
}
```

---

### Option 3: Lambda (Event-Driven)

**Best for**: Event-driven SRE tasks, cost optimization

⚠️ **Note**: Lambda has 15-minute timeout, not suitable for continuous monitoring. Use for:
- Event-triggered remediation
- Scheduled health checks
- On-demand actions

#### Lambda Handler
```python
# lambda_handler.py
import json
import asyncio
from sre_orchestrator import SREOrchestrator

def lambda_handler(event, context):
    """AWS Lambda handler for SRE tasks."""
    
    async def run():
        orchestrator = SREOrchestrator()
        await orchestrator.initialize()
        await orchestrator.run_cycle()
        await orchestrator.shutdown()
    
    # Run single cycle
    asyncio.run(run())
    
    return {
        'statusCode': 200,
        'body': json.dumps('SRE cycle completed')
    }
```

#### EventBridge Schedule
```yaml
# CloudFormation template for scheduled Lambda
Resources:
  SRECycleRule:
    Type: AWS::Events::Rule
    Properties:
      Description: "Run SRE cycle every 5 minutes"
      ScheduleExpression: "rate(5 minutes)"
      State: ENABLED
      Targets:
        - Arn: !GetAtt SRELambdaFunction.Arn
          Id: "SRETarget"
```

---

## Azure Deployment

### Option 1: Azure Container Instances

```bash
# Create resource group
az group create --name ai-sre-stack-rg --location eastus

# Create container instance
az container create \
  --resource-group ai-sre-stack-rg \
  --name ai-sre-orchestrator \
  --image your-registry/ai-sre-stack:latest \
  --cpu 1 \
  --memory 2 \
  --restart-policy Always \
  --environment-variables \
    DRY_RUN=false \
    AWS_REGION=us-east-1 \
  --secure-environment-variables \
    ANTHROPIC_API_KEY=your-key
```

### Option 2: Azure Kubernetes Service (AKS)

Use Kubernetes deployment files (same as above) with AKS cluster.

---

## Google Cloud Deployment

### Option 1: Cloud Run

```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/your-project/ai-sre-stack

gcloud run deploy ai-sre-orchestrator \
  --image gcr.io/your-project/ai-sre-stack \
  --platform managed \
  --region us-central1 \
  --set-env-vars DRY_RUN=false \
  --set-secrets ANTHROPIC_API_KEY=anthropic-key:latest
```

### Option 2: Google Kubernetes Engine (GKE)

Use Kubernetes deployment files with GKE cluster.

---

## Docker Deployment

### Build Docker Image

```dockerfile
# Dockerfile (production-ready)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 sre && \
    chown -R sre:sre /app && \
    mkdir -p /app/logs && \
    chown -R sre:sre /app/logs

# Switch to non-root user
USER sre

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

# Run orchestrator
CMD ["python", "-u", "sre_orchestrator.py"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  orchestrator:
    build: .
    container_name: ai-sre-orchestrator
    restart: unless-stopped
    
    environment:
      - DRY_RUN=false
      - AUTO_REMEDIATION=true
      - OBSERVATION_INTERVAL=60
      
      # Security controls
      - SECURITY_ENABLE_ACTION_WHITELIST=true
      - SECURITY_ENABLE_RATE_LIMITING=true
      - SECURITY_ENABLE_AUDIT_LOGGING=true
      - SECURITY_ENABLE_APPROVAL_WORKFLOW=true
    
    env_file:
      - .env  # Contains secrets
    
    volumes:
      - ./logs:/app/logs
      - ~/.kube/config:/app/.kube/config:ro
    
    networks:
      - sre-network
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  sre-network:
    driver: bridge
```

### Run with Docker Compose

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

---

## VM/Bare Metal Deployment

### Ubuntu/Debian

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python
sudo apt install python3 python3-pip python3-venv git -y

# 3. Create service user
sudo useradd -r -s /bin/bash -d /opt/ai-sre-stack sre

# 4. Clone repository
sudo git clone your-repo-url /opt/ai-sre-stack
sudo chown -R sre:sre /opt/ai-sre-stack

# 5. Install dependencies
sudo -u sre bash <<EOF
cd /opt/ai-sre-stack
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
EOF

# 6. Configure
sudo -u sre cp /opt/ai-sre-stack/.env.example /opt/ai-sre-stack/.env
sudo -u sre nano /opt/ai-sre-stack/.env

# 7. Create systemd service
sudo tee /etc/systemd/system/ai-sre-stack.service > /dev/null <<EOF
[Unit]
Description=AI SRE Stack Orchestrator
After=network.target

[Service]
Type=simple
User=sre
WorkingDirectory=/opt/ai-sre-stack
ExecStart=/opt/ai-sre-stack/venv/bin/python sre_orchestrator.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 8. Start service
sudo systemctl daemon-reload
sudo systemctl enable ai-sre-stack
sudo systemctl start ai-sre-stack

# 9. Check status
sudo systemctl status ai-sre-stack
sudo journalctl -u ai-sre-stack -f
```

---

## Production Best Practices

### 1. High Availability

**Kubernetes**: Use multiple replicas with leader election
```yaml
replicas: 3
# Add leader election logic in orchestrator
```

**AWS**: Use Auto Scaling Group with health checks
**Azure**: Use Availability Sets or Scale Sets

### 2. Secrets Management

**Best Practice**: Use dedicated secrets managers

**Kubernetes**:
- Sealed Secrets
- External Secrets Operator
- Vault integration

**AWS**:
- AWS Secrets Manager
- Parameter Store

**Azure**:
- Azure Key Vault

**GCP**:
- Secret Manager

### 3. Monitoring & Logging

**Metrics**:
- Prometheus + Grafana
- Datadog APM
- CloudWatch

**Logs**:
- ELK Stack (Elasticsearch + Logstash + Kibana)
- Splunk
- CloudWatch Logs

**Audit Logs**:
- Store in S3/Azure Blob/GCS
- Index in Elasticsearch
- Forward to SIEM

### 4. Backup & Recovery

```bash
# Backup audit logs
aws s3 sync /app/logs/ s3://ai-sre-backups/audit-logs/

# Backup configuration
kubectl get configmap ai-sre-config -n ai-sre-stack -o yaml > backup-config.yaml
```

### 5. Security Hardening

- Run as non-root user
- Use read-only file systems where possible
- Enable network policies (Kubernetes)
- Use security groups (AWS)
- Enable audit logging
- Rotate credentials regularly

### 6. Resource Limits

**Kubernetes**:
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

**Docker**:
```bash
docker run --memory="2g" --cpus="2" ai-sre-stack
```

---

## Deployment Comparison Matrix

| Platform | Complexity | Cost | HA | Scalability | Best For |
|----------|------------|------|----|-----------|----|
| **Kubernetes** | High | Medium | ✅ Excellent | ✅ Excellent | Production, Large scale |
| **AWS ECS** | Medium | Medium | ✅ Good | ✅ Good | AWS environments |
| **AWS EC2** | Low | Low | ⚠️ Manual | ⚠️ Manual | Simple deployments |
| **AWS Lambda** | Low | Very Low | ✅ Built-in | ✅ Auto | Event-driven tasks |
| **Azure ACI** | Low | Medium | ⚠️ Limited | ⚠️ Limited | Quick deployments |
| **GCP Cloud Run** | Low | Low | ✅ Built-in | ✅ Auto | Serverless needs |
| **Docker** | Low | Very Low | ❌ No | ❌ No | Development, Testing |
| **VM/Bare Metal** | Low | Variable | ❌ Manual | ❌ Manual | On-premise |

---

## Quick Start by Environment

### Development
```bash
python sre_orchestrator.py
```

### Testing
```bash
docker-compose up
```

### Staging (Kubernetes)
```bash
kubectl apply -f k8s/ --namespace=staging
```

### Production (Kubernetes)
```bash
kubectl apply -f k8s/ --namespace=production
kubectl rollout status deployment/ai-sre-orchestrator -n production
```

---

## Support & Troubleshooting

### Common Issues

**Pod CrashLoopBackOff**: Check logs for missing secrets or config
**High Memory Usage**: Increase resource limits
**Connection Timeouts**: Check network policies and security groups
**Permission Denied**: Verify RBAC or IAM roles

### Get Help

- Check logs: `kubectl logs` or `docker logs`
- Review audit logs: `logs/audit.jsonl`
- Test connectivity to external services
- Verify secrets are correctly configured

---

## Conclusion

The AI SRE Stack can be deployed anywhere Python runs:

✅ **Production**: Kubernetes (recommended)  
✅ **Cloud**: AWS ECS, Azure ACI, GCP Cloud Run  
✅ **Serverless**: AWS Lambda, GCP Cloud Functions  
✅ **Traditional**: VM, Bare Metal, Docker  

Choose based on your:
- Infrastructure preferences
- HA requirements
- Cost constraints
- Team expertise

**Start with Docker for testing, move to Kubernetes for production!**
