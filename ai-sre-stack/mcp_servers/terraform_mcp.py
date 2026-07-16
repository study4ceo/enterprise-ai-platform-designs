"""Terraform MCP Server implementation."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
from python_terraform import Terraform, IsFlagged
import os
import json
import logging

logger = logging.getLogger(__name__)


class TerraformMCP(BaseMCPServer):
    """Terraform MCP server for infrastructure as code management."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Terraform MCP server."""
        super().__init__("Terraform", MCPCategory.INFRA, config)
        self.tf = None
        self.workspace_path = config.get('workspace_path', './terraform')
        
    async def _connect(self):
        """Initialize Terraform workspace."""
        try:
            if not os.path.exists(self.workspace_path):
                raise FileNotFoundError(f"Terraform workspace not found: {self.workspace_path}")
            
            self.tf = Terraform(working_dir=self.workspace_path)
            logger.info(f"Initialized Terraform workspace: {self.workspace_path}")
        except Exception as e:
            logger.error(f"Failed to initialize Terraform: {e}")
            raise
    
    async def observe(self) -> Dict[str, Any]:
        """Observe current Terraform state.
        
        Returns:
            Current state including plan, drift, and resource status
        """
        try:
            # Get current state
            return_code, stdout, stderr = self.tf.cmd('show', '-json')
            state = json.loads(stdout) if stdout else {}
            
            # Run terraform plan to detect drift
            return_code, stdout, stderr = self.tf.plan(out=IsFlagged, detailed_exitcode=IsFlagged)
            
            drift_status = "no_drift"
            if return_code == 2:
                drift_status = "drift_detected"
            elif return_code != 0:
                drift_status = "error"
            
            # Get resource count
            resources = state.get('values', {}).get('root_module', {}).get('resources', [])
            
            return {
                "status": "healthy" if return_code in [0, 2] else "unhealthy",
                "drift_status": drift_status,
                "resource_count": len(resources),
                "resources": [
                    {
                        "type": r.get('type'),
                        "name": r.get('name'),
                        "address": r.get('address')
                    } for r in resources
                ],
                "workspace": self.workspace_path
            }
            
        except Exception as e:
            logger.error(f"Terraform observe error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Terraform action.
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action == "plan":
                return await self._run_plan(params)
            elif action == "apply":
                return await self._run_apply(params)
            elif action == "destroy":
                return await self._run_destroy(params)
            elif action == "validate":
                return await self._run_validate(params)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _run_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run terraform plan."""
        return_code, stdout, stderr = self.tf.plan(
            detailed_exitcode=IsFlagged,
            out='plan.tfplan'
        )
        
        return {
            "success": return_code in [0, 2],
            "has_changes": return_code == 2,
            "stdout": stdout,
            "stderr": stderr
        }
    
    async def _run_apply(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run terraform apply."""
        auto_approve = params.get('auto_approve', False)
        
        if auto_approve:
            return_code, stdout, stderr = self.tf.apply(skip_plan=True, auto_approve=IsFlagged)
        else:
            return_code, stdout, stderr = self.tf.apply('plan.tfplan')
        
        return {
            "success": return_code == 0,
            "stdout": stdout,
            "stderr": stderr
        }
    
    async def _run_destroy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run terraform destroy."""
        auto_approve = params.get('auto_approve', False)
        
        if not auto_approve:
            return {"error": "Destroy requires auto_approve=true for safety", "success": False}
        
        return_code, stdout, stderr = self.tf.destroy(auto_approve=IsFlagged)
        
        return {
            "success": return_code == 0,
            "stdout": stdout,
            "stderr": stderr
        }
    
    async def _run_validate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run terraform validate."""
        return_code, stdout, stderr = self.tf.validate()
        
        return {
            "success": return_code == 0,
            "stdout": stdout,
            "stderr": stderr
        }
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform Terraform-specific health check."""
        try:
            return_code, stdout, stderr = self.tf.cmd('version')
            return {
                "version": stdout.strip(),
                "message": "Terraform accessible"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get available Terraform capabilities."""
        return [
            "plan",
            "apply",
            "destroy",
            "validate",
            "detect_drift",
            "show_state"
        ]
