"""Base adapter class for router protocol adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class DeviceConnection:
    """Represents a device connection discovered by an adapter."""
    
    mac_address: str
    ip_address: str
    hostname: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class ConnectionTestResult:
    """Result of testing a router connection."""
    
    success: bool
    message: str
    error: Optional[str] = None
    details: Optional[dict] = None


class BaseAdapter(ABC):
    """Base class for all router protocol adapters."""
    
    def __init__(self, host: str, port: Optional[int] = None, **credentials):
        """
        Initialize adapter with connection parameters.
        
        Args:
            host: Router hostname or IP address
            port: Router port (protocol-specific default if None)
            **credentials: Protocol-specific credentials
        """
        self.host = host
        self.port = port
        self.credentials = credentials
    
    @abstractmethod
    async def get_connected_devices(self) -> List[DeviceConnection]:
        """
        Query router for connected devices.
        
        Returns:
            List of DeviceConnection objects
        
        Raises:
            Exception: If connection or query fails
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> ConnectionTestResult:
        """
        Test connection to router.
        
        Returns:
            ConnectionTestResult with success status and details
        """
        pass
    
    def _normalize_mac(self, mac: str) -> str:
        """
        Normalize MAC address to standard format (XX:XX:XX:XX:XX:XX).
        
        Args:
            mac: MAC address in various formats
        
        Returns:
            Normalized MAC address
        """
        # Remove common separators
        mac = mac.replace(":", "").replace("-", "").replace(".", "").upper()
        
        # Insert colons every 2 characters
        if len(mac) == 12:
            return ":".join(mac[i:i+2] for i in range(0, 12, 2))
        
        return mac
