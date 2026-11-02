# P23-B Keyboard Intake Completion E2E Evidence

## Status

`PARTIAL` — bounded automated keyboard and focus evidence for the existing P7 structured-intake
journey only. P23 remains `PARTIAL`; this is not a human accessibility audit or WCAG conformance
claim.

## Scope and evidence

The real Playwright journey now completes the existing synthetic intake without pointer input. It
exercises Chromium, patient-web, the same-origin BFF, FastAPI, and real PostgreSQL while proving:

- keyboard activation of intake start;
- deterministic focus on the current-question heading after navigation;
- sequential keyboard movement to the answer and save controls;
- non-sensitive route titles for intake and review states;
- deterministic focus on the review heading after save and reload;
- keyboard traversal through `Review or change`, the editable question, and `Review draft`;
- keyboard completion with focus transferred to the completed-state heading; and
- keyboard private-session exit followed by focus on the language route's main landmark.

The journey retains the existing draft-only language and authoritative reload check. It introduces
no synthetic accessibility scanner result and no browser-side clinical persistence.

## Change boundary

This unit strengthens one existing synthetic full-stack journey, records bounded evidence, and
allows isolated local Playwright dev-server ports while preserving the existing CI defaults. It
changes no product runtime component, backend, API contract, schema, migration, dependency,
lockfile, service worker, feature flag, infrastructure, clinical policy, or blocked P8+ capability.

## Acceptance truth

This closes one automated keyboard-path and focus-transfer evidence gap for the existing P7
technical journey. It does not prove human keyboard usability, screen-reader interoperability,
language equivalence, kiosk suitability, all-flow conformance, accessibility certification, pilot
authorization, or release readiness. `AC-P23-008`, `AC-P23-009`, all other `AC-P23` criteria, and
`AC-PROD-001..014` remain live/product-level `NOT VERIFIED`; qualified human review remains
outstanding.
