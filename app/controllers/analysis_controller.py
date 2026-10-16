from typing import Any
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.bll.analysis_service import AnalysisService
from app.core.security import get_current_user_claims
from app.dal.sql.database import get_db_session
from app.models.agent_outputs import InvestmentExecutiveReport
from app.models.property_schemas import AnalysisRunRequest, HITLApproveRequest

router = APIRouter(prefix="/api/v1/analysis", tags=["Multi-Agent Analysis & HITL"])


@router.post("/run", response_model=InvestmentExecutiveReport)
async def run_analysis(
    payload: AnalysisRunRequest,
    response: Response,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_db_session),
) -> InvestmentExecutiveReport:
    service = AnalysisService(session)
    paused_for_hitl, report = await service.run_investment_analysis(
        user_id=str(claims["sub"]),
        payload=payload,
    )
    if paused_for_hitl:
        response.status_code = status.HTTP_202_ACCEPTED
    else:
        response.status_code = status.HTTP_200_OK
    return report


@router.post("/{run_id}/approve", response_model=InvestmentExecutiveReport)
async def approve_hitl(
    run_id: str,
    payload: HITLApproveRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_db_session),
) -> InvestmentExecutiveReport:
    service = AnalysisService(session)
    return await service.approve_hitl_run(
        user_id=str(claims["sub"]),
        run_id=run_id,
        payload=payload,
    )


@router.get("/{run_id}", response_model=InvestmentExecutiveReport)
async def get_analysis_run(
    run_id: str,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_db_session),
) -> InvestmentExecutiveReport:
    service = AnalysisService(session)
    return await service.get_analysis_run(
        user_id=str(claims["sub"]),
        run_id=run_id,
    )
