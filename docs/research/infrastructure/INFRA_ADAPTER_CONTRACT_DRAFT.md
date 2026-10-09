# SwasthyaSetu AI — Infrastructure Adapter & Boundary Contract Draft

**Document ID:** `SSAI-OSS-R2D-INFRA-003`  
**Status:** Research-derived draft  
**Version:** `0.1.0-research`  
**Purpose:** Feed system architecture, security, observability, DevOps and implementation specifications.

---

## 1. Goal

Keep infrastructure/vendor-specific types outside clinical/product modules.

Primary infrastructure contracts:

```text
IdentityProviderPort
PseudonymousSessionService
ObjectStoragePort
JobQueuePort
EphemeralCachePort
SecretProvider
MessageBusPort             future
```

Observability should use standard OpenTelemetry APIs through the project observability package rather than inventing a proprietary telemetry provider interface.

---

# Identity

## 2. IdentityProviderPort

Conceptually:

```python
class IdentityProviderPort(Protocol):
    async def resolve_identity(self, token: str) -> ExternalIdentity:
        ...
```

Normal API request authentication should preferably use standards-based local JWT validation:

```text
issuer
JWKS
signature
audience
expiry
```

rather than provider network introspection on every request.

---

## 3. ExternalIdentity

```text
subject
issuer
audiences[]
roles[]
groups[]
auth_time?
authentication_methods[]
email?             only if needed
display_name?      only if needed
safe_claims_subset
```

Do not persist the entire raw token as identity metadata.

---

## 4. InternalActor

Map:

```text
ExternalIdentity -> InternalActor
```

Canonical actor:

```text
actor_id
actor_type
role_ids[]
institution_id?
provider_id?
status
```

Authorization uses `InternalActor`, not raw Keycloak/authentik claims.

---

## 5. PseudonymousSessionService

Separate interface:

```text
create_session
resume_session
rotate_token
revoke_session
expire_session
link_to_account
```

Linking to an authenticated account must be explicit and policy-controlled.

---

## 6. Pseudonymous token

Requirements:

- high entropy;
- opaque or securely signed;
- expiry;
- revocation/rotation support;
- no health data encoded;
- not equivalent to proof of legal identity.

---

# Object Storage

## 7. ObjectStoragePort

Conceptually:

```python
class ObjectStoragePort(Protocol):
    async def put(self, request: PutObjectRequest) -> ObjectRef: ...
    async def get(self, ref: ObjectRef) -> ObjectStream: ...
    async def head(self, ref: ObjectRef) -> ObjectMetadata: ...
    async def delete(self, ref: ObjectRef) -> None: ...
    async def presign_upload(self, request: PresignUploadRequest) -> PresignedRequest: ...
    async def presign_download(self, ref: ObjectRef, expires_in: int) -> PresignedRequest: ...
```

---

## 8. ObjectRef

```text
provider
bucket
opaque_key
version_id?
checksum_sha256
size_bytes
content_type
encryption_metadata?
created_at
```

Do not persist provider SDK objects.

---

## 9. Object key factory

One centralized key factory generates opaque paths.

Modules must not concatenate arbitrary storage paths.

---

## 10. Lifecycle class

Every clinical object should carry:

```text
CLINICAL_ORIGINAL
CLINICAL_DERIVED
TEMPORARY_PROCESSING
RESEARCH_APPROVED
SYSTEM_ASSET
```

which maps to retention/deletion policy.

---

## 11. Authorization

Authorization happens before object storage access.

S3/SeaweedFS does not know whether a clinician is assigned to a patient.

---

## 12. Upload workflow

Preferred large-file flow:

```text
browser
 -> API: request upload
 -> authorization / limits
 -> short-lived PUT URL
 -> object storage
 -> API: finalize
 -> checksum / MIME/signature / ownership validation
 -> document metadata activated
```

A completed S3 PUT is not automatically a valid clinical document.

---

# Background Jobs

## 13. JobQueuePort

```python
class JobQueuePort(Protocol):
    async def enqueue(self, request: JobRequest) -> JobHandle: ...
    async def cancel(self, job_id: UUID) -> JobCancellationResult: ...
```

Worker registration may remain implementation-specific.

---

## 14. JobRequest

```text
job_id
job_type
payload_ref
idempotency_key
correlation_id
priority?
run_after?
```

`payload_ref` generally contains opaque entity/run IDs, not clinical text.

---

## 15. Job state

Queue technology state is technical state.

Product entities retain user-relevant state such as:

```text
ClinicalDocument.processing_status
Referral.delivery_status
FHIRExport.status
```

---

## 16. Procrastinate adapter

Potential:

```text
ProcrastinateJobQueueAdapter
```

No domain import of the Procrastinate package.

