from typing import Any, Literal
from pydantic import BaseModel, Field


class InvestorProfileSchema(BaseModel):
    user_id: str | None = None
    available_equity_ils: float = Field(default=800000.0, gt=0)
    risk_tolerance: Literal["CONSERVATIVE", "MODERATE", "AGGRESSIVE"] = "MODERATE"
    max_risk_score_threshold: int = Field(default=70, ge=1, le=100)
    min_target_net_yield_pct: float = Field(default=3.2, ge=0.0)
    preferred_cities: list[str] = Field(default_factory=lambda: ["תל אביב", "חיפה", "רמת גן"])
    is_single_home_buyer: bool = False
    analysis_history: list[dict[str, Any]] = Field(default_factory=list)


class InvestorProfileUpdateRequest(BaseModel):
    available_equity_ils: float | None = Field(default=None, gt=0)
    risk_tolerance: Literal["CONSERVATIVE", "MODERATE", "AGGRESSIVE"] | None = None
    max_risk_score_threshold: int | None = Field(default=None, ge=1, le=100)
    min_target_net_yield_pct: float | None = Field(default=None, ge=0.0)
    preferred_cities: list[str] | None = None
    is_single_home_buyer: bool | None = None


class PropertyCreateRequest(BaseModel):
    address: str = Field(..., min_length=3, max_length=500)
    city: str = Field(..., min_length=2, max_length=120)
    neighborhood: str = Field(default="", max_length=120)
    asking_price_ils: float = Field(..., gt=0)
    area_sqm: float = Field(..., gt=10)
    rooms: float = Field(default=4.0, gt=0.5)
    floor: int = Field(default=1)
    estimated_monthly_rent_ils: float | None = Field(default=None, gt=0)
    is_single_home: bool = False


class PropertyResponse(BaseModel):
    id: str
    owner_user_id: str
    address: str
    city: str
    neighborhood: str
    asking_price_ils: float
    area_sqm: float
    rooms: float
    floor: int
    estimated_monthly_rent_ils: float | None = None
    is_single_home: bool


class DocumentUploadResponse(BaseModel):
    property_id: str
    filename: str
    chunks_indexed: int
    pages_extracted: int
    sanitized_warnings: list[str] = Field(default_factory=list)


class AnalysisRunRequest(BaseModel):
    property_id: str
    equity_ils: float | None = Field(default=None, gt=0)
    annual_interest_rate_pct: float = Field(default=4.85, gt=0, le=20.0)
    loan_years: int = Field(default=25, ge=4, le=35)
    annual_expenses_ils: float = Field(default=6000.0, ge=0)
    appreciation_rate_pct: float = Field(default=3.0, ge=-10.0, le=25.0)


class HITLApproveRequest(BaseModel):
    approved: bool = True
    updated_asking_price_ils: float | None = Field(default=None, gt=0)
    updated_equity_ils: float | None = Field(default=None, gt=0)
    investor_notes: str = ""
