"""Filter rule repository for data access operations."""

from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.filter_rule import FilterRule, RuleType


class FilterRepository:
    """Repository for filter rule data operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
    
    async def get_by_id(self, rule_id: int) -> Optional[FilterRule]:
        """Get filter rule by ID."""
        result = await self.session.execute(
            select(FilterRule).where(FilterRule.id == rule_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_mac_and_type(
        self, mac_address: str, rule_type: RuleType
    ) -> Optional[FilterRule]:
        """Get filter rule by MAC address and type."""
        result = await self.session.execute(
            select(FilterRule).where(
                and_(
                    FilterRule.mac_address == mac_address,
                    FilterRule.rule_type == rule_type.value
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_allowlist(self) -> List[FilterRule]:
        """Get all allowlist rules."""
        result = await self.session.execute(
            select(FilterRule)
            .where(FilterRule.rule_type == RuleType.ALLOWLIST.value)
            .order_by(FilterRule.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_blocklist(self) -> List[FilterRule]:
        """Get all blocklist rules."""
        result = await self.session.execute(
            select(FilterRule)
            .where(FilterRule.rule_type == RuleType.BLOCKLIST.value)
            .order_by(FilterRule.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, rule_data: dict) -> FilterRule:
        """Create new filter rule."""
        rule = FilterRule(**rule_data)
        self.session.add(rule)
        await self.session.flush()
        return rule
    
    async def delete(self, rule_id: int) -> bool:
        """Delete filter rule."""
        rule = await self.get_by_id(rule_id)
        if not rule:
            return False
        
        await self.session.delete(rule)
        await self.session.flush()
        return True
    
    async def delete_by_mac_and_type(
        self, mac_address: str, rule_type: RuleType
    ) -> bool:
        """Delete filter rule by MAC address and type."""
        rule = await self.get_by_mac_and_type(mac_address, rule_type)
        if not rule:
            return False
        
        await self.session.delete(rule)
        await self.session.flush()
        return True
    
    async def is_in_allowlist(self, mac_address: str) -> bool:
        """Check if MAC address is in allowlist."""
        rule = await self.get_by_mac_and_type(mac_address, RuleType.ALLOWLIST)
        return rule is not None
    
    async def is_in_blocklist(self, mac_address: str) -> bool:
        """Check if MAC address is in blocklist."""
        rule = await self.get_by_mac_and_type(mac_address, RuleType.BLOCKLIST)
        return rule is not None
