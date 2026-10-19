# P10 clinician and provenance readiness-gate review

Date of repository review: 2026-10-19
Required baseline: `main @ 08219993e96e2023500370bcaf4057c29f289df6`
Purpose: independently auditable design gate; **not a permission grant**

## Decision

P10 live clinician access is **BLOCKED**. The repository has P5 fact/provenance foundations, P7
deterministic patient intake, provider-neutral identity contracts, and a clinician-web empty shell.
It does not have trusted production clinician identity, an assignment source, governed access to
pseudonymous encounters, a clinician queue/API, summary implementation, review workflow, or approved
clinical-summary persistence.

An isolated P10-A domain/test-only subset may be proposed after independent review of the two Pre-P10
specifications. That subset is limited to pure summary types, deterministic source-backed projection,
state guards and non-PHI tests. It cannot add live routes, clinician data access, persistence, a
migration, external AI, P9 safety content, or production activation without a later explicit prompt
and applicable gate closure.

## Gate matrix

| Gate                                                                                      | Authoritative source                                                                                                                  | Accountable owner                                             | Evidence / approved scope                                                                                                    | Status      | Action and P10 impact                                                                                                                                                                       |
| ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Clinical source and summary correctness; no invented diagnosis                            | `docs/01_PRODUCT_REQUIREMENTS.md` FR-SUM-001..008; `docs/04_DOMAIN_MODEL.md` §§11–13, 37; `docs/12_CLINICAL_PROVENANCE_SPEC.md` §§2,4 | Clinical governance + summaries owner                         | P5 typed facts/guards exist; **NONE RECORDED** for clinical summary validation. Synthetic/non-PHI deterministic design only. | **OPEN**    | Approve source eligibility, abstention, terminology, contradictions, validation cases and sign-off. P10-A limited to policy-neutral mechanics.                                              |
| Trusted clinician identity, actor integrity, assignment/institution, MFA and audit access | `docs/06_API_CONTRACTS.md` §34; `docs/24_CLINICIAN_DASHBOARD_SPEC.md` §1; identity authorization code                                 | Identity/security + institutional governance                  | Role permissions and `ActorContext` exist; **NONE RECORDED** for IdP, directory, assignment or organization policy.          | **BLOCKED** | Select/configure trusted provider; define assurance, active/disabled lifecycle, assignment/transfer and tenant rules, MFA and audit. Blocks P10-B/C/D live use.                             |
| Lawful clinician access to pseudonymous P7 encounter; purpose, consent and sharing        | `docs/26_PRIVACY_CONSENT_SPEC.md`; P8-C gate; dashboard spec §1                                                                       | Privacy/legal + clinical operations + consent owner           | General product consent covers existing first-party P7 flow only; no transitive clinician-sharing approval.                  | **BLOCKED** | Record lawful basis/purpose, disclosure/withdrawal behavior, assignment transfer and minimum fields. Blocks P10-B/C/D.                                                                      |
| Medication/allergy completeness states and clinical UI wording                            | FR-CLIN-004; AC-P10-003; dashboard spec §2.2                                                                                          | Clinical content + medication safety + accessibility owners   | Typed P5 projections exist; **NONE RECORDED** for `UNKNOWN`/`NOT_RECORDED`/`UNVERIFIED` clinical copy.                       | **OPEN**    | Approve completeness semantics, conflict display, freshness and accessibility. Blocks clinical acceptance of P10-B/C.                                                                       |
| Source-detail permissions and P11/P16/P17 availability                                    | FR-CLIN-007/011; FR-PROV-002/007; provenance spec §§2.1,4                                                                             | Source-module owners + privacy/security                       | Bounded P5 source references exist; document/FHIR/ABDM viewers are not implemented.                                          | **OPEN**    | Define source-specific authorization/lifecycle and safe unavailable response. Defer actual viewers to P11/P16/P17; affects P10-B/D.                                                         |
| Fact confirm/correct/reject lifecycle, concurrency and rollback                           | API contracts §15; provenance spec §3                                                                                                 | Patients/provenance owners + clinical governance              | P5 guarded supersession exists; no clinician disposition API/audit contract.                                                 | **OPEN**    | Approve transitions, reviewer responsibility, expected versions, idempotency and transaction failure behavior; implement real PostgreSQL/API tests in P10-D.                                |
| Summary versions, persistence, provenance, audit/outbox, retention/deletion and migration | Domain model §37; database schema §16; dashboard spec §4                                                                              | Summaries + data governance + privacy/security owners         | Conceptual schema only; `summaries` is empty; **NONE RECORDED** for lifecycle/retention/migration.                           | **OPEN**    | Approve strict section/source schema, status/version consistency, retention/deletion, audit/outbox minimization and migration. P10-A may remain in-memory/domain-only; persistence blocked. |
| Clinical facts versus intake/P8 candidates; P8-C and P9-C isolation                       | P8-C and P9-C gate reviews; provenance spec §4.1                                                                                      | Clinical/AI/safety/privacy governance                         | P7 deterministic intake and synthetic P8/P9 engineering evidence only. Patient-facing stages remain blocked.                 | **BLOCKED** | Keep P7 labels, prohibit candidate promotion, external AI and synthetic safety display. Any later use requires every applicable P8-C/P9-C approval. Impacts all P10 phases.                 |
| Threat, privacy, accessibility and security review; production activation/rollback        | Engineering standards; privacy spec; dashboard spec §§3,5                                                                             | Security + privacy/legal + accessibility + operations/product | General engineering controls exist; **NONE RECORDED** for P10 data flow, production hosting or rollback approval.            | **OPEN**    | Complete data-flow/threat/privacy/accessibility reviews, penetration/IDOR tests, monitoring and explicit environment enablement. Blocks P10-C/live production.                              |

