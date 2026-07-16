"""Configuration management for AI SRE Stack."""

import os
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class AnthropicConfig(BaseModel):
    """Anthropic API configuration."""
    api_key: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.7


class KubernetesConfig(BaseModel):
    """Kubernetes MCP configuration."""
    enabled: bool = True
    kubeconfig_path: str = Field(default_factory=lambda: os.getenv("KUBECONFIG_PATH", "~/.kube/config"))
    namespace: str = Field(default_factory=lambda: os.getenv("K8S_NAMESPACE", "default"))


class AWSConfig(BaseModel):
    """AWS MCP configuration."""
    enabled: bool = True
    access_key_id: str = Field(default_factory=lambda: os.getenv("AWS_ACCESS_KEY_ID", ""))
    secret_access_key: str = Field(default_factory=lambda: os.getenv("AWS_SECRET_ACCESS_KEY", ""))
    region: str = Field(default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"))


class TerraformConfig(BaseModel):
    """Terraform MCP configuration."""
    enabled: bool = True
    workspace_path: str = Field(default_factory=lambda: os.getenv("TERRAFORM_WORKSPACE", "./terraform"))
    state_bucket: str = Field(default_factory=lambda: os.getenv("TERRAFORM_STATE_BUCKET", ""))


class DatadogConfig(BaseModel):
    """Datadog MCP configuration."""
    enabled: bool = True
    api_key: str = Field(default_factory=lambda: os.getenv("DATADOG_API_KEY", ""))
    app_key: str = Field(default_factory=lambda: os.getenv("DATADOG_APP_KEY", ""))
    site: str = Field(default_factory=lambda: os.getenv("DATADOG_SITE", "datadoghq.com"))


class PagerDutyConfig(BaseModel):
    """PagerDuty MCP configuration."""
    enabled: bool = True
    api_key: str = Field(default_factory=lambda: os.getenv("PAGERDUTY_API_KEY", ""))
    service_id: str = Field(default_factory=lambda: os.getenv("PAGERDUTY_SERVICE_ID", ""))


class GitHubConfig(BaseModel):
    """GitHub MCP configuration."""
    enabled: bool = True
    token: str = Field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    org: str = Field(default_factory=lambda: os.getenv("GITHUB_ORG", ""))
    repo: str = Field(default_factory=lambda: os.getenv("GITHUB_REPO", ""))


class ArgoCDConfig(BaseModel):
    """Argo CD MCP configuration."""
    enabled: bool = True
    server: str = Field(default_factory=lambda: os.getenv("ARGOCD_SERVER", ""))
    token: str = Field(default_factory=lambda: os.getenv("ARGOCD_TOKEN", ""))


class SlackConfig(BaseModel):
    """Slack MCP configuration."""
    enabled: bool = True
    bot_token: str = Field(default_factory=lambda: os.getenv("SLACK_BOT_TOKEN", ""))
    channel: str = Field(default_factory=lambda: os.getenv("SLACK_CHANNEL", "#incidents"))


class RunbookConfig(BaseModel):
    """Incident Runbook MCP configuration."""
    enabled: bool = True
    runbook_path: str = Field(default_factory=lambda: os.getenv("RUNBOOK_PATH", "./runbooks"))


class GuardDutyConfig(BaseModel):
    """AWS GuardDuty MCP configuration."""
    enabled: bool = True
    access_key_id: str = Field(default_factory=lambda: os.getenv("AWS_ACCESS_KEY_ID", ""))
    secret_access_key: str = Field(default_factory=lambda: os.getenv("AWS_SECRET_ACCESS_KEY", ""))
    region: str = Field(default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"))


class CloudTrailConfig(BaseModel):
    """AWS CloudTrail MCP configuration."""
    enabled: bool = True
    access_key_id: str = Field(default_factory=lambda: os.getenv("AWS_ACCESS_KEY_ID", ""))
    secret_access_key: str = Field(default_factory=lambda: os.getenv("AWS_SECRET_ACCESS_KEY", ""))
    region: str = Field(default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"))
    trail_name: str = Field(default_factory=lambda: os.getenv("CLOUDTRAIL_TRAIL_NAME", ""))


class VaultConfig(BaseModel):
    """HashiCorp Vault MCP configuration."""
    enabled: bool = True
    url: str = Field(default_factory=lambda: os.getenv("VAULT_URL", "http://localhost:8200"))
    token: str = Field(default_factory=lambda: os.getenv("VAULT_TOKEN", ""))
    mount_point: str = Field(default_factory=lambda: os.getenv("VAULT_MOUNT_POINT", "secret"))


class SecurityConfig(BaseModel):
    """Security control configuration."""
    # Action whitelisting
    enable_action_whitelist: bool = True
    custom_whitelist: Dict[str, List[str]] = {}
    maintenance_windows: Dict[str, Any] = {}
    
    # Rate limiting
    enable_rate_limiting: bool = True
    max_actions_per_minute: int = 10
    max_actions_per_hour: int = 100
    max_actions_per_day: int = 500
    
    # Audit logging
    enable_audit_logging: bool = True
    audit_log_path: str = "./logs/audit.jsonl"
    log_observations: bool = True
    log_decisions: bool = True
    log_actions: bool = True
    mask_sensitive: bool = True
    
    # Approval workflow
    enable_approval_workflow: bool = True
    require_approval_for_high_risk: bool = True
    require_approval_for_critical: bool = True
    auto_approve_low_severity: bool = True
    authorized_approvers: List[str] = ["admin", "sre-team"]


class SREConfig(BaseModel):
    """Main SRE Stack configuration."""
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig)
    kubernetes: KubernetesConfig = Field(default_factory=KubernetesConfig)
    aws: AWSConfig = Field(default_factory=AWSConfig)
    terraform: TerraformConfig = Field(default_factory=TerraformConfig)
    datadog: DatadogConfig = Field(default_factory=DatadogConfig)
    pagerduty: PagerDutyConfig = Field(default_factory=PagerDutyConfig)
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    argocd: ArgoCDConfig = Field(default_factory=ArgoCDConfig)
    slack: SlackConfig = Field(default_factory=SlackConfig)
    runbook: RunbookConfig = Field(default_factory=RunbookConfig)
    guardduty: GuardDutyConfig = Field(default_factory=GuardDutyConfig)
    cloudtrail: CloudTrailConfig = Field(default_factory=CloudTrailConfig)
    vault: VaultConfig = Field(default_factory=VaultConfig)
    
    # Security controls
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    # Orchestration settings
    observation_interval: int = 60  # seconds
    decision_threshold: float = 0.7
    auto_remediation: bool = True
    dry_run: bool = False


# Global configuration instance
config = SREConfig()


def get_enabled_mcps() -> Dict[str, Any]:
    """Get all enabled MCP configurations."""
    enabled = {}
    
    if config.kubernetes.enabled:
        enabled['kubernetes'] = config.kubernetes
    if config.aws.enabled:
        enabled['aws'] = config.aws
    if config.terraform.enabled:
        enabled['terraform'] = config.terraform
    if config.datadog.enabled:
        enabled['datadog'] = config.datadog
    if config.pagerduty.enabled:
        enabled['pagerduty'] = config.pagerduty
    if config.github.enabled:
        enabled['github'] = config.github
    if config.argocd.enabled:
        enabled['argocd'] = config.argocd
    if config.slack.enabled:
        enabled['slack'] = config.slack
    if config.runbook.enabled:
        enabled['runbook'] = config.runbook
    if config.guardduty.enabled:
        enabled['guardduty'] = config.guardduty
    if config.cloudtrail.enabled:
        enabled['cloudtrail'] = config.cloudtrail
    if config.vault.enabled:
        enabled['vault'] = config.vault
    
    return enabled
