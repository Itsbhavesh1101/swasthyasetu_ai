# P16-A — Synthetic FHIR Mapping Contracts

**Status:** complete bounded detached engineering subset; live P16 remains unapproved.

The interoperability module now contains immutable, content-free contracts for FHIR R4 `4.0.1`
mapping metadata. A pure mapper binds one closed synthetic source reference to a symbolic FHIR
resource type, exact mapping revision, UTC transformation time, deterministic context fingerprint,
and either an export-projection or non-authoritative import-candidate state.

The closed engineering vocabulary mechanically covers Patient, Encounter, Observation,
AllergyIntolerance, MedicationStatement, DiagnosticReport, DocumentReference, Consent, and
Provenance resource labels without defining any clinical field crosswalk. Model-risk and
unconfirmed-extraction source tokens are rejected, and `Condition` is not representable. Protected
environments are denied before a supplied context is inspected.

No contract contains patient values, narrative, clinical codes, terminology, profile claims, FHIR
JSON, document access, authorization, consent evaluation, destination, or transport. No validator,
FHIR package, HAPI sidecar, adapter, API, persistence, migration, dependency, network access,
feature flag, ABDM behavior, or runtime registration is added.

This is synthetic boundary evidence only. It is not a real mapper, profile/schema conformance
result, approved clinical crosswalk, exchange authorization, or proof of live `FR-FHIR-001..011`
or `AC-P16-001..010` acceptance. All P8-C, P9-C, P10, P11, P13–P17, privacy, consent, security,
identity, source, terminology, pilot, and production restrictions remain in force.
