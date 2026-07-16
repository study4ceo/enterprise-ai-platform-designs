# AI SRE Stack - Architecture Deep Dive

## System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                      CLAUDE AI AGENT                         │
│                   (Central Orchestrator)                     │
│                                                              │
│              Observe → Decide → Act Loop (60s)               │
│                                                              │
└────────┬─────────────────────────────────────────┬───────────┘
         │                                         │
         │  Parallel Observation                   │  Coordinated Actions
         │  (Async calls)                          │  (Sequential execution)
         │                                         │
    ┌────▼────────────────────────────────────────▼─────┐
    │                                                    │
    │           MCP SERVER LAYER (9 Servers)             │
    │                                                    │
    │   ┌──────────────┐  ┌──────────────┐             │
    │   │ Infrastructure│  │Observability │             │
    │   ├──────────────┤  ├──────────────┤             │
    │   │ Kubernetes   │  │ Datadog      │             │
    │   │ AWS          │  │ PagerDuty    │             │
    │   │ Terraform    │  │              │             │
    │   └──────────────┘  └──────────────┘             │
    │                                                    │
    │   ┌──────────────┐  ┌──────────────┐             │
    │   │    CI/CD     │  │Comms/Response│             │
    │   ├──────────────┤  ├──────────────┤             │
    │   │ GitHub       │  │ Slack        │             │
    │   │ Argo CD      │  │ Runbook      │             │
    │   └──────────────┘  └──────────────┘             │
    │                                                    │
    └────────┬───────────────────────────────┬──────────┘
             │                               │
             │ API Calls                     │ Actions
             │                               │
    ┌────────▼───────────┐         ┌────────▼───────────┐
    │  EXTERNAL SERVICES │         │  INFRASTRUCTURE    │
    │                    │         │                    │
    │ • K8s API Server   │         │ • Pods/Deployments │
    │ • AWS APIs         │         │ • EC2 Instances    │
    │ • Datadog API      │         │ • ArgoCD Apps      │
    │ • Slack API        │         │ • GitHub Repos     │
    │ • PagerDuty API    │         │ • Terraform State  │
    └────────────────────┘         └────────────────────┘
```

---

## Component Breakdown

### 1. **Claude AI Agent (Orchestrator)**

**File:** `sre_orchestrator.py`

**Responsibilities:**
- Coordinate the Observe → Decide → Act cycle
- Manage MCP server lifecycle (init, shutdown)
- Context management and history tracking
- Severity-based escalation
- Slack notification handling

**Key Methods:**
```python
async def observe() -> Dict[str, Any]:
    # Collect state from all MCP servers in parallel
    
async def decide(observations) -> Dict[str, Any]:
    # Send context to Claude for analysis
    # Receive recommended actions
    
async def act(decision) -> Dict[str, Any]:
    # Execute recommended actions
    # Track results
    
async def run_cycle():
    # One complete O→D→A cycle
    
async def run_continuous(interval=60):
    # Infinite monitoring loop
```

**Claude's Prompt Structure:**
```
Input:
  - Current state from all 9 MCP servers
  - Context history (previous cycles)
  - Configuration (thresholds, priorities)

Output (JSON):
  {
    "analysis": "Root cause analysis...",
    "severity": "low|medium|high|critical",
    "issues": ["Issue 1", "Issue 2"],
    "recommended_actions": [
      {
        "mcp_server": "kubernetes",
        "action": "scale_deployment",
        "params": {...},
        "reason": "Why this action is needed"
      }
    ]
  }
```

---

### 2. **MCP Server Layer**

**Base Class:** `mcp_servers/base_mcp.py`

**Abstract Interface:**
```python
class BaseMCPServer(ABC):
    async def initialize() -> bool
    async def observe() -> Dict[str, Any]
    async def act(action: str, params: Dict) -> Dict[str, Any]
    async def health_check() -> Dict[str, Any]
    async def shutdown()
    def get_capabilities() -> List[str]
```

**Categories:**
- `MCPCategory.INFRA` - Infrastructure (K8s, AWS, Terraform)
- `MCPCategory.OBSERVABILITY` - Monitoring (Datadog, PagerDuty)
- `MCPCategory.CICD` - Deployments (GitHub, Argo CD)
- `MCPCategory.COMMS` - Communications (Slack, Runbook)

**Status States:**
- `MCPStatus.HEALTHY` - All systems operational
- `MCPStatus.DEGRADED` - Partial functionality
- `MCPStatus.UNHEALTHY` - Service down or errors
- `MCPStatus.UNKNOWN` - Not initialized or indeterminate

---

### 3. **Configuration System**

**File:** `config.py`

**Structure:**
```python
SREConfig
  ├── anthropic: AnthropicConfig
  ├── kubernetes: KubernetesConfig
  ├── aws: AWSConfig
  ├── terraform: TerraformConfig
  ├── datadog: DatadogConfig
  ├── pagerduty: PagerDutyConfig
  ├── github: GitHubConfig
  ├── argocd: ArgoCDConfig
  ├── slack: SlackConfig
  └── runbook: RunbookConfig
  
  # Global settings
  ├── observation_interval: int
  ├── decision_threshold: float
  ├── auto_remediation: bool
  └── dry_run: bool
