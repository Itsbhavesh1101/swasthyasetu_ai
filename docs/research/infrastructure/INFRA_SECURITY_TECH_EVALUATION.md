# SwasthyaSetu AI — Infrastructure & Security Foundation Technology Evaluation

**Document ID:** `SSAI-OSS-R2D-INFRA-001`  
**Status:** Deep research / pre-implementation architecture decision  
**Version:** `0.1.0-research`  
**Review date:** 2026-10-09  
**Scope:** Identity, pseudonymous sessions, object storage, background jobs, event reliability, cache/messaging, secrets, observability, and software supply-chain security.

---

## 1. Executive decision

SwasthyaSetu should start with a deliberately small infrastructure footprint and add infrastructure only when a product capability needs it.

The current preferred direction is:

```text
Authenticated identity
    Keycloak                       preferred self-hosted candidate
    authentik                      strongest alternative
    ZITADEL                        multi-institution/B2B alternative

Anonymous / pseudonymous sessions
    SwasthyaSetu-owned SessionService
    not forced into an IdP account

Object storage
    ObjectStoragePort
      ├─ local filesystem          development/test
      ├─ managed S3/blob           preferred when cloud-managed
      └─ SeaweedFS                 preferred self-hosted candidate

Durable background work
    JobQueuePort
      ├─ Procrastinate             preferred initial candidate
      └─ Celery                    mature scale/ecosystem fallback

Reliable domain/integration events
    in-process event bus
      +
    PostgreSQL transactional outbox

Ephemeral cache / rate limiting
    Valkey                         optional only

Future distributed messaging
    NATS JetStream                 future service-extraction candidate

Secrets
    SecretProvider
      ├─ local env/CI secret store
      ├─ cloud-native secret manager
      ├─ OpenBao                   preferred self-hosted candidate
      └─ Infisical                 strong alternative

Observability
    OpenTelemetry SDK
      -> OpenTelemetry Collector
      -> Prometheus / compatible metrics backend
      -> Grafana optional operations UI
      -> log/trace backend selected later

Security pipeline
    Trivy
    Gitleaks
    SBOM
    dependency and image pinning
```

The important conclusion is what **not** to do:

```text
Do not turn local development into a 15-service platform.
Do not add Redis/Valkey merely because a library can use it.
Do not add NATS/Kafka before service extraction exists.
Do not store clinical truth in a task queue or cache.
Do not make authenticated identity a requirement for MannSetu's
pseudonymous first contact.
Do not log clinical text into observability backends.
```

---

## 2. Architectural requirements driving the research

The infrastructure selection must support SwasthyaSetu's established constraints:

- modular monolith first;
- PostgreSQL as canonical application source of truth;
- privacy-by-design;
- pseudonymous/zero-login first contact where required;
- clinician/admin RBAC;
- future authenticated patient accounts;
- document and audio processing workers;
- failure isolation;
- deterministic safety remains available during optional-provider outage;
- platform-agnostic deployment;
- replaceable external integrations;
- future institution/hospital integrations;
- auditability;
- no PHI in normal operational telemetry;
- local developer experience that Codex can reason about reliably.

A component is therefore judged not only by features but by how much architecture it forces on SwasthyaSetu.

---

## 3. Research method

For high-priority candidates, the review examined combinations of:

- repository structure;
- default-branch implementation;
- dependency/build manifests;
- tests and CI signals;
- formal security policy;
- source license and open-core boundaries;
- current release activity;
- deployment architecture;
- database dependencies;
- authentication/authorization model;
- recovery/upgrade posture;
- cloud/self-hosted options;
- ecosystem/adoption;
- replacement cost.

Stars were reviewed as an adoption signal but remain low weight.

Repository values recorded below are approximate point-in-time research snapshots and must be rechecked before production pinning.

---

## 4. Point-in-time candidate snapshot

