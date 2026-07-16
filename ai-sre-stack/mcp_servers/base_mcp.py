"""Base MCP Server class."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class MCPCategory(Enum):
    """MCP Server categories."""
    INFRA = "Infrastructure"
    OBSERVABILITY = "Observability"
    CICD = "CI/CD"
    COMMS = "Communications & Response"


class MCPStatus(Enum):
    """MCP Server status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class BaseMCPServer(ABC):
    """Base class for all MCP servers."""
    
    def __init__(self, name: str, category: MCPCategory, config: Dict[str, Any]):
        """Initialize MCP server.
        
        Args:
            name: Server name
            category: Server category
            config: Configuration dict
        """
        self.name = name
        self.category = category
        self.config = config
        self.status = MCPStatus.UNKNOWN
        self._initialized = False
        
    async def initialize(self) -> bool:
        """Initialize the MCP server.
        
        Returns:
            True if initialization successful
        """
        try:
            logger.info(f"Initializing {self.name} MCP server...")
            await self._connect()
            self._initialized = True
            self.status = MCPStatus.HEALTHY
            logger.info(f"{self.name} MCP server initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize {self.name}: {e}")
            self.status = MCPStatus.UNHEALTHY
            return False
    
    @abstractmethod
    async def _connect(self):
        """Establish connection to the service. Implemented by subclasses."""
        pass
    
    @abstractmethod
    async def observe(self) -> Dict[str, Any]:
        """Observe current state and metrics.
        
        Returns:
            Dictionary containing current state information
        """
        pass
    
    @abstractmethod
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action.
        
        Args:
            action: Action name
            params: Action parameters
            
        Returns:
            Dictionary containing action result
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of the MCP server.
        
        Returns:
            Health check result
        """
        try:
            if not self._initialized:
                return {
                    "status": MCPStatus.UNHEALTHY.value,
                    "message": "Not initialized"
                }
            
            # Perform basic health check
            result = await self._health_check()
            
            return {
                "server": self.name,
                "category": self.category.value,
                "status": self.status.value,
                **result
            }
        except Exception as e:
            logger.error(f"Health check failed for {self.name}: {e}")
            self.status = MCPStatus.UNHEALTHY
            return {
                "server": self.name,
                "status": MCPStatus.UNHEALTHY.value,
                "error": str(e)
            }
    
    @abstractmethod
    async def _health_check(self) -> Dict[str, Any]:
        """Perform server-specific health check. Implemented by subclasses."""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Get list of available capabilities/actions.
        
        Returns:
            List of capability names
        """
        return []
    
    async def shutdown(self):
        """Shutdown the MCP server gracefully."""
        logger.info(f"Shutting down {self.name} MCP server...")
        self._initialized = False
        self.status = MCPStatus.UNKNOWN
