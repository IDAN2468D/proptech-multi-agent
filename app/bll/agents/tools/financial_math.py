from typing import Any, Literal


def calculate_mortgage_schedule(
    principal: float,
    annual_rate_pct: float,
    years: int,
    method: Literal["spitzer", "equal_principal"] = "spitzer",
) -> dict[str, Any]:
    """
    Pure deterministic Python calculation for mortgage amortization schedule.
    Supports 'spitzer' (constant monthly payment) and 'equal_principal' (Keren Shava).
    """
    if principal < 0:
        raise ValueError("Principal cannot be negative")
    if years <= 0:
        raise ValueError("Loan term years must be positive")
    if annual_rate_pct < 0:
        raise ValueError("Annual interest rate cannot be negative")

    if principal == 0:
        return {
            "principal_ils": 0.0,
            "method": method,
            "months": years * 12,
            "first_monthly_payment_ils": 0.0,
            "average_monthly_payment_ils": 0.0,
            "total_paid_ils": 0.0,
            "total_interest_paid_ils": 0.0,
            "annual_summary": [],
        }

    months = years * 12
    monthly_rate = (annual_rate_pct / 100.0) / 12.0

    if method == "spitzer":
        if monthly_rate == 0:
            monthly_payment = principal / months
        else:
            factor = (1.0 + monthly_rate) ** months
            monthly_payment = principal * (monthly_rate * factor) / (factor - 1.0)

        balance = principal
        total_interest = 0.0
        annual_summary: list[dict[str, float]] = []
        year_interest = 0.0
        year_principal = 0.0

        for m in range(1, months + 1):
            interest_part = balance * monthly_rate
            principal_part = monthly_payment - interest_part
            balance = max(0.0, balance - principal_part)
            total_interest += interest_part
            year_interest += interest_part
            year_principal += principal_part

            if m % 12 == 0 or m == months:
                annual_summary.append(
                    {
                        "year": float((m - 1) // 12 + 1),
                        "principal_paid_ils": round(year_principal, 2),
                        "interest_paid_ils": round(year_interest, 2),
                        "ending_balance_ils": round(balance, 2),
                    }
                )
                year_interest = 0.0
                year_principal = 0.0

        total_paid = monthly_payment * months
        return {
            "principal_ils": round(principal, 2),
            "method": "spitzer",
            "months": months,
            "first_monthly_payment_ils": round(monthly_payment, 2),
            "average_monthly_payment_ils": round(monthly_payment, 2),
            "total_paid_ils": round(total_paid, 2),
            "total_interest_paid_ils": round(total_interest, 2),
            "annual_summary": annual_summary,
        }

    elif method == "equal_principal":
        monthly_principal = principal / months
        balance = principal
        total_interest = 0.0
        first_payment = 0.0
        annual_summary = []
        year_interest = 0.0
        year_principal = 0.0

        for m in range(1, months + 1):
            interest_part = balance * monthly_rate
            payment = monthly_principal + interest_part
            if m == 1:
                first_payment = payment
            balance = max(0.0, balance - monthly_principal)
            total_interest += interest_part
            year_interest += interest_part
            year_principal += monthly_principal

            if m % 12 == 0 or m == months:
                annual_summary.append(
                    {
                        "year": float((m - 1) // 12 + 1),
                        "principal_paid_ils": round(year_principal, 2),
                        "interest_paid_ils": round(year_interest, 2),
                        "ending_balance_ils": round(balance, 2),
                    }
                )
                year_interest = 0.0
                year_principal = 0.0

        total_paid = principal + total_interest
        avg_payment = total_paid / months
        return {
            "principal_ils": round(principal, 2),
            "method": "equal_principal",
            "months": months,
            "first_monthly_payment_ils": round(first_payment, 2),
            "average_monthly_payment_ils": round(avg_payment, 2),
            "total_paid_ils": round(total_paid, 2),
            "total_interest_paid_ils": round(total_interest, 2),
            "annual_summary": annual_summary,
        }

    raise ValueError(f"Unsupported mortgage calculation method: {method}")


def calculate_israeli_purchase_tax(property_price_ils: float, is_single_home: bool) -> float:
    """
    Deterministic calculation of Israeli Real Estate Purchase Tax (Mas Rechisha).
    - Single Home (Dira Yechida) progressive brackets:
      * Up to 1,978,745 ILS -> 0%
      * 1,978,745 to 2,347,040 ILS -> 3.5%
      * 2,347,040 to 6,055,070 ILS -> 5.0%
      * 6,055,070 to 20,183,565 ILS -> 8.0%
      * Above 20,183,565 ILS -> 10.0%
    - Investment / Additional Home (Dira Nosefet) brackets:
      * Up to 6,055,070 ILS -> 8.0%
      * Above 6,055,070 ILS -> 10.0%
    """
    if property_price_ils <= 0:
        raise ValueError("Property price must be positive")

    if is_single_home:
        brackets = [
            (1_978_745.0, 0.00),
            (2_347_040.0, 0.035),
            (6_055_070.0, 0.05),
            (20_183_565.0, 0.08),
            (float("inf"), 0.10),
        ]
    else:
        brackets = [
            (6_055_070.0, 0.08),
            (float("inf"), 0.10),
        ]

    tax = 0.0
    prev_limit = 0.0
    for upper_limit, rate in brackets:
        if property_price_ils > prev_limit:
            taxable_slice = min(property_price_ils, upper_limit) - prev_limit
            tax += taxable_slice * rate
            prev_limit = upper_limit
        else:
            break

    return round(tax, 2)


def _solve_irr(cashflows: list[float]) -> float:
    """Deterministic bisection solver for Internal Rate of Return (IRR) percentage."""
    if not cashflows or cashflows[0] >= 0:
        return 0.0

    low = -0.95
    high = 2.0

    def npv(rate: float) -> float:
        return sum(cf / ((1.0 + rate) ** t) for t, cf in enumerate(cashflows))

    npv_low = npv(low)
    npv_high = npv(high)
    if npv_low * npv_high > 0:
        return 0.0

    for _ in range(100):
        mid = (low + high) / 2.0
        val = npv(mid)
        if abs(val) < 1e-6:
            return round(mid * 100.0, 2)
        if npv_low * val < 0:
            high = mid
            npv_high = val
        else:
            low = mid
            npv_low = val

    return round(((low + high) / 2.0) * 100.0, 2)


def compute_roi_metrics(
    property_price_ils: float,
    equity_ils: float,
    monthly_rent_ils: float,
    annual_expenses_ils: float,
    monthly_mortgage_ils: float,
    appreciation_rate_pct: float,
    purchase_tax_ils: float = 0.0,
    ending_loan_balance_10yr_ils: float | None = None,
) -> dict[str, float]:
    """
    Pure deterministic Python ROI & Yield metrics calculator.
    Computes Gross Yield, Net Cap Rate, Net Monthly Cashflow, Cash-on-Cash Return, and 10-Yr IRR.
    """
    if property_price_ils <= 0:
        raise ValueError("Property price must be positive")
    if equity_ils <= 0:
        raise ValueError("Equity must be positive")

    annual_gross_rent = monthly_rent_ils * 12.0
    annual_noi = annual_gross_rent - annual_expenses_ils
    annual_debt_service = monthly_mortgage_ils * 12.0
    annual_net_cashflow = annual_noi - annual_debt_service
    net_monthly_cashflow = annual_net_cashflow / 12.0

    gross_yield_pct = (annual_gross_rent / property_price_ils) * 100.0
    net_cap_rate_pct = (annual_noi / property_price_ils) * 100.0

    total_cash_invested = equity_ils + purchase_tax_ils
    cash_on_cash_return_pct = (annual_net_cashflow / total_cash_invested) * 100.0

    # 10-year IRR cashflow projection
    loan_amount = max(0.0, property_price_ils - equity_ils)
    if ending_loan_balance_10yr_ils is None:
        # Approximate remaining principal after 10 years if schedule not passed
        ending_loan_balance_10yr_ils = max(0.0, loan_amount * 0.68)

    terminal_property_value = property_price_ils * ((1.0 + appreciation_rate_pct / 100.0) ** 10)
    terminal_equity_proceeds = terminal_property_value - ending_loan_balance_10yr_ils

    cashflows: list[float] = [-total_cash_invested]
    for year in range(1, 11):
        rent_y = annual_gross_rent * ((1.0 + (appreciation_rate_pct * 0.5) / 100.0) ** (year - 1))
        noi_y = rent_y - annual_expenses_ils
        cf_y = noi_y - annual_debt_service
        if year == 10:
            cf_y += terminal_equity_proceeds
        cashflows.append(cf_y)

    irr_10yr_pct = _solve_irr(cashflows)

    return {
        "net_monthly_cashflow_ils": round(net_monthly_cashflow, 2),
        "gross_yield_pct": round(gross_yield_pct, 2),
        "net_cap_rate_pct": round(net_cap_rate_pct, 2),
        "cash_on_cash_return_pct": round(cash_on_cash_return_pct, 2),
        "projected_10yr_irr_pct": round(irr_10yr_pct, 2),
    }
