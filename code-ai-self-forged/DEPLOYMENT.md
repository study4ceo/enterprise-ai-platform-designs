# Deployment Guide for Code-AI-Self-Forged

## Deployment Options

### Option 1: Local Development (Recommended for Testing)

**Requirements:**
- Python 3.14+
- pip
- Anthropic API key

**Steps:**
```bash
# 1. Clone/navigate to project
cd code-ai-self-forged

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Run application
python main.py

# Or run tests
python run_all_tests.py
```

---

## Option 2: Docker Deployment (Production Ready)

**Requirements:**
- Docker 20.10+
- Docker Compose 2.0+
- Anthropic API key

### Quick Start with Docker

```bash
# 1. Create .env file with your API key
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env

# 2. Build and run with Docker Compose
docker-compose up -d

# 3. Attach to interactive session
docker attach code-ai-self-forged

# 4. Or run in one-shot mode
docker-compose run --rm code-ai-self-forged python main.py "your problem here"
```

### Docker Build Only

```bash
# Build image
docker build -t code-ai-self-forged:latest .

# Run interactively
docker run -it --rm \
  -e ANTHROPIC_API_KEY=your_key_here \
  -v $(pwd)/workspace:/app/workspace \
  -v $(pwd)/logs:/app/logs \
  code-ai-self-forged:latest

# Run one-shot
docker run --rm \
  -e ANTHROPIC_API_KEY=your_key_here \
  code-ai-self-forged:latest \
  python main.py "Calculate fibonacci up to 100"
```

### Run Test Suites in Docker

```bash
# Run all tests
docker-compose --profile testing run --rm test-runner

# Run specific test suite
docker-compose run --rm code-ai-self-forged python test_time_series.py
```

---

## Option 3: Cloud Deployment

### Deploy to AWS (ECS/Fargate)

```bash
# 1. Build and tag image
docker build -t code-ai-self-forged:latest .
docker tag code-ai-self-forged:latest \
  your-account.dkr.ecr.region.amazonaws.com/code-ai-self-forged:latest

# 2. Push to ECR
aws ecr get-login-password --region region | docker login --username AWS --password-stdin your-account.dkr.ecr.region.amazonaws.com
docker push your-account.dkr.ecr.region.amazonaws.com/code-ai-self-forged:latest

# 3. Create ECS task definition with environment variables
# Add ANTHROPIC_API_KEY as secret from AWS Secrets Manager
```

### Deploy to Google Cloud Run

```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/your-project/code-ai-self-forged

# 2. Deploy to Cloud Run
gcloud run deploy code-ai-self-forged \
  --image gcr.io/your-project/code-ai-self-forged \
  --platform managed \
  --region us-central1 \
  --set-env-vars ANTHROPIC_API_KEY=your_key_here \
  --allow-unauthenticated
```

### Deploy to Azure Container Instances

```bash
# 1. Create container registry and push image
az acr build --registry yourregistry \
  --image code-ai-self-forged:latest .

# 2. Deploy to ACI
az container create \
  --resource-group your-rg \
  --name code-ai-self-forged \
  --image yourregistry.azurecr.io/code-ai-self-forged:latest \
  --environment-variables ANTHROPIC_API_KEY=your_key_here
```

---

## Option 4: Kubernetes Deployment

**Create Kubernetes manifests:**

### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: code-ai-self-forged
spec:
  replicas: 1
  selector:
    matchLabels:
      app: code-ai-self-forged
  template:
    metadata:
      labels:
        app: code-ai-self-forged
    spec:
      containers:
      - name: code-ai-self-forged
        image: code-ai-self-forged:latest
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: anthropic-secret
              key: api-key
        - name: MODEL_NAME
          value: "claude-sonnet-4.6"
        - name: MAX_TOKENS
          value: "8000"
        volumeMounts:
        - name: workspace
          mountPath: /app/workspace
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: workspace
        emptyDir: {}
      - name: logs
        persistentVolumeClaim:
          claimName: logs-pvc
```

### secret.yaml
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: anthropic-secret
type: Opaque
stringData:
  api-key: your_anthropic_api_key_here
```

**Deploy:**
```bash
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
```

---

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API key | - | Yes |
| `MODEL_NAME` | Claude model to use | `claude-sonnet-4.6` | No |
| `MAX_TOKENS` | Max response tokens | `8000` | No |
| `TEMPERATURE` | LLM temperature | `0.7` | No |
| `EXECUTION_TIMEOUT` | Code execution timeout (seconds) | `30` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

---

## Production Considerations

### Security
- ✅ Store API keys in secrets management (AWS Secrets Manager, Google Secret Manager, Azure Key Vault)
- ✅ Use least-privilege IAM roles
- ✅ Enable container security scanning
- ✅ Run as non-root user in production
- ✅ Use read-only file systems where possible

### Monitoring
- Set up logging aggregation (CloudWatch, Stackdriver, Application Insights)
- Monitor execution times and success rates
- Track API usage and costs
- Set up alerts for failures

### Scaling
- For API mode: Use auto-scaling based on queue depth
- For batch processing: Use job queues (AWS Batch, Cloud Tasks)
- Consider rate limiting for API requests

### Cost Optimization
- Use spot instances for non-critical workloads
- Set execution timeouts to prevent runaway costs
- Monitor Anthropic API usage
- Cache common results

---

## Health Checks

Add health check endpoint for production deployments:

```python
# Add to main.py or create health.py
from flask import Flask
app = Flask(__name__)

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

---

## Troubleshooting

### Docker Issues

**Container exits immediately:**
```bash
# Check logs
docker logs code-ai-self-forged

# Run with interactive shell
docker run -it --entrypoint /bin/bash code-ai-self-forged:latest
```

**API key not working:**
```bash
# Verify environment variable is set
docker exec code-ai-self-forged env | grep ANTHROPIC

# Check .env file is present
docker-compose config
```

### Performance Issues

**Slow execution:**
- Increase `EXECUTION_TIMEOUT`
- Check network latency to Anthropic API
- Monitor CPU/memory usage

**Out of memory:**
- Increase container memory limits
- Reduce `MAX_TOKENS`
- Optimize problem complexity

---

## Next Steps

1. ✅ Choose deployment option (Local, Docker, Cloud)
2. ✅ Set up environment variables
3. ✅ Test with sample problems
4. ✅ Run full test suite
5. ✅ Set up monitoring and alerts
6. ✅ Deploy to production

For API service deployment, see [API-DEPLOYMENT.md](API-DEPLOYMENT.md) (coming soon).
