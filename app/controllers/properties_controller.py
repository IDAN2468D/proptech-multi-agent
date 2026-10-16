from typing import Any
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.bll.analysis_service import AnalysisService
from app.core.security import get_current_user_claims
from app.dal.sql.database import get_db_session
from app.models.property_schemas import (
    DocumentUploadResponse,
    PropertyCreateRequest,
    PropertyResponse,
)

router = APIRouter(prefix="/api/v1/properties", tags=["Properties & RAG Documents"])


@router.get("", response_model=list[PropertyResponse], status_code=status.HTTP_200_OK)
async def list_properties(
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_db_session),
) -> list[PropertyResponse]:
    service = AnalysisService(session)
    return await service.list_properties(user_id=str(claims["sub"]))


@router.post("", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    payload: PropertyCreateRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_db_session),
) -> PropertyResponse:
    service = AnalysisService(session)
    return await service.create_property(user_id=str(claims["sub"]), payload=payload)


@router.post(
    "/{property_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_property_document(
    property_id: str,
    file: UploadFile = File(...),
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_db_session),
) -> DocumentUploadResponse:
    file_bytes = await file.read()
    service = AnalysisService(session)
    return await service.upload_and_index_document(
        user_id=str(claims["sub"]),
        property_id=property_id,
        filename=file.filename or "document.pdf",
        file_bytes=file_bytes,
    )
