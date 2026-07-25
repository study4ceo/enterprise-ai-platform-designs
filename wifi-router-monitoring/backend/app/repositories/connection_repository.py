"""Connection event repository for data access operations."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.connection_event import ConnectionEvent


class ConnectionRepository:
    """Repository for connection event data operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
    
    async def create(self, event_data: dict) -> ConnectionEvent:
        """Create new connection event."""
        event = ConnectionEvent(**event_data)
        self.session.add(event)
        await self.session.flush()
        return event
    
    async def get_by_id(self, event_id: int) -> Optional[ConnectionEvent]:
        """Get connection event by ID."""
        result = await self.session.execute(
            select(ConnectionEvent).where(ConnectionEvent.id == event_id)
        )
        return result.scalar_one_or_none()
    
    async def query_by_filters(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        mac_address: Optional[str] = None,
        router_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ConnectionEvent]:
        """Query connection events with filters."""
        query = select(ConnectionEvent)
        
        conditions = []
        if start_date:
            conditions.append(ConnectionEvent.timestamp >= start_date)
        if end_date:
            conditions.append(ConnectionEvent.timestamp <= end_date)
        if mac_address:
            conditions.append(ConnectionEvent.mac_address == mac_address)
        if router_id:
            conditions.append(ConnectionEvent.router_id == router_id)
        if event_type:
            conditions.append(ConnectionEvent.event_type == event_type)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(ConnectionEvent.timestamp.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def count_by_filters(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        mac_address: Optional[str] = None,
        router_id: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> int:
        """Count connection events matching filters."""
        query = select(func.count(ConnectionEvent.id))
        
        conditions = []
        if start_date:
            conditions.append(ConnectionEvent.timestamp >= start_date)
        if end_date:
            conditions.append(ConnectionEvent.timestamp <= end_date)
        if mac_address:
            conditions.append(ConnectionEvent.mac_address == mac_address)
        if router_id:
            conditions.append(ConnectionEvent.router_id == router_id)
        if event_type:
            conditions.append(ConnectionEvent.event_type == event_type)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def delete_older_than(self, cutoff_date: datetime) -> int:
        """Delete connection events older than cutoff date."""
        from sqlalchemy import delete
        
        stmt = delete(ConnectionEvent).where(ConnectionEvent.timestamp < cutoff_date)
        result = await self.session.execute(stmt)
        return result.rowcount
