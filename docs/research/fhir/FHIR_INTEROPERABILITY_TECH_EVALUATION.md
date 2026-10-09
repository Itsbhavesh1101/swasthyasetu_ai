# SwasthyaSetu AI — FHIR & Interoperability Technology Evaluation

**Document ID:** `SSAI-OSS-R2C-FHIR-001`  
**Status:** Deep research / pre-implementation architecture decision  
**Review date:** 2026-10-09  
**Scope:** FHIR server, validation, mapping, persistence, SMART-on-FHIR, ABDM R4 compatibility, security, audit, deployment and Python integration.

---

# 1. Executive conclusion

SwasthyaSetu should **not make an external FHIR server the internal clinical source of truth**.

The existing SwasthyaSetu domain model and PostgreSQL database remain authoritative.

The FHIR architecture should instead be:

```text
SwasthyaSetu Domain / PostgreSQL
             |
             v
      FHIR Mapping Layer
             |
             v
      FHIR Validation Port
             |
       +-----+------+
       |            |
       v            v
 HAPI Validator   Test/Local validator
 / sidecar
       |
       v
 Optional FHIR Repository Port
       |
       +-- HAPI FHIR JPA sidecar       <-- preferred persistent server candidate
       +-- Medplum adapter             <-- architecture-pivot alternative
       +-- External hospital FHIR      <-- remote endpoint
       +-- ABDM exchange adapter       <-- separate ABDM transport/workflow
```

The strongest current default is:

> **FHIR R4 first + SwasthyaSetu-owned mapping + HAPI FHIR validation/server sidecar only where needed.**

This is primarily because the current published ABDM FHIR implementation guide is based on **FHIR 4.0.1 (R4)**.

FHIR R5 is the latest published HL7 release, but it is not the correct first interoperability target for ABDM.

---

# 2. Critical architecture decision

## 2.1 Do not duplicate the source of truth

SwasthyaSetu already has:

```text
Patient
Encounter
ClinicalFact
Medication
Allergy
Observation
Document
Consent
Referral
RiskAssessment
...
```

with provenance and safety semantics that are richer than a naive FHIR persistence mapping.

A FHIR server is not allowed to become an independent shadow clinical database without a deliberate architecture change.

Correct initial flow:

```text
internal canonical data
       |
       v
mapping
       |
       v
FHIR R4 resource / document bundle
       |
       v
validation
       |
       v
external exchange
```

If persistent FHIR storage is later required for interoperability workflows, it is a projection/integration repository unless an ADR explicitly changes authority.

---

# 3. Why FHIR R4 is the primary target

HL7 FHIR R5 is the current published FHIR release.

However, the Indian integration target matters more than "latest version".

The current published ABDM implementation guide reviewed in this research:

```text
ABDM IG published line: 6.5.0
FHIR base: 4.0.1
FHIR release: R4
```

The current 7.0.0 preview/development build is also based on FHIR 4.0.1.

Therefore:

```text
SwasthyaSetu interoperability baseline = FHIR R4 (4.0.1)
```

R5 support is a future compatibility capability, not the first production target.

---

# 4. ABDM implications

The current published ABDM guide defines document-style clinical artifacts including:

```text
DiagnosticReportRecord
DischargeSummaryRecord
HealthDocumentRecord
ImmunizationRecord
OPConsultRecord
PrescriptionRecord
WellnessRecord
InvoiceRecord
DocumentBundle
```

and resource profiles including:

```text
AllergyIntolerance
Appointment
Binary
CarePlan
Condition
DiagnosticReport
DocumentReference
Encounter
FamilyMemberHistory
ImagingStudy
Immunization
Medication
MedicationRequest
...
```

This directly supports our decision to keep internal data separate and construct a profile-conformant document/bundle when exchange is needed.

---

# 5. HAPI FHIR — strongest default server/validator candidate

## 5.1 Repository maturity

Observed at review time:

```text
~2.4k GitHub stars
~1.5k forks
~11,000 commits
very active 2026 pull requests
Apache-2.0
latest stable release line observed: 8.10.x
main/master already beyond that release line
```

In a niche healthcare interoperability project, 2.4k stars is substantial.

More important than stars, the repository contains mature modules for:

```text
FHIR client
REST server
JPA server
R4 structures
R4B structures
R5 structures
validation
NPM/package validation support
subscriptions
OpenAPI
MDM
CQL / clinical reasoning
CDS Hooks
bulk operations
partitioning
audit interceptors
test utilities
R4/R4B/R5 JPA server tests
```