| Project | Approx. stars | Current/recent release observed | License posture | R2-D role |
|---|---:|---|---|---|
| Keycloak | ~37k | 26.8.0 | Apache-2.0 | preferred IdP candidate |
| authentik | ~26k | 2026.8.3 | MIT core + enterprise subtree | IdP alternative |
| ZITADEL | ~15k | v4.19.4 | AGPL-3.0 + exceptions | multi-tenant alternative |
| SeaweedFS | ~35k | 4.48 | Apache-2.0 | self-hosted object storage |
| MinIO | ~61k | repository archived in 2026 | AGPL-3.0 | reject as new default |
| Procrastinate | ~1.4k | 3.10.0 | MIT | PostgreSQL job queue |
| Celery | ~29k | 5.6.3 | BSD-3-Clause | mature job fallback |
| Dramatiq | ~5k | active | LGPL family | secondary candidate |
| Taskiq | ~2k | active | MIT | watch / secondary |
| Valkey | ~27k | 9.1.2 | BSD-3-Clause | optional ephemeral cache |
| NATS Server | ~21k | 2.15.1 | Apache-2.0 | future messaging |
| OpenBao | ~8k | 2.7.1 | MPL-2.0 | self-hosted secrets |
| Infisical | ~29k | active | MIT core + enterprise subtree | secrets alternative |
| OpenTelemetry Collector | ~8k | 0.162.0 release family | Apache-2.0 | telemetry |
| Prometheus | ~66k | active | Apache-2.0 | metrics backend |
| Grafana | ~77k | active | AGPL-3.0 | operations UI |
| Trivy | ~38k | 0.75.0 | Apache-2.0 | security scanning |
| Gitleaks | ~30k | maintained for security fixes | MIT | secret scanning |

---

# Part A — Identity & Access Management

## 5. Identity is not one problem

SwasthyaSetu has different identity classes:

```text
Pseudonymous patient/session
Authenticated patient
Clinician
Clinical reviewer
Administrator
Resource/provider manager
Researcher
Service/machine identity
Kiosk/device session
```

These classes have different trust and recovery requirements.

A healthcare product should not force every class through exactly the same login workflow.

---

## 6. Recommended identity boundary

```text
Patient PWA / Clinician UI / Admin UI
                |
          Authentication
                |
      +---------+----------+
      |                    |
pseudonymous          OIDC / OAuth2
SessionService             |
      |             IdentityProviderPort
      |                    |
SwasthyaSetu           Keycloak /
session token          authentik / future IdP
      |                    |
      +---------+----------+
                |
         InternalActor
                |
     SwasthyaSetu authorization
```

The IdP answers:

```text
Who authenticated?
How did authentication occur?
What broad roles/groups were asserted?
```

SwasthyaSetu answers:

```text
May this clinician view this patient's encounter?
May this reviewer confirm this extracted medication?
May this administrator approve a self-care record?
May this researcher access this approved dataset?
```

Resource-level clinical authorization must remain inside the application policy boundary.

---

## 7. Keycloak — preferred self-hosted IdP candidate

### 7.1 Repository and ecosystem maturity

Keycloak has the strongest overall maturity signal of the self-hosted IdP shortlist:

- large community;
- long-running security-sensitive codebase;
- Apache-2.0;
- active stable release cadence;
- formal vulnerability handling;
- extensive testing;
- OIDC/OAuth2/SAML ecosystem;
- CNCF ecosystem presence;
- broad institutional adoption.

### 7.2 Capabilities relevant to SwasthyaSetu

Keycloak can provide:

- OIDC/OAuth2;
- SAML;
- user management;
- identity federation;
- MFA;
- WebAuthn/passkeys;
- service accounts;
- groups/roles;
- external identity brokering;
- realm/client configuration.

This is enough for clinician/admin authentication and future patient accounts without SwasthyaSetu implementing password storage.

### 7.3 Recommended use

Use Keycloak for:

```text
clinician login
admin login
clinical reviewer login
resource-manager login
future authenticated patient accounts
machine/client credentials where justified
institutional identity federation later
```

### 7.4 Do not use Keycloak for

Do not force:

```text
MannSetu zero-login first contact
temporary kiosk session
anonymous intake draft
```

to create persistent IdP users.

Pseudonymity is a product/privacy property and should remain a separate session capability.

### 7.5 Resource authorization warning

A token claim such as:

```json
{"roles":["CLINICIAN"]}
```

does not prove the clinician may access any patient.

The application must evaluate patient/encounter assignment and permissions.

### 7.6 Operational cost

Keycloak introduces:

- JVM/Quarkus service;
- database;
- signing-key lifecycle;
- realm/client configuration;
- admin hardening;
- backup/restore;
- security upgrades;
- OIDC integration testing.

