from typing import Any
from fastapi import APIRouter, Depends
from app.bll.investor_memory_service import InvestorMemoryService
from app.core.security import get_current_user_claims
from app.models.property_schemas import (
    InvestorProfileSchema,
    InvestorProfileUpdateRequest,
)

router = APIRouter(prefix="/api/v1/investor", tags=["Investor Memory Profile"])


@router.get("/profile", response_model=InvestorProfileSchema)
async def get_investor_profile(
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> InvestorProfileSchema:
    service = InvestorMemoryService()
    return await service.get_profile(user_id=str(claims["sub"]))


@router.put("/profile", response_model=InvestorProfileSchema)
async def update_investor_profile(
    payload: InvestorProfileUpdateRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> InvestorProfileSchema:
    service = InvestorMemoryService()
    return await service.update_profile(user_id=str(claims["sub"]), payload=payload)
