# Architecture State – PropTech Multi-Agent Backend

## Current Architecture Status
- **Methodology:** Spec-Driven Development (SDD / OpenSpec)
- **Layered Architecture:** Strict `Controllers -> BLL -> DAL`
- **Database Layer:** Dual DAL (Async SQLAlchemy 2.0 + Async MongoDB / In-Memory Fallback for deterministic local/CI execution)
- **Multi-Agent Pattern:** Supervisor (`InvestmentOrchestrator`) + 3 Parallel Isolated Sub-Agents (`MarketAgent`, `FinancialAgent`, `LegalRAGAgent`) + `CriticGuardrailAgent` with `Human-In-The-Loop (HITL)` pause/resume.
