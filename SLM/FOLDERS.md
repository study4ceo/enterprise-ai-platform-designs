# 📁 SLM Platform - Folder Structure

Complete guide to the project directory structure.

---

## 📊 Overview

```
SLM/
├── 📖 Documentation Files          # Project docs (15,000+ lines)
├── 🐳 Docker Configuration         # Deployment files
├── 🔧 backend/                     # FastAPI backend (COMPLETE)
├── 🎓 training-worker/             # Training service (COMPLETE)
├── 🎨 frontend/                    # Next.js UI (NOT BUILT)
├── 💾 models/                      # Model storage
├── 📊 datasets/                    # Training data
└── 💿 checkpoints/                 # Training checkpoints
```

---

## 📖 Root Level Files

### Documentation
- **README.md** - Main project overview
- **QUICK_START.md** - 5-minute setup guide
- **BUILD_STATUS_UPDATE.md** - Current build status
- **IMPLEMENTATION_SUMMARY.md** - Technical deep dive
- **PROJECT_PROPOSAL.md** - Original vision
- **LLM_vs_SLM_COMPARISON.md** - Why SLMs? (10,000+ words)
- **FOLDERS.md** - This file

### Configuration
- **docker-compose.yml** - Service orchestration
- **init-db.sql** - Database schema (10 tables)
- **.env.example** - Environment variables template

---

## 🔧 backend/ (Backend API - COMPLETE ✅)

**Status**: 100% Complete, Production-Ready  
**Lines**: 1,800+  

```
backend/
├── main.py              # FastAPI app with 20+ endpoints
├── model_manager.py     # Model loading & inference engine
├── config.py            # Settings management
├── database.py          # SQLAlchemy models (10 tables)
├── schemas.py           # Pydantic request/response schemas
├── requirements.txt     # Python dependencies
├── Dockerfile           # CUDA-enabled container
└── README.md            # Backend documentation
```

### Key Components

**main.py** (450 lines)
- REST API endpoints
- Model management
- Dataset management
- Training job orchestration
- Inference endpoints
- Dashboard stats

**model_manager.py** (400 lines)
- LRU model caching
- Model loading (standard + PEFT)
- Quantization (int4/int8/fp16)
- Chat completion
- Text generation
- GPU/CPU inference

**database.py** (300 lines)
- 10 SQLAlchemy models
- Async database operations
- Relationships and indexes

**schemas.py** (400 lines)
- 40+ Pydantic models
- Request validation
- Response serialization

---

## 🎓 training-worker/ (Training Worker - COMPLETE ✅)

**Status**: 100% Complete, Functional  
**Lines**: 2,200+  

```
training-worker/
├── worker.py            # Main orchestration worker
├── lora_trainer.py      # LoRA fine-tuning implementation
├── qlora_trainer.py     # QLoRA (4-bit) implementation
├── config.py            # Worker configuration
├── database.py          # Simplified database models
├── requirements.txt     # ML dependencies
├── Dockerfile           # CUDA 12.1 container
└── README.md            # Worker documentation
```

### Key Components

**worker.py** (400 lines)
- Redis job queue consumer
- Job orchestration
- Database status updates
- Error handling
- GPU monitoring

**lora_trainer.py** (500 lines)
- LoRA implementation using PEFT
- Dataset preprocessing
- Training loop
- Checkpoint management
- WandB integration

**qlora_trainer.py** (550 lines)
- 4-bit quantization (BitsAndBytes)
- NF4 quantization
- 50% memory savings
- Same API as LoRA

---

## 🎨 frontend/ (Frontend Dashboard - NOT BUILT ⏳)

**Status**: 0% Complete, Placeholder Only  
**Lines**: 0  

```
frontend/
└── README.md            # Status: NOT BUILT YET
```

### Planned Structure

```
frontend/
├── app/
│   ├── page.tsx                  # Home dashboard
│   ├── models/
│   │   └── page.tsx              # Model management
│   ├── datasets/
│   │   └── page.tsx              # Dataset management
│   ├── training/
│   │   └── page.tsx              # Training interface
│   └── playground/
│       └── page.tsx              # Chat playground
├── components/
│   ├── ui/                       # shadcn/ui components
│   └── custom/                   # Custom components
├── lib/
│   ├── api.ts                    # API client
│   └── utils.ts                  # Utilities
├── package.json
├── next.config.js
└── tailwind.config.js
```

**Technology**:
- Next.js 14 (App Router)
- Tailwind CSS
- shadcn/ui
- React Query
- Zustand

**Timeline**: 3-4 days to complete

**Note**: Frontend service is commented out in `docker-compose.yml`

---

## 💾 models/ (Model Storage)

**Purpose**: Store downloaded language models  
**Size**: 2-14 GB per model  

