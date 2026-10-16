from typing import Literal, Optional
from pydantic import BaseModel, Field
from app.models.agent_outputs_v2 import (
    MacroStressTestResult,
    NegotiationPlaybookResult,
    UrbanRenewalGISResult,
    VisionRenovationResult,
)


class MarketAnalysisResult(BaseModel):
    """Strict output schema for Sub-Agent 1: Market & Comps Agent."""

    avg_price_per_sqm_ils: float = Field(..., gt=0)
    subject_price_per_sqm_ils: float = Field(..., gt=0)
    market_deviation_pct: float = Field(
        ...,
        description="Positive = more expensive than market average, Negative = below market average",
    )
    estimated_monthly_rent_ils: float = Field(..., gt=0)
    comparable_transactions_count: int = Field(..., ge=0)
    neighborhood_highlights: list[str] = Field(default_factory=list)


class FinancialMetricsResult(BaseModel):
    """Strict output schema for Sub-Agent 2: Financial & Mortgage ROI Agent (Pure deterministic Python math)."""

    purchase_tax_ils: float = Field(..., ge=0)
    loan_amount_ils: float = Field(..., ge=0)
    loan_to_value_pct: float = Field(..., ge=0, le=100)
    monthly_mortgage_payment_ils: float = Field(..., ge=0)
    net_monthly_cashflow_ils: float
    gross_yield_pct: float
    net_cap_rate_pct: float
    cash_on_cash_return_pct: float
    projected_10yr_irr_pct: float


class LegalFinding(BaseModel):
    """Single legal or appraisal finding with mandatory document & page citation."""

    category: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    description: str
    source_document: str
    page_number: int = Field(..., ge=1)
    exact_quote: str = Field(..., min_length=3)


class LegalDueDiligenceResult(BaseModel):
    """Strict output schema for Sub-Agent 3: Legal & Appraisal RAG Agent."""

    findings: list[LegalFinding] = Field(default_factory=list)
    registered_area_sqm: Optional[float] = Field(
        default=None,
        description="Area in sqm registered in the Tabu extract for cross-verification against listing",
    )
    has_blocking_liens_or_warnings: bool = False


class CriticVerdict(BaseModel):
    """Strict output schema for Sub-Agent 4/5: Risk Critic & Guardrails Agent."""

    status: Literal["APPROVED", "NEEDS_HUMAN_REVIEW", "REJECTED"]
    overall_risk_score: int = Field(..., ge=1, le=100)
    context_clashes_detected: list[str] = Field(default_factory=list)
    math_verification_passed: bool
    hitl_reason: Optional[str] = None


class InvestmentExecutiveReport(BaseModel):
    """Final unified 9-Agent report returned by InvestmentOrchestrator (v1 + v2 Expansion Pack)."""

    run_id: str
    property_id: str
    status: Literal["RUNNING", "COMPLETED", "PAUSED_FOR_APPROVAL", "REJECTED", "FAILED"] = "COMPLETED"
    run_status: Literal["RUNNING", "COMPLETED", "PAUSED_FOR_APPROVAL", "REJECTED", "FAILED"] = "COMPLETED"
    market: MarketAnalysisResult
    financials: FinancialMetricsResult
    legal: LegalDueDiligenceResult
    critic: CriticVerdict
    vision_renovation: Optional[VisionRenovationResult] = None
    urban_renewal_gis: Optional[UrbanRenewalGISResult] = None
    macro_stress_test: Optional[MacroStressTestResult] = None
    negotiation_playbook: Optional[NegotiationPlaybookResult] = None
    investment_recommendation: Literal[
        "STRONG_BUY",
        "BUY_WITH_CAUTION",
        "HOLD_FOR_REVIEW",
        "AVOID",
    ]
    executive_summary: str
