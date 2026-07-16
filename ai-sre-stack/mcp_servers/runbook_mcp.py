"""Incident Runbook MCP Server implementation."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
import os
import yaml
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RunbookMCP(BaseMCPServer):
    """Incident Runbook MCP server for SOP and remediation procedures."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Runbook MCP server."""
        super().__init__("Incident Runbook", MCPCategory.COMMS, config)
        self.runbook_path = config.get('runbook_path', './runbooks')
        self.runbooks = {}
        
    async def _connect(self):
        """Load runbooks from the filesystem."""
        try:
            if not os.path.exists(self.runbook_path):
                os.makedirs(self.runbook_path)
                logger.info(f"Created runbook directory: {self.runbook_path}")
            
            self._load_runbooks()
            logger.info(f"Loaded {len(self.runbooks)} runbooks from {self.runbook_path}")
        except Exception as e:
            logger.error(f"Failed to initialize Runbook MCP: {e}")
            raise
    
    def _load_runbooks(self):
        """Load all runbooks from the runbook directory."""
        runbook_files = Path(self.runbook_path).glob('**/*.{yaml,yml,json,md}')
        
        for file_path in runbook_files:
            try:
                runbook_id = file_path.stem
                
                if file_path.suffix in ['.yaml', '.yml']:
                    with open(file_path, 'r') as f:
                        runbook_data = yaml.safe_load(f)
                elif file_path.suffix == '.json':
                    with open(file_path, 'r') as f:
                        runbook_data = json.load(f)
                elif file_path.suffix == '.md':
                    with open(file_path, 'r') as f:
                        runbook_data = {
                            'id': runbook_id,
                            'title': runbook_id.replace('_', ' ').title(),
                            'content': f.read(),
                            'type': 'markdown'
                        }
                else:
                    continue
                
                self.runbooks[runbook_id] = runbook_data
                logger.debug(f"Loaded runbook: {runbook_id}")
                
            except Exception as e:
                logger.error(f"Failed to load runbook {file_path}: {e}")
    
    async def observe(self) -> Dict[str, Any]:
        """Observe current runbook state.
        
        Returns:
            Available runbooks and their metadata
        """
        try:
            runbook_list = []
            
            for runbook_id, runbook in self.runbooks.items():
                runbook_list.append({
                    "id": runbook_id,
                    "title": runbook.get('title', runbook_id),
                    "category": runbook.get('category', 'general'),
                    "severity": runbook.get('severity', 'medium'),
                    "tags": runbook.get('tags', []),
                    "steps_count": len(runbook.get('steps', []))
                })
            
            return {
                "status": "healthy",
                "runbooks": runbook_list,
                "total_runbooks": len(runbook_list),
                "runbook_path": self.runbook_path
            }
            
        except Exception as e:
            logger.error(f"Runbook observe error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Runbook action.
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action == "get_runbook":
                return await self._get_runbook(params)
            elif action == "search_runbooks":
                return await self._search_runbooks(params)
            elif action == "execute_step":
                return await self._execute_step(params)
            elif action == "create_runbook":
                return await self._create_runbook(params)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_runbook(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific runbook by ID."""
        runbook_id = params.get('runbook_id')
        
        if runbook_id not in self.runbooks:
            return {"error": f"Runbook '{runbook_id}' not found", "success": False}
        
        return {"success": True, "runbook": self.runbooks[runbook_id]}
    
    async def _search_runbooks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search runbooks by keywords, tags, or category."""
        query = params.get('query', '').lower()
        category = params.get('category')
        tags = params.get('tags', [])
        
        results = []
        
        for runbook_id, runbook in self.runbooks.items():
            match = False
            
            # Search in title and content
            if query:
                title = runbook.get('title', '').lower()
                content = str(runbook.get('content', '')).lower()
                if query in title or query in content:
                    match = True
            
            # Filter by category
            if category and runbook.get('category') == category:
                match = True
            
            # Filter by tags
            if tags:
                runbook_tags = runbook.get('tags', [])
                if any(tag in runbook_tags for tag in tags):
                    match = True
            
            if match or (not query and not category and not tags):
                results.append({
                    "id": runbook_id,
                    "title": runbook.get('title', runbook_id),
                    "category": runbook.get('category', 'general'),
                    "tags": runbook.get('tags', []),
                    "severity": runbook.get('severity', 'medium')
                })
        
        return {"success": True, "results": results, "count": len(results)}
    
    async def _execute_step(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific step from a runbook."""
        runbook_id = params.get('runbook_id')
        step_index = params.get('step_index', 0)
        
        if runbook_id not in self.runbooks:
            return {"error": f"Runbook '{runbook_id}' not found", "success": False}
        
        runbook = self.runbooks[runbook_id]
        steps = runbook.get('steps', [])
        
        if step_index >= len(steps):
            return {"error": f"Step {step_index} not found", "success": False}
        
        step = steps[step_index]
        
        return {
            "success": True,
            "step": step,
            "step_index": step_index,
            "total_steps": len(steps),
            "message": f"Executing step {step_index + 1} of {len(steps)}"
        }
    
    async def _create_runbook(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new runbook."""
        runbook_id = params.get('runbook_id')
        runbook_data = params.get('data')
        file_format = params.get('format', 'yaml')
        
        file_path = Path(self.runbook_path) / f"{runbook_id}.{file_format}"
        
        try:
            if file_format in ['yaml', 'yml']:
                with open(file_path, 'w') as f:
                    yaml.dump(runbook_data, f, default_flow_style=False)
            elif file_format == 'json':
                with open(file_path, 'w') as f:
                    json.dump(runbook_data, f, indent=2)
            
            self.runbooks[runbook_id] = runbook_data
            
            return {"success": True, "message": f"Runbook '{runbook_id}' created", "path": str(file_path)}
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform Runbook-specific health check."""
        try:
            path_exists = os.path.exists(self.runbook_path)
            return {
                "runbook_count": len(self.runbooks),
                "path_exists": path_exists,
                "message": "Runbook system accessible"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get available Runbook capabilities."""
        return [
            "get_runbook",
            "search_runbooks",
            "execute_step",
            "create_runbook",
            "list_runbooks"
        ]
