"""Immutable, deny-by-default P4-B authorization policy."""

from types import MappingProxyType
from typing import Final

from app.modules.identity.domain import PermissionCode, RoleCode
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.security import ActorContext
from app.shared.types import OpaqueId

PATIENT_READ_SELF = PermissionCode("patient:read:self")
PATIENT_WRITE_SELF = PermissionCode("patient:write:self")
ENCOUNTER_READ_SELF = PermissionCode("encounter:read:self")
ENCOUNTER_WRITE_SELF = PermissionCode("encounter:write:self")
ENCOUNTER_READ_ASSIGNED = PermissionCode("encounter:read:assigned")
SUMMARY_CONFIRM = PermissionCode("summary:confirm")
PROVIDER_MANAGE = PermissionCode("provider:manage")
POLICY_REVIEW = PermissionCode("policy:review")
RESEARCH_RUN = PermissionCode("research:run")
AUDIT_READ = PermissionCode("audit:read")
AUTHORIZATION_POLICY_VERSION: Final = "p5c-v1"

_ROLE_PERMISSIONS = MappingProxyType(
    {
        RoleCode.PATIENT: frozenset(
            {PATIENT_READ_SELF, PATIENT_WRITE_SELF, ENCOUNTER_READ_SELF, ENCOUNTER_WRITE_SELF}
        ),
        RoleCode.PSEUDONYMOUS_USER: frozenset(),
        RoleCode.CLINICIAN: frozenset({ENCOUNTER_READ_ASSIGNED, SUMMARY_CONFIRM}),
        RoleCode.RESOURCE_ADMIN: frozenset({PROVIDER_MANAGE}),
        RoleCode.CLINICAL_REVIEWER: frozenset({POLICY_REVIEW}),
        RoleCode.RESEARCHER: frozenset({RESEARCH_RUN}),
        RoleCode.SYSTEM_ADMIN: frozenset({PROVIDER_MANAGE, POLICY_REVIEW, AUDIT_READ}),
    }
)
_ADMINISTRATIVE_ROLES = frozenset(
    {RoleCode.RESOURCE_ADMIN, RoleCode.CLINICAL_REVIEWER, RoleCode.SYSTEM_ADMIN}
)


class AuthorizationService:
    """Authorize a trusted ActorContext without database or transport coupling."""

    policy_version = AUTHORIZATION_POLICY_VERSION
    role_permissions = _ROLE_PERMISSIONS

    def has_permission(self, actor_context: ActorContext, permission: PermissionCode) -> bool:
        if not actor_context.is_authenticated:
            return False
        roles = {role for value in actor_context.roles if (role := _parse_role(value)) is not None}
        if roles & _ADMINISTRATIVE_ROLES and not actor_context.mfa_verified:
            return False
        return any(permission in _ROLE_PERMISSIONS[role] for role in roles)

    def require_permission(self, actor_context: ActorContext, permission: PermissionCode) -> None:
        if not actor_context.is_authenticated:
            raise ApplicationError(
                code=ErrorCode.AUTHENTICATION_REQUIRED,
                message="A valid authenticated actor is required.",
            )
        if not self.has_permission(actor_context, permission):
            raise ApplicationError(
                code=ErrorCode.AUTHORIZATION_DENIED,
                message="The authenticated actor is not permitted to perform this action.",
            )

    def require_self_subject(
        self, actor_context: ActorContext, permission: PermissionCode, subject_id: OpaqueId
    ) -> None:
        self.require_permission(actor_context, permission)
        if actor_context.subject_id is None or actor_context.subject_id != subject_id:
            raise ApplicationError(
                code=ErrorCode.AUTHORIZATION_DENIED,
                message="The authenticated actor is not permitted to access this subject.",
            )


def _parse_role(value: str) -> RoleCode | None:
    try:
        return RoleCode(value)
    except ValueError:
        return None
