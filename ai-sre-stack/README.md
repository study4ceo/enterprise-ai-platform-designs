# AI SRE Stack - MCP Integration

An intelligent Site Reliability Engineering system with Claude as the central orchestrator, integrating **12 MCP servers** across Infrastructure, Observability, Security, CI/CD, and Communications domains, with **enterprise-grade security hardening**.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLAUDE AI ORCHESTRATOR                  │
│              Observe → Decide → Act                         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         🔒 SECURITY CONTROL LAYER 🔒                  │  │
│  │  • Action Whitelist    • Rate Limiting               │  │
│  │  • Approval Workflow   • Audit Logging               │  │
│  │  • Vault Integration                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │         MCP SERVERS (12)       │
        └───────────────┬───────────────┘
                        │
    ┌───────────┬───────┴────────┬───────────┬──────────────┐
    │           │                │           │              │
┌───▼────┐ ┌───▼─────┐ ┌────────▼──┐ ┌──────▼────┐ ┌──────▼────┐
│ Infra  │ │ Observe │ │ Security  │ │  CI/CD    │ │   Comms   │
│        │ │         │ │           │ │           │ │           │
│ • K8s  │ │ • Data- │ │ • Guard-  │ │ • GitHub  │ │ • Slack   │
│ • AWS  │ │   dog   │ │   Duty    │ │ • Argo CD │ │ • Runbook │
│ • Terra│ │ • Pager │ │ • Cloud-  │ │           │ │           │
│   form │ │   Duty  │ │   Trail   │ │           │ │           │
│        │ │         │ │ • Vault   │ │           │ │           │
└────────┘ └─────────┘ └───────────┘ └───────────┘ └───────────┘
```

Claude reads context from multiple MCP servers, makes intelligent decisions protected by 5 security layers, and takes automated actions to maintain system health and respond to incidents.

## MCP Servers (12 Total)

### Infrastructure (Infra)
1. **Kubernetes MCP** - Pod, event, log, and workload management
   - Observe pods, deployments, events
   - Scale deployments, restart pods
   - Get logs and resource status

2. **Terraform MCP** - Infrastructure as code review and drift detection
   - Detect configuration drift
   - Run plan, apply, validate
   - Monitor resource state

3. **AWS MCP** - Cloud resource, IAM, and cost management
   - Monitor EC2 instances
   - Track costs and usage
   - Start/stop/terminate instances

### Observability
4. **Datadog MCP** - Metrics, traces, and alert monitoring
   - Monitor active alerts
   - Query metrics and dashboards
   - Mute/unmute monitors

5. **PagerDuty MCP** - Incident and on-call management
   - Track active incidents
   - Get on-call schedules
   - Create, acknowledge, resolve incidents

### Security 🔒
6. **AWS GuardDuty MCP** - Threat detection and security monitoring
   - Detect security threats and anomalies
   - List and analyze findings
   - Archive findings, update threat intelligence

7. **AWS CloudTrail MCP** - API audit logging and compliance
   - Track API calls and user activity
   - Search security events
   - Audit compliance and access patterns

8. **HashiCorp Vault MCP** - Secrets management
   - Store and retrieve secrets securely
   - Dynamic secrets generation
   - Secret versioning and rotation
   - **High-risk**: Write/delete operations require approval

### CI/CD
9. **GitHub MCP** - Repository, PR, and issue management
   - Monitor PRs and issues
   - Review workflows and commits
   - Create issues, comment on PRs

10. **Argo CD MCP** - GitOps deployment and sync monitoring
    - Check sync status and drift
    - Sync, refresh, rollback applications
    - Monitor deployment health

### Comms & Response
11. **Slack MCP** - Team communication and incident coordination
    - Post messages and updates
    - Read thread context
    - Coordinate incident response

12. **Incident Runbook MCP** - SOP and remediation procedures
    - Search and retrieve runbooks
    - Execute step-by-step procedures
    - Track remediation progress

## Features

### Core Capabilities
- **Autonomous Monitoring** - Continuous health checks across all systems (60s interval)
- **Intelligent Decision Making** - Claude analyzes context and recommends actions
- **Automated Remediation** - Self-healing actions based on runbooks
- **Multi-Domain Orchestration** - Coordinated actions across infra, observability, security, and CI/CD
- **Incident Coordination** - Automated Slack notifications and PagerDuty escalation
- **Security Monitoring** - GuardDuty threat detection and CloudTrail audit logging
- **Secrets Management** - Centralized credential storage with Vault

### 🔒 Enterprise Security Hardening (5 Layers)

#### 1. **Action Whitelisting**
- Defines which actions are allowed to execute
- Read-only operations whitelisted by default
- High-risk actions require additional approval
- Time-based restrictions (maintenance windows)
- Permanently blocked dangerous operations

#### 2. **Rate Limiting / Throttling**
- Prevents runaway automation
- Global limits: 10/min, 100/hour, 500/day
- Per-MCP server limits (e.g., Terraform: 2/min)
- Per-action limits for high-risk operations
- Circuit breaker for emergency stops

#### 3. **Approval Workflow**
- Manual approval required for high-risk actions
- Auto-approval for safe, read-only operations
- Slack notifications for approval requests
- 30-minute approval timeout
- Authorized approver validation

#### 4. **Comprehensive Audit Logging**
- JSONL format for all orchestrator activity
- Logs observations, decisions, actions, results
- Sensitive data masking (passwords, tokens, keys)
- Security event logging
- 365-day retention by default
- Compliance support (SOC 2, ISO 27001, HIPAA)

#### 5. **Vault Integration**
- Centralized secrets management
- No credentials in code or environment variables
- Dynamic secrets generation
- Secret versioning and rotation
- Audit logging of secret access

### Safety Features
- **Dry Run Mode**: Test without executing actions
- **Auto-Remediation Toggle**: Require manual approval for actions
- **Severity-Based Escalation**: Only high/critical issues trigger PagerDuty
- **Slack Notifications**: All decisions logged with security stats
- **Context History**: All cycles logged for post-incident analysis
- **Security Statistics**: Track blocked/executed actions per cycle

## Setup

### Prerequisites

- Python 3.9+
- Anthropic API key
- Access credentials for your infrastructure (Kubernetes, AWS, etc.)
- API keys for observability and communication tools

### Installation

```bash
cd ai-sre-stack
pip install -r requirements.txt
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your API keys and configuration:
```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key

# Enable MCP servers by providing their credentials
# Leave blank to disable a specific server

# Kubernetes
KUBECONFIG_PATH=/path/to/kubeconfig
K8S_NAMESPACE=default

# AWS
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Datadog
DATADOG_API_KEY=your_datadog_api_key
DATADOG_APP_KEY=your_datadog_app_key

# ... (see .env.example for all options)
```

