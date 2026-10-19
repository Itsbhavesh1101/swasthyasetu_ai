# P8-C integration gate review

Date of repository review: 2026-10-19
Required baseline: `main @ ad3bb6cd709e2f403e6e798d1bac31f9477eaf23`

## Decision

P8-C Stage 3 is **BLOCKED**. The repository contains approved engineering contracts for deterministic P7 intake and the disabled-by-default P8-A/P8-B foundations, but it does not contain the clinical, identity, privacy, consent, retention, confirmation, or idempotency approvals required to expose patient-facing AI intake.

Only the Stage 2 safe engineering subset is authorized: synthetic, process-local, zero-egress verification of the existing P8-A orchestration and P8-B extraction contracts. It must remain detached from P7 persistence, public HTTP routes, the BFF, and patient UI.

The statuses below are deliberately separate:

- technically exercised in synthetic mode: permitted for Stage 2 verification;
- clinically approved for patient use: **no**;
- privacy/consent approved for patient use: **no**;
- enabled in production: **no**.

## Gate evidence

| Gate | Authoritative repository evidence | Decision owner | Decision ID / date | Approved scope | Status |
|---|---|---|---|---|---|
| Clinical validation | `docs/14_LLM_EXTRACTION_SPEC.md` permits only an exact synthetic literal grammar and says arbitrary free-text extraction is not clinically approved. | Institutional clinical governance owner | No approval recorded as of 2026-10-19 | Synthetic engineering fixtures only | **OPEN — Stage 3 blocked** |
| Trusted role binding | `docs/13_AI_ORCHESTRATION_SPEC.md` requires trusted role binding; no production identity-to-provider adapter or approved role mapping exists. | Identity/security and clinical governance owners | No approval recorded as of 2026-10-19 | No live conversational role binding | **OPEN — Stage 3 blocked** |
| Consent scope | `docs/26_PRIVACY_CONSENT_SPEC.md` states consent is specific and non-transitive; the current general product consent covers deterministic first-party intake, not third-party AI processing or new message persistence. | Privacy/legal and product governance owners | No approval recorded as of 2026-10-19 | Existing deterministic P7 consent only | **OPEN — Stage 3 blocked** |
| External egress and processor terms | `docs/13_AI_ORCHESTRATION_SPEC.md`, ADR-031, and R3 policy keep provider selection open and external clinical-data egress disabled. No processor/DPA, residency, or live provider approval is recorded. | Privacy/legal, security, and architecture owners | ADR-031 approves only an in-process gateway; no live-provider approval recorded | Deterministic offline provider only | **OPEN — Stage 3 blocked** |
| Message persistence and retention | The P8 specifications defer patient-message storage, retention, deletion, and audit semantics; no schema or migration is approved. | Privacy/legal and data governance owners | No approval recorded as of 2026-10-19 | No message persistence | **OPEN — Stage 3 blocked** |
| Withdrawal and in-flight handling | `docs/26_PRIVACY_CONSENT_SPEC.md` requires explicit purpose and withdrawal behavior; no policy covers an in-flight model request, derived candidates, or already-dispatched external data. | Privacy/legal and clinical governance owners | No approval recorded as of 2026-10-19 | No patient AI request may start | **OPEN — Stage 3 blocked** |
| Confirmation and canonical mutation | `docs/14_LLM_EXTRACTION_SPEC.md` defines candidates as unconfirmed and non-authoritative; no approved confirmation transaction may merge them into P7 or P5 facts. | Clinical governance and application architecture owners | No approval recorded as of 2026-10-19 | Detached unconfirmed candidates only | **OPEN — Stage 3 blocked** |
| Idempotency and retry semantics | The API design discusses `/messages`, but no authoritative create-message idempotency key, replay result, concurrency rule, or retry transaction is approved. | API/application architecture owner | No approval recorded as of 2026-10-19 | No public message endpoint | **OPEN — Stage 3 blocked** |
| Patient-facing copy and urgent-help interaction | No clinically approved conversational copy or AI-specific fallback/urgent-help wording is recorded. Existing deterministic P7 urgent-help UX remains authoritative. | Clinical safety, content, and accessibility owners | No approval recorded as of 2026-10-19 | Preserve existing P7 UI unchanged | **OPEN — Stage 3 blocked** |
| Production enablement | P8-A defaults to disabled/unconfigured and rejects engineering fakes in protected environments. | Platform/security and clinical governance owners | No production enablement decision recorded | Disabled/unconfigured | **BLOCKED** |

