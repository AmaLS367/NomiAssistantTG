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
            return_value=Response(200, json={
                "replyMessage": {
                    "text": "Hello, master.",
                    "role": "nomi"
                }
            })
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
            Response(200, json={"replyMessage": {"text": "Finally!"}})
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

