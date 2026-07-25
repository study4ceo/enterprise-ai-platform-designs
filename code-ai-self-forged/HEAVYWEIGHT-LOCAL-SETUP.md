# Heavyweight Local Model Setup Guide

## Overview

Run enterprise-grade AI models locally that rival Claude Opus 4.7 quality. This guide covers setting up 70B+ parameter models on high-end hardware.

## Why Go Heavyweight Local?

**Benefits:**
- ✅ Claude-Opus-level quality without per-token costs
- ✅ Complete data privacy
- ✅ No API rate limits
- ✅ Works offline
- ✅ Cost-effective for high usage (>500M tokens/month)

**Trade-offs:**
- ❌ High upfront hardware cost ($4K-$50K+)
- ❌ Slower than cloud APIs
- ❌ Requires technical setup
- ❌ Higher electricity costs

## Hardware Requirements by Model Size

### 70B Models (Llama 3.1, Qwen 2.5, CodeLlama)

**Option 1: CPU-Only (Not Recommended)**
- CPU: AMD Threadripper or Intel Xeon
- RAM: 80GB+ DDR4/DDR5
- Speed: ~3-8 tokens/sec
- Cost: $2,000-4,000

**Option 2: Dual GPU (Recommended)**
- CPU: AMD Ryzen 9 / Intel i9
- RAM: 32GB+ system RAM
- GPU: 2x NVIDIA RTX 4090 (48GB total VRAM)
- Speed: ~30-60 tokens/sec
- Cost: $4,000-5,000

**Option 3: Single Large GPU**
- GPU: NVIDIA A100 (80GB) or H100 (80GB)
- Speed: ~40-80 tokens/sec
- Cost: $10,000-30,000

### 236B Models (DeepSeek-Coder-V2)

**Multi-GPU Setup (Required)**
- CPU: High-end server CPU
- RAM: 256GB+ system RAM (for safety)
- GPU: 4x RTX 4090 (96GB VRAM) or 2x A100 80GB (160GB)
- Speed: ~10-25 tokens/sec
- Cost: $10,000-50,000

## Step-by-Step Setup

### 1. Prepare Hardware

**NVIDIA GPU Setup:**
```bash
# Install NVIDIA drivers (Windows)
# Download from: https://www.nvidia.com/Download/index.aspx

# Verify GPU recognition
nvidia-smi

# Should show all GPUs
```

**Check available VRAM:**
```bash
nvidia-smi --query-gpu=memory.total --format=csv
```

### 2. Install Ollama

**Windows:**
```bash
winget install Ollama.Ollama

# Or download installer
# https://ollama.ai/download/windows
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Verify installation:**
```bash
ollama --version
```

### 3. Configure Ollama for Multi-GPU

Ollama automatically uses all available GPUs. Verify:

```bash
# Check Ollama can see GPUs
ollama list

# Ollama logs will show GPU utilization
```

### 4. Pull Heavyweight Model

**Llama 3.1 70B (40GB):**
```bash
# This will take 30-60 minutes depending on internet speed
ollama pull llama3.1:70b
```

**Qwen 2.5 Coder 72B (42GB):**
```bash
ollama pull qwen2.5-coder:72b
```

**DeepSeek Coder V2 236B (136GB):**
```bash
# Requires 160GB+ VRAM
ollama pull deepseek-coder-v2:236b
```

**CodeLlama 70B (40GB):**
```bash
ollama pull codellama:70b
```

### 5. Test Model

**Quick test:**
```bash
ollama run llama3.1:70b "Write a Python function to calculate fibonacci"
```

**Performance test:**
```bash
# Monitor GPU usage during inference
watch -n 1 nvidia-smi

# In another terminal
ollama run llama3.1:70b
```

### 6. Configure Code-AI-Self-Forged

**Create heavyweight config:**
```env
# .env.heavyweight
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:70b
OLLAMA_BASE_URL=http://localhost:11434
MAX_TOKENS=8000
TEMPERATURE=0.7
EXECUTION_TIMEOUT=60
LOG_LEVEL=INFO
```

**Run:**
```bash
cp .env.heavyweight .env
python main.py
```

## Performance Optimization

### GPU Memory Optimization

**Reduce context window if OOM:**
```env
MAX_TOKENS=4000  # Reduce from 8000
```

**Enable GPU layers:**
```bash
# In Ollama, automatically optimized
# Check logs for GPU utilization
```

### Multi-GPU Load Balancing

Ollama automatically distributes model across GPUs:

```bash
# Monitor per-GPU usage
nvidia-smi dmon -s u

# Should show balanced usage across GPUs
```

### Increase Inference Speed

**Use quantized models (trade quality for speed):**
```bash
# Q4 quantization (faster, slight quality loss)
ollama pull llama3.1:70b-q4

