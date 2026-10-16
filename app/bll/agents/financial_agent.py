from pydantic import BaseModel, Field
from app.bll.agents.tools.financial_math import (
    calculate_israeli_purchase_tax,
    calculate_mortgage_schedule,
    compute_roi_metrics,
)
from app.models.agent_outputs import FinancialMetricsResult


class FinancialAgentIsolatedContext(BaseModel):
    """Isolated minimal context for FinancialAgent (Zero-Math Hallucination policy)."""

    asking_price_ils: float = Field(..., gt=0)
    equity_ils: float = Field(..., gt=0)
    estimated_monthly_rent_ils: float = Field(..., gt=0)
    is_single_home: bool = False
    annual_interest_rate_pct: float = Field(default=4.85, gt=0)
    loan_years: int = Field(default=25, gt=0)
    annual_expenses_ils: float = Field(default=6000.0, ge=0)
    appreciation_rate_pct: float = Field(default=3.0)


class FinancialAgent:
    """
    Sub-Agent 2: Financial & Mortgage ROI Agent.
    Strictly delegates all calculations to deterministic Python tools in financial_math.py.
    """

    async def run(self, context: FinancialAgentIsolatedContext) -> FinancialMetricsResult:
        purchase_tax = calculate_israeli_purchase_tax(
            property_price_ils=context.asking_price_ils,
            is_single_home=context.is_single_home,
        )
        loan_amount = max(0.0, context.asking_price_ils - context.equity_ils)
        ltv_pct = round((loan_amount / context.asking_price_ils) * 100.0, 2)

        schedule = calculate_mortgage_schedule(
            principal=loan_amount,
            annual_rate_pct=context.annual_interest_rate_pct,
            years=context.loan_years,
            method="spitzer",
        )
        monthly_mortgage = float(schedule["first_monthly_payment_ils"])

        ending_balance_10yr = None
        for yr_entry in schedule.get("annual_summary", []):
            if int(yr_entry["year"]) == 10:
                ending_balance_10yr = float(yr_entry["ending_balance_ils"])
                break

        roi = compute_roi_metrics(
            property_price_ils=context.asking_price_ils,
            equity_ils=context.equity_ils,
            monthly_rent_ils=context.estimated_monthly_rent_ils,
            annual_expenses_ils=context.annual_expenses_ils,
            monthly_mortgage_ils=monthly_mortgage,
            appreciation_rate_pct=context.appreciation_rate_pct,
            purchase_tax_ils=purchase_tax,
            ending_loan_balance_10yr_ils=ending_balance_10yr,
        )

        return FinancialMetricsResult(
            purchase_tax_ils=purchase_tax,
            loan_amount_ils=round(loan_amount, 2),
            loan_to_value_pct=ltv_pct,
            monthly_mortgage_payment_ils=monthly_mortgage,
            net_monthly_cashflow_ils=roi["net_monthly_cashflow_ils"],
            gross_yield_pct=roi["gross_yield_pct"],
            net_cap_rate_pct=roi["net_cap_rate_pct"],
            cash_on_cash_return_pct=roi["cash_on_cash_return_pct"],
            projected_10yr_irr_pct=roi["projected_10yr_irr_pct"],
        )
