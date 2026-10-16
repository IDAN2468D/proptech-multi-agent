# SPEC – מפרט ארכיטקטורה טכני (Technical Architecture Specification)
**מערכת:** PropTech Multi-Agent Real Estate Investment Analyzer
**תקן:** OpenSpec / Spec-Driven Development (SDD)

---

## 1. מחסנית טכנולוגית (Tech Stack)
* **שפה ושרת Web:** Python 3.11+, `FastAPI` (אסינכרוני מלא), `Uvicorn`, `Pydantic v2`, `pydantic-settings`.
* **אבטחה ואימות:** `PyJWT`, `bcrypt` / `passlib[bcrypt]`, OAuth2 Password Bearer, Middleware מרכזי לניהול שגיאות (`Centralized Error Manager`).
* **מסדי נתונים (שכבת DAL כפולה):**
  * **PostgreSQL / SQLite Async + SQLAlchemy 2.0 (Async ORM):** לניהול משתמשים, הרשאות, רישומי נכסים מובנים, היסטוריית עסקאות השוואה ולוגים של חישובים פיננסיים.
  * **MongoDB + Motor (Async NoSQL & Vector Store):** לשמירת מסמכי הנכס המפורקים, אינדקס וקטורי ל-RAG, וניהול `Short-Term Session Memory` ו-`Long-Term Investor Memory`.
* **תזמור סוכנים, RAG ו-MCP:** ארכיטקטורת Supervisor/Orchestrator אסינכרונית מבוססת חוזי Pydantic v2, `pypdf` לחילוץ עמודים וטקסט, ו-`mcp` (`FastMCP`) לבניית שרת ה-MCP.
* **בדיקות ו-DevOps:** `pytest`, `pytest-asyncio`, `httpx`, `Docker`, `docker-compose`, ו-GitHub Actions ל-CI/CD.

## 2. ארכיטקטורת שכבות קשיחה (`Controllers -> BLL -> DAL`)
1. **Presentation Layer (`app/controllers/`):** קליטת בקשות HTTP, ולידציית סכמות קלט, אימות JWT, והחזרת סכמות פלט וקודי סטטוס (`200`, `201`, `202 Accepted` עבור HITL).
2. **Business Logic & Multi-Agent Layer (`app/bll/`):** שירותי אימות, ניהול זיכרון משקיע, צינור ה-RAG, כלי חישוב פיננסיים דטרמיניסטיים, תתי-הסוכנים והאורקסטרטור.
3. **Data Access Layer (`app/dal/`):** ריפוזיטוריז אסינכרוניים ל-SQL, ריפוזיטוריז ל-MongoDB (Vector & Memory), ולקוח HTTP אסינכרוני עם Retry ו-Timeout לשירותי שוק חיצוניים.

## 3. חוזי הסוכנים (`app/models/agent_outputs.py`)

### 3.1 `MarketAnalysisResult`
* `avg_price_per_sqm_ils: float`
* `subject_price_per_sqm_ils: float`
* `market_deviation_pct: float`
* `estimated_monthly_rent_ils: float`
* `comparable_transactions_count: int`
* `neighborhood_highlights: list[str]`

### 3.2 `FinancialMetricsResult`
* `purchase_tax_ils: float`
* `loan_amount_ils: float`
* `loan_to_value_pct: float`
* `monthly_mortgage_payment_ils: float`
* `net_monthly_cashflow_ils: float`
* `gross_yield_pct: float`
* `net_cap_rate_pct: float`
* `cash_on_cash_return_pct: float`
* `projected_10yr_irr_pct: float`

### 3.3 `LegalFinding` & `LegalDueDiligenceResult`
* `findings: list[LegalFinding]` (`category`, `severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]`, `description`, `source_document`, `page_number: int`, `exact_quote: str`)
* `registered_area_sqm: Optional[float]`
* `has_blocking_liens_or_warnings: bool`

### 3.4 `CriticVerdict`
* `status: Literal["APPROVED", "NEEDS_HUMAN_REVIEW", "REJECTED"]`
* `overall_risk_score: int` (`1..100`)
* `context_clashes_detected: list[str]`
* `math_verification_passed: bool`
* `hitl_reason: Optional[str]`

### 3.5 `InvestmentExecutiveReport`
* `property_id: str`
* `run_id: str`
* `market: MarketAnalysisResult`
* `financials: FinancialMetricsResult`
* `legal: LegalDueDiligenceResult`
* `critic: CriticVerdict`
* `investment_recommendation: Literal["STRONG_BUY", "BUY_WITH_CAUTION", "HOLD_FOR_REVIEW", "AVOID"]`
* `executive_summary: str`

