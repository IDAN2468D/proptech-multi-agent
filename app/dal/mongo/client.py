from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import get_settings


class InMemoryAsyncCursor:
    """Async cursor compatible with Motor's cursor interface."""

    def __init__(self, docs: list[dict[str, Any]]) -> None:
        self._docs = docs

    def limit(self, count: int) -> "InMemoryAsyncCursor":
        self._docs = self._docs[:count]
        return self

    async def to_list(self, length: int | None = None) -> list[dict[str, Any]]:
        if length is None:
            return [dict(d) for d in self._docs]
        return [dict(d) for d in self._docs[:length]]


class InMemoryAsyncCollection:
    """Async MongoDB collection adapter for deterministic local/test execution."""

    def __init__(self) -> None:
        self._documents: list[dict[str, Any]] = []

    def _matches(self, doc: dict[str, Any], query: dict[str, Any]) -> bool:
        for k, v in query.items():
            if doc.get(k) != v:
                return False
        return True

    async def insert_one(self, document: dict[str, Any]) -> Any:
        self._documents.append(dict(document))
        return True

    async def insert_many(self, documents: list[dict[str, Any]]) -> Any:
        for doc in documents:
            self._documents.append(dict(doc))
        return True

    async def find_one(self, filter_query: dict[str, Any]) -> dict[str, Any] | None:
        for doc in self._documents:
            if self._matches(doc, filter_query):
                return dict(doc)
        return None

    def find(self, filter_query: dict[str, Any]) -> InMemoryAsyncCursor:
        matched = [dict(doc) for doc in self._documents if self._matches(doc, filter_query)]
        return InMemoryAsyncCursor(matched)

    async def update_one(
        self,
        filter_query: dict[str, Any],
        update_doc: dict[str, Any],
        upsert: bool = False,
    ) -> Any:
        set_payload = update_doc.get("$set", {})
        push_payload = update_doc.get("$push", {})
        for doc in self._documents:
            if self._matches(doc, filter_query):
                doc.update(set_payload)
                for pk, pv in push_payload.items():
                    doc.setdefault(pk, []).append(pv)
                return True
        if upsert:
            new_doc = {**filter_query, **set_payload}
            for pk, pv in push_payload.items():
                new_doc[pk] = [pv]
            self._documents.append(new_doc)
        return True

    async def delete_many(self, filter_query: dict[str, Any]) -> int:
        if not filter_query:
            count = len(self._documents)
            self._documents.clear()
            return count
        remaining = [d for d in self._documents if not self._matches(d, filter_query)]
        removed = len(self._documents) - len(remaining)
        self._documents = remaining
        return removed


class InMemoryAsyncDatabase:
    """In-memory database holding named collections."""

    def __init__(self) -> None:
        self._collections: dict[str, InMemoryAsyncCollection] = {}

    def __getitem__(self, name: str) -> InMemoryAsyncCollection:
        if name not in self._collections:
            self._collections[name] = InMemoryAsyncCollection()
        return self._collections[name]


_motor_client: AsyncIOMotorClient | None = None
_motor_loop: Any = None
_in_memory_db = InMemoryAsyncDatabase()


def get_mongo_db() -> AsyncIOMotorDatabase | InMemoryAsyncDatabase:
    """Return Motor AsyncIOMotorDatabase or in-memory async fallback."""
    global _motor_client, _motor_loop
    import asyncio

    settings = get_settings()
    if settings.USE_IN_MEMORY_MONGO_FALLBACK:
        return _in_memory_db
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None
    if _motor_client is None or _motor_loop is not current_loop:
        _motor_client = AsyncIOMotorClient(settings.MONGO_URI)
        _motor_loop = current_loop
    return _motor_client[settings.MONGO_DB_NAME]
