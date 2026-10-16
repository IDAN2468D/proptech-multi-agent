from app.dal.mongo.memory_repository import InvestorMemoryRepository
from app.models.property_schemas import (
    InvestorProfileSchema,
    InvestorProfileUpdateRequest,
)


class InvestorMemoryService:
    """BLL service managing Investor Long-Term Memory in MongoDB."""

    def __init__(self, memory_repo: InvestorMemoryRepository | None = None) -> None:
        self.memory_repo = memory_repo or InvestorMemoryRepository()

    async def get_profile(self, user_id: str) -> InvestorProfileSchema:
        raw = await self.memory_repo.get_investor_profile(user_id)
        return InvestorProfileSchema(**raw)

    async def update_profile(
        self,
        user_id: str,
        payload: InvestorProfileUpdateRequest,
    ) -> InvestorProfileSchema:
        updates = payload.model_dump(exclude_unset=True, exclude_none=True)
        updated = await self.memory_repo.upsert_investor_profile(user_id, updates)
        return InvestorProfileSchema(**updated)
