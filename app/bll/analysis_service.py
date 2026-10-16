import json
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.bll.agents.orchestrator import InvestmentOrchestrator
from app.bll.rag_pipeline.embedder_store import EmbedderStoreService
from app.bll.rag_pipeline.loader_splitter import LegalPDFLoaderSplitter
from app.bll.rag_pipeline.retriever import sanitize_chunk_text
from app.core.exceptions import (
    PermissionDeniedError,
    PropTechBaseException,
    ResourceNotFoundError,
)
from app.dal.mongo.memory_repository import InvestorMemoryRepository
from app.dal.sql.repositories import AnalysisRunRepository, PropertyRepository
from app.models.agent_outputs import InvestmentExecutiveReport
from app.models.property_schemas import (
    AnalysisRunRequest,
    DocumentUploadResponse,
    HITLApproveRequest,
    PropertyCreateRequest,
    PropertyResponse,
)


class AnalysisService:
    """
    Business Logic Layer service for property creation, PDF document RAG indexing,
    running the Multi-Agent analysis pipeline, and handling HITL approvals.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.property_repo = PropertyRepository(session)
        self.run_repo = AnalysisRunRepository(session)
        self.memory_repo = InvestorMemoryRepository()
        self.splitter = LegalPDFLoaderSplitter()
        self.embedder = EmbedderStoreService()
        self.orchestrator = InvestmentOrchestrator(session)

    async def create_property(
        self,
        user_id: str,
        payload: PropertyCreateRequest,
    ) -> PropertyResponse:
        prop = await self.property_repo.create(
            owner_user_id=user_id,
            data=payload.model_dump(),
        )
        return PropertyResponse(
            id=prop.id,
            owner_user_id=prop.owner_user_id,
            address=prop.address,
            city=prop.city,
            neighborhood=prop.neighborhood,
            asking_price_ils=prop.asking_price_ils,
            area_sqm=prop.area_sqm,
            rooms=prop.rooms,
            floor=prop.floor,
            estimated_monthly_rent_ils=prop.estimated_monthly_rent_ils,
            is_single_home=prop.is_single_home,
        )

    async def list_properties(self, user_id: str) -> list[PropertyResponse]:
        props = await self.property_repo.list_by_owner(user_id)
        return [
            PropertyResponse(
                id=p.id,
                owner_user_id=p.owner_user_id,
                address=p.address,
                city=p.city,
                neighborhood=p.neighborhood,
                asking_price_ils=p.asking_price_ils,
                area_sqm=p.area_sqm,
                rooms=p.rooms,
                floor=p.floor,
                estimated_monthly_rent_ils=p.estimated_monthly_rent_ils,
                is_single_home=p.is_single_home,
            )
            for p in props
        ]

    async def upload_and_index_document(
        self,
        user_id: str,
        property_id: str,
        filename: str,
        file_bytes: bytes,
    ) -> DocumentUploadResponse:
        prop = await self.property_repo.get_by_id(property_id)
        if not prop:
            raise ResourceNotFoundError("Property", property_id)
        if prop.owner_user_id != user_id:
            raise PermissionDeniedError()

        chunks, pages_count = self.splitter.split_pages_into_chunks(
            file_bytes=file_bytes,
            filename=filename,
        )
        sanitized_warnings: list[str] = []
        for ch in chunks:
            _, alerts = sanitize_chunk_text(ch.text)
            sanitized_warnings.extend(alerts)

        indexed_count = await self.embedder.index_property_chunks(
            user_id=user_id,
            property_id=property_id,
            chunks=chunks,
        )
        return DocumentUploadResponse(
            property_id=property_id,
            filename=filename,
            chunks_indexed=indexed_count,
            pages_extracted=pages_count,
            sanitized_warnings=sanitized_warnings,
        )

    async def run_investment_analysis(
        self,
        user_id: str,
        payload: AnalysisRunRequest,
    ) -> tuple[bool, InvestmentExecutiveReport]:
        """
        Execute multi-agent analysis. Returns (paused_for_hitl, InvestmentExecutiveReport).
        """
        prop = await self.property_repo.get_by_id(payload.property_id)
        if not prop:
            raise ResourceNotFoundError("Property", payload.property_id)
        if prop.owner_user_id != user_id:
            raise PermissionDeniedError()

        investor_profile = await self.memory_repo.get_investor_profile(user_id)
        equity_ils = float(payload.equity_ils or investor_profile.get("available_equity_ils", 800000.0))

        run_record = await self.run_repo.create(
            user_id=user_id,
            property_id=prop.id,
            equity_ils=equity_ils,
            annual_interest_rate_pct=payload.annual_interest_rate_pct,
            loan_years=payload.loan_years,
        )

        property_dict: dict[str, Any] = {
            "id": prop.id,
            "address": prop.address,
            "city": prop.city,
            "neighborhood": prop.neighborhood,
            "asking_price_ils": prop.asking_price_ils,
            "area_sqm": prop.area_sqm,
            "rooms": prop.rooms,
            "floor": prop.floor,
            "estimated_monthly_rent_ils": prop.estimated_monthly_rent_ils,
            "is_single_home": prop.is_single_home,
        }

        outcome = await self.orchestrator.execute_parallel_analysis(
            run_id=run_record.id,
            user_id=user_id,
            property_data=property_dict,
            equity_ils=equity_ils,
            annual_interest_rate_pct=payload.annual_interest_rate_pct,
            loan_years=payload.loan_years,
            annual_expenses_ils=payload.annual_expenses_ils,
            appreciation_rate_pct=payload.appreciation_rate_pct,
        )

        report: InvestmentExecutiveReport = outcome["report"]
        paused: bool = outcome["paused_for_hitl"]

        if paused:
            await self.run_repo.save_paused_state(
                run=run_record,
                overall_risk_score=report.critic.overall_risk_score,
                hitl_reason=report.critic.hitl_reason or "נדרש אישור אנושי (HITL)",
                intermediate_state=outcome["intermediate_state"],
            )
            await self.run_repo.save_completed_report(
                run=run_record,
                overall_risk_score=report.critic.overall_risk_score,
                report_dict=report.model_dump(),
                status_override="PAUSED_FOR_APPROVAL",
            )
        else:
            await self.run_repo.save_completed_report(
                run=run_record,
                overall_risk_score=report.critic.overall_risk_score,
                report_dict=report.model_dump(),
                status_override=report.status,
            )
            await self.memory_repo.append_analysis_history(
                user_id=user_id,
                summary_entry={
                    "run_id": run_record.id,
                    "property_id": prop.id,
                    "city": prop.city,
                    "recommendation": report.investment_recommendation,
                    "risk_score": report.critic.overall_risk_score,
                },
            )

        return paused, report

    async def approve_hitl_run(
        self,
        user_id: str,
        run_id: str,
        payload: HITLApproveRequest,
    ) -> InvestmentExecutiveReport:
        run_record = await self.run_repo.get_by_id(run_id)
        if not run_record:
            raise ResourceNotFoundError("AnalysisRun", run_id)
        if run_record.user_id != user_id:
            raise PermissionDeniedError()
        if run_record.status != "PAUSED_FOR_APPROVAL":
            raise PropTechBaseException(
                message=f"AnalysisRun '{run_id}' is in status '{run_record.status}' and is not awaiting HITL approval.",
                error_code="INVALID_HITL_STATE",
                status_code=400,
            )

        intermediate = json.loads(run_record.intermediate_state_json or "{}")
        report = await self.orchestrator.resume_after_hitl(
            run_id=run_record.id,
            user_id=user_id,
            intermediate_state=intermediate,
            approved=payload.approved,
            updated_asking_price_ils=payload.updated_asking_price_ils,
            updated_equity_ils=payload.updated_equity_ils,
            investor_notes=payload.investor_notes,
        )

        await self.run_repo.save_completed_report(
            run=run_record,
            overall_risk_score=report.critic.overall_risk_score,
            report_dict=report.model_dump(),
            status_override=report.status,
        )
        return report

    async def get_analysis_run(
        self,
        user_id: str,
        run_id: str,
    ) -> InvestmentExecutiveReport:
        run_record = await self.run_repo.get_by_id(run_id)
        if not run_record:
            raise ResourceNotFoundError("AnalysisRun", run_id)
        if run_record.user_id != user_id:
            raise PermissionDeniedError()
        if not run_record.final_report_json:
            raise PropTechBaseException(
                message="Analysis report is not yet available.",
                error_code="REPORT_NOT_READY",
                status_code=404,
            )
        data = json.loads(run_record.final_report_json)
        return InvestmentExecutiveReport(**data)


    async def analyze_property_vision(
        self,
        user_id: str,
        property_id: str,
        property_condition_hint: str = "NEEDS_COSMETIC_RENOVATION",
        has_dampness_hint: bool = False,
    ) -> dict[str, Any]:
        """Run Agent 6 (Vision & Renovation Estimator) on a property."""
        from app.bll.agents.vision_renovation_agent import (
            VisionAgentIsolatedContext,
            VisionRenovationAgent,
        )

        prop = await self.property_repo.get_by_id(property_id)
        if not prop:
            raise ResourceNotFoundError("Property", property_id)
        if prop.owner_user_id != user_id:
            raise PermissionDeniedError()

        valid_cond = (
            property_condition_hint
            if property_condition_hint
            in ("NEW", "GOOD", "NEEDS_COSMETIC_RENOVATION", "NEEDS_FULL_RENOVATION")
            else "NEEDS_COSMETIC_RENOVATION"
        )
        agent = VisionRenovationAgent()
        result = await agent.run(
            VisionAgentIsolatedContext(
                asking_price_ils=prop.asking_price_ils,
                area_sqm=prop.area_sqm,
                rooms=prop.rooms,
                floor=prop.floor,
                property_condition_hint=valid_cond,  # type: ignore[arg-type]
                has_dampness_hint=has_dampness_hint,
            )
        )
        return result.model_dump()

    async def run_interactive_stress_test(
        self,
        user_id: str,
        run_id: str,
        interest_rate_pct: float,
        monthly_rent_ils: float,
        renovation_overrun_ils: float = 0.0,
        equity_override_ils: float | None = None,
    ) -> dict[str, Any]:
        """Run interactive What-If Stress-Test & Monte Carlo simulation on an analysis run."""
        from app.bll.agents.macro_stress_test_agent import (
            MacroStressTestAgent,
            MacroStressTestContext,
        )

        run_record = await self.run_repo.get_by_id(run_id)
        if not run_record:
            raise ResourceNotFoundError("AnalysisRun", run_id)
        if run_record.user_id != user_id:
            raise PermissionDeniedError()

        prop = await self.property_repo.get_by_id(run_record.property_id)
        asking_price = prop.asking_price_ils if prop else 2_000_000.0
        equity = float(equity_override_ils or run_record.equity_ils)

        agent = MacroStressTestAgent()
        res = await agent.run(
            MacroStressTestContext(
                asking_price_ils=asking_price,
                equity_ils=equity,
                estimated_monthly_rent_ils=monthly_rent_ils,
                annual_interest_rate_pct=interest_rate_pct,
                loan_years=run_record.loan_years,
                renovation_overrun_ils=renovation_overrun_ils,
            )
        )
        return res.model_dump()

    async def share_deal_package(
        self,
        user_id: str,
        run_id: str,
        webhook_channel: str = "#proptech-deals",
    ) -> dict[str, Any]:
        """Dispatch deal report & .ics calendar invite via Deal-Room Comms MCP."""
        from mcp_servers.deal_room_comms_mcp import mcp_generate_deal_share_package

        report = await self.get_analysis_run(user_id=user_id, run_id=run_id)
        prop = await self.property_repo.get_by_id(report.property_id)
        address_label = f"{prop.address}, {prop.city}" if prop else report.property_id
        target_price = (
            report.negotiation_playbook.target_closing_price_ils
            if report.negotiation_playbook
            else (prop.asking_price_ils if prop else 1_800_000.0)
        )
        return mcp_generate_deal_share_package(
            run_id=run_id,
            property_address=address_label,
            recommendation=report.investment_recommendation,
            target_closing_price_ils=target_price,
            webhook_channel=webhook_channel,
        )