## Counts and ownership conclusion

- Approved for live clinician access: **0 of 9** gates.
- Open: **6 of 9** gates.
- Blocked: **3 of 9** gates.
- Existing technical foundations are evidence, not approvals.
- Owners requiring decisions: clinical governance; clinical content/medication safety; identity and
  institutional security; privacy/legal and consent; patients/provenance/summaries/source module
  owners; data governance; accessibility; platform operations and product governance.

## P10 phase disposition

| Phase | Disposition                                                                                                                                            |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| P10-A | **CONDITIONALLY READY FOR INDEPENDENTLY REVIEWED DOMAIN/TEST-ONLY SUBSET**; no live actor, API, persistence, migration, AI or clinical approval claim. |
| P10-B | **BLOCKED** on trusted identity, assignment/institution authority, lawful access and read-model approval.                                              |
| P10-C | **BLOCKED FOR SENSITIVE DATA** on P10-B plus accessibility/security/privacy and hosting approval.                                                      |
| P10-D | **BLOCKED** on review authority, lifecycle/concurrency, audit/outbox/retention and real transactional evidence.                                        |

## Preserved upstream restrictions

P8-C Stage 3 remains blocked: no patient-facing AI, external clinical-data egress, patient message
persistence, unconfirmed-candidate promotion, or AI summary composition is authorized. P9-C Stage 3
remains blocked: no real safety API/persistence, patient routing, triage, clinical alert, self-care
release, or synthetic policy presentation is authorized. P7 answers remain patient-reported,
non-diagnostic structured intake and are not interchangeable with P5 clinical facts.

## Review checklist before the next code prompt

- [ ] Independent review accepts `docs/12_CLINICAL_PROVENANCE_SPEC.md` and
      `docs/24_CLINICIAN_DASHBOARD_SPEC.md` without treating them as clinical approval.
- [ ] Any P10-A prompt states whether it is domain-only and explicitly excludes routes, live
      clinician identity, persistence/migrations and AI/safety activation.
- [ ] Gate owners record authoritative decision IDs, approved environment/population/use and dates
      before a blocked capability enters implementation scope.
- [ ] P10 completion is not claimed until AC-P10-001..009 have implementation evidence.
