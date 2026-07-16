"""PagerDuty MCP Server implementation."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
try:
    from pdpyras import APISession
except ImportError:
    from pagerduty import APISession
import logging

logger = logging.getLogger(__name__)


class PagerDutyMCP(BaseMCPServer):
    """PagerDuty MCP server for incident and on-call management."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize PagerDuty MCP server."""
        super().__init__("PagerDuty", MCPCategory.OBSERVABILITY, config)
        self.session = None
        self.service_id = config.get('service_id')
        
    async def _connect(self):
        """Connect to PagerDuty API."""
        try:
            self.session = APISession(self.config.get('api_key'))
            logger.info("Connected to PagerDuty API")
        except Exception as e:
            logger.error(f"Failed to connect to PagerDuty: {e}")
            raise
    
    async def observe(self) -> Dict[str, Any]:
        """Observe current PagerDuty incidents and on-call status.
        
        Returns:
            Current incidents, on-call schedules, and escalation state
        """
        try:
            # Get active incidents
            incidents = self.session.list_all('incidents', params={
                'statuses[]': ['triggered', 'acknowledged']
            })
            
            incident_list = []
            for incident in incidents:
                incident_list.append({
                    "id": incident['id'],
                    "title": incident['title'],
                    "status": incident['status'],
                    "urgency": incident['urgency'],
                    "created_at": incident['created_at'],
                    "service": incident.get('service', {}).get('summary', 'Unknown')
                })
            
            # Get on-call users
            oncalls = self.session.list_all('oncalls')
            oncall_list = []
            for oncall in oncalls:
                oncall_list.append({
                    "user": oncall['user']['summary'],
                    "escalation_level": oncall['escalation_level'],
                    "schedule": oncall.get('schedule', {}).get('summary', 'Unknown')
                })
            
            # Get service info if service_id provided
            service_info = {}
            if self.service_id:
                service = self.session.rget(f'/services/{self.service_id}')
                service_info = {
                    "name": service.get('name'),
                    "status": service.get('status'),
                    "escalation_policy": service.get('escalation_policy', {}).get('summary')
                }
            
            return {
                "status": "degraded" if len(incident_list) > 0 else "healthy",
                "incidents": incident_list,
                "incident_count": len(incident_list),
                "oncall_users": oncall_list,
                "service": service_info
            }
            
        except Exception as e:
            logger.error(f"PagerDuty observe error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PagerDuty action.
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action == "create_incident":
                return await self._create_incident(params)
            elif action == "acknowledge_incident":
                return await self._acknowledge_incident(params)
            elif action == "resolve_incident":
                return await self._resolve_incident(params)
            elif action == "add_note":
                return await self._add_note(params)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _create_incident(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new incident."""
        title = params.get('title')
        service_id = params.get('service_id', self.service_id)
        urgency = params.get('urgency', 'high')
        body = params.get('body', {})
        
        incident = self.session.rpost('/incidents', json={
            'incident': {
                'type': 'incident',
                'title': title,
                'service': {'id': service_id, 'type': 'service_reference'},
                'urgency': urgency,
                'body': body
            }
        })
        
        return {"success": True, "incident_id": incident['incident']['id'], "message": f"Incident created: {title}"}
    
    async def _acknowledge_incident(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Acknowledge an incident."""
        incident_id = params.get('incident_id')
        
        incident = self.session.rput(f'/incidents/{incident_id}', json={
            'incident': {
                'type': 'incident_reference',
                'status': 'acknowledged'
            }
        })
        
        return {"success": True, "message": f"Incident {incident_id} acknowledged"}
    
    async def _resolve_incident(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve an incident."""
        incident_id = params.get('incident_id')
        
        incident = self.session.rput(f'/incidents/{incident_id}', json={
            'incident': {
                'type': 'incident_reference',
                'status': 'resolved'
            }
        })
        
        return {"success": True, "message": f"Incident {incident_id} resolved"}
    
    async def _add_note(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a note to an incident."""
        incident_id = params.get('incident_id')
        note_content = params.get('content')
        
        note = self.session.rpost(f'/incidents/{incident_id}/notes', json={
            'note': {
                'content': note_content
            }
        })
        
        return {"success": True, "message": "Note added to incident"}
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform PagerDuty-specific health check."""
        try:
            # Get current user as a health check
            user = self.session.rget('/users/me')
            return {"user": user.get('name'), "message": "PagerDuty API accessible"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get available PagerDuty capabilities."""
        return [
            "create_incident",
            "acknowledge_incident",
            "resolve_incident",
            "add_note",
            "list_incidents",
            "get_oncall"
        ]
