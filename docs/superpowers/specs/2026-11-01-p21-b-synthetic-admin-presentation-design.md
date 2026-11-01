# P21-B Synthetic Admin Presentation Design

## Decision

Add a test-only presentation fixture for six closed engineering-synthetic authorization states. Keep
the fixture below `apps/admin-web/tests/support` so no production route, component, bundle, or runtime
can import it.

## Boundary

The fixture accepts only `LOCAL` and `TEST`. Protected or unknown environments return a fixed
unavailable state before reading the requested state. Unknown or hostile state values also fail
unavailable. Presentation copy is read-only, accessible, and never claims that access, approval, or
authority was granted.

The six states are identity unavailable, MFA required, scope denied, synthetic contract match, stale
snapshot, and pending human review. They contain no real identifiers, source content, clinical data,
credentials, tokens, controls, network access, browser storage, or cookies.

## Verification

Vitest covers every state, adversarial inputs, protected-environment short-circuiting, safe copy,
absence of browser/network capabilities, and absence of production imports. Existing admin-web and
repository quality gates remain unchanged.

## Explicit exclusions

No production UI, route, navigation, BFF/API, authentication, MFA ceremony, role/grant management,
data access, audit viewer, clinical review, maker-checker workflow, persistence, migration,
dependency, or runtime activation is authorized.
