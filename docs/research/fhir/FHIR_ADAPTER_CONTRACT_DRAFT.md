# SwasthyaSetu AI — FHIR Adapter & Gateway Contract Draft

**Document ID:** `SSAI-OSS-R2C-FHIR-003`  
**Status:** Research-derived draft  
**Feeds:** `20_FHIR_MAPPING_SPEC.md`, `21_ABDM_INTEGRATION_SPEC.md`, `13_AI_ORCHESTRATION_SPEC.md`

---

# 1. Architectural refinement

Replace the too-generic idea of one `FHIRProvider` with four explicit contracts:

```text
FHIRMapper
FHIRValidationPort
FHIRRepositoryPort
FHIRRemoteClientPort
```

An application-layer:

```text
FHIRGatewayService
```

orchestrates them.

---

# 2. FHIRMapper

This is SwasthyaSetu-owned.

Conceptual API:

```python
class FHIRMapper(Protocol):
    def export_resource(
        self,
        source: DomainObject,
        context: FHIRMappingContext,
    ) -> FHIRResourceEnvelope:
        ...

    def import_resource(
        self,
        resource: dict,
        context: FHIRImportContext,
    ) -> FHIRImportCandidate:
        ...
```

No third-party server owns mapping semantics.

---

# 3. FHIRMappingContext

Fields may include:

```text
fhir_version
implementation_guide
implementation_guide_version
profile
patient_id
encounter_id?
institution_id?
purpose
language?
export_policy_version
```

---

# 4. FHIRResourceEnvelope

```text
resource_type
profile_urls[]
resource
source_refs[]
mapping_version
warnings[]
```

`resource` is FHIR JSON.

---

# 5. Mapping version

Every mapping should carry:

```text
mapping_id
mapping_version
```

Example:

```text
Patient -> ABDMPatient / 1.0.0
ObservationLab -> ABDMObservation / 1.0.0
```

Mapping changes require regression tests.

---

# 6. FHIRValidationPort

Conceptual:

```python
class FHIRValidationPort(Protocol):
    async def validate(
        self,
        request: FHIRValidationRequest,
    ) -> FHIRValidationResult:
        ...
```

---

# 7. FHIRValidationRequest

```text
fhir_version
resource_or_bundle
profile_urls[]
implementation_guide_packages[]
validation_mode
trace_id
```

Validation mode:

```text
STRUCTURAL
PROFILE
PROFILE_AND_TERMINOLOGY
```

---

# 8. FHIRValidationResult

```text
valid
issues[]
validator_metadata
```

Issue:

```text
severity
code
diagnostics
location[]
expression[]
```

Validator metadata:

```text
provider
adapter_version
engine_version
fhir_version
packages[]
```

---

# 9. HAPI validation adapter

```text
HapiFhirValidationAdapter
```

Potential transport:

```text
private HTTP endpoint
or dedicated validation operation
```

Do not import HAPI Java types into Python domain code.

---

# 10. Validation blocking policy

The adapter reports issues.

A SwasthyaSetu policy decides whether an issue is:

```text
BLOCKING
WARNING
INFORMATIONAL
```

Do not bury policy inside HAPI-specific code.

---

# 11. FHIRRepositoryPort

Only needed if persistent FHIR storage/query is required.

```python
class FHIRRepositoryPort(Protocol):
    async def create(...): ...
    async def update(...): ...
    async def read(...): ...
    async def search(...): ...
    async def transaction(...): ...
    async def capability_statement(...): ...
```

---

# 12. Repository types

Possible implementations:

```text
HapiFhirRepositoryAdapter
MedplumFhirRepositoryAdapter
ExternalFhirRepositoryAdapter
InMemoryFhirRepositoryAdapter  # tests only
```

---

# 13. Repository is not domain storage

Application code must not perform:

```text
FHIRRepositoryPort.search("Observation")
```

as a substitute for domain repositories unless the use case is specifically interoperability.

Internal clinical screens should normally read SwasthyaSetu's canonical domain model.

---

