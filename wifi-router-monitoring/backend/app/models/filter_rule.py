"""FilterRule model for allowlist/blocklist management."""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint

from app.database import Base


class RuleType(str, Enum):
    """Filter rule types."""
    ALLOWLIST = "allowlist"
    BLOCKLIST = "blocklist"


class FilterRule(Base):
    """
    FilterRule model for managing device allowlists and blocklists.
    
    Attributes:
        id: Auto-incrementing primary key
        mac_address: Device MAC address
        rule_type: Type of rule (allowlist/blocklist)
        created_at: Rule creation timestamp
    """
    
    __tablename__ = "filter_rules"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Rule data
    mac_address = Column(String(17), nullable=False, index=True)
    rule_type = Column(String(20), nullable=False, index=True)
    
    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("mac_address", "rule_type", name="uq_mac_rule_type"),
    )
    
    def __repr__(self) -> str:
        """String representation of FilterRule."""
        return f"<FilterRule(mac={self.mac_address}, type={self.rule_type})>"
    
    def to_dict(self) -> dict:
        """Convert filter rule to dictionary."""
        return {
            "id": self.id,
            "mac_address": self.mac_address,
            "rule_type": self.rule_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
