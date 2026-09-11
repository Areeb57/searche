import logging
from typing import Optional
from app.config import settings
from app.llm.base import LLMProvider
from app.llm.openai import OpenAIProvider
from app.llm.gemini import GeminiProvider
from app.llm.claude import ClaudeProvider
from app.llm.mock import MockLLMProvider

logger = logging.getLogger(__name__)


def get_llm_provider(override_name: Optional[str] = None) -> LLMProvider:
    """Factory function to resolve and instantiate the active LLMProvider."""
    provider_name = (override_name or settings.LLM_PROVIDER).lower()

    if provider_name == "openai":
        if settings.OPENAI_API_KEY:
            return OpenAIProvider()
        logger.warning("OPENAI_API_KEY missing. Falling back to MockLLMProvider.")
        return MockLLMProvider()

    elif provider_name == "gemini":
        if settings.GEMINI_API_KEY:
            return GeminiProvider()
        logger.warning("GEMINI_API_KEY missing. Falling back to MockLLMProvider.")
        return MockLLMProvider()

    elif provider_name == "claude":
        if settings.CLAUDE_API_KEY:
            return ClaudeProvider()
        logger.warning("CLAUDE_API_KEY missing. Falling back to MockLLMProvider.")
        return MockLLMProvider()

    elif provider_name == "mock":
        return MockLLMProvider()

    else:
        logger.warning(f"Unknown LLM provider '{provider_name}'. Defaulting to MockLLMProvider.")
        return MockLLMProvider()
