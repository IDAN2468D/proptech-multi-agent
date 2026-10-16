# Frontend Architecture State – PropTech Multi-Agent Analyzer

- **Framework:** Next.js 15 App Router + React 19 + TypeScript Strict
- **Design System:** Liquid Glass 4.0 Pro UI (`backdrop-blur-xl`, RTL logical properties, Heebo font)
- **Boundary Validation:** Strict `Zod` schemas matching Backend `Pydantic v2` models 1:1
- **Backend Integration:** FastAPI Multi-Agent Server (`http://localhost:8000`) + Next.js BFF Auth Cookie Route Handlers