```

**Configuration Sources (Priority Order):**
1. Environment variables (`.env` file)
2. Default values in config models
3. Runtime overrides

---

## Data Flow

### **Observe Phase** (Parallel Execution)

```
┌─────────────────────────────────────────────────────┐
│ Orchestrator.observe()                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │ K8s.observe()│  │AWS.observe() │  │DD.observe│ │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘ │
│         │                 │                │       │
│         │  async gather (concurrent)       │       │
│         └─────────────────┴────────────────┘       │
│                           │                        │
│                           ▼                        │
│                  Aggregated State                  │
│                  {                                 │
│                    "kubernetes": {...},            │
│                    "aws": {...},                   │
│                    "datadog": {...},               │
│                    ...                             │
│                  }                                 │
└─────────────────────────────────────────────────────┘
```

**Example Observation Output:**
```json
{
  "kubernetes": {
    "status": "healthy",
    "pods": [{"name": "api-1", "ready": true, "restarts": 0}],
    "deployments": [{"name": "api", "replicas": 3, "available": 3}]
  },
  "datadog": {
    "status": "degraded",
    "active_alerts": [
      {"name": "High CPU", "severity": "warning", "value": "85%"}
    ]
  },
  "aws": {
    "status": "healthy",
    "instances": [{"id": "i-123", "state": "running"}],
    "costs": [{"date": "2024-01-15", "amount": 1250.00}]
  }
}
```

---

### **Decide Phase** (Claude Analysis)

```
┌────────────────────────────────────────────────────┐
│ Orchestrator.decide(observations)                  │
├────────────────────────────────────────────────────┤
│                                                    │
│  1. Build Context String                          │
│     ├─ Format observations                        │
│     ├─ Add context history                        │
│     └─ Include configuration                      │
│                                                    │
│  2. Create Prompt for Claude                      │
│     ├─ System state                               │
│     ├─ Analysis request                           │
│     └─ Response format (JSON)                     │
│                                                    │
│  3. Call Anthropic API                            │
│     └─ anthropic.messages.create()                │
│                                                    │
│  4. Parse Claude's Response                       │
│     └─ Extract JSON decision                      │
│                                                    │
│                    ▼                               │
│              Decision Object                       │
│              {                                     │
│                "analysis": "...",                  │
│                "severity": "high",                 │
│                "recommended_actions": [...]        │
│              }                                     │
└────────────────────────────────────────────────────┘
```

**Claude's Decision-Making Process:**
1. **Correlation** - Connect issues across domains
2. **Root Cause** - Identify primary failure point
3. **Impact Assessment** - Evaluate severity
4. **Action Planning** - Determine remediation steps
5. **Prioritization** - Order actions by importance

---

### **Act Phase** (Sequential Execution)

```
┌─────────────────────────────────────────────────────┐
│ Orchestrator.act(decision)                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  IF dry_run OR !auto_remediation:                  │
│    └─ Return actions WITHOUT executing             │
│                                                     │
│  ELSE:                                             │
│    FOR EACH action IN recommended_actions:         │
│      1. Validate MCP server exists                 │
│      2. Log action intent                          │
│      3. Execute: mcp_server.act(action, params)    │
│      4. Log result (success/failure)               │
│      5. Store in results array                     │
│                                                     │
│  IF severity >= HIGH:                              │
│    └─ Send Slack notification                      │
│                                                     │
│  Return: {                                         │
│    "executed": true,                               │
│    "results": [...]                                │
│  }                                                 │
└─────────────────────────────────────────────────────┘
```

---

## Execution Cycle Timeline

```
T+0s    │ Cycle Start
        │
T+0s    │ ═══ OBSERVE PHASE ═══
        │ ├─ Initialize MCP servers (if needed)
        │ ├─ Parallel observation calls (async)
        │ │  ├─ Kubernetes.observe() → 0.5s
        │ │  ├─ AWS.observe() → 0.8s
        │ │  ├─ Datadog.observe() → 0.6s
        │ │  └─ ... (all servers in parallel)
        │ └─ Aggregate results
T+1s    │ ✓ Observations complete
        │
T+1s    │ ═══ DECIDE PHASE ═══
        │ ├─ Build context string
        │ ├─ Create Claude prompt
        │ ├─ Call Anthropic API → 2-4s
        │ └─ Parse JSON response
T+5s    │ ✓ Decision received
        │
T+5s    │ ═══ ACT PHASE ═══
        │ ├─ Check dry_run / auto_remediation flags
        │ ├─ Execute actions sequentially:
        │ │  ├─ Action 1: Kubernetes.scale_deployment()
        │ │  ├─ Action 2: Slack.post_message()
        │ │  └─ Action 3: PagerDuty.create_incident()
        │ └─ Notify team (if high severity)
