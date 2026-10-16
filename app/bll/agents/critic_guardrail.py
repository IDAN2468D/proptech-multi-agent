from typing import Optional
from pydantic import BaseModel
from app.bll.agents.tools.financial_math import (
    calculate_israeli_purchase_tax,
    calculate_mortgage_schedule,
    compute_roi_metrics,
)
from app.models.agent_outputs import (
    CriticVerdict,
    FinancialMetricsResult,
    LegalDueDiligenceResult,
    MarketAnalysisResult,
)
from app.models.agent_outputs_v2 import (
    MacroStressTestResult,
    VisionRenovationResult,
)


class CriticAgentContext(BaseModel):
    """Structured context passed to CriticGuardrailAgent for cross-verification (v1 + v2)."""

    asking_price_ils: float
    declared_area_sqm: float
    equity_ils: float
    is_single_home: bool
    annual_interest_rate_pct: float = 4.85
    loan_years: int = 25
    annual_expenses_ils: float = 6000.0
    appreciation_rate_pct: float = 3.0
    estimated_monthly_rent_ils: float
    investor_risk_threshold: int = 70
    investor_available_equity_ils: Optional[float] = None
    market_result: MarketAnalysisResult
    financial_result: FinancialMetricsResult
    legal_result: LegalDueDiligenceResult
    vision_result: Optional[VisionRenovationResult] = None
    stress_test_result: Optional[MacroStressTestResult] = None


