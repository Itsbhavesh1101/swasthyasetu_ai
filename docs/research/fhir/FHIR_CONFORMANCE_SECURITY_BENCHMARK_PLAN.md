# SwasthyaSetu AI — FHIR Conformance, Security & Interoperability Benchmark Plan

**Document ID:** `SSAI-OSS-R2C-FHIR-002`  
**Status:** Benchmark / technical-spike specification  
**Review date:** 2026-10-09

---

# 1. Purpose

Validate the proposed FHIR architecture before production adoption.

Primary questions:

1. Can SwasthyaSetu reliably map internal clinical data to FHIR R4?
2. Can HAPI validate ABDM profiles correctly?
3. Can the integration fail safely and observably?
4. Can the sidecar be securely deployed without becoming another source of truth?
5. Is a persistent FHIR repository actually necessary?

---

# 2. Candidate components

Primary:

```text
HAPI FHIR JPA / validator
```

Secondary comparison:

```text
Medplum
LinuxForHealth FHIR
```

Optional remote-client libraries:

```text
SMART client-py
fhirpy
plain httpx implementation
```

---

# 3. Target standard

Primary:

```text
FHIR R4
version 4.0.1
```

ABDM:

```text
current published ABDM FHIR implementation-guide package
```

Preview ABDM packages must be tested separately and never silently replace published production conformance.

---

# 4. Initial resource coverage

Test at minimum:

```text
Patient
Encounter
Observation
AllergyIntolerance
Medication
MedicationRequest
DiagnosticReport
DocumentReference
Binary
Condition
FamilyMemberHistory
Procedure where applicable
Consent
Composition
Bundle
Provenance
```

Exact ABDM profiles are selected based on the artifact being generated.

---

# 5. Initial ABDM artifact coverage

Build representative synthetic examples for:

```text
OPConsultRecord
PrescriptionRecord
DiagnosticReportRecord
DischargeSummaryRecord
HealthDocumentRecord
DocumentBundle
```

Later:

```text
WellnessRecord
ImmunizationRecord
InvoiceRecord
```

if product scope requires them.

---

# 6. Synthetic test patient

Create a deterministic synthetic patient containing:

```text
demographics
encounter
chief complaint
confirmed allergy
active medication
historical medication
lab observation
diagnostic report
uploaded prior document
family history
confirmed problem
procedure
consent
```

Also include:

```text
OCR-extracted unconfirmed fact
ML risk assessment
physical safety decision
mental-health routing decision
```

to verify that unsupported/non-diagnostic concepts are **not** incorrectly exported as confirmed Conditions.

---

# 7. Mapping tests

For every mapped resource:

```text
internal entity
    -> FHIR resource
```

assert:

- correct `resourceType`;
- stable identifier behavior;
- correct patient reference;
- correct encounter reference;
- correct dates;
- correct status;
- correct units;
- correct profile URL;
- correct coding-system URL where known;
- no unintended sensitive fields;
- provenance link retained where designed.

---

# 8. Round-trip tests

Where import is supported:

```text
internal -> FHIR -> import candidate
```

must preserve relevant semantics.

Do not require byte-identical round trip.

Require semantic invariants such as:

```text
patient identity reference
observation value/unit
medication dose
allergy substance
document reference
encounter timing
```

---

# 9. Negative mapping tests

Verify:

```text
RiskAssessment != confirmed Condition
SafetyDecision != diagnosis
MentalHealthDecision != psychiatric diagnosis
OCR candidate fact != clinician-confirmed fact
SelfCareGuidance != MedicationRequest
Provider recommendation != Referral unless referral exists
```

These are hard safety/interoperability tests.

---

# 10. Base R4 validation

For each generated resource:

```text
FHIR structural validation
cardinality
datatype
reference format
required fields
FHIRPath invariants
```

must pass or produce expected issues.

---

# 11. ABDM profile validation

Install the exact ABDM package into the validator.

Validate:

```text
profile declarations
minimum elements
terminology bindings
bundle/document composition
references
Must Support handling
```

Store validator output as structured issues.

---

# 12. Published vs preview ABDM regression

Run all fixtures against:

```text
CURRENT_PUBLISHED
PREVIEW_NEXT
```

and produce:

```text
new failures
resolved failures
new mandatory fields
changed bindings
changed profile URLs
changed cardinality
```

This becomes the migration-readiness report.

---

# 13. Validation response schema

Normalize server-specific output into:

```text
ValidationResult
```

with:

```text
valid
issues[]
validator
validator_version
fhir_version
implementation_guide
implementation_guide_version
timestamp
```

Issue:

