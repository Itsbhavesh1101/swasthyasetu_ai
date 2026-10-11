# Codex Phase Prompt — P4-B Identity & Authorization Baseline

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P4-B`
**Phase unit:** P4-B — Identity & Authorization Baseline
**Base branch:** `main`
**Expected base commit:** `bb9a0522f13bbfb496d74d99a1655bc9d5117e58`
**Implementation branch:** `phase/p4-b-identity-authorization`
**Commit message:** `feat: establish P4-B identity authorization baseline`
**Expected final status:** `COMPLETE`, `PARTIAL`, `BLOCKED`, or `FAILED`

---

# 0. Mission

Continue P4 — Identity, Sessions, Authorization Baseline and Consent.

Merged state:

```text
P4-A — Sessions                         COMPLETE
P4-B — Identity & Authorization         NEXT
P4-C — Consent                          NOT STARTED
P4 overall                              PARTIAL
```

P4-B must implement only the identity/authorization baseline needed by later patient, clinician,
admin, research, and consent modules.

Implement:

```text
canonical Actor domain
canonical ActorType
explicit ActorStatus
initial RoleCode model
extensible PermissionCode model
actors persistence
actor_roles persistence
P4-A sessions.actor_id -> actors.id referential integrity
provider-neutral AuthenticationProvider contract
redacted authentication credential contract
authenticated-principal contract
identity application service
safe ActorContext enrichment
identity.current_actor capability
identity.authenticate capability
identity.authorize capability
deny-by-default authorization service
explicit role -> permission policy
administrative MFA authorization gate
server-side FastAPI permission guard
self-subject authorization primitive
basic IDOR/cross-subject tests
explicit identity module registration
Alembic migration
real PostgreSQL tests
synthetic privileged-route enforcement tests
documentation and P4 acceptance update
```

Do NOT implement:

```text
Keycloak
authentik
ZITADEL
Ory
real OIDC/OAuth provider
JWT verification
JWKS fetching
login endpoint
logout endpoint
password authentication
OTP
magic links
MFA enrollment/challenge
admin UI
identity-management HTTP APIs
actor-management HTTP APIs
role-management HTTP APIs
patient table
consent table
patient API
clinician API
admin API
ABHA/ABDM identity
caregiver delegation
audit module
P4-C consent
P5 patient domain
frontend authentication
cookies
Redis/Valkey session cache
```

P4-B establishes contracts, persistence, actor context, and authorization enforcement.

A real authenticated IdP remains behind a provider port and must undergo the already-required
technical spike before production activation.

---

# 1. Mandatory Preflight

From repository root:

```text
git rev-parse --show-toplevel
git branch --show-current
git status --short
git rev-parse HEAD
git remote -v
git log --oneline --decorate -12
```

Expected:

```text
branch: main
HEAD: bb9a0522f13bbfb496d74d99a1655bc9d5117e58
working tree: clean
```

Verify merged P4-A assets exist:

```text
backend/app/modules/sessions/
backend/migrations/versions/0003_sessions.py
docs/codex/CODEX_PHASE_PROMPTS/P4_A_SESSIONS.md
```

Verify P4-A migration head:

```text
p4a_0003
```

Verify tracker records:

```text
P4-A = COMPLETE
P4 = PARTIAL
next = P4-B — Identity & Authorization Baseline
```

If the branch/base differs only through the approved P4-A merge, inspect the history and report the
actual clean base SHA.

If unrelated local changes exist, stop rather than overwrite them.

---

# 2. Create Phase Branch

Create:

```text
git switch -c phase/p4-b-identity-authorization
```

If the branch already exists:

1. inspect history;
2. compare to `main`;
3. preserve legitimate work;
4. continue only if clearly intended for P4-B.

Do not work directly on `main`.

Do not merge.

---

# 3. Required Reading

Read before editing:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md
docs/05_DATABASE_SCHEMA.md
docs/06_API_CONTRACTS.md
docs/29_ENGINEERING_STANDARDS.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md

docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md

docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md

docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_ARCHITECTURE_RECONCILIATION.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md

docs/codex/CODEX_PHASE_PROMPTS/P4_A_SESSIONS.md
```

Inspect actual code:

```text
backend/app/main.py
backend/app/modules/sessions/
backend/app/modules/identity/
backend/app/shared/security/
backend/app/shared/modules/
backend/app/shared/capabilities/
backend/app/shared/errors/
backend/app/shared/persistence/
backend/app/api/
backend/app/config/
backend/tests/
backend/migrations/
.github/workflows/ci.yml
```

Do not code from remembered assumptions.

---

# 4. Canonical P4-B Acceptance Targets

P4-B directly targets:

```text
AC-P4-005 — Base actor context and role model exist.
AC-P4-006 — Backend authorization is enforced for privileged routes.
AC-P4-010 — Cross-subject access tests prevent basic IDOR.
```

P4-A already established:

```text
AC-P4-001
AC-P4-002
AC-P4-003
AC-P4-004
```

P4-C owns:

```text
AC-P4-007
AC-P4-008
AC-P4-009
```

Expected after successful P4-B:

```text
AC-P4-001 PASS
AC-P4-002 PASS
AC-P4-003 PASS
AC-P4-004 PASS
AC-P4-005 PASS
AC-P4-006 PASS
AC-P4-007 NOT YET IMPLEMENTED
AC-P4-008 NOT YET IMPLEMENTED
AC-P4-009 NOT YET IMPLEMENTED
AC-P4-010 PASS

P4-B = COMPLETE
P4 = PARTIAL
next = P4-C — Consent Domain & APIs
```

---

# 5. Governing Identity Architecture

Canonical architecture states:

```text
Authentication determines who the actor is.
Authorization determines what the actor may do.
```

Identity module responsibilities include:

```text
authenticated identities
pseudonymous identity
clinician/admin/service actor identity
actor context
identity-provider adapters
```

Canonical example capabilities:

```text
identity.current_actor
identity.authenticate
identity.resolve_patient_identity
```

P4-B implements:

```text
identity.current_actor
identity.authenticate
identity.authorize
```

Do NOT implement `identity.resolve_patient_identity` until the P5 patient domain exists.

Do not create a fake patient identity resolver.

---

# 6. R3 Identity Decision

R3 states:

```text
SwasthyaSetu-owned pseudonymous sessions — ADOPT
Keycloak — preferred authenticated IdP target, technical spike before activation
alternatives: authentik, ZITADEL, deployment-managed OIDC
SwasthyaSetu owns resource authorization regardless of IdP
```

Therefore P4-B MUST:

```text
own authorization internally
define provider-neutral authentication contracts
keep external IdP replaceable
```

P4-B MUST NOT:

