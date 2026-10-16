from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import get_settings
from app.controllers import (
    analysis_controller,
    auth_controller,
    investor_controller,
    properties_controller,
    stress_test_controller,
    vision_controller,
)
from app.core.exceptions import register_exception_handlers
from app.core.logging import set_trace_id
from app.dal.sql.database import init_sql_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await init_sql_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        version="2.0.0",
        description="Production PropTech Multi-Agent Real Estate Investment Analyzer Backend (v2.0 - 9 Agents & 5 MCPs)",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def trace_id_middleware(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        incoming_tid = request.headers.get("X-Trace-Id")
        tid = set_trace_id(incoming_tid)
        response: Response = await call_next(request)
        response.headers["X-Trace-Id"] = tid
        return response

    register_exception_handlers(app)

    app.include_router(auth_controller.router)
    app.include_router(investor_controller.router)
    app.include_router(properties_controller.router)
    app.include_router(analysis_controller.router)
    app.include_router(vision_controller.router)
    app.include_router(stress_test_controller.router)

    @app.get("/health", tags=["Health"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "healthy", "version": "2.0.0", "service": settings.APP_NAME}

    return app


app = create_app()