```text
severity
code
diagnostics
location[]
expression[]
source
```

---

# 14. HAPI version compatibility test

Pin one stable HAPI version.

Run:

```text
all mapping fixtures
ABDM validation fixtures
transaction tests
search tests
import/export tests
```

Then repeat on the proposed upgrade version.

No HAPI version upgrade without regression.

---

# 15. CapabilityStatement test

If a persistent FHIR endpoint is enabled:

assert CapabilityStatement reports only intended functionality where configurable.

Do not advertise features that are disabled by gateway/policy.

---

# 16. Search conformance tests

If FHIR search is required, test:

```text
Patient identifier
Encounter patient/date
Observation subject/code/date
AllergyIntolerance patient
DocumentReference patient/date/type
MedicationRequest patient/status
DiagnosticReport patient/date
```

Do not benchmark search functionality we do not expose.

---

# 17. Transaction bundle test

Create a synthetic document/exchange transaction where relevant.

Validate:

```text
atomic success
reference resolution
idempotency strategy
failure OperationOutcome
rollback on invalid entry
```

---

# 18. DocumentBundle test

For ABDM document artifacts verify:

```text
Composition first where required
all referenced resources included
patient context
encounter context
author/custodian where required
document identifiers
profile declarations
```

---

# 19. Identifier tests

Test:

```text
internal UUID
ABHA-like external identifier fixture
hospital MRN fixture
document identifiers
encounter identifiers
```

No real ABHA IDs in repository test data.

---

# 20. Date/time tests

Test:

```text
UTC timestamps
India timezone display/export where relevant
date-only
partial dates if supported
encounter start/end
lab effective date
document date
```

Avoid silently converting uncertain dates into precise timestamps.

---

# 21. UCUM/unit tests

Examples:

```text
mg
mL
mmHg
Cel
kg
mmol/L
mg/dL
```

Verify numeric value + unit mapping.

Wrong unit is a critical test failure.

---

# 22. Terminology tests

Use controlled synthetic codes.

Test:

```text
code recognized
unknown code
wrong system
display mismatch
value-set binding error
terminology service unavailable
```

Validation policy must document which failures are blocking.

---

# 23. Provenance tests

Where exported:

verify provenance can reference:

```text
source document
clinician confirmation
import source
system-generated export
```

Do not expose internal model prompt details as clinical provenance unless explicitly approved.

---

# 24. Consent tests

FHIR export API must fail before validation/transport if required sharing consent is absent.

Cases:

```text
valid consent
revoked consent
expired consent
wrong purpose
wrong scope
```

The FHIR server cannot override SwasthyaSetu consent policy.

---

# 25. Authorization tests

Attempt:

```text
patient A -> patient B resource access
clinician without assignment
admin without clinical permission
anonymous access
expired token
wrong audience
```

Expected denial.

---

# 26. Direct-sidecar exposure test

In production-like topology verify:

```text
HAPI port unreachable from public network
```

unless intentionally published.

Only approved gateway routes are exposed.

---

# 27. HAPI hardening tests

Assert configuration:

```text
MCP disabled
CORS restricted
H2 disabled
production Postgres
no default DB password
exact image/version pinned
tester UI internal/disabled
Swagger internal/disabled
bulk import/export disabled if unused
GraphQL disabled if unused
MDM disabled if unused
subscriptions disabled if unused
```

---

# 28. Database ownership test

SwasthyaSetu application DB user must not have direct privileges on HAPI tables.

HAPI DB user must not have direct privileges on SwasthyaSetu canonical tables.

---

# 29. Migration test

For HAPI:

```text
empty DB -> selected release schema
previous approved release -> selected release
rollback procedure documented
backup restore tested
```

Do not rely on unrestricted `hbm2ddl:auto=update` in production.

---

# 30. Audit test

Verify:

```text
SwasthyaSetu request audit event
correlation ID
FHIR exchange event
FHIR server audit event if enabled
```

can be linked without logging complete PHI payloads into general application logs.

---

# 31. Logging privacy test

Search logs for synthetic:

```text
patient name
identifier
medication
lab value
document contents
authorization token
```

Only explicitly approved audit/secure storage locations may contain sensitive fields.

General logs should not.

---

# 32. Rate-limit test

Test:

```text
search flood
large bundle
repeated validation
oversized payload
authentication failures
```

Gateway should enforce limits before resource exhaustion.

---

# 33. Request-size test

Reject unreasonable:

```text
huge Binary
huge Bundle
deeply nested resource
oversized search query
```

according to defined limits.

---

# 34. Malformed input test

Send:

