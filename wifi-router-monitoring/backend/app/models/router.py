"""Router model for storing router configurations."""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.database import Base


class RouterProtocol(str, Enum):
    """Supported router communication protocols."""
    SNMP = "snmp"
    SSH = "ssh"
    HTTP_API = "http_api"
    ARP = "arp"


class RouterStatus(str, Enum):
    """Router connection status."""
    SUCCESS = "success"
    FAILED = "failed"
    NEVER_SCANNED = "never_scanned"


class Router(Base):
    """
    Router model representing a configured router to monitor.
    
    Attributes:
        id: Unique router identifier
        name: User-friendly router name
        protocol: Communication protocol (snmp/ssh/http_api/arp)
        host: Router hostname or IP address
        port: Router port number
        credentials: Encrypted credentials (JSON)
        model: Router model/manufacturer
        firmware_version: Router firmware version
        last_scan_timestamp: Timestamp of last successful scan
        last_scan_status: Status of last scan attempt
        scan_interval: Scan interval in seconds
        enabled: Whether router scanning is enabled
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """
    
    __tablename__ = "routers"
    
    # Primary key
    id = Column(String(50), primary_key=True, index=True)
    
    # Router information
    name = Column(String(255), nullable=False)
    protocol = Column(String(20), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=True)
    
    # Credentials stored as encrypted JSON
    # Structure varies by protocol:
    # SNMP: {community, version}
    # SSH: {username, password, device_type}
    # HTTP API: {api_token, username, password}
    # ARP: {network_cidr}
    credentials = Column(JSON, nullable=False)
    
    # Router details
    model = Column(String(255), nullable=True)
    firmware_version = Column(String(100), nullable=True)
    
    # Scan status
    last_scan_timestamp = Column(DateTime(timezone=True), nullable=True, index=True)
    last_scan_status = Column(
        String(20),
        nullable=True,
        default=RouterStatus.NEVER_SCANNED.value
    )
    
    # Configuration
    scan_interval = Column(Integer, nullable=False, default=30)
    enabled = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
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
        back_populates="router",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation of Router."""
        return f"<Router(id={self.id}, name={self.name}, protocol={self.protocol})>"
    
    def to_dict(self, include_credentials: bool = False) -> dict:
        """
        Convert router to dictionary.
        
        Args:
            include_credentials: Whether to include credentials in output
        
        Returns:
            Dictionary representation of router
        """
        data = {
            "id": self.id,
            "name": self.name,
            "protocol": self.protocol,
            "host": self.host,
            "port": self.port,
            "model": self.model,
            "firmware_version": self.firmware_version,
            "last_scan_timestamp": (
                self.last_scan_timestamp.isoformat()
                if self.last_scan_timestamp
                else None
            ),
            "last_scan_status": self.last_scan_status,
            "scan_interval": self.scan_interval,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_credentials:
            data["credentials"] = self.credentials
        
        return data