## Authorized Stage 2 subset

The implementation may add automated proof that:

1. an exact synthetic `ClinicalExtractionTask` passes through `AIOrchestrationService` and `DeterministicOfflineLLMProvider` into `ClinicalIntakeExtractor` with correlated request, schema, prompt, provenance, deadline, and source metadata;
2. results remain detached `AI_EXTRACTED_UNCONFIRMED` candidates and never enter P7 repositories or database tables;
3. disabled/unconfigured providers, every closed failure category, malformed or mismatched output, invalid evidence, unsupported/injection-like source text, abstention, and refusal fail closed or return no candidate while deterministic P7 remains available;
4. the synthetic path performs no network egress and emits no patient text, identifiers, source references, or extracted content to logs or telemetry;
5. no public `/messages` route, BFF handler, patient UI, dependency, migration, or automatic module activation is added.

## Future Stage 3 authorization and transaction proposal

This proposal records questions for human decision; it is not implementation approval.

Before a future message request is accepted, the server would need to validate the opaque session, validate the exact approved consent purpose and scope, establish encounter ownership, bind a trusted role, enforce request idempotency, and select an approved provider under an explicit egress policy. Those checks must be server authoritative and fail closed.

A model call must not hold a database transaction open. If external processing is ever approved, the design must specify consent withdrawal and session closure behavior while a request is in flight, including whether the call is cancelled, whether a late response is discarded, and how that outcome is audited without retaining clinical text. After the call, authorization, consent, ownership, and idempotency state must be revalidated before any write.

Any future persistence transaction must atomically record only the approved minimal message metadata, idempotency result, detached unconfirmed candidate envelope, source linkage, and audit/outbox records. It must never directly update a P7 answer or authoritative P5 clinical fact. A separate, explicit patient/clinician confirmation transaction would be required to validate current authorization and consent again, apply correction/supersession rules, and atomically persist the confirmed canonical change with its audit/outbox evidence.

Human owners must first approve exact retention/deletion periods, payload encryption and access rules, processor/residency terms, retry and replay behavior, confirmation semantics, withdrawal behavior, clinically validated scope/languages/copy, monitoring/redaction rules, and rollback criteria.

## Stage 3 checklist

- [ ] Clinical approval for exact extraction scope, languages, prompt package, copy, failure states, and rollback thresholds
- [ ] Trusted production role binding and identity assurance
- [ ] Specific consent purpose/scope for AI processing, provider egress, and any message/candidate persistence
- [ ] Approved provider, processor terms, residency, and zero-retention/data-use configuration
- [ ] Retention, deletion, subject-access, and audit policy for messages and derived candidates
- [ ] Withdrawal and session-close semantics for queued/in-flight/completed requests
- [ ] Create-message idempotency, concurrency, retry, and replay contract
- [ ] Candidate confirmation and canonical mutation transaction contract
- [ ] Threat model, privacy review, clinical safety review, and incident/rollback plan
- [ ] Explicit production enablement decision

Until every applicable item is approved and recorded authoritatively, the patient message API, BFF, UI, persistence, external provider egress, and automatic AI activation remain prohibited.

## Synthetic verification status

The Stage 2 subset is technically tested in synthetic mode: 19 new integration tests and 208
combined P8-A/B/C focused tests pass. The full network-free backend, PostgreSQL, frontend, Docker,
and browser regressions also pass. This evidence does not change the separate clinical approval,
privacy approval, or production enablement statuses above; each remains **no / not established**.
