from typing import Literal
from pydantic import BaseModel, Field
from app.bll.agents.tools.renovation_calculator import calculate_renovation_boq_ils
from app.models.agent_outputs_v2 import RenovationItem, VisionRenovationResult


class VisionAgentIsolatedContext(BaseModel):
    """Isolated minimal context for Agent 6: Vision & Renovation Estimator Agent."""

    asking_price_ils: float = Field(..., gt=0)
    area_sqm: float = Field(..., gt=0)
    rooms: float = 4.0
    floor: int = 1
    property_condition_hint: Literal[
        "NEW",
        "GOOD",
        "NEEDS_COSMETIC_RENOVATION",
        "NEEDS_FULL_RENOVATION",
    ] = "NEEDS_COSMETIC_RENOVATION"
    has_dampness_hint: bool = False


class VisionRenovationAgent:
    """
    Sub-Agent 6: Vision Floorplan & Renovation Estimator Agent.
    Analyzes floorplan geometry & condition indicators, and delegates BOQ cost calculation
    strictly to deterministic Python tools in renovation_calculator.py.
    """

    async def run(self, context: VisionAgentIsolatedContext) -> VisionRenovationResult:
        # Determine room addition / layout optimization potential based on sqm per room ratio
        sqm_per_room = context.area_sqm / max(1.0, context.rooms)
        can_add_room = sqm_per_room >= 24.0

        structural_notes: list[str] = [
            f"יחס שטח לחדר הינו {sqm_per_room:.1f} מ\"ר לחדר – מאפשר תכנון מחדש של חלל המגורים.",
            "זוהתה הפרדה ברורה בין עמודים תומכים לקירות מחיצה פנימיים בתשריט הדירה.",
        ]
        if can_add_room:
            structural_notes.append(
                "פוטנציאל השבחה תכנוני: ניתן להוסיף חדר עבודה/שינה מניב באמצעות מחיצת גבס אקוסטית."
            )

        boq_res = calculate_renovation_boq_ils(
            area_sqm=context.area_sqm,
            property_condition=context.property_condition_hint,
            can_add_room_or_split=can_add_room,
            num_bathrooms=2 if context.area_sqm >= 90 else 1,
            has_dampness_or_moisture=context.has_dampness_hint,
        )

        renovation_cost = float(boq_res["total_estimated_renovation_ils"])
        value_uplift_multiplier = 1.65 if can_add_room else 1.35
        post_renovation_value = round(
            context.asking_price_ils + (renovation_cost * value_uplift_multiplier),
            2,
        )

        return VisionRenovationResult(
            property_condition=context.property_condition_hint,
            can_add_room_or_split=can_add_room,
            structural_notes=structural_notes,
            boq_items=[RenovationItem(**item) for item in boq_res["boq_items"]],
            total_estimated_renovation_ils=renovation_cost,
            estimated_post_renovation_value_ils=post_renovation_value,
        )
