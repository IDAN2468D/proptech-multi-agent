from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.dal.external.market_api_client import ExternalMarketAPIClient
from app.dal.sql.repositories import CompsRepository


async def fetch_market_comps_and_benchmarks(
    session: AsyncSession,
    city: str,
    area_sqm: float,
    asking_price_ils: float,
) -> dict[str, Any]:
    """
    Deterministic market tool combining SQL ComparableTransactionORM records and ExternalMarketAPIClient.
    Computes average price per sqm, subject price per sqm, and market deviation percentage.
    """
    api_client = ExternalMarketAPIClient()
    external_data = await api_client.fetch_city_market_data(city=city, area_sqm=area_sqm)

    comps_repo = CompsRepository(session)
    comps = await comps_repo.seed_comps_if_empty(
        city=city,
        comps_payload=external_data.get("synthetic_comps", []),
    )

    if comps:
        sqm_prices = [c.sale_price_ils / c.area_sqm for c in comps if c.area_sqm > 0]
        avg_price_per_sqm = sum(sqm_prices) / len(sqm_prices)
        comps_count = len(comps)
    else:
        avg_price_per_sqm = float(external_data["avg_price_per_sqm_ils"])
        comps_count = 0

    subject_price_per_sqm = asking_price_ils / area_sqm
    deviation_pct = ((subject_price_per_sqm - avg_price_per_sqm) / avg_price_per_sqm) * 100.0

    return {
        "avg_price_per_sqm_ils": round(avg_price_per_sqm, 2),
        "subject_price_per_sqm_ils": round(subject_price_per_sqm, 2),
        "market_deviation_pct": round(deviation_pct, 2),
        "estimated_monthly_rent_ils": round(float(external_data["estimated_monthly_rent_ils"]), 2),
        "comparable_transactions_count": comps_count,
        "neighborhood_highlights": list(external_data.get("neighborhood_highlights", [])),
    }
