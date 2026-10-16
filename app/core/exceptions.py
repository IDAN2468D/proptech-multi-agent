from typing import Any
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.logging import get_trace_id, logger


class PropTechBaseException(Exception):
    """Base domain exception for PropTech Multi-Agent system."""

    def __init__(
        self,
        message: str,
        error_code: str = "PROPTECH_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(PropTechBaseException):
    """Raised when JWT authentication or login credentials fail."""

    def __init__(self, message: str = "Authentication failed", details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            error_code="AUTH_UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class PermissionDeniedError(PropTechBaseException):
    """Raised when a user accesses a resource belonging to another user."""

    def __init__(self, message: str = "Access denied to requested resource") -> None:
        super().__init__(
            message=message,
            error_code="AUTH_FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ResourceNotFoundError(PropTechBaseException):
    """Raised when a requested entity (Property, Run, User) is not found."""

    def __init__(self, resource_name: str, resource_id: str) -> None:
        super().__init__(
            message=f"{resource_name} '{resource_id}' was not found.",
            error_code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource_name, "id": resource_id},
        )


class AgentExecutionError(PropTechBaseException):
    """Raised when an agent or guardrail fails validation or detects tampered math."""

    def __init__(self, agent_name: str, message: str, details: dict[str, Any] | None = None) -> None:
        merged = {"agent": agent_name, **(details or {})}
        super().__init__(
            message=message,
            error_code="AGENT_EXECUTION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=merged,
        )


class ContextGuardrailError(PropTechBaseException):
    """Raised when severe context poisoning or math tampering is blocked."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            error_code="CONTEXT_GUARDRAIL_BLOCKED",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


def build_error_Envelope(
    error_code: str,
    message: str,
    details: Any = None,
) -> dict[str, Any]:
    """Build a standardized JSON error envelope across all endpoints."""
    return {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
            "trace_id": get_trace_id(),
        },
    }


def register_exception_handlers(app: FastAPI) -> None:
    """Register Centralized Error Manager handlers on the FastAPI instance."""

    @app.exception_handler(PropTechBaseException)
    async def proptech_exception_handler(request: Request, exc: PropTechBaseException) -> JSONResponse:
        logger.warning(
            f"Domain exception [{exc.error_code}]: {exc.message}",
            extra={"extra_data": {"path": str(request.url.path), "details": exc.details}},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_Envelope(exc.error_code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(
            "Request validation error",
            extra={"extra_data": {"path": str(request.url.path), "errors": exc.errors()}},
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=build_error_Envelope(
                error_code="VALIDATION_ERROR",
                message="Request payload validation failed",
                details={"errors": exc.errors()},
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            f"Unhandled exception: {exc}",
            exc_info=True,
            extra={"extra_data": {"path": str(request.url.path)}},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=build_error_Envelope(
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected internal server error occurred.",
            ),
        )
