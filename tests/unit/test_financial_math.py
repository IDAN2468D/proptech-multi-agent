import pytest
from app.bll.agents.tools.financial_math import (
    calculate_israeli_purchase_tax,
    calculate_mortgage_schedule,
    compute_roi_metrics,
)


def test_calculate_mortgage_schedule_spitzer():
    schedule = calculate_mortgage_schedule(
        principal=1_000_000.0,
        annual_rate_pct=4.8,
        years=25,
        method="spitzer",
    )
    assert schedule["principal_ils"] == 1_000_000.0
    assert schedule["months"] == 300
    assert schedule["method"] == "spitzer"
    # Monthly payment on 1M at 4.8% for 25 yrs is ~5,729.97 ILS
    assert 5729.0 <= schedule["first_monthly_payment_ils"] <= 5731.0
    assert schedule["total_paid_ils"] > 1_700_000.0
    assert len(schedule["annual_summary"]) == 25
    assert schedule["annual_summary"][-1]["ending_balance_ils"] == 0.0


def test_calculate_mortgage_schedule_equal_principal():
    schedule = calculate_mortgage_schedule(
        principal=1_200_000.0,
        annual_rate_pct=5.0,
        years=20,
        method="equal_principal",
    )
    assert schedule["method"] == "equal_principal"
    assert schedule["months"] == 240
    # First month principal (5,000) + first month interest (1,200,000 * 0.05 / 12 = 5,000) = 10,000
    assert schedule["first_monthly_payment_ils"] == 10000.0
    assert schedule["average_monthly_payment_ils"] < schedule["first_monthly_payment_ils"]
    assert schedule["annual_summary"][-1]["ending_balance_ils"] == 0.0


def test_calculate_israeli_purchase_tax_single_home_exempt():
    tax = calculate_israeli_purchase_tax(property_price_ils=1_850_000.0, is_single_home=True)
    assert tax == 0.0


def test_calculate_israeli_purchase_tax_single_home_progressive():
    # 2,500,000 ILS single home:
    # 0 up to 1,978,745
    # 3.5% on (2,347,040 - 1,978,745) = 368,295 * 0.035 = 12,890.325
    # 5.0% on (2,500,000 - 2,347,040) = 152,960 * 0.05 = 7,648.00
    # Total = 20,538.325 -> 20,538.32
    tax = calculate_israeli_purchase_tax(property_price_ils=2_500_000.0, is_single_home=True)
    assert tax == pytest.approx(20538.32, abs=0.05)


def test_calculate_israeli_purchase_tax_investor_home():
    # 2,500,000 ILS investor home -> 8% flat up to 6,055,070 = 200,000 ILS
    tax = calculate_israeli_purchase_tax(property_price_ils=2_500_000.0, is_single_home=False)
    assert tax == 200_000.0


def test_compute_roi_metrics_accuracy():
    metrics = compute_roi_metrics(
        property_price_ils=2_000_000.0,
        equity_ils=1_000_000.0,
        monthly_rent_ils=7_500.0,
        annual_expenses_ils=6_000.0,
        monthly_mortgage_ils=5_200.0,
        appreciation_rate_pct=3.5,
        purchase_tax_ils=160_000.0,
    )
    # Gross rent = 90,000 -> Gross yield = 4.5%
    assert metrics["gross_yield_pct"] == 4.5
    # NOI = 90,000 - 6,000 = 84,000 -> Cap rate = 4.2%
    assert metrics["net_cap_rate_pct"] == 4.2
    # Net monthly cashflow = (84,000 - 62,400) / 12 = 1,800 ILS
    assert metrics["net_monthly_cashflow_ils"] == 1800.0
    assert metrics["cash_on_cash_return_pct"] > 0
    assert metrics["projected_10yr_irr_pct"] > 0