Therefore it should be introduced when authenticated clinician/admin workflows are implemented, not just because infrastructure research chose it.

### 7.7 Security update posture

Community Keycloak should be treated as a frequently patched security component.

Production policy should include:

- exact release pin;
- release/security monitoring;
- fast security-update path;
- upgrade regression tests;
- backup before migrations.

### 7.8 R2-D decision

**PREFERRED SELF-HOSTED IDP CANDIDATE — technical spike required before final adoption.**

---

## 8. authentik — strongest Keycloak alternative

### 8.1 Strengths

authentik has:

- active 2026 development;
- strong self-hosting experience;
- OIDC/OAuth2;
- SAML;
- LDAP;
- RADIUS;
- MFA;
- Docker/Kubernetes deployment;
- formal security process;
- modern Python/Django/PostgreSQL core;
- regular external security testing claims.

### 8.2 Important privileged features

Its own security policy documents intentionally powerful administrator behavior, including:

- expressions capable of executing Python;
- blueprints with filesystem access;
- blueprint imports that can change privileged objects;
- raw HTML/script-capable prompt customization;
- configurable outbound requests that are not automatically network-filtered.

These are not necessarily defects; they define the threat model.

For SwasthyaSetu:

```text
blueprint import         privileged
policy/expression edit   privileged code-equivalent action
custom prompt edit       privileged
outbound egress          network-policy controlled
```

### 8.3 License boundary

Core is MIT, while enterprise functionality has a separate license.

Before adopting a feature, verify its exact repository/license location.

### 8.4 R2-D decision

**STRONG ALTERNATIVE TO KEYCLOAK.**

It may win the practical spike if its administration/deployment simplicity materially reduces operational risk.

---

## 9. ZITADEL

### 9.1 Strengths

ZITADEL offers:

- OIDC;
- SAML;
- SCIM;
- WebAuthn/passkeys;
- MFA;
- machine identities;
- API-first administration;
- audit/event model;
- strong multi-tenant hierarchy;
- PostgreSQL deployment.

### 9.2 Why it is not the initial default

Its strongest differentiation—native organization/multi-tenant identity—is not yet a core SwasthyaSetu requirement.

Its AGPL-oriented main license also requires more legal review than Keycloak's Apache-2.0.

### 9.3 Decision

**CONSIDER if multi-institution/B2B tenancy becomes central.**

---

## 10. Ory Kratos / Hydra

Ory offers excellent composability and clear identity/OAuth separation.

That is attractive for a highly customized identity platform, but would require more:

- UX implementation;
- component integration;
- operations;
- recovery design;
- policy wiring.

SwasthyaSetu currently benefits more from a complete IdP.

**Decision: REFERENCE / FUTURE SPECIALIZED OPTION.**

---

## 11. Pseudonymous session architecture

Implement a SwasthyaSetu-owned session service for zero-login flows.

Conceptually:

```text
create session
issue opaque/high-entropy token
expire
rotate
revoke
resume where permitted
optionally link selected data to an authenticated account
```

Do not embed clinical information in the token.

Do not treat possession of a pseudonymous token as strong proof of civil identity.

---

## 12. Privileged MFA

Clinician/admin policies should support:

- TOTP and/or WebAuthn/passkey;
- recovery;
- session expiry;
- session revocation;
- step-up authentication for sensitive administration.

Exact security policy remains a later specification decision.

---

## 13. Service identities

Each deployable worker/service should have minimum permissions.

Avoid one shared service secret for:

```text
API
OCR worker
speech worker
FHIR sidecar
notification worker
research worker
```

Use OIDC workload/client identity or deployment-native identity where practical.

---

# Part B — Object Storage

## 14. Why object storage is a security boundary

Likely high-sensitivity objects include:

- scanned prescriptions;
- lab reports;
- discharge summaries;
- other prior records;
- page images;
- derived OCR/document artifacts;
- audio where retention policy allows;
- FHIR document artifacts;
- approved research datasets/model artifacts.

Required properties:

```text
private by default
encryption
opaque identifiers
short-lived signed access
integrity checksum
retention/deletion controls
backup/recovery
auditability
replaceable provider
```

---

## 15. ObjectStoragePort

Application modules should depend on:

```text
ObjectStoragePort
```

not directly on:

```text
boto3 S3 client
Azure Blob SDK
SeaweedFS-specific client
```

