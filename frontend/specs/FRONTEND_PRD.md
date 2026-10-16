# FRONTEND PRD – מסמך דרישות מוצר ל-Frontend (Product Requirements Document)
**מערכת:** PropTech Multi-Agent Real Estate Investment Analyzer – Next.js 15 Frontend
**גרסה:** 1.0.0
**שפה עיצובית:** Liquid Glass 4.0 Pro UI (RTL Native Hebrew)

---

## 1. סקירה ומטרת ה-Frontend
ממשק המשתמש של **PropTech Investment Analyzer** מעניק למשקיעי נדל"ן, שמאים ויועצי משכנתאות חדר בקרה ויזואלי ואינטראקטיבי (**Investment Command Center**). הממשק מאפשר להזין פרטי נכס, להעלות מסמכי PDF (נסח טאבו, חוזה מכר, דוח שמאות), לצפות בזמן אמת בעבודת צוות 5 הסוכנים (`Orchestrator`, `Market Agent`, `Financial Agent`, `Legal RAG Agent`, `Critic Guardrail Agent`), לאשר או לעדכן הנחות יסוד במצב `Human-In-The-Loop (HITL)`, ולקבל דוח השקעה אינטראקטיבי עם גרפים וציטוטים מדויקים מהמסמכים.

## 2. מסכים ודרישות פונקציונליות (Functional Requirements)

| מזהה | שם המסך / הרכיב | פירוט הדרישה |
| :--- | :--- | :--- |
| **FE-01** | **אימות משתמשים והגנת נתיבים (`Auth & JWT Middleware`)** | מסכי התחברות והרשמה נקיים, שמירת ה-`JWT` ב-HttpOnly Cookie (דרך Next.js Route Handlers), והגנה על נתיבי הדשבורד באמצעות `middleware.ts`. |
| **FE-02** | **הגדרת פרופיל משקיע (`Investor Memory Page`)** | מסך ניהול פרופיל המשקיע המסונכרן מול ה-`Long-Term Memory` ב-MongoDB: הגדרת הון עצמי זמין (`₪`), רמת סיכון מועדפת (שמרני / מאוזן / אגרסיבי), יעד תשואה מינימלי (`%`), וערים מועדפות. |
| **FE-03** | **אשף יצירת נכס והעלאת מסמכי RAG (`Property & PDF Upload Wizard`)** | טופס מובנה להזנת פרטי הנכס (כתובת, עיר, שטח במ"ר במודעה, מחיר מבוקש ב-`₪`, שכירות משוערת) + אזור Drag & Drop להעלאת קובצי PDF (נסח טאבו, חוזה מכר, דוח שמאות) עם חיווי אינדוקס ב-Vector Store. |
| **FE-04** | **תצוגת תזמור סוכנים חיה (`Live Multi-Agent Pipeline Visualizer`)** | תצוגה ויזואלית חיה של 5 הסוכנים בזמן ריצת הניתוח: מציגה אילו סוכנים רצים במקביל (`Market`, `Financial`, `Legal RAG`), מתי הסוכן המבקר (`Critic Guardrail`) בודק סתירות, וסטטוס כל סוכן. |
| **FE-05** | **מודאל אישור אנושי (`Human-In-The-Loop Approval Modal`)** | כאשר ה-Backend מחזיר קוד `202 Accepted` וסטטוס `PAUSED_FOR_APPROVAL`, נפתח מודאל התערבות שמציג את אזהרות ה-Critic (למשל `Context Clash` בין השטח במודעה לשטח בטאבו, הערת אזהרה או תזרים שלילי), ומאפשר למשתמש לעדכן מחיר/הון עצמי או לאשר המשך ריצה. |
| **FE-06** | **דשבורד דוח השקעה אינטראקטיבי (`Executive Investment Dashboard`)** | תצוגת הדוח הסופי מחולקת ל-4 כרטיסי עומק: 1. **המלצת השקעה וציון סיכון (Gauge 1–100)**, 2. **מדדים פיננסיים ולוח סילוקין משכנתא** (`Cap Rate`, `Cash-on-Cash`, `IRR`, מס רכישה ותזרים חודשי), 3. **השוואת שוק ומחיר למ"ר**, 4. **ממצאי RAG משפטיים עם ציטוט ומספר עמוד מודגש**. |

---

## 7. v2.0 Expansion Pack – UI & Spatial Audio (Sprint 10)
* **9-Agent Pipeline Visualizer:** תצוגה חיה של כל 9 הסוכנים במקביל (כולל Vision CAPEX, GIS תמ"א 38, מונטה-קרלו ומו"מ).
* **Floorplan Vision Analyzer (`FloorplanVisionAnalyzer.tsx`):** הצגת אומדן שיפוץ סעיף-אחר-סעיף (`BOQ`) והעלאת תמונות/תשריטים לבדיקת `Vision` חיה.
* **Urban Renewal GIS Card (`UrbanRenewalGisCard.tsx`):** הצגת פוטנציאל התחדשות עירונית, הסתברות לתמ"א 38/פינוי-בינוי, מרחק לרכבת קלה/מטרו ואפסייד צפוי.
* **Interactive What-If Sandbox (`InteractiveWhatIfSandbox.tsx`):** סימולטור הרגישות עם מחוונים לריבית בנק ישראל ושיעור אי-תפוסה, כולל התפלגות מונטה-קרלו (`P10`, `P50`, `P90`).
* **Negotiation Playbook Card (`NegotiationPlaybookCard.tsx`):** הצעת מחיר נגדית מומלצת, נקודות לחץ משפטיות/הנדסיות, העתקת טיוטת מו"מ בעברית, ושיתוף ישיר ל-WhatsApp / Telegram.
* **Spatial Audio Feedback (`SpatialAudioFeedback.ts`):** חיווי קולי תלת-ממדי מבוסס `Web Audio API` (`PannerNode` + `BiquadFilterNode`) עם כפתור השתקה ב-Topbar.
