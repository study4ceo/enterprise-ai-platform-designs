"""Action whitelisting for security control."""

from typing import Dict, Any, List, Set
from datetime import datetime, time as dt_time
import logging

logger = logging.getLogger(__name__)


class ActionWhitelist:
    """Controls which actions can be executed by the orchestrator."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize action whitelist.
        
        Args:
            config: Whitelist configuration
        """
        self.config = config or {}
        
        # Default whitelisted actions (safe, read-only operations)
        self.whitelisted_actions: Dict[str, Set[str]] = {
            'kubernetes': {'observe', 'get_logs', 'health_check'},
            'aws': {'observe', 'get_metrics', 'health_check'},
            'terraform': {'validate', 'plan', 'health_check'},
            'datadog': {'observe', 'query_metrics', 'get_dashboard', 'health_check'},
            'pagerduty': {'observe', 'list_incidents', 'add_note', 'health_check'},
            'github': {'observe', 'list_prs', 'list_issues', 'comment_pr', 'health_check'},
            'argocd': {'observe', 'get_app_details', 'refresh_app', 'health_check'},
            'slack': {'observe', 'post_message', 'health_check'},
            'runbook': {'observe', 'get_runbook', 'search_runbooks', 'health_check'},
            'guardduty': {'observe', 'get_finding_details', 'health_check'},
            'cloudtrail': {'observe', 'lookup_events', 'health_check'},
            'vault': {'observe', 'read_secret', 'health_check'}
        }
        
        # High-risk actions requiring special approval
        self.high_risk_actions: Dict[str, Set[str]] = {
            'kubernetes': {'delete_pod', 'scale_deployment', 'restart_pod'},
            'aws': {'stop_instance', 'terminate_instance', 'delete_bucket'},
            'terraform': {'apply', 'destroy'},
            'argocd': {'sync_app', 'rollback_app'},
            'vault': {'delete_secret', 'write_secret'}
        }
        
        # Blocked actions (never allowed)
        self.blocked_actions: Dict[str, Set[str]] = {
            'aws': {'terminate_all_instances'},
            'kubernetes': {'delete_namespace'},
            'terraform': {'destroy_all'}
        }
        
        # Time-based restrictions
        self.maintenance_windows = self.config.get('maintenance_windows', {})
        
        # Load custom whitelist from config
        if 'custom_whitelist' in self.config:
            self._load_custom_whitelist(self.config['custom_whitelist'])
    
    def _load_custom_whitelist(self, custom: Dict[str, List[str]]):
        """Load custom whitelist from configuration."""
        for mcp_server, actions in custom.items():
            if mcp_server not in self.whitelisted_actions:
                self.whitelisted_actions[mcp_server] = set()
            self.whitelisted_actions[mcp_server].update(actions)
    
    def is_allowed(self, mcp_server: str, action: str) -> tuple[bool, str]:
        """Check if an action is allowed.
        
        Args:
            mcp_server: MCP server name
            action: Action name
            
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        # Check if blocked
        if self._is_blocked(mcp_server, action):
            return False, f"Action {action} on {mcp_server} is permanently blocked"
        
        # Check if whitelisted
        if not self._is_whitelisted(mcp_server, action):
            return False, f"Action {action} on {mcp_server} is not whitelisted"
        
        # Check time restrictions
        if not self._is_within_allowed_time(mcp_server, action):
            return False, f"Action {action} on {mcp_server} not allowed outside maintenance window"
        
        return True, "Action allowed"
    
    def _is_blocked(self, mcp_server: str, action: str) -> bool:
        """Check if action is in blocklist."""
        return action in self.blocked_actions.get(mcp_server, set())
    
    def _is_whitelisted(self, mcp_server: str, action: str) -> bool:
        """Check if action is whitelisted."""
        return action in self.whitelisted_actions.get(mcp_server, set())
    
    def _is_within_allowed_time(self, mcp_server: str, action: str) -> bool:
        """Check if action is allowed at current time."""
        # If no time restrictions, always allowed
        if not self.maintenance_windows:
            return True
        
        # Check if this action has time restrictions
        restrictions = self.maintenance_windows.get(mcp_server, {}).get(action)
        if not restrictions:
            return True  # No restrictions for this action
        
        current_time = datetime.now().time()
        current_day = datetime.now().strftime('%A').lower()
        
        # Check if current day is allowed
        allowed_days = restrictions.get('days', ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
        if current_day not in allowed_days:
            return False
        
        # Check if current time is within window
        start_time = dt_time.fromisoformat(restrictions.get('start_time', '00:00:00'))
        end_time = dt_time.fromisoformat(restrictions.get('end_time', '23:59:59'))
        
        return start_time <= current_time <= end_time
    
    def is_high_risk(self, mcp_server: str, action: str) -> bool:
        """Check if action is considered high-risk.
        
        Args:
            mcp_server: MCP server name
            action: Action name
            
        Returns:
            True if action is high-risk
        """
        return action in self.high_risk_actions.get(mcp_server, set())
    
    def add_to_whitelist(self, mcp_server: str, action: str):
        """Add an action to the whitelist.
        
        Args:
            mcp_server: MCP server name
            action: Action name
        """
        if mcp_server not in self.whitelisted_actions:
            self.whitelisted_actions[mcp_server] = set()
        
        self.whitelisted_actions[mcp_server].add(action)
        logger.info(f"Added {action} on {mcp_server} to whitelist")
    
    def remove_from_whitelist(self, mcp_server: str, action: str):
        """Remove an action from the whitelist.
        
        Args:
            mcp_server: MCP server name
            action: Action name
        """
        if mcp_server in self.whitelisted_actions:
            self.whitelisted_actions[mcp_server].discard(action)
            logger.info(f"Removed {action} on {mcp_server} from whitelist")
    
    def get_allowed_actions(self, mcp_server: str) -> List[str]:
        """Get all allowed actions for an MCP server.
        
        Args:
            mcp_server: MCP server name
            
        Returns:
            List of allowed action names
        """
        return list(self.whitelisted_actions.get(mcp_server, set()))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get whitelist statistics.
        
        Returns:
            Statistics dictionary
        """
        total_whitelisted = sum(len(actions) for actions in self.whitelisted_actions.values())
        total_high_risk = sum(len(actions) for actions in self.high_risk_actions.values())
        total_blocked = sum(len(actions) for actions in self.blocked_actions.values())
        
        return {
            "total_whitelisted_actions": total_whitelisted,
            "total_high_risk_actions": total_high_risk,
            "total_blocked_actions": total_blocked,
            "mcp_servers_configured": len(self.whitelisted_actions),
            "maintenance_windows_configured": len(self.maintenance_windows)
        }
