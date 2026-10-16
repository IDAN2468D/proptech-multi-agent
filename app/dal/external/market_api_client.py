import asyncio
from typing import Any
import httpx
from app.config.settings import get_settings

CITY_BENCHMARKS: dict[str, dict[str, Any]] = {
    "תל אביב": {
        "avg_sqm_ils": 56000.0,
        "monthly_rent_per_sqm_ils": 115.0,
        "highlights": [
            "ביקוש שכירות קשיח וגבוה לאורך כל השנה",
            "נגישות לקווי הרכבת הקלה (הקו האדום והסגול)",
            "פוטנציאל השבחה והתחדשות עירונית במרכז העיר",
        ],
    },
    "רמת גן": {
        "avg_sqm_ils": 36500.0,
        "monthly_rent_per_sqm_ils": 82.0,
        "highlights": [
            "קרבה למתחם הבורסה וצירי תחבורה ראשיים",
            "תנופת תמ״א 38 ופינוי-בינוי משמעותית",
            "ביקוש יציב מצד משפחות וזוגות צעירים",
        ],
    },
    "חיפה": {
        "avg_sqm_ils": 19500.0,
        "monthly_rent_per_sqm_ils": 54.0,
        "highlights": [
            "תשואת שכירות שוטפת גבוהה יחסית למרכז הארץ",
            "ביקוש מצד סטודנטים (טכניון ואוניברסיטת חיפה) ואנשי הייטק במת״מ",
            "מחיר כניסה נוח למשקיעים עם הון עצמי בינוני",
        ],
    },
    "באר שבע": {
        "avg_sqm_ils": 15200.0,
        "monthly_rent_per_sqm_ils": 46.0,
        "highlights": [
            "קרבה לאוניברסיטת בן-גוריון, סורוקה ופארק ההייטק גב-ים",
            "תשואה שוטפת גבוהה בקרב דירות 3–4 חדרים",
        ],
    },
    "ירושלים": {
        "avg_sqm_ils": 38000.0,
        "monthly_rent_per_sqm_ils": 85.0,
        "highlights": [
            "ביקוש קשיח מצד אוכלוסייה מקומית ומשקיעי חוץ",
            "פיתוח מואץ סביב צירי הרכבת הקלה והכניסה לעיר",
        ],
    },
}


class ExternalMarketAPIClient:
    """Async httpx client with retry and timeout for external real estate market benchmarks."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_city_market_data(self, city: str, area_sqm: float) -> dict[str, Any]:
        """Attempt live REST API call with timeout & retry; fallback deterministically to benchmark data."""
        normalized_city = city.strip()
        benchmark = CITY_BENCHMARKS.get(
            normalized_city,
            {
                "avg_sqm_ils": 26500.0,
                "monthly_rent_per_sqm_ils": 68.0,
                "highlights": [
                    f"שוק שכירות פעיל ב{normalized_city}",
                    "נגישות למוסדות חינוך וצירי תחבורה מרכזיים",
                ],
            },
        )

        # Simulated resilient retry pattern with httpx
        for attempt in range(2):
            try:
                if self.settings.MARKET_API_BASE_URL.startswith("https://api.nadlan-gov-mock.il"):
                    # Deterministic fast benchmark response in local/mock mode
                    break
                async with httpx.AsyncClient(timeout=self.settings.MARKET_API_TIMEOUT_SECONDS) as client:
                    resp = await client.get(
                        f"{self.settings.MARKET_API_BASE_URL}/benchmarks",
                        params={"city": normalized_city},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        return data
            except Exception:
                if attempt == 0:
                    await asyncio.sleep(0.05)

        avg_sqm = float(benchmark["avg_sqm_ils"])
        est_rent = round(area_sqm * float(benchmark["monthly_rent_per_sqm_ils"]), 2)
        return {
            "city": normalized_city,
            "avg_price_per_sqm_ils": avg_sqm,
            "estimated_monthly_rent_ils": est_rent,
            "neighborhood_highlights": list(benchmark["highlights"]),
            "synthetic_comps": [
                {
                    "address": f"רחוב הרצל {10 + i * 4}, {normalized_city}",
                    "neighborhood": "מרכז העיר",
                    "sale_price_ils": round(avg_sqm * (area_sqm + (i - 2) * 3) * (1 + (i - 2) * 0.015), 2),
                    "area_sqm": float(area_sqm + (i - 2) * 3),
                    "rooms": 4.0,
                    "sale_date": f"2026-0{i + 1}-15",
                }
                for i in range(5)
            ],
        }
