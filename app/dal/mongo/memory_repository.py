from datetime import datetime, timezone
from typing import Any
from app.dal.mongo.client import get_mongo_db


class InvestorMemoryRepository:
    """Manages Long-Term Investor Memory and Short-Term Session Memory in MongoDB."""

    INVESTOR_COLLECTION = "investor_long_term_memory"
    SESSION_COLLECTION = "agent_short_term_memory"

    def __init__(self) -> None:
        self.db = get_mongo_db()
        self.investor_col = self.db[self.INVESTOR_COLLECTION]
        self.session_col = self.db[self.SESSION_COLLECTION]

    async def get_investor_profile(self, user_id: str) -> dict[str, Any]:
        doc = await self.investor_col.find_one({"user_id": user_id})
        if not doc:
            default_profile: dict[str, Any] = {
                "user_id": user_id,
                "available_equity_ils": 800000.0,
                "risk_tolerance": "MODERATE",
                "max_risk_score_threshold": 70,
                "min_target_net_yield_pct": 3.2,
                "preferred_cities": ["תל אביב", "חיפה", "רמת גן", "באר שבע"],
                "is_single_home_buyer": False,
                "analysis_history": [],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            await self.investor_col.insert_one(dict(default_profile))
            return {k: v for k, v in default_profile.items() if k != "_id"}
        return {k: v for k, v in doc.items() if k != "_id"}

    async def upsert_investor_profile(self, user_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        existing = await self.get_investor_profile(user_id)
        merged = {
            **existing,
            **{k: v for k, v in updates.items() if v is not None},
            "user_id": user_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.investor_col.update_one(
            {"user_id": user_id},
            {"$set": merged},
            upsert=True,
        )
        return merged

    async def append_analysis_history(self, user_id: str, summary_entry: dict[str, Any]) -> None:
        await self.get_investor_profile(user_id)
        await self.investor_col.update_one(
            {"user_id": user_id},
            {
                "$push": {"analysis_history": summary_entry},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()},
            },
            upsert=True,
        )

    async def save_session_trace(self, run_id: str, trace_payload: dict[str, Any]) -> None:
        await self.session_col.update_one(
            {"run_id": run_id},
            {
                "$set": {
                    "run_id": run_id,
                    **trace_payload,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            },
            upsert=True,
        )
