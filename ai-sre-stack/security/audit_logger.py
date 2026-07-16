"""Comprehensive audit logging for compliance and security."""

from typing import Dict, Any, Optional
from datetime import datetime
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditLogger:
    """Comprehensive audit logging for all orchestrator actions."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize audit logger.
        
        Args:
            config: Audit logging configuration
        """
        self.config = config or {}
        
        # Audit log storage location
        self.audit_log_path = Path(self.config.get('audit_log_path', './logs/audit.jsonl'))
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Retention settings
        self.retention_days = self.config.get('retention_days', 365)
        
        # What to log
        self.log_observations = self.config.get('log_observations', True)
        self.log_decisions = self.config.get('log_decisions', True)
        self.log_actions = self.config.get('log_actions', True)
        self.log_action_results = self.config.get('log_action_results', True)
        
        # Sensitive data masking
        self.mask_sensitive = self.config.get('mask_sensitive', True)
        self.sensitive_keys = {'password', 'secret', 'token', 'key', 'credential', 'api_key', 'access_key'}
        
        # External integrations
        self.elasticsearch_url = self.config.get('elasticsearch_url')
        self.s3_bucket = self.config.get('s3_bucket')
        
        logger.info(f"Audit logger initialized: {self.audit_log_path}")
    
    def log_observation(self, observations: Dict[str, Any], cycle_id: str):
        """Log observation phase.
        
        Args:
            observations: Observations from all MCP servers
            cycle_id: Unique cycle identifier
        """
        if not self.log_observations:
            return
        
        audit_entry = {
            "event_type": "observation",
            "cycle_id": cycle_id,
            "timestamp": datetime.utcnow().isoformat(),
            "observations": self._mask_sensitive_data(observations),
            "server_count": len(observations),
            "healthy_count": sum(1 for obs in observations.values() if obs.get('status') == 'healthy')
        }
        
        self._write_audit_entry(audit_entry)
    
    def log_decision(self, decision: Dict[str, Any], observations: Dict[str, Any], cycle_id: str):
        """Log decision phase.
        
        Args:
            decision: Claude's decision
            observations: Context used for decision
            cycle_id: Unique cycle identifier
        """
        if not self.log_decisions:
            return
        
        audit_entry = {
            "event_type": "decision",
            "cycle_id": cycle_id,
            "timestamp": datetime.utcnow().isoformat(),
            "decision": {
                "analysis": decision.get('analysis'),
                "severity": decision.get('severity'),
                "issues": decision.get('issues', []),
                "recommended_action_count": len(decision.get('recommended_actions', []))
            },
            "context_summary": {
                "server_count": len(observations),
                "overall_status": self._determine_overall_status(observations)
            }
        }
        
        self._write_audit_entry(audit_entry)
    
    def log_action(
        self,
        mcp_server: str,
        action: str,
        params: Dict[str, Any],
        reason: str,
        cycle_id: str,
        decision_id: Optional[str] = None,
        approved_by: Optional[str] = None
    ):
        """Log action execution.
        
        Args:
            mcp_server: MCP server name
            action: Action name
            params: Action parameters
            reason: Reason for action
            cycle_id: Unique cycle identifier
            decision_id: Decision that triggered this action
            approved_by: Who approved the action (if applicable)
        """
        if not self.log_actions:
            return
        
        audit_entry = {
            "event_type": "action",
            "cycle_id": cycle_id,
            "decision_id": decision_id,
            "timestamp": datetime.utcnow().isoformat(),
            "mcp_server": mcp_server,
            "action": action,
            "params": self._mask_sensitive_data(params),
            "reason": reason,
            "approved_by": approved_by,
            "user": "claude-orchestrator"
        }
        
        self._write_audit_entry(audit_entry)
    
    def log_action_result(
        self,
        mcp_server: str,
        action: str,
        result: Dict[str, Any],
        cycle_id: str,
        execution_time_ms: Optional[float] = None
    ):
        """Log action result.
        
        Args:
            mcp_server: MCP server name
            action: Action name
            result: Action result
            cycle_id: Unique cycle identifier
            execution_time_ms: Execution time in milliseconds
        """
        if not self.log_action_results:
            return
        
        audit_entry = {
            "event_type": "action_result",
            "cycle_id": cycle_id,
            "timestamp": datetime.utcnow().isoformat(),
            "mcp_server": mcp_server,
            "action": action,
            "success": result.get('success', False),
            "error": result.get('error'),
            "execution_time_ms": execution_time_ms,
            "result_summary": self._summarize_result(result)
        }
        
        self._write_audit_entry(audit_entry)
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        details: Dict[str, Any],
        cycle_id: Optional[str] = None
    ):
        """Log security-related events.
        
        Args:
            event_type: Type of security event
            severity: Event severity
            description: Event description
            details: Additional details
            cycle_id: Associated cycle ID
        """
        audit_entry = {
            "event_type": "security_event",
            "security_event_type": event_type,
            "cycle_id": cycle_id,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": severity,
            "description": description,
            "details": self._mask_sensitive_data(details)
        }
        
        self._write_audit_entry(audit_entry)
        
        # Also log to standard logger for visibility
        log_func = getattr(logger, severity.lower(), logger.info)
        log_func(f"Security Event: {event_type} - {description}")
    
    def log_approval(
        self,
        action: str,
        mcp_server: str,
        approved: bool,
        approver: str,
        reason: str,
        cycle_id: str
    ):
        """Log approval decisions.
        
        Args:
            action: Action requiring approval
            mcp_server: MCP server
            approved: Whether approved or denied
            approver: Who made the decision
            reason: Approval/denial reason
            cycle_id: Cycle identifier
        """
        audit_entry = {
            "event_type": "approval",
            "cycle_id": cycle_id,
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "mcp_server": mcp_server,
            "approved": approved,
            "approver": approver,
            "reason": reason
        }
        
        self._write_audit_entry(audit_entry)
    
    def _write_audit_entry(self, entry: Dict[str, Any]):
        """Write audit entry to log file.
        
        Args:
            entry: Audit entry to write
        """
        try:
            # Write to JSONL file (one JSON object per line)
            with open(self.audit_log_path, 'a') as f:
                f.write(json.dumps(entry) + '\n')
            
            # Send to external systems if configured
            if self.elasticsearch_url:
                self._send_to_elasticsearch(entry)
            
            if self.s3_bucket:
                self._send_to_s3(entry)
                
        except Exception as e:
            logger.error(f"Failed to write audit entry: {e}")
    
    def _mask_sensitive_data(self, data: Any) -> Any:
        """Mask sensitive data in audit logs.
        
        Args:
            data: Data to mask
            
        Returns:
            Masked data
        """
        if not self.mask_sensitive:
            return data
        
        if isinstance(data, dict):
            masked = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.sensitive_keys):
                    masked[key] = "***MASKED***"
                else:
                    masked[key] = self._mask_sensitive_data(value)
            return masked
        
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        
        else:
            return data
    
    def _determine_overall_status(self, observations: Dict[str, Any]) -> str:
        """Determine overall system status from observations.
        
        Args:
            observations: Observations dict
            
        Returns:
            Overall status string
        """
        statuses = [obs.get('status', 'unknown') for obs in observations.values()]
        
        if 'critical' in statuses:
            return 'critical'
        elif 'unhealthy' in statuses:
            return 'unhealthy'
        elif 'degraded' in statuses:
            return 'degraded'
        elif all(s == 'healthy' for s in statuses):
            return 'healthy'
        else:
            return 'mixed'
    
    def _summarize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of action result for audit log.
        
        Args:
            result: Full result dict
            
        Returns:
            Summarized result
        """
        return {
            "success": result.get('success', False),
            "message": result.get('message', ''),
            "has_error": 'error' in result,
            "keys": list(result.keys())
        }
    
    def _send_to_elasticsearch(self, entry: Dict[str, Any]):
        """Send audit entry to Elasticsearch.
        
        Args:
            entry: Audit entry
        """
        # TODO: Implement Elasticsearch integration
        pass
    
    def _send_to_s3(self, entry: Dict[str, Any]):
        """Send audit entry to S3 for long-term storage.
        
        Args:
            entry: Audit entry
        """
        # TODO: Implement S3 integration
        pass
    
    def query_audit_log(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[str] = None,
        mcp_server: Optional[str] = None,
        limit: int = 100
    ) -> list[Dict[str, Any]]:
        """Query audit log.
        
        Args:
            start_time: Start time filter
            end_time: End time filter
            event_type: Event type filter
            mcp_server: MCP server filter
            limit: Maximum results
            
        Returns:
            List of audit entries
        """
        results = []
        
        try:
            with open(self.audit_log_path, 'r') as f:
                for line in f:
                    if len(results) >= limit:
                        break
                    
                    entry = json.loads(line)
                    
                    # Apply filters
                    if start_time and datetime.fromisoformat(entry['timestamp']) < start_time:
                        continue
                    if end_time and datetime.fromisoformat(entry['timestamp']) > end_time:
                        continue
                    if event_type and entry.get('event_type') != event_type:
                        continue
                    if mcp_server and entry.get('mcp_server') != mcp_server:
                        continue
                    
                    results.append(entry)
            
        except Exception as e:
            logger.error(f"Failed to query audit log: {e}")
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audit logger statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            line_count = sum(1 for _ in open(self.audit_log_path))
            file_size = self.audit_log_path.stat().st_size
            
            return {
                "audit_log_path": str(self.audit_log_path),
                "total_entries": line_count,
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / 1024 / 1024, 2),
                "retention_days": self.retention_days,
                "mask_sensitive": self.mask_sensitive
            }
        except Exception:
            return {
                "audit_log_path": str(self.audit_log_path),
                "error": "Unable to read audit log"
            }
