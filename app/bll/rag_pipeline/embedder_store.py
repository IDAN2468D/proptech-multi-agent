import hashlib
import math
from typing import Any
from app.bll.rag_pipeline.loader_splitter import DocumentChunk
from app.dal.mongo.vector_repository import MongoVectorRepository

LEGAL_DOMAIN_KEYWORDS: list[str] = [
    "הערת אזהרה",
    "שעבוד",
    "עיקול",
    "משכנתא",
    "חריגת בנייה",
    "צו הריסה",
    "שטח",
    "מ\"ר",
    "מר",
    "טאבו",
    "גוש",
    "חלקה",
    "תת חלקה",
    "זכויות בנייה",
    "פיצוי מוסכם",
    "איחור במסירה",
    "הפקעה",
    "כינוס נכסים",
    "warning",
    "lien",
    "foreclosure",
    "sqm",
]


def compute_semantic_embedding(text: str, dim: int = 32) -> list[float]:
    """
    Deterministic domain-aware vector embedding combining legal keyword activation
    channels and n-gram hash projections (normalized to unit length).
    """
    vec = [0.0] * dim
    lowered = text.lower()

    for idx, kw in enumerate(LEGAL_DOMAIN_KEYWORDS):
        if kw in lowered:
            vec[idx % dim] += 3.0

    words = lowered.split()
    for word in words:
        digest = hashlib.sha256(word.encode("utf-8")).digest()
        bucket = digest[0] % dim
        sign = 1.0 if (digest[1] % 2 == 0) else -1.0
        vec[bucket] += sign * 0.5

    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return [1.0 / math.sqrt(dim)] * dim
    return [round(v / norm, 6) for v in vec]


class EmbedderStoreService:
    """Embeds split PDF chunks and indexes them into MongoDB Vector Store."""

    def __init__(self, vector_repo: MongoVectorRepository | None = None) -> None:
        self.vector_repo = vector_repo or MongoVectorRepository()

    async def index_property_chunks(
        self,
        user_id: str,
        property_id: str,
        chunks: list[DocumentChunk],
    ) -> int:
        docs: list[dict[str, Any]] = []
        for chunk in chunks:
            embedding = compute_semantic_embedding(chunk.text)
            docs.append(
                {
                    "user_id": user_id,
                    "property_id": property_id,
                    "chunk_id": chunk.chunk_id,
                    "source_document": chunk.source_document,
                    "page_number": chunk.page_number,
                    "text": chunk.text,
                    "embedding": embedding,
                }
            )
        return await self.vector_repo.insert_chunks(docs)
