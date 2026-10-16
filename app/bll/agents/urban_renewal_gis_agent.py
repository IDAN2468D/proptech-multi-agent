from typing import Any, Literal
from pydantic import BaseModel, Field
from app.models.agent_outputs_v2 import UrbanRenewalGISResult

CITY_GIS_RENEWAL_DB: dict[str, dict[str, Any]] = {
    "תל אביב": {
        "likelihood": "ACTIVE_PLAN",
        "light_rail_m": 280,
        "walkability": 94,
        "add_sqm": 14.0,
        "upside_pct": 26.5,
    },
    "רמת גן": {
        "likelihood": "HIGH",
        "light_rail_m": 410,
        "walkability": 89,
        "add_sqm": 12.0,
        "upside_pct": 24.0,
    },
    "חיפה": {
        "likelihood": "HIGH",
        "light_rail_m": 350,
        "walkability": 84,
        "add_sqm": 12.5,
        "upside_pct": 21.5,
    },
    "ירושלים": {
        "likelihood": "HIGH",
        "light_rail_m": 320,
        "walkability": 86,
        "add_sqm": 12.0,
        "upside_pct": 22.0,
    },
    "באר שבע": {
        "likelihood": "MEDIUM",
        "light_rail_m": 620,
        "walkability": 78,
        "add_sqm": 12.0,
        "upside_pct": 16.0,
    },
}


class UrbanRenewalGISContext(BaseModel):
    """Isolated minimal context for Agent 7: Urban Renewal & GIS Agent."""

    city: str
    address: str
    neighborhood: str = ""
    area_sqm: float = Field(..., gt=0)
    floor: int = 1


class UrbanRenewalGISAgent:
    """
    Sub-Agent 7: Urban Renewal (TAMA 38 / Pinui-Binui) & GIS Agent.
    Evaluates TAMA 38 / Pinui-Binui feasibility, transit proximity, walkability,
    and projected post-renewal sqm/value upside.
    """

    async def run(self, context: UrbanRenewalGISContext) -> UrbanRenewalGISResult:
        entry = CITY_GIS_RENEWAL_DB.get(
            context.city.strip(),
            {
                "likelihood": "MEDIUM",
                "light_rail_m": 540,
                "walkability": 80,
                "add_sqm": 12.0,
                "upside_pct": 18.0,
            },
        )
        likelihood: Literal["LOW", "MEDIUM", "HIGH", "ACTIVE_PLAN"] = entry["likelihood"]
        return UrbanRenewalGISResult(
            tama38_or_pinui_binui_likelihood=likelihood,
            distance_to_light_rail_meters=int(entry["light_rail_m"]),
            walkability_score=int(entry["walkability"]),
            expected_additional_sqm=float(entry["add_sqm"]),
            projected_renewal_upside_pct=float(entry["upside_pct"]),
        )
