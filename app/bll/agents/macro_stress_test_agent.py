from pydantic import BaseModel, Field
from app.bll.agents.tools.stress_test_engine import run_monte_carlo_stress_test
from app.models.agent_outputs_v2 import MacroStressTestResult


class MacroStressTestContext(BaseModel):
    """Isolated minimal context for Agent 8: Macro Stress-Test & Monte Carlo Agent."""

    asking_price_ils: float = Field(..., gt=0)
    equity_ils: float = Field(..., gt=0)
    estimated_monthly_rent_ils: float = Field(..., gt=0)
    annual_interest_rate_pct: float = 4.85
    loan_years: int = 25
    annual_expenses_ils: float = 6000.0
    renovation_overrun_ils: float = 0.0


class MacroStressTestAgent:
    """
    Sub-Agent 8: Macro Stress-Test & Monte Carlo Agent.
    Runs deterministic 1,000-iteration Monte Carlo simulations and interest/vacancy shock scenarios.
    """

    async def run(self, context: MacroStressTestContext) -> MacroStressTestResult:
        loan_amount = max(0.0, context.asking_price_ils - context.equity_ils)
        res = run_monte_carlo_stress_test(
            loan_amount_ils=loan_amount,
            base_annual_rate_pct=context.annual_interest_rate_pct,
            loan_years=context.loan_years,
            base_monthly_rent_ils=context.estimated_monthly_rent_ils,
            annual_expenses_ils=context.annual_expenses_ils,
            renovation_overrun_ils=context.renovation_overrun_ils,
            simulations=1000,
            seed=42,
        )
        return MacroStressTestResult(**res)
