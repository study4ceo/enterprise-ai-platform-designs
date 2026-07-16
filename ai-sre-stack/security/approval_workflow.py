"""Approval workflow for high-risk actions."""

from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import logging
import asyncio

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Approval status enum."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    AUTO_APPROVED = "auto_approved"


class ApprovalRequest:
    """Represents an approval request."""
    
    def __init__(
        self,
        request_id: str,
        mcp_server: str,
        action: str,
        params: Dict[str, Any],
        reason: str,
        severity: str,
        cycle_id: str
    ):
        """Initialize approval request."""
        self.request_id = request_id
        self.mcp_server = mcp_server
        self.action = action
        self.params = params
        self.reason = reason
        self.severity = severity
        self.cycle_id = cycle_id
        
        self.status = ApprovalStatus.PENDING
        self.requested_at = datetime.utcnow()
        self.expires_at = self.requested_at + timedelta(minutes=30)  # 30 min timeout
        
        self.approver: Optional[str] = None
        self.approved_at: Optional[datetime] = None
        self.approval_reason: Optional[str] = None


class ApprovalWorkflow:
    """Manages approval workflow for high-risk actions."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize approval workflow.
        
        Args:
            config: Approval workflow configuration
        """
        self.config = config or {}
        
        # Approval requirements
        self.require_approval_for_high_risk = self.config.get('require_approval_for_high_risk', True)
        self.require_approval_for_critical = self.config.get('require_approval_for_critical', True)
        
        # Auto-approval rules
        self.auto_approve_read_only = self.config.get('auto_approve_read_only', True)
        self.auto_approve_low_severity = self.config.get('auto_approve_low_severity', True)
        
        # Approval timeout
        self.approval_timeout_minutes = self.config.get('approval_timeout_minutes', 30)
        
        # Approved approvers list
        self.authorized_approvers = self.config.get('authorized_approvers', ['admin', 'sre-team'])
        
        # Pending approvals
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        
        # Approval history
        self.approval_history: list[ApprovalRequest] = []
        
        # Notification callback
        self.notification_callback: Optional[Callable] = None
        
        logger.info("Approval workflow initialized")
    
    def set_notification_callback(self, callback: Callable):
        """Set callback for approval notifications.
        
        Args:
            callback: Async function to call for notifications
        """
        self.notification_callback = callback
    
    async def request_approval(
        self,
        mcp_server: str,
        action: str,
        params: Dict[str, Any],
        reason: str,
        severity: str,
        cycle_id: str,
        is_high_risk: bool = False
    ) -> ApprovalRequest:
        """Request approval for an action.
        
        Args:
            mcp_server: MCP server name
            action: Action name
            params: Action parameters
            reason: Reason for action
            severity: Severity level
            cycle_id: Cycle identifier
            is_high_risk: Whether action is high-risk
            
        Returns:
            ApprovalRequest object
        """
        # Generate request ID
        request_id = f"{cycle_id}_{mcp_server}_{action}_{datetime.utcnow().timestamp()}"
        
        # Create approval request
        request = ApprovalRequest(
            request_id=request_id,
            mcp_server=mcp_server,
            action=action,
            params=params,
            reason=reason,
            severity=severity,
            cycle_id=cycle_id
        )
        
        # Check if auto-approval applies
        if self._can_auto_approve(action, severity, is_high_risk):
            request.status = ApprovalStatus.AUTO_APPROVED
            request.approver = "system"
            request.approved_at = datetime.utcnow()
            request.approval_reason = "Auto-approved by policy"
            
            logger.info(f"Auto-approved: {action} on {mcp_server}")
            
            # Add to history
            self.approval_history.append(request)
            
            return request
        
        # Requires manual approval
        self.pending_approvals[request_id] = request
        
        logger.warning(f"Approval required: {action} on {mcp_server} (request_id: {request_id})")
        
        # Send notification
        if self.notification_callback:
            await self.notification_callback(request)
        
        return request
    
    def _can_auto_approve(self, action: str, severity: str, is_high_risk: bool) -> bool:
        """Check if action can be auto-approved.
        
        Args:
            action: Action name
            severity: Severity level
            is_high_risk: Whether action is high-risk
            
        Returns:
            True if can be auto-approved
        """
        # Never auto-approve high-risk actions in critical situations
        if is_high_risk and severity == 'critical' and self.require_approval_for_critical:
            return False
        
        # Never auto-approve high-risk actions if policy requires approval
        if is_high_risk and self.require_approval_for_high_risk:
            return False
        
        # Auto-approve low-severity actions if enabled
        if severity in ['low', 'medium'] and self.auto_approve_low_severity:
            return True
        
        # Auto-approve read-only actions if enabled
        read_only_actions = {'observe', 'get', 'list', 'read', 'query', 'health_check'}
        if any(ro in action.lower() for ro in read_only_actions) and self.auto_approve_read_only:
            return True
        
        return False
    
    def approve(self, request_id: str, approver: str, reason: str = "") -> bool:
        """Approve a pending request.
        
        Args:
            request_id: Request identifier
            approver: Who is approving
            reason: Approval reason
            
        Returns:
            True if approved successfully
        """
        if request_id not in self.pending_approvals:
            logger.error(f"Approval request not found: {request_id}")
            return False
        
        request = self.pending_approvals[request_id]
        
        # Check if expired
        if datetime.utcnow() > request.expires_at:
            request.status = ApprovalStatus.EXPIRED
            del self.pending_approvals[request_id]
            self.approval_history.append(request)
            logger.warning(f"Approval request expired: {request_id}")
            return False
        
        # Check if approver is authorized
        if approver not in self.authorized_approvers:
            logger.warning(f"Unauthorized approver: {approver}")
            return False
        
        # Approve
        request.status = ApprovalStatus.APPROVED
        request.approver = approver
        request.approved_at = datetime.utcnow()
        request.approval_reason = reason or "Approved by authorized user"
        
        # Move to history
        del self.pending_approvals[request_id]
        self.approval_history.append(request)
        
        logger.info(f"Approved: {request_id} by {approver}")
        
        return True
    
    def deny(self, request_id: str, approver: str, reason: str) -> bool:
        """Deny a pending request.
        
        Args:
            request_id: Request identifier
            approver: Who is denying
            reason: Denial reason
            
        Returns:
            True if denied successfully
        """
        if request_id not in self.pending_approvals:
            logger.error(f"Approval request not found: {request_id}")
            return False
        
        request = self.pending_approvals[request_id]
        
        # Check if approver is authorized
        if approver not in self.authorized_approvers:
            logger.warning(f"Unauthorized approver: {approver}")
            return False
        
        # Deny
        request.status = ApprovalStatus.DENIED
        request.approver = approver
        request.approved_at = datetime.utcnow()
        request.approval_reason = reason
        
        # Move to history
        del self.pending_approvals[request_id]
        self.approval_history.append(request)
        
        logger.warning(f"Denied: {request_id} by {approver} - Reason: {reason}")
        
        return True
    
    def get_pending_approvals(self) -> list[ApprovalRequest]:
        """Get all pending approval requests.
        
        Returns:
            List of pending requests
        """
        # Clean up expired requests
        self._cleanup_expired()
        
        return list(self.pending_approvals.values())
    
    def _cleanup_expired(self):
        """Clean up expired approval requests."""
        now = datetime.utcnow()
        expired_ids = []
        
        for request_id, request in self.pending_approvals.items():
            if now > request.expires_at:
                request.status = ApprovalStatus.EXPIRED
                self.approval_history.append(request)
                expired_ids.append(request_id)
        
        for request_id in expired_ids:
            del self.pending_approvals[request_id]
            logger.warning(f"Approval request expired and removed: {request_id}")
    
    async def wait_for_approval(
        self,
        request: ApprovalRequest,
        timeout_seconds: Optional[int] = None
    ) -> bool:
        """Wait for approval decision.
        
        Args:
            request: Approval request
            timeout_seconds: Maximum wait time
            
        Returns:
            True if approved, False otherwise
        """
        if request.status == ApprovalStatus.AUTO_APPROVED:
            return True
        
        timeout = timeout_seconds or (self.approval_timeout_minutes * 60)
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            # Check if request still pending
            if request.request_id not in self.pending_approvals:
                # Request was processed
                return request.status == ApprovalStatus.APPROVED
            
            # Check if expired
            if datetime.utcnow() > request.expires_at:
                return False
            
            # Wait a bit before checking again
            await asyncio.sleep(5)
        
        # Timeout reached
        logger.warning(f"Approval wait timeout: {request.request_id}")
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get approval workflow statistics.
        
        Returns:
            Statistics dictionary
        """
        # Clean up expired first
        self._cleanup_expired()
        
        # Count statuses in history
        status_counts = {}
        for request in self.approval_history:
            status = request.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "pending_count": len(self.pending_approvals),
            "history_count": len(self.approval_history),
            "status_breakdown": status_counts,
            "require_approval_for_high_risk": self.require_approval_for_high_risk,
            "require_approval_for_critical": self.require_approval_for_critical,
            "auto_approve_enabled": self.auto_approve_low_severity or self.auto_approve_read_only,
            "authorized_approvers": len(self.authorized_approvers)
        }
