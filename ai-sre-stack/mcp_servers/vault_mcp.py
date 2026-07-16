"""HashiCorp Vault MCP Server implementation."""

from typing import Dict, Any, List
from .base_mcp import BaseMCPServer, MCPCategory, MCPStatus
import hvac
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class VaultMCP(BaseMCPServer):
    """HashiCorp Vault MCP server for secrets management."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Vault MCP server."""
        super().__init__("HashiCorp Vault", MCPCategory.OBSERVABILITY, config)
        self.client = None
        self.vault_url = config.get('url', 'http://localhost:8200')
        self.token = config.get('token')
        self.mount_point = config.get('mount_point', 'secret')
        
    async def _connect(self):
        """Connect to Vault."""
        try:
            self.client = hvac.Client(url=self.vault_url, token=self.token)
            
            # Verify authentication
            if not self.client.is_authenticated():
                raise Exception("Vault authentication failed")
            
            logger.info(f"Connected to Vault: {self.vault_url}")
                
        except Exception as e:
            logger.error(f"Failed to connect to Vault: {e}")
            raise
    
    async def observe(self) -> Dict[str, Any]:
        """Observe Vault status and secrets.
        
        Returns:
            Vault health, expiring secrets, and security status
        """
        try:
            # Get Vault health
            health = self.client.sys.read_health_status()
            
            # List secret engines
            secret_engines = self.client.sys.list_mounted_secrets_engines()
            
            # Get expiring secrets (for dynamic secrets)
            expiring_soon = []
            try:
                # List secrets in default mount
                secrets_list = self.client.secrets.kv.v2.list_secrets(
                    path='',
                    mount_point=self.mount_point
                )
                
                for secret_path in secrets_list.get('data', {}).get('keys', []):
                    try:
                        # Read secret metadata
                        metadata = self.client.secrets.kv.v2.read_secret_metadata(
                            path=secret_path,
                            mount_point=self.mount_point
                        )
                        
                        # Check if secret needs rotation (older than 90 days)
                        created_time = metadata.get('data', {}).get('created_time')
                        if created_time:
                            created = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                            age_days = (datetime.now(created.tzinfo) - created).days
                            
                            if age_days > 90:
                                expiring_soon.append({
                                    "path": secret_path,
                                    "age_days": age_days,
                                    "created": str(created_time)
                                })
                    except Exception:
                        continue  # Skip inaccessible secrets
                        
            except Exception as e:
                logger.warning(f"Could not list secrets: {e}")
            
            # Get seal status
            seal_status = self.client.sys.read_seal_status()
            
            # Get token info
            token_info = {}
            try:
                token_lookup = self.client.auth.token.lookup_self()
                token_info = {
                    "ttl": token_lookup.get('data', {}).get('ttl', 0),
                    "renewable": token_lookup.get('data', {}).get('renewable', False),
                    "policies": token_lookup.get('data', {}).get('policies', [])
                }
            except Exception:
                pass
            
            # Determine overall status
            overall_status = "healthy"
            if seal_status.get('sealed'):
                overall_status = "critical"
            elif len(expiring_soon) > 10:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "sealed": seal_status.get('sealed', True),
                "cluster_name": seal_status.get('cluster_name', 'unknown'),
                "version": seal_status.get('version', 'unknown'),
                "secret_engines": list(secret_engines.get('data', {}).keys()),
                "expiring_secrets": expiring_soon[:20],  # Limit to 20
                "expiring_count": len(expiring_soon),
                "token_info": token_info,
                "health": {
                    "initialized": health.get('initialized', False),
                    "sealed": health.get('sealed', True),
                    "standby": health.get('standby', False)
                }
            }
            
        except Exception as e:
            logger.error(f"Vault observe error: {e}")
            return {"error": str(e), "status": "unhealthy"}
    
    async def act(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Vault action.
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Action result
        """
        try:
            if action == "read_secret":
                return await self._read_secret(params)
            elif action == "write_secret":
                return await self._write_secret(params)
            elif action == "delete_secret":
                return await self._delete_secret(params)
            elif action == "rotate_secret":
                return await self._rotate_secret(params)
            elif action == "renew_token":
                return await self._renew_token(params)
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Action '{action}' failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _read_secret(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a secret from Vault."""
        path = params.get('path')
        mount_point = params.get('mount_point', self.mount_point)
        
        if not path:
            return {"error": "No secret path provided", "success": False}
        
        secret = self.client.secrets.kv.v2.read_secret_version(
            path=path,
            mount_point=mount_point
        )
        
        # Don't return the actual secret value in logs, just metadata
        return {
            "success": True,
            "path": path,
            "version": secret.get('data', {}).get('metadata', {}).get('version'),
            "created_time": secret.get('data', {}).get('metadata', {}).get('created_time'),
            "message": "Secret retrieved successfully (value not logged for security)"
        }
    
    async def _write_secret(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write a secret to Vault."""
        path = params.get('path')
        secret_data = params.get('data', {})
        mount_point = params.get('mount_point', self.mount_point)
        
        if not path or not secret_data:
            return {"error": "Path and data are required", "success": False}
        
        response = self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=secret_data,
            mount_point=mount_point
        )
        
        return {
            "success": True,
            "path": path,
            "version": response.get('data', {}).get('version'),
            "message": "Secret written successfully"
        }
    
    async def _delete_secret(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a secret from Vault."""
        path = params.get('path')
        mount_point = params.get('mount_point', self.mount_point)
        permanent = params.get('permanent', False)
        
        if not path:
            return {"error": "No secret path provided", "success": False}
        
        if permanent:
            # Permanently delete all versions
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=path,
                mount_point=mount_point
            )
            message = "Secret permanently deleted"
        else:
            # Soft delete (can be undeleted)
            self.client.secrets.kv.v2.delete_latest_version_of_secret(
                path=path,
                mount_point=mount_point
            )
            message = "Secret deleted (can be recovered)"
        
        return {
            "success": True,
            "path": path,
            "message": message
        }
    
    async def _rotate_secret(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate a secret (create new version)."""
        path = params.get('path')
        new_value = params.get('new_value')
        mount_point = params.get('mount_point', self.mount_point)
        
        if not path or not new_value:
            return {"error": "Path and new_value are required", "success": False}
        
        # Read current secret to preserve other fields
        try:
            current = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=mount_point
            )
            current_data = current.get('data', {}).get('data', {})
        except Exception:
            current_data = {}
        
        # Update with new value
        current_data.update(new_value)
        current_data['rotated_at'] = datetime.utcnow().isoformat()
        
        response = self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=current_data,
            mount_point=mount_point
        )
        
        return {
            "success": True,
            "path": path,
            "new_version": response.get('data', {}).get('version'),
            "message": "Secret rotated successfully"
        }
    
    async def _renew_token(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Renew the Vault token."""
        increment = params.get('increment', 3600)  # Default 1 hour
        
        response = self.client.auth.token.renew_self(increment=increment)
        
        return {
            "success": True,
            "ttl": response.get('auth', {}).get('lease_duration'),
            "message": f"Token renewed for {increment} seconds"
        }
    
    async def _health_check(self) -> Dict[str, Any]:
        """Perform Vault-specific health check."""
        try:
            health = self.client.sys.read_health_status()
            return {
                "initialized": health.get('initialized', False),
                "sealed": health.get('sealed', True),
                "message": "Vault accessible"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_capabilities(self) -> List[str]:
        """Get available Vault capabilities."""
        return [
            "read_secret",
            "write_secret",
            "delete_secret",
            "rotate_secret",
            "renew_token",
            "list_secrets",
            "monitor_expiring_secrets"
        ]