# 14. FHIRRemoteClientPort

Purpose: connect to hospital/partner FHIR servers.

```python
class FHIRRemoteClientPort(Protocol):
    async def capability_statement(...): ...
    async def read(...): ...
    async def search(...): ...
    async def create(...): ...
    async def transaction(...): ...
```

---

# 15. Remote endpoint configuration

```text
endpoint_id
base_url
fhir_version
auth_type
tenant/institution
timeout_profile
retry_profile
allowed_operations[]
enabled
```

Secrets are referenced indirectly.

---

# 16. Authentication types

Potential future support:

```text
NONE
BEARER_TOKEN
CLIENT_CREDENTIALS
SMART_BACKEND_SERVICES
SMART_APP_LAUNCH
CUSTOM_ABDM
```

Exact implementation is deferred.

---

# 17. ABDM transport separation

ABDM APIs are not simply "a FHIR server".

Keep:

```text
ABDMProvider
```

separate from:

```text
FHIRValidationPort
```

The ABDM adapter can use FHIR mapper/validator output as its payload.

---

# 18. FHIRGatewayService

Conceptual use case:

```python
class FHIRGatewayService:
    async def build_and_validate_abdm_document(...):
        ...
```

Flow:

```text
authorization
consent
snapshot internal facts
map
assemble document/bundle
validate
return artifact
```

Transport happens separately.

---

# 19. Export snapshot

FHIR export should record an immutable logical snapshot:

```text
export_id
patient_id
encounter_id?
source_versions
mapping_versions
policy_version
fhir_version
ig_version
created_at
```

This supports reproducibility.

---

# 20. Export statuses

```text
DRAFT
MAPPED
VALIDATION_FAILED
VALIDATED
READY_TO_SEND
SENT
FAILED
CANCELLED
```

---

# 21. Validation failure behavior

Do not send a resource/bundle that fails required validation unless a specific governed exception exists.

Store:

```text
validation result
mapping version
IG version
```

for debugging.

---

# 22. Import pipeline

```text
receive FHIR
  |
structural/profile validation
  |
source/provenance record
  |
mapping to import candidates
  |
deduplication/reconciliation
  |
human/system review rules
  |
canonical domain update
```

Never directly deserialize an external FHIR resource into authoritative domain rows.

---

# 23. FHIRImportCandidate

```text
candidate_id
resource_type
source_endpoint
source_resource_id
source_version?
candidate_facts[]
provenance
warnings[]
verification_state
```

Default:

```text
NEEDS_CONFIRMATION
```

unless an approved trusted-source rule says otherwise.

---

# 24. Idempotency

Outbound:

```text
export id
stable business identifier
remote transaction identifier
```

Inbound:

```text
endpoint
resourceType
id
versionId
```

where available.

Avoid duplicate import.

---

# 25. Provenance rules

Maintain both:

```text
technical exchange provenance
clinical fact provenance
```

They are related but distinct.

---

# 26. `meta.profile`

Generated resources should include approved profile URLs where the mapping claims profile conformance.

Do not add a profile URL merely to make validation "look" compliant.

---

# 27. FHIR version registry

Configuration:

```text
FHIR_R4_4_0_1
FHIR_R4B_4_3_0
FHIR_R5_5_0_0
```

Initial enabled export:

```text
FHIR_R4_4_0_1
```

---

# 28. Implementation-guide registry

```text
id
package_id
version
fhir_version
status
checksum
source
installed_at
approved_at?
```

Status:

```text
PREVIEW
CURRENT
DEPRECATED
RETIRED
```

---

# 29. ABDM current/preview

Production should use:

```text
CURRENT published package
```

Preview packages:

```text
validation compatibility only
```

until explicitly promoted.

---

# 30. Package loading

Never download an IG dynamically because an inbound resource references it.

Install approved packages in advance.

---

# 31. Terminology abstraction

Potential:

```text
TerminologyValidationPort
```

if terminology complexity grows.

Initially it may remain behind the FHIR validator.

Do not leak HAPI-specific terminology classes.

