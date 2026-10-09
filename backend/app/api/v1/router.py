"""Compile-time registration boundary for version-one module routers."""

from collections.abc import Sequence

from fastapi import APIRouter


def build_api_v1_router(
    *,
    prefix: str,
    module_routers: Sequence[APIRouter] = (),
) -> APIRouter:
    """Compose explicitly supplied module routers below the configured v1 prefix."""
    router = APIRouter(prefix=prefix)
    for module_router in module_routers:
        router.include_router(module_router)
    return router
