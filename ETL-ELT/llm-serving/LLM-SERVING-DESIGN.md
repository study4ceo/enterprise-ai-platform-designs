# LLM Serving Architecture: Managed vs Self-Hosted

## Executive Summary

This document covers comprehensive LLM (Large Language Model) serving strategies for production environments, comparing managed services (AWS Bedrock, Azure OpenAI) with self-hosted solutions (vLLM, TGI, Triton), and providing deployment architectures for both.

**Key Decision Factors:**
- **Cost**: Managed = predictable per-token pricing; Self-hosted = infrastructure cost at scale
- **Throughput**: vLLM = 20-30x faster than HuggingFace Transformers
- **Control**: Self-hosted = full control; Managed = limited customization
- **Maintenance**: Managed = zero ops; Self-hosted = GPU cluster management

---

## Table of Contents

1. [Overview](#overview)
2. [Managed LLM Services](#managed-llm-services)
3. [Self-Hosted Solutions](#self-hosted-solutions)
4. [vLLM Deep Dive](#vllm-deep-dive)
5. [Comparison Matrix](#comparison-matrix)
6. [Architecture Patterns](#architecture-patterns)
7. [Cost Analysis](#cost-analysis)
8. [Deployment Guides](#deployment-guides)
9. [Monitoring & Optimization](#monitoring--optimization)
10. [Decision Framework](#decision-framework)

---

## Overview

### LLM Serving Landscape

```
┌─────────────────────────────────────────────────────────────────┐
│                    LLM Serving Options                          │
└─────────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
     ┌──────▼──────┐                 ┌──────▼──────┐
     │   Managed   │                 │ Self-Hosted │
     │  Services   │                 │  Solutions  │
     └──────┬──────┘                 └──────┬──────┘
            │                               │
   ┌────────┴────────┐           ┌──────────┴──────────┐
   │                 │           │                     │
┌──▼───┐    ┌───────▼──┐    ┌───▼────┐    ┌─────────▼────┐
│Bedrock│   │Azure OAI│    │  vLLM  │    │  TGI/Triton  │
│Claude │   │  GPT-4  │    │PagedAttn│   │   TensorRT   │
│Titan  │   │         │    │Cont.Batch│   │              │
└───────┘   └─────────┘    └────────┘    └──────────────┘
```

### When to Use Each

| Scenario | Recommended Solution |
|----------|---------------------|
| **Prototype/MVP** | AWS Bedrock (fastest time-to-market) |
| **Production < 1M requests/month** | Managed services (lower TCO) |
| **Production > 10M requests/month** | vLLM (significant cost savings) |
| **Custom fine-tuned models** | vLLM (full control) |
| **Multi-region, high availability** | Hybrid (Bedrock + vLLM failover) |
| **Data sovereignty requirements** | Self-hosted (on-premises/VPC) |
| **Real-time, low-latency** | vLLM with GPU (< 50ms p99) |

---

## Managed LLM Services

### AWS Bedrock

**Overview**: Fully managed service providing access to foundation models from Anthropic (Claude), AI21, Cohere, Meta, Stability AI, and Amazon.

#### Features
- ✅ **Zero infrastructure** - No GPU management
- ✅ **Enterprise security** - AWS IAM, VPC endpoints
- ✅ **Multiple models** - Claude 3, Titan, Llama 2
- ✅ **Pay-per-use** - No upfront costs
- ✅ **Automatic scaling** - Handle traffic spikes
- ⚠️ **Model limitations** - Can't use custom fine-tuned models
- ⚠️ **Cost at scale** - Expensive for high volumes

#### Pricing (as of 2026)

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| Claude 3 Opus | $15.00 | $75.00 |
| Claude 3 Sonnet | $3.00 | $15.00 |
| Claude 3 Haiku | $0.25 | $1.25 |
| Titan Text G1 | $0.13 | $0.17 |
| Llama 2 70B | $0.265 | $0.35 |

**Monthly Cost Example** (10M tokens input + 2M output):
- Claude 3 Sonnet: $30,000 + $30,000 = **$60,000/month**
- Claude 3 Haiku: $2,500 + $2,500 = **$5,000/month**

#### Architecture

```python
# AWS Bedrock with LangChain
import boto3
from langchain_community.llms import Bedrock
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Initialize client
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)

# Create LLM
llm = Bedrock(
    client=bedrock_client,
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs={
        "max_tokens": 2048,
        "temperature": 0.7,
        "top_p": 0.9,
    },
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

# Invoke
response = llm.invoke("Explain quantum computing")
```

### Azure OpenAI Service

**Overview**: Microsoft's managed service for OpenAI models (GPT-4, GPT-3.5, DALL-E, Whisper).

#### Features
- ✅ **GPT-4 access** - Latest OpenAI models
- ✅ **Enterprise compliance** - SOC 2, HIPAA, ISO 27001
- ✅ **Private networking** - VNET integration
- ✅ **Azure integration** - Seamless with Azure services
- ⚠️ **Waitlist required** - Not immediately available
- ⚠️ **OpenAI only** - No Claude or other models

#### Pricing

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| GPT-4 Turbo | $10.00 | $30.00 |
| GPT-4 | $30.00 | $60.00 |
| GPT-3.5 Turbo | $0.50 | $1.50 |

---

## Self-Hosted Solutions

### Why Self-Host?

**Cost Savings at Scale:**
```
Break-even Analysis (Claude 3 Sonnet workload):

Managed (Bedrock):
- 10M tokens/month = $60,000/month = $720,000/year

Self-Hosted (vLLM + GPU):
- 4x A100 GPUs (reserved) = $15,000/month
- Inference overhead = $5,000/month
- Total = $20,000/month = $240,000/year

Savings = $480,000/year (67% reduction)
```

**Other Benefits:**
- 🚀 **20-30x throughput** with vLLM
- 🔒 **Data privacy** - No data leaves your infrastructure
- 🎯 **Custom models** - Fine-tuned, quantized, distilled
- ⚡ **Lower latency** - < 50ms p99 with GPU
- 📈 **Predictable costs** - No per-token billing

**Challenges:**
- ❌ GPU management complexity
- ❌ Model updates manual
- ❌ Scaling requires planning
- ❌ Requires ML/DevOps expertise

---

## vLLM Deep Dive

### What is vLLM?

**vLLM** (Very Large Language Model) is a high-throughput, memory-efficient inference engine for LLMs developed by UC Berkeley.

#### Key Innovations

1. **PagedAttention** - Inspired by OS virtual memory
   - Reduces KV cache memory by 50%
   - Allows longer sequences
   - Better GPU utilization

2. **Continuous Batching** - Dynamic request batching
   - 10-30x throughput vs naive batching
   - Handles variable sequence lengths
   - Minimal latency impact

3. **Optimized CUDA Kernels** - Custom GPU operations
   - Flash Attention 2 integration
   - Kernel fusion
   - Quantization support (INT8, INT4)

### Performance Comparison

**Throughput Benchmark** (Llama 2 7B on A100):

| Framework | Requests/sec | Latency (P99) | Memory Usage |
|-----------|--------------|---------------|--------------|
| HuggingFace Transformers | 100 | 500ms | 16GB |
| TensorRT-LLM | 800 | 150ms | 12GB |
| **vLLM** | **2,400** | **80ms** | **8GB** |

**Cost Per Million Tokens:**

| Method | Cost | Notes |
|--------|------|-------|
| Bedrock Claude 3 Sonnet | $18.00 | Managed, no infra cost |
| vLLM Llama 2 70B (A100) | $1.20 | Includes GPU amortization |
| vLLM Mistral 7B (A100) | $0.40 | Smaller model, same GPU |

### vLLM Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    vLLM Server Architecture                  │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  Client Request  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  FastAPI Server  │ ← OpenAI-compatible API
│  (async/await)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Request Scheduler│ ← Continuous batching
│ - Priority Queue │
│ - Load Balancing │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Engine Manager  │
│ - Model Loading  │
│ - GPU Allocation │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ PagedAttention   │ ← Memory-efficient KV cache
│   KV Cache       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   GPU Kernels    │ ← Optimized CUDA ops
│  (Flash Attn 2)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Token Stream    │ ← Streaming response
│  (Server-Sent    │
│   Events)        │
└──────────────────┘
```

### Supported Models

vLLM supports 50+ model architectures:

**Popular Models:**
- ✅ Llama 2/3 (7B, 13B, 70B, 405B)
- ✅ Mistral (7B, 8x7B MoE)
- ✅ Yi (6B, 34B)
- ✅ Qwen (7B, 14B, 72B)
- ✅ Phi-2/3 (2.7B, 14B)
- ✅ CodeLlama (7B, 13B, 34B)
- ✅ StarCoder (15.5B)
- ✅ Falcon (7B, 40B)

**NOT Supported:**
- ❌ GPT-4 (proprietary)
- ❌ Claude (proprietary)
- ❌ Gemini (proprietary)

### Installation & Setup

#### Basic Installation

```bash
# Install vLLM (requires CUDA 11.8+)
pip install vllm

# Verify installation
python -c "import vllm; print(vllm.__version__)"
```

#### Running vLLM Server

```python
# Start OpenAI-compatible server
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-chat-hf \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 1 \
    --dtype auto \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.9
```

#### Advanced Configuration

```python
from vllm import LLM, SamplingParams

# Initialize vLLM engine
llm = LLM(
    model="meta-llama/Llama-2-7b-chat-hf",
    tensor_parallel_size=4,  # 4 GPUs
    dtype="float16",
    max_model_len=4096,
    gpu_memory_utilization=0.9,
    swap_space=8,  # GB of CPU swap space
    quantization="awq",  # INT4 quantization
    enable_prefix_caching=True,  # Cache common prefixes
)

# Sampling parameters
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=1024,
    presence_penalty=0.5,
    frequency_penalty=0.5,
)

# Batch inference
prompts = [
    "Explain quantum computing",
    "What is machine learning?",
    "Describe photosynthesis",
]

outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    print(f"Prompt: {output.prompt}")
    print(f"Generated: {output.outputs[0].text}")
    print("---")
```

### OpenAI-Compatible API

vLLM provides drop-in replacement for OpenAI API:

```python
import openai

# Point to vLLM server
openai.api_base = "http://localhost:8000/v1"
openai.api_key = "EMPTY"  # vLLM doesn't require key

# Use standard OpenAI client
response = openai.ChatCompletion.create(
    model="meta-llama/Llama-2-7b-chat-hf",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain transformers"}
    ],
    temperature=0.7,
    max_tokens=512,
    stream=True  # Streaming support
)

for chunk in response:
    if chunk.choices[0].delta.get("content"):
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Multi-GPU Strategies

**Tensor Parallelism** (same model across GPUs):
```bash
# Split model across 4 GPUs
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-70b-chat-hf \
    --tensor-parallel-size 4
```

**Pipeline Parallelism** (layers across GPUs):
```bash
# Distribute layers across GPUs
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-70b-chat-hf \
    --pipeline-parallel-size 4
```

**Data Parallelism** (multiple replicas):
```bash
# Run 4 independent replicas with load balancer
for i in {0..3}; do
    CUDA_VISIBLE_DEVICES=$i python -m vllm.entrypoints.openai.api_server \
        --model meta-llama/Llama-2-7b-chat-hf \
        --port $((8000 + i)) &
done
```

---

## Comparison Matrix

### Feature Comparison

| Feature | AWS Bedrock | vLLM | TGI | Triton |
|---------|-------------|------|-----|--------|
| **Setup Complexity** | ⭐ Easy | ⭐⭐⭐ Complex | ⭐⭐ Moderate | ⭐⭐⭐⭐ Very Complex |
| **Throughput** | ⭐⭐ Moderate | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very Good | ⭐⭐⭐⭐ Very Good |
| **Cost (high volume)** | ⭐ Expensive | ⭐⭐⭐⭐⭐ Cheap | ⭐⭐⭐⭐ Cheap | ⭐⭐⭐⭐ Cheap |
| **Model Support** | ⭐⭐⭐ Limited | ⭐⭐⭐⭐⭐ 50+ models | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Any model |
| **Custom Models** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| **Maintenance** | ⭐⭐⭐⭐⭐ Zero | ⭐⭐ High | ⭐⭐ High | ⭐ Very High |
| **Scaling** | ⭐⭐⭐⭐⭐ Auto | ⭐⭐⭐ Manual K8s | ⭐⭐⭐ Manual K8s | ⭐⭐⭐ Manual K8s |
| **Latency** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very Good | ⭐⭐⭐⭐ Very Good |
| **OpenAI API Compat** | ❌ No | ✅ Yes | ✅ Yes | ⚠️ Partial |

### Cost Comparison

**Scenario**: 100M tokens/month (80M input + 20M output)

| Solution | Monthly Cost | Annual Cost | Notes |
|----------|--------------|-------------|-------|
| **Bedrock Claude 3 Sonnet** | $540,000 | $6,480,000 | Pay-per-token |
| **Bedrock Claude 3 Haiku** | $40,000 | $480,000 | Faster, cheaper |
| **Azure GPT-4 Turbo** | $1,400,000 | $16,800,000 | Most expensive |
| **Azure GPT-3.5 Turbo** | $70,000 | $840,000 | Good value |
| **vLLM Llama 2 70B (8xA100)** | $30,000 | $360,000 | Infrastructure only |
| **vLLM Mistral 7B (2xA100)** | $8,000 | $96,000 | Best TCO |

**Break-even Point**: ~5-10M tokens/month (depending on model)

---

## Architecture Patterns

### Pattern 1: Pure Managed (Bedrock)

```
Client → API Gateway → Lambda → Bedrock → Response
```

**Pros**: Simple, scalable, zero ops
**Cons**: Expensive at scale, no custom models
**Best for**: Prototypes, low-volume production

### Pattern 2: Pure Self-Hosted (vLLM)

```
Client → Load Balancer → vLLM Cluster (K8s) → Response
```

**Pros**: Cost-effective, full control
**Cons**: Complex ops, manual scaling
**Best for**: High-volume, cost-sensitive

### Pattern 3: Hybrid (Best of Both)

```
                    ┌─────────────┐
Client → Router ────┤             ├──→ Bedrock (Claude 3)
                    │ Intelligent │
                    │   Router    ├──→ vLLM (Llama 2)
                    │             │
                    └─────────────┘
                          │
                    Priority Rules:
                    - High priority → Bedrock
                    - Batch jobs → vLLM
                    - Custom models → vLLM
                    - Fallback → Bedrock
```

**Pros**: Flexibility, cost optimization, high availability
**Cons**: Moderate complexity
**Best for**: Production at scale

### Pattern 4: Multi-Region with Failover

```
Region 1 (us-east-1):
  - vLLM Primary (A100 cluster)
  - Bedrock Backup

Region 2 (us-west-2):
  - vLLM Secondary (A100 cluster)
  - Bedrock Backup

Traffic:
  1. Route to nearest vLLM
  2. If vLLM unhealthy → Bedrock
  3. If region fails → Other region
```

**Pros**: High availability, disaster recovery
**Cons**: Complex, higher cost
**Best for**: Mission-critical applications

---

## Cost Analysis

### TCO Calculator

```python
def calculate_tco(
    monthly_tokens: int,
    bedrock_cost_per_1k: float = 18.0,  # Claude 3 Sonnet avg
    vllm_gpu_cost_monthly: float = 15000.0,  # 4x A100 reserved
    vllm_ops_cost_monthly: float = 5000.0,
):
    """
    Total Cost of Ownership calculator
    """
    # Bedrock cost
    bedrock_monthly = (monthly_tokens / 1000) * bedrock_cost_per_1k
    bedrock_annual = bedrock_monthly * 12
    
    # vLLM cost
    vllm_monthly = vllm_gpu_cost_monthly + vllm_ops_cost_monthly
    vllm_annual = vllm_monthly * 12
    
    # Break-even
    break_even_tokens = (vllm_monthly / bedrock_cost_per_1k) * 1000
    
    return {
        "bedrock_monthly": bedrock_monthly,
        "bedrock_annual": bedrock_annual,
        "vllm_monthly": vllm_monthly,
        "vllm_annual": vllm_annual,
        "break_even_tokens": break_even_tokens,
        "savings_annual": bedrock_annual - vllm_annual if bedrock_annual > vllm_annual else 0,
    }

# Example calculations
scenarios = [
    ("Prototype", 1_000_000),      # 1M tokens/month
    ("Small Prod", 10_000_000),    # 10M tokens/month
    ("Medium Prod", 50_000_000),   # 50M tokens/month
    ("Large Prod", 100_000_000),   # 100M tokens/month
]

for name, tokens in scenarios:
    result = calculate_tco(tokens)
    print(f"\n{name} ({tokens:,} tokens/month):")
    print(f"  Bedrock: ${result['bedrock_monthly']:,.0f}/mo (${result['bedrock_annual']:,.0f}/yr)")
    print(f"  vLLM:    ${result['vllm_monthly']:,.0f}/mo (${result['vllm_annual']:,.0f}/yr)")
    print(f"  Savings: ${result['savings_annual']:,.0f}/yr")

# Output:
# Prototype (1,000,000 tokens/month):
#   Bedrock: $18,000/mo ($216,000/yr)
#   vLLM:    $20,000/mo ($240,000/yr)
#   Savings: $0/yr  → Use Bedrock
#
# Small Prod (10,000,000 tokens/month):
#   Bedrock: $180,000/mo ($2,160,000/yr)
#   vLLM:    $20,000/mo ($240,000/yr)
#   Savings: $1,920,000/yr  → Use vLLM
#
# Large Prod (100,000,000 tokens/month):
#   Bedrock: $1,800,000/mo ($21,600,000/yr)
#   vLLM:    $20,000/mo ($240,000/yr)
#   Savings: $21,360,000/yr  → Definitely vLLM!
```

### GPU Requirements

| Model | Min GPUs | Recommended GPUs | Memory | Notes |
|-------|----------|------------------|--------|-------|
| Llama 2 7B | 1x A10 (24GB) | 1x A100 (40GB) | ~14GB | Good for testing |
| Llama 2 13B | 1x A100 (40GB) | 2x A100 (80GB) | ~26GB | Production ready |
| Llama 2 70B | 2x A100 (80GB) | 4x A100 (80GB) | ~140GB | High quality |
| Mixtral 8x7B | 2x A100 (80GB) | 4x A100 (80GB) | ~100GB | MoE architecture |
| Llama 3 405B | 8x H100 (80GB) | 16x H100 (80GB) | ~810GB | Cutting edge |

---

## Deployment Guides

### Kubernetes Deployment (vLLM)

See: `D:\code_ai\code\etl-elt-platform\vllm-deployment\` for complete manifests.

**Key Components:**
1. GPU node pool with NVIDIA drivers
2. vLLM StatefulSet with persistent models
3. Horizontal Pod Autoscaler (HPA)
4. Service + Ingress for routing
5. Prometheus monitoring

### Docker Compose (Local Testing)

See: `D:\code_ai\code\etl-elt-platform\docker-compose.vllm.yml`

**Features:**
- vLLM with Llama 2 7B
- GPU passthrough
- Model caching
- Metrics endpoint

---

## Monitoring & Optimization

### Key Metrics

**vLLM-specific:**
```promql
# Request throughput
rate(vllm_requests_total[5m])

# Token generation speed (tokens/sec)
rate(vllm_tokens_generated_total[5m])

# KV cache utilization (should be < 90%)
vllm_kv_cache_usage_ratio

# GPU memory utilization
vllm_gpu_memory_usage_bytes / vllm_gpu_memory_total_bytes

# Batch size (continuous batching effectiveness)
vllm_current_batch_size

# Queue time (latency metric)
histogram_quantile(0.95, rate(vllm_queue_time_seconds_bucket[5m]))
```

### Optimization Tips

1. **GPU Memory Utilization**: Set to 0.9 (90%)
   ```python
   llm = LLM(gpu_memory_utilization=0.9)
   ```

2. **Enable Prefix Caching**: Reuse common prompts
   ```python
   llm = LLM(enable_prefix_caching=True)
   ```

3. **Quantization**: Use INT8 or INT4 for 2-4x speedup
   ```python
   llm = LLM(quantization="awq")  # or "gptq", "squeezellm"
   ```

4. **Increase Batch Size**: Better GPU utilization
   ```python
   llm = LLM(max_num_seqs=256)
   ```

5. **Adjust Max Sequence Length**: Match your use case
   ```python
   llm = LLM(max_model_len=2048)  # vs default 4096
   ```

---

## Decision Framework

### Decision Tree

```
Start: Do you need LLM serving?
│
├─ Volume < 1M tokens/month?
│  └─ YES → Use AWS Bedrock (simplest)
│
├─ Need GPT-4 specifically?
│  └─ YES → Use Azure OpenAI
│
├─ Volume > 10M tokens/month?
│  ├─ YES → Consider vLLM
│  │   │
│  │   ├─ Have ML/DevOps team?
│  │   │  ├─ YES → Use vLLM
│  │   │  └─ NO → Use Bedrock + hire team
│  │   │
│  │   └─ Need custom models?
│  │      └─ YES → Definitely vLLM
│  │
│  └─ NO → Stay with Bedrock
│
└─ Data sovereignty required?
   └─ YES → Self-hosted (vLLM on-premises)
```

### Recommendation by Company Size

| Company Size | Monthly Budget | Recommendation |
|--------------|----------------|----------------|
| **Startup** | < $10K | AWS Bedrock Haiku |
| **Scale-up** | $10K - $50K | Bedrock + vLLM prototype |
| **Mid-size** | $50K - $200K | Hybrid (vLLM + Bedrock failover) |
| **Enterprise** | > $200K | vLLM cluster + Bedrock backup |

---

## Summary

### Key Takeaways

1. **Start with Managed** (Bedrock/Azure) - Fastest time-to-market
2. **Monitor Costs** - Track token usage monthly
3. **Plan Migration** - At 5-10M tokens/month, evaluate vLLM
4. **Hybrid is Best** - Use both for optimal cost/reliability
5. **Invest in Team** - Self-hosting requires ML/DevOps expertise

### Implementation Path

**Phase 1: MVP** (Month 1-2)
- Use AWS Bedrock
- Instrument with metrics
- Track token usage

**Phase 2: Scale** (Month 3-6)
- If cost > $50K/month, prototype vLLM
- Test with 10% traffic
- Compare quality/cost

**Phase 3: Optimize** (Month 6-12)
- Implement hybrid routing
- Migrate high-volume to vLLM
- Keep Bedrock for:
  - Low-volume endpoints
  - Failover/backup
  - Claude-specific features

**Phase 4: Mature** (Year 2+)
- Multi-region vLLM
- Custom fine-tuned models
- Advanced optimizations (quantization, distillation)

---

## References

- [vLLM GitHub](https://github.com/vllm-project/vllm)
- [vLLM Documentation](https://docs.vllm.ai)
- [AWS Bedrock](https://aws.amazon.com/bedrock/)
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- [PagedAttention Paper](https://arxiv.org/abs/2309.06180)
- [LLM Inference Optimization](https://lilianweng.github.io/posts/2023-01-10-inference-optimization/)

---

**Document Version**: 1.0  
**Last Updated**: 2026-10-11  
**Status**: Complete
