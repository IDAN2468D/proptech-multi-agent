import math
from typing import Any
from app.dal.mongo.client import get_mongo_db


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class MongoVectorRepository:
    """Repository for storing and querying vector-embedded PDF chunks in MongoDB."""

    COLLECTION_NAME = "property_rag_vectors"

    def __init__(self) -> None:
        self.db = get_mongo_db()
        self.collection = self.db[self.COLLECTION_NAME]

    async def insert_chunks(self, chunk_docs: list[dict[str, Any]]) -> int:
        if not chunk_docs:
            return 0
        await self.collection.insert_many([dict(d) for d in chunk_docs])
        return len(chunk_docs)

    async def delete_property_chunks(self, user_id: str, property_id: str) -> int:
        res = await self.collection.delete_many(
            {"user_id": user_id, "property_id": property_id}
        )
        return int(getattr(res, "deleted_count", res if isinstance(res, int) else 0))

    async def similarity_search(
        self,
        user_id: str,
        property_id: str,
        query_embedding: list[float],
        top_k: int = 8,
    ) -> list[dict[str, Any]]:
        """Retrieve chunks strictly isolated by user_id and property_id, ranked by cosine similarity."""
        cursor = self.collection.find({"user_id": user_id, "property_id": property_id})
        docs = await cursor.to_list(length=500)
        scored: list[tuple[float, dict[str, Any]]] = []
        for doc in docs:
            emb = doc.get("embedding", [])
            score = _cosine_similarity(query_embedding, emb)
            doc_copy = {k: v for k, v in doc.items() if k != "_id"}
            doc_copy["similarity_score"] = round(score, 4)
            scored.append((score, doc_copy))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored[:top_k]]
