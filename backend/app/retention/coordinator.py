"""Explicit, manually invoked provider-neutral purge coordinator."""

from __future__ import annotations

from collections.abc import Sequence
from contextlib import suppress

from app.retention.contracts import (
    PurgeAuthorizationDecision,
    PurgeObserver,
    PurgePlan,
    PurgeRunResult,
    PurgeRunStatus,
    PurgeTargetAdapter,
    PurgeTargetKind,
    PurgeTargetOutcome,
    PurgeTargetReceipt,
)


class PurgeCoordinator:
    """Execute an already-authorized plan without deriving policy or scheduling work."""

    def __init__(
        self,
        *,
        adapters: Sequence[PurgeTargetAdapter],
        observer: PurgeObserver | None = None,
    ) -> None:
        by_kind = {}
        for adapter in adapters:
            kind = getattr(adapter, "kind", None)
            if not isinstance(kind, PurgeTargetKind):
                raise TypeError("purge adapter kind must be a PurgeTargetKind")
            if kind in by_kind:
                raise ValueError("purge adapters must have unique target kinds")
            by_kind[kind] = adapter
        self._adapters = by_kind
        self._observer = observer

    async def execute(self, plan: PurgePlan) -> PurgeRunResult:
        """Execute every target independently and report partial failure honestly."""
        if not isinstance(plan, PurgePlan):
            raise TypeError("plan must be a PurgePlan")
        if plan.authorization.decision is not PurgeAuthorizationDecision.AUTHORIZED:
            return PurgeRunResult(
                plan_id=plan.plan_id,
                status=PurgeRunStatus.BLOCKED,
                receipts=(),
            )

        receipts: list[PurgeTargetReceipt] = []
        for target in plan.targets:
            adapter = self._adapters.get(target.identity.kind)
            if adapter is None:
                receipt = PurgeTargetReceipt(
                    target=target,
                    outcome=PurgeTargetOutcome.FAILED,
                    error_code="PURGE_ADAPTER_UNAVAILABLE",
                )
            else:
                try:
                    candidate = await adapter.purge(target)
                    if candidate.target != target:
                        receipt = PurgeTargetReceipt(
                            target=target,
                            outcome=PurgeTargetOutcome.FAILED,
                            error_code="PURGE_RECEIPT_INVALID",
                        )
                    else:
                        receipt = candidate
                except Exception:
                    receipt = PurgeTargetReceipt(
                        target=target,
                        outcome=PurgeTargetOutcome.FAILED,
                        error_code="PURGE_TARGET_FAILED",
                    )
            receipts.append(receipt)
            if self._observer is not None:
                with suppress(Exception):
                    self._observer.record(receipt)

        failed_count = sum(item.outcome is PurgeTargetOutcome.FAILED for item in receipts)
        if failed_count == 0:
            status = PurgeRunStatus.COMPLETED
        elif failed_count == len(receipts):
            status = PurgeRunStatus.FAILED
        else:
            status = PurgeRunStatus.PARTIAL_FAILURE
        return PurgeRunResult(plan_id=plan.plan_id, status=status, receipts=tuple(receipts))
