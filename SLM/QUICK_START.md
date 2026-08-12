# 🚀 SLM Platform - Quick Start Guide

Get your local SLM training platform running in 5 minutes!

---

## Prerequisites

- Docker & Docker Compose
- NVIDIA GPU with CUDA support (optional but recommended)
- 20+ GB free disk space
- 8+ GB RAM

---

## 1. Clone & Setup (2 minutes)

```bash
cd D:\code_ai\code\project-designs\SLM

# Copy environment file
cp .env.example .env

# (Optional) Edit .env to customize settings
```

---

## 2. Start Services (3 minutes)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

You should see:
- ✅ slm-postgres (PostgreSQL)
- ✅ slm-redis (Redis)
- ✅ slm-minio (MinIO)
- ✅ slm-backend (API)
- ✅ slm-training-worker (GPU worker)

---

## 3. Verify Installation

### Check API Health
```bash
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "healthy",
  "gpu_available": true
}
```

### Check Database
```bash
docker exec -it slm-postgres psql -U slm_user -d slm_platform -c "SELECT COUNT(*) FROM models;"
```

Should show 5 pre-loaded models.

### Check API Documentation
Open in browser: http://localhost:8000/docs

---

## 4. Your First Training Job

### Step 1: Upload a Dataset

Create a simple dataset (`my_dataset.json`):
```json
[
  {"text": "The capital of France is Paris."},
  {"text": "Python is a programming language."},
  {"text": "The Earth revolves around the Sun."}
]
```

Upload it:
```bash
curl -X POST http://localhost:8000/api/v1/datasets/upload \
  -F "file=@my_dataset.json" \
  -F "name=My First Dataset" \
  -F "description=Test dataset"
```

### Step 2: Start Training

```bash
curl -X POST http://localhost:8000/api/v1/training/start \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Training",
    "model_id": "llama-3.2-1b",
    "dataset_id": "dataset-001",
    "training_method": "qlora",
    "lora_config": {
      "rank": 8,
      "alpha": 16,
      "dropout": 0.05
    },
    "training_config": {
      "num_epochs": 1,
      "batch_size": 2,
      "learning_rate": 0.0002
    }
  }'
```

### Step 3: Monitor Progress

```bash
# Get job ID from previous response
export JOB_ID="job-xxxxxxxx"

# Check status
curl http://localhost:8000/api/v1/training/$JOB_ID

# Watch logs
docker logs -f slm-training-worker
```

---

## 5. Run Inference

### Chat Completion
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "llama-3.2-1b",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "max_tokens": 50
  }'
```

### Text Generation
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "llama-3.2-1b",
    "prompt": "Once upon a time, in a land far away",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

---

## 6. View Dashboard Stats

```bash
curl http://localhost:8000/api/v1/dashboard/stats | jq
```

---

## Common Commands

### Start/Stop Services
```bash
# Start all
docker-compose up -d

# Stop all
docker-compose down

# Restart service
docker-compose restart backend

# View logs
docker-compose logs -f backend
docker-compose logs -f training-worker
```

### Database Operations
```bash
# Access database
docker exec -it slm-postgres psql -U slm_user -d slm_platform

# List models
docker exec -it slm-postgres psql -U slm_user -d slm_platform -c "SELECT model_id, name FROM models;"

# View training jobs
docker exec -it slm-postgres psql -U slm_user -d slm_platform -c "SELECT job_id, name, status FROM training_jobs;"
```

### Redis Operations
```bash
# Access Redis
docker exec -it slm-redis redis-cli

# Check queue length
docker exec -it slm-redis redis-cli LLEN training_jobs

# View queue (without removing)
docker exec -it slm-redis redis-cli LRANGE training_jobs 0 -1
```

### MinIO Storage
Open in browser: http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin123`

---

## Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA driver
nvidia-smi

# Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### Out of Memory
Edit `.env`:
```bash
# Reduce batch size
DEFAULT_BATCH_SIZE=1

# Enable gradient checkpointing
ENABLE_GRADIENT_CHECKPOINTING=true

# Use QLoRA instead of LoRA
# (Already default, but confirm in training request)
```

### Training Not Starting
```bash
# Check worker logs
docker logs slm-training-worker

# Check Redis queue
docker exec -it slm-redis redis-cli LLEN training_jobs

# Restart worker
docker-compose restart training-worker
```

### API Not Responding
```bash
# Check logs
docker logs slm-backend

# Check health
curl http://localhost:8000/health

# Restart
docker-compose restart backend
```

---

## API Examples

### List All Models
```bash
curl http://localhost:8000/api/v1/models
```

### List Datasets
```bash
curl http://localhost:8000/api/v1/datasets
```

### List Training Jobs
```bash
curl http://localhost:8000/api/v1/training
```

### Get Training Metrics
```bash
curl http://localhost:8000/api/v1/training/$JOB_ID/metrics
```

### Cancel Training
```bash
curl -X POST http://localhost:8000/api/v1/training/$JOB_ID/cancel
```

---

## Configuration

Key settings in `.env`:

```bash
# API
API_PORT=8000

# Training
DEFAULT_LEARNING_RATE=0.0002
DEFAULT_BATCH_SIZE=4
DEFAULT_NUM_EPOCHS=3

# LoRA
DEFAULT_LORA_RANK=16
DEFAULT_LORA_ALPHA=32

# GPU
CUDA_VISIBLE_DEVICES=0
MAX_GPU_MEMORY_FRACTION=0.9

# Monitoring
WANDB_ENABLED=false
WANDB_API_KEY=your-key-here
```

---

## Next Steps

1. **Explore API** - Visit http://localhost:8000/docs
2. **Upload Real Data** - Add your training datasets
3. **Fine-tune Models** - Train on your specific use case
4. **Run Inference** - Use your trained models
5. **Monitor Progress** - Watch training metrics

---

## Getting Help

- **Documentation**: Read `BUILD_STATUS_UPDATE.md`
- **Implementation**: See `IMPLEMENTATION_SUMMARY.md`
- **API Docs**: http://localhost:8000/docs
- **Logs**: `docker-compose logs -f`

---

## What's Next?

- ✅ Backend is production-ready
- ✅ Training worker is functional
- ⏳ Frontend dashboard (coming soon)
- ⏳ Model evaluation tools
- ⏳ Batch inference API
- ⏳ Model merging utilities

---

**You're all set! Start training your SLMs locally! 🎉**

```bash
# Quick test
curl http://localhost:8000/health && echo "✅ Platform is running!"
```
