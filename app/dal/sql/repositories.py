import json
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dal.sql.orm_models import (
    AnalysisRunORM,
    ComparableTransactionORM,
    PropertyORM,
    UserORM,
)


class UserRepository:
    """Async SQL repository for UserORM."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> UserORM | None:
        stmt = select(UserORM).where(UserORM.email == email.lower().strip())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> UserORM | None:
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, email: str, full_name: str, hashed_password: str) -> UserORM:
        user = UserORM(
            email=email.lower().strip(),
            full_name=full_name.strip(),
            hashed_password=hashed_password,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user


class PropertyRepository:
    """Async SQL repository for PropertyORM."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, owner_user_id: str, data: dict[str, Any]) -> PropertyORM:
        prop = PropertyORM(
            owner_user_id=owner_user_id,
            address=data["address"],
            city=data["city"],
            neighborhood=data.get("neighborhood") or "",
            asking_price_ils=float(data["asking_price_ils"]),
            area_sqm=float(data["area_sqm"]),
            rooms=float(data.get("rooms", 4.0)),
            floor=int(data.get("floor", 1)),
            estimated_monthly_rent_ils=(
                float(data["estimated_monthly_rent_ils"])
                if data.get("estimated_monthly_rent_ils") is not None
                else None
            ),
            is_single_home=bool(data.get("is_single_home", False)),
        )
        self.session.add(prop)
        await self.session.flush()
        await self.session.refresh(prop)
        return prop

    async def get_by_id(self, property_id: str) -> PropertyORM | None:
        stmt = select(PropertyORM).where(PropertyORM.id == property_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_owner(self, owner_user_id: str) -> list[PropertyORM]:
        stmt = select(PropertyORM).where(PropertyORM.owner_user_id == owner_user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class CompsRepository:
    """Async SQL repository for ComparableTransactionORM."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_city(self, city: str, limit: int = 15) -> list[ComparableTransactionORM]:
        stmt = (
            select(ComparableTransactionORM)
            .where(ComparableTransactionORM.city == city)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def seed_comps_if_empty(self, city: str, comps_payload: list[dict[str, Any]]) -> list[ComparableTransactionORM]:
        existing = await self.list_by_city(city)
        if existing:
            return existing
        created: list[ComparableTransactionORM] = []
        for item in comps_payload:
            comp = ComparableTransactionORM(
                city=city,
                neighborhood=item.get("neighborhood", "מרכז העיר"),
                address=item["address"],
                sale_price_ils=float(item["sale_price_ils"]),
                area_sqm=float(item["area_sqm"]),
                rooms=float(item.get("rooms", 4.0)),
                sale_date=item.get("sale_date", "2026-06-15"),
            )
            self.session.add(comp)
            created.append(comp)
        await self.session.flush()
        return created


class AnalysisRunRepository:
    """Async SQL repository for AnalysisRunORM."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        user_id: str,
        property_id: str,
        equity_ils: float,
        annual_interest_rate_pct: float,
        loan_years: int,
    ) -> AnalysisRunORM:
        run = AnalysisRunORM(
            user_id=user_id,
            property_id=property_id,
            status="RUNNING",
            equity_ils=equity_ils,
            annual_interest_rate_pct=annual_interest_rate_pct,
            loan_years=loan_years,
        )
        self.session.add(run)
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def get_by_id(self, run_id: str) -> AnalysisRunORM | None:
        stmt = select(AnalysisRunORM).where(AnalysisRunORM.id == run_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save_paused_state(
        self,
        run: AnalysisRunORM,
        overall_risk_score: int,
        hitl_reason: str,
        intermediate_state: dict[str, Any],
    ) -> AnalysisRunORM:
        run.status = "PAUSED_FOR_APPROVAL"
        run.overall_risk_score = overall_risk_score
        run.hitl_reason = hitl_reason
        run.intermediate_state_json = json.dumps(intermediate_state, ensure_ascii=False)
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def save_completed_report(
        self,
        run: AnalysisRunORM,
        overall_risk_score: int,
        report_dict: dict[str, Any],
        status_override: str = "COMPLETED",
    ) -> AnalysisRunORM:
        run.status = status_override
        run.overall_risk_score = overall_risk_score
        run.final_report_json = json.dumps(report_dict, ensure_ascii=False)
        await self.session.flush()
        await self.session.refresh(run)
        return run
