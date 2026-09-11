import logging
from typing import Any, Dict, List
import numpy as np
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Manages dense vector embedding generation and vector similarity calculations."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def get_embedding(self, text: str) -> List[float]:
        try:
            return await self.llm.generate_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Fallback zero/dummy vector
            return [0.0] * 1536

    @staticmethod
    def compute_similarity(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        a = np.array(v1, dtype=np.float32)
        b = np.array(v2, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
