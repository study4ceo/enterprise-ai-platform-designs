"""Device model for storing device profiles."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Device(Base):
    """
    Device model representing a network device that has connected to a router.
    
    Attributes:
        mac_address: Unique MAC address (primary key)
        ip_address: Last known IP address
        hostname: Device hostname
        vendor: Device manufacturer (from MAC OUI lookup)
        friendly_name: User-assigned friendly name
        notes: User notes about the device
        trusted: Whether device is trusted (no alerts)
        first_seen: Timestamp of first detection
        last_seen: Timestamp of last detection
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """
    
    __tablename__ = "devices"
    
    # Primary key
    mac_address = Column(String(17), primary_key=True, index=True)
    
    # Device information
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    hostname = Column(String(255), nullable=True)
    vendor = Column(String(255), nullable=True, index=True)
    
    # User-defined metadata
    friendly_name = Column(String(255), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    trusted = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    first_seen = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    last_seen = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        index=True
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    connection_events = relationship(
        "ConnectionEvent",
        back_populates="device",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation of Device."""
        name = self.friendly_name or self.hostname or self.mac_address
        return f"<Device(mac={self.mac_address}, name={name})>"
    
    def to_dict(self) -> dict:
        """Convert device to dictionary."""
        return {
            "mac_address": self.mac_address,
            "ip_address": self.ip_address,
            "hostname": self.hostname,
            "vendor": self.vendor,
            "friendly_name": self.friendly_name,
            "notes": self.notes,
            "trusted": self.trusted,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
