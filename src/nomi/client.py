import httpx
import logging
import asyncio
import random
from typing import Any, Dict, List, Optional
from .schemas import NomiResponse

log = logging.getLogger(__name__)

class NomiClient:
    def __init__(self, api_key: str, timeout: float = 30.0):
        self._headers = {
            "Authorization": api_key,
            "User-Agent": "NomiTGCompanion/1.0 (+github.com/AmaLS367)"
        }
        self._timeout = httpx.Timeout(timeout, connect=15.0, read=timeout, write=timeout)
        self._base = "https://api.nomi.ai"

    async def _request(self, method: str, url: str, json: Optional[dict] = None) -> httpx.Response:
        # Simple retry logic retained for now; consider moving to tenancy or transport adapters later
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=self._timeout, headers=self._headers) as s:
                    r = await s.request(method, url, json=json)
                
                if r.status_code == 429 and attempt < 2:
                    retry_after = r.headers.get("Retry-After")
                    base = float(retry_after) if (retry_after and retry_after.isdigit()) else 0.8 * (attempt + 1)
                    await asyncio.sleep(base + random.uniform(0, 0.3))
                    continue
                
                if r.status_code >= 500 and attempt < 2:
                    await asyncio.sleep(0.8 * (attempt + 1) + random.uniform(0, 0.3))
                    continue

                r.raise_for_status()
                return r
            except (httpx.ReadTimeout, httpx.ConnectTimeout):
                if attempt == 2:
                    raise
                await asyncio.sleep(0.8 * (attempt + 1))
        raise RuntimeError("Unreachable: max retries exceeded")

    async def list_nomis(self) -> List[Dict[str, Any]]:
        r = await self._request("GET", f"{self._base}/v1/nomis")
        data = r.json()
        if isinstance(data, list):
            return data
        # Fallback for wrapped responses
        return data.get("nomis", []) if isinstance(data, dict) else []

    def _parse_response(self, data: Any) -> Optional[str]:
        if not isinstance(data, dict):
            # Fallback for raw strings if API behaves unexpectedly
            return str(data).strip() or None

        try:
            resp = NomiResponse.model_validate(data)
            
            # Priority 1: Direct reply field
            if resp.replyMessage:
                return resp.replyMessage.text or resp.replyMessage.content
            
            # Priority 2: Message field
            if resp.message:
                return resp.message.text or resp.message.content

            # Priority 3: Messages list (history)
            if resp.messages:
                # Try to find the last message from the bot/assistant
                for msg in reversed(resp.messages):
                    if msg.role in ("assistant", "nomi", "ai", "bot"):
                        return msg.text or msg.content
                
                # If no role matches, just take the last one
                last = resp.messages[-1]
                return last.text or last.content

        except Exception as e:
            log.warning(f"Pydantic validation failed: {e}. Data: {data}")
            
        return None

    async def chat_direct(self, nomi_id: str, text: str) -> Optional[str]:
        payload = {"messageText": text}
        r = await self._request("POST", f"{self._base}/v1/nomis/{nomi_id}/chat", json=payload)
        
        try:
            data = r.json()
            return self._parse_response(data)
        except Exception:
            raw = r.text
            log.warning("Non-JSON direct chat response: %s", raw)
            return raw.strip() or None
