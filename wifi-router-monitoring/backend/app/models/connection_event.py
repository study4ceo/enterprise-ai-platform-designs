"""ConnectionEvent model for storing connection history."""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class EventType(str, Enum):
    """Connection event types."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class ConnectionEvent(Base):
    """
    ConnectionEvent model representing a device connection or disconnection event.
    
    Attributes:
        id: Auto-incrementing primary key
        timestamp: Event timestamp
        mac_address: Device MAC address (foreign key to devices)
        ip_address: Device IP at time of event
        hostname: Device hostname at time of event
        router_id: Router identifier (foreign key to routers)
        event_type: Type of event (connected/disconnected)
        connection_duration: Duration in seconds (for disconnection events)
        created_at: Record creation timestamp
    """
    
    __tablename__ = "connection_events"
    
    # Primary key
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # Event data
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        default=lambda: datetime.now(timezone.utc)
    )
    mac_address = Column(
        String(17),
        ForeignKey("devices.mac_address", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    ip_address = Column(String(45), nullable=True)
    hostname = Column(String(255), nullable=True)
    router_id = Column(
        String(50),
        ForeignKey("routers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    event_type = Column(
        String(20),
        nullable=False,
        index=True
    )
    
    # Duration for disconnection events (in seconds)
    connection_duration = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    device = relationship("Device", back_populates="connection_events")
    router = relationship("Router", back_populates="connection_events")
    
    # Composite indexes for common query patterns
    __table_args__ = (
        # Index for time-series queries
        # Index is already created by individual column indexes above
    )
    
    def __repr__(self) -> str:
        """String representation of ConnectionEvent."""
        return (
            f"<ConnectionEvent(id={self.id}, "
            f"mac={self.mac_address}, "
            f"type={self.event_type}, "
            f"time={self.timestamp})>"
        )
    
    def to_dict(self) -> dict:
        """Convert connection event to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "mac_address": self.mac_address,
            "ip_address": self.ip_address,
            "hostname": self.hostname,
            "router_id": self.router_id,
            "event_type": self.event_type,
            "connection_duration": self.connection_duration,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
