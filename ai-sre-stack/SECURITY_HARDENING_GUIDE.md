# Security Hardening Guide

## Overview

The AI SRE Stack includes comprehensive security hardening features to ensure safe, controlled, and auditable automation. This guide covers all five security components and how to use them effectively.

## Security Components

### 1. HashiCorp Vault Integration (Secrets Management)

**Purpose**: Centralized secrets management to prevent credential exposure.

**Features**:
- Secure storage and retrieval of API keys, passwords, tokens
- Dynamic secrets generation
- Secret versioning and rotation
- Audit logging of secret access
- TTL-based lease management

**Configuration**:
```bash
# .env file
VAULT_URL=http://localhost:8200
VAULT_TOKEN=your_vault_token
VAULT_MOUNT_POINT=secret
```

**Usage**:
```python
# Store a secret
vault_mcp.act('write_secret', {
    'path': 'prod/database',
    'data': {
        'username': 'admin',
        'password': 'secure_password'
    }
})

# Retrieve a secret
vault_mcp.act('read_secret', {
    'path': 'prod/database'
})

# Delete a secret
vault_mcp.act('delete_secret', {
    'path': 'prod/database'
})
```

**Vault MCP Actions**:
- `observe`: Check Vault health and seal status
- `read_secret`: Retrieve a secret from specified path
- `write_secret`: Store a secret (high-risk - requires approval)
- `delete_secret`: Remove a secret (high-risk - requires approval)
- `list_secrets`: List available secret paths
- `health_check`: Verify Vault connection

**Best Practices**:
- Never store credentials in code or environment variables
- Use short TTLs for dynamic secrets
- Rotate static secrets regularly
- Enable audit logging in Vault itself
- Use namespaces for multi-tenant environments

---

### 2. Action Whitelisting

**Purpose**: Define which actions are allowed to execute, preventing unauthorized or dangerous operations.

**Features**:
- Whitelisted actions (safe, approved operations)
- High-risk actions (require additional approval)
- Blocked actions (permanently forbidden)
- Time-based restrictions (maintenance windows)
- Per-MCP server configuration

**Configuration**:
```python
# In config.py or via environment
SECURITY_ENABLE_ACTION_WHITELIST=true
```

**Default Whitelisted Actions**:
- **Read-only operations**: `observe`, `get_logs`, `query_metrics`, `list_*`, `read_*`
- **Safe operations**: `health_check`, `refresh_app`, `post_message`, `add_note`

**High-Risk Actions** (Require Approval):
- `delete_pod`, `scale_deployment`, `restart_pod` (Kubernetes)
- `stop_instance`, `terminate_instance` (AWS)
- `apply`, `destroy` (Terraform)
- `sync_app`, `rollback_app` (Argo CD)
- `write_secret`, `delete_secret` (Vault)

**Blocked Actions** (Never Allowed):
- `terminate_all_instances` (AWS)
- `delete_namespace` (Kubernetes)
- `destroy_all` (Terraform)

**Custom Whitelist**:
```python
custom_whitelist = {
    'kubernetes': ['scale_deployment', 'restart_pod'],
    'aws': ['stop_instance']
}
```

**Time-Based Restrictions**:
```python
maintenance_windows = {
    'terraform': {
        'apply': {
            'days': ['saturday', 'sunday'],
            'start_time': '02:00:00',
            'end_time': '06:00:00'
        }
    }
}
```

**How It Works**:
1. Before executing any action, the orchestrator checks the whitelist
2. If action is blocked → rejected immediately
3. If action is not whitelisted → rejected
4. If outside maintenance window → rejected
5. If whitelisted → proceeds to next security check

**Security Events Logged**:
- `action_blocked_whitelist`: Action rejected by whitelist

---

### 3. Rate Limiting / Throttling

**Purpose**: Prevent runaway automation and protect against infinite loops or cascading failures.

**Features**:
- Global rate limits (system-wide)
- Per-MCP server limits
- Per-action type limits
- Circuit breaker for emergency stop
- Sliding window algorithm

**Configuration**:
```bash
SECURITY_ENABLE_RATE_LIMITING=true
SECURITY_MAX_ACTIONS_PER_MINUTE=10
SECURITY_MAX_ACTIONS_PER_HOUR=100
SECURITY_MAX_ACTIONS_PER_DAY=500
```

**Default Rate Limits**:

**Global Limits**:
- 10 actions per minute
- 100 actions per hour
- 500 actions per day

