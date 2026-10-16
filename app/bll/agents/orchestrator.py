import asyncio
from typing import Any, Literal
from sqlalchemy.ext.asyncio import AsyncSession
from app.bll.agents.critic_guardrail import CriticAgentContext, CriticGuardrailAgent
from app.bll.agents.financial_agent import (
    FinancialAgent,
    FinancialAgentIsolatedContext,
)
from app.bll.agents.legal_rag_agent import (
    LegalRAGAgent,
    LegalRAGAgentIsolatedContext,
)
from app.bll.agents.macro_stress_test_agent import (
    MacroStressTestAgent,
    MacroStressTestContext,
)
from app.bll.agents.market_agent import MarketAgent, MarketAgentIsolatedContext
from app.bll.agents.negotiation_agent import (
    NegotiationAgent,
    NegotiationAgentContext,
)
from app.bll.agents.urban_renewal_gis_agent import (
    UrbanRenewalGISAgent,
    UrbanRenewalGISContext,
)
from app.bll.agents.vision_renovation_agent import (
    VisionAgentIsolatedContext,
    VisionRenovationAgent,
)
from app.dal.mongo.memory_repository import InvestorMemoryRepository
from app.models.agent_outputs import (
    CriticVerdict,
    FinancialMetricsResult,
    InvestmentExecutiveReport,
    LegalDueDiligenceResult,
    MarketAnalysisResult,
)
from app.models.agent_outputs_v2 import (
    MacroStressTestResult,
    UrbanRenewalGISResult,
    VisionRenovationResult,
)


