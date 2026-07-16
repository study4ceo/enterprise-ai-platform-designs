"""Main SRE Orchestrator - Claude as the central decision-making agent."""

import asyncio
import logging
import uuid
import signal
import sys
from typing import Dict, Any, List
from datetime import datetime
from anthropic import Anthropic
from config import config, get_enabled_mcps
from mcp_servers import (
    KubernetesMCP, AWSMCP, TerraformMCP,
    DatadogMCP, PagerDutyMCP,
    GitHubMCP, ArgoCDMCP,
    SlackMCP, RunbookMCP,
    GuardDutyMCP, CloudTrailMCP, VaultMCP
)
from security import ActionWhitelist, ActionThrottle, AuditLogger, ApprovalWorkflow

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SREOrchestrator:
    """AI SRE Stack Orchestrator using Claude for decision-making."""
    
    def __init__(self):
        """Initialize the SRE orchestrator."""
        self.anthropic = Anthropic(api_key=config.anthropic.api_key)
        self.mcp_servers = {}
        self.context_history = []
        self.shutdown_requested = False
        
        # Initialize security controls
        if config.security.enable_action_whitelist:
            self.action_whitelist = ActionWhitelist({
                'custom_whitelist': config.security.custom_whitelist,
                'maintenance_windows': config.security.maintenance_windows
            })
            logger.info("✓ Action whitelist enabled")
        else:
            self.action_whitelist = None
        
        if config.security.enable_rate_limiting:
            self.action_throttle = ActionThrottle({
                'max_actions_per_minute': config.security.max_actions_per_minute,
                'max_actions_per_hour': config.security.max_actions_per_hour,
                'max_actions_per_day': config.security.max_actions_per_day
            })
            logger.info("✓ Rate limiting enabled")
        else:
            self.action_throttle = None
        
        if config.security.enable_audit_logging:
            self.audit_logger = AuditLogger({
                'audit_log_path': config.security.audit_log_path,
                'log_observations': config.security.log_observations,
                'log_decisions': config.security.log_decisions,
                'log_actions': config.security.log_actions,
                'mask_sensitive': config.security.mask_sensitive
            })
            logger.info("✓ Audit logging enabled")
        else:
            self.audit_logger = None
        
        if config.security.enable_approval_workflow:
            self.approval_workflow = ApprovalWorkflow({
                'require_approval_for_high_risk': config.security.require_approval_for_high_risk,
                'require_approval_for_critical': config.security.require_approval_for_critical,
                'auto_approve_low_severity': config.security.auto_approve_low_severity,
                'authorized_approvers': config.security.authorized_approvers
            })
            # Set notification callback
            self.approval_workflow.set_notification_callback(self._send_approval_notification)
            logger.info("✓ Approval workflow enabled")
        else:
            self.approval_workflow = None
        
    async def initialize(self):
        """Initialize all enabled MCP servers."""
        logger.info("Initializing AI SRE Stack...")
        
        enabled_mcps = get_enabled_mcps()
        
        # Initialize MCP servers based on configuration
        mcp_classes = {
            'kubernetes': KubernetesMCP,
            'aws': AWSMCP,
            'terraform': TerraformMCP,
            'datadog': DatadogMCP,
            'pagerduty': PagerDutyMCP,
            'github': GitHubMCP,
            'argocd': ArgoCDMCP,
            'slack': SlackMCP,
            'runbook': RunbookMCP,
            'guardduty': GuardDutyMCP,
            'cloudtrail': CloudTrailMCP,
            'vault': VaultMCP
        }
        
        for name, mcp_config in enabled_mcps.items():
            if name in mcp_classes:
                try:
                    mcp_instance = mcp_classes[name](mcp_config.model_dump())
                    success = await mcp_instance.initialize()
                    if success:
                        self.mcp_servers[name] = mcp_instance
                        logger.info(f"✓ {name.capitalize()} MCP initialized")
                    else:
                        logger.warning(f"✗ {name.capitalize()} MCP initialization failed")
                except Exception as e:
                    logger.error(f"✗ Failed to initialize {name}: {e}")
        
        logger.info(f"Initialized {len(self.mcp_servers)}/{len(enabled_mcps)} MCP servers")
    
    async def observe(self, cycle_id: str = None) -> Dict[str, Any]:
        """
        OBSERVE phase: Gather state from all MCP servers.
        
        Args:
            cycle_id: Unique cycle identifier for audit logging
        
        Returns:
            Aggregated observations from all servers
        """
        logger.info("=== OBSERVE PHASE ===")
        observations = {}
        
        for name, server in self.mcp_servers.items():
            try:
                observation = await server.observe()
                observations[name] = observation
                logger.info(f"📊 {name}: {observation.get('status', 'unknown')}")
            except Exception as e:
                logger.error(f"Failed to observe {name}: {e}")
                observations[name] = {"error": str(e), "status": "error"}
        
        # Log observations if audit logging enabled
        if self.audit_logger and cycle_id:
            self.audit_logger.log_observation(observations, cycle_id)
        
        return observations
    
    async def decide(self, observations: Dict[str, Any], cycle_id: str = None) -> Dict[str, Any]:
        """
        DECIDE phase: Use Claude to analyze observations and decide on actions.
        
        Args:
            observations: Current state from all MCP servers
            cycle_id: Unique cycle identifier for audit logging
            
        Returns:
            Decision including recommended actions
        """
        logger.info("=== DECIDE PHASE ===")
        
        # Build context for Claude
        context = self._build_context(observations)
        
        # Create prompt for Claude
        prompt = f"""You are an AI SRE agent managing a distributed system with multiple infrastructure, observability, CI/CD, and communication tools.

Current System State:
{context}

Your tasks:
1. Analyze the current state across all systems
2. Identify any issues, anomalies, or optimization opportunities
3. Recommend specific actions to take (or state "no action needed" if everything is healthy)
4. For each action, specify which MCP server to use and what parameters

Respond in JSON format:
{{
    "analysis": "Your analysis of the current state",
    "severity": "low|medium|high|critical",
    "issues": ["List of identified issues"],
    "recommended_actions": [
        {{
            "mcp_server": "server_name",
            "action": "action_name",
            "params": {{}},
            "reason": "Why this action is needed"
        }}
    ]
}}
"""
        
        try:
            # Call Claude for decision-making
            response = self.anthropic.messages.create(
                model=config.anthropic.model,
                max_tokens=config.anthropic.max_tokens,
                temperature=config.anthropic.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            decision_text = response.content[0].text
            logger.info(f"🤖 Claude's Analysis:\n{decision_text}")
            
            # Parse Claude's response
            import json
            decision = json.loads(decision_text)
            
            # Log decision if audit logging enabled
            if self.audit_logger and cycle_id:
                self.audit_logger.log_decision(decision, observations, cycle_id)
            
            return decision
            
        except Exception as e:
            logger.error(f"Decision-making failed: {e}")
            return {
                "analysis": f"Error during decision-making: {e}",
                "severity": "high",
                "issues": ["Decision-making failure"],
                "recommended_actions": []
            }
    
    async def act(self, decision: Dict[str, Any], cycle_id: str = None) -> Dict[str, Any]:
        """
        ACT phase: Execute recommended actions with security controls.
        
        Args:
            decision: Decision from Claude including recommended actions
            cycle_id: Unique cycle identifier for audit logging
            
        Returns:
            Results of executed actions
        """
        logger.info("=== ACT PHASE ===")
        
        if config.dry_run:
            logger.info("🔒 DRY RUN MODE - No actions will be executed")
            return {"dry_run": True, "actions": decision.get('recommended_actions', [])}
        
        if not config.auto_remediation:
            logger.info("🔒 AUTO-REMEDIATION DISABLED - Awaiting manual approval")
            return {"auto_remediation": False, "actions": decision.get('recommended_actions', [])}
        
        results = []
        actions = decision.get('recommended_actions', [])
        severity = decision.get('severity', 'medium')
        
        if not actions:
            logger.info("✓ No actions required - system healthy")
            return {"message": "No actions required", "results": []}
        
        # Security statistics
        security_stats = {
            "total_actions": len(actions),
            "blocked_by_whitelist": 0,
            "blocked_by_rate_limit": 0,
            "required_approval": 0,
            "auto_approved": 0,
            "executed": 0,
            "failed": 0
        }
        
        for action_spec in actions:
            try:
                mcp_name = action_spec.get('mcp_server')
                action_name = action_spec.get('action')
                params = action_spec.get('params', {})
                reason = action_spec.get('reason', '')
                
                if mcp_name not in self.mcp_servers:
                    logger.warning(f"⚠ MCP server '{mcp_name}' not available")
                    security_stats['failed'] += 1
                    continue
                
                logger.info(f"⚡ Processing action: {action_name} on {mcp_name}")
                logger.info(f"   Reason: {reason}")
                
                # === SECURITY CHECK 1: Action Whitelist ===
                if self.action_whitelist:
                    allowed, whitelist_reason = self.action_whitelist.is_allowed(mcp_name, action_name)
                    if not allowed:
                        logger.warning(f"🚫 Action blocked by whitelist: {whitelist_reason}")
                        security_stats['blocked_by_whitelist'] += 1
                        
                        if self.audit_logger and cycle_id:
                            self.audit_logger.log_security_event(
                                event_type="action_blocked_whitelist",
                                severity="medium",
                                description=f"Action {action_name} on {mcp_name} blocked by whitelist",
                                details={"mcp_server": mcp_name, "action": action_name, "reason": whitelist_reason},
                                cycle_id=cycle_id
                            )
                        
                        results.append({
                            "mcp_server": mcp_name,
                            "action": action_name,
                            "blocked": True,
                            "reason": whitelist_reason
                        })
                        continue
                
                # === SECURITY CHECK 2: Rate Limiting ===
                if self.action_throttle:
                    can_execute, throttle_reason = self.action_throttle.can_execute(mcp_name, action_name)
                    if not can_execute:
                        logger.warning(f"🚫 Action blocked by rate limiter: {throttle_reason}")
                        security_stats['blocked_by_rate_limit'] += 1
                        
                        if self.audit_logger and cycle_id:
                            self.audit_logger.log_security_event(
                                event_type="action_blocked_rate_limit",
                                severity="high",
                                description=f"Action {action_name} on {mcp_name} blocked by rate limiter",
                                details={"mcp_server": mcp_name, "action": action_name, "reason": throttle_reason},
                                cycle_id=cycle_id
                            )
                        
                        results.append({
                            "mcp_server": mcp_name,
                            "action": action_name,
                            "blocked": True,
                            "reason": throttle_reason
                        })
                        continue
                
                # === SECURITY CHECK 3: Approval Workflow ===
                approved = True
                approver = None
                
                if self.approval_workflow:
                    # Check if action is high-risk
                    is_high_risk = self.action_whitelist.is_high_risk(mcp_name, action_name) if self.action_whitelist else False
                    
                    # Request approval (may auto-approve based on policy)
                    approval_request = await self.approval_workflow.request_approval(
                        mcp_server=mcp_name,
                        action=action_name,
                        params=params,
                        reason=reason,
                        severity=severity,
                        cycle_id=cycle_id or "no-cycle",
                        is_high_risk=is_high_risk
                    )
                    
                    if approval_request.status.value == 'auto_approved':
                        approved = True
                        approver = "system"
                        security_stats['auto_approved'] += 1
                        logger.info(f"✓ Action auto-approved")
                    elif approval_request.status.value == 'pending':
                        logger.warning(f"⏳ Action requires manual approval - waiting...")
                        security_stats['required_approval'] += 1
                        
                        # Wait for approval (with timeout)
                        approved = await self.approval_workflow.wait_for_approval(approval_request)
                        
                        if approved:
                            approver = approval_request.approver
                            logger.info(f"✓ Action approved by {approver}")
                        else:
                            logger.warning(f"🚫 Action denied or timeout")
                            
                            if self.audit_logger and cycle_id:
                                self.audit_logger.log_security_event(
                                    event_type="action_approval_denied",
                                    severity="medium",
                                    description=f"Action {action_name} on {mcp_name} not approved",
                                    details={"mcp_server": mcp_name, "action": action_name, "status": approval_request.status.value},
                                    cycle_id=cycle_id
                                )
                            
                            results.append({
                                "mcp_server": mcp_name,
                                "action": action_name,
                                "blocked": True,
                                "reason": "Approval denied or timeout"
                            })
                            continue
                
                if not approved:
                    continue
                
                # === AUDIT LOG: Pre-Execution ===
                if self.audit_logger and cycle_id:
                    self.audit_logger.log_action(
                        mcp_server=mcp_name,
                        action=action_name,
                        params=params,
                        reason=reason,
                        cycle_id=cycle_id,
                        approved_by=approver
                    )
                
                # === EXECUTE ACTION ===
                logger.info(f"⚡ Executing {action_name} on {mcp_name}")
                
                start_time = datetime.utcnow()
                result = await self.mcp_servers[mcp_name].act(action_name, params)
                execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Record action in throttle
                if self.action_throttle:
                    self.action_throttle.record_action(mcp_name, action_name)
                
                # === AUDIT LOG: Post-Execution ===
                if self.audit_logger and cycle_id:
                    self.audit_logger.log_action_result(
                        mcp_server=mcp_name,
                        action=action_name,
                        result=result,
                        cycle_id=cycle_id,
                        execution_time_ms=execution_time_ms
                    )
                
                # Store result
                results.append({
                    "mcp_server": mcp_name,
                    "action": action_name,
                    "result": result,
                    "reason": reason,
                    "execution_time_ms": execution_time_ms,
                    "approved_by": approver
                })
                
                if result.get('success'):
                    logger.info(f"✓ Action completed successfully ({execution_time_ms:.2f}ms)")
                    security_stats['executed'] += 1
                else:
                    logger.error(f"✗ Action failed: {result.get('error')}")
                    security_stats['failed'] += 1
                
            except Exception as e:
                logger.error(f"Failed to execute action: {e}")
                security_stats['failed'] += 1
                
                if self.audit_logger and cycle_id:
                    self.audit_logger.log_security_event(
                        event_type="action_execution_error",
                        severity="high",
                        description=f"Action {action_name} on {mcp_name} failed with exception",
                        details={"mcp_server": mcp_name, "action": action_name, "error": str(e)},
                        cycle_id=cycle_id
                    )
                
                results.append({
                    "mcp_server": mcp_name,
                    "action": action_name,
                    "error": str(e)
                })
        
        logger.info(f"Security stats: {security_stats}")
        return {"executed": True, "results": results, "security_stats": security_stats}
    
    async def run_cycle(self):
        """Run one complete Observe → Decide → Act cycle."""
        logger.info("\n" + "="*60)
        logger.info("Starting new SRE cycle...")
        logger.info("="*60)
        
        # Generate unique cycle ID
        cycle_id = str(uuid.uuid4())
        logger.info(f"Cycle ID: {cycle_id}")
        
        try:
            # Phase 1: Observe
            observations = await self.observe(cycle_id=cycle_id)
            
            # Phase 2: Decide
            decision = await self.decide(observations, cycle_id=cycle_id)
            
            # Phase 3: Act
            action_results = await self.act(decision, cycle_id=cycle_id)
            
            # Store context for learning
            self.context_history.append({
                "cycle_id": cycle_id,
                "observations": observations,
                "decision": decision,
                "action_results": action_results
            })
            
            # Log security statistics
            if 'security_stats' in action_results:
                logger.info(f"Security Summary: {action_results['security_stats']}")
            
            # Notify via Slack if configured
            if 'slack' in self.mcp_servers and decision.get('severity') in ['high', 'critical']:
                await self._notify_slack(decision, action_results, cycle_id)
            
            logger.info("Cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Cycle failed: {e}")
            
            if self.audit_logger:
                self.audit_logger.log_security_event(
                    event_type="cycle_failure",
                    severity="critical",
                    description=f"SRE cycle failed with exception",
                    details={"error": str(e)},
                    cycle_id=cycle_id
                )
    
    async def _notify_slack(self, decision: Dict[str, Any], action_results: Dict[str, Any], cycle_id: str = None):
        """Send notification to Slack about decisions and actions."""
        try:
            severity = decision.get('severity', 'unknown')
            analysis = decision.get('analysis', '')
            issues = decision.get('issues', [])
            
            emoji = {
                'low': ':information_source:',
                'medium': ':warning:',
                'high': ':rotating_light:',
                'critical': ':fire:'
            }.get(severity, ':question:')
            
            message = f"{emoji} *AI SRE Alert - {severity.upper()}*\n\n"
            if cycle_id:
                message += f"*Cycle ID:* `{cycle_id}`\n\n"
            
            message += f"*Analysis:*\n{analysis}\n\n"
            
            if issues:
                message += f"*Issues Detected:*\n"
                for issue in issues:
                    message += f"• {issue}\n"
            
            if action_results.get('executed'):
                message += f"\n*Actions Taken:*\n"
                for result in action_results.get('results', []):
                    action = result.get('action')
                    server = result.get('mcp_server')
                    
                    if result.get('blocked'):
                        message += f"🚫 {action} on {server} - {result.get('reason')}\n"
                    else:
                        status = "✓" if result.get('result', {}).get('success') else "✗"
                        message += f"{status} {action} on {server}\n"
                        if result.get('approved_by'):
                            message += f"   Approved by: {result.get('approved_by')}\n"
            
            # Add security stats if available
            if 'security_stats' in action_results:
                stats = action_results['security_stats']
                message += f"\n*Security Summary:*\n"
                message += f"• Executed: {stats.get('executed', 0)}/{stats.get('total_actions', 0)}\n"
                if stats.get('blocked_by_whitelist', 0) > 0:
                    message += f"• Blocked by whitelist: {stats['blocked_by_whitelist']}\n"
                if stats.get('blocked_by_rate_limit', 0) > 0:
                    message += f"• Blocked by rate limit: {stats['blocked_by_rate_limit']}\n"
                if stats.get('required_approval', 0) > 0:
                    message += f"• Required approval: {stats['required_approval']}\n"
            
            await self.mcp_servers['slack'].act('post_message', {
                'text': message
            })
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    async def _send_approval_notification(self, approval_request):
        """Send approval request notification via Slack.
        
        Args:
            approval_request: ApprovalRequest object
        """
        try:
            if 'slack' not in self.mcp_servers:
                logger.warning("Slack MCP not available for approval notification")
                return
            
            message = f":warning: *APPROVAL REQUIRED*\n\n"
            message += f"*Request ID:* `{approval_request.request_id}`\n"
            message += f"*Action:* {approval_request.action} on {approval_request.mcp_server}\n"
            message += f"*Severity:* {approval_request.severity.upper()}\n"
            message += f"*Reason:* {approval_request.reason}\n"
            message += f"*Expires:* {approval_request.expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            message += f"To approve or deny, use the approval API or CLI."
            
            await self.mcp_servers['slack'].act('post_message', {
                'text': message
            })
            
            logger.info(f"Approval notification sent to Slack for request {approval_request.request_id}")
            
        except Exception as e:
            logger.error(f"Failed to send approval notification: {e}")
    
    def _build_context(self, observations: Dict[str, Any]) -> str:
        """Build formatted context string from observations."""
        context_parts = []
        
        for server_name, observation in observations.items():
            context_parts.append(f"\n{server_name.upper()}:")
            context_parts.append(f"  Status: {observation.get('status', 'unknown')}")
            
            # Add server-specific details
            if 'error' in observation:
                context_parts.append(f"  Error: {observation['error']}")
            else:
                for key, value in observation.items():
                    if key != 'status' and not key.startswith('_'):
                        context_parts.append(f"  {key}: {value}")
        
        return "\n".join(context_parts)
    
    async def run_continuous(self, interval: int = None):
        """
        Run continuous monitoring loop.
        
        Args:
            interval: Seconds between cycles (uses config.observation_interval if not specified)
        """
        interval = interval or config.observation_interval
        logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        logger.info("Press Ctrl+C to stop gracefully...")
        
        try:
            while not self.shutdown_requested:
                await self.run_cycle()
                
                if not self.shutdown_requested:
                    logger.info(f"Sleeping for {interval} seconds...")
                    
                    # Sleep in small intervals to respond faster to shutdown
                    for _ in range(interval):
                        if self.shutdown_requested:
                            break
                        await asyncio.sleep(1)
                        
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
        finally:
            if not self.shutdown_requested:
                await self.shutdown()
    
    def request_shutdown(self):
        """Request graceful shutdown."""
        logger.info("\n" + "="*60)
        logger.info("🛑 Shutdown requested...")
        logger.info("="*60)
        self.shutdown_requested = True
    
    async def shutdown(self):
        """Shutdown all MCP servers gracefully."""
        if self.shutdown_requested:
            logger.info("Graceful shutdown already in progress...")
            return
        
        self.shutdown_requested = True
        logger.info("\n" + "="*60)
        logger.info("Shutting down AI SRE Stack...")
        logger.info("="*60)
        
        # Log shutdown event
        if self.audit_logger:
            try:
                self.audit_logger.log_security_event(
                    event_type="system_shutdown",
                    severity="info",
                    description="AI SRE Stack shutting down",
                    details={"reason": "graceful_shutdown", "active_mcps": len(self.mcp_servers)},
                    cycle_id="shutdown"
                )
            except Exception as e:
                logger.error(f"Error logging shutdown event: {e}")
        
        # Shutdown MCP servers
        shutdown_errors = []
        for name, server in self.mcp_servers.items():
            try:
                await server.shutdown()
                logger.info(f"✓ {name} shut down successfully")
            except Exception as e:
                logger.error(f"✗ Error shutting down {name}: {e}")
                shutdown_errors.append(f"{name}: {e}")
        
        # Final status
        if shutdown_errors:
            logger.warning(f"Shutdown completed with {len(shutdown_errors)} errors")
        else:
            logger.info("✓ All MCP servers shut down successfully")
        
        logger.info("="*60)
        logger.info("👋 AI SRE Stack stopped")
        logger.info("="*60)


async def main():
    """Main entry point."""
    orchestrator = SREOrchestrator()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        """Handle shutdown signals."""
        signal_name = signal.Signals(signum).name
        logger.info(f"\n⚠️  Received {signal_name} signal")
        orchestrator.request_shutdown()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Docker stop
    
    try:
        await orchestrator.initialize()
        
        # Run one cycle or continuous monitoring
        if config.dry_run:
            logger.info("Running single cycle in dry-run mode...")
            await orchestrator.run_cycle()
        else:
            await orchestrator.run_continuous()
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Interrupted by user")
        sys.exit(0)
