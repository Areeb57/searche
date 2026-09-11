import json
import logging
from typing import List, Optional, Type, TypeVar
import httpx
from pydantic import BaseModel
from app.config import settings
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class ClaudeProvider(LLMProvider):
    """Anthropic Claude API provider adapter."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.CLAUDE_API_KEY
        self.model = model or settings.CLAUDE_MODEL
        self.base_url = "https://api.anthropic.com/v1"

        if not self.api_key:
            logger.warning("ClaudeProvider initialized without CLAUDE_API_KEY.")

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY is not configured.")

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 2048,
            "temperature": 0.3,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/messages", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"].strip()

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY is not configured.")

        schema_json = json.dumps(schema.model_json_schema())
        system_instruction = (
            f"{system_prompt or ''}\n\n"
            f"You MUST output valid JSON strictly conforming to this schema:\n"
            f"{schema_json}\n"
            f"Output only raw JSON with NO markdown tags."
        )

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "temperature": 0.1,
            "system": system_instruction,
            "messages": [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": "{"},  # Prefill JSON open bracket
            ],
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/messages", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            completion = "{" + data["content"][0]["text"]
            parsed = json.loads(completion)
            return schema.model_validate(parsed)

    async def generate_embedding(self, text: str) -> List[float]:
        # Claude doesn't have an embedding endpoint; generate deterministic pseudo-embedding
        # or use standard hash-based float projection
        import hashlib
        import numpy as np
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % (2**32)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(settings.EMBEDDING_DIM).astype(np.float32)
        vec /= np.linalg.norm(vec)
        return vec.tolist()