Preferred implementations:

```text
LocalObjectStorageAdapter
S3ObjectStorageAdapter
CloudBlobStorageAdapter
```

---

## 16. SeaweedFS — preferred self-hosted candidate

SeaweedFS aligns well because it supports a substantial S3-compatible surface and current features relevant to health data infrastructure:

- S3 gateway;
- IAM/STS-style controls;
- OIDC integration options;
- versioning;
- Object Lock / legal-hold capabilities;
- lifecycle;
- presigned URLs;
- multipart upload;
- server-side encryption options;
- external KMS integrations;
- audit log;
- rate limiting;
- TLS/mTLS;
- replication;
- Prometheus metrics.

### Recommended deployment scenarios

SeaweedFS is most attractive for:

```text
on-prem hospital pilot
private cloud
air-gapped/private deployment
self-hosted institution
```

If production uses AWS/Azure/GCP, the managed object store may be operationally safer.

### R2-D decision

**PREFERRED SELF-HOSTED S3 CANDIDATE.**

Not mandatory in initial local development.

---

## 17. MinIO — why stars are not enough

MinIO remains extremely popular, but its upstream GitHub repository is archived/read-only in the current research snapshot and its license is AGPL-3.0.

For a new 2026 foundation, an archived upstream is a strong negative.

Existing MinIO installations can still be accessed through an S3-compatible adapter.

**Decision: REJECT AS NEW DEFAULT.**

---

## 18. Garage

Garage is technically attractive for smaller geo-distributed self-hosting, but:

- smaller ecosystem;
- AGPL-3.0;
- less benefit for our use case than SeaweedFS.

**Decision: CONSIDER for a lightweight deployment profile.**

---

## 19. Object key policy

Never build object paths with patient names or diagnoses.

Avoid:

```text
patients/bhavesh/brain-tumor-report.pdf
```

Prefer:

```text
documents/<opaque-document-id>/original
documents/<opaque-document-id>/derived/page-0001
```

Human-facing filenames are metadata and subject to normal sensitive-data policy.

---

## 20. Presigned access

Presigned URLs should be:

- short-lived;
- method-scoped;
- object-scoped;
- content constraints where possible;
- logged as an authorization event;
- generated only after application permission checks.

No permanent public URL for clinical records.

---

## 21. Storage lifecycle classes

Define policy classes such as:

```text
CLINICAL_ORIGINAL
CLINICAL_DERIVED
TEMPORARY_PROCESSING
RESEARCH_APPROVED
SYSTEM_ASSET
```

Retention/deletion logic belongs to policy, not the storage vendor.

Object Lock must not be enabled globally because immutable retention can conflict with legitimate deletion requirements.

---

# Part C — Durable Jobs & Events

## 22. Background workloads

Jobs will include:

```text
document preprocessing
OCR
ASR
translation
FHIR export
notifications
provider verification
resource expiry checks
retention purge
model inference
research/model training
```

Different workloads need different resources and deadlines.

---

## 23. Queue state is not clinical state

A queue/broker can be rebuilt or lost.

Canonical application state must remain in PostgreSQL where relevant.

Example:

```text
ClinicalDocument.processing_status
ClinicalDocument.processing_run_id
```

should not exist only inside a task broker.

---

## 24. Transactional outbox

Reliable application event pattern:

```text
BEGIN
  update canonical entity
  insert outbox_event
COMMIT
```

Then:

```text
outbox dispatcher
  -> publishes/handles
  -> subscriber idempotently processes
  -> records dispatch
```

This pattern remains valuable even if future NATS is adopted.

---

## 25. Procrastinate — strongest initial job fit

Procrastinate is a PostgreSQL-based Python task queue with:

- async and sync APIs;
- ASGI-friendly operation;
- retries;
- periodic tasks;
- locks;
- migration tests;
- integration/acceptance tests;
- production/stable package classifier.

### Why it fits

SwasthyaSetu already requires PostgreSQL.

Using PostgreSQL-backed jobs initially means:

```text
no RabbitMQ just for OCR jobs
no Redis just for background processing
fewer local services
easier transactional behavior
```

### Caution

Its project currently seeks additional maintainers, which is a bus-factor signal.

That is why `JobQueuePort` remains mandatory.

### Decision

**PREFERRED INITIAL JOB-QUEUE CANDIDATE — benchmark before final adoption.**

