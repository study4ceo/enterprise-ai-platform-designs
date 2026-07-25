"""Device manager service for device profile operations."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.repositories.device_repository import DeviceRepository
from app.services.mac_lookup import MACVendorLookup


class DeviceManagerService:
    """
    Service for managing device profiles.
    
    Handles device creation, updates, and metadata management.
    Integrates with MAC vendor lookup for device identification.
    """
    
    def __init__(self, session: AsyncSession, mac_lookup: Optional[MACVendorLookup] = None):
        """
        Initialize device manager service.
        
        Args:
            session: Database session
            mac_lookup: MAC vendor lookup service
        """
        self.repository = DeviceRepository(session)
        self.mac_lookup = mac_lookup or MACVendorLookup()
    
    async def get_or_create_device(
        self,
        mac_address: str,
        ip_address: str,
        hostname: Optional[str] = None
    ) -> Device:
        """
        Get existing device or create new device profile.
        
        Args:
            mac_address: Device MAC address
            ip_address: Device IP address
            hostname: Device hostname
        
        Returns:
            Device object (new or existing)
        """
        # Try to get existing device
        device = await self.repository.get_by_mac(mac_address)
        
        if device:
            # Update last seen and current connection info
            await self.repository.update(mac_address, {
                "ip_address": ip_address,
                "hostname": hostname,
                "last_seen": datetime.now(timezone.utc)
            })
            return device
        
        # Create new device with vendor lookup
        vendor = self.mac_lookup.get_vendor(mac_address)
        
        device_data = {
            "mac_address": mac_address,
            "ip_address": ip_address,
            "hostname": hostname,
            "vendor": vendor,
            "trusted": False,
            "first_seen": datetime.now(timezone.utc),
            "last_seen": datetime.now(timezone.utc)
        }
        
        return await self.repository.create(device_data)
    
    async def update_device_metadata(
        self,
        mac_address: str,
        friendly_name: Optional[str] = None,
        notes: Optional[str] = None,
        trusted: Optional[bool] = None
    ) -> Optional[Device]:
        """
        Update device metadata (user-assigned fields).
        
        Args:
            mac_address: Device MAC address
            friendly_name: User-friendly name
            notes: User notes
            trusted: Trust status
        
        Returns:
            Updated device or None if not found
        """
        update_data = {}
        
        if friendly_name is not None:
            update_data["friendly_name"] = friendly_name
        if notes is not None:
            update_data["notes"] = notes
        if trusted is not None:
            update_data["trusted"] = trusted
        
        if not update_data:
            # No updates specified
            return await self.repository.get_by_mac(mac_address)
        
        return await self.repository.update(mac_address, update_data)
    
    async def search_devices(self, query: str) -> List[Device]:
        """
        Search devices by MAC, IP, hostname, or friendly name.
        
        Args:
            query: Search query string
        
        Returns:
            List of matching devices
        """
        return await self.repository.search(query)
    
    async def get_all_devices(self, limit: int = 100, offset: int = 0) -> List[Device]:
        """
        Get all devices with pagination.
        
        Args:
            limit: Maximum number of devices to return
            offset: Number of devices to skip
        
        Returns:
            List of devices
        """
        return await self.repository.get_all(limit=limit, offset=offset)
    
    async def get_device(self, mac_address: str) -> Optional[Device]:
        """
        Get device by MAC address.
        
        Args:
            mac_address: Device MAC address
        
        Returns:
            Device or None if not found
        """
        return await self.repository.get_by_mac(mac_address)
    
    def is_new_device(self, mac_address: str, existing_device: Optional[Device]) -> bool:
        """
        Check if device is new (first time seeing it).
        
        Args:
            mac_address: Device MAC address
            existing_device: Existing device object or None
        
        Returns:
            True if device is new, False otherwise
        """
        return existing_device is None
    
    async def refresh_vendor_info(self, mac_address: str) -> Optional[Device]:
        """
        Refresh vendor information for a device.
        
        Args:
            mac_address: Device MAC address
        
        Returns:
            Updated device or None if not found
        """
        vendor = self.mac_lookup.get_vendor(mac_address)
        return await self.repository.update(mac_address, {"vendor": vendor})
