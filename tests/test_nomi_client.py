import pytest
import respx
from httpx import Response

from nomi.client import NomiClient


@pytest.fixture
def client():
    return NomiClient(api_key="fake-key")


@pytest.mark.asyncio
async def test_chat_direct_success(client):
    """Test successful message send and parsing."""
    async with respx.mock:
        route = respx.post("https://api.nomi.ai/v1/nomis/nomi-uuid/chat").mock(
            return_value=Response(200, json={"replyMessage": {"text": "Hello, master.", "role": "nomi"}})
        )

        response = await client.chat_direct("nomi-uuid", "Hi")

        assert response == "Hello, master."
        assert route.called


@pytest.mark.asyncio
async def test_chat_retry_logic(client):
    """Test that the client retries on 429 errors."""
    async with respx.mock:
        route = respx.post("https://api.nomi.ai/v1/nomis/nomi-uuid/chat")
        # Fail twice with 429, then succeed
        route.side_effect = [
            Response(429, headers={"Retry-After": "0.1"}),
            Response(429, headers={"Retry-After": "0.1"}),
            Response(200, json={"replyMessage": {"text": "Finally!"}}),
        ]

        response = await client.chat_direct("nomi-uuid", "Hi")

        assert response == "Finally!"
        assert route.call_count == 3


@pytest.mark.asyncio
async def test_parse_malformed_response(client):
    """Test handling of unexpected JSON structure."""
    async with respx.mock:
        respx.post("https://api.nomi.ai/v1/nomis/nomi-uuid/chat").mock(
            return_value=Response(200, json={"unexpected": "data"})
        )

        # Should return None gently, logged as warning
        response = await client.chat_direct("nomi-uuid", "Hi")
        assert response is None


@pytest.mark.asyncio
async def test_list_nomis_success(client):
    """Test fetching the list of Nomis."""
    async with respx.mock:
        respx.get("https://api.nomi.ai/v1/nomis").mock(
            return_value=Response(200, json={"nomis": [{"id": "1", "name": "Nomi"}]})
        )

        nomis = await client.list_nomis()

        assert len(nomis) == 1
        assert nomis[0]["id"] == "1"


@pytest.mark.asyncio
async def test_list_nomis_direct_list(client):
    """Test list_nomis when API returns a list directly."""
    async with respx.mock:
        respx.get("https://api.nomi.ai/v1/nomis").mock(return_value=Response(200, json=[{"id": "1", "name": "Nomi"}]))

        nomis = await client.list_nomis()

        assert len(nomis) == 1
        assert nomis[0]["id"] == "1"


@pytest.mark.asyncio
async def test_chat_retry_500_error(client):
    """Test that the client retries on 500 errors."""
    async with respx.mock:
        route = respx.post("https://api.nomi.ai/v1/nomis/nomi-uuid/chat")
        route.side_effect = [Response(500), Response(200, json={"replyMessage": {"text": "Success after retry"}})]

        response = await client.chat_direct("nomi-uuid", "Hi")

        assert response == "Success after retry"
        assert route.call_count == 2


@pytest.mark.asyncio
async def test_parse_response_message_field(client):
    """Test parsing response with message field."""
    async with respx.mock:
        respx.post("https://api.nomi.ai/v1/nomis/nomi-uuid/chat").mock(
            return_value=Response(200, json={"message": {"text": "Message text", "role": "nomi"}})
        )

        response = await client.chat_direct("nomi-uuid", "Hi")

        assert response == "Message text"


@pytest.mark.asyncio
async def test_parse_response_messages_list(client):
    """Test parsing response with messages list."""
    async with respx.mock:
        respx.post("https://api.nomi.ai/v1/nomis/nomi-uuid/chat").mock(
            return_value=Response(
                200, json={"messages": [{"text": "First", "role": "user"}, {"text": "Second", "role": "nomi"}]}
            )
        )

        response = await client.chat_direct("nomi-uuid", "Hi")

        assert response == "Second"


@pytest.mark.asyncio
async def test_parse_response_non_dict(client):
    """Test parsing response with non-dict data."""
    async with respx.mock:
        respx.post("https://api.nomi.ai/v1/nomis/nomi-uuid/chat").mock(return_value=Response(200, json="Just a string"))

        response = await client.chat_direct("nomi-uuid", "Hi")

        assert response == "Just a string"


@pytest.mark.asyncio
async def test_chat_direct_non_json_response(client):
    """Test handling of non-JSON response."""
    async with respx.mock:
        respx.post("https://api.nomi.ai/v1/nomis/nomi-uuid/chat").mock(
            return_value=Response(200, text="Plain text response")
        )

        response = await client.chat_direct("nomi-uuid", "Hi")

        assert response == "Plain text response"
