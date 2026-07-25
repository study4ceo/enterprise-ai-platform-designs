"""Router repository for data access operations."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.router import Router


class RouterRepository:
    """Repository for router data operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
    
    async def get_by_id(self, router_id: str) -> Optional[Router]:
        """Get router by ID."""
        result = await self.session.execute(
            select(Router).where(Router.id == router_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, enabled_only: bool = False) -> List[Router]:
        """Get all routers."""
        query = select(Router)
        if enabled_only:
            query = query.where(Router.enabled == True)
        query = query.order_by(Router.name)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create(self, router_data: dict) -> Router:
        """Create new router."""
        router = Router(**router_data)
        self.session.add(router)
        await self.session.flush()
        return router
    
    async def update(self, router_id: str, update_data: dict) -> Optional[Router]:
        """Update router."""
        router = await self.get_by_id(router_id)
        if not router:
            return None
        
        for key, value in update_data.items():
            if hasattr(router, key):
                setattr(router, key, value)
        
        await self.session.flush()
        return router
    
    async def delete(self, router_id: str) -> bool:
        """Delete router."""
        router = await self.get_by_id(router_id)
        if not router:
            return False
        
        await self.session.delete(router)
        await self.session.flush()
        return True
    
    async def exists(self, router_id: str) -> bool:
        """Check if router exists."""
        router = await self.get_by_id(router_id)
        return router is not None