This is a real framework/platform, not a demonstration server.

## 5.2 Why HAPI aligns with SwasthyaSetu

It can serve three distinct roles without owning the product:

```text
1. FHIR validation engine
2. interoperability FHIR endpoint
3. optional FHIR projection/repository
```

This fits our ports/adapters design.

## 5.3 Strong validation support

HAPI has explicit support for:

- core FHIR validation;
- StructureDefinition validation;
- terminology validation;
- implementation-guide/package validation;
- repository validation interceptors;
- request/response validation interceptors.

This is highly important for ABDM because the implementation guide is distributed as a FHIR package containing profiles/value sets/examples.

## 5.4 PostgreSQL support

The current JPA server starter includes a PostgreSQL 16 Docker Compose example and a HAPI PostgreSQL Hibernate dialect.

This aligns operationally with our PostgreSQL-oriented environment.

However, the HAPI FHIR database must not be accessed directly by SwasthyaSetu domain repositories.

Use a separate DB or strongly separated schema/user.

## 5.5 FHIR version support

The main HAPI project contains explicit structures and JPA tests for:

```text
R4
R4B
R5
```

The starter defaults to R4.

This is ideal for our ABDM-first R4 target while keeping future R5 migration possible.

---

# 6. HAPI FHIR starter is NOT production-ready by default

This is one of the most important findings.

The official JPA starter explicitly states that it does not provide a complete production security implementation.

It also documents limitations around:

```text
enterprise logging
multi-instance subscription topic cache
multi-instance internal message broker
```

The current default starter configuration also exposes development-friendly settings that must not be copied into production unchanged.

Examples observed in the reviewed configuration:

```text
H2 default datasource
Hibernate hbm2ddl = update
open API enabled
FHIR tester/UI support
CORS allowed origin = *
MCP server enabled
bulk import/export disabled by default
validation not automatically enabled for every request
```

The Docker example includes illustrative database credentials.

### Consequence

Never deploy:

```text
hapiproject/hapi:latest
```

with starter defaults and expose it to the internet.

---

# 7. Required HAPI hardening profile

If HAPI is adopted, production configuration should include at minimum:

```text
exact pinned HAPI release/image
dedicated PostgreSQL database/user
secret-managed credentials
TLS at ingress
authentication/authorization gateway or HAPI security interceptor layer
restricted CORS
MCP disabled
FHIR tester UI disabled or internal only
Swagger/OpenAPI internal only unless explicitly required
request size limits
rate limits
FHIR request validation
profile validation where relevant
audit logging
backup/restore
database migration process
network policy
resource limits
health/readiness checks
security scans
no default H2
no hbm2ddl auto-update in production
```

If horizontally scaled and subscription/background features are enabled, replace in-memory coordination/message mechanisms with supported shared infrastructure.

---

# 8. HAPI MCP finding

The current starter configuration includes an MCP server option enabled in the reviewed file.

That capability is not required for SwasthyaSetu FHIR interoperability.

Recommended:

```text
spring.ai.mcp.server.enabled = false
```

unless a future security-reviewed feature explicitly requires it.

FHIR data should not become automatically exposed to general-purpose agent tooling.

---

# 9. HAPI audit capability

HAPI contains an IHE Basic Audit Logging Pattern (BALP) interceptor that can generate FHIR AuditEvent resources.

This is valuable, but it does not replace SwasthyaSetu's platform audit log.

Recommended separation:

```text
SwasthyaSetu audit
    = product/security/business actions

FHIR BALP AuditEvent
    = FHIR interoperability audit events
```

The two may be correlated using request/correlation IDs.

---

# 10. HAPI security posture

The main repository does not present the same simple top-level `SECURITY.md` experience as Medplum.

However, the project is actively maintained, security fixes are visible in changelog/dependency work, and the repository has high activity.

This means:

**security posture is acceptable for evaluation, but SwasthyaSetu must own dependency scanning and patch monitoring rather than assuming the server is secure by default.**

---

# 11. HAPI operational cost

Costs:

- Java/JVM service in a primarily Python/TypeScript stack;
- separate build/runtime;
- separate FHIR schema persistence;
- HAPI upgrade compatibility;
- terminology/IG package management;
- security hardening.

Benefits:

- deep FHIR maturity;
- profile validation;
- server features;
- active ecosystem;
- broad FHIR release support.