## 4. זרימת המידע ותזמור הסוכנים (Data Flow & Orchestration)
1. `POST /api/v1/analysis/run` מקבל `property_id` ופרמטרי מימון אופציונליים.
2. ה-`InvestmentOrchestrator` שולף מ-MongoDB את פרופיל המשקיע (`Long-Term Memory`).
3. הרצה מקבילית (`asyncio.gather`) של `MarketAgent`, `FinancialAgent`, ו-`LegalRAGAgent` בחלונות הקשר מבודדים לחלוטין.
4. `CriticGuardrailAgent` מאמת דטרמיניסטית את כל המספרים מול `financial_math.py` ומצליב נתונים בין המודעה לנסח הטאבו (`registered_area_sqm` מול `area_sqm`).
5. אם `overall_risk_score >= 70` (או סף הסיכון של המשקיע), או `has_blocking_liens_or_warnings == True`, או `net_monthly_cashflow_ils < 0`, הריצה נעצרת במצב `PAUSED_FOR_APPROVAL` ומוחזר סטטוס `202 Accepted`.
6. קריאה ל-`POST /api/v1/analysis/{run_id}/approve` מאפשרת למשקיע לאשר את הסיכון או לעדכן מחיר/הון עצמי לאחר מו"מ ולהפיק את ה-`InvestmentExecutiveReport` הסופי.

## 5. נתיבי ה-API (`app/controllers/`)

| Method | Endpoint | Auth | תיאור |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Public | רישום משתמש חדש ושמירת סיסמה מוצפנת ב-SQL. |
| `POST` | `/api/v1/auth/login` | Public | אימות משתמש והחזרת `access_token` מסוג JWT. |
| `GET` | `/api/v1/investor/profile` | JWT | שליפת פרופיל המשקיע והזיכרון ארוך-הטווח שלו מ-MongoDB. |
| `PUT` | `/api/v1/investor/profile` | JWT | עדכון העדפות משקיע (הון עצמי, סף סיכון, יעד תשואה, ערים מועדפות). |
| `POST` | `/api/v1/properties` | JWT | יצירת רשומת נכס חדשה לבדיקה ב-SQL. |
| `POST` | `/api/v1/properties/{property_id}/documents` | JWT | העלאת קובצי PDF והרצת צינור ה-RAG Indexing ל-MongoDB. |
| `POST` | `/api/v1/analysis/run` | JWT | הרצת צוות הסוכנים המלא על הנכס והחזרת דוח או בקשת אישור `HITL`. |
| `POST` | `/api/v1/analysis/{run_id}/approve` | JWT | אישור אנושי (`Human-In-The-Loop`) או עדכון פרמטרים להשלמת הדוח הסופי. |
| `GET` | `/api/v1/analysis/{run_id}` | JWT | שליפת מצב הריצה והדוח המלא לפי מזהה ריצה. |


---

## 6. מפרט טכני מורחב – גרסה v2.0 (9 Agents & 5 MCP Servers)

### 6.1 סכמות Pydantic v2 החדשות (`app/models/agent_outputs_v2.py`)
* **`VisionRenovationResult` (סוכן 6):** `property_condition`, `can_add_room_or_split`, `structural_notes`, `boq_items`, `total_estimated_renovation_ils`, `estimated_post_renovation_value_ils`.
* **`UrbanRenewalGISResult` (סוכן 7):** `tama38_or_pinui_binui_likelihood`, `distance_to_light_rail_meters`, `walkability_score`, `expected_additional_sqm`, `projected_renewal_upside_pct`.
* **`MacroStressTestResult` (סוכן 8):** `base_case_monthly_cashflow_ils`, `rate_hike_plus_1_5_pct_cashflow_ils`, `vacancy_2_months_annual_cashflow_ils`, `combined_worst_case_monthly_cashflow_ils`, `probability_of_positive_cashflow_pct`, `max_safe_interest_rate_pct`.
* **`NegotiationPlaybookResult` (סוכן 9):** `asking_price_ils`, `recommended_opening_offer_ils`, `target_closing_price_ils`, `walk_away_max_price_ils`, `price_reduction_justifications`, `ready_to_send_hebrew_message`.

### 6.2 ארבעת שרתי ה-MCP החדשים (`mcp_servers/`)
1. `geospatial_gis_mcp.py` – מרחקי רכבת קלה, GIS והתחדשות עירונית.
2. `playwright_market_mcp.py` – היצע מודעות פעילות, ירידות מחיר וזמן מדף (DOM).
3. `boi_macro_rates_mcp.py` – ריבית בנק ישראל, ריבית פריים ומדד המחירים לצרכן.
4. `deal_room_comms_mcp.py` – ייצוא דוח עסקה, שליחת Webhook ל-Slack ויצירת קובץ יומן `.ics`.

### 6.3 נתיבי API חדשים ב-v2.0
* `POST /api/v1/properties/{id}/vision-upload`
* `POST /api/v1/analysis/{run_id}/stress-test`
* `POST /api/v1/analysis/{run_id}/share-deal`
