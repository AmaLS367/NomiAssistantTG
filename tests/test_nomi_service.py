from unittest.mock import AsyncMock, MagicMock

import pytest

from nomi.service import NomiService


@pytest.fixture
def mock_client():
    client = MagicMock()
    # Mocking list_nomis to return a standard list of dicts
    client.list_nomis = AsyncMock(return_value=[{"id": "uuid-1", "name": "Alice"}, {"id": "uuid-2", "name": "Bob"}])
    client.chat_direct = AsyncMock(return_value="Hello there")
    return client


@pytest.mark.asyncio
async def test_ensure_default_auto_select(mock_client):
    """If no default UUID is provided, pick the first one from the list."""
    service = NomiService(client=mock_client, default_nomi_id=None)

    uuid, name = await service.ensure_default()

    assert uuid == "uuid-1"
    assert name == "Alice"
    assert service.default_nomi_id == "uuid-1"  # Should be cached


@pytest.mark.asyncio
async def test_ensure_default_already_set(mock_client):
    """If UUID is provided in init, resolve its name."""
    service = NomiService(client=mock_client, default_nomi_id="uuid-2")

    uuid, name = await service.ensure_default()

    assert uuid == "uuid-2"
    assert name == "Bob"


@pytest.mark.asyncio
async def test_no_nomis_found(mock_client):
    """Raise error if account has no Nomis."""
    mock_client.list_nomis.return_value = []
    service = NomiService(client=mock_client, default_nomi_id=None)

    with pytest.raises(RuntimeError, match="No Nomi found"):
        await service.ensure_default()


@pytest.mark.asyncio
async def test_send_success(mock_client):
    """Test send method with successful response."""
    service = NomiService(client=mock_client, default_nomi_id="uuid-1")

    result = await service.send("Hello")

    assert result == "Hello there"
    mock_client.chat_direct.assert_called_once_with("uuid-1", "Hello")


@pytest.mark.asyncio
async def test_send_no_response(mock_client):
    """Test send method when client returns None."""
    mock_client.chat_direct.return_value = None
    service = NomiService(client=mock_client, default_nomi_id="uuid-1")

    result = await service.send("Hello")

    assert result == "No response"
