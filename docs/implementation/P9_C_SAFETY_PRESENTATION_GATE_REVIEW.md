# P9-C safety presentation gate review

Date of repository review: 2026-10-19
Required baseline: `main @ 541fa9033349162c4bf1abb5d6cdfe7a6cd8d6fd`

## Decision

P9-C patient integration is **BLOCKED**. The repository contains policy-neutral P9-A decision
contracts and P9-B deterministic mechanics for one compile-time, nonmedical fixture. It contains no
clinician-approved physical-safety policy, validated patient signal definitions, clinical thresholds,
approved route wording, production policy lifecycle, authorized safety API, or decision persistence.

Only the Stage 2 safe engineering subset is authorized: a detached, nonclinical presentation
contract and isolated component tests that demonstrate strict parsing, protected-environment
refusal, synthetic labeling, accessibility, and fail-closed degraded behavior. This evidence does
not activate a patient workflow or establish clinical validity.

The statuses below remain separate:

- synthetic presentation mechanics technically exercised: permitted for Stage 2 verification;
- clinically approved for patient use: **no**;
- privacy/authorization approved for a patient safety API: **no**;
- production or pilot enabled: **no**.

## Approval-gate matrix

| Gate                                                                                                         | Current source path and section                                                                                                                       | Accountable owner                                                               | Decision ID / date                                      | Approved environment, population, and use                                                     | Status                             | Action required to unblock                                                                                                                 |
| ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Clinician-approved policy source, scope, populations, validated signals, and clinical thresholds             | `docs/08_SAFETY_AND_TRIAGE_POLICY.md`, Purpose and boundary; Approval required                                                                        | Clinical safety governance                                                      | **NONE RECORDED** as of 2026-10-19                      | No patient population or clinical environment; nonmedical synthetic engineering fixtures only | **OPEN — real rules prohibited**   | Approve source-traceable signal definitions, populations, thresholds, limitations, validation protocol, and accountable clinical sign-off. |
| Clinically approved route precedence, uncertainty semantics, and self-care exclusions                        | `docs/08_SAFETY_AND_TRIAGE_POLICY.md`, Policy-independent framework behavior and P9-B synthetic mechanics                                             | Clinical safety governance                                                      | **NONE RECORDED** as of 2026-10-19                      | P9-B symbolic precedence in local/test only; no medical significance                          | **OPEN**                           | Approve deterministic clinical precedence, missing-data behavior, exclusions, reason codes, and reviewed cases.                            |
| Approved patient/clinician wording, emergency disclaimers, accessibility, localization, and escalation links | `docs/22_UX_AND_USER_FLOWS.md` §§21–24; `docs/29_ENGINEERING_STANDARDS.md` §§220–221, 267, 329                                                        | Clinical safety, content, accessibility, and localization owners                | **NONE RECORDED** as of 2026-10-19                      | Existing generic urgent-help copy only                                                        | **OPEN**                           | Approve exact route/degraded copy, languages, accessibility evidence, escalation resources, ownership, and review versions.                |
| Deployment-specific policy identity/version, approval evidence, lifecycle, monitoring, rollback, and expiry  | `docs/08_SAFETY_AND_TRIAGE_POLICY.md`, Validation and lifecycle gate; `docs/34_MASTER_IMPLEMENTATION_PLAN.md` §17                                     | Clinical governance and platform operations                                     | **NONE RECORDED** as of 2026-10-19                      | P9-A engineering metadata in local/test only; metadata checksum is not approval               | **OPEN**                           | Record signed approval evidence, environments, effective/expiry dates, monitoring, incident response, retirement, and rollback.            |
| Session, consent, encounter/object authorization for safety read/evaluate endpoints                          | `docs/06_API_CONTRACTS.md` §14 conceptual future example; `docs/26_PRIVACY_CONSENT_SPEC.md` §§2–6                                                     | Identity/security, privacy/legal, and application architecture owners           | **NONE RECORDED** as of 2026-10-19                      | Existing deterministic P7 session/consent use only; no safety endpoint                        | **UNIMPLEMENTED**                  | Approve exact purpose/scope and implement bearer, consent, encounter ownership, terminal-state, IDOR, and real PostgreSQL tests.           |
| Persistence, retention, deletion, audit/outbox, and policy/input provenance                                  | `docs/05_DATABASE_SCHEMA.md` §13 conceptual tables; `docs/26_PRIVACY_CONSENT_SPEC.md` §§7–9                                                           | Data governance, privacy/legal, security, and clinical governance owners        | **NONE RECORDED** as of 2026-10-19                      | No safety persistence; Alembic remains `p7a_0007`                                             | **OPEN — no migration authorized** | Approve minimum data, provenance, lifecycle, retention/deletion, access, audit/outbox, rollback, and migration design.                     |
| API idempotency/concurrency, evaluation consistency, recomputation, and ambiguous recovery                   | `docs/06_API_CONTRACTS.md` §14; `docs/33_ERROR_HANDLING_POLICY.md` §§6, 9, 11                                                                         | API/application architecture owner                                              | **NONE RECORDED** as of 2026-10-19                      | No `/safety/evaluate` activation                                                              | **OPEN**                           | Define idempotency, optimistic concurrency, source/version pinning, reevaluation, atomicity, and no-replay recovery.                       |
| Self-care eligibility release and hard fail-closed block across future consumers                             | `docs/00_PROJECT_MASTER_SPEC.md` §§6, 28; `docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md` AC-P9-008                                             | Clinical safety and self-care governance owners                                 | **NONE RECORDED** as of 2026-10-19                      | No active self-care workflow or authorization                                                 | **BLOCKED — no implied release**   | Approve real policy and P15 integration; prove exclusions and that unavailable/invalid safety always blocks continuation.                  |
| P8-C real-patient AI gates                                                                                   | `docs/implementation/P8_C_INTEGRATION_GATE_REVIEW.md`, Gate evidence and Stage 3 checklist                                                            | Clinical, identity/security, privacy/legal, data governance, and product owners | P8-C gate review / 2026-10-19; no approval IDs recorded | Synthetic process-local, zero-egress P8 evidence only                                         | **OPEN — unchanged**               | Complete every recorded P8-C clinical, role, consent, egress, retention, confirmation, privacy, and production gate.                       |
| Threat/privacy/clinical-safety review and explicit production/pilot enablement                               | `docs/08_SAFETY_AND_TRIAGE_POLICY.md`, Validation and lifecycle gate; `docs/26_PRIVACY_CONSENT_SPEC.md`; `docs/29_ENGINEERING_STANDARDS.md` §§130–131 | Security, privacy/legal, clinical safety, product, and deployment owners        | **NONE RECORDED** as of 2026-10-19                      | Local/test synthetic proof only; a fake is never production authority                         | **OPEN**                           | Complete reviewed threat/data-flow/clinical-safety assessments and record explicit environment-specific enablement and rollback decision.  |