**Per-MCP Limits**:
- Kubernetes: 5/min, 50/hour
- AWS: 5/min, 50/hour
- Terraform: 2/min, 10/hour
- Vault: 10/min, 100/hour

**Per-Action Limits** (High-Risk):
- `terminate_instance`: 5/hour, 20/day
- `delete_pod`: 10/hour, 50/day
- `scale_deployment`: 2/min, 10/hour
- `rollback_app`: 5/hour, 20/day

**Circuit Breaker**:
- Threshold: 50 actions in 5 minutes
- When triggered: All actions blocked for 5 minutes
- Purpose: Emergency stop for runaway automation

**How It Works**:
1. Before executing action, check all applicable rate limits
2. If any limit exceeded → reject action
3. If circuit breaker open → reject all actions
4. If within limits → proceed to next security check
5. After execution → record action timestamp

**Security Events Logged**:
- `action_blocked_rate_limit`: Action rejected due to rate limit
- Circuit breaker triggers logged as critical events

**Monitoring**:
```python
# Get rate limiter statistics
stats = throttle.get_stats()
# {
#   "actions_last_minute": 5,
#   "actions_last_hour": 23,
#   "actions_last_day": 145,
#   "circuit_breaker_open": False
# }
```

---

### 4. Comprehensive Audit Logging

**Purpose**: Record all orchestrator activity for compliance, security analysis, and forensics.

**Features**:
- JSONL format (one JSON per line)
- Logs observations, decisions, actions, results
- Sensitive data masking
- Security event logging
- Approval decision logging
- Retention management

**Configuration**:
```bash
SECURITY_ENABLE_AUDIT_LOGGING=true
SECURITY_AUDIT_LOG_PATH=./logs/audit.jsonl
SECURITY_MASK_SENSITIVE=true
```

**What Gets Logged**:

**1. Observations** (Phase 1):
```json
{
  "event_type": "observation",
  "cycle_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "observations": {...},
  "server_count": 12,
  "healthy_count": 11
}
```

**2. Decisions** (Phase 2):
```json
{
  "event_type": "decision",
  "cycle_id": "uuid",
  "timestamp": "2024-01-15T10:30:05Z",
  "decision": {
    "analysis": "...",
    "severity": "high",
    "issues": ["..."],
    "recommended_action_count": 3
  }
}
```

**3. Actions** (Phase 3 - Pre-execution):
```json
{
  "event_type": "action",
  "cycle_id": "uuid",
  "timestamp": "2024-01-15T10:30:10Z",
  "mcp_server": "kubernetes",
  "action": "scale_deployment",
  "params": {"replicas": 5},
  "reason": "High CPU utilization",
  "approved_by": "admin",
  "user": "claude-orchestrator"
}
```

**4. Action Results** (Phase 3 - Post-execution):
```json
{
  "event_type": "action_result",
  "cycle_id": "uuid",
  "timestamp": "2024-01-15T10:30:12Z",
  "mcp_server": "kubernetes",
  "action": "scale_deployment",
  "success": true,
  "execution_time_ms": 1543.2
}
```

**5. Security Events**:
```json
{
  "event_type": "security_event",
  "security_event_type": "action_blocked_whitelist",
  "cycle_id": "uuid",
  "timestamp": "2024-01-15T10:30:15Z",
  "severity": "medium",
  "description": "Action blocked by whitelist",
  "details": {...}
}
```

**6. Approval Events**:
```json
{
  "event_type": "approval",
  "cycle_id": "uuid",
  "timestamp": "2024-01-15T10:30:20Z",
  "action": "terminate_instance",
  "mcp_server": "aws",
  "approved": true,
  "approver": "admin",
  "reason": "Confirmed failed instance"
}
```

**Sensitive Data Masking**:
Automatically masks fields containing:
- `password`, `secret`, `token`, `key`, `credential`, `api_key`, `access_key`

Example:
```json
{
  "params": {
    "username": "admin",
    "password": "***MASKED***",
    "api_key": "***MASKED***"
  }
}
```

**Query Audit Log**:
```python
# Query by time range
entries = audit_logger.query_audit_log(
    start_time=datetime(2024, 1, 15),
    end_time=datetime(2024, 1, 16),
    event_type="action",
    limit=100
)

# Get statistics
stats = audit_logger.get_stats()
# {
#   "total_entries": 15234,
#   "file_size_mb": 45.6,
#   "retention_days": 365
# }
```

**External Integrations** (Future):
- Elasticsearch for search and visualization
- S3 for long-term archival
- SIEM integration for security monitoring

