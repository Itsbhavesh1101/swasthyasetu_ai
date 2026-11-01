# P23-B Synthetic Accessibility Evidence Foundation

## Status

`PARTIAL — BOUNDED DETACHED ENGINEERING-SYNTHETIC FOUNDATION ONLY`

This unit provides metadata-integrity mechanics for a future accessibility evidence catalog. It does
not perform an accessibility audit and does not verify `AC-P23-008`, `AC-P23-009`, or any
`NFR-ACCESS-*` requirement.

## Implemented boundary

The unregistered `app.validation` package now includes a closed eight-area catalog matching the
canonical P23 assessment:

- keyboard and focus;
- semantics and announcements;
- contrast and display;
- language;
- urgent help;
- PWA and offline behavior;
- kiosk and shared-device behavior; and
- staff shells.

Immutable definitions and observations bind exact engineering versions, build SHA, configuration,
source-evidence and checklist hashes, and UTC chronology. Tamper-evident receipts can state only
`EVIDENCE_CONSISTENT` or `ABSTAINED`. Every object remains labelled `ENGINEERING_ONLY`,
`ENGINEERING_SYNTHETIC`, `UNVERIFIED`, and `HUMAN_REVIEW_REQUIRED`.

The exact eight-entry manifest is canonical and deterministic. Missing, duplicate, aliased,
misordered, malformed, drifted, stale, or forcibly mutated values fail closed. Staging, pilot, and
production reject before caller-controlled evidence is inspected.

## Explicitly not implemented

- No accessibility scanner, browser journey, human keyboard review, or assistive-technology session.
- No screen-reader/browser/device/locale/kiosk support matrix.
- No WCAG success-criterion mapping, conformance report, certification, pass, severity, finding,
  remediation, waiver, or approval.
- No review of clinical language, urgent-resource correctness, language equivalence, or staff flow.
- No patient/user content, screenshot, recording, transcript, identifier, or realistic sensitive data.
- No persistence, migration, API, BFF, UI, event, job, telemetry, dependency, network, feature flag,
  module registration, runtime activation, deployment, pilot, or release behavior.

## Verification expectations

Focused tests cover the exact catalog, strict construction, UTC normalization, immutable nested
reconstruction, deterministic fingerprints, direct-constructor forgery, manifest completeness,
protected-environment short-circuiting, metadata drift, content-free errors, representation privacy,
runtime isolation, and absence of audit or authority surfaces.

The standard backend, frontend, PostgreSQL, Docker, Playwright, and security gates remain regression
requirements. Their success proves only the checked engineering baseline.

## Outstanding accountable review

Before any real P23-B audit or acceptance claim, the repository still requires an approved
critical-flow inventory; supported AT/browser/device/locale matrix; reviewed copy; severity and
remediation rules; kiosk/shared-device policy; privacy-safe evidence handling; and qualified human
accessibility, language/content, privacy/security, institution, product, and application-owner
review.

`AC-P23-008`, `AC-P23-009`, `NFR-ACCESS-001..007`, all other live P23 criteria, and every product
acceptance outcome remain unverified. P23-C, P23-D, P24, pilot, and release work are outside this
unit.
