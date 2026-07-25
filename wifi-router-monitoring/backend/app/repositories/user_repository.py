"""User repository for data access operations."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Repository for user data operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_data: dict) -> User:
        """Create new user."""
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()
        return user
    
    async def update_last_login(self, user_id: int) -> Optional[User]:
        """Update user's last login timestamp."""
        from datetime import datetime, timezone
        
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        user.last_login = datetime.now(timezone.utc)
        await self.session.flush()
        return user
    
    async def exists(self, username: str) -> bool:
        """Check if user exists."""
        user = await self.get_by_username(username)
        return user is not None