---

### 5. Approval Workflow

**Purpose**: Require human approval for high-risk actions before execution.

**Features**:
- Auto-approval for low-risk actions
- Manual approval for high-risk actions
- Timeout mechanism (30 minutes default)
- Slack notifications for approval requests
- Authorized approver list
- Approval history tracking

**Configuration**:
```bash
SECURITY_ENABLE_APPROVAL_WORKFLOW=true
SECURITY_REQUIRE_APPROVAL_FOR_HIGH_RISK=true
SECURITY_REQUIRE_APPROVAL_FOR_CRITICAL=true
SECURITY_AUTO_APPROVE_LOW_SEVERITY=true
```

**Auto-Approval Rules**:

**Always Auto-Approved**:
- Read-only operations (`observe`, `get_*`, `list_*`, `read_*`)
- Low severity incidents (if `AUTO_APPROVE_LOW_SEVERITY=true`)

**Requires Manual Approval**:
- High-risk actions (see whitelist section)
- Critical severity incidents
- Actions during business hours (configurable)

**Approval Process**:

1. **Action Proposed**: Claude recommends a high-risk action
2. **Approval Request Created**: System generates approval request
3. **Notification Sent**: Slack message sent to incident channel
4. **Wait for Decision**: System waits up to 30 minutes
5. **Execute or Timeout**: Action executes if approved, blocks if denied/timeout

**Slack Notification Format**:
```
⚠️ APPROVAL REQUIRED

Request ID: `abc-123-def-456`
Action: scale_deployment on kubernetes
Severity: HIGH
Reason: CPU utilization above 90%
Expires: 2024-01-15 11:00:00 UTC

To approve or deny, use the approval API or CLI.
```

**Approval API** (Future Enhancement):
```bash
# Approve action
curl -X POST /api/approvals/abc-123-def-456/approve \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"approver": "admin", "reason": "Verified high load"}'

# Deny action
curl -X POST /api/approvals/abc-123-def-456/deny \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"approver": "admin", "reason": "Not necessary"}'
```

**Approval Workflow States**:
- `PENDING`: Waiting for decision
- `APPROVED`: Approved by authorized user
- `DENIED`: Denied by authorized user
- `EXPIRED`: Timeout reached (30 min default)
- `AUTO_APPROVED`: Automatically approved by policy

**Statistics**:
```python
stats = approval_workflow.get_stats()
# {
#   "pending_count": 2,
#   "history_count": 145,
#   "status_breakdown": {
#     "auto_approved": 120,
#     "approved": 15,
#     "denied": 5,
#     "expired": 5
#   }
# }
```

---

## Security Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Recommends Action                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  1. Action Whitelist   │
            │  Check if allowed      │
            └────────┬───────────────┘
                     │ Allowed
                     ▼
            ┌────────────────────────┐
            │  2. Rate Limiting      │
            │  Check if within limit │
            └────────┬───────────────┘
                     │ Within Limit
                     ▼
            ┌────────────────────────┐
            │  3. Approval Workflow  │
            │  Auto or manual?       │
            └────────┬───────────────┘
                     │ Approved
                     ▼
            ┌────────────────────────┐
            │  4. Audit Log          │
            │  Log pre-execution     │
            └────────┬───────────────┘
                     │
                     ▼
            ┌────────────────────────┐
            │  5. Execute Action     │
            │  via MCP server        │
            └────────┬───────────────┘
                     │
                     ▼
            ┌────────────────────────┐
            │  6. Record in Throttle │
            │  Update rate limit     │
            └────────┬───────────────┘
                     │
                     ▼
            ┌────────────────────────┐
            │  7. Audit Log Result   │
            │  Log post-execution    │
            └────────────────────────┘
```

## Security Best Practices

### 1. Start Conservative
- Enable all security controls initially
- Use dry-run mode for testing
- Review audit logs regularly
- Gradually relax policies as confidence builds

### 2. Least Privilege
- Only whitelist necessary actions
- Use time-based restrictions for risky operations
- Require approval for production changes
- Limit authorized approvers

### 3. Defense in Depth
- All five security layers work together
- Even if one layer fails, others provide protection
- Whitelist prevents unauthorized actions
- Rate limiting prevents abuse
- Approval adds human oversight
- Audit log provides accountability
- Vault protects credentials

### 4. Monitoring and Alerting
- Review audit logs daily
- Monitor rate limit violations
- Track approval patterns
- Alert on circuit breaker triggers
- Investigate security events

### 5. Incident Response
- Approval workflow provides time to assess
- Audit log provides forensics
- Circuit breaker provides emergency stop
- Vault allows credential rotation

### 6. Compliance
- Audit logs support SOC 2, ISO 27001, HIPAA
- Sensitive data masking protects PII
- Approval workflow provides separation of duties
- Retention settings meet regulatory requirements

## Configuration Examples

### Development Environment
```bash
# More relaxed for testing
SECURITY_ENABLE_ACTION_WHITELIST=true
SECURITY_ENABLE_RATE_LIMITING=true
SECURITY_ENABLE_AUDIT_LOGGING=true
SECURITY_ENABLE_APPROVAL_WORKFLOW=false  # Disabled for speed

