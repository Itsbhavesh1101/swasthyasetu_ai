# SwasthyaSetu AI — Infrastructure & Security Technical Spike Plan

**Document ID:** `SSAI-OSS-R2D-INFRA-002`  
**Status:** Technical-spike specification  
**Version:** `0.1.0-research`  
**Review date:** 2026-10-09

---

## 1. Objective

Validate R2-D recommendations with reproducible engineering evidence before production adoption.

The spike is divided into:

```text
A. Identity
B. Object storage
C. Jobs / events / optional cache
D. Secrets
E. Observability and software-supply-chain security
```

All test data must be synthetic or explicitly approved non-production data.

---

# A — Identity Spike

## 2. Candidates

Mandatory comparison:

```text
Keycloak
authentik
```

Optional:

```text
ZITADEL
```

Only add ZITADEL to hands-on evaluation if multi-institution tenancy becomes near-term or Keycloak/authentik reveal a blocking gap.

---

## 3. Synthetic clients

Configure:

```text
patient-web-authenticated
clinician-web
admin-web
backend-api
test-machine-client
```

Pseudonymous patient sessions are tested through the SwasthyaSetu session service and not represented as IdP users.

---

## 4. OIDC flow

Verify:

- Authorization Code + PKCE;
- issuer validation;
- JWKS validation;
- audience validation;
- state/nonce;
- callback handling;
- refresh where allowed;
- logout;
- session expiry.

---

## 5. MFA

Test:

```text
TOTP
WebAuthn/passkey if supported
recovery flow
MFA reset
admin enforcement
```

Measure configuration complexity and recovery safety.

---

## 6. Role mapping

Synthetic roles:

```text
PATIENT
CLINICIAN
CLINICAL_REVIEWER
ADMIN
RESOURCE_MANAGER
RESEARCHER
```

Token roles/groups should map into an internal actor model.

Do not map IdP claims directly to unrestricted database access.

---

## 7. Resource authorization

Test:

```text
Clinician A has CLINICIAN role
but is not authorized for Patient B
```

API must deny Patient B.

This test proves:

```text
authentication role != resource-level authorization
```

---

## 8. Revocation

Test:

- disable user;
- remove role;
- reset credentials;
- revoke sessions;
- stale access token;
- refresh attempt.

Document expected token lifetime behavior.

---

## 9. Signing-key rotation

Rotate IdP signing key.

Verify:

```text
JWKS refresh
new-token verification
old-token grace behavior
no unnecessary app restart
```

---

## 10. IdP outage

Stop IdP.

Verify:

- new login fails cleanly;
- API behavior with existing unexpired JWT follows policy;
- clinician UI shows controlled error;
- pseudonymous patient flow remains usable where designed;
- urgent/crisis resources remain reachable.

---

## 11. Backup / restore

For the chosen IdP:

1. create users/roles/client/MFA fixture;
2. backup DB/config;
3. destroy environment;
4. restore;
5. login;
6. verify roles;
7. verify MFA;
8. verify client configuration.

---

## 12. Upgrade test

Test current selected stable -> next candidate stable.

Verify:

```text
schema migration
users
roles/groups
OIDC clients
signing keys
MFA
logout
custom theme if later used
```

---

## 13. Identity scoring

| Category | Weight |
|---|---:|
| Security/OIDC/MFA correctness | 25% |
| Operational simplicity | 15% |
| Upgrade/maintenance | 15% |
| Federation/authorization fit | 15% |
| Backup/recovery | 10% |
| Automation/API | 10% |
| License/governance | 5% |
| Community/adoption | 5% |

---

# B — Object Storage Spike

## 14. Candidates

```text
Local filesystem adapter   baseline
SeaweedFS                  self-hosted candidate
Managed object store       if cloud target is selected
```

Garage is optional.

MinIO is excluded from new-default selection because current upstream is archived.

---

## 15. Required contract

Every implementation must support the subset required by `ObjectStoragePort`:

```text
put
get
head
delete
presign_upload
presign_download
checksum metadata
```

Multipart/large uploads are required for the production adapter if file limits make them necessary.

---

## 16. Privacy

Generated object keys must not contain synthetic PHI canaries such as:

```text
TEST_PATIENT_NAME_9382
TEST_PHONE_999999
TEST_DIAGNOSIS_X
```

---

## 17. Access control

Verify:

```text
anonymous GET -> denied
anonymous LIST -> denied
admin interface -> not public
signed GET -> permitted before expiry
signed GET -> denied after expiry
signed PUT -> allowed only for intended key
wrong method -> denied
```

---

## 18. File policy

Attempt:

- valid PDF;
- JPEG/PNG;
- executable renamed `.pdf`;
- invalid signature;
- oversized upload.