For SwasthyaSetu, this trade is reasonable **only because HAPI is isolated behind an interoperability adapter**.

---

# 12. Medplum — strongest full-platform alternative

## 12.1 Repository maturity

Observed:

```text
~2.7k stars
~960 forks
~7,000 commits
Apache-2.0
very active releases
5.2.x release line current in October 2026
```

Medplum is highly active.

Its codebase contains:

```text
FHIR API/server
PostgreSQL
Redis/BullMQ
OAuth/OIDC
SMART-on-FHIR
AccessPolicy authorization
FHIR AuditEvent logging
WebSockets/subscriptions
bots/workers
React UI
SDKs
storage adapters
AWS/Azure/GCP integrations
OpenTelemetry
GraphQL
HL7 support
```

## 12.2 Strong security/product posture

Medplum has a formal security policy and documents:

- TLS;
- encryption-at-rest practices;
- penetration testing;
- security reviews;
- SSO;
- RBAC;
- responsible disclosure.

Source inspection also shows:

- AccessPolicy logic;
- AuditEvent handling;
- OAuth/SMART launch support;
- pre-commit FHIR validation;
- PostgreSQL repository abstraction.

This is a stronger out-of-the-box application-security story than the HAPI starter.

## 12.3 FHIR focus

Medplum's hosted API is FHIR R4 focused.

The platform advertises SMART-on-FHIR and implementation-guide-oriented ecosystem support.

This aligns well with ABDM's FHIR R4 base.

---

# 13. Why Medplum is not the current default for SwasthyaSetu

Medplum is **too complete** for our chosen architecture.

It already owns concepts that SwasthyaSetu intentionally owns:

```text
identity
authorization
FHIR data repository
background jobs
application server
web application framework
bots/workflows
storage
audit
project/tenant model
```

Adopting Medplum as core would effectively reopen our foundation architecture.

We would have to decide whether:

```text
SwasthyaSetu PostgreSQL domain model
```

or

```text
Medplum FHIR repository
```

is authoritative.

That is a Class E architecture change and is not justified by the current requirements.

## Decision

**CONSIDER as architecture-pivot alternative or external FHIR platform, not current default.**

---

# 14. When Medplum WOULD become attractive

Reconsider Medplum if SwasthyaSetu later decides:

```text
FHIR-native repository as primary clinical data store
+
SMART/OAuth integrated directly into that platform
+
FHIR-first workflow extensions
```

In that world Medplum may reduce significant engineering work.

That is not our current architecture.

---

# 15. Medplum self-hosting hardening

The reviewed configuration/deployment ecosystem exposes many powerful capabilities.

Even with a stronger security baseline, a self-hosted deployment still requires:

```text
restricted CORS
rate limiting
secret rotation
PostgreSQL security
Redis security
object-storage security
worker isolation
project/access policy review
bot execution controls
audit retention
backup/restore
dependency scanning
network segmentation
```

Do not assume "self-hosted" automatically means secure.

---

# 16. LinuxForHealth FHIR Server

## 16.1 Strengths

The LinuxForHealth FHIR Server is a modular Java FHIR server with:

```text
R4
R4B
validation
profiles / implementation guides
JDBC persistence
audit
Open Liberty
JWT-related server APIs
Kafka/NATS integrations
terminology modules
```

The project is Apache-2.0.

It has real enterprise architecture and originated from IBM's FHIR server work.

## 16.2 Community/adoption

Observed repository scale is materially smaller than HAPI/Medplum:

```text
~370 stars
~160 forks
```

The project remains available with 5.x releases, but its broader community activity is significantly lower.

## 16.3 Fit

Technically capable, but choosing it instead of HAPI would give us:

- smaller ecosystem;
- smaller adopter base;
- another Java server;
- no decisive SwasthyaSetu-specific advantage discovered in this review.

## Decision

**CONSIDER / secondary benchmark, not primary.**

---

# 17. Microsoft FHIR Server

## 17.1 Strengths

The open-source Microsoft FHIR Server has:

- MIT license;
- Azure-oriented deployment;
- authentication/RBAC documentation;
- SQL provider;
- bulk operations;
- security disclosure process;
- managed-service lineage.

## 17.2 Important 2026 lifecycle changes

The repository currently states:

```text
FHIR R4B support ended July 1, 2026
FHIR R4 remains supported
Cosmos DB provider support ended September 30, 2026
SQL provider remains supported
```

## 17.3 Architecture fit

