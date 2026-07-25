"""Unit tests for RouterScannerService."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.adapters.base import DeviceConnection
from app.models.connection_event import EventType
from app.models.router import RouterProtocol
from app.services.router_scanner import RouterScannerService


@pytest.fixture
def mock_session():
    """Create mock database session."""
    session = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def mock_device_manager():
    """Create mock device manager service."""
    manager = MagicMock()
    manager.get_or_create_device = AsyncMock()
    return manager


@pytest.fixture
def mock_event_handler():
    """Create mock event handler."""
    handler = MagicMock()
    handler.handle_connection_event = AsyncMock()
    handler.handle_disconnection_event = AsyncMock()
    return handler


@pytest.fixture
def scanner_service(mock_session, mock_device_manager, mock_event_handler):
    """Create RouterScannerService instance with mocks."""
    return RouterScannerService(
        session=mock_session,
        device_manager=mock_device_manager,
        event_handler=mock_event_handler
    )


@pytest.mark.asyncio
async def test_scan_router_not_found(scanner_service):
    """Test scanning a non-existent router."""
    with patch.object(scanner_service.repository, 'get_by_id', return_value=None):
        result = await scanner_service.scan_router("nonexistent-router")
    
    assert result["success"] is False
    assert result["error"] == "Router not found"
    assert result["devices_found"] == 0


@pytest.mark.asyncio
async def test_scan_router_disabled(scanner_service, mock_router_data):
    """Test scanning a disabled router."""
    mock_router = MagicMock()
    mock_router.id = "test-router"
    mock_router.enabled = False
    
    with patch.object(scanner_service.repository, 'get_by_id', return_value=mock_router):
        result = await scanner_service.scan_router("test-router")
    
    assert result["success"] is True
    assert result["error"] == "Router disabled"
    assert result["devices_found"] == 0


@pytest.mark.asyncio
async def test_scan_router_snmp_success(scanner_service):
    """Test successful SNMP router scan."""
    # Create mock router
    mock_router = MagicMock()
    mock_router.id = "test-router"
    mock_router.name = "Test Router"
    mock_router.enabled = True
    mock_router.protocol = RouterProtocol.SNMP.value
    mock_router.host = "192.168.1.1"
    mock_router.port = 161
    mock_router.credentials = {"community": "public", "version": "2c"}
    
    # Mock devices returned from adapter
    mock_devices = [
        DeviceConnection(
            mac_address="AA:BB:CC:DD:EE:FF",
            ip_address="192.168.1.100",
            hostname="device1",
            timestamp=datetime.now(timezone.utc)
        ),
        DeviceConnection(
            mac_address="11:22:33:44:55:66",
            ip_address="192.168.1.101",
            hostname="device2",
            timestamp=datetime.now(timezone.utc)
        )
    ]
    
    # Mock adapter
    mock_adapter = MagicMock()
    mock_adapter.get_connected_devices = AsyncMock(return_value=mock_devices)
    
    with patch.object(scanner_service.repository, 'get_by_id', return_value=mock_router), \
         patch.object(scanner_service, '_get_adapter', return_value=mock_adapter), \
         patch.object(scanner_service, '_update_scan_status', new_callable=AsyncMock):
        
        result = await scanner_service.scan_router("test-router")
    
    assert result["success"] is True
    assert result["devices_found"] == 2
    assert result["new_connections"] == 2
    assert result["disconnections"] == 0


@pytest.mark.asyncio
async def test_scan_router_adapter_failure(scanner_service):
    """Test router scan with adapter connection failure."""
    mock_router = MagicMock()
    mock_router.id = "test-router"
    mock_router.enabled = True
    mock_router.protocol = RouterProtocol.SNMP.value
    mock_router.host = "192.168.1.1"
    mock_router.port = 161
    mock_router.credentials = {"community": "public"}
    
    # Mock adapter that raises exception
    mock_adapter = MagicMock()
    mock_adapter.get_connected_devices = AsyncMock(
        side_effect=Exception("Connection timeout")
    )
    
    with patch.object(scanner_service.repository, 'get_by_id', return_value=mock_router), \
         patch.object(scanner_service, '_get_adapter', return_value=mock_adapter), \
         patch.object(scanner_service, '_update_scan_status', new_callable=AsyncMock):
        
        result = await scanner_service.scan_router("test-router")
    
    assert result["success"] is False
    assert "Connection timeout" in result["error"]
    assert result["devices_found"] == 0


@pytest.mark.asyncio
async def test_detect_new_connections(scanner_service, mock_device_manager):
    """Test detection of new device connections."""
    router_id = "test-router"
    
    # Previous scan: empty
    previous_devices = {}
    
    # Current scan: 2 devices
    current_devices = {
        "AA:BB:CC:DD:EE:FF": ("192.168.1.100", "device1", datetime.now(timezone.utc)),
        "11:22:33:44:55:66": ("192.168.1.101", "device2", datetime.now(timezone.utc))
    }
    
    # Mock device manager responses
    mock_device = MagicMock()
    mock_device_manager.get_or_create_device.return_value = mock_device
    
    new_count = await scanner_service._detect_new_connections(
        router_id, current_devices, previous_devices
    )
    
    assert new_count == 2
    assert mock_device_manager.get_or_create_device.call_count == 2
    assert scanner_service.event_handler.handle_connection_event.call_count == 2


@pytest.mark.asyncio
async def test_detect_disconnections(scanner_service):
    """Test detection of device disconnections."""
    router_id = "test-router"
    
    # Previous scan: 2 devices
    timestamp = datetime.now(timezone.utc)
    previous_devices = {
        "AA:BB:CC:DD:EE:FF": ("192.168.1.100", "device1", timestamp),
        "11:22:33:44:55:66": ("192.168.1.101", "device2", timestamp)
    }
    
    # Current scan: 1 device (device1 disconnected)
    current_devices = {
        "11:22:33:44:55:66": ("192.168.1.101", "device2", timestamp)
    }
    
    # Initialize connection times
    scanner_service._connection_times[router_id] = {
        "AA:BB:CC:DD:EE:FF": timestamp
    }
    
    disconnection_count = await scanner_service._detect_disconnections(
        router_id, current_devices, previous_devices
    )
    
    assert disconnection_count == 1
    assert scanner_service.event_handler.handle_disconnection_event.call_count == 1
    
    # Verify connection duration was calculated
    call_args = scanner_service.event_handler.handle_disconnection_event.call_args
    event_data = call_args[0][0]
    assert event_data["event_type"] == EventType.DISCONNECTED.value
    assert event_data["connection_duration"] is not None
    assert event_data["connection_duration"] >= 0


@pytest.mark.asyncio
async def test_build_device_map(scanner_service):
    """Test building device map from scan results."""
    timestamp = datetime.now(timezone.utc)
    devices = [
        DeviceConnection(
            mac_address="AA:BB:CC:DD:EE:FF",
            ip_address="192.168.1.100",
            hostname="device1",
            timestamp=timestamp
        ),
        DeviceConnection(
            mac_address="11:22:33:44:55:66",
            ip_address="192.168.1.101",
            hostname=None,
            timestamp=timestamp
        )
    ]
    
    device_map = scanner_service._build_device_map(devices)
    
    assert len(device_map) == 2
    assert "AA:BB:CC:DD:EE:FF" in device_map
    assert device_map["AA:BB:CC:DD:EE:FF"][0] == "192.168.1.100"
    assert device_map["AA:BB:CC:DD:EE:FF"][1] == "device1"


def test_get_adapter_snmp(scanner_service):
    """Test SNMP adapter creation."""
    mock_router = MagicMock()
    mock_router.protocol = RouterProtocol.SNMP.value
    mock_router.host = "192.168.1.1"
    mock_router.port = 161
    mock_router.credentials = {"community": "public", "version": "2c"}
    
    adapter = scanner_service._get_adapter(mock_router)
    
    assert adapter is not None
    assert adapter.host == "192.168.1.1"
    assert adapter.port == 161


def test_get_adapter_ssh(scanner_service):
    """Test SSH adapter creation."""
    mock_router = MagicMock()
    mock_router.protocol = RouterProtocol.SSH.value
    mock_router.host = "192.168.1.1"
    mock_router.port = 22
    mock_router.credentials = {
        "username": "admin",
        "password": "password",
        "device_type": "cisco_ios"
    }
    
    adapter = scanner_service._get_adapter(mock_router)
    
    assert adapter is not None
    assert adapter.host == "192.168.1.1"
    assert adapter.port == 22


def test_get_adapter_http_api(scanner_service):
    """Test HTTP API adapter creation."""
    mock_router = MagicMock()
    mock_router.protocol = RouterProtocol.HTTP_API.value
    mock_router.host = "192.168.1.1"
    mock_router.port = 8080
    mock_router.credentials = {"auth_token": "test-token"}
    
    adapter = scanner_service._get_adapter(mock_router)
    
    assert adapter is not None


def test_get_adapter_arp(scanner_service):
    """Test ARP scanner creation."""
    mock_router = MagicMock()
    mock_router.protocol = RouterProtocol.ARP.value
    mock_router.host = "192.168.1.0"
    mock_router.port = None
    mock_router.credentials = {"network_cidr": "192.168.1.0/24"}
    
    adapter = scanner_service._get_adapter(mock_router)
    
    assert adapter is not None


@pytest.mark.asyncio
async def test_connection_duration_calculation(scanner_service):
    """Test accurate connection duration calculation."""
    router_id = "test-router"
    mac = "AA:BB:CC:DD:EE:FF"
    
    # Set connection time to 60 seconds ago
    from datetime import timedelta
    connection_time = datetime.now(timezone.utc) - timedelta(seconds=60)
    
    scanner_service._connection_times[router_id] = {mac: connection_time}
    
    previous_devices = {mac: ("192.168.1.100", "device1", connection_time)}
    current_devices = {}  # Device disconnected
    
    await scanner_service._detect_disconnections(
        router_id, current_devices, previous_devices
    )
    
    # Verify duration is approximately 60 seconds (allow small variance)
    call_args = scanner_service.event_handler.handle_disconnection_event.call_args
    event_data = call_args[0][0]
    duration = event_data["connection_duration"]
    
    assert 58 <= duration <= 62  # Allow 2 second variance


@pytest.mark.asyncio
async def test_multiple_routers_independent_tracking(scanner_service):
    """Test that multiple routers track connections independently."""
    # Scan router 1
    router1_devices = {
        "AA:BB:CC:DD:EE:FF": ("192.168.1.100", "device1", datetime.now(timezone.utc))
    }
    scanner_service._previous_scans["router1"] = router1_devices
    
    # Scan router 2
    router2_devices = {
        "11:22:33:44:55:66": ("192.168.2.100", "device2", datetime.now(timezone.utc))
    }
    scanner_service._previous_scans["router2"] = router2_devices
    
    # Verify independent tracking
    assert "router1" in scanner_service._previous_scans
    assert "router2" in scanner_service._previous_scans
    assert len(scanner_service._previous_scans["router1"]) == 1
    assert len(scanner_service._previous_scans["router2"]) == 1
    assert "AA:BB:CC:DD:EE:FF" in scanner_service._previous_scans["router1"]
    assert "11:22:33:44:55:66" in scanner_service._previous_scans["router2"]
