"""Unit tests for SSH adapter."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from app.adapters.ssh_adapter import SSHAdapter
from app.adapters.base import DeviceConnection, ConnectionTestResult


@pytest.fixture
def ssh_adapter():
    """Create SSH adapter instance for testing."""
    return SSHAdapter(
        host="192.168.1.1",
        port=22,
        username="admin",
        password="password",
        device_type="cisco_ios"
    )


@pytest.fixture
def cisco_arp_output():
    """Sample Cisco 'show ip arp' output."""
    return """
Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  192.168.1.100    15         aabb.cc00.1122  ARPA   GigabitEthernet0/1
Internet  192.168.1.101    30         1234.5678.9abc  ARPA   GigabitEthernet0/1
Internet  192.168.1.1      -          0011.2233.4455  ARPA   Vlan1
"""


@pytest.fixture
def ubiquiti_arp_output():
    """Sample Ubiquiti 'show arp' output."""
    return """
Address                  HWtype  HWaddress           Flags Mask            Iface
192.168.1.100            ether   aa:bb:cc:dd:ee:ff   C                     eth1
192.168.1.101            ether   11:22:33:44:55:66   C                     eth1
192.168.1.1              ether   00:11:22:33:44:55   C                     br0
"""


@pytest.fixture
def mikrotik_arp_output():
    """Sample MikroTik '/ip arp print' output."""
    return """