---

# 32. FHIR identifiers

Create central mapping rules for:

```text
patient internal UUID
external MRN
ABHA identifier
encounter ID
document ID
provider ID
```

Never expose a database primary key where a different stable identifier is required without policy.

---

# 33. Reference construction

Avoid ad hoc strings across modules.

Use a helper:

```text
FHIRReferenceBuilder
```

which knows resource type + logical ID only.

It does not fetch domain data.

---

# 34. Bundle builder

Implement a SwasthyaSetu-owned:

```text
FHIRDocumentBundleBuilder
```

which takes already-mapped resources.

Responsibilities:

```text
entry ordering
fullUrl generation
Composition/document requirements
reference closure
deduplication
```

---

# 35. Mapping Patient

Potential fields:

```text
identifier
name
telecom where consented/required
gender / sex mapping only if approved
birthDate
address only if required/consented
communication language
```

Do not export more than required.

---

# 36. Mapping Encounter

Potential:

```text
identifier
status
class
subject
period
serviceProvider
participants where appropriate
```

Final exact mapping belongs in FHIR mapping spec.

---

# 37. Mapping Observation

Need:

```text
status
code
subject
encounter
effective[x]
value[x]
unit/system/code
referenceRange
interpretation where authoritative
```

Do not generate interpretation from OCR uncertainty alone.

---

# 38. Mapping AllergyIntolerance

Only map accepted allergy records according to verification policy.

Do not convert every "medicine caused discomfort" free-text mention into confirmed AllergyIntolerance.

---

# 39. Mapping MedicationRequest

Only actual medication orders/prescriptions should become MedicationRequest.

Historical patient-reported medication may map differently, e.g. MedicationStatement in R4 where appropriate.

Exact policy must be defined.

---

# 40. Mapping Condition

Hard rule:

```text
model risk != Condition
symptom != Condition
safety route != Condition
unconfirmed OCR diagnosis != confirmed Condition
```

Only approved problem/diagnosis states map to Condition.

---

# 41. Mapping DocumentReference/Binary

Original document storage remains object storage.

FHIR representation includes only what the target workflow needs.

Avoid unnecessary duplicate binary copies.

---

# 42. Mapping Consent

FHIR Consent is an interoperability representation.

SwasthyaSetu consent database remains authoritative for product authorization.

Do not read a FHIR Consent resource and automatically override internal authorization without an import policy.

---

# 43. Mapping Provenance

FHIR Provenance may capture exchange/clinical attribution.

Internal provenance remains richer and authoritative.

Define a deliberate subset.

---

# 44. AuditEvent

FHIR server AuditEvent does not replace platform audit.

Correlation:

```text
request_id
exchange_id
FHIR resource ids
actor
```

where appropriate.

---

# 45. Error normalization

FHIR errors should normalize into:

```text
FHIR_VALIDATION_FAILED
FHIR_REMOTE_UNAVAILABLE
FHIR_AUTH_FAILED
FHIR_CONFLICT
FHIR_NOT_FOUND
FHIR_RATE_LIMITED
FHIR_UNSUPPORTED_OPERATION
FHIR_VERSION_MISMATCH
FHIR_PROFILE_MISMATCH
```

Preserve OperationOutcome internally for diagnostics.

---

# 46. Retry policy

Retry only safe operations:

```text
GET
validated idempotent PUT
specific conditional operations
queued transaction with idempotency design
```

Do not blindly retry non-idempotent POST.

---

# 47. Circuit breaking

Remote FHIR adapter may use:

```text
timeout
bounded retry
circuit breaker
```

if justified.

FHIR sidecar outage must not block safety/intake.

---

# 48. Observability

Record:

```text
operation
resource type
profile
endpoint id
FHIR version
IG version
latency
status
issue count
request/correlation id
```

Avoid logging complete FHIR resources by default.

---

# 49. Metrics

Examples:

```text
fhir_validation_total
fhir_validation_failed_total
fhir_export_total
fhir_export_failed_total
fhir_remote_request_latency
fhir_remote_error_total
abdm_profile_validation_failures
```

