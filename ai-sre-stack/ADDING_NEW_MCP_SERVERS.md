# Adding New MCP Servers - Step-by-Step Guide

This guide shows how to extend the AI SRE Stack with additional MCP servers beyond the initial 9.

## Why Add More MCP Servers?

The beauty of this architecture is **extensibility**. You can integrate ANY tool or service that your SRE team uses:

- **More observability tools** (Prometheus, Grafana, New Relic)
- **Cloud providers** (GCP, Azure)
- **Databases** (PostgreSQL, MongoDB, Redis)
- **Security tools** (Vault, Snyk)
- **Business tools** (Jira, Confluence)

Claude will automatically **observe** these new systems and make **correlated decisions** across all domains.

---

## Step-by-Step: Adding Prometheus MCP

Let's walk through adding Prometheus as an example.

### Step 1: Create the MCP Server Class

Create `mcp_servers/prometheus_mcp.py` (already done above as example):

```python
from .base_mcp import BaseMCPServer, MCPCategory

class PrometheusMCP(BaseMCPServer):
    def __init__(self, config):
        super().__init__("Prometheus", MCPCategory.OBSERVABILITY, config)
        self.prometheus_url = config.get('url')
    
    async def _connect(self):
        # Initialize connection to Prometheus API
        pass
    
    async def observe(self):
        # Return: active alerts, target health, key metrics
        return {
            "status": "healthy",
            "active_alerts": [...],
            "unhealthy_targets": [...]
        }
    
    async def act(self, action, params):
        # Execute: query_metric, silence_alert, etc.
        return {"success": True}
    
    async def _health_check(self):
        # Check Prometheus is accessible
        return {"healthy": True}
```

**Key methods to implement:**
- `_connect()` - Establish connection
- `observe()` - Return current state
- `act(action, params)` - Execute actions
- `_health_check()` - Verify service health
- `get_capabilities()` - List available actions

### Step 2: Add Configuration

Edit `config.py` to add Prometheus config:

```python
class PrometheusConfig(BaseModel):
    """Prometheus MCP configuration."""
    enabled: bool = True
    url: str = Field(default_factory=lambda: os.getenv("PROMETHEUS_URL", "http://localhost:9090"))
    username: str = Field(default_factory=lambda: os.getenv("PROMETHEUS_USERNAME", ""))
    password: str = Field(default_factory=lambda: os.getenv("PROMETHEUS_PASSWORD", ""))

class SREConfig(BaseModel):
    # ... existing configs ...
    prometheus: PrometheusConfig = Field(default_factory=PrometheusConfig)

# Update get_enabled_mcps():
def get_enabled_mcps() -> Dict[str, Any]:
    enabled = {}
    # ... existing servers ...
    if config.prometheus.enabled:
        enabled['prometheus'] = config.prometheus
    return enabled
```

### Step 3: Add Environment Variables

Edit `.env.example` (and your `.env`):

```bash
# Prometheus
PROMETHEUS_URL=http://localhost:9090
PROMETHEUS_USERNAME=optional_username
PROMETHEUS_PASSWORD=optional_password
```

### Step 4: Update MCP Server Imports

Edit `mcp_servers/__init__.py`:

```python
from .prometheus_mcp import PrometheusMCP

__all__ = [
    # ... existing servers ...
    'PrometheusMCP',
]
```

### Step 5: Initialize in Orchestrator

Edit `sre_orchestrator.py` in the `initialize()` method:

```python
mcp_classes = {
    # ... existing servers ...
    'prometheus': PrometheusMCP,
}
```

### Step 6: Test the New Server

```python
# Test standalone
import asyncio
from mcp_servers import PrometheusMCP

async def test():
    config = {'url': 'http://localhost:9090'}
    mcp = PrometheusMCP(config)
    await mcp.initialize()
    
    # Test observe
    observation = await mcp.observe()
    print("Observation:", observation)
    
    # Test action
    result = await mcp.act('query_metric', {'query': 'up'})
    print("Action result:", result)

asyncio.run(test())
```

### Step 7: Run the Full System

```bash
# Add Prometheus URL to .env
echo "PROMETHEUS_URL=http://your-prometheus:9090" >> .env

# Run the orchestrator
python sre_orchestrator.py
```

Claude will now:
- Observe Prometheus alerts alongside Datadog/PagerDuty
- Correlate Prometheus metrics with Kubernetes/AWS state
- Make decisions based on ALL 10 systems
- Execute actions across multiple domains

---

## Real-World Example: Multi-Tool Correlation

**Scenario:** Database Performance Issue

With Prometheus added, Claude can now correlate:

**Observe:**
- **Prometheus**: High database query latency (>500ms)
- **Kubernetes**: Database pod CPU at 85%
- **AWS**: RDS instance IOPS maxed out
- **Datadog**: Application error rate increased
- **GitHub**: Recent migration PR merged 2 hours ago

