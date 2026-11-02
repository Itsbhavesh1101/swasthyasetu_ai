"""Deterministic, content-free P13 engineering demonstration."""

from dataclasses import dataclass
from datetime import UTC, datetime

from app.modules.providers.domain import SyntheticProviderRecord, SyntheticSourceEvidence
from app.modules.providers.routing import (
    SymbolicRoutingRequest,
    SymbolicRoutingRule,
    SyntheticRoutingPolicy,
    evaluate_symbolic_route,
)
from app.modules.referrals.domain import SyntheticReferral, SyntheticReferralStatus
from app.modules.resources.domain import SyntheticCareResourceRecord


@dataclass(frozen=True, slots=True)
class EngineeringReferralDiscoveryResult:
    classification: str
    authority: str
    route_disposition: str
    route_reason: str
    service_code: str
    provider_display_name: str
    provider_service_code: str
    provider_verification: str
    resource_display_name: str
    resource_code: str
    resource_verification: str
    source_verification: str
    contacts_available: bool
    provider_selected: bool
    referral_state_model: str
    referral_created: bool
    sharing_consent: str
    external_delivery: bool
    notification_delivery: bool
    notice: str


class EngineeringReferralDemoService:
    """Compose reviewed P13 mechanics without lookup, sharing, or external effects."""

    def project(self, *, clock: datetime | None = None) -> EngineeringReferralDiscoveryResult:
        now = clock or datetime.now(UTC)
        source = SyntheticSourceEvidence(
            source_id="syn_source_college_demo",
            source_version="v1",
            artifact_hash="a" * 64,
            acquired_at=now,
        )
        provider = SyntheticProviderRecord(
            record_id="syn_provider_college_demo",
            record_version=1,
            display_name="Synthetic College Demo Provider",
            service_code="syn_service_college_demo",
            source=source,
            created_at=now,
        )
        resource = SyntheticCareResourceRecord(
            record_id="syn_resource_college_demo",
            record_version=1,
            display_name="Synthetic College Demo Resource",
            resource_code="syn_resource_type_college_demo",
            source=source,
            created_at=now,
        )
        routing = evaluate_symbolic_route(
            SymbolicRoutingRequest(
                request_id="syn_route_request_college_demo",
                signal_code="syn_signal_college_demo",
                created_at=now,
            ),
            SyntheticRoutingPolicy(
                policy_id="syn_route_policy_college_demo",
                policy_version="v1",
                artifact_hash="b" * 64,
                rules=(
                    SymbolicRoutingRule(
                        rule_id="syn_route_rule_college_demo",
                        signal_code="syn_signal_college_demo",
                        service_code="syn_service_college_demo",
                        order=1,
                    ),
                ),
                activated_at=now,
            ),
            evaluated_at=now,
        )
        referral = SyntheticReferral(
            referral_id="syn_referral_college_demo",
            version=1,
            status=SyntheticReferralStatus.OFFERED,
            created_at=now,
            updated_at=now,
        )
        return EngineeringReferralDiscoveryResult(
            classification=provider.classification.value,
            authority=provider.authority.value,
            route_disposition=routing.disposition.value,
            route_reason=routing.reason.value,
            service_code=routing.service_code or "",
            provider_display_name=provider.display_name,
            provider_service_code=provider.service_code,
            provider_verification=provider.verification.value,
            resource_display_name=resource.display_name,
            resource_code=resource.resource_code,
            resource_verification=resource.verification.value,
            source_verification=source.verification.value,
            contacts_available=False,
            provider_selected=False,
            referral_state_model=referral.status.value,
            referral_created=False,
            sharing_consent="NOT_REQUESTED",
            external_delivery=False,
            notification_delivery=False,
            notice=(
                "Synthetic engineering preview only. Directory records are unverified, no provider "
                "is selected, no referral is created, and no data is shared or delivered."
            ),
        )
