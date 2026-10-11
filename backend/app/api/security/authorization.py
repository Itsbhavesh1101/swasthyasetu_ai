"""Server-side FastAPI guards over trusted request actor context."""

from collections.abc import Callable

from fastapi import Request

from app.modules.identity.domain import PermissionCode
from app.modules.identity.public import IDENTITY_AUTHORIZE
from app.shared.security import ActorContext
from app.shared.types import OpaqueId


def _actor_context(request: Request) -> ActorContext:
    value = getattr(request.state, "actor_context", None)
    return (
        value
        if isinstance(value, ActorContext)
        else ActorContext(request_id=getattr(request.state, "request_id", None))
    )


def require_permission(permission: PermissionCode) -> Callable[[Request], None]:
    def guard(request: Request) -> None:
        authorization = request.app.state.capability_registry.resolve(IDENTITY_AUTHORIZE)
        authorization.require_permission(_actor_context(request), permission)

    return guard


def require_self_subject(
    permission: PermissionCode, path_parameter: str
) -> Callable[[Request], None]:
    def guard(request: Request) -> None:
        authorization = request.app.state.capability_registry.resolve(IDENTITY_AUTHORIZE)
        try:
            subject_id = OpaqueId.parse(request.path_params[path_parameter])
        except (KeyError, ValueError) as error:
            from app.shared.errors import ApplicationError, ErrorCode

            raise ApplicationError(
                code=ErrorCode.AUTHORIZATION_DENIED,
                message="The authenticated actor is not permitted to access this subject.",
                cause=error,
            ) from error
        authorization.require_self_subject(_actor_context(request), permission, subject_id)

    return guard
