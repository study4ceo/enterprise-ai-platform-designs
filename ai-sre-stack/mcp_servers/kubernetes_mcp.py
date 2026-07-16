"""Kubernetes MCP Server implementation."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
from kubernetes import client, config as k8s_config
from kubernetes.client.rest import ApiException
import logging

logger = logging.getLogger(__name__)


class KubernetesMCP(BaseMCPServer):
    """Kubernetes MCP server for pod, event, and workload management."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Kubernetes MCP server."""
        super().__init__("Kubernetes", MCPCategory.INFRA, config)
        self.core_api = None
        self.apps_api = None
        self.namespace = config.get('namespace', 'default')
        
    async def _connect(self):
        """Connect to Kubernetes cluster."""
        try:
            k8s_config.load_kube_config(config_file=self.config.get('kubeconfig_path'))
            self.core_api = client.CoreV1Api()
            self.apps_api = client.AppsV1Api()
            logger.info("Connected to Kubernetes cluster")
        except Exception as e:
            logger.error(f"Failed to connect to Kubernetes: {e}")
            raise
    
    async def observe(self) -> Dict[str, Any]:
        """Observe current Kubernetes state.
        
        Returns:
            Current state including pods, events, and workloads
        """
        try:
            # Get pods
            pods = self.core_api.list_namespaced_pod(namespace=self.namespace)
            pod_status = []
            for pod in pods.items:
                pod_status.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "restarts": sum([cs.restart_count for cs in pod.status.container_statuses or []]),
                    "ready": all([cs.ready for cs in pod.status.container_statuses or []]) if pod.status.container_statuses else False
                })
            
            # Get deployments
            deployments = self.apps_api.list_namespaced_deployment(namespace=self.namespace)
            deployment_status = []
            for deploy in deployments.items:
                deployment_status.append({
                    "name": deploy.metadata.name,
                    "replicas": deploy.spec.replicas,
                    "available": deploy.status.available_replicas or 0,
                    "ready": deploy.status.ready_replicas or 0,
                    "updated": deploy.status.updated_replicas or 0
                })
            
            # Get recent events
            events = self.core_api.list_namespaced_event(namespace=self.namespace)
            recent_events = []
            for event in sorted(events.items, key=lambda e: e.last_timestamp or e.event_time, reverse=True)[:10]:
                recent_events.append({
                    "type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "object": f"{event.involved_object.kind}/{event.involved_object.name}",
                    "timestamp": str(event.last_timestamp or event.event_time)
                })
            
            return {
                "cluster_status": "healthy" if all(p['ready'] for p in pod_status) else "degraded",
                "pods": pod_status,
                "deployments": deployment_status,
                "recent_events": recent_events,
                "namespace": self.namespace
            }
            
        except ApiException as e:
            logger.error(f"Kubernetes API error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Kubernetes action.
        
        Args:
            action: Action to execute (restart_pod, scale_deployment, etc.)
            params: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action == "restart_pod":
                return await self._restart_pod(params)
            elif action == "scale_deployment":
                return await self._scale_deployment(params)
            elif action == "get_logs":
                return await self._get_pod_logs(params)
            elif action == "delete_pod":
                return await self._delete_pod(params)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _restart_pod(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Restart a pod by deleting it."""
        pod_name = params.get('pod_name')
        namespace = params.get('namespace', self.namespace)
        
        self.core_api.delete_namespaced_pod(name=pod_name, namespace=namespace)
        return {"success": True, "message": f"Pod {pod_name} restarted"}
    
    async def _scale_deployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scale a deployment."""
        deployment_name = params.get('deployment_name')
        replicas = params.get('replicas')
        namespace = params.get('namespace', self.namespace)
        
        deployment = self.apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        deployment.spec.replicas = replicas
        self.apps_api.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=deployment)
        
        return {"success": True, "message": f"Deployment {deployment_name} scaled to {replicas} replicas"}
    
    async def _get_pod_logs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get pod logs."""
        pod_name = params.get('pod_name')
        namespace = params.get('namespace', self.namespace)
        tail_lines = params.get('tail_lines', 100)
        
        logs = self.core_api.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            tail_lines=tail_lines
        )
        
        return {"success": True, "logs": logs}
    
    async def _delete_pod(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a pod."""
        pod_name = params.get('pod_name')
        namespace = params.get('namespace', self.namespace)
        
        self.core_api.delete_namespaced_pod(name=pod_name, namespace=namespace)
        return {"success": True, "message": f"Pod {pod_name} deleted"}
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform Kubernetes-specific health check."""
        try:
            # Try to list nodes as a health check
            nodes = self.core_api.list_node()
            healthy_nodes = sum(1 for node in nodes.items 
                              if any(c.type == "Ready" and c.status == "True" 
                                    for c in node.status.conditions))
            
            return {
                "nodes_total": len(nodes.items),
                "nodes_healthy": healthy_nodes,
                "message": "Kubernetes cluster accessible"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get available Kubernetes capabilities."""
        return [
            "restart_pod",
            "scale_deployment",
            "get_logs",
            "delete_pod",
            "observe_pods",
            "observe_deployments",
            "observe_events"
        ]
