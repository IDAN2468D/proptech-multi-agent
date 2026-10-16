from typing import Any
from fastapi import APIRouter, Depends, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.bll.analysis_service import AnalysisService
from app.core.security import get_current_user_claims
from app.dal.sql.database import get_db_session
from app.models.agent_outputs_v2 import VisionRenovationResult

router = APIRouter(prefix="/api/v1/properties", tags=["Vision & Floorplan Agent (v2.0)"])


@router.post(
    "/{property_id}/vision-upload",
    response_model=VisionRenovationResult,
    status_code=status.HTTP_200_OK,
)
async def upload_floorplan_and_photos(
    property_id: str,
    property_condition_hint: str = Form(default="NEEDS_COSMETIC_RENOVATION"),
    has_dampness_hint: bool = Form(default=False),
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_db_session),
) -> VisionRenovationResult:
    service = AnalysisService(session)
    data = await service.analyze_property_vision(
        user_id=str(claims["sub"]),
        property_id=property_id,
        property_condition_hint=property_condition_hint,
        has_dampness_hint=has_dampness_hint,
    )
    return VisionRenovationResult(**data)
