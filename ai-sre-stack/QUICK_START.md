# AI SRE Stack - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
cd ai-sre-stack
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials (at minimum, add Anthropic API key)
nano .env
```

**Minimum required:**
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key
```

**Optional** (enable specific MCP servers by adding their credentials):
- Kubernetes: `KUBECONFIG_PATH`, `K8S_NAMESPACE`
- AWS: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Datadog: `DATADOG_API_KEY`, `DATADOG_APP_KEY`
- Slack: `SLACK_BOT_TOKEN`
- etc.

### Step 3: Test Run (Dry Mode)

```bash
# Run a single observation cycle without executing actions
python sre_orchestrator.py
```

This will:
1. Initialize all configured MCP servers
2. Observe current state across all systems
3. Have Claude analyze and recommend actions
4. Display recommendations WITHOUT executing them

### Step 4: Review Output

You'll see output like:

```
=== OBSERVE PHASE ===
📊 kubernetes: healthy
📊 aws: healthy  
📊 datadog: degraded (2 active alerts)
📊 slack: healthy

=== DECIDE PHASE ===
🤖 Claude's Analysis:
{
  "analysis": "System mostly healthy. Datadog shows 2 active CPU alerts...",
  "severity": "medium",
  "recommended_actions": [...]
}

=== ACT PHASE ===
🔒 DRY RUN MODE - No actions will be executed
```

### Step 5: Enable Auto-Remediation (Optional)

Once you're confident, enable automatic action execution:

```python
# Edit config.py:
dry_run = False
auto_remediation = True
observation_interval = 60  # seconds
```

Then run continuous monitoring:
```bash
python sre_orchestrator.py
```

## 🎯 Common Use Cases

### Use Case 1: Monitor Kubernetes Only

```bash
# .env
ANTHROPIC_API_KEY=your_key
KUBECONFIG_PATH=~/.kube/config
K8S_NAMESPACE=production
SLACK_BOT_TOKEN=your_slack_token
```

The system will:
- Monitor pod health, deployments, events
- Alert to Slack if issues detected
- Recommend scaling/restart actions

### Use Case 2: Full Stack Monitoring

Configure all MCP servers in `.env`, then run continuous monitoring:

```bash
python sre_orchestrator.py
```

Claude will:
- Observe all 9 systems every 60 seconds
- Correlate issues across domains
- Execute coordinated remediation
- Notify teams via Slack
- Escalate critical issues to PagerDuty

### Use Case 3: Custom Incident Response

1. Create custom runbook:
```yaml
# runbooks/my_app_down.yaml
id: my_app_down
title: My App Recovery
steps:
  - name: Check pods
    action: kubernetes
    command: observe
  - name: Restart
    action: kubernetes
    command: restart_pod
```

2. Claude will automatically discover and use this runbook when appropriate

## 📊 Monitoring the Orchestrator

### Check Logs
```bash
# All logs go to stdout
python sre_orchestrator.py | tee orchestrator.log
```

### Watch Slack Channel
Configure `SLACK_CHANNEL=#incidents` to see all high/critical decisions

### Review Context History
The orchestrator stores all cycles in memory:
```python
# In sre_orchestrator.py, add at the end:
print(f"Total cycles: {len(orchestrator.context_history)}")
```

## 🔧 Troubleshooting

### "Failed to initialize X MCP"
- Check credentials for that service in `.env`
- Verify network connectivity
- Review error message in logs

### "Claude decision-making failed"
- Check Anthropic API key
- Verify API rate limits not exceeded
- Review prompt formatting

### "No actions executed"
- Ensure `dry_run = False` in config
- Check `auto_remediation = True`
- Verify MCP server has required permissions

## 💡 Tips

- Start with dry_run mode to understand Claude's decision-making
- Enable one MCP server at a time to isolate issues
- Review Claude's analysis even when no actions recommended
- Use Slack notifications for visibility
- Create custom runbooks for your specific incidents

## 📚 Next Steps

- Read full [README.md](README.md) for detailed documentation
- Review [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for capabilities
- Customize runbooks in `runbooks/` directory
- Add more MCP servers as needed
- Set up monitoring dashboard (future enhancement)

## 🆘 Need Help?

1. Check the comprehensive [README.md](README.md)
2. Review example runbooks in `runbooks/`
3. Look at MCP server implementations in `mcp_servers/`
4. Check configuration in `config.py`

## ⚡ Quick Commands

```bash
# Single test cycle (dry-run)
python sre_orchestrator.py

# Continuous monitoring (requires config changes)
python sre_orchestrator.py

# Test individual MCP server
python -c "
import asyncio
from mcp_servers import KubernetesMCP
async def test():
    mcp = KubernetesMCP({'kubeconfig_path': '~/.kube/config', 'namespace': 'default'})
    await mcp.initialize()
    print(await mcp.observe())
asyncio.run(test())
"

# Check all MCP server status
python -c "
import asyncio
from config import get_enabled_mcps
for name, config in get_enabled_mcps().items():
    print(f'{name}: enabled')
"
```

That's it! You now have a fully functional AI SRE Stack running with Claude as your intelligent orchestrator. 🎉
