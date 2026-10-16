# PLAN – תוכנית עבודה ומימוש בספרינטים (Implementation Plan)

## Phase 1: הקמת תשתית SDD, קונפיגורציה, Docker וניהול שגיאות
* [x] יצירת עץ התיקיות המלא וקובצי המפרט (`specs/PRD.md`, `specs/SPEC.md`, `specs/PLAN.md`, `AGENTS.md`).
* [x] כתיבת `pyproject.toml` ו-`.env.example` עם כל התלויות הנדרשות.
* [x] כתיבת `docker-compose.yml` להרמת `postgres:16` ו-`mongo:7` יחד עם שירות ה-`backend`.
* [x] מימוש `app/config/settings.py`, `app/core/logging.py`, ו-`app/core/exceptions.py` (מנהל שגיאות מרכזי שמחזיר JSON אחיד לכל שגיאת ולידציה, הרשאה או שגיאת סוכן).

## Phase 2: שכבת ה-DAL (SQL + MongoDB), אימות JWT וכלים פיננסיים דטרמיניסטיים
* [x] מימוש מודלי ה-ORM ב-SQLAlchemy (`UserORM`, `PropertyORM`, `ComparableTransactionORM`, `AnalysisRunORM`) וריפוזיטוריז אסינכרוניים ב-`app/dal/sql/`.
* [x] מימוש לקוח MongoDB אסינכרוני ב-`app/dal/mongo/` לניהול מסמכי RAG וזיכרון משקיע (`memory_repository.py`).
* [x] מימוש מנגנון `JWT` מלא ב-`app/core/security.py` ושירות אימות ב-`app/bll/auth_service.py`.
* [x] מימוש כלי החישוב הפיננסיים הדטרמיניסטיים ב-`app/bll/agents/tools/financial_math.py`:
  * פונקציית `calculate_mortgage_schedule(principal, annual_rate_pct, years, method="spitzer")`
  * פונקציית `calculate_israeli_purchase_tax(property_price_ils, is_single_home)`
  * פונקציית `compute_roi_metrics(property_price_ils, equity_ils, monthly_rent_ils, annual_expenses_ils, monthly_mortgage_ils, appreciation_rate_pct)`
* [x] כתיבת והרצת בדיקות יחידה (`tests/unit/test_financial_math.py`) לאימות מתמטי של כל הנוסחאות.

## Phase 3: צינור ה-RAG על מסמכי נדל"ן ושרת ה-MCP
* [x] מימוש `loader_splitter.py` לחילוץ טקסט ומספרי עמודים מקובצי PDF וחלוקה לסגמנטים עם חפיפה שומרת-הקשר.
* [x] מימוש `embedder_store.py` ו-`retriever.py` כולל סינון לפי `user_id` ו-`property_id` וסניטציה נגד `Context Poisoning` (הסרת הוראות זדוניות המוסתרות בטקסט המסמך).
* [x] מימוש `mcp_servers/proptech_mcp_server.py` באמצעות `FastMCP` החושף את כלי החישוב הפיננסיים, כלי תחקור עסקאות השוואה, וכלי שליפת דוח השקעה.

## Phase 4: בניית צוות הסוכנים (`Market`, `Financial`, `Legal RAG`, `Critic`)
* [x] מימוש הסכמות המובנות ב-`app/models/agent_outputs.py`.
* [x] מימוש 4 תתי-הסוכנים ב-`app/bll/agents/` כך שכל סוכן מקבל אך ורק את ה-Context המינימלי הדרוש לו ומחזיר אובייקט Pydantic מאומת.
* [x] מימוש `CriticGuardrailAgent` שבודק התאמה מספרית מול כלי הפייתון, מזהה `Context Clash` בין נתוני המודעה לנתוני הטאבו, ומחליט אם להפעיל עצירת `Human-In-The-Loop`.