Remember: storage accepts bytes; SwasthyaSetu performs document/file security validation.

---

## 19. Encryption

Where provider supports it, verify:

```text
TLS
server-side encryption
KMS integration
backup encryption
```

Record exact guarantee rather than assuming "S3 compatible" implies encryption.

---

## 20. Versioning/deletion

Test:

- initial object;
- overwrite/new version;
- delete marker;
- full purge;
- derived artifact purge.

Verify retention policy can satisfy project deletion requirements.

---

## 21. Integrity

Record:

```text
SHA-256
size
content type
provider metadata
```

Do not assume ETag always equals MD5.

---

## 22. Failure tests

Simulate:

```text
timeout
server unavailable
partial multipart upload
revoked credential
disk full/quota
missing object
```

Expected:

- typed error;
- no false success;
- resumable/retryable state where appropriate.

---

## 23. Basic performance

Use synthetic:

```text
10 MB PDF
100 MB document bundle
100 small page images
concurrent uploads/downloads
```

Measure latency and memory.

Do not optimize for billion-object scale before a requirement exists.

---

# C — Jobs, Outbox and Optional Cache

## 24. Queue candidates

Primary:

```text
Procrastinate
Celery
```

Dramatiq/Taskiq remain paper alternatives unless a primary candidate exposes a blocker.

---

## 25. Representative jobs

Implement synthetic tasks:

```text
document.parse
ocr.extract
speech.transcribe
fhir.export
notification.send
retention.purge
```

No real PHI.

---

## 26. Transactional enqueue

Test crashes:

```text
before DB commit
after DB commit
before worker receives
after worker receives
before success acknowledgement
```

No canonical entity should get stuck in an unrecoverable invisible state.

---

## 27. Outbox

Test separately:

```text
canonical entity update
+
outbox event
same transaction
```

Then:

```text
publish
crash before dispatched marker
restart
re-publish
subscriber deduplicates
```

At-least-once delivery is expected.

---

## 28. Retry

Simulate:

```text
network timeout
HTTP 429
HTTP 503
GPU unavailable
permanent invalid input
```

Verify:

- bounded attempts;
- backoff;
- no retry of permanent validation error;
- final failure state.

---

## 29. Idempotency

Execute same job twice.

Verify no duplicate:

```text
referral
notification where idempotency required
FHIR export
document extraction run
provider verification state
```

---

## 30. Worker crash

Kill worker:

- mid-compute;
- after external side effect;
- before job ack.

Document recovery.

---

## 31. Payload privacy

Inspect queue table/broker.

Task payloads should use opaque IDs instead of full clinical content.

---

## 32. Job observability

Emit:

```text
job type
attempt
duration
status
error code
correlation id
```

Do not emit clinical text.

---

## 33. Job scoring

| Category | Weight |
|---|---:|
| Durability/crash semantics | 25% |
| Transactional fit | 20% |
| Retry/idempotency controls | 15% |
| Operational simplicity | 15% |
| Async/FastAPI fit | 10% |
| Observability | 5% |
| Maintenance | 5% |
| License/community | 5% |

---

## 34. Procrastinate adoption criterion

Choose Procrastinate if:

```text
transactional enqueue is clean
worker recovery is acceptable
PostgreSQL load is acceptable
periodic tasks meet requirements
locks/retries are sufficient
migration/upgrade is manageable
```

Reject if maintainership or feature gaps create unacceptable operational risk.

---

## 35. Celery adoption criterion

Choose Celery instead if the application genuinely needs:

- broker-scale routing;
- proven distributed worker patterns;
- specialized transports;
- mature operational integrations that justify a broker.

---

## 36. Valkey

Only test once a concrete cache/rate-limit need exists.

Test:

```text
TTL
eviction
restart
TLS
authentication
rate counter
```

Then delete all cache data and prove application correctness remains intact.

---

## 37. NATS

Do not run this spike during modular-monolith MVP.

Trigger criteria:

```text
multiple independently deployed services
+
real cross-service reliable event transport need
```

Then test JetStream:

- durable consumer;
- ack/redelivery;
- deduplication;
- retention;
- TLS/auth;
- outbox integration.

---

# D — Secrets

## 38. Candidates

Self-hosted:

```text
OpenBao
Infisical
```

Managed cloud secret manager may be preferred if a cloud is selected.

---

## 39. Synthetic secret set

Use only dummy credentials:

```text
database password
object-storage key
OIDC client secret
external API key
signing key fixture
```

---

## 40. Static retrieval

Verify:

```text
service authenticates
allowed path works
unallowed path fails
secret value is not logged
```

---

## 41. Dynamic DB credential

Where supported:

1. request short-lived PostgreSQL credential;
2. connect;
3. verify least privilege;
4. wait/force expiry;
5. verify revocation.

---

## 42. Rotation

Rotate dummy:

```text
API key
DB password
```

Record whether services can refresh without unsafe restart behavior.

---

## 43. Secret-manager outage

Test:

- startup without manager;
- manager outage after service starts;
- lease renewal failure;
- expiry;
- recovery.

Document fail-open/fail-closed behavior.

---

## 44. Audit

Secret manager audit should show:

```text
service identity
secret path/logical name
operation
time
success/failure
```

Never secret content.

---

## 45. Backup/recovery

Practice provider-specific backup/restore.

A secrets platform is not acceptable if we cannot recover it reliably.

---

# E — Observability & Supply Chain

## 46. OpenTelemetry

Instrument:

```text
FastAPI request
PostgreSQL operation
background job
HTTP call to mock provider
```

Generate trace + metrics + structured logs through Collector.

---

## 47. PHI canary

Use synthetic forbidden strings:

```text
TEST_PATIENT_NAME_9382
TEST_ABHA_1234
TEST_MEDICATION_SECRET
TEST_TRANSCRIPT_SECRET
```

Send them through normal application workflows.

Search:

```text
collector output
metrics backend
dashboard backend
log output
trace backend
CI artifacts
```

The test fails if they appear where policy prohibits them.

---

## 48. Metric cardinality

Create 10,000 synthetic patients/requests.

Series count must not grow by patient.

Explicitly reject labels:

```text
patient_id
document_id
encounter_id
email
phone
```

---

## 49. Collector outage

Stop Collector.

The API and worker must continue.

Measure:

```text
latency
memory/backpressure
warnings
dropped telemetry
```

---

## 50. Initial metrics

Examples:

```text
http_requests_total
http_request_duration_seconds
db_pool_wait_seconds
job_started_total
job_failed_total
job_duration_seconds
external_provider_requests_total
external_provider_latency_seconds
safety_policy_evaluations_total
```

---

## 51. Dashboard smoke test

One operational dashboard should show:

```text
API latency/error rate
job queue/failure
DB saturation
external-provider failures
```

Do not put patient-level clinical analytics into the operations dashboard by default.

---

## 52. Trivy

Run in CI:

```text
trivy fs
trivy image
trivy config
trivy sbom
```

Illustrative initial policy:

```text
CRITICAL -> block
HIGH -> block or time-bounded reviewed waiver
MEDIUM -> report/triage
```

Final thresholds belong to engineering/security standards.

---

## 53. Vulnerability waiver

Required fields:

```text
advisory/CVE
component
reason
exploitability analysis
mitigation
owner
created_at
expires_at
tracking issue
```

Expired waiver fails CI.

---

## 54. Gitleaks

Test:

```text
pre-commit
PR
full history
```

Seed fake keys and prove detection.

Reports should redact values.

---

## 55. SBOM

Generate SPDX or CycloneDX per production container.

Associate:

```text
git commit
image digest
build timestamp
```

Store as release artifact.

---

## 56. Docker Compose profiles

Test optional profiles such as:

```text
core
auth
storage
observability
fhir
research
```

`core` must remain the simplest common developer setup.

---

## 57. Local Windows/Docker Desktop test

Validate:

```text
PostgreSQL
FastAPI
worker
local object storage
optional Keycloak
optional observability
```

Document any Linux-specific functionality clearly.

---

## 58. Resource budget

Record idle/local resource use for optional stack:

```text
Postgres
Keycloak/authentik
SeaweedFS
OTel Collector
Prometheus
Grafana
```

Do not make a typical developer laptop run all optional components continuously.

---

# Security Acceptance

## 59. Pilot checklist

Before pilot:

```text
[ ] no production default passwords
[ ] TLS/ingress strategy documented
[ ] secrets outside source control
[ ] admin MFA enabled
[ ] object storage private
[ ] PostgreSQL private
[ ] queue payload minimized
[ ] telemetry PHI-canary passes
[ ] Trivy policy passes
[ ] Gitleaks passes
[ ] SBOM produced
[ ] canonical DB backup tested
[ ] object backup/restore tested
[ ] IdP backup/restore tested
[ ] failure/degraded modes tested
```

---

## 60. Required output

Technical spike should produce:

```text
INFRA_SPIKE_RESULTS.md
identity_comparison.csv
storage_results.csv
job_results.csv
secrets_results.csv
telemetry_phi_canary_report.txt
security_scan_summary.json
INFRA_SELECTION.json
```

---

## 61. Final selection rule

Select the smallest infrastructure configuration that passes:

```text
security
privacy
recovery
failure isolation
reliability
developer operability
```

More features and more stars do not automatically mean a better foundation.
