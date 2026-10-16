import re
from pydantic import BaseModel
from app.bll.rag_pipeline.retriever import SanitizedContextRetriever
from app.models.agent_outputs import LegalDueDiligenceResult, LegalFinding


class LegalRAGAgentIsolatedContext(BaseModel):
    """Isolated minimal context for LegalRAGAgent."""

    user_id: str
    property_id: str


class LegalRAGAgent:
    """
    Sub-Agent 3: Legal & Appraisal RAG Agent.
    Queries sanitized PDF chunks from MongoDB Vector Store and extracts legal findings
    with mandatory page numbers and exact quotes, plus registered Tabu area in sqm.
    """

    def __init__(self, retriever: SanitizedContextRetriever | None = None) -> None:
        self.retriever = retriever or SanitizedContextRetriever()

    def _extract_registered_area_sqm(self, text: str) -> float | None:
        patterns = [
            r"שטח(?:\s+הדירה)?(?:\s+הרשום)?(?:\s+בטאבו)?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(?:מ\"ר|מ״ר|מר|sqm)",
            r"registered\s+area\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*sqm",
            r"(\d+(?:\.\d+)?)\s*(?:מ\"ר|מ״ר)\s+רשום\s+בטאבו",
        ]
        for pat in patterns:
            match = re.search(pat, text, flags=re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    async def run(self, context: LegalRAGAgentIsolatedContext) -> LegalDueDiligenceResult:
        retrieved = await self.retriever.retrieve_for_property(
            user_id=context.user_id,
            property_id=context.property_id,
        )
        chunks = retrieved["chunks"]
        poisoning_alerts = retrieved["poisoning_alerts"]

        findings: list[LegalFinding] = []
        registered_area: float | None = None
        has_blocking = False

        if poisoning_alerts:
            findings.append(
                LegalFinding(
                    category="SECURITY_CONTEXT_POISONING",
                    severity="HIGH",
                    description="זוהתה וסוננה ניסיון הזרקת הנחיות זדוניות (Context Poisoning) בתוך מסמך הנכס.",
                    source_document=chunks[0]["source_document"] if chunks else "uploaded_document.pdf",
                    page_number=chunks[0]["page_number"] if chunks else 1,
                    exact_quote="[REDACTED_PROMPT_INJECTION]",
                )
            )

        risk_rules: list[tuple[str, str, str, list[str], bool]] = [
            (
                "FORECLOSURE_OR_LIEN",
                "CRITICAL",
                "זוהה צו עיקול או כינוס נכסים פעיל בנסח הטאבו החוסם העברת זכויות.",
                ["עיקול", "כינוס נכסים", "foreclosure", "active lien"],
                True,
            ),
            (
                "UNAUTHORIZED_CONSTRUCTION",
                "CRITICAL",
                "זוהתה חריגת בנייה או צו הריסה מנהלי/שיפוטי בדוח השמאות/טאבו.",
                ["חריגת בנייה", "חריגות בנייה", "צו הריסה", "ללא היתר", "unauthorized construction"],
                True,
            ),
            (
                "WARNING_NOTE_SECTION_126",
                "HIGH",
                "רשומה הערת אזהרה או שעבוד בנסח הטאבו הדורשים מכתב החרגה/סילוק.",
                ["הערת אזהרה", "שעבוד", "משכנתא מדרגה", "warning note"],
                True,
            ),
            (
                "CONTRACT_PENALTY_CLAUSE",
                "MEDIUM",
                "זוהה סעיף פיצוי מוסכם או תנאי תשלום מחמיר בחוזה המכר.",
                ["פיצוי מוסכם", "הפרה יסודית", "איחור במסירה"],
                False,
            ),
        ]

        for chunk in chunks:
            text = chunk["text"]
            doc_name = chunk["source_document"]
            page_num = int(chunk["page_number"])

            if registered_area is None:
                extracted_area = self._extract_registered_area_sqm(text)
                if extracted_area is not None:
                    registered_area = extracted_area

            for category, severity, desc, keywords, is_blocking in risk_rules:
                for kw in keywords:
                    if kw.lower() in text.lower():
                        # Extract exact quote around keyword
                        idx = text.lower().find(kw.lower())
                        start = max(0, idx - 35)
                        end = min(len(text), idx + len(kw) + 65)
                        exact_quote = text[start:end].strip()
                        findings.append(
                            LegalFinding(
                                category=category,
                                severity=severity,  # type: ignore[arg-type]
                                description=desc,
                                source_document=doc_name,
                                page_number=page_num,
                                exact_quote=exact_quote,
                            )
                        )
                        if is_blocking:
                            has_blocking = True
                        break

        if not findings and chunks:
            first = chunks[0]
            findings.append(
                LegalFinding(
                    category="CLEAN_TITLE_CHECK",
                    severity="LOW",
                    description="נסרקו מסמכי הנכס ולא נמצאו עיקולים חוסמים או חריגות בנייה.",
                    source_document=first["source_document"],
                    page_number=int(first["page_number"]),
                    exact_quote=first["text"][:120],
                )
            )

        return LegalDueDiligenceResult(
            findings=findings,
            registered_area_sqm=registered_area,
            has_blocking_liens_or_warnings=has_blocking,
        )
