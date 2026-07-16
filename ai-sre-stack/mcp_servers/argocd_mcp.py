"""Argo CD MCP Server implementation."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
import requests
import logging

logger = logging.getLogger(__name__)


class ArgoCDMCP(BaseMCPServer):
    """Argo CD MCP server for GitOps deployment and sync monitoring."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Argo CD MCP server."""
        super().__init__("Argo CD", MCPCategory.CICD, config)
        self.server_url = config.get('server')
        self.token = config.get('token')
        self.headers = None
        
    async def _connect(self):
        """Connect to Argo CD API."""
        try:
            self.headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            # Test connection
            response = requests.get(
                f"{self.server_url}/api/v1/applications",
                headers=self.headers,
                verify=False  # In production, use proper SSL verification
            )
            response.raise_for_status()
            logger.info(f"Connected to Argo CD: {self.server_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Argo CD: {e}")
            raise
    
    async def observe(self) -> Dict[str, Any]:
        """Observe current Argo CD application state.
        
        Returns:
            Current sync status, drift, and application health
        """
        try:
            # Get all applications
            response = requests.get(
                f"{self.server_url}/api/v1/applications",
                headers=self.headers,
                verify=False
            )
            response.raise_for_status()
            apps_data = response.json()
            
            applications = []
            out_of_sync = 0
            unhealthy = 0
            
            for app in apps_data.get('items', []):
                status = app.get('status', {})
                sync_status = status.get('sync', {}).get('status', 'Unknown')
                health_status = status.get('health', {}).get('status', 'Unknown')
                
                if sync_status != 'Synced':
                    out_of_sync += 1
                if health_status not in ['Healthy', 'Progressing']:
                    unhealthy += 1
                
                applications.append({
                    "name": app['metadata']['name'],
                    "namespace": app['metadata'].get('namespace', 'default'),
                    "sync_status": sync_status,
                    "health_status": health_status,
                    "revision": status.get('sync', {}).get('revision', '')[:7],
                    "repo": app['spec'].get('source', {}).get('repoURL', '')
                })
            
            overall_status = "healthy"
            if unhealthy > 0:
                overall_status = "unhealthy"
            elif out_of_sync > 0:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "applications": applications,
                "total_apps": len(applications),
                "out_of_sync": out_of_sync,
                "unhealthy": unhealthy
            }
            
        except requests.RequestException as e:
            logger.error(f"Argo CD API error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Argo CD action.
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action == "sync_app":
                return await self._sync_application(params)
            elif action == "rollback_app":
                return await self._rollback_application(params)
            elif action == "refresh_app":
                return await self._refresh_application(params)
            elif action == "get_app_details":
                return await self._get_application_details(params)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _sync_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sync an application."""
        app_name = params.get('app_name')
        prune = params.get('prune', False)
        dry_run = params.get('dry_run', False)
        
        sync_request = {
            "prune": prune,
            "dryRun": dry_run
        }
        
        response = requests.post(
            f"{self.server_url}/api/v1/applications/{app_name}/sync",
            headers=self.headers,
            json=sync_request,
            verify=False
        )
        response.raise_for_status()
        
        return {"success": True, "message": f"Application {app_name} sync initiated"}
    
    async def _rollback_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback an application to a previous revision."""
        app_name = params.get('app_name')
        revision = params.get('revision')
        
        rollback_request = {
            "revision": revision
        }
        
        response = requests.post(
            f"{self.server_url}/api/v1/applications/{app_name}/rollback",
            headers=self.headers,
            json=rollback_request,
            verify=False
        )
        response.raise_for_status()
        
        return {"success": True, "message": f"Application {app_name} rolled back to {revision}"}
    
    async def _refresh_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh an application (re-read from Git)."""
        app_name = params.get('app_name')
        
        response = requests.get(
            f"{self.server_url}/api/v1/applications/{app_name}?refresh=true",
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        
        return {"success": True, "message": f"Application {app_name} refreshed"}
    
    async def _get_application_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about an application."""
        app_name = params.get('app_name')
        
        response = requests.get(
            f"{self.server_url}/api/v1/applications/{app_name}",
            headers=self.headers,
            verify=False
        )
        response.raise_for_status()
        app_data = response.json()
        
        return {"success": True, "application": app_data}
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform Argo CD-specific health check."""
        try:
            response = requests.get(
                f"{self.server_url}/api/version",
                headers=self.headers,
                verify=False
            )
            response.raise_for_status()
            version = response.json()
            return {"version": version.get('Version'), "message": "Argo CD API accessible"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get available Argo CD capabilities."""
        return [
            "sync_app",
            "rollback_app",
            "refresh_app",
            "get_app_details",
            "list_applications",
            "check_sync_status"
        ]
