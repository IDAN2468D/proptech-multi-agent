# FRONTEND PLAN – תוכנית עבודה ומימוש בספרינטים ל-Frontend

## Phase 1: הקמת פרויקט Next.js 15, קובצי SDD, תשתית RTL ו-Design System
* [x] יצירת קובצי המפרט (`specs/FRONTEND_PRD.md`, `specs/FRONTEND_SPEC.md`, `specs/FRONTEND_PLAN.md`, `.agents/state/ARCHITECTURE_STATE.md`).
* [x] אתחול פרויקט `Next.js 15` (App Router, TypeScript, Tailwind CSS) והגדרת פונט עברי (`Heebo` או `Rubik`) ו-`dir="rtl"` ב-`src/app/layout.tsx`.
* [x] מימוש כלי עזר ב-`src/lib/formatters.ts` לפורמט שקלים (`₪`), אחוזים, מ"ר ותאריכים ישראליים.
* [x] בניית מעטפת הדשבורד היוקרתית (`Liquid Glass 4.0 Pro UI`) עם תפריט צד בעברית, פס עליון המציג את תקציב המשקיע הנוכחי מ-`Long-Term Memory`, ותמיכה במצב כהה (Dark Mode).

## Phase 2: שכבת ה-API Client, סכמות ה-Zod ואימות JWT
* [x] מימוש כל סכמות ה-`Zod` ב-`src/lib/schemas/` (`auth.schema.ts`, `property.schema.ts`, `agent-outputs.schema.ts`).
* [x] מימוש `src/lib/api-client.ts` עם הזרקת `Authorization: Bearer <token>`, טיפול מרכזי בשגיאות HTTP (401, 422, 500), ואימות תגובות עם `Zod`.
* [x] מימוש מסכי `/login` ו-`/register` והגדרת `src/middleware.ts` להגנה על נתיבי הדשבורד.

## Phase 3: מסך פרופיל משקיע (`Long-Term Memory`) ואשף העלאת נכס ומסמכי RAG
* [x] מימוש מסך `/investor-profile` המאפשר למשתמש לעדכן הון עצמי, סף סיכון, יעד תשואה שנתית וערים מועדפות מול `/api/v1/investor/profile`.
* [x] מימוש אשף `/properties/new` הכולל טופס פרטי נכס מאומת ב-`Zod` ורכיב `PdfRagDropzone.tsx` להעלאת קובצי PDF מרובים (נסח טאבו, חוזה מכר, דוח שמאות) עם פס התקדמות לאינדוקס ה-RAG.

## Phase 4: ויזואליזציית צוות הסוכנים בזמן אמת ומודאל `Human-In-The-Loop (HITL)`
* [x] מימוש `AgentPipelineVisualizer.tsx` באמצעות `Framer Motion`: תרשים חי המציג את ה-`Orchestrator` מפעיל במקביל את שלושת הסוכנים (`Market`, `Financial`, `Legal RAG`) ומעביר את הפלט ל-`Critic Guardrail`.
* [x] מימוש `HitlApprovalModal.tsx`: נפתח אוטומטית כאשר הסטטוס הוא `PAUSED_FOR_APPROVAL`, מציג למשתמש בבירור את סתירות ה-`Context Clash` או התראות הסיכון, ומאפשר לו לערוך את מחיר הרכישה/ההון העצמי או לאשר את המשך הריצה מול `POST /api/v1/analysis/{run_id}/approve`.

## Phase 5: דשבורד דוח ההשקעה הסופי (`Executive Investment Report`) ובדיקות
* [x] מימוש `ExecutiveSummaryHero.tsx` עם תגית ההמלצה (`STRONG_BUY`, `BUY_WITH_CAUTION`, `HOLD_FOR_REVIEW`, `AVOID`), מד סיכון ויזואלי (1–100), ואישור `math_verification_passed`.
* [x] מימוש `FinancialMetricsGrid.tsx` ו-`MortgageAmortizationChart.tsx` (`Recharts`) להצגת מס רכישה, החזר משכנתא חודשי, תזרים נטו, `Cap Rate`, `Cash-on-Cash` ו-`IRR`.
* [x] מימוש `MarketCompsSection.tsx` ו-`LegalRagFindingsList.tsx` (כולל סינון לפי חומרה, הצגת הציטוט המדויק ומספר העמוד במסמך).
* [x] הרצת בדיקת TypeScript (`tsc --noEmit`) ובניית פרודקשן (`next build`) כדי לוודא אפס שגיאות טיפוסים או רינדור.

---

## Phase 6 (Sprint 10 – v2.0 Expansion Pack): שדרוג ה-Frontend ב-Next.js 15 ל-v2.0
* [x] הוספת סכמות ה-`Zod` החדשות ב-`src/lib/schemas/agent-outputs-v2.schema.ts` ועדכון `AgentPipelineVisualizer.tsx` לתצוגת 9 הסוכנים.
* [x] מימוש ארבע הקומפוננטות החדשות בדשבורד הדוח: `FloorplanVisionAnalyzer.tsx`, `UrbanRenewalGisCard.tsx`, `InteractiveWhatIfSandbox.tsx` ו-`NegotiationPlaybookCard.tsx`.
* [x] הוספת `SpatialAudioFeedback.ts` (Web Audio API) עם כפתור השתקת סאונד ב-Topbar, ואימות בנייה מלאה (`tsc --noEmit` ו-`next build`).
