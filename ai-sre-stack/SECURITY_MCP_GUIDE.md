# Security MCP Servers - Guide

## Overview

We've added **2 powerful security MCP servers** to enhance threat detection, audit logging, and incident response capabilities:

1. **AWS GuardDuty MCP** - Intelligent threat detection
2. **AWS CloudTrail MCP** - Comprehensive audit logging

These integrate seamlessly with the existing 9 MCP servers, giving Claude visibility into security events and the ability to respond automatically.

---

## 🔐 AWS GuardDuty MCP

### What It Does

GuardDuty is AWS's intelligent threat detection service that continuously monitors for:
- **Reconnaissance** - Port scanning, unusual API activity
- **Instance Compromise** - Malware, cryptocurrency mining, backdoors
- **Account Compromise** - Credential misuse, unusual IAM activity
- **Bucket Compromise** - S3 data exfiltration, unauthorized access

### Features Implemented

#### **Observe Phase:**
```python
{
  "status": "critical",  # or healthy, degraded, unhealthy
  "findings": [
    {
      "type": "UnauthorizedAccess:EC2/TorIPCaller",
      "severity": 8.0,
      "severity_label": "HIGH",
      "title": "EC2 instance communicating with Tor network",
      "resource": {
        "instance_id": "i-1234567890abcdef0",
        "instance_type": "t2.micro"
      },
      "action": {
        "type": "NetworkConnectionAction",
        "network": {
          "remote_ip": "198.51.100.42",
          "remote_country": "Unknown",
          "blocked": false
        }
      }
    }
  ],
  "severity_breakdown": {
    "critical": 2,
    "high": 5,
    "medium": 10,
    "low": 3
  }
}
```

#### **Actions Available:**
- `archive_findings` - Mark findings as resolved
- `unarchive_findings` - Reopen archived findings
- `get_finding_details` - Get full details on specific findings
- `create_sample_findings` - Generate test findings for development
- `update_findings_feedback` - Mark findings as useful/not useful

### Use Cases

**1. Compromised EC2 Instance Detection**
```
Observe: GuardDuty detects instance communicating with known malicious IP
Decide: Claude analyzes - instance likely compromised
Act: 
  - Stop EC2 instance
  - Create PagerDuty incident
  - Post Slack alert
  - Archive GuardDuty finding after remediation
```

**2. Credential Compromise**
```
Observe: GuardDuty detects IAM credentials used from unusual location
Decide: Claude determines credentials may be compromised
Act:
  - Deactivate access keys
  - Force password reset
  - Alert security team
  - Review CloudTrail for full activity timeline
```

**3. S3 Data Exfiltration**
```
Observe: GuardDuty detects unusual S3 API calls from suspicious IP
Decide: Claude assesses potential data breach
Act:
  - Block IP at security group level
  - Review S3 access logs
  - Create incident ticket
  - Notify compliance team
```

---

## 📋 AWS CloudTrail MCP

### What It Does

CloudTrail provides comprehensive audit logging of all AWS API activity:
- **Who** - Which user or role made the call
- **What** - Which API was called (e.g., TerminateInstances, DeleteBucket)
- **When** - Timestamp of the action
- **Where** - Source IP address and location
- **Why** - Success or failure, error messages

### Features Implemented

#### **Observe Phase:**
```python
{
  "status": "healthy",
  "trails": [
    {
      "name": "my-organization-trail",
      "is_logging": true,
      "s3_bucket": "my-cloudtrail-bucket",
      "is_multi_region": true
    }
  ],
  "recent_events": [
    {
      "event_name": "TerminateInstances",
      "username": "admin@company.com",
      "event_time": "2026-07-15T10:30:00Z",
      "source_ip": "203.0.113.42",
      "resources": ["i-1234567890abcdef0"],
      "is_security_relevant": true
    }
  ],
  "anomalies": [
    {
      "type": "root_account_usage",
      "severity": "critical",
      "description": "Root account activity detected"
    }
  ],
  "event_type_breakdown": {
    "ConsoleLogin": 45,
    "DescribeInstances": 32,
    "PutObject": 28
  }
}
```

