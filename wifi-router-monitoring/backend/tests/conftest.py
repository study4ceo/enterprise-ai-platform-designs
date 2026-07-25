"""Pytest configuration and shared fixtures for the test suite."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.config import Settings
from app.database import Base, get_db
from app.main import app

# Test database URL (using in-memory SQLite for fast tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client with database session override."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        database_url=TEST_DATABASE_URL,
        secret_key="test-secret-key",
        debug=True,
        app_env="testing",
    )


# Mock data fixtures

@pytest.fixture
def mock_device_data() -> dict:
    """Sample device data for testing."""
    return {
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "ip_address": "192.168.1.100",
        "hostname": "test-device",
        "vendor": "Apple, Inc.",
        "friendly_name": None,
        "notes": None,
        "trusted": False,
    }


@pytest.fixture
def mock_router_data() -> dict:
    """Sample router data for testing."""
    return {
        "id": "test-router-1",
        "name": "Test Router",
        "protocol": "snmp",
        "host": "192.168.1.1",
        "port": 161,
        "credentials": {
            "community": "public",
            "version": "2c",
        },
        "scan_interval": 30,
        "enabled": True,
    }


@pytest.fixture
def mock_connection_event_data() -> dict:
    """Sample connection event data for testing."""
    return {
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "ip_address": "192.168.1.100",
        "hostname": "test-device",
        "router_id": "test-router-1",
        "event_type": "connected",
    }


@pytest.fixture
def mock_user_data() -> dict:
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "password": "testpassword123",
        "email": "testuser@example.com",
    }


# Router adapter mocks

@pytest.fixture
def mock_snmp_response():
    """Mock SNMP response data."""
    return [
        {
            "mac_address": "AA:BB:CC:DD:EE:FF",
            "ip_address": "192.168.1.100",
            "hostname": "device1",
        },
        {
            "mac_address": "11:22:33:44:55:66",
            "ip_address": "192.168.1.101",
            "hostname": "device2",
        },
    ]


@pytest.fixture
def mock_ssh_output():
    """Mock SSH command output."""
    return """
    Internet  192.168.1.100  15   AA:BB:CC:DD:EE:FF  ARPA   GigabitEthernet0/1
    Internet  192.168.1.101  30   11:22:33:44:55:66  ARPA   GigabitEthernet0/1
    """


# Helper functions

def create_test_device(session: AsyncSession, **kwargs):
    """Helper to create a test device in the database."""
    from app.models.device import Device
    from datetime import datetime, timezone
    
    device_data = {
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "ip_address": "192.168.1.100",
        "hostname": "test-device",
        "vendor": "Test Vendor",
        "trusted": False,
        "first_seen": datetime.now(timezone.utc),
        "last_seen": datetime.now(timezone.utc),
    }
    device_data.update(kwargs)
    
    device = Device(**device_data)
    session.add(device)
    return device


async def create_test_router(session: AsyncSession, **kwargs):
    """Helper to create a test router in the database."""
    from app.models.router import Router
    
    router_data = {
        "id": "test-router-1",
        "name": "Test Router",
        "protocol": "snmp",
        "host": "192.168.1.1",
        "port": 161,
        "credentials": {"community": "public"},
        "scan_interval": 30,
        "enabled": True,
    }
    router_data.update(kwargs)
    
    router = Router(**router_data)
    session.add(router)
    await session.commit()
    return router


async def create_test_user(session: AsyncSession, **kwargs):
    """Helper to create a test user in the database."""
    from app.models.user import User
    from app.services.auth_service import AuthService
    
    user_data = {
        "username": "testuser",
        "password": "testpassword123",
    }
    user_data.update(kwargs)
    
    auth_service = AuthService()
    password_hash = auth_service.hash_password(user_data["password"])
    
    user = User(
        username=user_data["username"],
        password_hash=password_hash,
    )
    session.add(user)
    await session.commit()
    return user


# Export helper functions for use in tests
__all__ = [
    "create_test_device",
    "create_test_router",
    "create_test_user",
]
