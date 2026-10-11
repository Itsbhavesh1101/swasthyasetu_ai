"""FastAPI application construction and Uvicorn entry point."""

from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.api.errors import register_error_handlers
from app.api.health import router as health_router
from app.api.middleware import RequestContextMiddleware
from app.api.v1 import build_api_v1_router
from app.config import Settings
from app.shared.feature_flags import ConfigurationFeatureFlagProvider, FeatureFlagService
from app.shared.modules import ModuleRegistration, ModuleRegistry
from app.shared.observability import (
    ObservabilityRuntime,
    configure_logging,
    create_observability_runtime,
)
from app.shared.persistence import DatabaseRuntime, create_database_runtime

APP_VERSION = "0.1.0"


def create_app(
    settings: Settings | None = None,
    *,
    api_v1_routers: Sequence[APIRouter] = (),
    module_registrations: Sequence[ModuleRegistration[APIRouter]] = (),
    observability: ObservabilityRuntime | None = None,
    feature_flags: FeatureFlagService | None = None,
    database: DatabaseRuntime | None = None,
) -> FastAPI:
    """Create an application from explicitly supplied, compile-time registrations."""
    resolved_settings = settings or Settings()
    configure_logging(resolved_settings.log_level)
    resolved_observability = observability or create_observability_runtime(
        resolved_settings.observability
    )
    resolved_feature_flags = feature_flags or FeatureFlagService(
        ConfigurationFeatureFlagProvider.from_names(resolved_settings.features.enabled)
    )
    resolved_database = (
        database if database is not None else create_database_runtime(resolved_settings.database)
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        """Dispose the application-owned database runtime on shutdown."""
        try:
            yield
        finally:
            if resolved_database is not None:
                await resolved_database.dispose()

    module_registry = ModuleRegistry[APIRouter]()
    for registration in module_registrations:
        module_registry.register(registration)
    module_registry.finalize()

    application = FastAPI(
        title=resolved_settings.app_name,
        version=APP_VERSION,
        debug=resolved_settings.debug,
        lifespan=lifespan,
    )
    application.state.settings = resolved_settings
    application.state.module_registry = module_registry
    application.state.capability_registry = module_registry.capability_registry
    application.state.feature_flags = resolved_feature_flags
    application.state.observability = resolved_observability
    application.state.database = resolved_database

    register_error_handlers(application)
    application.add_middleware(RequestContextMiddleware, observability=resolved_observability)
    application.include_router(health_router)
    application.include_router(
        build_api_v1_router(
            prefix=resolved_settings.api_v1_prefix,
            module_routers=(*api_v1_routers, *module_registry.routers),
        )
    )
    return application


app = create_app()