T+8s    │ ✓ Actions complete
        │
T+8s    │ Store cycle in context_history
        │ Log cycle completion
        │
T+60s   │ Sleep until next cycle
        │ (configurable: observation_interval)
        │
T+60s   │ ► Start next cycle
```

---

## Safety Mechanisms

### 1. **Dry-Run Mode**
```python
if config.dry_run:
    logger.info("🔒 DRY RUN MODE - No actions executed")
    return {"dry_run": True, "actions": decision.get('recommended_actions')}
```

**Use Case:** Test Claude's decision-making without impacting production

### 2. **Auto-Remediation Toggle**
```python
if not config.auto_remediation:
    logger.info("🔒 AUTO-REMEDIATION DISABLED - Manual approval required")
    return {"auto_remediation": False, "actions": decision.get('recommended_actions')}
```

**Use Case:** Require human approval before executing actions

### 3. **Severity-Based Escalation**
```python
if decision.get('severity') in ['high', 'critical']:
    await self._notify_slack(decision, action_results)
```

**Use Case:** Only alert team for serious issues

### 4. **Error Handling & Graceful Degradation**
```python
try:
    observation = await server.observe()
except Exception as e:
    logger.error(f"Failed to observe {name}: {e}")
    observations[name] = {"error": str(e), "status": "error"}
```

**Use Case:** Continue operating even if some MCP servers fail

### 5. **Context History**
```python
self.context_history.append({
    "observations": observations,
    "decision": decision,
    "action_results": action_results
})
```

**Use Case:** Learn from past cycles, post-incident analysis

---

## Extensibility Points

### 1. **Add New MCP Servers**
- Create `mcp_servers/yourservice_mcp.py`
- Inherit from `BaseMCPServer`
- Add to configuration and initialization

### 2. **Custom Decision Logic**
- Modify Claude prompt in `decide()` method
- Add custom rules or thresholds
- Integrate external decision engines

### 3. **Enhanced Actions**
- Add new `act()` methods to MCP servers
- Create multi-step action workflows
- Implement rollback capabilities

### 4. **Runbook System**
- Add YAML/JSON runbooks to `runbooks/` directory
- Claude automatically discovers and uses them
- Step-by-step procedures with conditions

### 5. **Notification Channels**
- Add email, SMS, phone notifications
- Custom webhook integrations
- Status page updates

---

## Performance Characteristics

### **Observation Phase:**
- **Concurrency:** All MCP servers observed in parallel (async)
- **Typical Duration:** 0.5-2 seconds (depends on API response times)
- **Bottleneck:** Slowest MCP server response

### **Decision Phase:**
- **Processing:** Sequential (Anthropic API call)
- **Typical Duration:** 2-5 seconds
- **Bottleneck:** Claude API latency, prompt complexity

### **Action Phase:**
- **Execution:** Sequential (safety-first approach)
- **Typical Duration:** 1-10 seconds (depends on action count)
- **Bottleneck:** Slowest action execution (e.g., deployment scaling)

### **Total Cycle Time:**
- **Typical:** 5-15 seconds
- **Interval:** 60 seconds (configurable)
- **Utilization:** 8-25% (mostly idle, waiting for next cycle)

---

## Scalability Considerations

### **Current Implementation:**
- **Single orchestrator instance**
- **Synchronous cycles** (one at a time)
- **In-memory context history**

### **Scaling Options:**

1. **Horizontal Scaling**
   - Run multiple orchestrators
   - Use leader election (e.g., etcd, Consul)
   - Shared state in Redis/DB

2. **Vertical Scaling**
   - Reduce observation_interval for faster detection
   - Parallel action execution (with care!)
   - Batch similar actions

3. **State Management**
   - Persist context_history to database
   - Share state across orchestrator instances
   - Event sourcing for audit trail

4. **High Availability**
   - Primary/secondary orchestrator setup
   - Automatic failover
   - Health monitoring of orchestrator itself

---

## Security Architecture

### **Credential Management:**
```
.env (not in git)
  ↓
Environment Variables
  ↓
Config Objects (Pydantic)
  ↓
MCP Servers (in-memory only)
```

### **Access Control:**
- **Kubernetes:** RBAC with least privilege
- **AWS:** IAM roles with minimal permissions
- **APIs:** Read-only where possible during testing
- **Secrets:** Never logged or stored in plaintext

### **Audit Trail:**
- All observations logged
- All decisions logged with reasoning
- All actions logged with results
- Timestamps and context preserved

---

## Summary

The AI SRE Stack is a **production-ready, extensible, intelligent SRE automation system**:

✅ **Modular** - Each MCP server is independent  
✅ **Extensible** - Easy to add new integrations  
✅ **Safe** - Multiple safety mechanisms  
✅ **Intelligent** - Claude provides context-aware decisions  
✅ **Observable** - Comprehensive logging and history  
✅ **Scalable** - Can handle large infrastructures  

**Total Architecture:** ~15 files, ~2,500 lines of code, 9 MCP servers, infinite possibilities. 🚀