# Q8 quantization (balanced)
ollama pull llama3.1:70b-q8
```

## Model Quality Comparison

| Model | Parameters | Quality vs Claude | Speed | VRAM |
|-------|------------|-------------------|-------|------|
| **DeepSeek-V2 236B** | 236B | ~95% Opus 4.7 | Slow | 160GB |
| **Qwen 2.5 Coder 72B** | 72B | ~90% Opus 4.7 | Medium | 48GB |
| **Llama 3.1 70B** | 70B | ~85% Opus 4.7 | Medium | 48GB |
| **CodeLlama 70B** | 70B | ~80% Opus 4.7 | Medium | 48GB |
| **Qwen 2.5 32B** | 32B | ~75% Sonnet 4.6 | Fast | 20GB |

*Percentages are approximate for coding tasks*

## Benchmarks

### Code Generation Quality (HumanEval)

| Model | Pass@1 | Comparable To |
|-------|--------|---------------|
| DeepSeek-Coder-V2 236B | 90% | Claude Opus 4.7 |
| Qwen 2.5 Coder 72B | 85% | Claude Sonnet 4.6 |
| Llama 3.1 70B | 75% | GPT-4 |
| CodeLlama 70B | 70% | GPT-3.5 Turbo |

### Speed (Tokens/Second)

**On 2x RTX 4090:**
- Llama 3.1 70B: ~35 tokens/sec
- Qwen 2.5 72B: ~30 tokens/sec

**On 4x RTX 4090:**
- DeepSeek-V2 236B: ~15 tokens/sec

**On Single A100 80GB:**
- Llama 3.1 70B: ~60 tokens/sec

## Cost Analysis

### Hardware Investment Examples

**Option 1: Dual RTX 4090 Build**
- 2x RTX 4090: $3,200
- AMD Ryzen 9 7950X: $550
- 64GB DDR5 RAM: $200
- Motherboard + PSU + Case: $800
- **Total: ~$4,750**
- **Can run: 70B models**

**Option 2: Quad RTX 4090 Server**
- 4x RTX 4090: $6,400
- AMD Threadripper: $2,000
- 128GB DDR5 RAM: $400
- Server motherboard + PSU + Case: $2,000
- **Total: ~$10,800**
- **Can run: 236B models**

**Option 3: Dual A100 80GB**
- 2x A100 80GB: $20,000
- Xeon server: $3,000
- 256GB RAM: $800
- Server components: $2,000
- **Total: ~$25,800**
- **Can run: 236B models optimally**

### Break-Even vs Cloud

**Compared to Claude Opus 4.7 ($15 input, $75 output):**

Assuming 50/50 input/output mix = $45 per 1M tokens

**Dual RTX 4090 ($4,750):**
- Break-even at: ~105M tokens
- If 100M tokens/month: ROI in 1-2 months

**Quad RTX 4090 ($10,800):**
- Break-even at: ~240M tokens
- If 100M tokens/month: ROI in 2-3 months

**Electricity costs:**
- 2x RTX 4090: ~$2-3/day at full load
- 4x RTX 4090: ~$5-7/day at full load

## Docker Setup for Heavyweight

**docker-compose.heavyweight.yml:**
```yaml
version: '3.8'

services:
  ollama-heavy:
    image: ollama/ollama:latest
    container_name: ollama-heavy
    ports:
      - "11434:11434"
    volumes:
      - ollama-heavy-data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped

  code-ai-heavyweight:
    build: .
    container_name: code-ai-heavyweight
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_MODEL=llama3.1:70b
      - OLLAMA_BASE_URL=http://ollama-heavy:11434
      - MAX_TOKENS=8000
      - EXECUTION_TIMEOUT=60
    depends_on:
      - ollama-heavy
    stdin_open: true
    tty: true

volumes:
  ollama-heavy-data:
```

**Run:**
```bash
docker-compose -f docker-compose.heavyweight.yml up -d
docker exec -it ollama-heavy ollama pull llama3.1:70b
docker attach code-ai-heavyweight
```

## Troubleshooting

### Out of Memory (OOM)

```bash
# Reduce context
MAX_TOKENS=4000

# Use quantized model
ollama pull llama3.1:70b-q4

# Check actual VRAM usage
nvidia-smi
```

### Slow Inference

```bash
# Verify GPU usage
nvidia-smi

# Should show high GPU utilization (>80%)
# If low, check Ollama logs for issues
```

### Model Not Using All GPUs

```bash
# Verify Ollama sees all GPUs
ollama list

# Check GPU memory distribution
nvidia-smi

# Should be balanced across GPUs
```

## When to Choose Heavyweight Local

✅ **Choose Heavyweight Local if:**
- Process >100M tokens/month
- Need Opus-level quality
- Require complete privacy
- Have budget for hardware ($5K-$50K)
- Want offline capability
- Can wait for slower inference

❌ **Stick with Cloud if:**
- Occasional usage (<10M tokens/month)
- Need fastest response times
- Don't have powerful hardware
- Want zero setup
- Limited budget (<$5K)

## Next Steps

1. ✅ Verify hardware meets requirements
2. ✅ Install Ollama
3. ✅ Pull heavyweight model
4. ✅ Configure Code-AI-Self-Forged
5. ✅ Run benchmark tests
6. ✅ Monitor GPU utilization
7. ✅ Optimize settings

**Result**: Claude-Opus-level coding AI running completely local!
