# Model Evaluation Framework

Complete guide and tools for evaluating LLMs and AI models.

## 📚 Documentation

**[MODEL-EVALUATION-GUIDE.md](./MODEL-EVALUATION-GUIDE.md)** - Comprehensive guide covering:
- Automated metrics (BLEU, ROUGE, BERTScore, Perplexity)
- Human evaluation methods
- Benchmark datasets (GLUE, SQuAD, HumanEval, GSM8K)
- Tools & frameworks (LangChain, RAGAS, TruLens)
- Production monitoring
- Best practices

**[DEPLOYMENT-READINESS.md](./DEPLOYMENT-READINESS.md)** - When to deploy a model
- Performance criteria (benchmarks, baseline comparison)
- Business requirements (ROI, UX thresholds)
- Safety checks (error rates, bias, adversarial robustness)
- Operational readiness (monitoring, rollback, A/B testing)
- Complete deployment checklist with code examples

**[LLM-USAGE-GOVERNANCE.md](./LLM-USAGE-GOVERNANCE.md)** - **How to limit LLM usage across teams** 🆕
- API Gateway with rate limiting and quotas
- Token budget system with alerts
- Cost tracking and attribution
- Priority queuing for critical teams
- Usage policies and approval workflows
- Monitoring dashboard and admin interface

## 🚀 Quick Start

### Setup

```bash
cd model-evaluation
pip install -r requirements.txt

# Set API keys
export GROQ_API_KEY="your_groq_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
```

### Run Evaluation

```bash
python creative-hub-eval.py
```

## 📊 Example Output

```
Starting Creative Automation Hub Model Evaluation
Test cases: 3
Models: Groq (llama-3.3-70b) vs Anthropic (claude-sonnet-4)

[1/3] Testing: Write a tweet about sustainable fashion...
[2/3] Testing: Write a blog intro about remote work...
[3/3] Testing: Create ad copy for a project management...

============================================================
EVALUATION SUMMARY
============================================================

Groq (llama-3.3-70b):
  ROUGE-1:      0.654 ± 0.082
  ROUGE-L:      0.588 ± 0.091
  BERTScore F1: 0.892 ± 0.034
  Avg Time:     2.14s

Anthropic (claude-sonnet-4):
  ROUGE-1:      0.698 ± 0.075
  ROUGE-L:      0.621 ± 0.088
  BERTScore F1: 0.915 ± 0.028
  Avg Time:     3.87s

============================================================
Winner: Anthropic
============================================================
```

## 🧪 Evaluation Metrics

### Automated Metrics

| Metric     | Purpose                | Range | Higher = Better |
|-----------|------------------------|-------|-----------------|
| ROUGE-1   | Word overlap           | 0-1   | ✅              |
| ROUGE-L   | Longest common subseq  | 0-1   | ✅              |
| BERTScore | Semantic similarity    | 0-1   | ✅              |
| Perplexity| Language model quality | 0-∞   | ❌ (lower better)|

### LLM-as-Judge Criteria

- **Engagement**: Is it engaging and shareable?
- **Clarity**: Is the message clear?
- **Professionalism**: Appropriate tone?
- **Call-to-Action**: Does it inspire action?

## 📝 Custom Test Cases

Add your own test cases:

```python
from creative_hub_eval import TestCase

test_case = TestCase(
    prompt="Your prompt here",
    content_type="social",  # or "blog", "ad"
    tone="professional",    # or "casual", "friendly"
    reference="Expected output here",
    criteria={
        "criterion_1": "Description",
        "criterion_2": "Description"
    }
)
```

## 🔍 Evaluation Methods

### 1. Automated Metrics
- Fast and cheap
- Consistent
- Good for regression testing

### 2. LLM-as-Judge
- Scalable
- Evaluates nuanced criteria
- Decent correlation with human judgment

### 3. Human Evaluation
- Gold standard
- Slow and expensive
- Use for final validation

## 📈 Tracking Over Time

```python
# Run weekly evaluations
results_week_1 = evaluator.run_batch(test_cases)
results_week_2 = evaluator.run_batch(test_cases)

# Compare
improvement = (
    results_week_2['bert_f1_mean'] - 
    results_week_1['bert_f1_mean']
)
```

## 🛠️ Tools Used

- **bert-score**: Semantic similarity via BERT embeddings
- **rouge-score**: N-gram overlap for summarization
- **Groq API**: Fast LLM inference
- **Anthropic API**: High-quality generation

## 📚 Additional Resources

- [GLUE Benchmark](https://gluebenchmark.com/)
- [HuggingFace Evaluate](https://huggingface.co/docs/evaluate/)
- [LangChain Evaluators](https://python.langchain.com/docs/guides/evaluation/)
- [RAGAS Documentation](https://docs.ragas.io/)

## 🎯 Use Cases

### Creative Automation Hub
- Evaluate text generation quality
- Compare Groq vs Anthropic
- A/B test different prompts

### General LLM Projects
- Model selection
- Prompt engineering
- Fine-tuning validation
- Production monitoring

## 🤝 Contributing

Add more test cases, metrics, or evaluation methods:

1. Add test cases to `create_test_suite()`
2. Implement new metrics in `evaluate_single()`
3. Add criteria to `llm_as_judge()`

## 📖 Learn More

See [MODEL-EVALUATION-GUIDE.md](./MODEL-EVALUATION-GUIDE.md) for:
- Detailed metric explanations
- Benchmark datasets
- Production monitoring setup
- Statistical significance testing
- Cost analysis

## 💡 Tips

1. **Start simple**: Use automated metrics first
2. **Add LLM-as-judge**: For nuanced criteria
3. **Validate with humans**: Sample 10-20% for human eval
4. **Track over time**: Monitor for regressions
5. **Consider cost**: Balance quality vs API costs

## 📊 Example Results

**Groq Pros:**
- ✅ 2x faster (2.1s vs 3.9s)
- ✅ Cheaper ($0.05 vs $0.15 per 1K tokens)

**Anthropic Pros:**
- ✅ Higher quality (0.915 vs 0.892 BERTScore)
- ✅ Better ROUGE scores

**Choose based on:**
- Groq: Speed and cost matter
- Anthropic: Quality matters most
