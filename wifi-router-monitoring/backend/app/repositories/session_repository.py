"""Session repository for data access operations."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


class SessionRepository:
    """Repository for session data operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
    
    async def get_by_id(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        result = await self.session.execute(
            select(Session).where(Session.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, session_data: dict) -> Session:
        """Create new session."""
        session_obj = Session(**session_data)
        self.session.add(session_obj)
        await self.session.flush()
        return session_obj
    
    async def delete(self, session_id: str) -> bool:
        """Delete session."""
        session_obj = await self.get_by_id(session_id)
        if not session_obj:
            return False
        
        await self.session.delete(session_obj)
        await self.session.flush()
        return True
    
    async def cleanup_expired(self) -> int:
        """Delete all expired sessions."""
        now = datetime.now(timezone.utc)
        stmt = delete(Session).where(Session.expires_at < now)
        result = await self.session.execute(stmt)
        return result.rowcount
    
    async def exists(self, session_id: str) -> bool:
        """Check if session exists."""
        session_obj = await self.get_by_id(session_id)
        return session_obj is not None
    
    async def is_valid(self, session_id: str) -> bool:
        """Check if session exists and is not expired."""
        session_obj = await self.get_by_id(session_id)
        if not session_obj:
            return False
        return not session_obj.is_expired()
