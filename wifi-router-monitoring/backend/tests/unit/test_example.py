"""Example unit test to verify test framework is working."""

import pytest


def test_example_sync():
    """Example synchronous test."""
    assert 1 + 1 == 2


@pytest.mark.asyncio
async def test_example_async():
    """Example asynchronous test."""
    result = await async_add(5, 3)
    assert result == 8


async def async_add(a: int, b: int) -> int:
    """Example async function for testing."""
    return a + b


def test_example_with_fixture(mock_device_data):
    """Example test using a fixture."""
    assert mock_device_data["mac_address"] == "AA:BB:CC:DD:EE:FF"
    assert mock_device_data["ip_address"] == "192.168.1.100"


class TestExampleClass:
    """Example test class."""
    
    def test_method_example(self):
        """Example test method."""
        assert True
    
    @pytest.mark.asyncio
    async def test_async_method_example(self):
        """Example async test method."""
        result = await async_add(10, 20)
        assert result == 30
