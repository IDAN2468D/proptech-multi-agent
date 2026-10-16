import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.dal.sql.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserORM(Base):
    """Registered user in PostgreSQL / SQL database."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class PropertyORM(Base):
    """Structured real estate property record submitted for analysis."""

    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    neighborhood: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    asking_price_ils: Mapped[float] = mapped_column(Float, nullable=False)
    area_sqm: Mapped[float] = mapped_column(Float, nullable=False)
    rooms: Mapped[float] = mapped_column(Float, default=4.0, nullable=False)
    floor: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    estimated_monthly_rent_ils: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_single_home: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class ComparableTransactionORM(Base):
    """Historical comparable real estate transactions in SQL."""

    __tablename__ = "comparable_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    city: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    neighborhood: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    sale_price_ils: Mapped[float] = mapped_column(Float, nullable=False)
    area_sqm: Mapped[float] = mapped_column(Float, nullable=False)
    rooms: Mapped[float] = mapped_column(Float, default=4.0, nullable=False)
    sale_date: Mapped[str] = mapped_column(String(32), nullable=False)


class AnalysisRunORM(Base):
    """Persisted multi-agent analysis run and Human-In-The-Loop state."""

    __tablename__ = "analysis_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    property_id: Mapped[str] = mapped_column(String(36), ForeignKey("properties.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        index=True,
        nullable=False,
        default="RUNNING",
    )  # RUNNING | PAUSED_FOR_APPROVAL | COMPLETED | REJECTED
    equity_ils: Mapped[float] = mapped_column(Float, nullable=False)
    asking_price_override_ils: Mapped[float | None] = mapped_column(Float, nullable=True)
    annual_interest_rate_pct: Mapped[float] = mapped_column(Float, default=4.85, nullable=False)
    loan_years: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    overall_risk_score: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    hitl_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    intermediate_state_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_report_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
