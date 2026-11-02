# P23-B Intake Error Accessibility E2E Evidence

## Status

`PARTIAL` — bounded automated accessibility evidence for the existing P7 structured-intake failure
path only. P23 remains `PARTIAL`; this is not a human accessibility audit or a WCAG conformance
claim.

## Scope and evidence

The answer-control contract now associates an active mutation error with every supported control
shape through `aria-invalid` and `aria-describedby`. Existing question help and the active error are
both retained in the description relationship. Grouped radio, checkbox, boolean, and scale controls
carry the relationship on their fieldset; direct text, number, date, and duration controls carry it
on the input.

Eight component-test cases cover every closed answer type. The existing real Chromium, patient-web
BFF, FastAPI, and PostgreSQL save-failure journey additionally proves that:

- start, answer entry, submission, and explicit retry are keyboard operated;
- the failed request is announced by an alert and focus moves deterministically to the question
  heading;
- the still-editable answer is marked invalid and described by both help and error text;
- the unsent value remains available for correction without being reported as saved;
- the dynamic intake failure state has no page-level horizontal overflow at 320 CSS pixels; and
- only a later explicit retry writes the authoritative answer.

## Change boundary

The correction is limited to answer-control accessibility metadata, focused component regression
tests, the existing synthetic full-stack save-failure journey, and project evidence. There is no
backend, API contract, schema, migration, dependency, lockfile, service worker, feature flag,
clinical policy, or blocked P8+ capability change.

## Acceptance truth

This closes one automated error-association and narrow-screen evidence gap for the existing P7
technical journey. It does not prove screen-reader interoperability, human keyboard usability,
language equivalence, kiosk suitability, all-flow conformance, accessibility certification, pilot
authorization, or release readiness. `AC-P23-008`, `AC-P23-009`, all other `AC-P23` criteria, and
`AC-PROD-001..014` remain live/product-level `NOT VERIFIED`; qualified human review remains
outstanding.