#### **Actions Available:**
- `start_logging` - Enable CloudTrail logging
- `stop_logging` - Disable CloudTrail logging (use with caution!)
- `lookup_events` - Query events by user, event name, resource, time
- `get_event_details` - Get full JSON details of specific event
- `create_trail` - Create new CloudTrail configuration

### Built-in Anomaly Detection

CloudTrail MCP automatically detects:

**1. High Error Rate**
```
Trigger: >10 failed API calls in 15 minutes
Severity: Medium
Meaning: Potential unauthorized access attempts or misconfiguration
```

**2. Security Activity Spike**
```
Trigger: >5 security-relevant events in 15 minutes
Severity: High
Security Events: IAM changes, security group modifications, instance terminations
```

**3. Root Account Usage**
```
Trigger: Any root account activity
Severity: Critical
Best Practice: Root account should never be used for daily operations
```

### Use Cases

**1. Unauthorized API Activity Investigation**
```
Observe: CloudTrail shows unusual API calls from unknown IP
Decide: Claude correlates with GuardDuty findings
Act:
  - Lookup all events from that IP
  - Identify compromised credentials
  - Revoke access
  - Create incident report
```

**2. Compliance Auditing**
```
Observe: CloudTrail tracks all infrastructure changes
Decide: Claude identifies changes without proper approvals
Act:
  - Generate compliance report
  - Alert audit team
  - Rollback unauthorized changes
```

**3. Incident Timeline Reconstruction**
```
Observe: Security incident detected
Decide: Claude needs to understand what happened
Act:
  - Query CloudTrail for 24-hour timeline
  - Identify all actions by compromised user
  - Document incident timeline
  - Export for forensics
```

---

## 🤝 Integration with Existing MCP Servers

Claude can now make **correlated security decisions** across all 11 MCP servers:

### Example 1: Multi-Domain Security Response

**Scenario:** GuardDuty detects compromised instance

```
OBSERVE:
  - GuardDuty: High-severity finding on i-abc123
  - CloudTrail: Unusual API calls from same instance
  - Kubernetes: Instance is running production pods
  - AWS: Instance has IAM role with S3 access
  - Datadog: Instance showing high network egress

DECIDE (Claude):
  "Compromised EC2 instance detected. It's running production workloads
   and has S3 access. High risk of data exfiltration. Immediate isolation
   required."

ACT:
  1. AWS: Stop EC2 instance
  2. Kubernetes: Drain pods to healthy nodes
  3. AWS: Revoke IAM role credentials
  4. GuardDuty: Archive finding after remediation
  5. PagerDuty: Create critical incident
  6. Slack: Alert #security-incidents channel
  7. GitHub: Create post-mortem issue
  8. CloudTrail: Export logs for forensics
```

### Example 2: Insider Threat Detection

**Scenario:** CloudTrail detects suspicious administrative activity

```
OBSERVE:
  - CloudTrail: Admin user deleting security groups at 3 AM
  - GuardDuty: No specific findings (yet)
  - AWS: Multiple instances now exposed to internet
  - GitHub: No authorized change requests for this modification
  - PagerDuty: No open maintenance windows

DECIDE (Claude):
  "Unauthorized security group deletion detected outside maintenance
   windows with no approval. Potential insider threat or compromised
   admin account."

ACT:
  1. AWS: Recreate deleted security groups (from Terraform state)
  2. CloudTrail: Get full activity timeline for this user
  3. AWS: Suspend admin user credentials immediately
  4. PagerDuty: Create critical security incident
  5. Slack: Alert security team + CTO
  6. GitHub: Create security incident ticket
  7. Terraform: Verify and reapply correct configurations
```

---

## 📖 Setup Instructions

### 1. Prerequisites

**Enable GuardDuty:**
```bash
aws guardduty create-detector --enable
```

**Enable CloudTrail:**
```bash
# Create S3 bucket for logs
aws s3 mb s3://my-cloudtrail-logs

# Create trail
aws cloudtrail create-trail \
  --name my-organization-trail \
  --s3-bucket-name my-cloudtrail-logs \
  --is-multi-region-trail

# Start logging
aws cloudtrail start-logging --name my-organization-trail
```

