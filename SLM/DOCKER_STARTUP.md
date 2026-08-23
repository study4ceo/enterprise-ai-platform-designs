# 🐳 Docker Startup Guide

How to start the SLM Platform with Docker Compose.

---

## ⚠️ Important Note

The **frontend is not built yet**, so the frontend service is commented out in `docker-compose.yml`.

The platform will start with:
- ✅ PostgreSQL (database)
- ✅ Redis (job queue)
- ✅ MinIO (storage)
- ✅ Backend API (FastAPI)
- ✅ Training Worker (GPU)
- ❌ Frontend (not built)

---

## 🚀 Quick Start

### 1. Setup Environment
```bash
cd D:\code_ai\code\project-designs\SLM
cp .env.example .env
```

### 2. Start All Services
```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- Redis on port 6379
- MinIO on ports 9000 (API) and 9001 (Console)
- Backend on port 8000
- Training Worker (background)

### 3. Verify Status
```bash
# Check all services
docker-compose ps

# Should see all services as "Up"
```

### 4. Test API
```bash
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "healthy",
  "redis": "healthy",
  "minio": "healthy",
  "gpu_available": true,
  "gpu_count": 1
}
```

---

## 🔧 Service Details

### PostgreSQL
- **Port**: 5432
- **Database**: slm_platform
- **User**: slm_user
- **Password**: slm_password

Access:
```bash
docker exec -it slm-postgres psql -U slm_user -d slm_platform
```

### Redis
- **Port**: 6379
- **Persistence**: Enabled

Access:
```bash
docker exec -it slm-redis redis-cli
```

### MinIO
- **API Port**: 9000
- **Console Port**: 9001
- **Username**: minioadmin
- **Password**: minioadmin123

Access Console: http://localhost:9001

### Backend API
- **Port**: 8000
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### Training Worker
- **No direct port** - Consumes jobs from Redis
- **View logs**: `docker logs -f slm-training-worker`

---

## 📊 Common Commands

### Start Services
```bash
# Start all
docker-compose up -d

# Start specific service
docker-compose up -d backend

# Start without worker (for testing)
docker-compose up -d postgres redis minio backend
```

### Stop Services
```bash
# Stop all
docker-compose down

# Stop but keep data
docker-compose stop

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f training-worker

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Check Status
```bash
# Service status
docker-compose ps

# Resource usage
docker stats

# Detailed info
docker-compose logs --tail=50
```

---

## 🔍 Troubleshooting

### GPU Not Available

**Problem**: Backend shows `gpu_available: false`

**Solution**:
```bash
# Check NVIDIA driver
nvidia-smi

# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# Install NVIDIA Container Toolkit if needed
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

### Port Already in Use

**Problem**: `Error: port 8000 already in use`

**Solution**:
```bash
# Find what's using the port
netstat -ano | findstr :8000

# Kill the process or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Service Won't Start

**Problem**: Service keeps restarting

**Solution**:
```bash
# Check logs
docker-compose logs backend

# Check for errors in last 50 lines
docker-compose logs --tail=50 backend

# Try rebuilding
docker-compose build backend
docker-compose up -d backend
```

### Database Connection Failed

**Problem**: Backend can't connect to database

**Solution**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify connection
docker exec -it slm-postgres psql -U slm_user -d slm_platform -c "SELECT 1;"
```

### Out of Memory

**Problem**: Training worker crashes with OOM

**Solution**:
Edit `.env`:
```bash
DEFAULT_BATCH_SIZE=1
ENABLE_GRADIENT_CHECKPOINTING=true
# Use QLoRA instead of LoRA (in training request)
```

---

## 🛠️ Development Mode

### Hot Reload

Both backend and worker support hot reload:
- Backend: Uses `--reload` flag
- Worker: Mount code as volume

Changes to Python files will auto-reload.

### Debugging

**Backend**:
```bash
# Stop container
docker-compose stop backend

# Run manually with debugging
docker-compose run --rm backend python -m pdb main.py
```

**Worker**:
```bash
# View detailed logs
docker-compose logs -f training-worker

# Check GPU usage
docker exec slm-training-worker nvidia-smi
```

---

## 📦 Building Images

### Rebuild After Code Changes
```bash
# Rebuild all
docker-compose build

# Rebuild specific service
docker-compose build backend

# Rebuild without cache
docker-compose build --no-cache backend
```

### Pull Latest Images
```bash
# Update base images
docker-compose pull
```

---

## 🧹 Cleanup

### Remove Stopped Containers
```bash
docker-compose down
```

### Remove All Data (⚠️ Destructive)
```bash
# Remove containers, networks, and volumes
docker-compose down -v

# Clean up Docker system
docker system prune -a
```

### Free Disk Space
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Check space
docker system df
```

---

## 🔐 Security Notes

### Default Credentials

**Change these in production**:
```bash
# PostgreSQL
POSTGRES_PASSWORD=slm_password

# MinIO
MINIO_ROOT_PASSWORD=minioadmin123

# JWT Secret (in .env)
JWT_SECRET=change-this-to-a-secure-random-string
```

### Network

All services are on `slm-network`. To expose services:
```yaml
# In docker-compose.yml
networks:
  default:
    name: slm-network
    driver: bridge
```

---

## 📈 Resource Requirements

### Minimum
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 50 GB
- **GPU**: Optional (for training)

### Recommended
- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Disk**: 200 GB SSD
- **GPU**: NVIDIA RTX 3090/4090

---

## ✅ Verification Checklist

After starting, verify:

- [ ] All 5 services are running: `docker-compose ps`
- [ ] Backend health check passes: `curl http://localhost:8000/health`
- [ ] Database has tables: `docker exec -it slm-postgres psql -U slm_user -d slm_platform -c "\dt"`
- [ ] Redis is responsive: `docker exec -it slm-redis redis-cli ping`
- [ ] MinIO console accessible: http://localhost:9001
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] GPU detected (if available): Check health endpoint

---

## 🎯 Next Steps

Once all services are running:

1. **Explore API**: http://localhost:8000/docs
2. **Upload dataset**: See QUICK_START.md
3. **Start training**: POST to `/api/v1/training/start`
4. **Run inference**: POST to `/api/v1/chat`

---

## 📞 Getting Help

**Service logs**:
```bash
docker-compose logs -f
```

**Health status**:
```bash
curl http://localhost:8000/health | jq
```

**Documentation**:
- QUICK_START.md
- BUILD_STATUS_UPDATE.md
- FOLDERS.md

---

**Your platform is ready to use! 🚀**