---

## 17. Celery adapter

Potential fallback:

```text
CeleryJobQueueAdapter
```

Broker configuration remains infrastructure-only.

---

## 18. Idempotent workers

Before side effects:

```text
is already complete?
does idempotency record exist?
is entity still eligible?
is consent still valid?
```

Assume duplicate delivery can happen.

---

## 19. Consent re-check

Any delayed job that sends sensitive data externally must re-check applicable consent at execution time.

---

## 20. Worker service identity

Each worker uses least privilege.

OCR worker should not receive general admin authorization.

---

# Cache

## 21. EphemeralCachePort

Only introduce if used.

```python
class EphemeralCachePort(Protocol):
    async def get(self, key: str): ...
    async def set(self, key: str, value, ttl_seconds: int): ...
    async def delete(self, key: str): ...
    async def increment(self, key: str, ttl_seconds: int): ...
```

---

## 22. Cache correctness

All cache entries may disappear at any moment.

Canonical correctness must remain.

---

## 23. Valkey adapter

Potential:

```text
ValkeyCacheAdapter
```

Production:

- authentication;
- private network;
- TLS where required;
- bounded TTL.

Do not store complete longitudinal patient records as generic shared cache entries.

---

# Domain Events / Messaging

## 24. In-process MessageBusPort

Current:

```text
InProcessMessageBus
```

Future:

```text
NatsJetStreamMessageBusAdapter
```

Reliable dispatch comes from the PostgreSQL outbox.

---

## 25. DomainEventEnvelope

```text
event_id
event_type
event_version
aggregate_type
aggregate_id
occurred_at
payload
correlation_id
causation_id?
```

Payload is minimized and versioned.

---

## 26. Outbox

The module that changes state writes its outbox row in the same transaction.

Subscribers remain idempotent.

---

# Secrets

## 27. SecretProvider

```python
class SecretProvider(Protocol):
    async def get_secret(self, ref: SecretRef) -> SecretValue:
        ...
```

---

## 28. SecretRef

```text
logical_name
environment
version?
```

Example:

```text
external/llm/api-key
```

Provider-specific paths belong in infrastructure configuration.

---

## 29. SecretValue

Secret values should not be casually printable.

Avoid dataclasses whose default `repr` reveals content.

---

## 30. Implementations

Potential:

```text
EnvironmentSecretProvider
CloudSecretProvider
OpenBaoSecretProvider
InfisicalSecretProvider
```

---

## 31. Local environment

`.env` is:

```text
developer convenience
gitignored
not production secret storage
```

`.env.example` includes names and dummy values only.

---

## 32. Secret cache

In-memory secret caching may be allowed if:

- TTL bounded;
- never written to disk;
- rotation-aware;
- logs exclude it.

---

# Observability

## 33. OpenTelemetry APIs

Use standard:

```text
tracer
meter
structured logger
```

through project observability utilities.

Do not create a vendor-specific Grafana/Datadog interface in the domain.

---

## 34. Trace allowlist

Allowed examples:

```text
app.module
app.operation
http.route
job.type
external.provider
model.name
model.version
policy.version
result.status
```

Prohibited by default:

```text
patient.name
phone
email
ABHA
transcript
OCR text
document text
prompt
LLM response
free-text diagnosis
```

---

## 35. Metric labels

Allowed:

```text
route
method
status_class
module
provider
model
result
```

Forbidden:

```text
patient_id
encounter_id
document_id
request_id
phone
email
```

---

## 36. Correlation ID

Use random correlation IDs.

Do not derive correlation IDs from patient or encounter IDs.

---

## 37. Logging

Structured logging wrapper should:

- redact known secret fields;
- omit Authorization headers;
- omit request/response bodies by default;
- avoid sensitive query strings;
- include correlation ID;
- include stable error code.

---

## 38. LLM telemetry

Allowed:

```text
provider
model
operation
latency
token counts where permitted
schema validation result
retry count
```

No prompt/response body in general observability.

---

## 39. OCR telemetry

Allowed:

```text
provider
model
page count
latency
status
confidence summary
```

No OCR text.

---

## 40. ASR telemetry

Allowed:

```text
provider
model
audio duration
language
latency
status
```

No transcript.

---

## 41. FHIR telemetry

Allowed:

```text
operation
resource_type
profile
endpoint_id
status
validation issue count
```

No full clinical Bundle.

---

# Security Pipeline

## 42. Required CI security jobs

As applicable:

```text
lint
typecheck
unit/integration tests
secret scan
filesystem/dependency vulnerability scan
container scan
IaC/config scan
SBOM generation
```

---

## 43. Trivy

Store project configuration if needed under:

```text
security/trivy.yaml
```

Pin scanner release in CI.

