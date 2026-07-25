"""Router scanner service for periodic device scanning."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.arp_scanner import ARPScanner
from app.adapters.base import BaseAdapter, DeviceConnection
from app.adapters.http_adapter import HTTPAPIAdapter
from app.adapters.snmp_adapter import SNMPAdapter
from app.adapters.ssh_adapter import SSHAdapter
from app.models.connection_event import EventType
from app.models.router import Router, RouterProtocol
from app.repositories.router_repository import RouterRepository

# Set up structured logging
logger = logging.getLogger(__name__)


class RouterScannerService:
    """
    Service for scanning routers and detecting device connections/disconnections.
    
    Handles:
    - Periodic scanning of configured routers
    - Protocol adapter selection based on router configuration
    - Connection/disconnection detection by comparing scans
    - Connection duration calculation
    - Error handling with structured logging
    """
    
    def __init__(
        self,
        session: AsyncSession,
        device_manager=None,
        event_handler=None
    ):
        """
        Initialize router scanner service.
        
        Args:
            session: Database session
            device_manager: Device manager service (optional, for dependency injection)
            event_handler: Connection event handler (optional, for dependency injection)
        """
        self.session = session
        self.repository = RouterRepository(session)
        self.device_manager = device_manager
        self.event_handler = event_handler
        
        # Track previous scan results for each router
        # Format: {router_id: {mac_address: (ip, hostname, timestamp)}}
        self._previous_scans: Dict[str, Dict[str, tuple]] = {}
        
        # Track connection start times for duration calculation
        # Format: {router_id: {mac_address: connection_timestamp}}
        self._connection_times: Dict[str, Dict[str, datetime]] = {}
    
    async def scan_router(self, router_id: str) -> Dict[str, any]:
        """
        Perform single scan of specified router.
        
        Compares current scan with previous scan to detect:
        - New connections (devices present now but not before)
        - Disconnections (devices present before but not now)
        
        Args:
            router_id: Router identifier
        
        Returns:
            ScanResult dictionary with:
                - success: bool
                - router_id: str
                - devices_found: int
                - new_connections: int
                - disconnections: int
                - error: Optional[str]
        """
        logger.info(f"Starting scan for router {router_id}")
        
        try:
            # Get router configuration
            router = await self.repository.get_by_id(router_id)
            if not router:
                logger.error(f"Router {router_id} not found")
                return {
                    "success": False,
                    "router_id": router_id,
                    "devices_found": 0,
                    "new_connections": 0,
                    "disconnections": 0,
                    "error": "Router not found"
                }
            
            if not router.enabled:
                logger.debug(f"Router {router_id} is disabled, skipping scan")
                return {
                    "success": True,
                    "router_id": router_id,
                    "devices_found": 0,
                    "new_connections": 0,
                    "disconnections": 0,
                    "error": "Router disabled"
                }
            
            # Select and initialize appropriate protocol adapter
            adapter = self._get_adapter(router)
            if not adapter:
                logger.error(f"Failed to create adapter for router {router_id} with protocol {router.protocol}")
                await self._update_scan_status(router_id, "failed")
                return {
                    "success": False,
                    "router_id": router_id,
                    "devices_found": 0,
                    "new_connections": 0,
                    "disconnections": 0,
                    "error": f"Unsupported protocol: {router.protocol}"
                }
            
            # Query router for connected devices
            try:
                devices = await adapter.get_connected_devices()
                logger.debug(f"Router {router_id} scan found {len(devices)} devices")
            except Exception as e:
                logger.error(f"Router {router_id} scan failed: {str(e)}", exc_info=True)
                await self._update_scan_status(router_id, "failed")
                return {
                    "success": False,
                    "router_id": router_id,
                    "devices_found": 0,
                    "new_connections": 0,
                    "disconnections": 0,
                    "error": str(e)
                }
            
            # Compare with previous scan to detect changes
            current_devices = self._build_device_map(devices)
            previous_devices = self._previous_scans.get(router_id, {})
            
            new_connections = await self._detect_new_connections(
                router_id, current_devices, previous_devices
            )
            
            disconnections = await self._detect_disconnections(
                router_id, current_devices, previous_devices
            )
            
            # Update scan status and timestamp
            await self._update_scan_status(router_id, "success")
            
            # Store current scan for next comparison
            self._previous_scans[router_id] = current_devices
            
            logger.info(
                f"Router {router_id} scan complete: "
                f"{len(devices)} devices, "
                f"{new_connections} new, "
                f"{disconnections} disconnected"
            )
            
            return {
                "success": True,
                "router_id": router_id,
                "devices_found": len(devices),
                "new_connections": new_connections,
                "disconnections": disconnections,
                "error": None
            }
        
        except Exception as e:
            logger.error(f"Unexpected error scanning router {router_id}: {str(e)}", exc_info=True)
            await self._update_scan_status(router_id, "failed")
            return {
                "success": False,
                "router_id": router_id,
                "devices_found": 0,
                "new_connections": 0,
                "disconnections": 0,
                "error": str(e)
            }
    
    def _get_adapter(self, router: Router) -> Optional[BaseAdapter]:
        """
        Select appropriate protocol adapter based on router configuration.
        
        Args:
            router: Router model instance
        
        Returns:
            Initialized adapter or None if protocol unsupported
        """
        protocol = RouterProtocol(router.protocol)
        credentials = router.credentials or {}
        
        try:
            if protocol == RouterProtocol.SNMP:
                return SNMPAdapter(
                    host=router.host,
                    port=router.port or 161,
                    community=credentials.get("community", "public"),
                    version=credentials.get("version", "2c")
                )
            
            elif protocol == RouterProtocol.SSH:
                return SSHAdapter(
                    host=router.host,
                    port=router.port or 22,
                    username=credentials.get("username", ""),
                    password=credentials.get("password", ""),
                    device_type=credentials.get("device_type", "generic")
                )
            
            elif protocol == RouterProtocol.HTTP_API:
                base_url = f"http://{router.host}"
                if router.port:
                    base_url = f"{base_url}:{router.port}"
                
                return HTTPAPIAdapter(
                    base_url=base_url,
                    auth_token=credentials.get("auth_token"),
                    username=credentials.get("username"),
                    password=credentials.get("password")
                )
            
            elif protocol == RouterProtocol.ARP:
                return ARPScanner(
                    network_cidr=credentials.get("network_cidr", "192.168.1.0/24")
                )
            
            else:
                logger.error(f"Unsupported protocol: {protocol}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to create adapter for protocol {protocol}: {str(e)}", exc_info=True)
            return None
    
    def _build_device_map(self, devices: List[DeviceConnection]) -> Dict[str, tuple]:
        """
        Build device map from scan results.
        
        Args:
            devices: List of DeviceConnection objects
        
        Returns:
            Dictionary mapping MAC address to (ip, hostname, timestamp)
        """
        return {
            device.mac_address: (
                device.ip_address,
                device.hostname,
                device.timestamp
            )
            for device in devices
        }
    
    async def _detect_new_connections(
        self,
        router_id: str,
        current_devices: Dict[str, tuple],
        previous_devices: Dict[str, tuple]
    ) -> int:
        """
        Detect new device connections by comparing current and previous scans.
        
        Args:
            router_id: Router identifier
            current_devices: Current scan device map
            previous_devices: Previous scan device map
        
        Returns:
            Number of new connections detected
        """
        current_macs = set(current_devices.keys())
        previous_macs = set(previous_devices.keys())
        new_macs = current_macs - previous_macs
        
        if not new_macs:
            return 0
        
        logger.debug(f"Router {router_id}: Detected {len(new_macs)} new connections")
        
        # Initialize connection times tracking for this router if needed
        if router_id not in self._connection_times:
            self._connection_times[router_id] = {}
        
        # Process new connections
        new_connection_count = 0
        for mac in new_macs:
            ip, hostname, timestamp = current_devices[mac]
            
            # Record connection start time
            self._connection_times[router_id][mac] = timestamp
            
            # Create connection event via device manager and event handler
            if self.device_manager and self.event_handler:
                try:
                    # Get or create device profile
                    device = await self.device_manager.get_or_create_device(
                        mac_address=mac,
                        ip_address=ip,
                        hostname=hostname
                    )
                    
                    # Create connection event
                    event_data = {
                        "timestamp": timestamp,
                        "mac_address": mac,
                        "ip_address": ip,
                        "hostname": hostname,
                        "router_id": router_id,
                        "event_type": EventType.CONNECTED.value,
                        "connection_duration": None
                    }
                    
                    await self.event_handler.handle_connection_event(event_data)
                    new_connection_count += 1
                    
                    logger.info(
                        f"New device connected to router {router_id}: "
                        f"MAC={mac}, IP={ip}, Hostname={hostname}"
                    )
                
                except Exception as e:
                    logger.error(
                        f"Failed to process new connection for {mac}: {str(e)}",
                        exc_info=True
                    )
            else:
                logger.warning("Device manager or event handler not configured")
        
        return new_connection_count
    
    async def _detect_disconnections(
        self,
        router_id: str,
        current_devices: Dict[str, tuple],
        previous_devices: Dict[str, tuple]
    ) -> int:
        """
        Detect device disconnections by comparing current and previous scans.
        
        Args:
            router_id: Router identifier
            current_devices: Current scan device map
            previous_devices: Previous scan device map
        
        Returns:
            Number of disconnections detected
        """
        current_macs = set(current_devices.keys())
        previous_macs = set(previous_devices.keys())
        disconnected_macs = previous_macs - current_macs
        
        if not disconnected_macs:
            return 0
        
        logger.debug(f"Router {router_id}: Detected {len(disconnected_macs)} disconnections")
        
        # Process disconnections
        disconnection_count = 0
        for mac in disconnected_macs:
            ip, hostname, _ = previous_devices[mac]
            
            # Calculate connection duration
            connection_duration = None
            if router_id in self._connection_times and mac in self._connection_times[router_id]:
                start_time = self._connection_times[router_id][mac]
                end_time = datetime.now(timezone.utc)
                connection_duration = int((end_time - start_time).total_seconds())
                
                # Clean up connection time tracking
                del self._connection_times[router_id][mac]
            
            # Create disconnection event
            if self.event_handler:
                try:
                    event_data = {
                        "timestamp": datetime.now(timezone.utc),
                        "mac_address": mac,
                        "ip_address": ip,
                        "hostname": hostname,
                        "router_id": router_id,
                        "event_type": EventType.DISCONNECTED.value,
                        "connection_duration": connection_duration
                    }
                    
                    await self.event_handler.handle_disconnection_event(event_data)
                    disconnection_count += 1
                    
                    duration_str = f"{connection_duration}s" if connection_duration else "unknown"
                    logger.info(
                        f"Device disconnected from router {router_id}: "
                        f"MAC={mac}, Duration={duration_str}"
                    )
                
                except Exception as e:
                    logger.error(
                        f"Failed to process disconnection for {mac}: {str(e)}",
                        exc_info=True
                    )
            else:
                logger.warning("Event handler not configured")
        
        return disconnection_count
    
    async def _update_scan_status(self, router_id: str, status: str) -> None:
        """
        Update router scan status and timestamp.
        
        Args:
            router_id: Router identifier
            status: Scan status ("success" or "failed")
        """
        try:
            await self.repository.update(router_id, {
                "last_scan_timestamp": datetime.now(timezone.utc),
                "last_scan_status": status
            })
            await self.session.commit()
        except Exception as e:
            logger.error(f"Failed to update scan status for router {router_id}: {str(e)}")
            await self.session.rollback()
