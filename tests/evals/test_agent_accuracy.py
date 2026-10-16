import pytest
from app.bll.agents.critic_guardrail import CriticAgentContext, CriticGuardrailAgent
from app.models.agent_outputs import (
    FinancialMetricsResult,
    LegalDueDiligenceResult,
    LegalFinding,
    MarketAnalysisResult,
)
from mcp_servers.proptech_mcp_server import (
    mcp_calculate_mortgage,
    mcp_calculate_purchase_tax,
    mcp_compute_property_roi,
    mcp_query_city_comps,
)


@pytest.mark.asyncio
async def test_eval_critic_blocks_hallucinated_financial_math():
    """
    Agent Eval 1: Verify that CriticGuardrailAgent deterministically catches and blocks
    any hallucinated or tampered financial metric (Zero-Math Hallucination Guardrail).
    """
    market = MarketAnalysisResult(
        avg_price_per_sqm_ils=19500.0,
        subject_price_per_sqm_ils=19000.0,
        market_deviation_pct=-2.56,
        estimated_monthly_rent_ils=6500.0,
        comparable_transactions_count=5,
        neighborhood_highlights=["תשואה גבוהה"],
    )

    # Inject a hallucinated FinancialMetricsResult (claims 9.9% net cap rate and 500 ILS mortgage on 1.5M loan)
    hallucinated_financials = FinancialMetricsResult(
        purchase_tax_ils=0.0,  # Should be 8% = 160,000 ILS for non-single home
        loan_amount_ils=1_200_000.0,
        loan_to_value_pct=60.0,
        monthly_mortgage_payment_ils=500.0,  # Hallucinated low mortgage payment!
        net_monthly_cashflow_ils=6000.0,
        gross_yield_pct=9.9,  # Hallucinated yield!
        net_cap_rate_pct=9.5,
        cash_on_cash_return_pct=15.0,
        projected_10yr_irr_pct=22.0,
    )

    legal = LegalDueDiligenceResult(
        findings=[
            LegalFinding(
                category="CLEAN_TITLE_CHECK",
                severity="LOW",
                description="נסח טאבו תקין.",
                source_document="tabu.pdf",
                page_number=1,
                exact_quote="שטח הדירה הרשום בטאבו: 100 מ\"ר",
            )
        ],
        registered_area_sqm=100.0,
        has_blocking_liens_or_warnings=False,
    )

    critic = CriticGuardrailAgent()
    verdict = await critic.run(
        CriticAgentContext(
            asking_price_ils=2_000_000.0,
            declared_area_sqm=100.0,
            equity_ils=800_000.0,
            is_single_home=False,
            annual_interest_rate_pct=4.85,
            loan_years=25,
            annual_expenses_ils=6_000.0,
            appreciation_rate_pct=3.0,
            estimated_monthly_rent_ils=6_500.0,
            market_result=market,
            financial_result=hallucinated_financials,
            legal_result=legal,
        )
    )

    assert verdict.math_verification_passed is False
    assert verdict.status == "REJECTED"
    assert verdict.hitl_reason is not None
    assert "Zero-Math Hallucination Guardrail" in verdict.hitl_reason
    assert len(verdict.context_clashes_detected) >= 3


@pytest.mark.asyncio
async def test_eval_mcp_server_tools_accuracy():
    """Agent Eval 2: Verify Custom PropTech MCP Server tools return accurate deterministic results."""
    mortgage_res = mcp_calculate_mortgage(
        principal_ils=900_000.0,
        annual_rate_pct=4.5,
        years=20,
        method="spitzer",
    )
    assert mortgage_res["principal_ils"] == 900_000.0
    assert mortgage_res["first_monthly_payment_ils"] > 5000.0

    tax_res = mcp_calculate_purchase_tax(
        property_price_ils=3_000_000.0,
        is_single_home=False,
    )
    assert tax_res["purchase_tax_ils"] == 240_000.0
    assert tax_res["effective_tax_rate_pct"] == 8.0

    roi_res = mcp_compute_property_roi(
        property_price_ils=2_000_000.0,
        equity_ils=1_000_000.0,
        monthly_rent_ils=7_000.0,
    )
    assert roi_res["gross_yield_pct"] == 4.2

    comps_res = await mcp_query_city_comps(city="תל אביב", area_sqm=85.0)
    assert comps_res["city"] == "תל אביב"
    assert comps_res["avg_price_per_sqm_ils"] > 40_000.0