---

# 50. Security boundaries

Public:

```text
SwasthyaSetu API/interop gateway
```

Private:

```text
HAPI FHIR JPA
PostgreSQL FHIR DB
validator endpoints
admin/test UI
```

---

# 51. HAPI adapter config

Possible config fields:

```text
base_url
version
expected_fhir_version
timeout_seconds
validation_endpoint
repository_enabled
auth_mode
```

No default public credentials.

---

# 52. HAPI production switches

Recommended initial:

```text
MCP OFF
GraphQL OFF
MDM OFF
Bulk export OFF
Bulk import OFF
Subscriptions OFF
Elasticsearch OFF
FHIR tester external access OFF
OpenAPI external access OFF
```

Enable only when requirements justify.

---

# 53. HAPI upgrade process

1. read release notes;
2. scan CVEs;
3. backup DB;
4. run migration in staging;
5. run FHIR/ABDM golden suite;
6. run performance smoke;
7. review changed CapabilityStatement;
8. deploy canary/staging;
9. promote;
10. retain rollback.

---

# 54. Testing adapters

`MockFHIRValidationAdapter`:

- deterministic;
- unit tests only.

`HapiFHIRValidationAdapter`:

- integration tests.

`InMemoryFHIRRepositoryAdapter`:

- test workflows only.

Do not test domain logic using a remote public FHIR server.

---

# 55. Public test servers

Public HAPI/SMART servers are useful for learning/manual experiments only.

Never send patient data to them.

---

# 56. Suggested repository structure

```text
services/api/app/interoperability/
├── domain/
├── application/
├── ports/
│   ├── fhir_validation.py
│   ├── fhir_repository.py
│   └── fhir_remote_client.py
├── mapping/
│   ├── patient_r4.py
│   ├── encounter_r4.py
│   ├── observation_r4.py
│   └── ...
└── adapters/
    ├── hapi/
    ├── medplum/
    └── remote/

packages/
└── fhir_contracts/

clinical/interoperability/
└── fixtures/
```

Exact tree must still respect the repository structure specification.

---

# 57. Dependency rule

FHIR adapter code may depend on:

```text
HTTP client
interop contracts
config
observability
```

Domain modules must not depend on HAPI/Medplum SDKs.

---

# 58. No Java code in Python domain layer

HAPI is a service boundary.

We do not embed the Java runtime into FastAPI.

---

# 59. Python model choice

Because current `fhir.resources` major versions do not include R4, do not couple the mapping layer to that package for ABDM.

Safer initial approach:

```text
our typed mapping DTOs / dict builders
+
golden JSON fixtures
+
external HAPI validation
```

A dedicated R4 Python model dependency may be added only after separate evaluation.

---

# 60. Remote client choice

Start with `httpx` behind `FHIRRemoteClientPort`.

Reason:

- FastAPI already uses Python HTTP tooling;
- avoids locking to a client whose FHIR/auth assumptions may not match ABDM;
- easy to replace later.

Use SMART client library only for actual SMART OAuth workflows.

---

# 61. Definition of done for interoperability adapter

```text
[ ] FHIR R4 mapping contracts defined
[ ] HAPI validator integration passes
[ ] ABDM package pinned
[ ] no risk-to-diagnosis mapping
[ ] provenance preserved
[ ] consent enforced before send
[ ] sidecar private
[ ] errors normalized
[ ] timeouts/retries bounded
[ ] logs privacy-safe
[ ] version/IG metadata recorded
[ ] tests include invalid fixtures
```

---

# 62. Current recommendation to Codex

Do not implement HAPI or FHIR persistence during early core phases.

When FHIR phase starts:

1. create ports/contracts;
2. build mapping fixtures;
3. create HAPI validation sidecar spike;
4. run ABDM conformance;
5. decide whether persistent repository is required;
6. only then add HAPI JPA persistence if justified.

This keeps interoperability standards-driven instead of infrastructure-driven.