## Authorized Stage 2 implementation

The approved engineering subset may add:

1. a closed TypeScript presentation state with `NOT_AVAILABLE`, `DEGRADED`, and
   `ENGINEERING_SYNTHETIC_PREVIEW`;
2. a strict allowlist parser that accepts the exact P9-B decision shape and exact synthetic policy
   identity only in explicitly supplied `LOCAL` or `TEST` environments;
3. unavailable/degraded defaults that always block hypothetical self-care continuation;
4. an isolated pure React component used only from component tests, with no app route, BFF, network,
   persistence, patient data, clinical advice, or runtime source;
5. regression tests proving synthetic labeling, accessibility, protected-environment refusal,
   bounded output, and unchanged P7/P8-C/public-route boundaries.

The trust boundary is deliberately incomplete for patient use. A future authenticated server API
must load validated minimum-necessary signals from authoritative server state, enforce exact session,
consent, encounter ownership, policy lifecycle, and persistence rules, and return a minimized,
strictly versioned response. Browser-supplied route or approval fields can never establish authority.

## Stage 3 authorization checklist — design only, not implementation approval

- [ ] Clinician-approved, versioned physical-safety policy and typed patient signal schema
- [ ] Approved route precedence, ambiguity behavior, self-care exclusions, reason codes, and reviewed cases
- [ ] Approved patient/clinician copy, emergency disclaimers, localization, accessibility, and escalation resources
- [ ] Deployment policy identity, approval evidence, effective interval, expiry, monitoring, rollback, and incident plan
- [ ] Exact bearer, SESSION consent purpose/scope, encounter ownership, permission, and terminal-state contract
- [ ] Authorized `POST /api/v1/encounters/{encounter_id}/safety/evaluate` contract with `no-store` and common safe errors
- [ ] Idempotency, concurrency, recomputation, changed-input/version, and ambiguous-request recovery semantics
- [ ] Approved persistence, retention, deletion, audit/outbox, provenance, atomicity, and Alembic migration
- [ ] P15 self-care authorization that fails closed on missing, invalid, retired, or degraded policy
- [ ] All P8-C role, consent, egress, retention, confirmation, privacy, and production gates closed
- [ ] Independent clinical validation, threat/privacy review, security tests, and explicit pilot/production enablement

Until every applicable item is approved and recorded authoritatively, no real safety evaluation API,
BFF, patient result, route-specific clinical copy, persistence, self-care release, or production
triage may be implemented or activated.

## Acceptance classification

P9-C is `PARTIAL — SAFE PRESENTATION ENGINEERING SUBSET / PATIENT ROUTING BLOCKED`. P9 remains
`PARTIAL`. P8-C remains `PARTIAL` and approval-blocked. Stage 2 tests are presentation-architecture
and degraded-state evidence only; they are not a patient safety journey, clinical acceptance,
database evidence, or production authorization.
