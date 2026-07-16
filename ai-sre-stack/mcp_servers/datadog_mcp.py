"""Datadog MCP Server implementation."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.dashboards_api import DashboardsApi
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v2.api.metrics_api import MetricsApi
import logging

logger = logging.getLogger(__name__)


class DatadogMCP(BaseMCPServer):
    """Datadog MCP server for metrics, traces, and alert monitoring."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Datadog MCP server."""
        super().__init__("Datadog", MCPCategory.OBSERVABILITY, config)
        self.api_client = None
        self.dashboards_api = None
        self.monitors_api = None
        self.metrics_api = None
        
    async def _connect(self):
        """Connect to Datadog API."""
        try:
            configuration = Configuration()
            configuration.api_key['apiKeyAuth'] = self.config.get('api_key')
            configuration.api_key['appKeyAuth'] = self.config.get('app_key')
            configuration.server_variables['site'] = self.config.get('site', 'datadoghq.com')
            
            self.api_client = ApiClient(configuration)
            self.dashboards_api = DashboardsApi(self.api_client)
            self.monitors_api = MonitorsApi(self.api_client)
            self.metrics_api = MetricsApi(self.api_client)
            
            logger.info("Connected to Datadog API")
        except Exception as e:
            logger.error(f"Failed to connect to Datadog: {e}")
            raise
    
    async def observe(self) -> Dict[str, Any]:
        """Observe current Datadog metrics and alerts.
        
        Returns:
            Current metrics, active alerts, and dashboard status
        """
        try:
            # Get active monitors (alerts)
            monitors = self.monitors_api.list_monitors()
            active_alerts = []
            for monitor in monitors:
                if monitor.overall_state in ['Alert', 'Warn', 'No Data']:
                    active_alerts.append({
                        "id": monitor.id,
                        "name": monitor.name,
                        "status": monitor.overall_state,
                        "type": monitor.type,
                        "message": monitor.message
                    })
            
            # Get dashboards
            dashboards = self.dashboards_api.list_dashboards()
            dashboard_list = []
            for dashboard in dashboards.get('dashboards', []):
                dashboard_list.append({
                    "id": dashboard.get('id'),
                    "title": dashboard.get('title'),
                    "is_read_only": dashboard.get('is_read_only', False)
                })
            
            return {
                "status": "healthy" if len(active_alerts) == 0 else "degraded",
                "active_alerts": active_alerts,
                "alert_count": len(active_alerts),
                "dashboards": dashboard_list[:10],  # Limit to 10
                "total_monitors": len(monitors)
            }
            
        except Exception as e:
            logger.error(f"Datadog observe error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Datadog action.
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action == "mute_monitor":
                return await self._mute_monitor(params)
            elif action == "unmute_monitor":
                return await self._unmute_monitor(params)
            elif action == "query_metrics":
                return await self._query_metrics(params)
            elif action == "get_dashboard":
                return await self._get_dashboard(params)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _mute_monitor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mute a monitor."""
        monitor_id = params.get('monitor_id')
        
        self.monitors_api.mute_monitor(monitor_id)
        return {"success": True, "message": f"Monitor {monitor_id} muted"}
    
    async def _unmute_monitor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Unmute a monitor."""
        monitor_id = params.get('monitor_id')
        
        self.monitors_api.unmute_monitor(monitor_id)
        return {"success": True, "message": f"Monitor {monitor_id} unmuted"}
    
    async def _query_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query metrics from Datadog."""
        query = params.get('query')
        from_time = params.get('from', int((datetime.now() - timedelta(hours=1)).timestamp()))
        to_time = params.get('to', int(datetime.now().timestamp()))
        
        from datetime import datetime, timedelta
        
        response = self.metrics_api.query_metrics(
            _from=from_time,
            to=to_time,
            query=query
        )
        
        return {"success": True, "data": response}
    
    async def _get_dashboard(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get dashboard details."""
        dashboard_id = params.get('dashboard_id')
        
        dashboard = self.dashboards_api.get_dashboard(dashboard_id)
        return {"success": True, "dashboard": dashboard}
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform Datadog-specific health check."""
        try:
            # Try to list monitors as a health check
            monitors = self.monitors_api.list_monitors(page_size=1)
            return {"message": "Datadog API accessible"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get available Datadog capabilities."""
        return [
            "mute_monitor",
            "unmute_monitor",
            "query_metrics",
            "get_dashboard",
            "list_monitors",
            "observe_alerts"
        ]
