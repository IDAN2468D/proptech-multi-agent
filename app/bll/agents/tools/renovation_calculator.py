from typing import Any, Literal

ISRAELI_RENOVATION_PRICELIST_ILS: dict[str, float] = {
    "cosmetic_paint_and_plaster_per_sqm": 420.0,
    "full_flooring_porcelain_per_sqm": 680.0,
    "plumbing_and_bathroom_full_unit": 28_000.0,
    "kitchen_cabinetry_and_countertop_unit": 42_000.0,
    "electrical_three_phase_upgrade_unit": 16_500.0,
    "gypsum_room_addition_partition_unit": 19_000.0,
    "moisture_and_sealing_treatment_unit": 12_500.0,
}


def calculate_renovation_boq_ils(
    area_sqm: float,
    property_condition: Literal[
        "NEW",
        "GOOD",
        "NEEDS_COSMETIC_RENOVATION",
        "NEEDS_FULL_RENOVATION",
    ] = "NEEDS_COSMETIC_RENOVATION",
    can_add_room_or_split: bool = True,
    num_bathrooms: int = 1,
    has_dampness_or_moisture: bool = False,
) -> dict[str, Any]:
    """
    Pure deterministic Python calculator for Israeli Renovation Bill of Quantities (BOQ) in ILS.
    Zero-Math Hallucination compliant.
    """
    if area_sqm <= 0:
        raise ValueError("area_sqm must be positive")

    boq_items: list[dict[str, Any]] = []

    if property_condition == "NEW":
        boq_items.append(
            {
                "work_category": "בדיקת בדק בית והתאמות קלות לדירה חדשה",
                "area_or_units": 1.0,
                "unit_cost_ils": 4500.0,
                "total_cost_ils": 4500.0,
            }
        )
    elif property_condition == "GOOD":
        paint_cost = round(area_sqm * 280.0, 2)
        boq_items.append(
            {
                "work_category": "צביעה אקרילית, תיקוני שפכטל ורענון כללי",
                "area_or_units": round(area_sqm, 1),
                "unit_cost_ils": 280.0,
                "total_cost_ils": paint_cost,
            }
        )
    elif property_condition == "NEEDS_COSMETIC_RENOVATION":
        paint_cost = round(
            area_sqm * ISRAELI_RENOVATION_PRICELIST_ILS["cosmetic_paint_and_plaster_per_sqm"],
            2,
        )
        boq_items.append(
            {
                "work_category": "שפכטל אמריקאי, צביעה והחלפת דלתות פנים",
                "area_or_units": round(area_sqm, 1),
                "unit_cost_ils": ISRAELI_RENOVATION_PRICELIST_ILS["cosmetic_paint_and_plaster_per_sqm"],
                "total_cost_ils": paint_cost,
            }
        )
        bath_cost = round(
            max(1, num_bathrooms) * (ISRAELI_RENOVATION_PRICELIST_ILS["plumbing_and_bathroom_full_unit"] * 0.65),
            2,
        )
        boq_items.append(
            {
                "work_category": "שדרוג חדרי רחצה וכלים סניטריים",
                "area_or_units": float(max(1, num_bathrooms)),
                "unit_cost_ils": round(
                    ISRAELI_RENOVATION_PRICELIST_ILS["plumbing_and_bathroom_full_unit"] * 0.65,
                    2,
                ),
                "total_cost_ils": bath_cost,
            }
        )
    else:  # NEEDS_FULL_RENOVATION
        floor_cost = round(
            area_sqm * ISRAELI_RENOVATION_PRICELIST_ILS["full_flooring_porcelain_per_sqm"],
            2,
        )
        boq_items.append(
            {
                "work_category": "ריצוף גרניט פורצלן 80x80 כולל פירוק והדבקה",
                "area_or_units": round(area_sqm, 1),
                "unit_cost_ils": ISRAELI_RENOVATION_PRICELIST_ILS["full_flooring_porcelain_per_sqm"],
                "total_cost_ils": floor_cost,
            }
        )
        paint_cost = round(
            area_sqm * ISRAELI_RENOVATION_PRICELIST_ILS["cosmetic_paint_and_plaster_per_sqm"],
            2,
        )
        boq_items.append(
            {
                "work_category": "טיח, שפכטל, צביעה והחלפת נגרות פנים",
                "area_or_units": round(area_sqm, 1),
                "unit_cost_ils": ISRAELI_RENOVATION_PRICELIST_ILS["cosmetic_paint_and_plaster_per_sqm"],
                "total_cost_ils": paint_cost,
            }
        )
        bath_total = round(
            max(1, num_bathrooms) * ISRAELI_RENOVATION_PRICELIST_ILS["plumbing_and_bathroom_full_unit"],
            2,
        )
        boq_items.append(
            {
                "work_category": "החלפת צנרת SP מלאה ושיפוץ קומפלט לחדרי רחצה",
                "area_or_units": float(max(1, num_bathrooms)),
                "unit_cost_ils": ISRAELI_RENOVATION_PRICELIST_ILS["plumbing_and_bathroom_full_unit"],
                "total_cost_ils": bath_total,
            }
        )
        boq_items.append(
            {
                "work_category": "חידוש מטבח קומפלט כולל שיש אבן קיסר",
                "area_or_units": 1.0,
                "unit_cost_ils": ISRAELI_RENOVATION_PRICELIST_ILS["kitchen_cabinetry_and_countertop_unit"],
                "total_cost_ils": ISRAELI_RENOVATION_PRICELIST_ILS["kitchen_cabinetry_and_countertop_unit"],
            }
        )
        boq_items.append(
            {
                "work_category": "שדרוג לוח חשמל תלת-פאזי ונקודות תקשורת",
                "area_or_units": 1.0,
                "unit_cost_ils": ISRAELI_RENOVATION_PRICELIST_ILS["electrical_three_phase_upgrade_unit"],
                "total_cost_ils": ISRAELI_RENOVATION_PRICELIST_ILS["electrical_three_phase_upgrade_unit"],
            }
        )

    if can_add_room_or_split:
        boq_items.append(
            {
                "work_category": "בניית מחיצות גבס אקוסטי להוספת חדר עבודה/שינה מניב",
                "area_or_units": 1.0,
                "unit_cost_ils": ISRAELI_RENOVATION_PRICELIST_ILS["gypsum_room_addition_partition_unit"],
                "total_cost_ils": ISRAELI_RENOVATION_PRICELIST_ILS["gypsum_room_addition_partition_unit"],
            }
        )

    if has_dampness_or_moisture:
        boq_items.append(
            {
                "work_category": "טיפול איטום וייבוש מוקדי רטיבות פעילים",
                "area_or_units": 1.0,
                "unit_cost_ils": ISRAELI_RENOVATION_PRICELIST_ILS["moisture_and_sealing_treatment_unit"],
                "total_cost_ils": ISRAELI_RENOVATION_PRICELIST_ILS["moisture_and_sealing_treatment_unit"],
            }
        )

    total_renovation_ils = round(sum(item["total_cost_ils"] for item in boq_items), 2)
    return {
        "boq_items": boq_items,
        "total_estimated_renovation_ils": total_renovation_ils,
    }
