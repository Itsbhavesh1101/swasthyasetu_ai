"""FastAPI application construction and Uvicorn entry point."""

from collections.abc import Sequence

from fastapi import APIRouter, FastAPI

from app.api.errors import register_error_handlers
from app.api.health import router as health_router
from app.api.middleware import RequestContextMiddleware
from app.api.v1 import build_api_v1_router
from app.config import Settings
from app.shared.modules import ModuleRegistration, ModuleRegistry
from app.shared.observability import configure_logging

APP_VERSION = "0.1.0"


def create_app(
    settings: Settings | None = None,
    *,
    api_v1_routers: Sequence[APIRouter] = (),
    module_registrations: Sequence[ModuleRegistration[APIRouter]] = (),
) -> FastAPI:
    """Create an application from explicitly supplied, compile-time registrations."""
    resolved_settings = settings or Settings()
    configure_logging(resolved_settings.log_level)

    module_registry = ModuleRegistry[APIRouter]()
    for registration in module_registrations:
        module_registry.register(registration)
    module_registry.finalize()

    application = FastAPI(
        title=resolved_settings.app_name,
        version=APP_VERSION,
        debug=resolved_settings.debug,
    )
    application.state.settings = resolved_settings
    application.state.module_registry = module_registry
    application.state.capability_registry = module_registry.capability_registry

    register_error_handlers(application)
    application.add_middleware(RequestContextMiddleware)
    application.include_router(health_router)
    application.include_router(
        build_api_v1_router(
            prefix=resolved_settings.api_v1_prefix,
            module_routers=(*api_v1_routers, *module_registry.routers),
        )
    )
    return application


app = create_app()
