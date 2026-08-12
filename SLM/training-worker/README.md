# Training Worker

GPU-powered worker that processes fine-tuning jobs from Redis queue.

## Features

✅ **LoRA Training** - Parameter-efficient fine-tuning  
✅ **QLoRA Training** - 4-bit quantized training (50% memory savings)  
✅ **Redis Integration** - Job queue consumer  
✅ **Database Updates** - Real-time progress tracking  
✅ **GPU Monitoring** - Memory and utilization tracking  
✅ **Checkpointing** - Automatic checkpoint saving  
✅ **WandB Integration** - Optional experiment tracking  

## Architecture

```
Redis Queue → Training Worker → Database Updates
                    ↓
            LoRA/QLoRA Trainer
                    ↓
            Fine-tuned Model
```

## Files

- **worker.py** - Main worker process (Redis consumer)
- **lora_trainer.py** - LoRA fine-tuning implementation
- **qlora_trainer.py** - QLoRA (4-bit) implementation
- **config.py** - Configuration management
- **database.py** - Database models
- **requirements.txt** - Python dependencies
- **Dockerfile** - CUDA-enabled container

## Configuration

Key environment variables:

```bash
# Worker
WORKER_ID=worker-1

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/slm_platform

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_QUEUE_NAME=training_jobs

# Training Defaults
DEFAULT_LORA_RANK=16
DEFAULT_LORA_ALPHA=32
DEFAULT_LEARNING_RATE=0.0002
DEFAULT_NUM_EPOCHS=3
DEFAULT_BATCH_SIZE=4

# WandB (optional)
WANDB_ENABLED=true
WANDB_PROJECT=slm-training
WANDB_API_KEY=your-api-key
```

## Usage

### Docker
```bash
docker-compose up training-worker
```

### Local Development
```bash
cd training-worker
pip install -r requirements.txt
python worker.py
```

## Training Methods

### LoRA (Low-Rank Adaptation)
- Standard precision training
- ~1-2% of parameters trainable
- Fast and efficient
- Good for most use cases

### QLoRA (Quantized LoRA)
- 4-bit quantized base model
- 50% less GPU memory
- Slightly slower than LoRA
- Best for large models on consumer GPUs

## GPU Requirements

| Model Size | LoRA Memory | QLoRA Memory | Recommended GPU |
|------------|-------------|--------------|-----------------|
| 1B params  | 8 GB        | 4 GB         | RTX 3060 12GB   |
| 3B params  | 16 GB       | 8 GB         | RTX 3090 24GB   |
| 7B params  | 32 GB       | 16 GB        | RTX 4090 24GB   |
| 13B params | 48 GB       | 24 GB        | A100 40GB       |

## Training Flow

1. **Job Submitted** - Backend pushes job to Redis queue
2. **Worker Picks Up** - Worker reads job from queue
3. **Load Model** - Base model loaded from disk
4. **Prepare Dataset** - Tokenization and preprocessing
5. **Train** - LoRA/QLoRA training loop
6. **Save Checkpoint** - Adapter weights saved
7. **Update Database** - Final metrics recorded

## Monitoring

### Logs
```bash
# View worker logs
docker logs -f slm-training-worker

# View training metrics
docker exec slm-training-worker python -c "import torch; print(torch.cuda.memory_summary())"
```

### Database
```sql
-- Check job status
SELECT job_id, name, status, progress_percent FROM training_jobs ORDER BY created_at DESC;

-- View training metrics
SELECT * FROM training_metrics WHERE job_id = 'job-xxx' ORDER BY step;
```

### WandB
If enabled, view real-time metrics at: https://wandb.ai/your-project/slm-training

## Error Handling

The worker handles errors gracefully:

- **Model not found** - Job marked as failed
- **OOM errors** - Logged with memory stats
- **Dataset errors** - Detailed error message saved
- **Training crashes** - Job status updated to failed

All errors are logged to database with stack traces.

## Performance Tips

### Memory Optimization
- Use QLoRA for large models
- Enable gradient checkpointing
- Reduce batch size
- Use mixed precision (bf16)

### Speed Optimization
- Increase batch size if memory allows
- Use gradient accumulation
- Enable Flash Attention
- Use better transformer backend

### Quality Optimization
- Use validation split for early stopping
- Tune learning rate
- Increase LoRA rank for complex tasks
- Use warmup steps

## Troubleshooting

### Out of Memory
```bash
# Reduce batch size or use QLoRA
DEFAULT_BATCH_SIZE=2
ENABLE_GRADIENT_CHECKPOINTING=true
```

### Slow Training
```bash
# Increase batch size with gradient accumulation
DEFAULT_BATCH_SIZE=8
DEFAULT_GRADIENT_ACCUMULATION_STEPS=2
```

### Poor Quality
```bash
# Increase LoRA rank and training epochs
DEFAULT_LORA_RANK=32
DEFAULT_NUM_EPOCHS=5
```

## Development

### Running Tests
```bash
pytest tests/
```

### Debugging
```bash
# Enable debug logging
LOG_LEVEL=DEBUG python worker.py
```

### Adding New Training Methods
1. Create new trainer class (e.g., `dora_trainer.py`)
2. Add method to `execute_training_job()` in `worker.py`
3. Update database schema if needed

## License

MIT License - see main project README
