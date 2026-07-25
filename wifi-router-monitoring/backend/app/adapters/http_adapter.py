"""HTTP API adapter for router device discovery."""

from typing import List

import httpx

from app.adapters.base import BaseAdapter, ConnectionTestResult, DeviceConnection


class HTTPAPIAdapter(BaseAdapter):
    """HTTP API adapter for discovering devices via router REST APIs."""
    
    def __init__(
        self,
        host: str,
        port: int = 443,
        api_token: str = "",
        username: str = "",
        password: str = "",
        **credentials
    ):
        """Initialize HTTP API adapter."""
        super().__init__(host, port, api_token=api_token, username=username, password=password, **credentials)
        self.api_token = api_token
        self.username = username
        self.password = password
    
    async def get_connected_devices(self) -> List[DeviceConnection]:
        """Query router via HTTP API for connected devices."""
        # TODO: Implement HTTP API device discovery
        # Support for UniFi, TP-Link Omada, etc.
        raise NotImplementedError("HTTP API adapter not yet implemented")
    
    async def test_connection(self) -> ConnectionTestResult:
        """Test HTTP API connection to router."""
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f"{self.host}/api/health",
                    headers={"Authorization": f"Bearer {self.api_token}"}
                )
                response.raise_for_status()
            
            return ConnectionTestResult(
                success=True,
                message="HTTP API connection successful"
            )
        except Exception as e:
            return ConnectionTestResult(
                success=False,
                message="HTTP API connection failed",
                error=str(e)
            )
