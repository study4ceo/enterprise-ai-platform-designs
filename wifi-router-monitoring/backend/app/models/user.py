"""User model for authentication."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class User(Base):
    """
    User model for authentication and authorization.
    
    Attributes:
        id: Auto-incrementing primary key
        username: Unique username
        password_hash: Bcrypt password hash
        email: User email address
        created_at: Account creation timestamp
        last_login: Last login timestamp
    """
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # User credentials
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # User information
    email = Column(String(255), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, username={self.username})>"
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding password hash)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