```text
invalid JSON
wrong resourceType
invalid date
wrong datatype
unknown element
invalid reference
wrong profile
```

expect deterministic 4xx / OperationOutcome behavior.

---

# 35. SSRF/external-reference policy

If the FHIR server can resolve terminology/packages/external references, verify it cannot freely fetch untrusted user-provided URLs.

Allow only explicitly configured outbound destinations.

---

# 36. Implementation-guide package integrity

Store:

```text
package ID
version
source
checksum
installation date
approved status
```

Do not automatically download moving packages at runtime.

---

# 37. Backup/restore benchmark

Create synthetic FHIR dataset.

Test:

```text
backup
destroy database
restore
search resources
validate checksums/counts
```

Document RTO/RPO target later.

---

# 38. Availability test

Simulate HAPI unavailable.

Expected SwasthyaSetu behavior:

```text
core clinical intake still works
safety still works
document processing still works
FHIR export shows unavailable/pending
no data loss
retry job can resume
```

FHIR sidecar failure must not collapse the patient workflow.

---

# 39. Timeout/retry test

Remote FHIR:

```text
connection timeout
read timeout
HTTP 429
HTTP 503
expired token
invalid OperationOutcome
partial network failure
```

Use bounded retries only on safe/idempotent operations.

---

# 40. Idempotency tests

For outbound creation/sync:

test repeated identical request.

Avoid duplicate:

```text
Patient
Encounter
DocumentReference
Composition
```

Use stable business identifiers/conditional operations only where approved.

---

# 41. Concurrency tests

Simulate:

```text
two exports of same encounter
fact confirmation during export
document update during bundle generation
consent revocation during queued export
```

Define snapshot semantics.

Critical recommendation:

re-check authorization/consent at actual send time.

---

# 42. Performance baseline

Measure HAPI:

```text
cold start
memory
idle memory
single-resource validation latency
document-bundle validation latency
FHIR transaction latency
search p50/p95
PostgreSQL footprint
```

We do not need extreme throughput for MVP.

Correctness/security dominate.

---

# 43. HAPI vs Medplum functional spike

Implement the same minimal fixture in both:

```text
create Patient
create Encounter
create Observation
search by patient
validate resource/profile
record audit
deny unauthorized read
```

Evaluate:

- setup time;
- configuration complexity;
- auth integration;
- validation quality;
- operational dependencies;
- adapter complexity.

This spike validates our architectural recommendation.

---

# 44. LinuxForHealth optional spike

Only if HAPI reveals a blocker.

Do not spend equal engineering time on a third server without a reason.

---

# 45. Python client spike

Compare:

```text
plain httpx
fhirclient
fhirpy
```

for:

```text
CapabilityStatement
read
search
transaction
OAuth/SMART needs
OperationOutcome handling
```

Prefer the smallest dependency that meets our actual remote-client requirements.

---

# 46. Mapping test fixtures

Store under:

```text
tests/fhir/fixtures/internal/
tests/fhir/fixtures/r4/
tests/fhir/fixtures/abdm/
tests/fhir/fixtures/invalid/
```

All fixtures synthetic.

---

# 47. Golden conformance cases

Each ABDM artifact gets:

```text
one valid golden document
missing required field case
wrong profile case
bad reference case
bad terminology case
wrong status case
```

---

# 48. CI integration

In CI:

```text
unit mapping tests
JSON schema/typing tests
golden fixture validation
ABDM package conformance
```

Heavy server integration tests can run in a containerized integration job.

---

# 49. Container pinning

CI and deployment must use:

```text
hapiproject/hapi:<exact-version>
```

plus recorded image digest.

Never `latest`.

---

# 50. Acceptance criteria for R2-C spike

```text
[ ] FHIR R4 target confirmed
[ ] ABDM current published package installed and pinned
[ ] OPConsultRecord fixture validates
[ ] PrescriptionRecord fixture validates
[ ] DiagnosticReportRecord fixture validates
[ ] DischargeSummaryRecord fixture validates
[ ] invalid fixtures fail as expected
[ ] risk/safety outputs are not exported as diagnoses
[ ] consent is checked before external send
[ ] HAPI sidecar is private
[ ] HAPI hardening checks pass
[ ] sidecar failure does not break clinical intake
[ ] upgrade regression suite exists
[ ] exact release/model/package versions are recorded
```

---

# 51. Final benchmark decision

Production FHIR architecture is approved only after the spike confirms that:

```text
custom internal mapping
+
HAPI validation
+
optional HAPI repository
```

is simpler and safer than using a full FHIR-native application platform.

If not, create an ADR before considering Medplum as the core clinical data platform.
