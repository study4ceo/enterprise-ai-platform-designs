"""Device repository for data access operations."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device


class DeviceRepository:
    """Repository for device data operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
    
    async def get_by_mac(self, mac_address: str) -> Optional[Device]:
        """Get device by MAC address."""
        result = await self.session.execute(
            select(Device).where(Device.mac_address == mac_address)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Device]:
        """Get all devices with pagination."""
        result = await self.session.execute(
            select(Device)
            .order_by(Device.last_seen.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    async def search(self, query: str) -> List[Device]:
        """Search devices by MAC, IP, hostname, or friendly name."""
        search_pattern = f"%{query}%"
        result = await self.session.execute(
            select(Device).where(
                or_(
                    Device.mac_address.ilike(search_pattern),
                    Device.ip_address.ilike(search_pattern),
                    Device.hostname.ilike(search_pattern),
                    Device.friendly_name.ilike(search_pattern)
                )
            ).order_by(Device.last_seen.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, device_data: dict) -> Device:
        """Create new device."""
        device = Device(**device_data)
        self.session.add(device)
        await self.session.flush()
        return device
    
    async def update(self, mac_address: str, update_data: dict) -> Optional[Device]:
        """Update device metadata."""
        device = await self.get_by_mac(mac_address)
        if not device:
            return None
        
        for key, value in update_data.items():
            if hasattr(device, key):
                setattr(device, key, value)
        
        device.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return device
    
    async def exists(self, mac_address: str) -> bool:
        """Check if device exists."""
        device = await self.get_by_mac(mac_address)
        return device is not None
