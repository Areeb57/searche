import logging
from typing import Any, Dict, List, Optional
from app.schemas.knowledge import ClaimProvenance

logger = logging.getLogger(__name__)


class ProvenanceTracker:
    """Maintains and queries the complete provenance lineage from claims to documents and source URLs."""

    def __init__(self):
        # Maps source_id -> source metadata (domain, url, title)
        self.sources: Dict[str, Dict[str, Any]] = {}
        # Maps doc_id -> doc metadata (url, source_id, title)
        self.documents: Dict[str, Dict[str, Any]] = {}
        # Maps claim_id -> claim metadata (text, doc_id, source_id)
        self.claims: Dict[str, Dict[str, Any]] = {}

    def register_source(self, source_id: str, url: str, domain: str, title: Optional[str] = None) -> None:
        self.sources[source_id] = {
            "source_id": source_id,
            "url": url,
            "domain": domain,
            "title": title or domain,
        }

    def register_document(self, doc_id: str, source_id: str, url: str, title: Optional[str] = None) -> None:
        self.documents[doc_id] = {
            "document_id": doc_id,
            "source_id": source_id,
            "url": url,
            "title": title,
        }

    def register_claim(self, claim_id: str, text: str, doc_id: str, source_id: str, importance: float = 0.8) -> None:
        self.claims[claim_id] = {
            "claim_id": claim_id,
            "text": text,
            "document_id": doc_id,
            "source_id": source_id,
            "importance": importance,
        }

    def trace_claim(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the full provenance trail for an individual claim."""
        claim_info = self.claims.get(claim_id)
        if not claim_info:
            return None

        doc_info = self.documents.get(claim_info["document_id"], {})
        source_info = self.sources.get(claim_info["source_id"], {})

        return {
            "claim_id": claim_id,
            "text": claim_info["text"],
            "importance": claim_info["importance"],
            "document": doc_info,
            "source": source_info,
        }

    def build_provenance_list(self, claim_ids: List[str]) -> List[ClaimProvenance]:
        """Construct ClaimProvenance items for a unified claim."""
        provenance_list: List[ClaimProvenance] = []
        for cid in claim_ids:
            claim_info = self.claims.get(cid)
            if not claim_info:
                continue
            s_id = claim_info["source_id"]
            d_id = claim_info["document_id"]
            source_info = self.sources.get(s_id, {})

            provenance_list.append(
                ClaimProvenance(
                    source_id=s_id,
                    document_id=d_id,
                    source_url=source_info.get("url"),
                    support="direct",
                )
            )
        return provenance_list
