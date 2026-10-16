import random
from typing import Any
from app.bll.agents.tools.financial_math import calculate_mortgage_schedule


def run_monte_carlo_stress_test(
    loan_amount_ils: float,
    base_annual_rate_pct: float,
    loan_years: int,
    base_monthly_rent_ils: float,
    annual_expenses_ils: float,
    renovation_overrun_ils: float = 0.0,
    simulations: int = 1000,
    seed: int = 42,
) -> dict[str, Any]:
    """
    Pure deterministic Python Macro Stress-Test & 1,000-iteration seeded Monte Carlo simulator.
    Evaluates:
      1. Base case monthly cashflow
      2. +1.5% BOI interest rate shock
      3. 2 months annual vacancy shock
      4. Combined worst-case (+1.5% rate + -10% rent + 20% expense spike)
      5. Probability of positive monthly cashflow across 1,000 stochastic trials
      6. Break-even maximum interest rate where net cashflow = 0
    """
    base_sched = calculate_mortgage_schedule(
        principal=loan_amount_ils,
        annual_rate_pct=base_annual_rate_pct,
        years=loan_years,
        method="spitzer",
    )
    base_mortgage = float(base_sched["first_monthly_payment_ils"])
    monthly_expenses = annual_expenses_ils / 12.0
    base_monthly_cashflow = round(base_monthly_rent_ils - monthly_expenses - base_mortgage, 2)

    # Scenario 1: +1.5% Rate Hike
    hike_sched = calculate_mortgage_schedule(
        principal=loan_amount_ils + renovation_overrun_ils,
        annual_rate_pct=base_annual_rate_pct + 1.5,
        years=loan_years,
        method="spitzer",
    )
    hike_mortgage = float(hike_sched["first_monthly_payment_ils"])
    rate_hike_monthly_cf = round(base_monthly_rent_ils - monthly_expenses - hike_mortgage, 2)

    # Scenario 2: 2 Months Vacancy (10 months rent collected out of 12)
    vacancy_annual_cf = round(
        (base_monthly_rent_ils * 10.0) - annual_expenses_ils - (base_mortgage * 12.0),
        2,
    )

    # Scenario 3: Combined Worst Case (+1.5% rate, -10% rent drop, +20% expenses)
    worst_rent = base_monthly_rent_ils * 0.90
    worst_expenses = monthly_expenses * 1.20
    combined_worst_monthly_cf = round(worst_rent - worst_expenses - hike_mortgage, 2)

    # Deterministic seeded 1,000-run Monte Carlo
    rng = random.Random(seed)
    positive_count = 0
    for _ in range(simulations):
        rate_shock = rng.gauss(0.25, 0.75)  # Mean +0.25% rate drift, std 0.75%
        rent_multiplier = rng.gauss(1.0, 0.06)  # 6% rent volatility
        vacancy_months = max(0.0, min(3.0, rng.gauss(0.6, 0.5)))

        sim_rate = max(1.0, base_annual_rate_pct + rate_shock)
        sim_sched = calculate_mortgage_schedule(
            principal=loan_amount_ils,
            annual_rate_pct=sim_rate,
            years=loan_years,
            method="spitzer",
        )
        sim_mortgage = float(sim_sched["first_monthly_payment_ils"])
        effective_monthly_rent = (
            base_monthly_rent_ils * rent_multiplier * ((12.0 - vacancy_months) / 12.0)
        )
        sim_cf = effective_monthly_rent - monthly_expenses - sim_mortgage
        if sim_cf >= 0.0:
            positive_count += 1

    prob_positive_pct = round((positive_count / simulations) * 100.0, 2)

    # Solve break-even max safe interest rate via bisection
    target_payment = max(0.0, base_monthly_rent_ils - monthly_expenses)
    if loan_amount_ils <= 0:
        max_safe_rate = 15.0
    else:
        low_r, high_r = 0.0, 20.0
        for _ in range(40):
            mid_r = (low_r + high_r) / 2.0
            pmt = float(
                calculate_mortgage_schedule(loan_amount_ils, mid_r, loan_years, "spitzer")[
                    "first_monthly_payment_ils"
                ]
            )
            if pmt <= target_payment:
                low_r = mid_r
            else:
                high_r = mid_r
        max_safe_rate = round((low_r + high_r) / 2.0, 2)

    return {
        "base_case_monthly_cashflow_ils": base_monthly_cashflow,
        "rate_hike_plus_1_5_pct_cashflow_ils": rate_hike_monthly_cf,
        "vacancy_2_months_annual_cashflow_ils": vacancy_annual_cf,
        "combined_worst_case_monthly_cashflow_ils": combined_worst_monthly_cf,
        "probability_of_positive_cashflow_pct": prob_positive_pct,
        "max_safe_interest_rate_pct": max_safe_rate,
    }
