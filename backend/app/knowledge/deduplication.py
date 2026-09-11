import logging
import uuid
from typing import Any, Dict, List, Tuple
import numpy as np
from app.llm.base import LLMProvider
from app.schemas.knowledge import Claim, UnifiedClaim, ClaimProvenance
from app.knowledge.provenance import ProvenanceTracker

logger = logging.getLogger(__name__)


class ClaimDeduplicator:
    """Combines embedding vector cosine similarity and LLM semantic evaluation to deduplicate claims."""

    def __init__(self, llm: LLMProvider, provenance: ProvenanceTracker, similarity_threshold: float = 0.82):
        self.llm = llm
        self.provenance = provenance
        self.similarity_threshold = similarity_threshold

    @staticmethod
    def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
        a = np.array(v1, dtype=np.float32)
        b = np.array(v2, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    async def deduplicate_claims(self, claims: List[Claim]) -> List[UnifiedClaim]:
        """Group claims by semantic equivalence and generate UnifiedClaim entities with provenance."""
        if not claims:
            return []

        # 1. Generate embeddings for all claims
        claim_embeddings: List[List[float]] = []
        for c in claims:
            try:
                emb = await self.llm.generate_embedding(c.text)
            except Exception as e:
                logger.warning(f"Embedding error on claim '{c.text[:30]}': {e}")
                # Simple fallback pseudo-vector
                emb = [0.0] * 1536
            claim_embeddings.append(emb)

        # 2. Cluster claims based on similarity threshold
        clusters: List[List[int]] = []  # List of lists of claim indices
        assigned = set()

        n = len(claims)
        for i in range(n):
            if i in assigned:
                continue
            current_cluster = [i]
            assigned.add(i)

            for j in range(i + 1, n):
                if j in assigned:
                    continue
                sim = self._cosine_similarity(claim_embeddings[i], claim_embeddings[j])
                if sim >= self.similarity_threshold:
                    current_cluster.append(j)
                    assigned.add(j)

            clusters.append(current_cluster)

        # 3. Formulate Unified Claims
        unified_claims: List[UnifiedClaim] = []
        for idx, cluster in enumerate(clusters, start=1):
            cluster_claims = [claims[i] for i in cluster]
            # Primary canonical claim is the one with highest importance
            cluster_claims.sort(key=lambda x: x.importance, reverse=True)
            primary_claim = cluster_claims[0]

            # If cluster has multiple claims, ask LLM to synthesize the most precise canonical formulation
            canonical_text = primary_claim.text
            if len(cluster_claims) > 1:
                claim_texts = "\n".join([f"- {c.text}" for c in cluster_claims])
                prompt = (
                    f"The following statements from multiple research sources express the same core concept:\n"
                    f"{claim_texts}\n\n"
                    f"Synthesize them into one single, authoritative, precise claim statement (one sentence only)."
                )
                try:
                    synth_text = await self.llm.generate_text(prompt)
                    if synth_text and len(synth_text) > 10:
                        canonical_text = synth_text.strip().strip('"')
                except Exception as e:
                    logger.debug(f"Synthesis fallback to primary claim: {e}")

            # Collect source provenance
            provenance_map: Dict[str, ClaimProvenance] = {}
            for c in cluster_claims:
                doc_info = self.provenance.documents.get(c.source_document_id, {})
                source_info = self.provenance.sources.get(c.source_id or doc_info.get("source_id", ""), {})
                src_id = c.source_id or doc_info.get("source_id", "src_unknown")

                if src_id not in provenance_map:
                    provenance_map[src_id] = ClaimProvenance(
                        source_id=src_id,
                        document_id=c.source_document_id,
                        source_url=source_info.get("url"),
                        support="direct",
                    )

            u_id = f"uclm_{uuid.uuid4().hex[:8]}"
            unified = UnifiedClaim(
                id=u_id,
                text=canonical_text,
                confidence=round(min(1.0, 0.7 + (0.1 * len(cluster_claims))), 2),
                sources=list(provenance_map.values()),
                original_claim_ids=[c.id for c in cluster_claims],
            )
            unified_claims.append(unified)

        return unified_claims