## Phase 5: אורקסטרטור, זיכרון משקיע ו-Controllers ב-FastAPI
* [x] מימוש `InvestmentOrchestrator` ב-`app/bll/agents/orchestrator.py` המריץ במקביל את הסוכנים, משלב את ה-`Long-Term Memory` של המשקיע, ותומך בעצירה והמשך ריצה (`HITL Resume`).
* [x] חיבור כל ה-Controllers (`auth`, `investor`, `properties`, `analysis`) אל שכבת ה-`BLL` ב-`app/main.py`.

## Phase 6: בדיקות אינטגרציה, Agent Evaluation ו-CI/CD
* [x] כתיבת בדיקות אינטגרציה ב-`tests/integration/` הבודקות את כל נתיבי ה-API (כולל זרימת `PAUSED_FOR_APPROVAL` ואישור `HITL`).
* [x] כתיבת בדיקת הערכת סוכנים (`tests/evals/test_agent_accuracy.py`) שמוודאת שסוכן ה-Critic בולם בהצלחה ניסיון להזריק מספר שגוי או סתירה בשטח הדירה.
* [x] יצירת `.github/workflows/ci.yml` להרצה אוטומטית של הטסטים.


---

## v2.0 Expansion Pack (Sprints 7–10)

### Sprint 7: כלי חישוב חדשים, סוכן Vision & Renovation (סוכן 6) וסוכן Urban Renewal GIS (סוכן 7)
* [x] עדכון `specs/PRD.md`, `specs/SPEC.md` ו-`specs/PLAN.md` עם מפרט גרסה v2.0.
* [x] מימוש `renovation_calculator.py` ו-`stress_test_engine.py` כולל בדיקות יחידה ב-`tests/unit/test_v2_engines.py`.
* [x] מימוש סוכן 6 (`vision_renovation_agent.py`) וסוכן 7 (`urban_renewal_gis_agent.py`) והגדרת סכמות ה-Pydantic שלהם ב-`agent_outputs_v2.py`.

### Sprint 8: סוכן Stress-Test (סוכן 8), סוכן Negotiation (סוכן 9) ושדרוג ה-Orchestrator
* [x] מימוש סוכן 8 (`macro_stress_test_agent.py`) וסוכן 9 (`negotiation_agent.py`).
* [x] עדכון ה-`InvestmentOrchestrator` להרצה מקבילית של סוכנים 1, 2, 3, 6, 7, 8, העברה ל-`CriticGuardrailAgent` והפעלת `NegotiationAgent`.
* [x] עדכון ה-`CriticGuardrailAgent` לשקלול עלות השיפוץ ומבחן הקיצון.

### Sprint 9: הקמת רשת 4 שרתי ה-MCP החדשים וחשיפת נתיבי ה-API ב-FastAPI
* [x] מימוש ארבעת שרתי ה-MCP ב-`mcp_servers/` (`geospatial_gis_mcp.py`, `playwright_market_mcp.py`, `boi_macro_rates_mcp.py`, `deal_room_comms_mcp.py`).
* [x] חשיפת נתיבי ה-Controllers החדשים (`/vision-upload`, `/stress-test`, `/share-deal`) ב-`app/main.py` והרצת בדיקות אינטגרציה ב-`pytest`.

### Sprint 10: שדרוג ה-Frontend ב-Next.js 15 ל-v2.0
* [x] הוספת סכמות ה-`Zod` החדשות ב-`frontend/src/lib/schemas/agent-outputs-v2.schema.ts` ועדכון `AgentPipelineVisualizer.tsx` לתצוגת 9 הסוכנים.
* [x] מימוש ארבע הקומפוננטות החדשות בדשבורד הדוח: `FloorplanVisionAnalyzer.tsx`, `UrbanRenewalGisCard.tsx`, `InteractiveWhatIfSandbox.tsx` ו-`NegotiationPlaybookCard.tsx`.
* [x] הוספת `SpatialAudioFeedback.ts` (Web Audio API) עם כפתור השתקת סאונד ב-Topbar, ואימות בנייה מלאה (`tsc --noEmit` ו-`next build`).
