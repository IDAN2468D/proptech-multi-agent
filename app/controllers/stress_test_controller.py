from typing import Any
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.bll.analysis_service import AnalysisService
from app.core.security import get_current_user_claims
from app.dal.sql.database import get_db_session
from app.models.agent_outputs_v2 import MacroStressTestResult


class InteractiveStressTestRequest(BaseModel):
    interest_rate_pct: float = Field(default=4.85, gt=0, le=20.0)
    monthly_rent_ils: float = Field(default=6800.0, gt=0)
    renovation_overrun_ils: float = Field(default=0.0, ge=0)
    equity_override_ils: float | None = Field(default=None, gt=0)


class ShareDealRequest(BaseModel):
    webhook_channel: str = "#proptech-deals"


router = APIRouter(prefix="/api/v1/analysis", tags=["Stress-Test & Deal-Room (v2.0)"])


@router.post(
    "/{run_id}/stress-test",
    response_model=MacroStressTestResult,
    status_code=status.HTTP_200_OK,
)
async def run_what_if_stress_test(
    run_id: str,
    payload: InteractiveStressTestRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_db_session),
) -> MacroStressTestResult:
    service = AnalysisService(session)
    res = await service.run_interactive_stress_test(
        user_id=str(claims["sub"]),
        run_id=run_id,
        interest_rate_pct=payload.interest_rate_pct,
        monthly_rent_ils=payload.monthly_rent_ils,
        renovation_overrun_ils=payload.renovation_overrun_ils,
        equity_override_ils=payload.equity_override_ils,
    )
    return MacroStressTestResult(**res)


@router.post(
    "/{run_id}/share-deal",
    status_code=status.HTTP_200_OK,
)
async def share_deal_to_slack_and_calendar(
    run_id: str,
    payload: ShareDealRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    service = AnalysisService(session)
    return await service.share_deal_package(
        user_id=str(claims["sub"]),
        run_id=run_id,
        webhook_channel=payload.webhook_channel,
    )
