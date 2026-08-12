import sys
sys.path.append('../shared')

from shared.database import DatabaseManager, Base
from config import settings

# Create database manager instance
db_manager = DatabaseManager(settings.DATABASE_URL)

async def get_db():
    """Dependency for getting database session"""
    async for session in db_manager.get_session():
        yield session

async def init_db():
    """Initialize database"""
    await db_manager.init_db()

# Export engine for compatibility
engine = db_manager.engine