**Decide (Claude's Analysis):**
```json
{
  "analysis": "Database performance degraded after recent migration. Root cause: inefficient query added in PR #123. Multiple indicators confirm database is bottleneck.",
  "severity": "high",
  "recommended_actions": [
    {
      "mcp_server": "kubernetes",
      "action": "scale_deployment",
      "params": {"deployment_name": "api", "replicas": 5},
      "reason": "Scale API to reduce database connection pressure"
    },
    {
      "mcp_server": "github",
      "action": "comment_pr",
      "params": {"pr_number": 123, "comment": "⚠️ This PR caused database performance regression. Query optimization needed."},
      "reason": "Alert developers to issue"
    },
    {
      "mcp_server": "slack",
      "action": "post_message",
      "params": {"text": "🚨 Database performance issue traced to PR #123. Scaling API, investigating query."},
      "reason": "Notify team"
    }
  ]
}
```

See how Prometheus data **enriched Claude's decision-making**?

---

## Template for Any New MCP Server

```python
"""YourService MCP Server implementation."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
import logging

logger = logging.getLogger(__name__)


class YourServiceMCP(BaseMCPServer):
    """YourService MCP server for [purpose]."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("YourService", MCPCategory.OBSERVABILITY, config)  # or INFRA, CICD, COMMS
        self.api_client = None
        # Store config values
        self.api_url = config.get('url')
        self.api_key = config.get('api_key')
        
    async def _connect(self):
        """Connect to YourService API."""
        try:
            # Initialize your API client
            # Test connection
            logger.info(f"Connected to YourService")
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise
    
    async def observe(self) -> Dict[str, Any]:
        """Observe current state.
        
        Returns:
            Current state, metrics, alerts, etc.
        """
        try:
            # Fetch current state from your service
            # Return structured data
            return {
                "status": "healthy",  # or "degraded", "unhealthy"
                # Add service-specific data
                "metric_1": 123,
                "alerts": [],
                "custom_field": "value"
            }
        except Exception as e:
            logger.error(f"Observe error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action.
        
        Args:
            action: Action name (e.g., "restart", "scale", "alert")
            params: Action parameters
            
        Returns:
            Action result with success flag
        """
        try:
            if action == "your_action":
                return await self._your_action(params)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _your_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Implement your specific action."""
        # Execute the action
        return {"success": True, "message": "Action completed"}
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            # Test service is accessible
            return {"message": "YourService accessible"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """List available capabilities."""
        return [
            "your_action",
            "another_action",
            "query_data"
        ]
```

---

## Examples of Possible MCP Servers

### 1. **PostgreSQL MCP**
```python
async def observe(self):
    return {
        "active_connections": 45,
        "slow_queries": [...],
        "replication_lag": 0.5,
        "database_size_gb": 120
    }

async def act(self, action, params):
    if action == "kill_query":
        # Terminate long-running query
    elif action == "vacuum_table":
        # Run VACUUM on table
```

### 2. **Grafana MCP**
```python
async def observe(self):
    return {
        "dashboards": [...],
        "active_alerts": [...],
        "recent_annotations": [...]
    }

async def act(self, action, params):
    if action == "create_annotation":
        # Mark deployment on dashboard
    elif action == "snapshot_dashboard":
        # Take dashboard snapshot
```

### 3. **Jira MCP**
```python
async def observe(self):
    return {
        "open_incidents": [...],
        "sprint_progress": 0.75,
        "blocked_issues": [...]
    }

async def act(self, action, params):
    if action == "create_ticket":
        # Create incident ticket
    elif action == "update_status":
        # Move ticket to "In Progress"
```

---

## Benefits of Adding More MCP Servers

1. **Richer Context**: Claude sees more of your infrastructure
2. **Better Decisions**: Correlate data across MORE systems
3. **Automated Actions**: Take actions in MORE tools
4. **Single Interface**: One AI agent manages everything
5. **Custom Workflows**: Create runbooks that span all your tools

---

## Best Practices

### ✅ DO:
- Implement all required methods (`observe`, `act`, `_health_check`)
- Add comprehensive error handling
- Include logging for debugging
- Return consistent data structures
- Document capabilities clearly

### ❌ DON'T:
- Make blocking synchronous calls (use async)
- Store sensitive credentials in code
- Skip error handling
- Return inconsistent data formats
- Forget to test standalone before integrating

---

## Testing Checklist

Before integrating a new MCP server:

- [ ] Test `initialize()` - Connection successful?
- [ ] Test `observe()` - Returns valid data?
- [ ] Test `act()` - Actions execute correctly?
- [ ] Test `health_check()` - Detects failures?
- [ ] Test error handling - Graceful degradation?
- [ ] Test with orchestrator - Integrates smoothly?
- [ ] Document in README - Others can use it?

---

## Summary

**Adding new MCP servers is simple:**
1. Create server class (inherit from `BaseMCPServer`)
2. Add configuration
3. Update imports and initialization
4. Test and deploy

**Result:**
Claude now observes and acts on your new service, making **correlated decisions** across your ENTIRE infrastructure stack!

This is the power of the extensible AI SRE architecture. 🚀
