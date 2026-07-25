# Offline Mode - Running Without API Keys

## Overview

Run Code-AI-Self-Forged completely offline using local LLMs. No API keys, no cloud services, no external dependencies.

## Option 1: Ollama (Recommended for Offline)

### What is Ollama?

Ollama runs large language models locally on your machine. No API keys, no internet required (after initial model download).

### Setup

**1. Install Ollama:**

Windows:
```bash
# Download from https://ollama.ai/download/windows
# Or use winget
winget install Ollama.Ollama
```

Linux/Mac:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**2. Pull a Model:**
```bash
# Recommended: Llama 3.1 (8B) - Good balance of speed and capability
ollama pull llama3.1:8b

# Or for better performance (requires more RAM):
ollama pull llama3.1:70b

# Or coding-focused model:
ollama pull codellama:34b

# Or latest Qwen coding model:
ollama pull qwen2.5-coder:32b
```

**3. Configure Code-AI-Self-Forged:**

Edit `.env`:
```env
# No API key needed!
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
```

**4. Run:**
```bash
python main.py
```

### Docker with Ollama

**docker-compose.offline.yml:**
```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    restart: unless-stopped

  code-ai-self-forged:
    build: .
    container_name: code-ai-self-forged-offline
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_MODEL=llama3.1:8b
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
    stdin_open: true
    tty: true
    restart: unless-stopped

volumes:
  ollama-data:
```

**Run:**
```bash
# Start Ollama and pull model
docker-compose -f docker-compose.offline.yml up -d ollama
docker exec -it ollama ollama pull llama3.1:8b

# Start Code-AI-Self-Forged
docker-compose -f docker-compose.offline.yml up -d code-ai-self-forged
docker attach code-ai-self-forged-offline
```

---

## Option 2: LM Studio

### Setup

**1. Install LM Studio:**
- Download from: https://lmstudio.ai/
- Free, GUI-based, runs on Windows/Mac/Linux

**2. Download a Model:**
- Open LM Studio
- Search for: `TheBloke/CodeLlama-34B-Instruct-GGUF`
- Or: `deepseek-ai/deepseek-coder-33b-instruct-GGUF`
- Download and load model

**3. Start Local Server:**
- In LM Studio: Server → Start Server
- Default: http://localhost:1234

**4. Configure:**
```env
LLM_PROVIDER=openai_compatible
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=not-needed
```

---

## Option 3: llama.cpp (Most Lightweight)

### Setup

**1. Install llama.cpp:**
```bash
# Clone and build
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Or download pre-built binaries
```

**2. Download Model:**
```bash
# Download GGUF model (e.g., Llama 3.1 8B)
wget https://huggingface.co/...model.gguf
```

**3. Start Server:**
```bash
./server -m model.gguf --host 0.0.0.0 --port 8080
```

**4. Configure:**
```env
LLM_PROVIDER=openai_compatible
OPENAI_BASE_URL=http://localhost:8080/v1
OPENAI_API_KEY=not-needed
```

---

## Model Recommendations

### For Code Generation:

| Model | Size | RAM Needed | Speed | Quality | Notes |
|-------|------|------------|-------|---------|-------|
| **CodeLlama 7B** | 4GB | 8GB | Fast | Good | Quick prototyping |
| **CodeLlama 34B** | 20GB | 32GB | Medium | Excellent | Production ready |
| **Qwen2.5-Coder 32B** | 19GB | 32GB | Medium | Excellent | Top coding model |
| **Llama 3.1 8B** | 5GB | 8GB | Fast | Good | General purpose |
| **Llama 3.1 70B** | 40GB | 64GB | Slow | Excellent | Best reasoning |
| **DeepSeek Coder 33B** | 19GB | 32GB | Medium | Excellent | Strong at code |

### Heavyweight Local Models (High VRAM):

For users with powerful GPUs (RTX 4090, A100, etc.):

| Model | Size | VRAM/RAM | Quality | Speed | Best Use Case |
|-------|------|----------|---------|-------|---------------|
| **Llama 3.1 70B** | 40GB | 48GB+ | ⭐⭐⭐⭐⭐ | Slow | Complex multi-step reasoning |
| **Qwen2.5-Coder 72B** | 42GB | 48GB+ | ⭐⭐⭐⭐⭐ | Slow | Maximum coding quality |
| **DeepSeek-Coder-V2 236B** | 136GB | 160GB+ | ⭐⭐⭐⭐⭐ | V.Slow | Ultimate coding (multi-GPU) |
| **Codestral 22B** | 13GB | 16GB | ⭐⭐⭐⭐ | Medium | Mistral's code specialist |
| **Wizard-Vicuna 70B** | 40GB | 48GB+ | ⭐⭐⭐⭐ | Slow | Strong general reasoning |
| **CodeLlama 70B** | 40GB | 48GB+ | ⭐⭐⭐⭐ | Slow | Meta's largest code model |

**Multi-GPU Setup for 70B+ Models:**
```bash
# Example for 2x RTX 4090 (48GB total)
ollama pull llama3.1:70b

# Ollama automatically uses multiple GPUs if available
```

**Quality Comparison:**
- **236B DeepSeek**: Rivals Claude Opus 4.7, best local option
- **70B+ models**: Comparable to Claude Sonnet 4.6
- **32B models**: Good for most tasks, best price/performance
- **8B models**: Fast, suitable for simple tasks

