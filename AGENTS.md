# AGENTS.md – הנדסת הקשר, גבולות גזרה וחוקי עבודה לצוות הסוכנים

## 1. כללי ברזל הנדסיים (Non-Negotiable Constraints)

1. **ארכיטקטורת שכבות קשיחה (`Controllers -> BLL -> DAL`):**
   * `app/controllers/` עוסקים אך ורק בקליטת בקשות HTTP, אימות `JWT` והחזרת תגובות. אסור לייבא מודלי ORM או לקוחות DB בתוך `controllers`.
   * `app/bll/` מכילה את כל הלוגיקה העסקית, צינור ה-RAG ותזמור הסוכנים.
   * `app/dal/` מכילה את כל הגישה למסדי הנתונים (PostgreSQL / SQLAlchemy ו-MongoDB / Motor) ול-APIs חיצוניים.

2. **אפס הזיות מתמטיות (Zero-Math Hallucination):**
   * חל איסור מוחלט על מודל השפה (LLM) לחשב בעצמו לוח סילוקין של משכנתא, מס רכישה, תשואה שנתית, `Cap Rate`, `Cash-on-Cash` או `IRR`.
   * כל חישוב פיננסי חייב להתבצע אך ורק דרך כלי פייתון דטרמיניסטיים בתיקיית `app/bll/agents/tools/financial_math.py`.
   * סוכן ה-`CriticGuardrailAgent` מריץ אימות דטרמיניסטי משלו ופוסל כל פלט שבו מספר כלשהו סוטה מתוצאת הפונקציה המתמטית.

3. **הנדסת הקשר (`Context Engineering`):**
   * **מניעת `Context Confusion` & `Context Distraction`:** כל תת-סוכן מקבל אך ורק את תת-הסכמה המינימלית הדרושה לתפקידו (למשל, `MarketAgent` לא מקבל את טקסט החוזה, ו-`LegalRAGAgent` לא מקבל את היסטוריית עסקאות ההשוואה).
   * **מניעת `Context Poisoning`:** כל קטע טקסט שנשלף מ-MongoDB Vector Store עובר סניטציה ב-`retriever.py` לסינון הזרקות פרומפט (`Prompt Injection`) המוסתרות בתוך מסמכי PDF.
   * **זיהוי `Context Clash`:** `CriticGuardrailAgent` מצליב את שטח הנכס המוצהר במודעה (`area_sqm`) מול השטח הרשום בנסח הטאבו (`registered_area_sqm`) ומתריע על כל סטייה של מעל 5%.

## 2. טופולוגיית הסוכנים (Multi-Agent Topology)
* **`InvestmentOrchestrator`:** סוכן-על (Supervisor) המנהל את זרימת הריצה האסינכרונית, שולף את פרופיל המשקיע מ-MongoDB (`Long-Term Memory`), ומפעיל במקביל (`asyncio.gather`) את שלושת סוכני המומחה.
* **`MarketAgent`:** מנתח עסקאות השוואה, מחיר למ"ר ושכירות חודשית משוערת.
* **`FinancialAgent`:** מפעיל את כלי `financial_math.py` ומחזיר `FinancialMetricsResult`.
* **`LegalRAGAgent`:** מתחקר את מקטעי ה-PDF המאוחסנים ב-MongoDB ומחזיר ממצאים משפטיים עם ציטוט מדויק ומספר עמוד.
* **`CriticGuardrailAgent`:** מאמת חישובים, מזהה סתירות (`Context Clash`), מחשב ציון סיכון (1–100) ומחליט אם לעצור ל-`Human-In-The-Loop` (`PAUSED_FOR_APPROVAL`).