3. Create runbooks directory and add custom runbooks:
```bash
mkdir -p runbooks
# Add your YAML runbook files
```

## Usage

### Run Single Cycle (Dry Run)

Test the system without executing actions:

```bash
python sre_orchestrator.py
```

Set `dry_run = True` in `config.py` or set environment variable.

### Run Continuous Monitoring

For production monitoring with auto-remediation:

```python
# In config.py, set:
dry_run = False
auto_remediation = True
observation_interval = 60  # seconds
```

Then run:
```bash
python sre_orchestrator.py
```

### Custom Interval

```bash
# Edit sre_orchestrator.py main() function:
await orchestrator.run_continuous(interval=120)  # 2 minutes
```

## How It Works

### 1. Observe Phase
- All enabled MCP servers collect current state
- Kubernetes: pod status, events, deployments
- AWS: instance health, costs
- Datadog: active alerts, metrics
- PagerDuty: open incidents
- Argo CD: sync status
- GitHub: recent PRs, workflow runs

### 2. Decide Phase
- Observations sent to Claude as context
- Claude analyzes:
  - System health across all domains
  - Correlation between infrastructure, observability, and deployment states
  - Severity assessment
  - Root cause analysis
- Claude recommends specific actions with parameters

### 3. Act Phase (with Security Controls)
- **Security Check 1**: Action whitelist validation
- **Security Check 2**: Rate limiting check
- **Security Check 3**: Approval workflow
  - High-risk actions require manual approval
  - Slack notification sent to incident channel
  - 30-minute approval timeout
- **Pre-execution**: Audit log with approver info
- **Execution**: Orchestrator executes approved actions
- Actions can span multiple domains:
  - Scale Kubernetes deployment
  - Post Slack notification
  - Create PagerDuty incident
  - Rollback Argo CD deployment
  - Archive GuardDuty finding
  - Rotate secrets in Vault
- **Post-execution**: Record in rate limiter, audit log result
- Results logged with security statistics

## Example Scenarios

### Scenario 1: High CPU Usage
1. **Observe**: Datadog alerts high CPU, Kubernetes shows pod at 95%
2. **Decide**: Claude recommends scaling deployment
3. **Act**: Scale deployment, notify Slack, monitor recovery