---

## 26. Celery

Celery remains the mature high-scale alternative.

Strengths:

- large community;
- mature routing;
- RabbitMQ/Redis/SQS/PubSub transports;
- scheduling;
- retries;
- many operational integrations.

Costs for SwasthyaSetu MVP:

- another broker;
- larger config surface;
- more infrastructure;
- more worker lifecycle complexity.

**Decision: MATURE FALLBACK.**

Adopt if Procrastinate exposes a demonstrated limitation.

---

## 27. Dramatiq

Dramatiq is solid but:

- requires RabbitMQ/Redis for normal distributed operation;
- has LGPL-family licensing;
- smaller ecosystem than Celery;
- no decisive advantage for our architecture.

**Decision: CONSIDER, not preferred.**

---

## 28. Taskiq

Taskiq is attractive for async/FastAPI use and has optional OpenTelemetry integration.

However its current package metadata still declares an Alpha development status.

For a healthcare foundation, that warrants caution.

**Decision: WATCH / SECONDARY CANDIDATE.**

---

## 29. Job payload privacy

Prefer:

```json
{
  "job_id": "...",
  "document_id": "...",
  "processing_run_id": "..."
}
```

over:

```json
{
  "patient_name": "...",
  "full_prescription_text": "...",
  "entire_transcript": "..."
}
```

Workers fetch necessary data with scoped authorization.

---

## 30. Idempotency

Assume at-least-once execution.

Any retryable job should use:

- idempotency key;
- processing run ID;
- unique constraint where appropriate;
- state transition checks;
- external idempotency support if available.

Do not design around exactly-once delivery.

---

## 31. Consent re-check

A queued referral/export/sharing operation must re-check consent at execution/send time because consent may have changed after the job was queued.

---

# Part D — Ephemeral Cache & Future Messaging

## 32. Valkey

Valkey is the preferred optional Redis-compatible direction because it has:

- permissive BSD license;
- Linux Foundation community governance;
- active releases;
- TLS support;
- large integration-test surface;
- broad ecosystem compatibility.

Potential uses:

```text
rate-limit counters
short-lived cache
ephemeral coordination
websocket/session helper
```

Hard rule:

```text
Delete all Valkey data and the clinical system should still be correct.
```

**Decision: ADOPT ONLY WHEN A REAL EPHEMERAL USE CASE APPEARS.**

---

## 33. NATS / JetStream

NATS is a strong future distributed messaging choice:

- Apache-2.0;
- CNCF;
- multi-language clients;
- active release cadence;
- strong security posture;
- JetStream durability.

But SwasthyaSetu is not starting as microservices.

Initial:

```text
in-process events
+
PostgreSQL outbox
```

Future:

```text
PostgreSQL outbox
   -> NATS JetStream
      -> separately deployed service consumers
```

**Decision: APPROVED FUTURE CANDIDATE — DO NOT DEPLOY YET.**

---

# Part E — Secrets & Key Material

## 34. Secret classes

Examples:

- database credentials;
- object-store credentials;
- OIDC client secrets;
- LLM API keys;
- BHASHINI credentials;
- ABDM credentials;
- notification provider keys;
- signing keys;
- encryption/wrapping keys;
- service-to-service credentials.

Secrets must never be:

```text
committed
placed in documentation
included in Codex prompts
logged
sent to frontend bundles
stored in test fixtures
```

---

## 35. SecretProvider

Use a provider-neutral application contract.

Development:

```text
EnvironmentSecretProvider
```

Production options:

```text
CloudSecretProvider
OpenBaoSecretProvider
InfisicalSecretProvider
```

---

## 36. OpenBao — preferred pure self-hosted candidate

OpenBao provides:

- encrypted secret storage;
- dynamic secrets;
- leases;
- renewal/revocation;
- transit encryption;
- audit;
- database credential patterns;
- PKI/key-management building blocks.

This aligns well with future hospital/private-cloud deployments.

### Operational warning

Running a secret manager securely requires:

- initialization/recovery;
- root/admin governance;
- HA;
- backup;
- policy management;
- audit;
- authentication methods;
- disaster recovery.

Using OpenBao in a one-developer MVP just to avoid a `.env` file would increase risk, not reduce it.

### Decision

