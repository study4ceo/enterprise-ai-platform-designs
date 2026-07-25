# Model Information

## Current Model: Claude Sonnet 4.6

**Model ID:** `claude-sonnet-4.6`

### Why Claude Sonnet 4.6?

Claude Sonnet 4.6 is chosen for Code-AI-Self-Forged because it delivers:

1. **Frontier Performance**: State-of-the-art coding and agentic capabilities
2. **Multi-Step Reasoning**: Excels at complex, multi-step problem solving
3. **Cost Efficiency**: Same pricing as Sonnet 4.5 ($3/$15 per million tokens)
4. **Token Efficiency**: Consumes fewer tokens than Sonnet 4 while improving performance
5. **Production Ready**: Current recommended model for everyday tasks and agentic workflows
6. **Full Feature Support**: Prompt caching supported at standard pricing

### Model Capabilities

- **Agentic Coding**: Can compress multi-day coding projects into hours
- **Production Solutions**: Delivers production-ready code
- **Self-Correction**: Strong reasoning for error analysis and iteration
- **Context Handling**: Excellent at maintaining conversation context
- **Code Quality**: Generates clean, well-structured, commented code

### Pricing

- **Input**: $3 per million tokens
- **Output**: $15 per million tokens
- **Same as Sonnet 4.5** - no price increase for improved performance

### Migration History

| Date | Event |
|------|-------|
| December 2024 | Claude Sonnet 4.6 released |
| April 2026 | Claude Sonnet 4 (`claude-sonnet-4-20250514`) deprecated |
| June 15, 2026 | Claude Sonnet 4 scheduled for retirement |
| June 22, 2026 | Claude Sonnet 4.5 removed from consumer apps |

**Recommendation**: Always use `claude-sonnet-4.6` as it is the current stable, non-deprecated model.

### Alternative Models

If you need different capabilities, you can configure these models via `MODEL_NAME` environment variable:

**For Maximum Intelligence:**
- `claude-opus-4.7` - Highest reasoning capability, better for extremely complex problems
- More expensive but more capable

**For Speed/Cost:**
- `claude-sonnet-4.6` (Current) - Best balance
- `claude-haiku-4` - Faster and cheaper for simpler tasks (when available)

### Configuring Model

**Environment Variable:**
```bash
MODEL_NAME=claude-sonnet-4.6
```

**In Code:**
```python
from config import settings
settings.model_name = "claude-sonnet-4.6"
```

**Docker:**
```bash
docker run -e MODEL_NAME=claude-sonnet-4.6 code-ai-self-forged
```

### Model Monitoring

Track your usage and costs:
- [Anthropic Console](https://console.anthropic.com/)
- Monitor token consumption in logs
- Set up billing alerts

### References

- [Anthropic Release Notes](https://docs.anthropic.com/en/release-notes/)
- [Claude Sonnet 4.6 Announcement](https://www.anthropic.com/news/claude-sonnet-4-6)
- [Model Deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)

*Content summarized for compliance with licensing restrictions. Visit official Anthropic documentation for complete information.*
