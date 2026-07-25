"""SNMP adapter for router device discovery."""

import asyncio
from typing import List, Optional

from pysnmp.hlapi.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    bulkCmd,
    getCmd,
)

from app.adapters.base import BaseAdapter, ConnectionTestResult, DeviceConnection


class SNMPAdapter(BaseAdapter):
    """
    SNMP adapter for discovering connected devices.
    
    Supports SNMP v1, v2c, and v3.
    """
    
    # SNMP OIDs for device discovery
    IP_NET_TO_MEDIA_PHYS_ADDRESS = "1.3.6.1.2.1.4.22.1.2"  # MAC address
    IP_NET_TO_MEDIA_NET_ADDRESS = "1.3.6.1.2.1.4.22.1.3"   # IP address
    
    def __init__(
        self,
        host: str,
        port: int = 161,
        community: str = "public",
        version: str = "2c",
        **credentials
    ):
        """
        Initialize SNMP adapter.
        
        Args:
            host: Router hostname or IP
            port: SNMP port (default 161)
            community: SNMP community string
            version: SNMP version (1, 2c, or 3)
            **credentials: Additional SNMP v3 credentials
        """
        super().__init__(host, port, community=community, version=version, **credentials)
        self.community = community
        self.version = version
        self.engine = SnmpEngine()
    
    async def get_connected_devices(self) -> List[DeviceConnection]:
        """
        Query router via SNMP for connected devices.
        
        Returns:
            List of discovered devices
        
        Raises:
            Exception: If SNMP query fails
        """
        devices = []
        
        try:
            # Query MAC addresses
            mac_addresses = await self._snmp_bulk_walk(self.IP_NET_TO_MEDIA_PHYS_ADDRESS)
            
            # Query IP addresses
            ip_addresses = await self._snmp_bulk_walk(self.IP_NET_TO_MEDIA_NET_ADDRESS)
            
            # Combine MAC and IP mappings
            for idx, mac_hex in mac_addresses.items():
                if idx in ip_addresses:
                    mac = self._hex_to_mac(mac_hex)
                    ip = ip_addresses[idx]
                    
                    if mac and ip:
                        devices.append(DeviceConnection(
                            mac_address=self._normalize_mac(mac),
                            ip_address=ip,
                            hostname=None  # SNMP doesn't provide hostname
                        ))
        
        except Exception as e:
            raise Exception(f"SNMP query failed: {str(e)}")
        
        return devices
    
    async def test_connection(self) -> ConnectionTestResult:
        """
        Test SNMP connection to router.
        
        Returns:
            ConnectionTestResult with status
        """
        try:
            # Try to get system description OID
            system_desc_oid = "1.3.6.1.2.1.1.1.0"
            
            iterator = await getCmd(
                self.engine,
                CommunityData(self.community, mpModel=self._get_snmp_version()),
                await UdpTransportTarget.create((self.host, self.port)),
                ContextData(),
                ObjectType(ObjectIdentity(system_desc_oid))
            )
            
            error_indication, error_status, error_index, var_binds = iterator
            
            if error_indication:
                return ConnectionTestResult(
                    success=False,
                    message="SNMP connection failed",
                    error=str(error_indication)
                )
            
            if error_status:
                return ConnectionTestResult(
                    success=False,
                    message="SNMP error",
                    error=f"{error_status.prettyPrint()} at {error_index}"
                )
            
            # Extract system description
            sys_desc = str(var_binds[0][1]) if var_binds else "Unknown"
            
            return ConnectionTestResult(
                success=True,
                message="SNMP connection successful",
                details={"system_description": sys_desc}
            )
        
        except Exception as e:
            return ConnectionTestResult(
                success=False,
                message="SNMP connection test failed",
                error=str(e)
            )
    
    async def _snmp_bulk_walk(self, oid: str) -> dict:
        """
        Perform SNMP bulk walk on OID.
        
        Args:
            oid: SNMP OID to walk
        
        Returns:
            Dictionary mapping OID indices to values
        """
        results = {}
        
        iterator = await bulkCmd(
            self.engine,
            CommunityData(self.community, mpModel=self._get_snmp_version()),
            await UdpTransportTarget.create((self.host, self.port)),
            ContextData(),
            0, 25,  # Non-repeaters, max-repetitions
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode=False
        )
        
        for error_indication, error_status, error_index, var_binds in iterator:
            if error_indication:
                break
            if error_status:
                break
            
            for var_bind in var_binds:
                oid_str = str(var_bind[0])
                value = str(var_bind[1])
                
                # Extract index from OID
                if oid in oid_str:
                    index = oid_str.replace(oid + ".", "")
                    results[index] = value
        
        return results
    
    def _get_snmp_version(self) -> int:
        """Get SNMP version number."""
        version_map = {
            "1": 0,
            "2c": 1,
            "3": 3
        }
        return version_map.get(self.version, 1)
    
    def _hex_to_mac(self, hex_string: str) -> Optional[str]:
        """
        Convert hex string to MAC address.
        
        Args:
            hex_string: Hex representation of MAC (e.g., '0x112233445566')
        
        Returns:
            MAC address string or None
        """
        try:
            # Remove '0x' prefix if present
            hex_string = hex_string.replace("0x", "").replace(" ", "")
            
            # Convert to MAC format
            if len(hex_string) == 12:
                return ":".join(hex_string[i:i+2] for i in range(0, 12, 2)).upper()
            
            return None
        except Exception:
            return None
