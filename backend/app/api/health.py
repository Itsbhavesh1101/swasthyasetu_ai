"""Dependency-free process health endpoints."""

from enum import StrEnum

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/health", tags=["health"])


class LivenessStatus(StrEnum):
    """Liveness state returned by the process."""

    OK = "ok"


class ReadinessStatus(StrEnum):
    """Readiness state returned by the application."""

    READY = "ready"


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
async def readiness() -> ReadinessResponse:
    """Report readiness using only dependencies that exist in P1-A."""
    return ReadinessResponse(status=ReadinessStatus.READY)