```text
activate Keycloak
add Keycloak Compose
add an OIDC dependency
pretend a synthetic provider is production authentication
```

The external provider remains unconfigured by default.

---

# 7. Administrative MFA Boundary

`NFR-SEC-003` requires:

```text
Administrative accounts SHALL require MFA.
```

P4-B does not implement an MFA challenge or IdP.

It MUST establish the backend authorization invariant that administrative actor contexts cannot
exercise privileged permissions unless the trusted authentication principal indicates MFA was
satisfied.

Administrative baseline roles:

```text
resource_admin
clinical_reviewer
system_admin
```

For those roles:

```text
authenticated + permission + mfa_verified=True -> may authorize
authenticated + permission + mfa_verified=False -> deny
```

Do not trust an HTTP header supplied directly by the client as MFA evidence.

`mfa_verified` may only enter `ActorContext` from a trusted `AuthenticatedPrincipal` produced by an
`AuthenticationProvider`.

Document:

```text
policy gate implemented
real MFA enforcement/claims mapping still depends on the selected production IdP
```

Do not claim NFR-SEC-003 is fully production-complete until a real IdP/MFA integration is activated.

---

# 8. Specification Drift — Actor Lifecycle Status

There is a documentation gap that must be reconciled explicitly.

`docs/04_DOMAIN_MODEL.md` defines Actor fields:

```text
actor_id
actor_type
roles[]
subject_id?
institution_id?
session_id?
```

but does not define actor lifecycle status.

`docs/05_DATABASE_SCHEMA.md` requires:

```text
actors.status VARCHAR NOT NULL
```

Engineering standards require explicit finite states.

Before implementation report:

```text
SPECIFICATION DRIFT DETECTED
```

with:

```text
Source A: docs/04_DOMAIN_MODEL.md Actor
Source B: docs/05_DATABASE_SCHEMA.md actors
Conflict: persistence requires actor status but canonical domain does not define lifecycle values
Resolution: define ActorStatus ACTIVE / DISABLED for the P4-B baseline
```

Update both domain/schema documentation narrowly.

Do not invent a larger identity lifecycle without a requirement.

---

# 9. Actor Domain

Use:

```text
backend/app/modules/identity/
```

Recommended useful files:

```text
domain.py
contracts.py
application.py
authorization.py
infrastructure.py
public.py
__init__.py
```

Optional concise `README.md`.

Remove:

```text
backend/app/modules/identity/.gitkeep
```

when real files exist.

Do not create empty directory ceremony.

---

# 10. Canonical Actor Types

Define exactly the canonical ActorType values from `04_DOMAIN_MODEL.md`:

```text
PATIENT
PSEUDONYMOUS_USER
CAREGIVER
CLINICIAN
COUNSELLOR
TRIAGE_STAFF
RESOURCE_ADMIN
CLINICAL_REVIEWER
SYSTEM_ADMIN
RESEARCHER
SERVICE_ACCOUNT
```

Actor type is not permission.

Never infer a permission solely from ActorType.

A `CAREGIVER` does not automatically inherit patient access.

---

# 11. Actor Status

Define:

```text
ACTIVE
DISABLED
```

Semantics:

```text
ACTIVE   -> may participate in authentication/authorization if other checks pass
DISABLED -> cannot produce an authenticated current actor
```

Do not auto-delete actors.

No reactivation HTTP API in P4-B.

---

# 12. Initial Roles

The P4 master plan defines these initial roles:

```text
patient
pseudonymous_user
clinician
resource_admin
clinical_reviewer
system_admin
researcher
```

Use an explicit typed role representation, preferably `RoleCode`.

Do not add:

```text
superuser
root
*
all
```

Do not create wildcard role inheritance.

Future roles such as caregiver/counsellor/triage staff may be added through governed migrations and
policy changes when those workflows activate.

---

# 13. Permission Model

Permissions are action/capability oriented.

Create an extensible immutable `PermissionCode` value object rather than a closed enum that blocks
future modules.

Canonical initial permission constants should include the architecture examples needed by current
role policy:

```text
patient:read:self
encounter:read:assigned
summary:confirm
provider:manage
policy:review
research:run
audit:read
```

Validate permission strings with a stable lowercase colon-separated grammar.

Do not allow:

```text
*
admin:*
*:*
```

Wildcard authorization is prohibited in the baseline.

---

# 14. Initial Role -> Permission Policy

Use an explicit immutable mapping.

Foundation policy:

```text
patient
  -> patient:read:self

pseudonymous_user
  -> no privileged permission by default

clinician
  -> encounter:read:assigned
  -> summary:confirm

resource_admin
  -> provider:manage

clinical_reviewer
  -> policy:review

researcher
  -> research:run

system_admin
  -> provider:manage
  -> policy:review
  -> audit:read
```

Important:

```text
system_admin is NOT wildcard superuser
```

Every future new permission requires explicit policy consideration.

No actor type automatically grants a role.

---

# 15. Actor Entity

Define a framework-independent immutable Actor with:

```text
actor_id
actor_type
roles
subject_id?
institution_id?
status
created_at
updated_at
```

Use:

```text
OpaqueId
frozenset[RoleCode]
timezone-aware UTC timestamps
```

Do not include:

```text
password
email
phone
OIDC token
session bearer token
MFA secret
clinical data
```

---

# 16. Shared ActorContext Evolution

P2 created an identity-neutral:

```text
backend/app/shared/security/actor.py
```

P4-B should evolve it without coupling shared security to SQLAlchemy/FastAPI/vendor SDKs.

Safe fields:

```text
actor_id: OpaqueId | None
actor_type: str | None
roles: frozenset[str]
subject_id: OpaqueId | None
institution_id: OpaqueId | None
session_id: OpaqueId | None
request_id: RequestId | None
is_authenticated: bool
mfa_verified: bool
```

Requirements:

```text
frozen
slots
immutable roles
safe repr
no credentials
no PII
```

Defaults remain anonymous/least privilege:

```text
is_authenticated=False
mfa_verified=False
roles=empty
```

Do not make a pseudonymous P4-A session automatically `is_authenticated=True`.

---

# 17. ActorContext Trust Rule

Only a trusted authentication boundary may construct an authenticated ActorContext.

Do NOT provide a public HTTP mechanism such as:

```text
X-Actor-ID
X-Roles
X-MFA
```

to populate ActorContext.

Never trust client role headers.

Synthetic tests may inject ActorContext directly through test-only dependency construction.

Production code must not expose a bypass.

---

# 18. Authentication Credential

Define a small sensitive credential wrapper for provider adapters.

Requirements:

```text
opaque string/bytes-like logical credential
non-empty
bounded
immutable
excluded/redacted from repr
never persisted
never logged
```

A class such as:

