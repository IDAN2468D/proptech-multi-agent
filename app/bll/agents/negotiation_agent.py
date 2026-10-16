from typing import Any
from pydantic import BaseModel, Field
from app.models.agent_outputs import LegalDueDiligenceResult, MarketAnalysisResult
from app.models.agent_outputs_v2 import (
    NegotiationPlaybookResult,
    VisionRenovationResult,
)


class NegotiationAgentContext(BaseModel):
    """Context for Agent 9: AI Negotiation & Counter-Offer Strategist."""

    city: str
    address: str
    asking_price_ils: float = Field(..., gt=0)
    declared_area_sqm: float = Field(..., gt=0)
    market_result: MarketAnalysisResult
    legal_result: LegalDueDiligenceResult
    vision_result: VisionRenovationResult


class NegotiationAgent:
    """
    Sub-Agent 9: AI Negotiation & Counter-Offer Strategist.
    Synthesizes RAG legal defects, Tabu area discrepancies, market overpricing, and Vision BOQ
    renovation costs into concrete price reduction justifications, target closing price,
    and a ready-to-send Hebrew counter-offer message.
    """

    async def run(self, ctx: NegotiationAgentContext) -> NegotiationPlaybookResult:
        justifications: list[dict[str, Any]] = []
        total_deduction = 0.0

        # 1. Check Tabu area discrepancy deduction
        tabu_sqm = ctx.legal_result.registered_area_sqm
        if tabu_sqm is not None and tabu_sqm > 0 and ctx.declared_area_sqm > tabu_sqm:
            missing_sqm = ctx.declared_area_sqm - tabu_sqm
            if missing_sqm >= 2.0:
                sqm_deduction = round(
                    missing_sqm * ctx.market_result.avg_price_per_sqm_ils * 0.65,
                    -3,
                )
                justifications.append(
                    {
                        "reason": f"פער של {missing_sqm:.0f} מ\"ר בין השטח המוצג במודעה ({ctx.declared_area_sqm:.0f} מ\"ר) לשטח הרשום בנסח הטאבו ({tabu_sqm:.0f} מ\"ר)",
                        "deduction_amount_ils": float(sqm_deduction),
                        "evidence_source": "Sub-Agent 3 (Legal & Tabu RAG Agent)",
                    }
                )
                total_deduction += sqm_deduction

        # 2. Check Market Overpricing deduction
        if ctx.market_result.market_deviation_pct > 2.0:
            fair_market_value = ctx.declared_area_sqm * ctx.market_result.avg_price_per_sqm_ils
            overprice_gap = max(0.0, round((ctx.asking_price_ils - fair_market_value) * 0.75, -3))
            if overprice_gap > 0:
                justifications.append(
                    {
                        "reason": f"המחיר המבוקש גבוה ב-{ctx.market_result.market_deviation_pct:.1f}% מממוצע עסקאות ההשוואה ברחוב",
                        "deduction_amount_ils": float(overprice_gap),
                        "evidence_source": "Sub-Agent 1 (Market & Comps Agent)",
                    }
                )
                total_deduction += overprice_gap

        # 3. Check Renovation BOQ deduction
        reno_cost = ctx.vision_result.total_estimated_renovation_ils
        if reno_cost > 10_000:
            shared_reno_deduction = round(reno_cost * 0.70, -3)
            justifications.append(
                {
                    "reason": f"עלות שיפוץ והתאמות הנדסיות לפי כתב כמויות (BOQ: {reno_cost:,.0f} ש\"ח)",
                    "deduction_amount_ils": float(shared_reno_deduction),
                    "evidence_source": "Sub-Agent 6 (Vision & Renovation Estimator)",
                }
            )
            total_deduction += shared_reno_deduction

        # 4. Check Legal / Warning Note risk premium deduction
        if ctx.legal_result.has_blocking_liens_or_warnings:
            legal_deduction = round(ctx.asking_price_ils * 0.025, -3)
            justifications.append(
                {
                    "reason": "סיכון משפטי וזמן המתנה להסרת הערת אזהרה / עיקול בנסח הטאבו",
                    "deduction_amount_ils": float(legal_deduction),
                    "evidence_source": "Sub-Agent 3 (Legal & Tabu RAG Agent)",
                }
            )
            total_deduction += legal_deduction

        # Cap maximum deduction at 24% of asking price for realistic negotiation bounds
        capped_deduction = min(total_deduction, ctx.asking_price_ils * 0.24)
        if capped_deduction == 0.0:
            capped_deduction = round(ctx.asking_price_ils * 0.035, -3)
            justifications.append(
                {
                    "reason": "מרווח משא ומתן מסחרי מקובל בעסקאות יד שנייה באזור",
                    "deduction_amount_ils": float(capped_deduction),
                    "evidence_source": "Sub-Agent 9 (Negotiation Strategist)",
                }
            )

        target_closing = round(ctx.asking_price_ils - capped_deduction, -3)
        opening_offer = round(target_closing - (ctx.asking_price_ils * 0.03), -3)
        walk_away_max = round(target_closing + (capped_deduction * 0.35), -3)

        bullet_lines = "\n".join(
            f"• {j['reason']} (הפחתה מוערכת: {j['deduction_amount_ils']:,.0f} ₪)"
            for j in justifications
        )
        hebrew_msg = (
            f"שלום רב,\n"
            f"לאחר בדיקה שמאית, משפטית והנדסית מקיפה לנכס ב{ctx.address}, {ctx.city}, "
            f"אנו מעוניינים להתקדם לעסקה מהירה ובטוחה.\n"
            f"יחד עם זאת, בבדיקת המסמכים והתשריט עלו הממצאים הבאים הדורשים התאמה במחיר:\n"
            f"{bullet_lines}\n\n"
            f"בהתאם לכך, הצעת המחיר הרשמית שלנו הינה {opening_offer:,.0f} ₪, "
            f"עם נכונות לסגירה מיידית וחתימת חוזה סביב {target_closing:,.0f} ₪ בכפוף להמצאת מכתב החרגה/סילוק תקינים.\n"
            f"נשמח לתאם שיחה קצרה לקידום העסקה."
        )

        return NegotiationPlaybookResult(
            asking_price_ils=ctx.asking_price_ils,
            recommended_opening_offer_ils=opening_offer,
            target_closing_price_ils=target_closing,
            walk_away_max_price_ils=walk_away_max,
            price_reduction_justifications=justifications,
            ready_to_send_hebrew_message=hebrew_msg,
        )
