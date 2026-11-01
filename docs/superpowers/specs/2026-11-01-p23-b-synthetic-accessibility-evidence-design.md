# P23-B Synthetic Accessibility Evidence Design

## Intent

Create the smallest safe P23-B engineering foundation for cataloguing accessibility evidence
metadata without performing or claiming a human accessibility audit. The foundation is detached,
synthetic, and content-free. It does not certify WCAG conformance, review clinical copy, establish a
supported assistive-technology matrix, or approve any live workflow.

## Canonical scope

The closed catalog contains the eight areas in the P23 readiness assessment:

1. keyboard and focus;
2. semantics and announcements;
3. contrast and display;
4. language;
5. urgent help;
6. PWA and offline behavior;
7. kiosk and shared-device behavior; and
8. staff shells.

Every entry is permanently labelled `ENGINEERING_ONLY`, `ENGINEERING_SYNTHETIC`, `UNVERIFIED`, and
`HUMAN_REVIEW_REQUIRED`. A matching observation proves only that content-free metadata is internally
consistent for an exact build and checklist. It cannot represent a pass, finding disposition, audit
result, clinical review, or conformance claim.

## Architecture

`backend/app/validation/accessibility.py` owns strict immutable definitions, observations, receipts,
manifests, canonical fingerprints, UTC normalization, snapshot reconstruction, and two pure
operations: canonical manifest construction and metadata evaluation.

The implementation remains in the unregistered `app.validation` package. It exposes no route,
module capability, persistence, migration, job, event, browser runner, network access, or UI.
`LOCAL` and `TEST` are the only permitted environments; protected environments reject before
caller-controlled input is inspected.

## Integrity rules

- Definitions bind an exact engineering version, build SHA, configuration hash, source-evidence hash,
  checklist hash, area, and UTC creation time.
- Observations bind the same metadata plus the definition fingerprint and UTC capture time.
- Receipts reconstruct their nested values and derive only `EVIDENCE_CONSISTENT` or `ABSTAINED`.
- Manifests contain exactly one canonically ordered definition for each of the eight areas.
- Direct-constructor forgery, aliases, missing/duplicate areas, hash drift, chronology errors, naive
  clocks, and forced mutation fail closed with stable content-free errors.
- Hashes and nested evidence are suppressed from representations.

## Explicit non-goals

- No automated accessibility tool or browser execution.
- No human keyboard, screen-reader, zoom, contrast, forced-colors, language, kiosk, or shared-device
  audit.
- No WCAG success-criterion mapping or conformance/certification statement.
- No clinical content, emergency-resource correctness, supported locale, AT/browser/device matrix,
  severity rule, remediation decision, or reviewer identity/signature.
- No change to P6/P7 behavior, service workers, application code, dependencies, CI, or deployment.

## Verification

Tests cover the exact eight-area inventory, strict types, immutable reconstruction, UTC behavior,
deterministic fingerprints, direct-constructor consistency, manifest completeness/order, protected
environment short-circuiting, drift abstention, content-free errors, representation privacy, runtime
isolation, and absence of audit/approval surfaces. All existing quality and six CI jobs remain
required.

## Governance outcome

This is bounded engineering metadata infrastructure only. `AC-P23-008`, `AC-P23-009`, and
`NFR-ACCESS-001..007` remain live-unverified. P23 remains partial. Qualified human accessibility,
language/content, privacy/security, institution/kiosk, product, and application-owner review remains
mandatory before any audit result or conformance statement.
