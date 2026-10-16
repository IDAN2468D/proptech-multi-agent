# FRONTEND SPEC – מפרט ארכיטקטורה טכני ל-Frontend (Technical Specification)

## 1. מחסנית טכנולוגית (Frontend Tech Stack)
* **Framework:** `Next.js 15` (App Router), `React 19`, `TypeScript 5+` (Strict Mode).
* **Styling & UI:** `Tailwind CSS v4`, `Framer Motion` (אנימציות 120Hz מבוססות GPU), `lucide-react` (אייקונים).
* **Data Visualization:** `Recharts` (גרף תזרים מזומנים, לוח סילוקין משכנתא קרן/ריבית, והשוואת מחיר למ"ר).
* **State, Forms & Validation:** `TanStack Query v5`, `React Hook Form`, ו-`Zod` לאימות גבולות קשיח (1:1 מול סכמות `Pydantic v2` ב-FastAPI).

## 2. כללי ברזל הנדסיים ועיצוביים
* **תמיכה מלאה בעברית ו-RTL טבעי:** `dir="rtl"` ב-Root Layout, שימוש ב-Logical Properties (`ms-`, `me-`, `ps-`, `pe-`, `text-start`), פורמט מטבע ישראלי (`₪` באמצעות `Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS' })`), ותאריכים בפורמט `DD/MM/YYYY`.
* **Liquid Glass 4.0 Pro UI:** משטחי זכוכית כהה (`backdrop-blur-xl bg-slate-900/60 border border-white/10`), גבולות זוהרים עדינים לכרטיסי הסוכנים, ואנימציות GPU חלקות.
* **Strict Zod Boundary Validation:** כל תגובה משרת ה-FastAPI עוברת `Schema.parse()` לפני רינדור בקומפוננטה.
* **מודולריות קפדנית:** מקסימום 200 שורות קוד (LOC) לכל קובץ קומפוננטה.

## 3. מיפוי קריאות ה-API מול שרת ה-FastAPI (`src/lib/api-client.ts`)
* `POST /api/v1/auth/register` & `POST /api/v1/auth/login` (דרך Next.js BFF Route Handlers לשמירת Cookie + Token).
* `GET` & `PUT /api/v1/investor/profile` – שליפה ועדכון של `Long-Term Investor Memory`.
* `GET` & `POST /api/v1/properties` – רשימת נכסים ויצירת נכס חדש.
* `POST /api/v1/properties/{id}/documents` – העלאת קובצי PDF ואינדוקס RAG ב-MongoDB.
* `POST /api/v1/analysis/run` – הרצת צוות 5 הסוכנים במקביל.
* `GET /api/v1/analysis/{run_id}` – שליפת דוח או מצב `PAUSED_FOR_APPROVAL`.
* `POST /api/v1/analysis/{run_id}/approve` – אישור אנושי (`HITL`) או עדכון מחיר/הון עצמי לאחר משא ומתן.

---

## 6. v2.0 Expansion Pack Components & Schemas (Sprint 10)
* `src/lib/schemas/agent-outputs-v2.schema.ts`: סכמות `Zod` עבור `VisionRenovationResultSchema`, `UrbanRenewalGISResultSchema`, `MacroStressTestResultSchema`, `NegotiationPlaybookResultSchema`.
* `src/components/vision/FloorplanVisionAnalyzer.tsx`: רכיב ניתוח תמונות ותשריטי דירה מול `POST /api/v1/properties/{id}/vision-upload`.
* `src/components/urban/UrbanRenewalGisCard.tsx`: כרטיס GIS להתחדשות עירונית ותשתיות תחבורה.
* `src/components/stress-test/InteractiveWhatIfSandbox.tsx`: סימולטור `What-If` מול `POST /api/v1/analysis/{run_id}/stress-test`.
* `src/components/negotiation/NegotiationPlaybookCard.tsx`: כרטיס אסטרטגיית מו"מ ושיתוף דיל מול `POST /api/v1/analysis/{run_id}/share-deal`.
* `src/components/audio/SpatialAudioFeedback.ts`: מנוע סאונד מרחבי ב-Web Audio API.
