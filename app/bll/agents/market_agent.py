from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.bll.agents.tools.market_tools import fetch_market_comps_and_benchmarks
from app.models.agent_outputs import MarketAnalysisResult


class MarketAgentIsolatedContext(BaseModel):
    """Isolated minimal context for MarketAgent to prevent Context Confusion/Distraction."""

    city: str
    address: str
    asking_price_ils: float = Field(..., gt=0)
    area_sqm: float = Field(..., gt=0)
    rooms: float = 4.0


class MarketAgent:
    """
    Sub-Agent 1: Market & Comps Agent.
    Operates strictly on MarketAgentIsolatedContext and returns a validated MarketAnalysisResult.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def run(self, context: MarketAgentIsolatedContext) -> MarketAnalysisResult:
        raw_metrics = await fetch_market_comps_and_benchmarks(
            session=self.session,
            city=context.city,
            area_sqm=context.area_sqm,
            asking_price_ils=context.asking_price_ils,
        )
        return MarketAnalysisResult(**raw_metrics)