SECURITY_MAX_ACTIONS_PER_MINUTE=20
SECURITY_MAX_ACTIONS_PER_HOUR=200
SECURITY_AUTO_APPROVE_LOW_SEVERITY=true
```

### Production Environment
```bash
# Maximum security
SECURITY_ENABLE_ACTION_WHITELIST=true
SECURITY_ENABLE_RATE_LIMITING=true
SECURITY_ENABLE_AUDIT_LOGGING=true
SECURITY_ENABLE_APPROVAL_WORKFLOW=true

SECURITY_MAX_ACTIONS_PER_MINUTE=5
SECURITY_MAX_ACTIONS_PER_HOUR=50
SECURITY_REQUIRE_APPROVAL_FOR_HIGH_RISK=true
SECURITY_REQUIRE_APPROVAL_FOR_CRITICAL=true
SECURITY_AUTO_APPROVE_LOW_SEVERITY=false  # Require approval for everything
```

## Testing Security Controls

### Test 1: Whitelist Blocking
```python
# Try to execute a blocked action
result = await orchestrator.act({
    'recommended_actions': [{
        'mcp_server': 'aws',
        'action': 'terminate_all_instances',  # Blocked!
        'params': {},
        'reason': 'Testing'
    }]
})
# Expected: Blocked by whitelist
```

### Test 2: Rate Limiting
```python
# Execute many actions rapidly
for i in range(20):
    await orchestrator.act({
        'recommended_actions': [{
            'mcp_server': 'kubernetes',
            'action': 'scale_deployment',
            'params': {'replicas': i},
            'reason': 'Load test'
        }]
    })
# Expected: Some actions blocked by rate limiter
```

### Test 3: Approval Workflow
```python
# Try high-risk action
result = await orchestrator.act({
    'severity': 'critical',
    'recommended_actions': [{
        'mcp_server': 'aws',
        'action': 'terminate_instance',
        'params': {'instance_id': 'i-12345'},
        'reason': 'Failed instance'
    }]
})
# Expected: Approval required, Slack notification sent
```

### Test 4: Audit Logging
```python
# Check audit log after actions
entries = audit_logger.query_audit_log(
    event_type='action',
    limit=10
)
print(f"Found {len(entries)} action log entries")
```

## Troubleshooting

### Actions Being Blocked Unexpectedly
1. Check whitelist configuration
2. Review maintenance windows
3. Verify action name matches exactly
4. Check audit log for `action_blocked_whitelist` events

### Rate Limiting Too Aggressive
1. Increase limits in configuration
2. Add per-MCP exceptions
3. Review action frequency patterns
4. Check if circuit breaker triggered

### Approval Workflow Not Working
1. Verify Slack MCP is enabled
2. Check authorized approvers list
3. Review approval timeout setting
4. Check for expired approval requests

### Audit Log Growing Too Large
1. Implement log rotation
2. Archive old logs to S3
3. Reduce logged event types
4. Adjust retention period

## Future Enhancements

1. **Web UI for Approvals**: Browser-based approval interface
2. **Machine Learning**: Learn from approval patterns
3. **Risk Scoring**: Dynamic risk assessment per action
4. **Integration**: SIEM, Elasticsearch, Splunk
5. **Multi-Factor Auth**: For approvals
6. **Scheduled Actions**: Pre-approved maintenance windows
7. **Rollback Capability**: Automatic action reversal

## Conclusion

The five-layer security architecture provides comprehensive protection:
1. **Vault**: Protects credentials
2. **Whitelist**: Defines allowed actions
3. **Rate Limiting**: Prevents abuse
4. **Approval Workflow**: Adds human oversight
5. **Audit Logging**: Ensures accountability

Together, these layers enable safe, controlled, and auditable AI-driven SRE automation.
