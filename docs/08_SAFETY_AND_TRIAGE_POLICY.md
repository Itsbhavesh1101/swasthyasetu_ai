# Safety and Triage Policy

**Status:** DRAFT — NOT CLINICALLY APPROVED — NO REAL TRIAGE RULES

**Owner:** Clinical safety governance, with platform implementation support

**Runtime authority:** NONE

**Current implementation scope:** P9-A contract and metadata-registry foundation only

## Purpose and boundary

This document reserves the canonical location named by the Project Master Specification for a
future physical-safety policy. It currently records architecture and approval boundaries only. It
does not define symptoms, measurements, thresholds, diagnoses, urgency criteria,
contraindications, age or pregnancy rules, treatment, self-care advice, or emergency copy.

P9-A may represent the five framework routes `EMERGENCY`, `PRIORITY_REVIEW`, `ROUTINE_CARE`,
`SUPPORTED_SELF_CARE`, and `CLARIFICATION_REQUIRED`. Those names do not establish the clinical
conditions under which any route applies. The only policy metadata fixture is explicitly
engineering-only, contains no rules, and cannot be selected in staging, pilot, or production.

## Policy-independent framework behavior

- A computed decision must identify an exact policy ID and version and provide bounded,
  deterministic machine reason codes.
- Clarification must be explicit and must block self-care. Missing or unavailable policy metadata
  cannot be interpreted as routine care, supported self-care, or any other clinical disposition.
- Generative or predictive output cannot be clinical safety authority. A future deterministic
  policy must remain independently executable and must own hard-override behavior.
- A metadata checksum attests only to canonical metadata bytes. It is not a signature, approval
  record, or evidence of clinical validation.
- Patient evaluation, decision persistence, APIs, UI, advice, and runtime activation are outside
  P9-A.

Route precedence beyond the explicit clarification invariant requires approved clinical rules and
P9-B implementation. No route/flag combination in an engineering fixture is evidence of medical
eligibility for self-care.

## Approval required before clinical policy authoring or activation

A future version must record authoritative source material, exact scope and populations,
jurisdictions and languages, accountable clinical approvers, approval evidence and date, policy
identity/version, effective and retirement dates, change-control and supersession rules, missing
information behavior, validated reason-code definitions, and approved patient/clinician copy.

Clinical safety governance must approve the actual policy content and validation protocol.
Privacy/legal, security, accessibility/content, product, and architecture owners must approve the
parts within their remit. Application configuration, feature flags, hashes, tests, or an
`APPROVED` string cannot substitute for recorded human approval.

## Validation and lifecycle gate

Before a real policy can be activated, a separately reviewed phase must provide:

1. source-traceable clinical rules and structured signals with explicit missing-data semantics;
2. deterministic unit, boundary, repeatability, hard-override, model-nondowngrade, and self-care
   blocking tests against clinically reviewed cases;
3. independent clinical validation with documented limitations, rollback criteria, incident
   handling, monitoring, and revalidation cadence;
4. versioned activation, retirement, supersession, audit, persistence, and environment controls;
5. approved API authorization, consent, UI/degraded-mode behavior, and patient-facing copy.

Any unapproved, missing, invalid, expired, or degraded policy state must fail closed and block
self-care. The exact patient-facing response remains an open clinical/content decision; P9-A does
not manufacture an emergency disposition.

## Open decisions

- authoritative structured input signal fields and validation rules;
- clinical route criteria and deterministic precedence;
- approved reason-code namespace and definitions;
- policy owners, approvers, evidence identifiers, effective interval, and jurisdictions;
- missing-critical-information and degraded-mode semantics;
- persistence/audit model and policy-to-decision linkage;
- patient and clinician copy, accessibility behavior, and escalation operations;
- validation datasets, acceptance thresholds, monitoring, retirement, and rollback process.

Until these decisions are approved and recorded, P9-B clinical evaluation and P9-C patient
integration remain blocked. `SAFE-003`, `SAFE-009`, `FR-SAFE-001..012`, and full AC-P9 acceptance
are not clinically verified by P9-A metadata tests.

## Independence from P8-C

P9-A does not resolve or relax any P8-C Stage 3 gate. Patient-facing AI messages, trusted role
binding, AI-specific consent and external egress, provider/processor/residency approval,
persistence/retention/deletion, withdrawal and in-flight handling, candidate confirmation and
canonical mutation, message idempotency/concurrency/replay, clinical copy, threat/privacy/clinical
safety review, and explicit production enablement remain blocked exactly as recorded in
`docs/implementation/P8_C_INTEGRATION_GATE_REVIEW.md`.