It is strongly optimized for Azure.

SwasthyaSetu is intentionally platform-agnostic.

## Decision

**REFERENCE / CONSIDER ONLY IF AZURE BECOMES THE CHOSEN CLOUD.**

Do not make it the default while cloud choice remains open.

---

# 18. Firely .NET SDK

Firely's .NET SDK is high-quality and supports:

```text
R4
R4B
R5
parsing
serialization
FHIR client
profile validation tooling
FHIRPath
```

But it is a .NET SDK, not our desired server architecture.

## Decision

**REFERENCE / interoperability test client only.**

Not a SwasthyaSetu core dependency.

---

# 19. Google FHIR / FhirProto

Google's project provides strongly typed Protocol Buffer representations and FHIR conversion/validation utilities.

It is useful for:

- analytics;
- protobuf-heavy data systems;
- Google-style pipelines.

It is not a FHIR REST server and does not solve our immediate ABDM exchange architecture.

## Decision

**REFERENCE ONLY.**

---

# 20. Python FHIR libraries

A Python-native mapping/client layer is desirable because our application backend is FastAPI.

However, current library details matter.

---

# 21. `fhir.resources`

Strengths:

- Pydantic-based;
- typed resource classes;
- Python-native;
- permissive BSD license.

Important current limitation:

The project's current major line defaults to R5 and exposes R4B/STU3 as previous-version subpackages.

Its current documentation explicitly states that **FHIR R4 is not included in the latest major line**.

That conflicts directly with our ABDM R4 requirement.

## Decision

**DO NOT use current `fhir.resources` as the authoritative ABDM R4 type system.**

An older pinned major could technically provide R4, but starting a new healthcare system on an older branch solely for version compatibility is unattractive.

---

# 22. SMART `fhirclient`

The SMART-on-FHIR Python client supports FHIR R4 and SMART OAuth workflows.

Potential use:

```text
remote SMART/FHIR client integration
test tooling
external hospital connectivity
```

It is not a profile validator or server.

## Decision

**CONSIDER for remote SMART client flows only.**

Do not make it our mapping authority.

---

# 23. `fhirpy`

`fhirpy` is a compact synchronous/asynchronous Python FHIR client.

Potential use:

```text
simple backend FHIR REST client
```

It is not a full profile validator or server and has less complete OAuth/SMART behavior than dedicated SMART clients.

## Decision

**CONSIDER behind remote-client adapter if it materially simplifies code.**

A small internal HTTP client may be sufficient instead.

---

# 24. Recommended FHIR layer decomposition

Our prior generic `FHIRProvider` concept is too broad.

R2-C recommends splitting it into:

```text
FHIRMapper
FHIRValidationPort
FHIRRepositoryPort
FHIRRemoteClientPort
```

and orchestrating them through:

```text
FHIRGatewayService
```

This avoids a god interface and keeps concerns separate.

---

# 25. FHIRMapper

Owned by SwasthyaSetu.

Responsibilities:

```text
internal domain -> FHIR R4 resources
FHIR R4 resource -> import candidates
ABDM document composition
identifier mapping
provenance mapping
profile/meta assignment
```

It does **not** perform transport or persistent FHIR storage.

---

# 26. FHIRValidationPort

Responsibilities:

```text
validate base R4 structure
validate profile
validate ABDM IG
validate terminology bindings where configured
return OperationOutcome-like structured issues
```

Primary candidate:

```text
HapiFhirValidationAdapter
```

---

# 27. FHIRRepositoryPort

Optional.

Responsibilities:

```text
create/update/read/search resources
transaction bundle
history where required
capability statement
```

Primary candidate:

```text
HapiFhirRepositoryAdapter
```

Alternative:

```text
MedplumFhirRepositoryAdapter
```

Only introduce persistent repository if a real requirement exists.

---

# 28. FHIRRemoteClientPort

Responsibilities:

```text
external FHIR base URL
auth token injection
CapabilityStatement discovery
read/search/write/transaction
timeouts/retries
OperationOutcome handling
```

This is separate from HAPI/Medplum local hosting.

---

# 29. Why mapping remains custom

No off-the-shelf FHIR library understands SwasthyaSetu semantics such as:

```text
extracted vs clinician-confirmed fact
AI provenance
safety route vs diagnosis
risk score vs Condition
self-care guidance
consent scopes
OCR source block
MannSetu deterministic route
```

We must define those mappings explicitly.

---

# 30. Critical mapping invariant: risk is not diagnosis

