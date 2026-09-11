import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar
import numpy as np
from pydantic import BaseModel
from app.config import settings
from app.llm.base import LLMProvider
from app.schemas.search import GeneratedQueries
from app.schemas.knowledge import ExtractedArticleKnowledge, Claim, Entity, Fact, Recommendation, Statistic, Evidence, Limitation, Relationship

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(LLMProvider):
    """Smart offline Mock LLM provider for zero-cost local testing and verification."""

    def __init__(self, embedding_dim: int = 1536):
        self.embedding_dim = embedding_dim
        logger.info("MockLLMProvider initialized in offline mode.")

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        lower_p = prompt.lower()
        if "answer" in lower_p or "synthesize" in lower_p:
            return (
                "Based on the synthesized research, healthy weight gain requires a sustained, nutrient-dense caloric surplus "
                "combined with progressive resistance training. Key nutritional pillars include prioritizing whole food energy sources "
                "such as complex carbohydrates (oats, brown rice, whole grains), lean and plant proteins (eggs, poultry, legumes, dairy), "
                "and heart-healthy monounsaturated and polyunsaturated fats (avocados, nuts, seeds, olive oil). While most clinical sources "
                "emphasize a modest surplus of 300-500 kcal/day to minimize visceral adiposity, certain athletic guidelines advocate larger surpluses "
                "for accelerated hypertrophic stimulus."
            )
        if "question" in lower_p or "follow-up" in lower_p:
            return (
                "Regarding your follow-up inquiry: The consensus across primary research sources highlights nuts, nut butters, avocados, "
                "and whole grains as the most consistently recommended calorie-dense staples. Clinical sources specifically noted that "
                "liquid calories (such as whole milk smoothies) produce lower satiety per calorie, making surplus goals significantly easier to attain."
            )
        return f"Mock response analyzing: {prompt[:80]}... All criteria evaluated with high confidence."

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        schema_name = schema.__name__

        # Mock for Query Generation
        if schema_name == "GeneratedQueries" or issubclass(schema, GeneratedQueries):
            topic = prompt.split(":")[-1].strip() if ":" in prompt else prompt
            queries = [
                f"{topic}",
                f"high calorie nutrient dense foods for {topic}",
                f"protein rich diet strategies for {topic}",
                f"clinical nutrition guidelines and risks for {topic}",
            ]
            return schema.model_validate({"original_query": prompt, "queries": queries})

        # Mock for Article Knowledge Extraction
        if schema_name == "ExtractedArticleKnowledge" or issubclass(schema, ExtractedArticleKnowledge):
            hash_suffix = hashlib.md5(prompt.encode()).hexdigest()[:6]
            data = {
                "topic": "Nutrition and Caloric Surplus Strategies",
                "summary": "Clinical analysis of progressive caloric surplus, macronutrient distribution, and satiety mechanics.",
                "claims": [
                    {
                        "id": f"claim_{hash_suffix}_1",
                        "text": "A caloric surplus of 300 to 500 calories daily promotes lean tissue accumulation while mitigating fat accretion.",
                        "importance": 0.95,
                        "source_document_id": "doc_current",
                        "source_id": "src_current",
                    },
                    {
                        "id": f"claim_{hash_suffix}_2",
                        "text": "Protein consumption of 1.6 to 2.2 grams per kilogram of body weight optimizes muscle protein synthesis.",
                        "importance": 0.92,
                        "source_document_id": "doc_current",
                        "source_id": "src_current",
                    },
                    {
                        "id": f"claim_{hash_suffix}_3",
                        "text": "Nut butters, olive oil, and avocados deliver high caloric density without triggering premature digestive satiety.",
                        "importance": 0.88,
                        "source_document_id": "doc_current",
                        "source_id": "src_current",
                    },
                ],
                "facts": [
                    {"text": "1 gram of fat provides 9 calories compared to 4 calories per gram of carbohydrate or protein.", "confidence": 1.0},
                    {"text": "Liquid meal alternatives digest faster than fibrous whole solids.", "confidence": 0.95},
                ],
                "entities": [
                    {"name": "Caloric Surplus", "type": "concept", "description": "Consuming more calories than total daily expenditure."},
                    {"name": "Protein", "type": "nutrient", "description": "Essential macronutrient composed of amino acids."},
                    {"name": "Avocado", "type": "food", "description": "High-fat fruit rich in oleic acid."},
                    {"name": "Peanut Butter", "type": "food", "description": "Calorie-dense spread rich in lipids and protein."},
                ],
                "recommendations": [
                    {"text": "Add two tablespoons of olive oil or flaxseed oil to salads or grains to add 240 calories effortlessly.", "priority": "high"},
                    {"text": "Incorporate nutrient-dense liquid smoothies between solid meals.", "priority": "medium"},
                ],
                "statistics": [
                    {"metric": "Surplus Range", "value": "300-500 kcal/day", "context": "Recommended for controlled lean mass gain"},
                    {"metric": "Protein Ratio", "value": "1.6-2.2 g/kg", "context": "Optimal threshold for muscle protein synthesis"},
                ],
                "evidence": [
                    {"claim": "Protein drives hypertrophy", "finding": "Meta-analysis of 49 trials demonstrated positive correlation up to 1.6g/kg."},
                ],
                "limitations": [
                    {"text": "Excessive surplus over 1000 kcal/day exponentially increases visceral adipose deposition rather than muscle tissue."},
                ],
                "definitions": [
                    {"term": "Satiety", "definition": "The physiological feeling of fullness and satisfaction following food intake."},
                ],
                "relationships": [
                    {"source_entity": "Caloric Surplus", "target_entity": "Weight Gain", "relation_type": "causes", "description": "Direct positive energy balance."},
                    {"source_entity": "Protein", "target_entity": "Muscle Growth", "relation_type": "supports", "description": "Substrate for protein synthesis."},
                ],
            }
            return schema.model_validate(data)

        # Generic fallback for any arbitrary Pydantic schema
        try:
            return schema.model_validate({})
        except Exception:
            # Construct minimal dummy dict from schema fields
            mock_dict = {}
            for field_name, field_info in schema.model_fields.items():
                if field_info.annotation == str or field_info.annotation == Optional[str]:
                    mock_dict[field_name] = f"Mock {field_name}"
                elif field_info.annotation == int or field_info.annotation == Optional[int]:
                    mock_dict[field_name] = 1
                elif field_info.annotation == float or field_info.annotation == Optional[float]:
                    mock_dict[field_name] = 0.9
                elif field_info.annotation == bool or field_info.annotation == Optional[bool]:
                    mock_dict[field_name] = True
                elif getattr(field_info.annotation, "__origin__", None) is list:
                    mock_dict[field_name] = []
                elif getattr(field_info.annotation, "__origin__", None) is dict:
                    mock_dict[field_name] = {}
                else:
                    mock_dict[field_name] = None
            return schema.model_validate(mock_dict)

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate deterministic normalized vector using MD5 hash as pseudo-random seed."""
        clean_text = text.strip().lower()
        seed = int(hashlib.md5(clean_text.encode("utf-8")).hexdigest(), 16) % (2**32)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self.embedding_dim).astype(np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.tolist()
