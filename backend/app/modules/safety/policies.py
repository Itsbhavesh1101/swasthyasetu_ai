"""Explicit, immutable and fail-closed safety policy metadata registry."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from app.config.settings import Environment

_POLICY_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_VERSION_PATTERN = re.compile(r"^[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*$")
_NAMESPACE_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*_$")
_CHECKSUM_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_ENGINEERING_ENVIRONMENTS = frozenset({Environment.LOCAL, Environment.TEST})
_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


class SafetyPolicyRegistryError(ValueError):
    """Base class for content-free safety policy registry failures."""


class InvalidPolicyMetadataError(SafetyPolicyRegistryError):
    """Raised when policy metadata is malformed or internally inconsistent."""


class DuplicatePolicyRegistrationError(SafetyPolicyRegistryError):
    """Raised when a policy identity is registered more than once."""


class AmbiguousPolicySelectionError(SafetyPolicyRegistryError):
    """Raised when selection is duplicated or cannot be resolved uniquely."""


class UnknownPolicyError(SafetyPolicyRegistryError):
    """Raised when an exact policy identity is absent."""


class PolicyUnavailableError(SafetyPolicyRegistryError):
    """Raised when no selectable policy is configured."""


class PolicyEnvironmentRejectedError(SafetyPolicyRegistryError):
    """Raised when policy selection is forbidden in the requested environment."""


class SafetyPolicyType(StrEnum):
    PHYSICAL_SAFETY = "PHYSICAL_SAFETY"


class PolicyApprovalState(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"
    CLINICAL_APPROVAL_REQUIRED = "CLINICAL_APPROVAL_REQUIRED"


class PolicyActivationState(StrEnum):
    INACTIVE = "INACTIVE"
    ENGINEERING_TEST_ONLY = "ENGINEERING_TEST_ONLY"


def _canonical_metadata_bytes(
    *,
    policy_type: SafetyPolicyType,
    policy_id: str,
    policy_version: str,
    approval_state: PolicyApprovalState,
    activation_state: PolicyActivationState,
    supported_environments: tuple[Environment, ...],
    reason_code_namespace: str,
) -> bytes:
    if (
        not isinstance(policy_type, SafetyPolicyType)
        or not isinstance(approval_state, PolicyApprovalState)
        or not isinstance(activation_state, PolicyActivationState)
        or not isinstance(supported_environments, tuple)
        or any(not isinstance(item, Environment) for item in supported_environments)
        or not isinstance(policy_id, str)
        or not isinstance(policy_version, str)
        or not isinstance(reason_code_namespace, str)
    ):
        raise InvalidPolicyMetadataError("invalid canonical policy metadata")
    payload = {
        "activation_state": activation_state.value,
        "approval_state": approval_state.value,
        "policy_id": policy_id,
        "policy_type": policy_type.value,
        "policy_version": policy_version,
        "reason_code_namespace": reason_code_namespace,
        "supported_environments": [item.value for item in supported_environments],
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


@dataclass(frozen=True, slots=True, kw_only=True)
class SafetyPolicyMetadata:
    """Auditable policy metadata, never a clinical approval credential.

    ``metadata_checksum`` attests only to this canonical metadata record. It is
    neither a signature nor evidence of clinical review.
    """

    policy_type: SafetyPolicyType
    policy_id: str
    policy_version: str
    approval_state: PolicyApprovalState
    activation_state: PolicyActivationState
    supported_environments: tuple[Environment, ...]
    reason_code_namespace: str
    metadata_checksum: str

    def __post_init__(self) -> None:
        if not isinstance(self.policy_type, SafetyPolicyType):
            raise InvalidPolicyMetadataError("invalid policy type")
        if not isinstance(self.policy_id, str) or not 1 <= len(self.policy_id) <= 128:
            raise InvalidPolicyMetadataError("invalid policy ID")
        if _POLICY_ID_PATTERN.fullmatch(self.policy_id) is None:
            raise InvalidPolicyMetadataError("invalid policy ID")
        if not isinstance(self.policy_version, str) or not 1 <= len(self.policy_version) <= 64:
            raise InvalidPolicyMetadataError("invalid policy version")
        if _VERSION_PATTERN.fullmatch(self.policy_version) is None:
            raise InvalidPolicyMetadataError("invalid policy version")
        if not isinstance(self.approval_state, PolicyApprovalState):
            raise InvalidPolicyMetadataError("invalid approval state")
        if not isinstance(self.activation_state, PolicyActivationState):
            raise InvalidPolicyMetadataError("invalid activation state")
        if not isinstance(self.supported_environments, tuple) or any(
            not isinstance(item, Environment) for item in self.supported_environments
        ):
            raise InvalidPolicyMetadataError("invalid supported environments")
        if len(set(self.supported_environments)) != len(self.supported_environments):
            raise InvalidPolicyMetadataError("duplicate supported environments")
        if self.supported_environments != tuple(
            sorted(self.supported_environments, key=lambda item: item.value)
        ):
            raise InvalidPolicyMetadataError("supported environments must be ordered")
        if (
            not isinstance(self.reason_code_namespace, str)
            or len(self.reason_code_namespace) > 32
            or _NAMESPACE_PATTERN.fullmatch(self.reason_code_namespace) is None
        ):
            raise InvalidPolicyMetadataError("invalid reason-code namespace")
        if (
            not isinstance(self.metadata_checksum, str)
            or _CHECKSUM_PATTERN.fullmatch(self.metadata_checksum) is None
        ):
            raise InvalidPolicyMetadataError("invalid metadata checksum")

        environments = frozenset(self.supported_environments)
        if self.activation_state is PolicyActivationState.INACTIVE:
            if environments:
                raise InvalidPolicyMetadataError("inactive policy cannot support environments")
        elif (
            self.approval_state is not PolicyApprovalState.ENGINEERING_ONLY
            or not environments
            or not environments <= _ENGINEERING_ENVIRONMENTS
        ):
            raise InvalidPolicyMetadataError("engineering policy environment is invalid")

        expected = self.compute_checksum(
            policy_type=self.policy_type,
            policy_id=self.policy_id,
            policy_version=self.policy_version,
            approval_state=self.approval_state,
            activation_state=self.activation_state,
            supported_environments=self.supported_environments,
            reason_code_namespace=self.reason_code_namespace,
        )
        if self.metadata_checksum != expected:
            raise InvalidPolicyMetadataError("metadata checksum mismatch")

    @staticmethod
    def compute_checksum(
        *,
        policy_type: SafetyPolicyType,
        policy_id: str,
        policy_version: str,
        approval_state: PolicyApprovalState,
        activation_state: PolicyActivationState,
        supported_environments: tuple[Environment, ...],
        reason_code_namespace: str,
    ) -> str:
        return hashlib.sha256(
            _canonical_metadata_bytes(
                policy_type=policy_type,
                policy_id=policy_id,
                policy_version=policy_version,
                approval_state=approval_state,
                activation_state=activation_state,
                supported_environments=supported_environments,
                reason_code_namespace=reason_code_namespace,
            )
        ).hexdigest()

    @classmethod
    def create(
        cls,
        *,
        policy_type: SafetyPolicyType,
        policy_id: str,
        policy_version: str,
        approval_state: PolicyApprovalState,
        activation_state: PolicyActivationState,
        supported_environments: tuple[Environment, ...],
        reason_code_namespace: str,
    ) -> SafetyPolicyMetadata:
        checksum = cls.compute_checksum(
            policy_type=policy_type,
            policy_id=policy_id,
            policy_version=policy_version,
            approval_state=approval_state,
            activation_state=activation_state,
            supported_environments=supported_environments,
            reason_code_namespace=reason_code_namespace,
        )
        return cls(
            policy_type=policy_type,
            policy_id=policy_id,
            policy_version=policy_version,
            approval_state=approval_state,
            activation_state=activation_state,
            supported_environments=supported_environments,
            reason_code_namespace=reason_code_namespace,
            metadata_checksum=checksum,
        )

    @property
    def identity(self) -> tuple[str, str]:
        return (self.policy_id, self.policy_version)


@dataclass(frozen=True, slots=True, kw_only=True)
class ActivePolicySelection:
    policy_type: SafetyPolicyType
    policy_id: str
    policy_version: str

    def __post_init__(self) -> None:
        if not isinstance(self.policy_type, SafetyPolicyType):
            raise InvalidPolicyMetadataError("invalid policy type")
        if (
            not isinstance(self.policy_id, str)
            or _POLICY_ID_PATTERN.fullmatch(self.policy_id) is None
        ):
            raise InvalidPolicyMetadataError("invalid policy ID")
        if (
            not isinstance(self.policy_version, str)
            or _VERSION_PATTERN.fullmatch(self.policy_version) is None
        ):
            raise InvalidPolicyMetadataError("invalid policy version")


@dataclass(frozen=True, slots=True, init=False)
class SafetyPolicyRegistry:
    """Immutable explicit registry; it contains metadata, not a policy engine."""

    _policies: Mapping[tuple[str, str], SafetyPolicyMetadata]
    _selections: Mapping[SafetyPolicyType, SafetyPolicyMetadata]

    def __init__(
        self,
        *,
        policies: tuple[SafetyPolicyMetadata, ...] = (),
        selections: tuple[ActivePolicySelection, ...] = (),
    ) -> None:
        if not isinstance(policies, tuple) or any(
            not isinstance(item, SafetyPolicyMetadata) for item in policies
        ):
            raise InvalidPolicyMetadataError("invalid policy registrations")
        if not isinstance(selections, tuple) or any(
            not isinstance(item, ActivePolicySelection) for item in selections
        ):
            raise InvalidPolicyMetadataError("invalid policy selections")

        registrations: dict[tuple[str, str], SafetyPolicyMetadata] = {}
        for policy in policies:
            SafetyPolicyMetadata(
                policy_type=policy.policy_type,
                policy_id=policy.policy_id,
                policy_version=policy.policy_version,
                approval_state=policy.approval_state,
                activation_state=policy.activation_state,
                supported_environments=policy.supported_environments,
                reason_code_namespace=policy.reason_code_namespace,
                metadata_checksum=policy.metadata_checksum,
            )
            if policy.identity in registrations:
                raise DuplicatePolicyRegistrationError("duplicate policy registration")
            registrations[policy.identity] = policy

        selected: dict[SafetyPolicyType, SafetyPolicyMetadata] = {}
        for selection in selections:
            if selection.policy_type in selected:
                raise AmbiguousPolicySelectionError("duplicate active policy selection")
            policy = registrations.get((selection.policy_id, selection.policy_version))
            if policy is None or policy.policy_type is not selection.policy_type:
                raise UnknownPolicyError("unknown policy selection")
            if policy.activation_state is PolicyActivationState.INACTIVE:
                raise PolicyUnavailableError("selected policy is inactive")
            selected[selection.policy_type] = policy

        ordered_registrations = dict(sorted(registrations.items()))
        object.__setattr__(
            self,
            "_policies",
            MappingProxyType(ordered_registrations),
        )
        object.__setattr__(
            self,
            "_selections",
            MappingProxyType(dict(sorted(selected.items(), key=lambda item: item[0].value))),
        )

    def all(self) -> tuple[SafetyPolicyMetadata, ...]:
        return tuple(self._policies.values())

    def require(self, *, policy_id: str, policy_version: str) -> SafetyPolicyMetadata:
        try:
            return self._policies[(policy_id, policy_version)]
        except KeyError as exc:
            raise UnknownPolicyError("unknown policy identity") from exc

    def get_active_policy(
        self, *, policy_type: SafetyPolicyType, environment: Environment
    ) -> SafetyPolicyMetadata:
        if not isinstance(policy_type, SafetyPolicyType):
            raise InvalidPolicyMetadataError("invalid policy type")
        if not isinstance(environment, Environment):
            raise InvalidPolicyMetadataError("invalid environment")
        policy = self._selections.get(policy_type)
        if policy is None:
            raise PolicyUnavailableError("active policy is unavailable")
        if environment in _PROTECTED_ENVIRONMENTS:
            raise PolicyEnvironmentRejectedError("policy rejected in protected environment")
        if (
            policy.approval_state is not PolicyApprovalState.ENGINEERING_ONLY
            or policy.activation_state is not PolicyActivationState.ENGINEERING_TEST_ONLY
            or environment not in policy.supported_environments
        ):
            raise PolicyEnvironmentRejectedError("policy rejected in environment")
        return policy


SYNTHETIC_PHYSICAL_SAFETY_METADATA = SafetyPolicyMetadata.create(
    policy_type=SafetyPolicyType.PHYSICAL_SAFETY,
    policy_id="synthetic-physical-safety-metadata",
    policy_version="engineering.1",
    approval_state=PolicyApprovalState.ENGINEERING_ONLY,
    activation_state=PolicyActivationState.ENGINEERING_TEST_ONLY,
    supported_environments=(Environment.LOCAL, Environment.TEST),
    reason_code_namespace="SYNTHETIC_",
)


def build_default_policy_registry() -> SafetyPolicyRegistry:
    """Build the production-safe default: no registration and no selection."""

    return SafetyPolicyRegistry()


def build_synthetic_policy_registry() -> SafetyPolicyRegistry:
    """Build an explicitly selected metadata-only local/test fixture registry."""

    return SafetyPolicyRegistry(
        policies=(SYNTHETIC_PHYSICAL_SAFETY_METADATA,),
        selections=(
            ActivePolicySelection(
                policy_type=SafetyPolicyType.PHYSICAL_SAFETY,
                policy_id=SYNTHETIC_PHYSICAL_SAFETY_METADATA.policy_id,
                policy_version=SYNTHETIC_PHYSICAL_SAFETY_METADATA.policy_version,
            ),
        ),
    )
