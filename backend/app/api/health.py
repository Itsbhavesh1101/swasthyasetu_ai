"""Process liveness and dependency-aware readiness endpoints."""

from enum import StrEnum

from fastapi import APIRouter, Request, Response, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/health", tags=["health"])


class LivenessStatus(StrEnum):
    """Liveness state returned by the process."""

    OK = "ok"


class ReadinessStatus(StrEnum):
    """Readiness state returned by the application."""

    READY = "ready"
    NOT_READY = "not_ready"


class DependencyStatus(StrEnum):
    """Status values reserved for real readiness dependencies."""

    OK = "ok"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class LivenessResponse(BaseModel):
    """Stable liveness response contract."""

    status: LivenessStatus


class ReadinessResponse(BaseModel):
    """Stable readiness response contract for current dependencies."""

    status: ReadinessStatus
    required: dict[str, DependencyStatus] = Field(default_factory=dict)
    optional: dict[str, DependencyStatus] = Field(default_factory=dict)


@router.get("/live", response_model=LivenessResponse)
async def liveness() -> LivenessResponse:
    """Report whether the application process can serve requests."""
    return LivenessResponse(status=LivenessStatus.OK)


@router.get("/ready", response_model=ReadinessResponse)
async def readiness(request: Request, response: Response) -> ReadinessResponse:
    """Report one bounded, privacy-safe check for every required dependency."""
    database = getattr(request.app.state, "database", None)
    if database is None:
        return ReadinessResponse(status=ReadinessStatus.READY)

    try:
        await database.ping()
    except Exception:  # noqa: BLE001 - dependency details must not cross this boundary
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            status=ReadinessStatus.NOT_READY,
            required={"database": DependencyStatus.UNAVAILABLE},
        )

    return ReadinessResponse(
        status=ReadinessStatus.READY,
        required={"database": DependencyStatus.OK},
    )
