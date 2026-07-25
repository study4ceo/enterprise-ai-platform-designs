"""Session model for authentication session management."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class Session(Base):
    """
    Session model for managing user authentication sessions.
    
    Attributes:
        session_id: Unique session identifier (primary key)
        user_id: Foreign key to user
        created_at: Session creation timestamp
        expires_at: Session expiration timestamp
    """
    
    __tablename__ = "sessions"
    
    # Primary key
    session_id = Column(String(255), primary_key=True, index=True)
    
    # User reference
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    def __repr__(self) -> str:
        """String representation of Session."""
        return f"<Session(id={self.session_id}, user_id={self.user_id})>"
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    def to_dict(self) -> dict:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_expired": self.is_expired(),
        }