Example:

```text
RiskAssessment(task="cardiovascular", risk_probability=0.71)
```

must not silently generate:

```text
Condition(code="cardiovascular disease", verificationStatus="confirmed")
```

Possible export patterns must be explicitly approved, for example:

```text
Observation
RiskAssessment-like custom profile where applicable
DiagnosticReport component
or no FHIR export until mapping is approved
```

Never fake a confirmed Condition.

---

# 31. Critical mapping invariant: extracted is not confirmed

OCR/LLM candidate clinical facts should not be exported as confirmed clinical data without a mapping policy reflecting their verification state.

Potential mechanisms:

```text
Provenance
verification-related fields where resource supports them
status fields
extensions
document context
or exclusion from certain exchange artifacts
```

Exact design belongs in `20_FHIR_MAPPING_SPEC.md`.

---

# 32. ABDM package strategy

Maintain an explicit conformance registry:

```text
package_id: ndhm.in
version: 6.5.0
fhir_version: 4.0.1
status: CURRENT_PUBLISHED
checksum: ...
installed_at: ...
```

Also track preview separately:

```text
package_id: ndhm.in
version: 7.0.0
status: PREVIEW_ONLY
```

Do not automatically replace production validation with a preview build.

---

# 33. Implementation-guide upgrade policy

When ABDM IG version changes:

1. download new package;
2. checksum;
3. run conformance regression;
4. generate diff report;
5. identify affected mappings;
6. update fixtures;
7. clinical/interoperability review;
8. deploy behind version flag;
9. preserve ability to validate historical exchange where needed.

---

# 34. Recommended deployment topology

Initial interoperability environment:

```text
FastAPI
  |
  | internal HTTP / controlled network
  v
FHIR Interop Sidecar (HAPI)
  |
  +-- dedicated Postgres database
  |
  +-- installed R4 / ABDM packages
```

Public exposure:

```text
Internet / partner
      |
API gateway / ingress
      |
auth / rate limit / audit
      |
SwasthyaSetu interop endpoint
      |
FHIR sidecar
```

Do not expose HAPI admin/test endpoints directly.

---

# 35. Database ownership

Recommended:

```text
swasthyasetu_app database
  = authoritative domain data

swasthyasetu_fhir database
  = FHIR interoperability projection/server state
```

They may share a PostgreSQL cluster but should use different database/schema ownership and credentials.

No cross-database shortcuts in application domain code.

---

# 36. Do we need a FHIR server in MVP?

Probably not.

For initial MVP:

```text
FHIRMapper
+
FHIRValidationPort
```

may be sufficient.

A persistent FHIR repository is needed only if we must provide:

```text
FHIR search endpoint
FHIR history
subscriptions
external SMART apps
partner query access
persistent FHIR projection
```

Avoid running infrastructure merely because it exists.

---

# 37. SMART-on-FHIR position

SMART-on-FHIR is valuable for future:

```text
hospital app launch
clinician app integrations
external patient context launch
third-party approved clinical apps
```

It is not required to build the initial patient intake flow.

Medplum includes SMART/OAuth natively.

HAPI requires the application/security layer to implement/attach authorization behavior.

SwasthyaSetu should defer SMART server launch support until a concrete integration requires it.

---

# 38. Terminology services

FHIR profile validation may depend on terminology.

Potential areas:

```text
LOINC
SNOMED CT
UCUM
ICD-related systems
ABDM value sets
```

Do not bundle terminology licensing assumptions into HAPI setup.

Terminology source/licensing requires a separate decision.

For early ABDM conformance, install the exact profile/value-set package and use controlled validation settings.

---

# 39. Search/indexing

HAPI supports relational search indexes and optional advanced Lucene/Elasticsearch features.

SwasthyaSetu does not need Elasticsearch for initial FHIR interoperability.

Recommended:

```text
relational/JPA search only
```

until a specific query/profile requires more.

---

# 40. Bulk operations

Both HAPI/Medplum ecosystems have bulk capabilities.

Initial SwasthyaSetu recommendation:

```text
bulk import/export OFF
```

unless a research/import or institution integration specifically requires it.

Bulk endpoints increase data-exfiltration and operational risk.

---

# 41. GraphQL

FHIR GraphQL support is not an initial requirement.

Do not expose GraphQL merely because the server supports it.

---

# 42. Subscriptions

FHIR subscriptions may be useful for future HIS integration.

But they introduce:

```text
message delivery
cluster coordination
retry semantics
duplicate handling
security
```

Initial recommendation:

```text
OFF unless a concrete integration requires it
```

Use SwasthyaSetu domain events internally.

---

# 43. FHIR server multitenancy

Do not use HAPI partitioning or Medplum project isolation as a substitute for defining SwasthyaSetu institution scope.

If future multi-institution deployment is approved, map our institution boundary deliberately to FHIR server tenant/project/partition capabilities.

---

# 44. FHIR privacy boundary

FHIR exports must apply:

```text
authorization
consent
purpose
minimum necessary scope
```

before constructing/sending the external payload.

The FHIR server itself does not decide whether SwasthyaSetu has permission to share patient data.

---

# 45. Binary / DocumentReference handling

ABDM profiles include document-oriented artifacts.

Large raw PDFs/images should remain in SwasthyaSetu object storage under controlled access.

FHIR may export:

```text
DocumentReference
Binary
Attachment
```

according to the target profile/transport rules.

Avoid casually base64-duplicating large originals into multiple databases.

---

# 46. Security comparison summary

| Area | HAPI FHIR | Medplum | LinuxForHealth | Microsoft FHIR |
|---|---|---|---|---|
| Mature FHIR engine | Excellent | Excellent | Strong | Strong |
| R4 | Yes | Yes | Yes | Yes |
| R4B | Framework support | No primary platform target | Yes | Support ended 2026 |
| R5 | Yes | Not primary | No main focus | No |
| Built-in auth product | Requires integration | Strong | Server/JWT integrations | Strong Azure model |
| Profile validation | Excellent | Strong | Strong | Strong |
| PostgreSQL fit | Yes | Native | JDBC | SQL Server/Azure focus |
| Cloud-neutral | Strong | Reasonable | Strong | Weak |
| Product overlap with SwasthyaSetu | Low-medium | High | Low-medium | Medium |
| Community/adoption | Strong niche | Strong niche | Smaller | Strong vendor |
| Best use for us | Validator/sidecar | Alternative platform | Secondary | Azure-only alternative |

---

# 47. Engineering-screen recommendation

Weighted qualitative conclusion:

```text
HAPI FHIR              9/10 fit as interop sidecar
Medplum                8/10 technology, 6/10 architectural fit
LinuxForHealth         7/10 technical fit, lower ecosystem signal
Microsoft FHIR         8/10 if Azure, 5/10 platform-neutral fit
Firely .NET SDK        strong SDK, not server candidate
Google FHIR            useful library, wrong problem
```

These are architecture-fit scores, not product-quality scores.

---

# 48. Current preferred decision

**ADOPT HAPI FHIR BEHIND ADAPTER**, with the following interpretation:

Not:

```text
"Put all SwasthyaSetu data into HAPI"
```

Instead:

```text
"Use HAPI as an isolated FHIR standards/conformance service and optional FHIR projection repository."
```

---

# 49. Version pin recommendation

At implementation time:

- select latest approved stable HAPI release;
- do not use moving `master`;
- do not use `latest` Docker tag;
- record image digest;
- record HAPI version;
- record Java version;
- record ABDM package version;
- record database migration/schema version.

The research snapshot observed HAPI stable 8.10.1 in 2026, but implementation should re-check for security/stable updates before pinning.

---

# 50. Decisions that remain open

Do not let Codex silently decide:

```text
exact HAPI release to pin
whether a persistent FHIR repository is needed for MVP
terminology server/provider
SMART-on-FHIR server support
ABDM transport/API implementation
FHIR security-label strategy
exact AI provenance extensions
risk-assessment FHIR representation
multi-institution tenant mapping
```

These belong to later detailed specifications / ADRs.

---

# 51. R2-C final recommendation

The project should proceed with:

```text
Internal source of truth:
    SwasthyaSetu PostgreSQL/domain model

FHIR baseline:
    HL7 FHIR R4 4.0.1

India conformance:
    ABDM current published R4 implementation guide

Mapping:
    SwasthyaSetu-owned

Validation:
    HAPI FHIR sidecar

Persistent FHIR server:
    HAPI JPA only when a concrete requirement needs it

Full-platform alternative:
    Medplum, only if architecture is deliberately changed

Secondary server:
    LinuxForHealth, keep as benchmark/reference

Azure-specific alternative:
    Microsoft FHIR Server
```

This preserves interoperability without surrendering SwasthyaSetu's architecture.