class CriticGuardrailAgent:
    """
    Sub-Agent 5: Risk Critic & Guardrails Agent (v2.0).
    Enforces Zero-Math Hallucination by deterministically verifying FinancialMetricsResult,
    detects Context Clashes (e.g., listing sqm vs. Tabu registered sqm, renovation budget overrun),
    evaluates Macro Stress-Test solvency, computes overall risk score (1-100),
    and triggers Human-In-The-Loop (HITL) when thresholds are breached.
    """

    def verify_financial_math(self, ctx: CriticAgentContext) -> tuple[bool, list[str]]:
        """Re-calculate financial metrics deterministically and assert exact match."""
        mismatches: list[str] = []

        expected_tax = calculate_israeli_purchase_tax(
            property_price_ils=ctx.asking_price_ils,
            is_single_home=ctx.is_single_home,
        )
        if abs(ctx.financial_result.purchase_tax_ils - expected_tax) > 0.5:
            mismatches.append(
                f"Purchase tax mismatch: reported {ctx.financial_result.purchase_tax_ils} vs deterministic {expected_tax}"
            )

        expected_loan = max(0.0, ctx.asking_price_ils - ctx.equity_ils)
        schedule = calculate_mortgage_schedule(
            principal=expected_loan,
            annual_rate_pct=ctx.annual_interest_rate_pct,
            years=ctx.loan_years,
            method="spitzer",
        )
        expected_mortgage = float(schedule["first_monthly_payment_ils"])
        if abs(ctx.financial_result.monthly_mortgage_payment_ils - expected_mortgage) > 0.5:
            mismatches.append(
                f"Monthly mortgage mismatch: reported {ctx.financial_result.monthly_mortgage_payment_ils} vs deterministic {expected_mortgage}"
            )

        ending_10yr = None
        for yr_entry in schedule.get("annual_summary", []):
            if int(yr_entry["year"]) == 10:
                ending_10yr = float(yr_entry["ending_balance_ils"])
                break

        expected_roi = compute_roi_metrics(
            property_price_ils=ctx.asking_price_ils,
            equity_ils=ctx.equity_ils,
            monthly_rent_ils=ctx.estimated_monthly_rent_ils,
            annual_expenses_ils=ctx.annual_expenses_ils,
            monthly_mortgage_ils=expected_mortgage,
            appreciation_rate_pct=ctx.appreciation_rate_pct,
            purchase_tax_ils=expected_tax,
            ending_loan_balance_10yr_ils=ending_10yr,
        )

        if abs(ctx.financial_result.gross_yield_pct - expected_roi["gross_yield_pct"]) > 0.05:
            mismatches.append(
                f"Gross yield mismatch: reported {ctx.financial_result.gross_yield_pct}% vs deterministic {expected_roi['gross_yield_pct']}%"
            )

        if abs(ctx.financial_result.net_cap_rate_pct - expected_roi["net_cap_rate_pct"]) > 0.05:
            mismatches.append(
                f"Net Cap Rate mismatch: reported {ctx.financial_result.net_cap_rate_pct}% vs deterministic {expected_roi['net_cap_rate_pct']}%"
            )

        if abs(ctx.financial_result.net_monthly_cashflow_ils - expected_roi["net_monthly_cashflow_ils"]) > 1.0:
            mismatches.append(
                f"Net monthly cashflow mismatch: reported {ctx.financial_result.net_monthly_cashflow_ils} vs deterministic {expected_roi['net_monthly_cashflow_ils']}"
            )

        return (len(mismatches) == 0), mismatches

    async def run(self, ctx: CriticAgentContext) -> CriticVerdict:
        math_ok, math_mismatches = self.verify_financial_math(ctx)
        clashes: list[str] = []
        risk_score = 15  # Baseline low risk

        if not math_ok:
            clashes.extend(math_mismatches)
            risk_score += 65

        # Check Context Clash: Declared listing area vs. Tabu registered area
        tabu_area = ctx.legal_result.registered_area_sqm
        if tabu_area is not None and tabu_area > 0:
            area_diff_pct = abs(ctx.declared_area_sqm - tabu_area) / tabu_area * 100.0
            if area_diff_pct > 5.0:
                clashes.append(
                    f"Context Clash (Area Discrepancy): שטח המודעה ({ctx.declared_area_sqm} מ\"ר) סוטה ב-{area_diff_pct:.1f}% מהשטח הרשום בנסח הטאבו ({tabu_area} מ\"ר)."
                )
                risk_score += 35

        # Market deviation risk
        if ctx.market_result.market_deviation_pct > 15.0:
            clashes.append(
                f"Context Clash (Overpricing): המחיר המבוקש למ\"ר גבוה ב-{ctx.market_result.market_deviation_pct:.1f}% מממוצע העסקאות באזור."
            )
            risk_score += 20

        # v2.0: Check Vision Renovation cost vs Investor Available Equity
        if ctx.vision_result and ctx.investor_available_equity_ils:
            total_cash_required = (
                ctx.equity_ils
                + ctx.financial_result.purchase_tax_ils
                + ctx.vision_result.total_estimated_renovation_ils
            )
            if total_cash_required > ctx.investor_available_equity_ils * 1.15:
                clashes.append(
                    f"Context Clash (Equity + Renovation Overrun): סך המזומן הנדרש כולל מס רכישה ושיפוץ ({total_cash_required:,.0f} ש\"ח) חורג מההון הזמין בפרופיל המשקיע ({ctx.investor_available_equity_ils:,.0f} ש\"ח)."
                )
                risk_score += 15

        # v2.0: Check Macro Stress-Test severe insolvency
        if ctx.stress_test_result:
            if ctx.stress_test_result.combined_worst_case_monthly_cashflow_ils < -4500.0:
                risk_score += 10

        # Legal findings risk scoring
        for finding in ctx.legal_result.findings:
            if finding.severity == "CRITICAL":
                risk_score += 40
            elif finding.severity == "HIGH":
                risk_score += 25
            elif finding.severity == "MEDIUM":
                risk_score += 10

        # Negative monthly cashflow risk
        if ctx.financial_result.net_monthly_cashflow_ils < 0:
            risk_score += 25

        # High LTV leverage risk
        if ctx.financial_result.loan_to_value_pct > 75.0:
            risk_score += 20

        overall_risk_score = max(1, min(100, risk_score))

        # Determine status & HITL triggers per SPEC 2.4
        hitl_reasons: list[str] = []
        threshold = min(70, ctx.investor_risk_threshold)

        if not math_ok:
            return CriticVerdict(
                status="REJECTED",
                overall_risk_score=overall_risk_score,
                context_clashes_detected=clashes,
                math_verification_passed=False,
                hitl_reason="כשל באימות מתמטי דטרמיניסטי (Zero-Math Hallucination Guardrail): " + "; ".join(math_mismatches),
            )

        if overall_risk_score >= threshold:
            hitl_reasons.append(f"ציון הסיכון הכולל ({overall_risk_score}/100) חוצה את סף הסיכון המוגדר ({threshold}).")
        if ctx.legal_result.has_blocking_liens_or_warnings:
            hitl_reasons.append("זוהו הערות אזהרה, שעבודים או עיקולים חוסמים במסמכי הנכס.")
        if ctx.financial_result.net_monthly_cashflow_ils < 0:
            hitl_reasons.append(
                f"תזרים מזומנים חודשי נטו שלילי ({ctx.financial_result.net_monthly_cashflow_ils} ש\"ח)."
            )
        if clashes:
            hitl_reasons.append("זוהו סתירות נתונים (Context Clash) בין המודעה למסמכים המשפטיים/השוק.")

        if hitl_reasons:
            return CriticVerdict(
                status="NEEDS_HUMAN_REVIEW",
                overall_risk_score=overall_risk_score,
                context_clashes_detected=clashes,
                math_verification_passed=True,
                hitl_reason=" | ".join(hitl_reasons),
            )

        return CriticVerdict(
            status="APPROVED",
            overall_risk_score=overall_risk_score,
            context_clashes_detected=clashes,
            math_verification_passed=True,
            hitl_reason=None,
        )
