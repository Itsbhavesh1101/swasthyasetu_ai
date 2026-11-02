# Wave 8 Synthetic ABDM Boundary Preview Design

## Intent

Give the college demonstration a working, truthful view of the already implemented P17-A/B/D
engineering boundaries without creating an official ABDM, ABHA, sandbox, exchange, or patient-data
path.

## Goals

- Compose the closed P17-A request/result contracts through a deterministic zero-egress adapter.
- Show one scripted rejection and one unknown-request unavailable result.
- Preserve strict local/test-only, default-off registration and fail closed in protected environments.
- Present an accessible, input-free, non-actionable patient-web preview with exact negative claims.
- Keep the existing PostgreSQL P17-D tests as the independent evidence that detached failures do not
  damage committed P7 intake data.

## Non-goals and anti-goals

No official protocol names, ABHA identifiers, identity/linkage, consent semantics, FHIR payloads,
callbacks, sandbox, credentials, network traffic, retries, import/export, persistence, migrations,
new dependencies, production activation, or conformance claims. The preview must not show an
accepted result because that could be mistaken for official exchange success.

## Approach

The selected approach follows the existing Wave 5-7 engineering-demo pattern: a separate backend
module owns a fixed content-free request, a private deterministic adapter implementing the existing
provider-neutral port, and a minimized literal response. A strict same-origin BFF validates every
field and rejects added fields or stronger claims. The page has no inputs or external/action links.

Alternatives rejected:

1. Import the test-support mock into runtime code: rejected because production modules must not
   depend on the test package.
2. Add a database-backed demo: rejected because P17-D already proves failure isolation and runtime
   persistence would expand scope without adding a truthful user-facing capability.
3. Add a sandbox or HTTP adapter: rejected because official sources, roles, credentials, consent,
   security, and release approvals remain unresolved.

## Verification

Test direct service behavior, protected-environment denial, default-off registration, strict
transport parsing, hostile authority/effect mutations, accessible no-action UI, and a real browser
journey. Run the complete backend/frontend quality suites, production builds, migration-head check,
all six GitHub CI jobs, and post-merge `main` CI.
