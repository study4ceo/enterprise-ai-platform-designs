"""SSH adapter for router device discovery."""

import asyncio
import re
from typing import List, Dict, Callable

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

from app.adapters.base import BaseAdapter, ConnectionTestResult, DeviceConnection


class SSHAdapter(BaseAdapter):
    """
    SSH adapter for discovering connected devices via router CLI.
    
    Supports multiple router types:
    - Cisco IOS/IOS-XE
    - Ubiquiti EdgeRouter/UniFi
    - MikroTik RouterOS
    """
    
    # Router type command mappings
    ROUTER_COMMANDS: Dict[str, str] = {
        "cisco_ios": "show ip arp",
        "cisco_xe": "show ip arp",
        "ubiquiti_edge": "show arp",
        "ubiquiti_edgerouter": "show arp",
        "mikrotik_routeros": "/ip arp print",
        "mikrotik": "/ip arp print",
    }
    
    def __init__(
        self,
        host: str,
        port: int = 22,
        username: str = "",
        password: str = "",
        device_type: str = "cisco_ios",
        **credentials
    ):
        """
        Initialize SSH adapter.
        
        Args:
            host: Router hostname or IP
            port: SSH port (default 22)
            username: SSH username
            password: SSH password
            device_type: Netmiko device type (cisco_ios, ubiquiti_edge, mikrotik, etc.)
            **credentials: Additional credentials (secret, enable password, etc.)
        """
        super().__init__(host, port, username=username, password=password, device_type=device_type, **credentials)
        self.username = username
        self.password = password
        self.device_type = device_type
        self.secret = credentials.get("secret")  # Enable password for Cisco
    
    async def get_connected_devices(self) -> List[DeviceConnection]:
        """
        Query router via SSH for connected devices.
        
        Returns:
            List of discovered devices
        
        Raises:
            Exception: If SSH connection or command execution fails
        """
        # Run SSH commands in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_devices_sync)
    
    def _get_devices_sync(self) -> List[DeviceConnection]:
        """Synchronous device discovery via SSH."""
        connection = None
        try:
            # Connect to router
            device_params = {
                "device_type": self.device_type,
                "host": self.host,
                "port": self.port,
                "username": self.username,
                "password": self.password,
            }
            
            if self.secret:
                device_params["secret"] = self.secret
            
            connection = ConnectHandler(**device_params)
            
            # Enter enable mode for Cisco devices if secret provided
            if self.secret and "cisco" in self.device_type.lower():
                connection.enable()
            
            # Get command for router type
            command = self._get_command_for_router()
            
            # Execute command
            output = connection.send_command(command, read_timeout=30)
            
            # Parse output based on router type
            devices = self._parse_output(output)
            
            return devices
        
        except NetmikoAuthenticationException as e:
            raise Exception(f"SSH authentication failed: {str(e)}")
        except NetmikoTimeoutException as e:
            raise Exception(f"SSH connection timeout: {str(e)}")
        except Exception as e:
            raise Exception(f"SSH command execution failed: {str(e)}")
        finally:
            if connection:
                connection.disconnect()
    
    async def test_connection(self) -> ConnectionTestResult:
        """
        Test SSH connection to router.
        
        Returns:
            ConnectionTestResult with status
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._test_connection_sync)
    
    def _test_connection_sync(self) -> ConnectionTestResult:
        """Synchronous connection test."""
        connection = None
        try:
            device_params = {
                "device_type": self.device_type,
                "host": self.host,
                "port": self.port,
                "username": self.username,
                "password": self.password,
            }
            
            if self.secret:
                device_params["secret"] = self.secret
            
            connection = ConnectHandler(**device_params)
            
            # Get router prompt/hostname
            prompt = connection.find_prompt()
            
            connection.disconnect()
            
            return ConnectionTestResult(
                success=True,
                message="SSH connection successful",
                details={"prompt": prompt, "device_type": self.device_type}
            )
        
        except NetmikoAuthenticationException as e:
            return ConnectionTestResult(
                success=False,
                message="SSH authentication failed",
                error=str(e)
            )
        except NetmikoTimeoutException as e:
            return ConnectionTestResult(
                success=False,
                message="SSH connection timeout",
                error=str(e)
            )
        except Exception as e:
            return ConnectionTestResult(
                success=False,
                message="SSH connection failed",
                error=str(e)
            )
        finally:
            if connection and connection.is_alive():
                connection.disconnect()
    
    def _get_command_for_router(self) -> str:
        """
        Get appropriate command for router type.
        
        Returns:
            Command string to execute
        
        Raises:
            ValueError: If router type is not supported
        """
        command = self.ROUTER_COMMANDS.get(self.device_type)
        
        if not command:
            # Try to match partial device type
            for device_key, cmd in self.ROUTER_COMMANDS.items():
                if device_key in self.device_type:
                    return cmd
            
            raise ValueError(f"Unsupported router type: {self.device_type}")
        
        return command
    
    def _parse_output(self, output: str) -> List[DeviceConnection]:
        """
        Parse command output based on router type.
        
        Args:
            output: Command output from router
        
        Returns:
            List of DeviceConnection objects
        """
        if "cisco" in self.device_type.lower():
            return self._parse_cisco_arp(output)
        elif "ubiquiti" in self.device_type.lower() or "edge" in self.device_type.lower():
            return self._parse_ubiquiti_arp(output)
        elif "mikrotik" in self.device_type.lower():
            return self._parse_mikrotik_arp(output)
        else:
            # Default to Cisco-style parsing
            return self._parse_cisco_arp(output)
    
    def _parse_cisco_arp(self, output: str) -> List[DeviceConnection]:
        """
        Parse Cisco 'show ip arp' output.
        
        Example format:
        Protocol  Address          Age (min)  Hardware Addr   Type   Interface
        Internet  192.168.1.100    5          aabb.cc00.1122  ARPA   Vlan1
        """
        devices = []
        
        # Match lines with IP, MAC, and optionally hostname
        # Cisco MAC format: aabb.cc00.1122 or aabb-cc00-1122
        pattern = r"Internet\s+(\d+\.\d+\.\d+\.\d+)\s+\S+\s+([\da-fA-F]{4}[.-][\da-fA-F]{4}[.-][\da-fA-F]{4})"
        
        for line in output.split("\n"):
            match = re.search(pattern, line)
            if match:
                ip = match.group(1)
                mac = match.group(2)
                
                # Normalize MAC address
                mac_normalized = self._normalize_mac(mac)
                
                # Skip incomplete entries
                if mac_normalized and ip:
                    devices.append(DeviceConnection(
                        mac_address=mac_normalized,
                        ip_address=ip,
                        hostname=None
                    ))
        
        return devices
    
    def _parse_ubiquiti_arp(self, output: str) -> List[DeviceConnection]:
        """
        Parse Ubiquiti 'show arp' output.
        
        Example format:
        Address                  HWtype  HWaddress           Flags Mask            Iface
        192.168.1.100            ether   aa:bb:cc:dd:ee:ff   C                     eth1
        """
        devices = []
        
        # Match lines with IP and MAC
        # Ubiquiti MAC format: aa:bb:cc:dd:ee:ff
        pattern = r"(\d+\.\d+\.\d+\.\d+)\s+\S+\s+([\da-fA-F:]{17})"
        
        for line in output.split("\n"):
            match = re.search(pattern, line)
            if match:
                ip = match.group(1)
                mac = match.group(2)
                
                # Normalize MAC address
                mac_normalized = self._normalize_mac(mac)
                
                if mac_normalized and ip:
                    devices.append(DeviceConnection(
                        mac_address=mac_normalized,
                        ip_address=ip,
                        hostname=None
                    ))
        
        return devices
    
    def _parse_mikrotik_arp(self, output: str) -> List[DeviceConnection]:
        """
        Parse MikroTik '/ip arp print' output.
        
        Example format:
        # ADDRESS         MAC-ADDRESS       INTERFACE
        0 192.168.1.100   AA:BB:CC:DD:EE:FF ether1
        """
        devices = []
        
        # Match lines with IP and MAC
        # MikroTik MAC format: AA:BB:CC:DD:EE:FF
        pattern = r"\d+\s+(\d+\.\d+\.\d+\.\d+)\s+([\da-fA-F:]{17})"
        
        for line in output.split("\n"):
            match = re.search(pattern, line)
            if match:
                ip = match.group(1)
                mac = match.group(2)
                
                # Normalize MAC address
                mac_normalized = self._normalize_mac(mac)
                
                if mac_normalized and ip:
                    devices.append(DeviceConnection(
                        mac_address=mac_normalized,
                        ip_address=ip,
                        hostname=None
                    ))
        
        return devices
