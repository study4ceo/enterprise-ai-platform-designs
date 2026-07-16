"""Prometheus MCP Server implementation - EXAMPLE."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
import requests
import logging

logger = logging.getLogger(__name__)


class PrometheusMCP(BaseMCPServer):
    """Prometheus MCP server for metrics and alerting."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Prometheus MCP server."""
        super().__init__("Prometheus", MCPCategory.OBSERVABILITY, config)
        self.prometheus_url = config.get('url', 'http://localhost:9090')
        
    async def _connect(self):
        """Connect to Prometheus API."""
        try:
            # Test connection
            response = requests.get(f"{self.prometheus_url}/api/v1/status/config")
            response.raise_for_status()
            logger.info(f"Connected to Prometheus: {self.prometheus_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Prometheus: {e}")
            raise
    
    async def observe(self) -> Dict[str, Any]:
        """Observe current Prometheus metrics and alerts.
        
        Returns:
            Current alerts, target health, and key metrics
        """
        try:
            # Get active alerts
            alerts_response = requests.get(f"{self.prometheus_url}/api/v1/alerts")
            alerts_data = alerts_response.json()
            
            active_alerts = []
            for alert in alerts_data.get('data', {}).get('alerts', []):
                if alert['state'] == 'firing':
                    active_alerts.append({
                        "name": alert['labels'].get('alertname'),
                        "severity": alert['labels'].get('severity', 'unknown'),
                        "summary": alert['annotations'].get('summary', ''),
                        "value": alert['value']
                    })
            
            # Get target health
            targets_response = requests.get(f"{self.prometheus_url}/api/v1/targets")
            targets_data = targets_response.json()
            
            unhealthy_targets = []
            for target in targets_data.get('data', {}).get('activeTargets', []):
                if target['health'] != 'up':
                    unhealthy_targets.append({
                        "job": target['labels'].get('job'),
                        "instance": target['labels'].get('instance'),
                        "health": target['health'],
                        "error": target.get('lastError', '')
                    })
            
            # Query key metrics (example: CPU usage)
            query = 'avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100'
            metrics_response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={'query': query}
            )
            metrics_data = metrics_response.json()
            
            avg_cpu_idle = None
            if metrics_data.get('data', {}).get('result'):
                avg_cpu_idle = float(metrics_data['data']['result'][0]['value'][1])
            
            overall_status = "healthy"
            if len(active_alerts) > 0 or len(unhealthy_targets) > 0:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "active_alerts": active_alerts,
                "alert_count": len(active_alerts),
                "unhealthy_targets": unhealthy_targets,
                "unhealthy_target_count": len(unhealthy_targets),
                "avg_cpu_idle_percent": avg_cpu_idle
            }
            
        except Exception as e:
            logger.error(f"Prometheus observe error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Prometheus action.
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action == "query_metric":
                return await self._query_metric(params)
            elif action == "query_range":
                return await self._query_range(params)
            elif action == "silence_alert":
                return await self._silence_alert(params)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _query_metric(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query a Prometheus metric."""
        query = params.get('query')
        
        response = requests.get(
            f"{self.prometheus_url}/api/v1/query",
            params={'query': query}
        )
        data = response.json()
        
        return {"success": True, "data": data.get('data', {})}
    
    async def _query_range(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query a Prometheus metric over a time range."""
        query = params.get('query')
        start = params.get('start')
        end = params.get('end')
        step = params.get('step', '15s')
        
        response = requests.get(
            f"{self.prometheus_url}/api/v1/query_range",
            params={
                'query': query,
                'start': start,
                'end': end,
                'step': step
            }
        )
        data = response.json()
        
        return {"success": True, "data": data.get('data', {})}
    
    async def _silence_alert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an alert silence in Alertmanager."""
        # Note: This requires Alertmanager API, not Prometheus
        alertname = params.get('alertname')
        duration = params.get('duration', '1h')
        comment = params.get('comment', 'Silenced by AI SRE')
        
        # This is a placeholder - actual implementation would use Alertmanager API
        return {
            "success": True,
            "message": f"Alert {alertname} silenced for {duration}",
            "note": "Requires Alertmanager integration"
        }
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform Prometheus-specific health check."""
        try:
            response = requests.get(f"{self.prometheus_url}/-/healthy")
            return {"message": "Prometheus accessible", "healthy": response.status_code == 200}
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get available Prometheus capabilities."""
        return [
            "query_metric",
            "query_range",
            "silence_alert",
            "list_alerts",
            "check_targets"
        ]
