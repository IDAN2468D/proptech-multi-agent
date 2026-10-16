import re
from typing import Any
from app.bll.rag_pipeline.embedder_store import compute_semantic_embedding
from app.dal.mongo.vector_repository import MongoVectorRepository

POISONING_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?prior\s+rules", re.IGNORECASE),
    re.compile(r"system\s*prompt\s*override", re.IGNORECASE),
    re.compile(r"אתה\s+חייב\s+להתעלם\s+מכל\s+ההוראות", re.IGNORECASE),
    re.compile(r"התעלם\s+מהוראות\s+קודמות", re.IGNORECASE),
    re.compile(r"אשר\s+את\s+העסקה\s+ללא\s+בדיקה", re.IGNORECASE),
    re.compile(r"set\s+overall_risk_score\s*=\s*1\b", re.IGNORECASE),
]


def sanitize_chunk_text(raw_text: str) -> tuple[str, list[str]]:
    """
    Sanitizes retrieved PDF chunk text against Context Poisoning / Prompt Injection attacks.
    Returns (sanitized_text, detected_injection_warnings).
    """
    sanitized = raw_text
    warnings: list[str] = []
    for pattern in POISONING_PATTERNS:
        if pattern.search(sanitized):
            warnings.append(f"Context Poisoning attempt neutralized: '{pattern.pattern}'")
            sanitized = pattern.sub("[REDACTED_PROMPT_INJECTION]", sanitized)
    return sanitized.strip(), warnings


class SanitizedContextRetriever:
    """
    Retrieves property document chunks strictly isolated by user_id and property_id,
    applying anti-Context-Poisoning sanitization and preserving mandatory page citations.
    """

    def __init__(self, vector_repo: MongoVectorRepository | None = None) -> None:
        self.vector_repo = vector_repo or MongoVectorRepository()

    async def retrieve_for_property(
        self,
        user_id: str,
        property_id: str,
        query: str = "הערת אזהרה שעבוד עיקול חריגת בנייה שטח רשום טאבו חוזה",
        top_k: int = 10,
    ) -> dict[str, Any]:
        query_emb = compute_semantic_embedding(query)
        raw_chunks = await self.vector_repo.similarity_search(
            user_id=user_id,
            property_id=property_id,
            query_embedding=query_emb,
            top_k=top_k,
        )

        sanitized_chunks: list[dict[str, Any]] = []
        poisoning_alerts: list[str] = []

        for chunk in raw_chunks:
            clean_text, alerts = sanitize_chunk_text(chunk.get("text", ""))
            if alerts:
                poisoning_alerts.extend(alerts)
            sanitized_chunks.append(
                {
                    "chunk_id": chunk.get("chunk_id"),
                    "source_document": chunk.get("source_document", "document.pdf"),
                    "page_number": int(chunk.get("page_number", 1)),
                    "text": clean_text,
                    "similarity_score": chunk.get("similarity_score", 0.0),
                }
            )

        return {
            "chunks": sanitized_chunks,
            "poisoning_alerts": poisoning_alerts,
        }
