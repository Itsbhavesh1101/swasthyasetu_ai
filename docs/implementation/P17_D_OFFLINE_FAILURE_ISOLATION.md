# P17-D Offline Failure-Isolation Evidence

## Status

PARTIAL — bounded engineering-only PostgreSQL evidence. P17 remains PARTIAL, P17-C remains blocked,
and every live P17 acceptance criterion remains unverified.

## Baseline and scope

This unit starts from merged `main` at
`42314e0547181cddeecc74de272e75d55d76d2b4`. It adds tests only: no production code, migration,
dependency, API, BFF, UI, configuration, feature flag, network path, retry, callback, consent,
reconciliation, or runtime activation is introduced.

The test data is synthetic and content-free. A minimal P7 intake and a skipped answer are persisted
through the real PostgreSQL repositories in a completed local transaction. Only after that
transaction commits does the detached P17-B test adapter return a synthetic rejection or
unavailability result, or raise a sanitized clock failure.

## Evidence

Each failure case:

1. commits the P7 intake and skipped answer before invoking the adapter;
2. invokes the zero-egress adapter outside the database transaction;
3. reloads both records through a fresh database session and checks exact equality;
4. completes the same intake in a new transaction; and
5. reloads it again to prove the local record remains writable and its answer remains unchanged.

This is narrow evidence toward the local-preservation intent of `FR-ABDM-005`. It proves that the
tested detached failure outcomes do not roll back, erase, or block already committed P7 data.

## Explicit non-claims

This evidence does not implement or verify an official ABDM operation, remote transaction,
ambiguous remote outcome, delivery guarantee, retry or reconciliation policy, idempotent remote
submission, callback processing, exchange consent, clinical-data exchange, import/export
provenance, sandbox conformance, or production resilience. It therefore does not satisfy
`AC-P17-005` or any other live `AC-P17-*` criterion. `FR-ABDM-001..007` and
`AC-P17-001..007` remain LIVE NOT VERIFIED.

## Next action

Keep P17-C blocked until accountable decisions and current official sources authorize live
synchronization semantics. Review this tests-only evidence independently before relying on it as a
foundation for any later approved integration design.