```text
AuthenticationCredential
```

is appropriate.

Do not parse JWT in P4-B.

---

# 19. Authenticated Principal

Define a provider-neutral immutable result from a trusted authentication adapter.

Recommended fields:

```text
actor_id
provider
mfa_verified
```

Optional safe provider metadata may be added only if necessary.

Do not include raw credential.

Do not include arbitrary OIDC claims.

P4-B only needs enough information to resolve the internal actor.

---

# 20. AuthenticationProvider Port

Define a provider-neutral async protocol, conceptually:

```python
class AuthenticationProvider(Protocol):
    async def authenticate(
        self, credential: AuthenticationCredential
    ) -> AuthenticatedPrincipal | None:
        ...
```

Rules:

```text
None/rejection -> AUTHENTICATION_REQUIRED
provider unavailable -> safe dependency failure if explicitly represented
raw provider exception never leaks
```

No provider SDK dependency.

No default synthetic provider in production code.

Tests may define a fake provider locally.

---

# 21. Default External Authentication State

The default P4-B identity module must NOT pretend an external IdP exists.

Default provider:

```text
None / disabled / unavailable
```

Calling `identity.authenticate` when no provider is configured should fail honestly with:

```text
DEPENDENCY_UNAVAILABLE
```

or an equally safe documented unavailable result.

Do not silently authenticate anyone.

No HTTP login route is added, so this state does not break existing P4-A session flows.

---

# 22. Identity Service

Implement a module-owned application service with explicit dependencies:

```text
DatabaseRuntime | None
ActorRepository
AuthenticationProvider | None
clock
authorization policy
```

No global singleton.

Potential operations:

```text
create_actor(...)            # internal/trusted application operation
get_actor(...)
disable_actor(...)
authenticate(...)
current_actor(...)
```

No public actor-management HTTP API.

---

# 23. Actor Provisioning

P4-B needs a deterministic way to persist/test actors and roles.

Provide an internal application operation such as:

```text
create_actor(
    actor_type,
    roles,
    subject_id?,
    institution_id?
)
```

It is NOT exposed over HTTP.

Rules:

```text
ACTIVE by default
explicit roles required/accepted
no role inferred from actor type
timestamps UTC
duplicates rejected as appropriate
```

No provider-specific external-subject mapping table.

---

# 24. Current Actor Resolution

`identity.current_actor` should accept a trusted `AuthenticatedPrincipal`, not an arbitrary raw
`actor_id` from an HTTP caller.

Flow:

```text
AuthenticatedPrincipal
    |
load actor from PostgreSQL
    |
actor exists?
actor ACTIVE?
roles loaded?
    |
ActorContext(
  is_authenticated=True,
  mfa_verified=principal.mfa_verified,
  ...
)
```

Unknown/disabled actor must fail closed with:

```text
AUTHENTICATION_REQUIRED
```

Do not reveal whether actor ID exists or is disabled through a public auth boundary.

---

# 25. Authenticate Capability

`identity.authenticate`:

```text
AuthenticationCredential
    |
AuthenticationProvider
    |
AuthenticatedPrincipal
    |
identity.current_actor
    |
ActorContext
```

If no provider configured:

```text
DEPENDENCY_UNAVAILABLE
```

If credential rejected:

```text
AUTHENTICATION_REQUIRED
```

Do not log credential/provider token.

---

# 26. Pseudonymous Identity Boundary

P4-A already provides pseudonymous and kiosk session continuity.

P4-B MUST NOT create a persisted Actor merely because a pseudonymous session exists.

A pseudonymous session may continue with:

```text
actor_id = NULL
```

until a workflow genuinely needs a persisted actor.

Do not silently promote pseudonymous users into identified users.

Do not make session existence imply identity authentication.

---

# 27. Authenticated Session Boundary

Do not expose creation of:

```text
AUTHENTICATED
CLINICIAN
ADMIN
RESEARCH
```

sessions yet.

The schema/model can represent them, but real activation depends on the selected IdP and a trusted
binding flow.

Do not fake authenticated continuity with a test provider in production.

---

# 28. Actors Persistence

Implement SQLAlchemy 2.x typed ORM for:

```text
actors
```

Canonical columns:

```text
id UUID PK
actor_type VARCHAR NOT NULL
subject_ref UUID NULL
institution_id UUID NULL
status VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Owner:

```text
identity
```

No additional identity/PII columns.

---

# 29. Actor Roles Persistence

Implement:

```text
actor_roles
```

Canonical columns:

```text
actor_id UUID NOT NULL FK actors(id)
role_code VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
PRIMARY KEY(actor_id, role_code)
```

Owner:

```text
identity
```

Use named PK/FK/check constraints.

`actor_id` foreign key may use `ON DELETE CASCADE` for role rows if justified.

Do not create role records independent of an actor.

---

# 30. Actor DB Constraints

Use named constraints for:

```text
actor_type in canonical ActorType values
status in ACTIVE/DISABLED
role_code in the P4-B baseline RoleCode values
```

Use opaque UUID IDs.

No sequential IDs.

---

# 31. Session Actor Foreign Key

P4-A intentionally staged:

```text
sessions.actor_id UUID NULL
```

without an FK because `actors` did not exist yet.

P4-B should now add referential integrity:

```text
sessions.actor_id -> actors.id
```

Requirements:

```text
nullable remains allowed
no patient FK yet
no direct session-table business writes from identity
```

Use a named foreign key.

Do not create the P5 patient FK yet.

Update the SQLAlchemy SessionRecord metadata to match the migration, using a string FK target without
introducing repository cross-module business logic.

---

# 32. No Actor Deletion API

Do not implement actor deletion.

Lifecycle baseline is:

```text
ACTIVE
DISABLED
```

Authorization must fail for disabled actors.

Deletion/privacy workflows belong to later governance/privacy work.

---

# 33. Actor Repository

Implement a narrow identity-owned repository.

Operations may include:

```text
create
get
get_for_update
disable
```

and role loading required by the service.

No generic CRUD abstraction.

Repository does not commit.

Application service owns transaction boundaries.

---

# 34. Role Persistence Semantics

Roles persisted in `actor_roles` are authoritative for persisted actors.

Do not duplicate role lists into:

```text
actors JSON
session token
client headers
cache
```

No Redis.

No token-carried authorization claims as the sole authority.

---

# 35. Authorization Service

Implement a framework-independent authorization service.

Required operations:

```text
has_permission(actor_context, permission) -> bool
require_permission(actor_context, permission) -> None
require_self_subject(actor_context, permission, subject_id) -> None
```

Rules:

```text
unauthenticated -> AUTHENTICATION_REQUIRED
authenticated but insufficient permission -> AUTHORIZATION_DENIED
disabled actor never reaches authenticated context
unknown roles grant nothing
no wildcard permission
```

Use existing canonical public error codes.

---

# 36. Self-Subject Authorization

`patient:read:self` is the baseline object-scope rule.

To authorize self access:

```text
actor is authenticated
actor has patient:read:self
actor.subject_id is not NULL
actor.subject_id == requested_subject_id
```

Otherwise:

```text
AUTHORIZATION_DENIED
HTTP 403
```

Do not allow:

```text
actor A subject -> actor B subject
```

This is the P4-B foundation for preventing basic IDOR before P5 patient endpoints exist.

No patient table is created.

Tests use synthetic opaque subject UUIDs.

---

# 37. Actor Type Does Not Authorize

Mandatory tests:

```text
ActorType.SYSTEM_ADMIN with no system_admin role -> no admin permission
ActorType.PATIENT with no patient role -> no patient:read:self
ActorType.CAREGIVER -> no inherited patient permission
```

Roles and explicit permission policy are authoritative.

---

# 38. MFA Authorization Gate

Define the administrative role set explicitly:

```text
resource_admin
clinical_reviewer
system_admin
```

If authenticated ActorContext contains any administrative role and:

```text
mfa_verified=False
```

then privileged permission authorization must fail closed.

Use:

```text
AUTHORIZATION_DENIED
```

with a safe message.

No raw provider/MFA details.

Tests:

```text
resource_admin + provider:manage + mfa false -> deny
resource_admin + provider:manage + mfa true -> allow
system_admin + audit:read + mfa false -> deny
system_admin + audit:read + mfa true -> allow
```

Do not trust a request header to set `mfa_verified`.

---

# 39. Server-Side Route Guard

Create a reusable FastAPI authorization guard in the API/security boundary.

Reasonable location:

```text
backend/app/api/security/authorization.py
```

It should:

```text
read trusted ActorContext supplied by application/auth boundary
call identity authorization capability
return/allow only on success
```

If no actor context exists on the request, treat it as anonymous.

Do not read:

```text
X-Actor-ID
X-Role
X-MFA
```

from the client.

No frontend visibility rule counts as authorization.

---

# 40. Request Actor Context Default

Do not require a new authentication middleware in P4-B.

A transport helper may return an anonymous ActorContext when `request.state.actor_context` is absent.

Safe defaults:

```text
is_authenticated=False
roles=empty
mfa_verified=False
request_id preserved if available
```

Future provider authentication may populate a trusted ActorContext before privileged application use.

Do not modify P4-A session bearer parsing into external IdP authentication.

---

# 41. Privileged Route Acceptance Test

There are no production privileged actor-management routes in P4-B.

Do NOT add a public `/admin-probe` or `/identity/debug` route merely for acceptance.

Instead use a synthetic test-only FastAPI router through the existing test composition hook.

Test the real project guard:

```text
anonymous context -> 401 AUTHENTICATION_REQUIRED
authenticated wrong role -> 403 AUTHORIZATION_DENIED
authenticated correct role -> 200
```

For an administrative role also prove MFA gating.

This satisfies AC-P4-006 without shipping a debug security endpoint.

---

# 42. Cross-Subject Route Test

Use a synthetic test-only route such as:

```text
/subjects/{subject_id}
```

not present in production registration.

Inside the route, use the real authorization service/guard path.

Test:

```text
patient actor subject A -> subject A => allowed
patient actor subject A -> subject B => 403
```

No patient table required.

This is the AC-P4-010 baseline.

---

# 43. Identity Module Capabilities

Define central typed capability keys in `identity/public.py`.

Required:

```text
identity.authenticate
identity.current_actor
identity.authorize
```

Do not implement:

```text
identity.resolve_patient_identity
```

until P5 provides a patient identity target.

Do not duplicate capability keys elsewhere.

---

# 44. Identity Module Manifest

Create:

```text
module_id = identity
version = 1
```

Provided capabilities:

```text
identity.authenticate
identity.current_actor
identity.authorize
```

Data ownership:

```text
actors
actor_roles
```

API prefixes:

```text
none
```

No HTTP identity-management API in P4-B.

No feature flag required.

No required permission metadata because the module exposes no privileged HTTP route.

---

# 45. Default Module Composition

Default application composition after P4-B should explicitly register:

```text
sessions
identity
```

through the existing `ModuleRegistry`.

No runtime scanning.

No entry points.

No importlib discovery.

Registry remains sealed before runtime use.

Custom explicit `module_registrations=(...)` tests must continue to control their own composition
without implicit duplicate built-ins.

---

# 46. Identity Module Registration

`build_identity_registration(...)` should accept explicit infrastructure:

```text
database
authentication_provider=None
clock=utc_now
authorization policy/default
```

It should build per-application services.

No global identity service.

No shared mutable role registry.

---

# 47. Authentication Provider Is Not a Module Plugin

The provider is a normal injected adapter implementing a Protocol.

Do not create:

```text
runtime provider discovery
provider import strings
entry-point plugin loading
```

Provider choice is explicit composition.

---

# 48. No Identity HTTP API

P4-B MUST NOT add:

```text
POST /login
POST /logout
GET /me
POST /actors
GET /actors
PUT /roles
POST /roles
```

The canonical P4 HTTP APIs currently list sessions and consent.

Identity baseline remains an internal capability/security boundary.

A future IdP integration may add auth transport after its spike and contract review.

---

# 49. No JWT

Do not add:

```text
PyJWT
python-jose
Authlib
OIDC middleware
JWKS cache
JWT claim parsing
```

P4-B credential is provider-neutral and opaque.

---

# 50. No Keycloak Infrastructure

Do not modify Compose to add Keycloak.

Do not add Keycloak realm exports.

Do not add Keycloak client secrets.

Do not add IdP environment variables.

Record as deferred:

```text
Keycloak/OIDC spike required before real authenticated identity activation.
```

---

# 51. No MFA Implementation

Do not implement:

```text
TOTP
SMS OTP
email OTP
WebAuthn
MFA enrollment
recovery codes
```

Only authorization policy consumes trusted `mfa_verified`.

The eventual IdP owns primary authentication/MFA proof.

---

# 52. No Consent

Do not add consent fields to Actor, ActorContext, roles, or permissions.

Session/identity does not imply consent.

P4-C owns consent.

---

# 53. No Patient Domain

`subject_ref` is an opaque future subject reference.

Do not create or query a patient table.

No FK from `actors.subject_ref` yet.

P5 owns patients.

---

# 54. No Caregiver Delegation

ActorType may include CAREGIVER.

Do not implement:

```text
caregiver -> patient delegation
proxy consent
guardian linkage
```

A caregiver gets no patient permission automatically.

Future governed feature required.

---

# 55. No Institutional Authorization Model Yet

`institution_id` remains optional metadata.

Do not implement institution membership/tenant tables.

Do not use institution equality as a substitute for explicit permission/object scope.

---

# 56. Actor Timestamp Invariants

All actor timestamps:

```text
created_at
updated_at
```

must be timezone-aware UTC.

Service clock:

```text
reject naive
normalize aware non-UTC to UTC
```

Use deterministic injection.

No `datetime.utcnow()`.

---

# 57. Authentication Credential Privacy

Test with marker:

```text
synthetic-private-auth-credential
```

Verify it is absent from:

```text
repr
logs
errors
database
ActorContext
```

Do not persist authentication credentials.

---

# 58. Authentication Provider Failure Privacy

A synthetic provider exception may contain:

```text
synthetic-provider-secret-detail
```

Application boundary must not expose that message through a public typed error or stored actor state.

Do not log raw exception by default.

Unexpected provider failures may map to:

```text
DEPENDENCY_UNAVAILABLE
```

with safe message.

Credential rejection maps to:

```text
AUTHENTICATION_REQUIRED
```

---

# 59. Current Actor Privacy

ActorContext may contain only opaque internal references and authorization metadata.

Do not put:

```text
email
phone
display name
credential
token
raw IdP claims
```

into ActorContext.

---

# 60. Identity Service Database Disabled Behavior

If PostgreSQL is disabled/unavailable, persisted-actor operations fail safely with:

```text
DEPENDENCY_UNAVAILABLE
```

No HTTP route uses identity directly yet, but capability behavior must be deterministic.

Authorization of an already supplied ActorContext remains pure and does not need DB access.

---

# 61. Migration

Create:

```text
backend/migrations/versions/0004_identity_authorization.py
```

Recommended revision:

```text
p4b_0004
```

Parent:

```text
p4a_0003
```

Migration performs only:

```text
create actors
create actor_roles
add sessions.actor_id -> actors.id FK
```

No consent/patient/audit tables.

---

# 62. Migration Downgrade

Downgrade order must safely:

```text
drop sessions.actor_id FK
drop actor_roles
drop actors
```

Return to P4-A schema.

Do not drop sessions.

Do not alter token/session lifecycle.

---

# 63. Alembic Metadata Registration

Explicitly register identity ORM models.

After P4-B:

```text
Base.metadata tables =
outbox_events
sessions
actors
actor_roles
```

No consent/patient tables.

`SessionRecord.actor_id` metadata must match the new FK.

`patient_id` remains without FK until P5.

---

# 64. Migration Verification

Against a fresh PostgreSQL volume:

```text
heads -> exactly p4b_0004
upgrade head
current
alembic check
```

Then:

```text
downgrade p4a_0003
actors absent
actor_roles absent
sessions remains
sessions.actor_id FK absent
outbox remains
upgrade head
actors/actor_roles restored
sessions.actor_id FK restored
alembic check clean
```

End at head.

---

# 65. FK Verification

Real PostgreSQL tests must verify:

```text
actor_roles.actor_id references actors.id
sessions.actor_id references actors.id
sessions.patient_id still has no patient FK
```

Attempting to set `sessions.actor_id` to a nonexistent actor should fail at DB level.

Use synthetic data and rollback/cleanup.

---

# 66. Actor Persistence Tests

Real PostgreSQL tests:

```text
create actor
persist multiple roles
load actor
roles round-trip
timestamps
disable actor
disabled actor cannot resolve as current actor
```

No PII.

---

# 67. Role Constraint Test

Verify invalid role code cannot be persisted through normal domain validation and DB check.

Do not weaken DB constraints.

---

# 68. Actor Type Constraint Test

Verify invalid actor type is rejected.

No free-form role/type values in authoritative rows.

---

# 69. Authentication Provider Test

Use a test-only fake provider.

Test:

```text
credential -> principal(actor_id, mfa false/true)
actor loaded from PostgreSQL
roles loaded
ActorContext authenticated
```

No network.

No vendor SDK.

---

# 70. Unconfigured Provider Test

Default identity registration:

```text
authentication_provider=None
```

Calling authenticate:

```text
DEPENDENCY_UNAVAILABLE
```

No fake success.

---

# 71. Rejected Credential Test

Fake provider returns no principal.

Expected:

```text
AUTHENTICATION_REQUIRED
```

No actor existence leakage.

---

# 72. Unknown Principal Actor Test

Provider returns an actor ID not in PostgreSQL.

Expected:

```text
AUTHENTICATION_REQUIRED
```

Do not return RESOURCE_NOT_FOUND.

---

# 73. Disabled Actor Test

Provider returns disabled actor ID.

Expected:

```text
AUTHENTICATION_REQUIRED
```

No role authorization.

---

# 74. Authorization Error Semantics

Use existing:

```text
AUTHENTICATION_REQUIRED -> 401
AUTHORIZATION_DENIED -> 403
DEPENDENCY_UNAVAILABLE -> 503
```

Do not add new public auth codes unless canonical docs require them.

---

# 75. Pure Authorization

`AuthorizationService` must not perform database I/O during permission checking.

It consumes trusted ActorContext and static/versioned foundation policy.

Future dynamic policy sources may be added later behind a policy boundary.

---

# 76. Policy Versioning Note

P4-B foundation role mapping may be a code-owned versioned constant such as:

```text
AUTHORIZATION_POLICY_VERSION = "p4b-v1"
```

This is optional but useful.

Do not build an admin-editable policy engine in P4-B.

If version is exposed in internal decisions, no sensitive data.

---

# 77. No Role Claims as Authority

Even when future IdP tokens contain roles, SwasthyaSetu role persistence/policy remains authoritative.

P4-B provider principal should return:

```text
actor_id
mfa_verified
```

not arbitrary client/provider roles that bypass `actor_roles`.

Do not authorize from raw external token role claims.

---

# 78. Administrative MFA Role Test

Mandatory:

```text
persist resource_admin actor with resource_admin role
trusted principal mfa_verified=False
current actor resolved
provider:manage denied