**PREFERRED SELF-HOSTED SECRET MANAGER WHEN PRODUCTION REQUIREMENTS JUSTIFY IT.**

---

## 37. Infisical

Infisical provides excellent developer experience around:

- secret projects/environments;
- versioning;
- rotation;
- dynamic secrets;
- agents;
- Kubernetes integration;
- PKI;
- KMS;
- machine identity;
- audit;
- secret scanning.

Core is permissively licensed while enterprise functionality is separated.

**Decision: STRONG ALTERNATIVE.**

Before relying on a feature, confirm whether it is OSS or enterprise-only.

---

## 38. Secret-manager timing

Recommended:

```text
local:
  .env ignored by git
  .env.example contains names/dummies only

CI:
  CI platform secret store

pilot/production:
  selected cloud secret manager
  OR OpenBao
  OR Infisical
```

This preserves security without making every local command depend on a secret-management cluster.

---

# Part F — Observability

## 39. OpenTelemetry — architecture standard

OpenTelemetry is the correct contract because it is:

- vendor-neutral;
- cloud-neutral;
- supports traces, metrics and logs;
- widely instrumented across Python/JS/infrastructure;
- compatible with many backends.

Use:

```text
FastAPI/worker instrumentation
        |
       OTLP
        |
OpenTelemetry Collector
        |
   selected backend(s)
```

### Decision

**ADOPT OpenTelemetry APIs and OTLP.**

---

## 40. Collector distribution

The standard Collector is deliberately minimal.

Collector Contrib provides many production-useful integrations.

Recommended:

```text
Collector Contrib initially
+
explicit allowlist of enabled receivers/processors/exporters
```

Do not enable every component.

A custom smaller distribution can be considered later if attack surface or image size warrants it.

---

## 41. Grafana Alloy

Alloy is a strong OpenTelemetry/Prometheus-oriented distribution.

It is useful if the operations stack standardizes on Grafana products.

However the application contract should remain:

```text
OTLP / OpenTelemetry
```

not:

```text
Grafana-specific API
```

**Decision: CONSIDER as deployment distribution.**

---

## 42. Prometheus

Prometheus is the preferred self-hosted metrics backend for pilot/development environments.

Use it for low-cardinality operational metrics.

Examples:

```text
HTTP latency
5xx rate
job duration
job failure count
external-provider latency
DB pool pressure
```

**Decision: ADOPT for self-hosted metrics.**

---

## 43. Grafana

Grafana is a mature operations UI.

SwasthyaSetu may use it for:

- dashboards;
- operational alerts;
- infrastructure views.

The application must not depend on Grafana for correctness.

**Decision: ADOPT/CONSIDER as optional operations UI.**

---

## 44. Loki and trace backends

Do not deploy Loki/Tempo merely because Grafana exists.

Start with:

- structured JSON logs;
- OpenTelemetry Collector;
- metrics.

Choose log/trace storage when retention/query requirements become concrete.

**Decision: DEFER dedicated log backend.**

---

## 45. PHI-safe telemetry

Normal telemetry must not contain:

```text
patient name
phone/email
ABHA identifier
full conversation
ASR transcript
OCR text
medical document body
LLM prompt
LLM response
free-text diagnosis
free-text medication
```

Safe examples include:

```text
module
operation
provider
model name/version
status
latency
error code
policy version
feature-flag version
```

---

## 46. Metrics cardinality

Never use:

```text
patient_id
encounter_id
document_id
request_id
email
```

as Prometheus labels.

High-cardinality correlation IDs belong in controlled traces/logs, not metric dimensions.

---

## 47. Audit is different from observability

Authoritative audit records include:

- actor;
- action;
- resource;
- time;
- consent/security events.

Prometheus/Grafana/Loki are operational infrastructure and do not replace the product/security audit ledger.

---

# Part G — Software Supply Chain

## 48. Trivy

Trivy is the preferred broad CI scanner because it can cover:

- filesystem dependencies;
- container images;
- vulnerabilities;
- misconfigurations;
- secrets;
- SBOM output;
- IaC/config.

**Decision: ADOPT IN CI.**

Use pinned stable releases, not moving/canary artifacts.

---

## 49. Gitleaks

Gitleaks remains an excellent focused secret scanner.

The project currently describes itself as feature-complete with future work focused on security fixes.

For a narrow scanner, feature-complete is not itself a negative.