Flags: X - disabled, I - invalid, H - DHCP, D - dynamic, P - published, C - complete
# ADDRESS         MAC-ADDRESS       INTERFACE
0 192.168.1.100   AA:BB:CC:DD:EE:FF ether1
1 192.168.1.101   11:22:33:44:55:66 ether1
2 192.168.1.1     00:11:22:33:44:55 bridge1
"""


class TestSSHAdapterInit:
    """Test SSH adapter initialization."""
    
    def test_init_with_defaults(self):
        """Test adapter initialization with default values."""
        adapter = SSHAdapter(
            host="192.168.1.1",
            username="admin",
            password="password"
        )
        
        assert adapter.host == "192.168.1.1"
        assert adapter.port == 22
        assert adapter.username == "admin"
        assert adapter.password == "password"
        assert adapter.device_type == "cisco_ios"
        assert adapter.secret is None
    
    def test_init_with_custom_values(self):
        """Test adapter initialization with custom values."""
        adapter = SSHAdapter(
            host="10.0.0.1",
            port=2222,
            username="netadmin",
            password="secretpass",
            device_type="mikrotik_routeros",
            secret="enablepass"
        )
        
        assert adapter.host == "10.0.0.1"
        assert adapter.port == 2222
        assert adapter.username == "netadmin"
        assert adapter.password == "secretpass"
        assert adapter.device_type == "mikrotik_routeros"
        assert adapter.secret == "enablepass"


class TestSSHAdapterCommands:
    """Test SSH adapter command selection."""
    
    def test_get_command_cisco(self, ssh_adapter):
        """Test command selection for Cisco routers."""
        command = ssh_adapter._get_command_for_router()
        assert command == "show ip arp"
    
    def test_get_command_ubiquiti(self):
        """Test command selection for Ubiquiti routers."""
        adapter = SSHAdapter(
            host="192.168.1.1",
            username="admin",
            password="password",
            device_type="ubiquiti_edge"
        )
        command = adapter._get_command_for_router()
        assert command == "show arp"
    
    def test_get_command_mikrotik(self):
        """Test command selection for MikroTik routers."""
        adapter = SSHAdapter(
            host="192.168.1.1",
            username="admin",
            password="password",
            device_type="mikrotik_routeros"
        )
        command = adapter._get_command_for_router()
        assert command == "/ip arp print"
    
    def test_get_command_unsupported(self):
        """Test command selection for unsupported router type."""
        adapter = SSHAdapter(
            host="192.168.1.1",
            username="admin",
            password="password",
            device_type="unknown_router"
        )
        
        with pytest.raises(ValueError, match="Unsupported router type"):
            adapter._get_command_for_router()


class TestSSHAdapterParsing:
    """Test SSH adapter output parsing."""
    
    def test_parse_cisco_arp(self, ssh_adapter, cisco_arp_output):
        """Test parsing Cisco ARP output."""
        devices = ssh_adapter._parse_cisco_arp(cisco_arp_output)
        
        assert len(devices) == 3
        assert devices[0].mac_address == "AA:BB:CC:00:11:22"
        assert devices[0].ip_address == "192.168.1.100"
        assert devices[0].hostname is None
        
        assert devices[1].mac_address == "12:34:56:78:9A:BC"
        assert devices[1].ip_address == "192.168.1.101"
        
        assert devices[2].mac_address == "00:11:22:33:44:55"
        assert devices[2].ip_address == "192.168.1.1"
    
    def test_parse_cisco_arp_empty(self, ssh_adapter):
        """Test parsing empty Cisco ARP output."""
        devices = ssh_adapter._parse_cisco_arp("")
        assert len(devices) == 0
    
    def test_parse_cisco_arp_invalid(self, ssh_adapter):
        """Test parsing invalid Cisco ARP output."""
        invalid_output = "Some random text without ARP entries"
        devices = ssh_adapter._parse_cisco_arp(invalid_output)
        assert len(devices) == 0
    
    def test_parse_ubiquiti_arp(self, ssh_adapter, ubiquiti_arp_output):
        """Test parsing Ubiquiti ARP output."""
        devices = ssh_adapter._parse_ubiquiti_arp(ubiquiti_arp_output)
        
        assert len(devices) == 3
        assert devices[0].mac_address == "AA:BB:CC:DD:EE:FF"
        assert devices[0].ip_address == "192.168.1.100"
        assert devices[0].hostname is None
        
        assert devices[1].mac_address == "11:22:33:44:55:66"
        assert devices[1].ip_address == "192.168.1.101"
        
        assert devices[2].mac_address == "00:11:22:33:44:55"
        assert devices[2].ip_address == "192.168.1.1"
    
    def test_parse_ubiquiti_arp_empty(self, ssh_adapter):
        """Test parsing empty Ubiquiti ARP output."""
        devices = ssh_adapter._parse_ubiquiti_arp("")
        assert len(devices) == 0
    
    def test_parse_mikrotik_arp(self, ssh_adapter, mikrotik_arp_output):
        """Test parsing MikroTik ARP output."""
        devices = ssh_adapter._parse_mikrotik_arp(mikrotik_arp_output)
        
        assert len(devices) == 3
        assert devices[0].mac_address == "AA:BB:CC:DD:EE:FF"
        assert devices[0].ip_address == "192.168.1.100"
        assert devices[0].hostname is None
        
        assert devices[1].mac_address == "11:22:33:44:55:66"
        assert devices[1].ip_address == "192.168.1.101"
        
        assert devices[2].mac_address == "00:11:22:33:44:55"
        assert devices[2].ip_address == "192.168.1.1"
    
    def test_parse_mikrotik_arp_empty(self, ssh_adapter):
        """Test parsing empty MikroTik ARP output."""
        devices = ssh_adapter._parse_mikrotik_arp("")
        assert len(devices) == 0


class TestSSHAdapterConnection:
    """Test SSH adapter connection functionality."""
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, ssh_adapter):
        """Test successful SSH connection."""
        with patch('app.adapters.ssh_adapter.ConnectHandler') as mock_handler:
            # Mock successful connection
            mock_conn = MagicMock()
            mock_conn.find_prompt.return_value = "Router#"
            mock_conn.is_alive.return_value = True
            mock_handler.return_value = mock_conn
            
            result = await ssh_adapter.test_connection()
            
            assert result.success is True
            assert result.message == "SSH connection successful"
            assert result.details["prompt"] == "Router#"
            assert result.details["device_type"] == "cisco_ios"
            mock_conn.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_connection_auth_failure(self, ssh_adapter):
        """Test SSH connection with authentication failure."""
        from netmiko.exceptions import NetmikoAuthenticationException
        
        with patch('app.adapters.ssh_adapter.ConnectHandler') as mock_handler:
            mock_handler.side_effect = NetmikoAuthenticationException("Auth failed")
            
            result = await ssh_adapter.test_connection()
            
            assert result.success is False
            assert result.message == "SSH authentication failed"
            assert "Auth failed" in result.error
    
    @pytest.mark.asyncio
    async def test_test_connection_timeout(self, ssh_adapter):
        """Test SSH connection with timeout."""
        from netmiko.exceptions import NetmikoTimeoutException
        
        with patch('app.adapters.ssh_adapter.ConnectHandler') as mock_handler:
            mock_handler.side_effect = NetmikoTimeoutException("Connection timeout")
            
            result = await ssh_adapter.test_connection()
            
            assert result.success is False
            assert result.message == "SSH connection timeout"
            assert "Connection timeout" in result.error
    
    @pytest.mark.asyncio
    async def test_test_connection_generic_error(self, ssh_adapter):
        """Test SSH connection with generic error."""
        with patch('app.adapters.ssh_adapter.ConnectHandler') as mock_handler:
            mock_handler.side_effect = Exception("Generic connection error")
            
            result = await ssh_adapter.test_connection()
            
            assert result.success is False
            assert result.message == "SSH connection failed"
            assert "Generic connection error" in result.error


class TestSSHAdapterDeviceDiscovery:
    """Test SSH adapter device discovery."""
    
    @pytest.mark.asyncio
    async def test_get_connected_devices_cisco(self, ssh_adapter, cisco_arp_output):
        """Test device discovery for Cisco router."""
        with patch('app.adapters.ssh_adapter.ConnectHandler') as mock_handler:
            # Mock successful connection and command execution
            mock_conn = MagicMock()
            mock_conn.send_command.return_value = cisco_arp_output
            mock_handler.return_value = mock_conn
            
            devices = await ssh_adapter.get_connected_devices()
            
            assert len(devices) == 3
            assert isinstance(devices[0], DeviceConnection)
            assert devices[0].mac_address == "AA:BB:CC:00:11:22"
            assert devices[0].ip_address == "192.168.1.100"
            
            mock_conn.send_command.assert_called_once_with("show ip arp", read_timeout=30)
            mock_conn.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_connected_devices_ubiquiti(self, ubiquiti_arp_output):
        """Test device discovery for Ubiquiti router."""
        adapter = SSHAdapter(
            host="192.168.1.1",
            username="admin",
            password="password",
            device_type="ubiquiti_edge"
        )
        
        with patch('app.adapters.ssh_adapter.ConnectHandler') as mock_handler:
            mock_conn = MagicMock()
            mock_conn.send_command.return_value = ubiquiti_arp_output
            mock_handler.return_value = mock_conn
            
            devices = await adapter.get_connected_devices()
            
            assert len(devices) == 3
            assert devices[0].mac_address == "AA:BB:CC:DD:EE:FF"
            assert devices[0].ip_address == "192.168.1.100"
            
            mock_conn.send_command.assert_called_once_with("show arp", read_timeout=30)
    
    @pytest.mark.asyncio
    async def test_get_connected_devices_mikrotik(self, mikrotik_arp_output):
        """Test device discovery for MikroTik router."""
        adapter = SSHAdapter(
            host="192.168.1.1",
            username="admin",
            password="password",
            device_type="mikrotik_routeros"
        )
        
        with patch('app.adapters.ssh_adapter.ConnectHandler') as mock_handler:
            mock_conn = MagicMock()
            mock_conn.send_command.return_value = mikrotik_arp_output
            mock_handler.return_value = mock_conn
            
            devices = await adapter.get_connected_devices()
            
            assert len(devices) == 3
            assert devices[0].mac_address == "AA:BB:CC:DD:EE:FF"
            assert devices[0].ip_address == "192.168.1.100"
            
            mock_conn.send_command.assert_called_once_with("/ip arp print", read_timeout=30)
    
    @pytest.mark.asyncio
    async def test_get_connected_devices_with_enable(self):
        """Test device discovery with enable mode for Cisco."""
        adapter = SSHAdapter(
            host="192.168.1.1",
            username="admin",
            password="password",
            device_type="cisco_ios",
            secret="enablepass"
        )
        
        with patch('app.adapters.ssh_adapter.ConnectHandler') as mock_handler:
            mock_conn = MagicMock()
            mock_conn.send_command.return_value = "Internet  192.168.1.100  15  aabb.cc00.1122  ARPA  Vlan1"
            mock_handler.return_value = mock_conn
            
            devices = await adapter.get_connected_devices()
            
            # Verify enable mode was called
            mock_conn.enable.assert_called_once()
            assert len(devices) == 1
    
    @pytest.mark.asyncio
    async def test_get_connected_devices_auth_failure(self, ssh_adapter):
        """Test device discovery with authentication failure."""
        from netmiko.exceptions import NetmikoAuthenticationException
        
        with patch('app.adapters.ssh_adapter.ConnectHandler') as mock_handler:
            mock_handler.side_effect = NetmikoAuthenticationException("Auth failed")
            
            with pytest.raises(Exception, match="SSH authentication failed"):
                await ssh_adapter.get_connected_devices()
    
    @pytest.mark.asyncio
    async def test_get_connected_devices_timeout(self, ssh_adapter):
        """Test device discovery with timeout."""
        from netmiko.exceptions import NetmikoTimeoutException
        
        with patch('app.adapters.ssh_adapter.ConnectHandler') as mock_handler:
            mock_handler.side_effect = NetmikoTimeoutException("Connection timeout")
            
            with pytest.raises(Exception, match="SSH connection timeout"):
                await ssh_adapter.get_connected_devices()
    
    @pytest.mark.asyncio
    async def test_get_connected_devices_command_error(self, ssh_adapter):
        """Test device discovery with command execution error."""
        with patch('app.adapters.ssh_adapter.ConnectHandler') as mock_handler:
            mock_conn = MagicMock()
            mock_conn.send_command.side_effect = Exception("Command failed")
            mock_handler.return_value = mock_conn
            
            with pytest.raises(Exception, match="SSH command execution failed"):
                await ssh_adapter.get_connected_devices()
    
    @pytest.mark.asyncio
    async def test_get_connected_devices_empty_output(self, ssh_adapter):
        """Test device discovery with empty output."""
        with patch('app.adapters.ssh_adapter.ConnectHandler') as mock_handler:
            mock_conn = MagicMock()
            mock_conn.send_command.return_value = ""
            mock_handler.return_value = mock_conn
            
            devices = await ssh_adapter.get_connected_devices()
            
            assert len(devices) == 0
            mock_conn.disconnect.assert_called_once()


class TestSSHAdapterMACNormalization:
    """Test MAC address normalization."""
    
    def test_normalize_cisco_mac_dot_format(self, ssh_adapter):
        """Test normalizing Cisco dot-separated MAC."""
        mac = "aabb.cc00.1122"
        normalized = ssh_adapter._normalize_mac(mac)
        assert normalized == "AA:BB:CC:00:11:22"
    
    def test_normalize_cisco_mac_dash_format(self, ssh_adapter):
        """Test normalizing Cisco dash-separated MAC."""
        mac = "aabb-cc00-1122"
        normalized = ssh_adapter._normalize_mac(mac)
        assert normalized == "AA:BB:CC:00:11:22"
    
    def test_normalize_standard_mac(self, ssh_adapter):
        """Test normalizing standard colon-separated MAC."""
        mac = "aa:bb:cc:dd:ee:ff"
        normalized = ssh_adapter._normalize_mac(mac)
        assert normalized == "AA:BB:CC:DD:EE:FF"
    
    def test_normalize_lowercase_mac(self, ssh_adapter):
        """Test normalizing lowercase MAC."""
        mac = "aabbccddeeff"
        normalized = ssh_adapter._normalize_mac(mac)
        assert normalized == "AA:BB:CC:DD:EE:FF"