### For Agentic Reasoning:

- **Llama 3.1 70B** - Best reasoning (requires powerful GPU/CPU)
- **Qwen2.5 32B** - Good balance
- **Llama 3.1 8B** - Fastest, still capable

---

## Performance Comparison

### Cloud (Anthropic):
- ✅ Highest quality
- ✅ Fastest (no local compute)
- ❌ Requires API key
- ❌ Costs money ($3-15/M tokens)
- ❌ Requires internet

### Local (Ollama/llama.cpp):
- ✅ Completely free
- ✅ No API key needed
- ✅ Works offline
- ✅ Privacy - data stays local
- ❌ Requires powerful hardware
- ❌ Slower than cloud
- ❌ Lower quality for complex tasks

---

## Hardware Requirements

### Minimum (8B models):
- **CPU**: Modern multi-core (AMD Ryzen 5, Intel i5+)
- **RAM**: 8GB system RAM
- **GPU**: Optional (NVIDIA with CUDA speeds up significantly)
- **Storage**: 10GB

### Recommended (32-34B models):
- **CPU**: High-end (AMD Ryzen 9, Intel i9)
- **RAM**: 32GB system RAM
- **GPU**: NVIDIA RTX 3090 / 4090 (24GB VRAM) - Highly recommended
- **Storage**: 50GB

### Optimal (70B models):
- **CPU**: Threadripper / Xeon
- **RAM**: 64GB+ system RAM
- **GPU**: 2x RTX 4090 (48GB total VRAM) or 1x A100 (80GB)
- **Storage**: 100GB

### Ultimate (236B models):
- **CPU**: High-end server CPU
- **RAM**: 192GB+ system RAM
- **GPU**: 4x A100 (160GB+ total VRAM) or 8x RTX 4090 (192GB total)
- **Storage**: 300GB
- **Budget**: $50,000+ for hardware

---

## GPU Acceleration

### With NVIDIA GPU:

**Ollama (auto-detects GPU):**
```bash
# Ollama automatically uses GPU if available
ollama pull llama3.1:8b
ollama run llama3.1:8b
```

**llama.cpp with CUDA:**
```bash
# Build with CUDA support
make LLAMA_CUDA=1

# Run with GPU layers
./server -m model.gguf -ngl 35 --host 0.0.0.0
```

### Performance Boost:
- **CPU only (8B)**: ~10-20 tokens/sec
- **GPU (8B)**: ~50-100+ tokens/sec
- **GPU (70B)**: ~10-30 tokens/sec
- **Multi-GPU (70B)**: ~30-80 tokens/sec
- **Multi-GPU (236B)**: ~5-20 tokens/sec

**GPU significantly faster** for all model sizes. Investment in GPU pays off quickly for frequent use.

---

## Hybrid Mode (Best of Both)

Use local LLM for development/testing, cloud for production:

```python
# In config.py
if os.getenv("ENVIRONMENT") == "production":
    LLM_PROVIDER = "anthropic"
else:
    LLM_PROVIDER = "ollama"
```

---

## Cost Comparison

### Cloud (per 1M tokens):
- **Anthropic Claude Sonnet 4.6**: $3 input / $15 output
- **Anthropic Claude Opus 4.7**: $15 input / $75 output
- **OpenAI GPT-4**: $10-30

### Local (one-time + ongoing):
- **Hardware Investment**:
  - 8B models: $0 (existing PC) to $1,500 (RTX 4070)
  - 32B models: $2,000 (RTX 4090)
  - 70B models: $4,000 (2x RTX 4090)
  - 236B models: $50,000+ (4x A100 or 8x RTX 4090)
- **Electricity**: 
  - 8B on CPU: ~$0.50/day
  - 70B on 2x GPU: ~$2-3/day (24/7 usage)
  - 236B multi-GPU: ~$5-10/day
- **Free after setup** (no per-token costs)

**Break-even Analysis:**
- **8B models**: Break-even after ~50-100M tokens
- **32B models**: Break-even after ~100-200M tokens  
- **70B models**: Break-even after ~200-500M tokens
- **236B models**: Break-even after 2-5B tokens

**For heavy users (>100M tokens/month)**: Local heavyweight models become cost-effective despite high upfront investment.

---

## Which Should You Use?

### Use Cloud (Anthropic) if:
- ✅ You need highest quality
- ✅ You want fast responses
- ✅ You don't have powerful hardware
- ✅ You process < 100M tokens/month

### Use Local (Ollama) if:
- ✅ You have powerful hardware (16GB+ RAM, preferably GPU)
- ✅ You need complete privacy
- ✅ You want to work offline
- ✅ You process > 100M tokens/month
- ✅ You don't want to manage API keys
- ✅ **You have high-end GPU(s) for heavyweight models (70B+)**
- ✅ **You want Claude-Opus-level quality without cloud costs**

### Use Hybrid if:
- ✅ You want flexibility
- ✅ Different use cases (dev vs prod)
- ✅ Cost optimization

---

## Next Steps

1. ✅ Choose your approach (Cloud vs Local vs Hybrid)
2. ✅ Install Ollama if going local
3. ✅ Pull appropriate model
4. ✅ Update `.env` configuration
5. ✅ Test with simple problem
6. ✅ Run test suites

**For truly zero API keys**: Use Ollama with local models!