### Scenario 2: Failed Deployment
1. **Observe**: Argo CD shows out-of-sync, GitHub shows recent merge
2. **Decide**: Claude recommends rollback and incident creation
3. **Act**: Rollback deployment, create PagerDuty incident, post to Slack

### Scenario 3: Cost Spike
1. **Observe**: AWS shows 200% cost increase, EC2 instances increased
2. **Decide**: Claude identifies orphaned instances
3. **Act**: Terminate unused instances, notify team

## Runbook Format

Create YAML runbooks in `runbooks/` directory:

```yaml
id: high_cpu_usage
title: High CPU Usage Remediation
category: performance
severity: high
tags: [performance, cpu, kubernetes]
description: Steps to remediate high CPU usage

steps:
  - name: Check metrics
    action: datadog
    command: query_metrics
    params:
      query: "avg:kubernetes.cpu.usage{*}"
    
  - name: Scale deployment
    action: kubernetes
    command: scale_deployment
    params:
      replicas: auto
    
  - name: Notify team
    action: slack
    command: post_message
    params:
      text: "Scaled deployment due to high CPU"
```

## Safety Features

- **Dry Run Mode**: Test without executing actions
- **Auto-Remediation Toggle**: Require manual approval for actions
- **Severity-Based Escalation**: Only high/critical issues trigger PagerDuty
- **Slack Notifications**: All decisions logged to Slack
- **Context History**: All cycles logged for post-incident analysis

## Development

### Adding New MCP Servers

1. Create new server in `mcp_servers/new_server_mcp.py`
2. Inherit from `BaseMCPServer`
3. Implement `_connect()`, `observe()`, `act()`, `_health_check()`
4. Add configuration to `config.py`
5. Import and initialize in `sre_orchestrator.py`

### Testing Individual MCP Servers

```python
import asyncio
from mcp_servers import KubernetesMCP

async def test():
    mcp = KubernetesMCP({'kubeconfig_path': '~/.kube/config', 'namespace': 'default'})
    await mcp.initialize()
    observation = await mcp.observe()
    print(observation)

asyncio.run(test())
```

## Troubleshooting

**MCP server initialization fails:**
- Check API keys and credentials in `.env`
- Verify network connectivity to services
- Review logs for specific error messages

**Claude not making good decisions:**
- Review observation data - ensure MCP servers returning useful info
- Adjust temperature in config (lower = more conservative)
- Add more context to prompts

**Actions not executing:**
- Check `auto_remediation = True` in config
- Verify MCP server has required permissions
- Review dry_run setting

## Security Considerations

### Built-in Security Controls
The system includes comprehensive security hardening:
- **Action Whitelist**: Only approved actions can execute
- **Rate Limiting**: Protection against runaway automation
- **Approval Workflow**: Human oversight for high-risk actions
- **Audit Logging**: Full accountability and compliance
- **Vault Integration**: Secure secrets management

See [SECURITY_HARDENING_GUIDE.md](SECURITY_HARDENING_GUIDE.md) for complete details.

### Best Practices
- Store credentials in Vault (never in `.env` or code)
- Use read-only credentials where possible during testing
- Enable all security controls in production
- Review audit logs regularly
- Start with dry-run mode before enabling auto-remediation
- Use Kubernetes RBAC with least privilege
- Rotate API keys via Vault regularly
- Monitor security statistics per cycle

### Compliance Support
- **SOC 2**: Audit logging, approval workflow, access control
- **ISO 27001**: Security controls, audit trails, access management
- **HIPAA**: Audit logging, sensitive data masking
- **PCI DSS**: Audit trails, access control, change management

## Documentation

- **[README.md](README.md)** - This file (getting started)
- **[QUICK_START.md](QUICK_START.md)** - Quick start guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture
- **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** - Implementation checklist
- **[SECURITY_HARDENING_GUIDE.md](SECURITY_HARDENING_GUIDE.md)** - Complete security guide
- **[SECURITY_MCP_GUIDE.md](SECURITY_MCP_GUIDE.md)** - GuardDuty & CloudTrail guide
- **[SECURITY_HARDENING_COMPLETE.md](SECURITY_HARDENING_COMPLETE.md)** - Implementation summary

## License

MIT License

## Contributing

Contributions welcome! Please submit pull requests with:
- New MCP server implementations
- Additional runbook templates
- Improved decision-making prompts
- Bug fixes and improvements
