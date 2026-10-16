from typing import Any, Literal
from pydantic import BaseModel, Field


class RenovationItem(BaseModel):
    """Single Bill of Quantities (BOQ) line item in ILS."""

    work_category: str
    area_or_units: float = Field(..., gt=0)
    unit_cost_ils: float = Field(..., ge=0)
    total_cost_ils: float = Field(..., ge=0)


class VisionRenovationResult(BaseModel):
    """Strict output schema for Agent 6: Vision Floorplan & Renovation Estimator Agent."""

    property_condition: Literal[
        "NEW",
        "GOOD",
        "NEEDS_COSMETIC_RENOVATION",
        "NEEDS_FULL_RENOVATION",
    ]
    can_add_room_or_split: bool
    structural_notes: list[str] = Field(default_factory=list)
    boq_items: list[RenovationItem] = Field(default_factory=list)
    total_estimated_renovation_ils: float = Field(..., ge=0)
    estimated_post_renovation_value_ils: float = Field(..., gt=0)


class UrbanRenewalGISResult(BaseModel):
    """Strict output schema for Agent 7: Urban Renewal (TAMA 38 / Pinui-Binui) & GIS Agent."""

    tama38_or_pinui_binui_likelihood: Literal["LOW", "MEDIUM", "HIGH", "ACTIVE_PLAN"]
    distance_to_light_rail_meters: int = Field(..., ge=0)
    walkability_score: int = Field(..., ge=1, le=100)
    expected_additional_sqm: float = Field(..., ge=0)
    projected_renewal_upside_pct: float = Field(..., ge=0)


class StressScenario(BaseModel):
    """Single stress scenario outcome."""

    scenario_name: str
    monthly_cashflow_ils: float
    annual_cashflow_ils: float


class MacroStressTestResult(BaseModel):
    """Strict output schema for Agent 8: Macro Stress-Test & Monte Carlo Agent."""

    base_case_monthly_cashflow_ils: float
    rate_hike_plus_1_5_pct_cashflow_ils: float
    vacancy_2_months_annual_cashflow_ils: float
    combined_worst_case_monthly_cashflow_ils: float
    probability_of_positive_cashflow_pct: float = Field(..., ge=0, le=100)
    max_safe_interest_rate_pct: float = Field(..., ge=0)


class PriceReductionJustification(BaseModel):
    """Single evidence-backed price reduction justification for negotiation."""

    reason: str
    deduction_amount_ils: float = Field(..., ge=0)
    evidence_source: str


class NegotiationPlaybookResult(BaseModel):
    """Strict output schema for Agent 9: AI Negotiation & Counter-Offer Strategist."""

    asking_price_ils: float = Field(..., gt=0)
    recommended_opening_offer_ils: float = Field(..., gt=0)
    target_closing_price_ils: float = Field(..., gt=0)
    walk_away_max_price_ils: float = Field(..., gt=0)
    price_reduction_justifications: list[dict[str, Any]] = Field(default_factory=list)
    ready_to_send_hebrew_message: str