same actor/principal with mfa_verified=True
provider:manage allowed
```

No real MFA provider required.

---

# 79. System Admin Explicit-Permission Test

Mandatory:

```text
system_admin + mfa true
audit:read -> allowed
provider:manage -> allowed
research:run -> denied unless explicitly mapped
```

This proves no wildcard superuser behavior.

---

# 80. Patient Self-Scope Test

Mandatory:

```text
patient role
subject_id=A
patient:read:self + subject=A -> allowed
patient:read:self + subject=B -> denied
```

Actor type alone without role must deny.

---

# 81. Caregiver Non-Inheritance Test

Mandatory:

```text
ActorType.CAREGIVER
no patient role
subject/ref relation irrelevant
patient:read:self -> denied
```

Do not infer delegation.

---

# 82. Request Guard Test

Create test-only actor provider or fixed context injection.

Use real FastAPI guard implementation.

Verify canonical error envelope:

```text
anonymous -> 401 AUTHENTICATION_REQUIRED
authenticated insufficient -> 403 AUTHORIZATION_DENIED
authorized -> 200
```

Do not add the synthetic route to production module registration.

---

# 83. MFA Route Guard Test

Synthetic privileged test route requiring:

```text
provider:manage
```

Use resource-admin contexts:

```text
mfa false -> 403
mfa true -> 200
```

No client header controls MFA state.

---

# 84. Basic IDOR Route Test

Synthetic subject route uses real self-subject authorization rule.

Verify:

```text
actor subject A requesting A -> 200
actor subject A requesting B -> 403
```

This is the P4-B AC-P4-010 proof.

No production patient route exists yet.

---

# 85. Shared ActorContext Regression

P2 tests expecting default ActorContext must remain valid.

Add tests for:

```text
default anonymous
roles immutable
authenticated context safe repr
no credential fields
mfa false by default
```

Do not break request ID behavior.

---

# 86. Sessions Regression

All P4-A session tests remain green.

Do not alter:

```text
pseudonymous/kiosk token flow
expiry
close
token hashing
HTTP routes
```

except adding the `actor_id` FK metadata.

P4-A-created sessions still use:

```text
actor_id = NULL
patient_id = NULL
```

---

# 87. Session FK Regression

P4-A session creation must still work with `actor_id=NULL`.

P4-A API does not suddenly require actor authentication.

This is mandatory.

---

# 88. Module Registry Tests

Default app should now register:

```text
identity
sessions
```

Registry remains sealed.

Identity capabilities resolve:

```text
identity.authenticate
identity.current_actor
identity.authorize
```

Sessions capabilities remain resolvable.

Custom explicit module-registration tests remain deterministic.

---

# 89. Identity Module Has No Router

Identity registration should contribute:

```text
routers=()
```

No new OpenAPI identity paths.

Test OpenAPI does not gain debug/login/actor-management paths.

---

# 90. API Security Transport Placement

FastAPI-specific authorization guard belongs in API/interface layer, not identity domain.

Identity authorization policy remains framework-independent.

Do not import FastAPI into:

```text
identity/domain.py
identity/authorization.py
```

---

# 91. No Frontend Changes

Expected unchanged:

```text
apps/**
packages/ui/**
package.json
pnpm-lock.yaml
```

P6 will integrate frontend identity/session UX.

Frontend quality remains regression-only.

---

# 92. No New Runtime Dependency Expected

Expected:

```text
backend/pyproject.toml unchanged
backend/uv.lock unchanged
```

Use:

```text
stdlib
existing Pydantic/FastAPI/SQLAlchemy
```

If a new OIDC/auth package appears necessary:

```text
STATUS: BLOCKED — DEPENDENCY / IDP SPIKE REQUIRED
```

Do not add it silently.

---

# 93. No Configuration Churn

Do not add Keycloak/OIDC configuration.

No provider endpoint/client ID/secret yet.

Identity module is provider-unconfigured by default.

Existing `SecuritySettings` may remain unchanged.

---

# 94. Docker / Compose

Expected unchanged:

```text
deployments/local/compose.yaml
infra/docker/backend.Dockerfile
```

Do not add an IdP service.

No Redis.

No new port.

---

# 95. CI

Keep the six mandatory jobs:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

No seventh job required.

Update migration assertions from:

```text
p4a_0003
```

to:

```text
p4b_0004
```

where exact head is checked.

---

# 96. Persistence Integration CI

Fresh DB workflow must verify:

```text
one head
upgrade p4b_0004
alembic check
PostgreSQL regressions
identity tests execute
downgrade p4a_0003
identity tables absent
sessions remains
re-upgrade p4b_0004
```

Do not weaken P3/P4-A checks.

---

# 97. Schema Inspection CI

Verify:

```text
actors exists
actor_roles exists
sessions exists
outbox_events exists
```

Check:

```text
actor_roles FK
sessions.actor_id FK
expected identity constraints
Alembic version p4b_0004
```

No patient/consent table.

---

# 98. PostgreSQL Marker

Use existing:

```text
@pytest.mark.postgres
```

for DB tests.

Remote Persistence integration must execute relevant tests with zero relevant skips.

No SQLite substitution.

---

# 99. Authentication Credential Logging Test

Capture logs around synthetic provider authentication using known credential marker.

Marker must not appear.

Do not log provider credential on success/failure.

---

# 100. Provider Exception Logging Test

If provider exception is caught, verify raw secret marker is absent from:

```text
response/error message
stored state
logs
```

Use safe dependency error.

---

# 101. No Actor PII Test

Inspect actors row/model/API surfaces.

There is no HTTP actor response, but persistence/domain must not contain:

```text
email
phone
name
address
```

P4-B stores authorization identity metadata only.

---

# 102. Actor Repr Privacy

Actor and ActorContext repr may include opaque IDs/roles but never credentials.

AuthenticationCredential repr must redact its value.

AuthenticatedPrincipal contains no credential.

---

# 103. Authorization Policy Immutability

Foundation role-permission mapping must not be request-mutable.

Use immutable/frozen structures.

No global dict exposed for mutation.

No admin edit endpoint.

---

# 104. Permission Normalization

Permission codes must compare exactly after validation.

Do not lowercase arbitrary untrusted permission strings silently at authorization time.

Callers use validated constants/value objects.

---

# 105. Role Normalization

Role codes are canonical lowercase constants.

Persist canonical values.

Do not accept whitespace variants silently inside persistence.

---

# 106. Actor Status Authorization

Even if a stale ActorContext were manually constructed with a disabled actor's roles, normal
`identity.current_actor` must never produce such context.

Authorization service cannot query DB, so the trusted-context boundary is important.

Document this trust invariant.

---

# 107. Session Actor FK Ownership

Adding the FK is a coordinated schema evolution, not permission for identity code to update session
business state.

Identity module MUST NOT import `PostgresSessionRepository` or mutate session rows.

No session actor-binding operation is implemented in P4-B.

Real authenticated-session binding waits for the IdP integration design.

---

# 108. No Cross-Module DB Writes

Identity writes:

```text
actors
actor_roles
```

only.

Sessions module continues writing:

```text
sessions
```

The database FK is integrity, not ownership transfer.

---

# 109. No Identity Events Required

Do not add:

```text
ActorCreated
RoleAssigned
ActorDisabled
```

unless a concrete current consumer requires them.

No current consumer does.

Prefer no new event work.

---

# 110. No Audit Module Yet

Authorization/role actions will eventually be auditable, but P4-B does not create `audit_events`.

Do not misuse OTel logs as audit storage.

Later audit phase owns governed audit persistence.

---

# 111. Documentation Updates

Expected:

```text
README.md
backend/README.md
REPOSITORY_TREE.txt
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md
docs/05_DATABASE_SCHEMA.md
docs/06_API_CONTRACTS.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P4_B_IDENTITY_AUTHORIZATION_BASELINE.md
```

Possible:

```text
backend/app/modules/identity/README.md
```

No source-material changes.

---

# 112. API Contract Documentation

Do not add an identity endpoint.

Clarify general authorization semantics:

```text
401 = no valid authenticated actor
403 = authenticated actor lacks permission/object scope/auth strength
backend guard is authoritative
frontend visibility is not security
external IdP remains replaceable/unconfigured
```

Document admin MFA trust requirement.

---

# 113. Domain Documentation

Reconcile ActorStatus.

Document distinction:

```text
ActorType != RoleCode
RoleCode != PermissionCode
Actor != Patient
Caregiver gets no automatic patient permission
```

Do not turn actor domain into a patient profile.

---

# 114. Database Documentation

Update identity schema with:

```text
ActorStatus values
baseline role codes
sessions.actor_id FK activation in P4-B
```

No patient FK yet.

No provider identity table.

---

# 115. Backend README

Document:

```text
identity module has no HTTP login/management API
external auth provider unconfigured by default
authorization policy is server-side
admin roles require trusted MFA indication
synthetic provider exists only in tests
Keycloak/OIDC remains a future spike
```

Do not provide unsafe "set X-Role header" examples.

---

# 116. Progress Tracker Before Remote CI

After local verification but before remote green:

```text
P4-B = PARTIAL — REMOTE CI VERIFICATION PENDING
P4 = PARTIAL
```

Record:

```text
base SHA
branch
implementation SHA
migration p4b_0004
actor/role policy
authorization tests
MFA policy tests
IDOR tests
provider-unconfigured behavior
```

---

# 117. Progress Tracker After Remote CI

Only after all six mandatory jobs pass:

```text
P4-B = COMPLETE
P4 = PARTIAL
```

Record:

```text
CI run ID
CI URL
head SHA
AC-P4-005 PASS
AC-P4-006 PASS
AC-P4-010 PASS
next = P4-C — Consent Domain & APIs
```

P4 remains PARTIAL because consent is not implemented.

---

# 118. Unit Verification

From `backend/`:

```text
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m compileall -q app tests
```

Run import smoke.

All must pass.

---

# 119. PostgreSQL Verification

Against fresh PostgreSQL:

```text
uv run alembic -c alembic.ini heads
uv run alembic -c alembic.ini upgrade head
uv run alembic -c alembic.ini current
uv run alembic -c alembic.ini check
uv run pytest -m postgres
```

Identity Postgres tests must execute.

---

# 120. Downgrade / Re-upgrade Verification

Verify:

```text
upgrade p4b_0004
downgrade p4a_0003
actors absent
actor_roles absent
sessions present
outbox_events present
upgrade head
actors present
actor_roles present
session actor FK present
alembic check clean
```

End at head.

---

# 121. Root Quality Gates

From repository root:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

Both pass.

---

# 122. Dependency Diff

Run:

```text
git diff -- backend/pyproject.toml backend/uv.lock package.json pnpm-lock.yaml
```

Expected:

```text
empty
```

Investigate any change.

---

# 123. Docker / Compose Diff

Run:

```text
git diff -- deployments/local/compose.yaml infra/docker/backend.Dockerfile
```

Expected empty.

No IdP service.

---

# 124. Migration Review

Inspect migration manually.

It must contain only:

```text
actors
actor_roles
sessions.actor_id foreign key
```

No consent/patient/audit/provider mapping tables.

---

# 125. Privacy / Security Audit

Before commit verify:

```text
no raw authentication credential persisted
no raw credential logged
no client-controlled roles
no client-controlled mfa flag
no wildcard authorization
no actor PII
no JWT/OIDC secret
no fake production authentication
no consent implication
```

---

# 126. Architecture Audit

Verify:

```text
identity owns actors/actor_roles
sessions still owns sessions
no direct identity write to sessions
provider-neutral authentication port
authorization owned by SwasthyaSetu
backend route guard exists
no runtime plugin discovery
no Keycloak/IdP activation
no patient/consent tables
P2 registry preserved
P3 persistence/events/jobs/storage preserved
P4-A sessions preserved
```

---

# 127. Git Audit

Run:

```text
git status --short
git diff --stat
git diff
git diff --check
```

Do not commit:

```text
.env
tokens
OIDC/JWT samples that resemble real secrets
DB dumps
Postgres data
logs containing credentials
```

---

# 128. Commit & Push

After local verification:

```text
git add <P4-B files only>
git commit -m "feat: establish P4-B identity authorization baseline"
git push -u origin phase/p4-b-identity-authorization
```

Do not merge.

Do not force-push.

---

# 129. Remote CI

Verify final branch SHA passes:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

Do not claim success without observing the actual run.

---

# 130. Closure Commit

If implementation was pushed before CI completed:

1. keep tracker P4-B partial;
2. observe all six jobs;
3. fix real failures;
4. after green CI update tracker;
5. mark P4-B complete;
6. keep P4 partial;
7. record CI evidence;
8. set next P4-C;
9. create focused docs closure commit;
10. push same branch.

Do not merge.

---

# 131. P4 Acceptance Audit

Report all:

```text
AC-P4-001
AC-P4-002
AC-P4-003
AC-P4-004
AC-P4-005
AC-P4-006
AC-P4-007
AC-P4-008
AC-P4-009
AC-P4-010
```

Expected after successful P4-B:

```text
AC-P4-001 PASS
AC-P4-002 PASS
AC-P4-003 PASS
AC-P4-004 PASS
AC-P4-005 PASS
AC-P4-006 PASS
AC-P4-007 NOT YET IMPLEMENTED
AC-P4-008 NOT YET IMPLEMENTED
AC-P4-009 NOT YET IMPLEMENTED
AC-P4-010 PASS
```

Use actual evidence.

---

# 132. Final Report Format

Return exactly these sections.

## STATUS

```text
COMPLETE / PARTIAL / BLOCKED / FAILED
```

`COMPLETE` requires all six mandatory CI jobs green.

## SPECIFICATION DRIFT

Report:

```text
Detected
Source A
Source B
Conflict
Resolution
Files reconciled
```

## BRANCH / GIT

Report:

```text
base branch
base SHA
implementation branch
implementation SHA
closure SHA if any
remote SHA
main SHA
working-tree state
```

## SCOPE IMPLEMENTED

Only P4-B.

## ACTOR DOMAIN

Report:

```text
Actor location
ActorType values
ActorStatus values
RoleCode values
PermissionCode strategy
role/actor separation
timestamp invariants
```

## ACTOR CONTEXT

Report:

```text
shared ActorContext fields
default anonymous behavior
authenticated behavior
roles representation
subject/institution/session references
MFA field
privacy
```

## AUTHENTICATION CONTRACT

Report:

```text
AuthenticationCredential
AuthenticatedPrincipal
AuthenticationProvider
identity.authenticate
identity.current_actor
default provider state
credential rejection
provider failure
unknown/disabled actor
real IdP status
```

## AUTHORIZATION POLICY

Report:

```text
role -> permission mapping
wildcard status
unauthenticated behavior
insufficient permission behavior
self-subject behavior
caregiver behavior
system-admin behavior
policy mutability/version
```

## MFA BASELINE

Report:

```text
admin roles requiring MFA
mfa false behavior
mfa true behavior
source of mfa_verified
real MFA implementation status
```

## PERSISTENCE

Report:

```text
ActorRecord
ActorRoleRecord
tables
columns
constraints
foreign keys
session actor FK
patient FK status
table ownership
```

## IDENTITY SERVICE

Report:

```text
create actor
get/current actor
disable actor
authenticate
database-disabled behavior
provider-unconfigured behavior
transaction boundaries
```

## MODULE REGISTRATION / CAPABILITIES

Report:

```text
manifest
module id
provided capabilities
router count
data ownership
default app modules
registry sealing
```

## HTTP AUTHORIZATION GUARD

Report:

```text
guard location
trusted actor-context source
anonymous behavior
401 behavior
403 behavior
client role-header behavior
production identity endpoints added
```

## BASIC IDOR TEST

Report:

```text
subject A -> A
subject A -> B
result codes
patient table dependency
```

## PRIVACY / SECURITY

Report:

```text
credential persistence
credential logging
client-controlled roles
client-controlled MFA
actor PII
wildcard privileges
disabled actor behavior
frontend authorization reliance
```

## ALEMBIC / MIGRATION

Report:

```text
revision
parent
file
created tables
session FK change
constraints
downgrade
metadata registration
```

## MIGRATION VERIFICATION

Report:

```text
fresh DB
head
upgrade/current/check
downgrade p4a_0003
table/FK state after downgrade
re-upgrade
final drift check
```

## FILES CHANGED

Group:

```text
identity domain/contracts
authorization
persistence
shared actor context
API security
composition
migration
tests
CI
documentation
```

## DEPENDENCIES

Expected:

```text
No new runtime/dev dependency.
```

Report exact diffs.

## TESTS

Report:

```text
new unit tests
new PostgreSQL tests
synthetic privileged-route tests
MFA tests
IDOR tests
credential privacy tests
actor/role persistence tests
total backend tests
Postgres pass/skip
P4-A session regression
```

## VERIFICATION

Report all local checks.

## CI

Report:

```text
run ID
URL
head SHA
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
overall result
```

## P4 ACCEPTANCE STATUS

Report AC-P4-001 through AC-P4-010.

## ARCHITECTURE / GOVERNANCE CHECK

Explicitly report:

```text
Actor type does not imply role: YES/NO
Roles do not use wildcard authorization: YES/NO
Authorization is server-side: YES/NO
Unauthenticated privileged access fails closed: YES/NO
Cross-subject access fails closed: YES/NO
Administrative roles require trusted MFA flag: YES/NO
Client cannot set role/MFA through headers: YES/NO
External identity provider is replaceable: YES/NO
Real IdP is NOT falsely activated: YES/NO
No actor PII introduced: YES/NO
No consent pulled forward: YES/NO
No patient table pulled forward: YES/NO
No JWT/Keycloak/Redis added: YES/NO
Identity module uses explicit module registry: YES/NO
No runtime plugin discovery: YES/NO
P4-A session lifecycle preserved: YES/NO
P2/P3 contracts preserved: YES/NO
```

## DEVIATIONS

List every deviation and reason.

## BLOCKERS / OPEN DECISIONS

Only genuine unresolved items.

Expected deferred non-blockers:

```text
Keycloak/OIDC/authentik/ZITADEL provider spike before real authenticated identity activation
external subject -> internal actor mapping design at provider integration
production MFA claim/assurance mapping
caregiver delegation model
institution membership/tenant authorization
```

## PROGRESS TRACKER

State:

```text
P4-B status
overall P4 status
CI evidence
next recommended unit
```

## MERGE

```text
MERGE PERFORMED: NO
```

## RECOMMENDED NEXT UNIT

If P4-B complete:

```text
P4-C — Consent Domain & APIs
```

Do not implement it.

---

# 133. Success Definition

P4-B is successful only when:

- canonical ActorType exists;
- explicit ActorStatus ACTIVE/DISABLED exists;
- initial RoleCode model exists;
- extensible PermissionCode exists;
- ActorContext is immutable, privacy-safe, and least-privilege by default;
- actor type does not imply role;
- caregiver has no automatic patient permission;
- actors table exists;
- actor_roles table exists;
- roles persist authoritatively in PostgreSQL;
- sessions.actor_id gains valid FK to actors;
- sessions.patient_id remains staged without patient FK;
- provider-neutral AuthenticationProvider exists;
- authentication credential is redacted and never persisted/logged;
- default external provider is unconfigured and cannot fake authentication;
- test-only provider can produce trusted principal for deterministic verification;
- identity.current_actor loads ACTIVE persisted actor + roles;
- unknown/disabled actor fails closed;
- authorization service is deny-by-default;
- no wildcard/superuser permission exists;
- administrative roles require `mfa_verified=True` for privileged authorization;
- no client header can set actor roles or MFA;
- FastAPI server-side permission guard exists;
- synthetic privileged-route test proves 401/403/allow behavior;
- synthetic cross-subject test proves subject A cannot access subject B;
- no production debug/login/actor-management route is added;
- identity module exposes typed capabilities through the registry;
- default app explicitly registers sessions + identity;
- no Keycloak/JWT/OIDC dependency is added;
- no real IdP is falsely claimed active;
- only actors/actor_roles and the session actor FK are added to schema;
- Alembic head becomes p4b_0004;
- downgrade/re-upgrade and Alembic drift checks pass;
- P4-A session regression remains green;
- all six remote CI jobs pass;
- AC-P4-005, AC-P4-006 and AC-P4-010 PASS;
- P4-B is COMPLETE;
- overall P4 remains PARTIAL;
- branch is pushed but not merged.

Stop after P4-B.