---

## 44. Gitleaks

Optional project config:

```text
.gitleaks.toml
```

Allowlist entries require a reason.

---

## 45. Vulnerability waivers

Potential registry:

```text
security/vulnerability-waivers.yaml
```

Entry:

```text
id
component
advisory
reason
mitigation
owner
created_at
expires_at
tracking_issue
```

CI should fail expired exceptions.

---

## 46. SBOM

Generate as a release artifact.

Do not commit huge generated SBOM files to source control by default.

---

# Deployment Profiles

## 47. Infrastructure layout

Conceptually:

```text
infra/
├── docker/
├── terraform/
├── identity/
├── storage/
├── observability/
└── security/
```

Exact layout must follow `03_REPOSITORY_STRUCTURE.md`.

---

## 48. Compose profiles

Possible:

```text
core
auth
storage
observability
fhir
research
```

No optional service should silently become part of `core`.

---

## 49. Health/readiness

Each service defines:

```text
liveness
readiness
dependency degradation behavior
```

API readiness should not fail merely because a non-critical optional service is unavailable.

---

## 50. Dependency class

Infrastructure dependencies can be classified:

```text
CRITICAL
IMPORTANT
OPTIONAL
RESEARCH
```

Examples:

```text
PostgreSQL       CRITICAL
IdP              IMPORTANT for authenticated portal
Telemetry        OPTIONAL for immediate patient flow correctness
QML worker       RESEARCH
```

---

## 51. Capability registry

Examples:

```text
auth.oidc
storage.objects
jobs.background
cache.ephemeral
telemetry.otlp
messaging.distributed
secrets.dynamic
```

Feature flag answers:

```text
Should this feature run?
```

Capability answers:

```text
Is the technical provider available?
```

Both can be required.

---

# Administrative Surfaces

## 52. Private admin UIs

Protect infrastructure UIs:

```text
Keycloak/admin
authentik/admin
SeaweedFS/admin
Grafana
OpenBao
Infisical
```

Prefer private network/VPN/admin gateway.

Do not place them beside the public patient route with weak protection.

---

## 53. Default credentials

Local-only defaults must be clearly marked.

Production mode should reject obvious placeholders:

```text
admin
password
changeme
development-secret
```

---

# Object-Storage Permissions

## 54. Separate principals

Where feasible:

```text
API presigner
document worker
backup process
storage administrator
```

No application-wide object-store super-admin credential.

---

# Worker Topology

## 55. Logical modular monolith, physical worker processes

Workers may be separate processes/containers while using the same code package.

Example:

```text
same Python application package
different entrypoint
different job subscriptions
```

This does not require microservices.

---

## 56. Queue categories

Potential:

```text
documents
language
notifications
interop
maintenance
research
```

Resource-heavy OCR/QML work should not share a general lightweight queue.

---

## 57. Research isolation

Research training jobs require:

- separate queue;
- separate worker;
- separate permissions;
- separate dataset access;
- separate resource limits.

---

# Backup & Recovery

## 58. Backup identities

Backup principal should have only the permissions required to produce/restore backups.

Avoid using application super-admin credentials.

---

## 59. Restore drills

Infrastructure specifications should require periodic restore tests.

A backup never tested for restoration is not an adequate recovery plan.

---

# Provider Replacement

## 60. Architecture fitness test

The following replacements should not require domain rewrites:

```text
Keycloak -> managed OIDC
SeaweedFS -> AWS S3
Procrastinate -> Celery
OpenBao -> cloud secret manager
Prometheus -> managed metrics
```

If replacement requires changes to clinical domain code, the boundary is wrong.

---

# Initial Implementation

## 61. First provider-independent implementations

Before external infrastructure:

```text
MockIdentityProvider
PseudonymousSessionService
LocalObjectStorageAdapter
Inline/TestJobQueueAdapter
EnvironmentSecretProvider
OpenTelemetry configured/no-op local mode
InProcessMessageBus
PostgresOutboxRepository
```

Then add external providers at the phase where they are required.

---

## 62. Definition of done for a new provider adapter

```text
[ ] adapter contract tests pass
[ ] exact version pinned
[ ] license recorded
[ ] security policy reviewed
[ ] threat model updated
[ ] secrets externalized
[ ] failure behavior tested
[ ] backup/recovery documented where stateful
[ ] observability present
[ ] PHI telemetry regression passes
[ ] deployment docs updated
[ ] rollback/replacement path documented
```

---

## 63. Final boundary rule

Third-party infrastructure is replaceable implementation detail.

SwasthyaSetu owns:

```text
clinical domain
consent
safety
resource authorization
provenance
patient context
workflow state
audit semantics
```

No external infrastructure product may silently become the product's domain model.