### 2. Configure Environment

Add to your `.env` file:

```bash
# AWS Credentials (shared with AWS MCP)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Optional: Specific CloudTrail trail name
CLOUDTRAIL_TRAIL_NAME=my-organization-trail
```

### 3. Enable in Config

Both MCP servers are enabled by default if AWS credentials are configured. To disable:

```python
# config.py
class GuardDutyConfig(BaseModel):
    enabled: bool = False  # Disable GuardDuty MCP

class CloudTrailConfig(BaseModel):
    enabled: bool = False  # Disable CloudTrail MCP
```

### 4. Test

```python
import asyncio
from mcp_servers import GuardDutyMCP, CloudTrailMCP

async def test():
    # Test GuardDuty
    gd_config = {
        'access_key_id': 'YOUR_KEY',
        'secret_access_key': 'YOUR_SECRET',
        'region': 'us-east-1'
    }
    guardduty = GuardDutyMCP(gd_config)
    await guardduty.initialize()
    findings = await guardduty.observe()
    print("GuardDuty Findings:", findings)
    
    # Test CloudTrail
    ct_config = {
        'access_key_id': 'YOUR_KEY',
        'secret_access_key': 'YOUR_SECRET',
        'region': 'us-east-1'
    }
    cloudtrail = CloudTrailMCP(ct_config)
    await cloudtrail.initialize()
    events = await cloudtrail.observe()
    print("CloudTrail Events:", events)

asyncio.run(test())
```

---

## 🎯 Best Practices

### GuardDuty

1. **Enable in all regions** - Threats can come from anywhere
2. **Review findings daily** - Don't ignore medium/low severity
3. **Archive resolved findings** - Keep your console clean
4. **Integrate with SIEM** - Forward findings to your security platform
5. **Test with sample findings** - Validate your response procedures

### CloudTrail

1. **Never disable logging** - Always keep CloudTrail enabled
2. **Use multi-region trails** - Capture activity in all regions
3. **Enable log file validation** - Detect tampering
4. **Retain logs long-term** - Keep at least 1 year for compliance
5. **Monitor for anomalies** - Watch for unusual patterns

### Combined Usage

1. **Correlate data** - Use both together for complete visibility
2. **Automate responses** - Let Claude handle routine security incidents
3. **Create runbooks** - Document response procedures
4. **Regular testing** - Run security drills using sample findings
5. **Continuous improvement** - Update runbooks based on real incidents

---

## 🚨 Security Runbook

We've included a comprehensive security runbook: `runbooks/security_incident_response.yaml`

**Steps included:**
1. Check GuardDuty findings
2. Review CloudTrail context
3. Identify affected resources
4. Isolate compromised instances
5. Revoke suspicious credentials
6. Alert security team (PagerDuty + Slack)
7. Document incident (GitHub issue)
8. Archive findings after remediation

---

## 📊 Metrics to Monitor

### GuardDuty Metrics
- Total active findings
- Critical/high severity count
- Time to remediation
- False positive rate
- Findings by type (recon, compromise, etc.)

### CloudTrail Metrics
- API call volume
- Failed authentication attempts
- Security-relevant events count
- Root account usage incidents
- Compliance audit readiness

---

## 🔮 Future Enhancements

Potential additions:

1. **AWS Security Hub MCP** - Centralized security findings
2. **AWS IAM Access Analyzer MCP** - Identify overly permissive policies
3. **AWS Config MCP** - Configuration compliance monitoring
4. **VPC Flow Logs MCP** - Network traffic analysis
5. **AWS Macie MCP** - S3 data classification and protection

---

## Summary

You now have **11 MCP servers total**:

**Original 9:**
1. Kubernetes
2. AWS (EC2/Compute)
3. Terraform
4. Datadog
5. PagerDuty
6. GitHub
7. Argo CD
8. Slack
9. Runbook

**New Security MCPs:**
10. **AWS GuardDuty** - Threat detection
11. **AWS CloudTrail** - Audit logging

Claude can now **detect, analyze, and respond to security threats automatically** while correlating data across your entire infrastructure stack! 🔐🚀