```
models/
├── llama-3.2-1b/
│   ├── config.json
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   └── pytorch_model.bin
├── llama-3.2-3b/
├── mistral-7b/
└── ...
```

### Usage

Models are stored here when:
1. Downloaded via API: `POST /api/v1/models/download`
2. Manually copied
3. Mounted from host in Docker

### Notes

- Base models cached from HuggingFace
- Can use symlinks to save space
- Fine-tuned models stored separately
- See `models/README.md` for details

---

## 📊 datasets/ (Training Datasets)

**Purpose**: Store training datasets  
**Size**: 10 MB - 10 GB per dataset  

```
datasets/
├── dataset-001.json
├── dataset-002.csv
├── my-custom-data.jsonl
└── ...
```

### Supported Formats

**JSON/JSONL**:
```json
[
  {"text": "Example 1"},
  {"instruction": "Question?", "output": "Answer"}
]
```

**CSV**:
```csv
text
"Example 1"
"Example 2"
```

### Usage

Upload datasets via:
1. API: `POST /api/v1/datasets/upload`
2. Manual copy
3. Mount from host

### Notes

- Auto-preprocessed during training
- Tokenized on-the-fly
- Train/validation split automatic
- See `datasets/README.md` for details

---

## 💿 checkpoints/ (Training Checkpoints)

**Purpose**: Store training checkpoints and fine-tuned models  
**Size**: 200 MB - 1 GB per checkpoint  

```
checkpoints/
├── job-abc12345/
│   ├── checkpoint-500/
│   │   ├── adapter_model.bin       # LoRA weights
│   │   ├── adapter_config.json     # Configuration
│   │   └── optimizer.pt            # Optimizer state
│   ├── checkpoint-1000/
│   └── final/                      # Final model
│       ├── adapter_model.bin
│       └── adapter_config.json
└── job-def67890/
```

### Contents

- **Adapter weights**: LoRA/QLoRA adapters (~100-500 MB)
- **Configuration**: LoRA config, training args
- **Optimizer state**: For resuming training
- **Trainer state**: Step count, best metrics

### Usage

- Auto-created during training
- Saved every N steps
- Keeps last 3 checkpoints
- Final model saved on completion

### Notes

- Only LoRA adapters stored (not full model)
- Need base model + adapter to use
- Can be backed up to MinIO
- See `checkpoints/README.md` for details

---

## 🐳 Docker Volumes

Created by docker-compose:

```
volumes/
├── postgres_data/       # PostgreSQL database
├── redis_data/          # Redis persistence
├── minio_data/          # MinIO object storage
└── model_cache/         # HuggingFace cache
```

These are managed by Docker and stored in Docker's volume directory.

---

## 📏 Size Breakdown

| Directory | Size Range | Notes |
|-----------|------------|-------|
| `backend/` | 1 MB | Code only |
| `training-worker/` | 1 MB | Code only |
| `frontend/` | 0 MB | Not built |
| `models/` | 0-100 GB | Depends on models |
| `datasets/` | 0-50 GB | Depends on data |
| `checkpoints/` | 0-100 GB | Grows with training |
| Docker volumes | 1-10 GB | Database + cache |

**Recommended Disk Space**: 50-200 GB

---

## 🔍 Finding Files

### Code Files
```bash
# Backend
ls backend/*.py

# Training worker
ls training-worker/*.py

# Configuration
ls *.yml *.sql
```

### Documentation
```bash
ls *.md
```

### Data Directories
```bash
# Check what's stored
ls models/
ls datasets/
ls checkpoints/
```

---

## 🚀 Usage

### Start Platform
```bash
# All services (except frontend)
docker-compose up -d

# Check what's running
docker-compose ps
```

### Access Data
```bash
# Models
docker exec -it slm-backend ls /models

# Datasets
docker exec -it slm-backend ls /datasets

# Checkpoints
docker exec -it slm-training-worker ls /checkpoints
```

### View Logs
```bash
# Backend logs
docker logs slm-backend

# Worker logs
docker logs slm-training-worker
```

---

## 📝 Summary

### Complete ✅
- `backend/` - Full API implementation
- `training-worker/` - LoRA/QLoRA trainers
- Documentation - 15,000+ lines
- Configuration - Docker setup

### Data Directories (Ready) ✅
- `models/` - For model storage
- `datasets/` - For training data
- `checkpoints/` - For training outputs

### Not Built Yet ⏳
- `frontend/` - Web dashboard

---

## 🎯 Next Steps

1. **Use backend API** - Everything works via REST API
2. **Upload models** - Manually or via API
3. **Add datasets** - Copy or upload
4. **Start training** - API will create checkpoints
5. **Build frontend** - When ready (3-4 days)

---

**All folders are now in place and documented!**

See individual README files in each directory for more details.