Use:

```text
pre-commit
pull request
protected branch
scheduled/full-history scan
```

**Decision: ADOPT, WITH PERIODIC MAINTENANCE RE-EVALUATION.**

---

## 50. SBOM

Every production image should produce an SBOM, e.g. SPDX or CycloneDX.

Initial source:

```text
Trivy SBOM
```

or Syft if later needed.

Do not add multiple SBOM generators until a real gap exists.

---

## 51. Vulnerability waiver policy

A waiver should require:

```text
CVE/advisory
component/version
why not currently exploitable or why update is blocked
mitigation
owner
tracking issue
created date
expiry date
```

No permanent wildcard ignore.

Expired waiver should fail CI.

---

## 52. Container baseline

Production images should aim for:

- exact base versions;
- digest pinning where practical;
- non-root process;
- minimal packages;
- no embedded secrets;
- health checks;
- read-only filesystem where feasible;
- vulnerability scan;
- SBOM.

---

# Part H — Minimal Infrastructure Footprint

## 53. Phase-1 local development

Default developer startup should look roughly like:

```text
PostgreSQL
FastAPI
Next.js app(s)
background worker process
local object-storage directory
```

Optional profile:

```text
OpenTelemetry Collector
Prometheus
Grafana
```

Do not require on day one:

```text
Keycloak
SeaweedFS
Valkey
NATS
OpenBao
Kubernetes
Loki
```

---

## 54. Why this matters for Codex

A smaller environment improves:

- repeatable Codex commands;
- test reliability;
- local startup;
- debugging;
- dependency isolation;
- architecture comprehension.

Ports should exist before providers are activated.

---

## 55. Suggested Docker Compose profiles

Conceptually:

```text
core
auth
storage
observability
fhir
ai-workers
research
```

A developer working on an API validation rule should not have to boot every AI and infrastructure service.

---

## 56. Pilot footprint

A pilot will likely need:

```text
PostgreSQL
FastAPI
Next.js
durable worker
private object storage
IdP
production secret storage
OTel Collector
metrics
backup
TLS ingress
```

Specific products remain deployment-dependent.

---

# Part I — Failure Isolation

## 57. IdP outage

Expected behavior:

- new authenticated login fails clearly;
- authenticated request behavior follows token-expiry policy;
- pseudonymous intake may remain available;
- crisis/urgent safety resources must not disappear merely because the IdP is unavailable.

---

## 58. Object-store outage

Expected:

- new document/audio uploads unavailable;
- previously loaded in-memory clinical safety logic continues;
- text-based intake can continue;
- queued processing remains recoverable.

---

## 59. Worker outage

Expected:

- jobs remain pending;
- API reports processing queued/degraded;
- no silent document-processing success;
- clinical safety route does not depend on asynchronous worker completion.

---

## 60. Telemetry outage

Expected:

- application continues;
- telemetry may buffer/drop within bounded limits;
- no request failure solely because Collector/Grafana is down.

---

## 61. Secret-manager outage

Expected behavior depends on leased credential lifetime.

Systems should:

- avoid printing secret values in errors;
- fail closed when a required credential cannot be obtained;
- continue with valid already-issued credentials only where policy permits.

---

# Part J — Backup, Encryption & Isolation

## 62. Backup scope

Back up according to importance:

```text
canonical PostgreSQL        critical
clinical object storage     critical
IdP database/config         important once used
FHIR repository DB          important if persistent
secret manager              provider-specific critical recovery
telemetry                   lower clinical priority
```

---

## 63. Restore drills

"Backup configured" is not enough.

Pilot/production process should periodically test:

```text
restore database
restore objects
restore identity configuration
verify checksums/counts
verify selected user login
verify app startup
```

---

## 64. Encryption

At rest:

- DB volume/storage encryption;
- object-store encryption;
- backup encryption;
- secret-manager encryption.

In transit:

- TLS at public boundaries;
- private network isolation;
- mTLS where threat model/deployment justifies it.

Field-level encryption is a separate threat-model decision.

---

## 65. Environment isolation

At minimum:

```text
local
test
staging/pilot
production
```

Never share production:

```text
database
object bucket
IdP realm/tenant
API keys
signing keys
encryption keys
```

with staging.

---

## 66. Research isolation

ML/QML research must not gain broad production clinical storage access.

Research services use:

- approved datasets;
- separate object paths/buckets;
- separate credentials;
- explicit export workflow.

---

# Part K — Network & Egress

## 67. Private-only services

Normally private:

```text
PostgreSQL
Valkey
FHIR sidecar
object-storage admin API
OpenBao / Infisical backend
worker control surfaces
Prometheus scrape endpoints
```

Public:

```text
approved patient/clinician/admin ingress
approved interoperability ingress
```

---

## 68. Egress policy

AI/document systems can become exfiltration paths.

Production should support explicit outbound destinations for:

```text
approved LLM provider
BHASHINI where approved
ABDM endpoints
notification provider
approved provider directory source
```

Local model workers should not receive unrestricted internet if they do not need it.

---

# Part L — Final R2-D Decisions

## 69. Component decision matrix

| Capability | Preferred R2-D decision |
|---|---|
| Authenticated IdP | **Keycloak — preferred candidate** |
| IdP alternative | **authentik** |
| Multi-tenant IAM alternative | **ZITADEL** |
| Pseudonymous sessions | **SwasthyaSetu-owned** |
| Object storage contract | **provider-neutral/S3-oriented** |
| Self-hosted object storage | **SeaweedFS** |
| MinIO for new deployment | **reject as default** |
| Background jobs | **Procrastinate candidate** |
| High-scale/mature job fallback | **Celery** |
| Reliable events | **PostgreSQL outbox** |
| Ephemeral cache | **Valkey only when needed** |
| Future service messaging | **NATS JetStream** |
| Self-hosted secrets | **OpenBao when justified** |
| Secrets alternative | **Infisical** |
| Telemetry standard | **OpenTelemetry** |
| Metrics | **Prometheus** |
| Operations UI | **Grafana optional** |
| Dedicated logs | **defer** |
| Vulnerability/misconfig scanner | **Trivy** |
| Secret scanner | **Gitleaks** |

---

## 70. Mandatory architecture rules

```text
INFRA-001  IdP authenticates; SwasthyaSetu performs resource authorization.
INFRA-002  Pseudonymous patient sessions are first-class and do not require an IdP account.
INFRA-003  Object storage contains bytes; PostgreSQL retains canonical metadata.
INFRA-004  Queue state never becomes clinical source of truth.
INFRA-005  Valkey/cache may disappear without corrupting correctness.
INFRA-006  Domain-event reliability begins with PostgreSQL outbox.
INFRA-007  NATS is future infrastructure, not current default.
INFRA-008  Secrets are accessed through a provider boundary.
INFRA-009  OpenTelemetry is the observability contract.
INFRA-010  General telemetry excludes PHI by default.
INFRA-011  Audit records are separate from operational telemetry.
INFRA-012  Every production dependency is pinned and security-scanned.
INFRA-013  Optional infrastructure failure must not remove core safety behavior.
INFRA-014  Research approval is not permission to add every service to Docker Compose.
```

---

## 71. Codex restrictions

Codex must **not** infer from this research that it should:

- install Keycloak during the first repository-skeleton task;
- add Valkey/Redis without a specific requirement;
- introduce NATS/Kafka early;
- add SeaweedFS to the default local stack;
- add OpenBao to every developer startup;
- store clinical data inside Celery/Valkey task metadata;
- log prompts/transcripts/OCR output into OTel;
- use patient identifiers as Prometheus labels;
- create public buckets;
- clone/fork upstream infrastructure projects into our monorepo.

Instead, Codex should first implement SwasthyaSetu-owned interfaces, mocks, local adapters and tests.

---

## 72. Recommended implementation timing

```text
Repository/Foundation
  -> interfaces, mocks, local storage, structured logging, security CI

Identity phase
  -> Keycloak vs authentik technical spike
  -> choose IdP

Document phase
  -> activate object-storage adapter/provider

Async processing phase
  -> Procrastinate vs Celery spike
  -> choose durable task implementation

Pilot hardening
  -> production secret manager
  -> OTel collector/backend
  -> backups/restore
  -> MFA/security hardening

Future service extraction
  -> NATS JetStream only if justified
```

---

## 73. R2-D conclusion

The research reinforces the modular-monolith plan rather than pushing SwasthyaSetu toward infrastructure sprawl.

The best foundation is the one whose complexity we can delay while preserving clean interfaces today.
