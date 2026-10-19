# Safety and Triage Policy

**Status:** DRAFT — NOT CLINICALLY APPROVED — NO REAL TRIAGE RULES

**Owner:** Clinical safety governance, with platform implementation support

**Runtime authority:** NONE

**Current implementation scope:** P9-A contracts/metadata registry, P9-B synthetic mechanical
evaluation, and P9-C detached presentation/degraded-state engineering evidence only

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

Route precedence for any real patient requires approved clinical rules. No route/flag combination
in an engineering fixture is evidence of medical eligibility for self-care.

## P9-B synthetic mechanics — not clinical policy

P9-B adds a pure evaluator for one fixed, compile-time engineering fixture. Its closed vocabulary
contains only nonmedical symbols: `SYNTHETIC_COMPLETE_A`, `SYNTHETIC_OVERRIDE_A`,
`SYNTHETIC_OVERRIDE_B`, `SYNTHETIC_MISSING_A`, `SYNTHETIC_AMBIGUOUS_A`,
`SYNTHETIC_EXCLUDE_A`, `SYNTHETIC_PRIORITY_A`, `SYNTHETIC_ROUTINE_A`, and
`SYNTHETIC_SELF_CARE_A`. These names test ordering and failure mechanics; they do not stand for
symptoms, measurements, diagnoses, populations, treatments, or approved clinical criteria.

The synthetic evaluator is available only when a caller deliberately supplies both the explicit
local/test metadata registry and the exactly checksummed engineering fixture. It resolves active
metadata at every evaluation, rejects staging/pilot/production, and has no API, runtime module
binding, persistence, provider, network, P7/P8 mutation, or patient-facing output. Importing the
fixture registers or activates nothing. The rule checksum covers canonical synthetic fixture bytes
only; it is neither the P9-A metadata checksum nor a signature or approval credential.

Synthetic tests demonstrate hard-override ordering, advisory non-downgrade, clarification for toy
missing/ambiguous inputs, self-care exclusion, deterministic reason ordering, and fail-closed
missing/tampered policy behavior. This is engineering evidence only. Real signal definitions,
clinical precedence, policy-specific reason codes, patient decision persistence, P9-C integration,
and production rollout remain **OPEN — CLINICAL GOVERNANCE REQUIRED**.

## P9-C detached presentation evidence — not patient integration

P9-C adds a closed frontend view-state projection and a pure React component used only by isolated
tests. The projection accepts the exact P9-B synthetic policy identity and bounded P9-A decision
shape only when a trusted caller explicitly supplies `LOCAL` or `TEST`. Missing, unknown,
staging, pilot, and production environments return unavailable before decision data is inspected.
Malformed, stale, incompatible, extra-field, or privacy-bearing values degrade without echo and
always block any hypothetical self-care continuation.

The synthetic component states prominently that it is engineering test data and not a medical
assessment. It renders harmless machine tokens only and has no action, route, network source,
patient data, clinical advice, or runtime application import. The real `/results` page remains
unavailable, `/urgent-help` remains generic and independent, and completed P7 intake remains a
non-diagnostic draft that is not an urgency assessment.

The exact gate evidence and future authorization checklist are recorded in
`docs/implementation/P9_C_SAFETY_PRESENTATION_GATE_REVIEW.md`. This work is presentation-architecture
and degraded-state evidence only. It does not activate `safety.evaluate`, authorize patient-facing
routing, approve policy content or copy, create persistence, or complete P9.

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

Until these decisions are approved and recorded, real clinical evaluation and P9-C patient
integration remain blocked. `SAFE-003`, `SAFE-009`, `FR-SAFE-001..012`, and full AC-P9 acceptance
are not clinically verified by P9-A metadata, P9-B synthetic mechanics, or P9-C detached
presentation tests.

## Independence from P8-C

P9-A does not resolve or relax any P8-C Stage 3 gate. Patient-facing AI messages, trusted role
binding, AI-specific consent and external egress, provider/processor/residency approval,
persistence/retention/deletion, withdrawal and in-flight handling, candidate confirmation and
canonical mutation, message idempotency/concurrency/replay, clinical copy, threat/privacy/clinical
safety review, and explicit production enablement remain blocked exactly as recorded in
`docs/implementation/P8_C_INTEGRATION_GATE_REVIEW.md`.
