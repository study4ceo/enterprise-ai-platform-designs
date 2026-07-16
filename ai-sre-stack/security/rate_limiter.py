"""Rate limiting and throttling for action execution."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import deque
import logging

logger = logging.getLogger(__name__)


class ActionThrottle:
    """Rate limits action execution to prevent runaway automation."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize action throttle.
        
        Args:
            config: Rate limiting configuration
        """
        self.config = config or {}
        
        # Global rate limits
        self.max_actions_per_minute = self.config.get('max_actions_per_minute', 10)
        self.max_actions_per_hour = self.config.get('max_actions_per_hour', 100)
        self.max_actions_per_day = self.config.get('max_actions_per_day', 500)
        
        # Per-MCP rate limits
        self.per_mcp_limits = self.config.get('per_mcp_limits', {
            'kubernetes': {'per_minute': 5, 'per_hour': 50},
            'aws': {'per_minute': 5, 'per_hour': 50},
            'terraform': {'per_minute': 2, 'per_hour': 10},
            'vault': {'per_minute': 10, 'per_hour': 100}
        })
        
        # Per-action rate limits (for high-risk actions)
        self.per_action_limits = self.config.get('per_action_limits', {
            'terminate_instance': {'per_hour': 5, 'per_day': 20},
            'delete_pod': {'per_hour': 10, 'per_day': 50},
            'scale_deployment': {'per_minute': 2, 'per_hour': 10},
            'rollback_app': {'per_hour': 5, 'per_day': 20}
        })
        
        # Action history (stores timestamps)
        self.action_history: deque = deque(maxlen=1000)  # Last 1000 actions
        self.mcp_history: Dict[str, deque] = {}
        self.action_type_history: Dict[str, deque] = {}
        
        # Circuit breaker for runaway automation
        self.circuit_breaker_threshold = self.config.get('circuit_breaker_threshold', 50)
        self.circuit_breaker_window_minutes = self.config.get('circuit_breaker_window_minutes', 5)
        self.circuit_open = False
        self.circuit_open_until = None
    
    def can_execute(self, mcp_server: str, action: str) -> tuple[bool, str]:
        """Check if action can be executed within rate limits.
        
        Args:
            mcp_server: MCP server name
            action: Action name
            
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        # Check circuit breaker
        if self.circuit_open:
            if datetime.now() < self.circuit_open_until:
                return False, f"Circuit breaker open until {self.circuit_open_until}"
            else:
                self.circuit_open = False
                logger.info("Circuit breaker reset")
        
        # Check global limits
        if not self._check_global_limits():
            self._trigger_circuit_breaker()
            return False, "Global rate limit exceeded"
        
        # Check per-MCP limits
        if not self._check_mcp_limits(mcp_server):
            return False, f"Rate limit exceeded for {mcp_server}"
        
        # Check per-action limits
        if not self._check_action_limits(action):
            return False, f"Rate limit exceeded for action {action}"
        
        return True, "Within rate limits"
    
    def record_action(self, mcp_server: str, action: str):
        """Record an executed action.
        
        Args:
            mcp_server: MCP server name
            action: Action name
        """
        timestamp = datetime.now()
        
        # Record in global history
        self.action_history.append(timestamp)
        
        # Record in MCP-specific history
        if mcp_server not in self.mcp_history:
            self.mcp_history[mcp_server] = deque(maxlen=200)
        self.mcp_history[mcp_server].append(timestamp)
        
        # Record in action-specific history
        if action not in self.action_type_history:
            self.action_type_history[action] = deque(maxlen=100)
        self.action_type_history[action].append(timestamp)
        
        logger.debug(f"Recorded action: {action} on {mcp_server}")
    
    def _check_global_limits(self) -> bool:
        """Check global rate limits."""
        now = datetime.now()
        
        # Count actions in last minute
        one_minute_ago = now - timedelta(minutes=1)
        actions_last_minute = sum(1 for ts in self.action_history if ts > one_minute_ago)
        
        if actions_last_minute >= self.max_actions_per_minute:
            logger.warning(f"Global per-minute limit exceeded: {actions_last_minute}/{self.max_actions_per_minute}")
            return False
        
        # Count actions in last hour
        one_hour_ago = now - timedelta(hours=1)
        actions_last_hour = sum(1 for ts in self.action_history if ts > one_hour_ago)
        
        if actions_last_hour >= self.max_actions_per_hour:
            logger.warning(f"Global per-hour limit exceeded: {actions_last_hour}/{self.max_actions_per_hour}")
            return False
        
        # Count actions in last day
        one_day_ago = now - timedelta(days=1)
        actions_last_day = sum(1 for ts in self.action_history if ts > one_day_ago)
        
        if actions_last_day >= self.max_actions_per_day:
            logger.warning(f"Global per-day limit exceeded: {actions_last_day}/{self.max_actions_per_day}")
            return False
        
        return True
    
    def _check_mcp_limits(self, mcp_server: str) -> bool:
        """Check per-MCP rate limits."""
        if mcp_server not in self.per_mcp_limits:
            return True  # No limits configured
        
        limits = self.per_mcp_limits[mcp_server]
        history = self.mcp_history.get(mcp_server, deque())
        now = datetime.now()
        
        # Check per-minute limit
        if 'per_minute' in limits:
            one_minute_ago = now - timedelta(minutes=1)
            count = sum(1 for ts in history if ts > one_minute_ago)
            if count >= limits['per_minute']:
                logger.warning(f"{mcp_server} per-minute limit exceeded: {count}/{limits['per_minute']}")
                return False
        
        # Check per-hour limit
        if 'per_hour' in limits:
            one_hour_ago = now - timedelta(hours=1)
            count = sum(1 for ts in history if ts > one_hour_ago)
            if count >= limits['per_hour']:
                logger.warning(f"{mcp_server} per-hour limit exceeded: {count}/{limits['per_hour']}")
                return False
        
        return True
    
    def _check_action_limits(self, action: str) -> bool:
        """Check per-action rate limits."""
        if action not in self.per_action_limits:
            return True  # No limits configured
        
        limits = self.per_action_limits[action]
        history = self.action_type_history.get(action, deque())
        now = datetime.now()
        
        # Check per-minute limit
        if 'per_minute' in limits:
            one_minute_ago = now - timedelta(minutes=1)
            count = sum(1 for ts in history if ts > one_minute_ago)
            if count >= limits['per_minute']:
                logger.warning(f"Action {action} per-minute limit exceeded: {count}/{limits['per_minute']}")
                return False
        
        # Check per-hour limit
        if 'per_hour' in limits:
            one_hour_ago = now - timedelta(hours=1)
            count = sum(1 for ts in history if ts > one_hour_ago)
            if count >= limits['per_hour']:
                logger.warning(f"Action {action} per-hour limit exceeded: {count}/{limits['per_hour']}")
                return False
        
        # Check per-day limit
        if 'per_day' in limits:
            one_day_ago = now - timedelta(days=1)
            count = sum(1 for ts in history if ts > one_day_ago)
            if count >= limits['per_day']:
                logger.warning(f"Action {action} per-day limit exceeded: {count}/{limits['per_day']}")
                return False
        
        return True
    
    def _trigger_circuit_breaker(self):
        """Trigger circuit breaker to stop all actions."""
        self.circuit_open = True
        self.circuit_open_until = datetime.now() + timedelta(minutes=self.circuit_breaker_window_minutes)
        logger.critical(f"CIRCUIT BREAKER TRIGGERED - All actions blocked until {self.circuit_open_until}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics.
        
        Returns:
            Statistics dictionary
        """
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        
        return {
            "circuit_breaker_open": self.circuit_open,
            "circuit_breaker_until": str(self.circuit_open_until) if self.circuit_open_until else None,
            "actions_last_minute": sum(1 for ts in self.action_history if ts > one_minute_ago),
            "actions_last_hour": sum(1 for ts in self.action_history if ts > one_hour_ago),
            "actions_last_day": sum(1 for ts in self.action_history if ts > one_day_ago),
            "total_actions_tracked": len(self.action_history),
            "limits": {
                "max_per_minute": self.max_actions_per_minute,
                "max_per_hour": self.max_actions_per_hour,
                "max_per_day": self.max_actions_per_day
            }
        }