class InvestmentOrchestrator:
    """
    Supervisor / Orchestrator (v2.0 – 9 Agents) coordinating:
      - Agent 1: MarketAgent
      - Agent 2: FinancialAgent
      - Agent 3: LegalRAGAgent
      - Agent 6: VisionRenovationAgent
      - Agent 7: UrbanRenewalGISAgent
      - Agent 8: MacroStressTestAgent
    in parallel (asyncio.gather) with strict context isolation, followed by:
      - Agent 5: CriticGuardrailAgent
      - Agent 9: NegotiationAgent
    and Human-In-The-Loop (HITL) pause/resume support.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.memory_repo = InvestorMemoryRepository()
        self.market_agent = MarketAgent(session)
        self.financial_agent = FinancialAgent()
        self.legal_agent = LegalRAGAgent()
        self.vision_agent = VisionRenovationAgent()
        self.gis_agent = UrbanRenewalGISAgent()
        self.stress_agent = MacroStressTestAgent()
        self.critic_agent = CriticGuardrailAgent()
        self.negotiation_agent = NegotiationAgent()

    def _determine_recommendation(
        self,
        market: MarketAnalysisResult,
        financials: FinancialMetricsResult,
        legal: LegalDueDiligenceResult,
        critic: CriticVerdict,
        min_target_yield_pct: float,
    ) -> Literal["STRONG_BUY", "BUY_WITH_CAUTION", "HOLD_FOR_REVIEW", "AVOID"]:
        if critic.status == "REJECTED" or critic.overall_risk_score >= 85:
            return "AVOID"
        if legal.has_blocking_liens_or_warnings or critic.status == "NEEDS_HUMAN_REVIEW":
            return "HOLD_FOR_REVIEW"
        if (
            financials.net_cap_rate_pct >= min_target_yield_pct
            and financials.net_monthly_cashflow_ils >= 0
            and market.market_deviation_pct <= 5.0
        ):
            return "STRONG_BUY"
        return "BUY_WITH_CAUTION"

    def _build_executive_summary(
        self,
        city: str,
        address: str,
        recommendation: str,
        market: MarketAnalysisResult,
        financials: FinancialMetricsResult,
        legal: LegalDueDiligenceResult,
        critic: CriticVerdict,
        vision: VisionRenovationResult | None = None,
        negotiation_target_ils: float | None = None,
        investor_notes: str = "",
    ) -> str:
        summary = (
            f"דוח השקעה מסכם (9 סוכנים) לנכס ב{address}, {city}: המלצת המערכת הינה {recommendation}. "
            f"מחיר מבוקש למ\"ר: {market.subject_price_per_sqm_ils:,.0f} ש\"ח "
            f"(סטייה של {market.market_deviation_pct:+.1f}% מממוצע השוק בעיר). "
            f"תשואת Cap Rate נטו: {financials.net_cap_rate_pct:.2f}%, "
            f"תזרים חודשי נטו לאחר משכנתא: {financials.net_monthly_cashflow_ils:,.0f} ש\"ח, "
            f"ו-IRR חזוי ל-10 שנים: {financials.projected_10yr_irr_pct:.2f}%. "
            f"ציון סיכון מבוקר: {critic.overall_risk_score}/100 (ממצאים משפטיים: {len(legal.findings)})."
        )
        if vision:
            summary += f" אומדן שיפוץ (BOQ): {vision.total_estimated_renovation_ils:,.0f} ש\"ח."
        if negotiation_target_ils:
            summary += f" מחיר יעד מומלץ לסגירה במו\"מ: {negotiation_target_ils:,.0f} ש\"ח."
        if investor_notes:
            summary += f" הערות משקיע באישור HITL: {investor_notes}"
        return summary

    async def execute_parallel_analysis(
        self,
        run_id: str,
        user_id: str,
        property_data: dict[str, Any],
        equity_ils: float,
        annual_interest_rate_pct: float = 4.85,
        loan_years: int = 25,
        annual_expenses_ils: float = 6000.0,
        appreciation_rate_pct: float = 3.0,
    ) -> dict[str, Any]:
        """
        Execute Sub-Agents 1, 2, 3, 6, 7, 8 in parallel using asyncio.gather with isolated Pydantic contexts,
        then evaluate through CriticGuardrailAgent (Agent 5) and NegotiationAgent (Agent 9).
        """
        investor_profile = await self.memory_repo.get_investor_profile(user_id)
        risk_threshold = int(investor_profile.get("max_risk_score_threshold", 70))
        min_target_yield = float(investor_profile.get("min_target_net_yield_pct", 3.2))
        investor_avail_equity = float(investor_profile.get("available_equity_ils", equity_ils))

        asking_price = float(property_data["asking_price_ils"])
        area_sqm = float(property_data["area_sqm"])
        rooms = float(property_data.get("rooms", 4.0))
        floor = int(property_data.get("floor", 1))
        city = str(property_data["city"])
        address = str(property_data["address"])
        neighborhood = str(property_data.get("neighborhood", ""))
        is_single_home = bool(
            property_data.get("is_single_home", investor_profile.get("is_single_home_buyer", False))
        )

        fallback_rent = float(property_data.get("estimated_monthly_rent_ils") or round(asking_price * 0.0032, 2))

        market_ctx = MarketAgentIsolatedContext(
            city=city,
            address=address,
            asking_price_ils=asking_price,
            area_sqm=area_sqm,
            rooms=rooms,
        )
        fin_ctx = FinancialAgentIsolatedContext(
            asking_price_ils=asking_price,
            equity_ils=equity_ils,
            estimated_monthly_rent_ils=fallback_rent,
            is_single_home=is_single_home,
            annual_interest_rate_pct=annual_interest_rate_pct,
            loan_years=loan_years,
            annual_expenses_ils=annual_expenses_ils,
            appreciation_rate_pct=appreciation_rate_pct,
        )
        legal_ctx = LegalRAGAgentIsolatedContext(
            user_id=user_id,
            property_id=str(property_data["id"]),
        )
        vision_ctx = VisionAgentIsolatedContext(
            asking_price_ils=asking_price,
            area_sqm=area_sqm,
            rooms=rooms,
            floor=floor,
        )
        gis_ctx = UrbanRenewalGISContext(
            city=city,
            address=address,
            neighborhood=neighborhood,
            area_sqm=area_sqm,
            floor=floor,
        )
        stress_ctx = MacroStressTestContext(
            asking_price_ils=asking_price,
            equity_ils=equity_ils,
            estimated_monthly_rent_ils=fallback_rent,
            annual_interest_rate_pct=annual_interest_rate_pct,
            loan_years=loan_years,
            annual_expenses_ils=annual_expenses_ils,
        )

        # Parallel execution of 6 isolated specialist sub-agents
        (
            market_res,
            fin_res,
            legal_res,
            vision_res,
            gis_res,
            stress_res,
        ) = await asyncio.gather(
            self.market_agent.run(market_ctx),
            self.financial_agent.run(fin_ctx),
            self.legal_agent.run(legal_ctx),
            self.vision_agent.run(vision_ctx),
            self.gis_agent.run(gis_ctx),
            self.stress_agent.run(stress_ctx),
        )

        # If property had no explicit rent, re-align FinancialAgent & MacroStressTestAgent with MarketAgent's rent
        if property_data.get("estimated_monthly_rent_ils") is None:
            fin_ctx.estimated_monthly_rent_ils = market_res.estimated_monthly_rent_ils
            stress_ctx.estimated_monthly_rent_ils = market_res.estimated_monthly_rent_ils
            fin_res, stress_res = await asyncio.gather(
                self.financial_agent.run(fin_ctx),
                self.stress_agent.run(stress_ctx),
            )

        # Agent 5: CriticGuardrailAgent
        critic_ctx = CriticAgentContext(
            asking_price_ils=asking_price,
            declared_area_sqm=area_sqm,
            equity_ils=equity_ils,
            is_single_home=is_single_home,
            annual_interest_rate_pct=annual_interest_rate_pct,
            loan_years=loan_years,
            annual_expenses_ils=annual_expenses_ils,
            appreciation_rate_pct=appreciation_rate_pct,
            estimated_monthly_rent_ils=fin_ctx.estimated_monthly_rent_ils,
            investor_risk_threshold=risk_threshold,
            investor_available_equity_ils=investor_avail_equity,
            market_result=market_res,
            financial_result=fin_res,
            legal_result=legal_res,
            vision_result=vision_res,
            stress_test_result=stress_res,
        )
        critic_verdict = await self.critic_agent.run(critic_ctx)

        # Agent 9: NegotiationAgent
        negotiation_res = await self.negotiation_agent.run(
            NegotiationAgentContext(
                city=city,
                address=address,
                asking_price_ils=asking_price,
                declared_area_sqm=area_sqm,
                market_result=market_res,
                legal_result=legal_res,
                vision_result=vision_res,
            )
        )

        recommendation = self._determine_recommendation(
            market=market_res,
            financials=fin_res,
            legal=legal_res,
            critic=critic_verdict,
            min_target_yield_pct=min_target_yield,
        )

        paused = critic_verdict.status == "NEEDS_HUMAN_REVIEW"
        report_status: Literal["COMPLETED", "PAUSED_FOR_APPROVAL", "REJECTED"] = (
            "PAUSED_FOR_APPROVAL"
            if paused
            else ("REJECTED" if critic_verdict.status == "REJECTED" else "COMPLETED")
        )

        report = InvestmentExecutiveReport(
            run_id=run_id,
            property_id=str(property_data["id"]),
            status=report_status,
            run_status=report_status,
            market=market_res,
            financials=fin_res,
            legal=legal_res,
            critic=critic_verdict,
            vision_renovation=vision_res,
            urban_renewal_gis=gis_res,
            macro_stress_test=stress_res,
            negotiation_playbook=negotiation_res,
            investment_recommendation=recommendation,
            executive_summary=self._build_executive_summary(
                city=city,
                address=address,
                recommendation=recommendation,
                market=market_res,
                financials=fin_res,
                legal=legal_res,
                critic=critic_verdict,
                vision=vision_res,
                negotiation_target_ils=negotiation_res.target_closing_price_ils,
            ),
        )

        await self.memory_repo.save_session_trace(
            run_id=run_id,
            trace_payload={
                "user_id": user_id,
                "property_id": str(property_data["id"]),
                "status": report_status,
                "overall_risk_score": critic_verdict.overall_risk_score,
            },
        )

        return {
            "paused_for_hitl": paused,
            "report": report,
            "intermediate_state": {
                "property_data": property_data,
                "equity_ils": equity_ils,
                "annual_interest_rate_pct": annual_interest_rate_pct,
                "loan_years": loan_years,
                "annual_expenses_ils": annual_expenses_ils,
                "appreciation_rate_pct": appreciation_rate_pct,
                "market": market_res.model_dump(),
                "financials": fin_res.model_dump(),
                "legal": legal_res.model_dump(),
                "critic": critic_verdict.model_dump(),
                "vision_renovation": vision_res.model_dump(),
                "urban_renewal_gis": gis_res.model_dump(),
                "macro_stress_test": stress_res.model_dump(),
                "negotiation_playbook": negotiation_res.model_dump(),
                "min_target_yield": min_target_yield,
            },
        }

    async def resume_after_hitl(
        self,
        run_id: str,
        user_id: str,
        intermediate_state: dict[str, Any],
        approved: bool,
        updated_asking_price_ils: float | None = None,
        updated_equity_ils: float | None = None,
        investor_notes: str = "",
    ) -> InvestmentExecutiveReport:
        """
        Resume a PAUSED_FOR_APPROVAL analysis run after Human-In-The-Loop review,
        optionally recalculating deterministic financials & stress-test if price/equity were renegotiated.
        """
        prop_data = dict(intermediate_state["property_data"])
        equity = float(updated_equity_ils or intermediate_state["equity_ils"])
        if updated_asking_price_ils is not None:
            prop_data["asking_price_ils"] = float(updated_asking_price_ils)

        market_res = MarketAnalysisResult(**intermediate_state["market"])
        legal_res = LegalDueDiligenceResult(**intermediate_state["legal"])
        vision_res = (
            VisionRenovationResult(**intermediate_state["vision_renovation"])
            if intermediate_state.get("vision_renovation")
            else None
        )
        gis_res = (
            UrbanRenewalGISResult(**intermediate_state["urban_renewal_gis"])
            if intermediate_state.get("urban_renewal_gis")
            else None
        )

        if updated_asking_price_ils is not None or updated_equity_ils is not None:
            market_res = await self.market_agent.run(
                MarketAgentIsolatedContext(
                    city=prop_data["city"],
                    address=prop_data["address"],
                    asking_price_ils=float(prop_data["asking_price_ils"]),
                    area_sqm=float(prop_data["area_sqm"]),
                    rooms=float(prop_data.get("rooms", 4.0)),
                )
            )
            est_rent = float(
                prop_data.get("estimated_monthly_rent_ils") or market_res.estimated_monthly_rent_ils
            )
            fin_res, stress_res = await asyncio.gather(
                self.financial_agent.run(
                    FinancialAgentIsolatedContext(
                        asking_price_ils=float(prop_data["asking_price_ils"]),
                        equity_ils=equity,
                        estimated_monthly_rent_ils=est_rent,
                        is_single_home=bool(prop_data.get("is_single_home", False)),
                        annual_interest_rate_pct=float(intermediate_state.get("annual_interest_rate_pct", 4.85)),
                        loan_years=int(intermediate_state.get("loan_years", 25)),
                        annual_expenses_ils=float(intermediate_state.get("annual_expenses_ils", 6000.0)),
                        appreciation_rate_pct=float(intermediate_state.get("appreciation_rate_pct", 3.0)),
                    )
                ),
                self.stress_agent.run(
                    MacroStressTestContext(
                        asking_price_ils=float(prop_data["asking_price_ils"]),
                        equity_ils=equity,
                        estimated_monthly_rent_ils=est_rent,
                        annual_interest_rate_pct=float(intermediate_state.get("annual_interest_rate_pct", 4.85)),
                        loan_years=int(intermediate_state.get("loan_years", 25)),
                        annual_expenses_ils=float(intermediate_state.get("annual_expenses_ils", 6000.0)),
                    )
                ),
            )
        else:
            fin_res = FinancialMetricsResult(**intermediate_state["financials"])
            stress_res = (
                MacroStressTestResult(**intermediate_state["macro_stress_test"])
                if intermediate_state.get("macro_stress_test")
                else None
            )

        if vision_res is None:
            vision_res = await self.vision_agent.run(
                VisionAgentIsolatedContext(
                    asking_price_ils=float(prop_data["asking_price_ils"]),
                    area_sqm=float(prop_data["area_sqm"]),
                )
            )

        negotiation_res = await self.negotiation_agent.run(
            NegotiationAgentContext(
                city=str(prop_data["city"]),
                address=str(prop_data["address"]),
                asking_price_ils=float(prop_data["asking_price_ils"]),
                declared_area_sqm=float(prop_data["area_sqm"]),
                market_result=market_res,
                legal_result=legal_res,
                vision_result=vision_res,
            )
        )

        old_critic = CriticVerdict(**intermediate_state["critic"])
        if approved:
            final_critic = CriticVerdict(
                status="APPROVED",
                overall_risk_score=old_critic.overall_risk_score,
                context_clashes_detected=old_critic.context_clashes_detected,
                math_verification_passed=old_critic.math_verification_passed,
                hitl_reason=old_critic.hitl_reason,
            )
            final_status: Literal["COMPLETED", "REJECTED"] = "COMPLETED"
            rec: Literal["STRONG_BUY", "BUY_WITH_CAUTION", "HOLD_FOR_REVIEW", "AVOID"] = (
                "BUY_WITH_CAUTION" if old_critic.overall_risk_score >= 50 else "STRONG_BUY"
            )
        else:
            final_critic = CriticVerdict(
                status="REJECTED",
                overall_risk_score=old_critic.overall_risk_score,
                context_clashes_detected=old_critic.context_clashes_detected,
                math_verification_passed=old_critic.math_verification_passed,
                hitl_reason="נדחה על ידי המשקיע בשלב אישור אנושי (HITL).",
            )
            final_status = "REJECTED"
            rec = "AVOID"

        report = InvestmentExecutiveReport(
            run_id=run_id,
            property_id=str(prop_data["id"]),
            status=final_status,
            run_status=final_status,
            market=market_res,
            financials=fin_res,
            legal=legal_res,
            critic=final_critic,
            vision_renovation=vision_res,
            urban_renewal_gis=gis_res,
            macro_stress_test=stress_res,
            negotiation_playbook=negotiation_res,
            investment_recommendation=rec,
            executive_summary=self._build_executive_summary(
                city=str(prop_data["city"]),
                address=str(prop_data["address"]),
                recommendation=rec,
                market=market_res,
                financials=fin_res,
                legal=legal_res,
                critic=final_critic,
                vision=vision_res,
                negotiation_target_ils=negotiation_res.target_closing_price_ils,
                investor_notes=investor_notes,
            ),
        )

        await self.memory_repo.append_analysis_history(
            user_id=user_id,
            summary_entry={
                "run_id": run_id,
                "property_id": str(prop_data["id"]),
                "city": str(prop_data["city"]),
                "recommendation": rec,
                "risk_score": final_critic.overall_risk_score,
            },
        )
        return report
