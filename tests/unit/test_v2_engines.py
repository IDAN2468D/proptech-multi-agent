import pytest
from app.bll.agents.tools.renovation_calculator import calculate_renovation_boq_ils
from app.bll.agents.tools.stress_test_engine import run_monte_carlo_stress_test
from app.bll.agents.urban_renewal_gis_agent import (
    UrbanRenewalGISAgent,
    UrbanRenewalGISContext,
)
from app.bll.agents.vision_renovation_agent import (
    VisionAgentIsolatedContext,
    VisionRenovationAgent,
)


def test_renovation_calculator_deterministic_boq():
    res = calculate_renovation_boq_ils(
        area_sqm=100.0,
        property_condition="NEEDS_COSMETIC_RENOVATION",
        can_add_room_or_split=True,
        num_bathrooms=2,
        has_dampness_or_moisture=True,
    )
    assert len(res["boq_items"]) == 4
    # 100 * 420 (42,000) + 2 * 18,200 (36,400) + 19,000 + 12,500 = 109,900 ILS
    assert res["total_estimated_renovation_ils"] == 109_900.0


def test_monte_carlo_stress_test_engine_deterministic():
    stress = run_monte_carlo_stress_test(
        loan_amount_ils=800_000.0,
        base_annual_rate_pct=4.75,
        loan_years=25,
        base_monthly_rent_ils=6_800.0,
        annual_expenses_ils=6_000.0,
        simulations=1000,
        seed=42,
    )
    assert stress["base_case_monthly_cashflow_ils"] > stress["rate_hike_plus_1_5_pct_cashflow_ils"]
    assert stress["combined_worst_case_monthly_cashflow_ils"] < stress["base_case_monthly_cashflow_ils"]
    assert 0.0 <= stress["probability_of_positive_cashflow_pct"] <= 100.0
    assert stress["max_safe_interest_rate_pct"] > 4.75


@pytest.mark.asyncio
async def test_vision_and_urban_renewal_agents_v2():
    vision_agent = VisionRenovationAgent()
    v_res = await vision_agent.run(
        VisionAgentIsolatedContext(
            asking_price_ils=1_900_000.0,
            area_sqm=105.0,
            rooms=4.0,
            floor=3,
        )
    )
    assert v_res.can_add_room_or_split is True
    assert v_res.total_estimated_renovation_ils > 0
    assert v_res.estimated_post_renovation_value_ils > 1_900_000.0

    gis_agent = UrbanRenewalGISAgent()
    g_res = await gis_agent.run(
        UrbanRenewalGISContext(
            city="חיפה",
            address="שדרות הנשיא 45",
            area_sqm=105.0,
        )
    )
    assert g_res.tama38_or_pinui_binui_likelihood in ("HIGH", "ACTIVE_PLAN")
    assert g_res.walkability_score >= 80
