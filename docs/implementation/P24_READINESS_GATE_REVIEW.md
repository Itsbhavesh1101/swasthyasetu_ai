# Pre-P24 — Pilot, Release and Operational Accountable Readiness Review

> **DRAFT — EIGHT DESCRIPTIVE, UNSIGNED HUMAN REVIEW DOMAINS; NOT AN OFFICIAL P24 GATE COUNT, RELEASE BOARD, GO/NO-GO DECISION OR PILOT AUTHORIZATION**

**Recorded:** 2026-10-25

**Reviewed baseline:** `main @ 4f4a128566635231dd498ae84c79664cbb53a95a`

**Current technical classification:** **NOT ELIGIBLE FOR P24 PILOT DECISION — UPSTREAM GATES OPEN/BLOCKED**

**Formal release decision:** **NOT RECORDED**

P24 and every engineering, pilot, deployment and release activity under it remain **NOT STARTED**. Every `AC-P24-001..013` criterion is **LIVE NOT VERIFIED**. `OPEN` means an accountable review could proceed when its evidence exists; `BLOCKED` means prerequisite authority or evidence is absent. Neither label is a pass, gate count, waiver, approval, or human release decision.

Source precedence is approved clinical/safety policy; the [Project Master Specification](../00_PROJECT_MASTER_SPEC.md); [System Architecture](../02_SYSTEM_ARCHITECTURE.md); [Product Requirements](../01_PRODUCT_REQUIREMENTS.md); privacy/security and domain sources; [Engineering Standards](../29_ENGINEERING_STANDARDS.md); [Master Implementation Plan](../34_MASTER_IMPLEMENTATION_PLAN.md); [Phase Acceptance Criteria](35_PHASE_ACCEPTANCE_CRITERIA.md); then this review. The companion [P24 evidence assessment](P24_PILOT_EVIDENCE_AND_RELEASE_SCOPE_ASSESSMENT.md) contains the detailed applicability, document and rehearsal registers.

Current technical evidence comprises P0–P7 engineering, bounded synthetic/detached P8–P11 subsets, 13 Chromium checks, real PostgreSQL migration/integration tests, local Docker health and six CI jobs. It does not establish clinical validation, human-participant ethics, institutional authority, platform-wide security acceptance, accessibility certification, performance/recovery evidence, operational staffing, or pilot eligibility.

## 1. Approved scope, institution, ethics, participant governance and lawful basis — BLOCKED

- **Current evidence:** P7 has a pseudonymous first-party manual intake under `GENERAL_PRODUCT_USE` / `clinical_intake`. Product Requirements §46 supplies release labels but no approved scope. No institution, study population, jurisdiction, protocol, recruitment, participant count, dates, legal basis or ethics decision is recorded.
- **Conditionality:** owners must classify every proposed capability as included, excluded or not applicable for one exact environment. No model or document may infer scope from technical availability.
- **Why missing:** no genuine pilot protocol, institution agreement, ethics/IRB-equivalent determination where required, participant safeguards, approved pilot notice/consent, entry/exit/stopping rules or evidence owner exists.
- **Accountable reviewers:** institution/product, qualified clinical/safety, ethics/legal/privacy, research/statistical, participant-safeguard, accessibility and independent release roles.
- **Required signed evidence:** exact intended use, population, institution, jurisdiction, environment, capability applicability, legal/ethics decisions, purpose-specific notice/consent, data flow, safeguards, stopping/withdrawal and adverse-event process.
- **Adversarial/negative cases:** scope creep; consent-purpose substitution; vulnerable person without approved authority; forged/stale approval; wrong institution/environment/build; continued collection after withdrawal or stopping rule.
- **Residual risk / safer alternative:** human harm, unlawful processing and misleading participation remain uncharacterized. Keep activity synthetic/offline and do not recruit, enroll or collect.
- **Hard STOP:** no human pilot, real patient, clinician practice, institution participation, invitation, protocol execution or clinical testing. A candidate worksheet may be reviewed manually only.

## 2. Clinician-owned physical/mental safety policies, enabled languages, crisis copy/resources and evaluation oracles — BLOCKED

- **Current evidence:** Spec 08 explicitly has no real clinical policy; P9 uses engineering-only synthetic fixtures and detached presentation. P8-C/P9-C Stage 3 remain blocked. P14 is an unapproved framework; `/urgent-help` says verified resources are not configured.
- **Conditionality:** physical or mental clinical behavior, patient copy, crisis/resource path and every enabled language require exact approved scope. Disabling a module is not approval to use any dependent behavior.
- **Why missing:** no approved policy source, population, signal/threshold, ambiguity rule, simultaneous-channel precedence, route semantics, copy, current resources, multilingual equivalence, held-out clinical set, pre-registered metric or independent oracle.
- **Accountable reviewers:** qualified physical and mental-health clinical safety, emergency/resource, clinical-language, accessibility/content, privacy, institution, research/statistical and independent clinical validation roles.
- **Required signed evidence:** versioned policies, source authority, effective/expiry lifecycle, approved copy/resources, frozen held-out data, no-training guarantee, route concordance/critical-false-negative/clarification methodology, actual results and rollback/incident plan.
- **Adversarial/negative cases:** negation, quotation, historical/third-party language, ambiguity, missing context, code switching, model downgrade, simultaneous signals, stale policy/resource, provider/LLM outage and unsafe self-care continuation.
- **Residual risk / safer alternative:** no safe clinical outcome can be inferred. Preserve only P7 manual intake and generic non-clinical help; render high-risk modules unavailable.
- **Hard STOP:** no diagnosis, triage, crisis assertion, medical reassurance, clinical threshold, safety result, resource promise or patient-facing activation.

## 3. Conditionally enabled self-care, verified provider/resource, referral and clinician/document pathways — BLOCKED

- **Current evidence:** P10/P11 live gates remain 0/9 approved; P11 is five OPEN/four BLOCKED. Clinician and admin apps are shells. P13 has no registry/referral runtime. P15 is an unapproved draft with no content corpus or eligibility policy.
- **Conditionality:** only a signed scope decision can mark a pathway excluded. If enabled, all owning clinical, source, identity, consent, privacy/security and operational requirements apply.
- **Why missing:** no trusted clinician identity/assignment/MFA/source access; upload/storage/scanner/OCR flow; approved self-care corpus; verified provider/resource record; recipient; referral status authority; or external delivery adapter.
- **Accountable reviewers:** clinician/institution identity, document security/source/provenance, self-care/medication/content, provider/resource/referral/source governance, privacy/consent, accessibility and operations.
- **Required signed evidence:** exact approved source/version/recipient; identity/assignment matrix; hostile-file and source-view tests; content eligibility/exclusion validation; registry freshness/revocation; referral minimization, idempotency and authoritative status.
- **Adversarial/negative cases:** fabricated or stale contact/remedy; malicious file; cross-patient source; role/header forgery; clinician fact promotion without provenance; wrong recipient/purpose; duplicate/ambiguous referral; revoked consent.
- **Residual risk / safer alternative:** misinformation, unauthorized disclosure and unsafe treatment remain possible. Keep document/results/referral routes honestly unavailable and provide no self-care output.
- **Hard STOP:** no upload, OCR, clinician review, remedy, provider display/contact or external sharing. Any referral requires active purpose-specific `REFERRAL_SHARING` consent plus every additional applicable requirement.

## 4. Privacy notice, per-purpose/participant consent, data minimization, retention/deletion/derived copies and audit — BLOCKED

- **Current evidence:** P4 centralized consent and P6/P7 server-only bearer/browser protections exist. Spec 26 states `privacy-v1` is an engineering boundary, P7 consent is non-transitive, and retention/deletion decisions remain unresolved. Audit module is absent.
- **Conditionality:** actual purposes, data classes, processors, stores and enabled modules determine the required notice/consent/retention matrix; qualified owners decide, not software.
- **Why missing:** no pilot notice or participant/research consent; no optional-processing permissions; no per-store schedule, legal-hold rule, purge/reconciliation system, provider deletion, backup deletion, derived-copy inventory or production audit design.
- **Accountable reviewers:** privacy/legal/ethics, institution/records, consent, data governance, audit, security, domain/provider owners and SRE/backup.
- **Required signed evidence:** purpose/data-flow register; minimum-field allowlists; versioned accessible notice/consent; withdrawal/in-flight rules; retention/hold/deletion schedule; tested purge/failure/restore reconciliation; access-controlled audit evidence.
- **Adversarial/negative cases:** general-consent substitution; wrong/expired/revoked purpose; excess data; retry after withdrawal; orphan derivative; backup resurrection; provider refusal; cross-tenant read; raw sensitive log/metric/export.
- **Residual risk / safer alternative:** overcollection, retained derivatives and false deletion promises remain unresolved. Process no pilot data and create no new signal or audit export.
- **Hard STOP:** no real-data access, retention promise, research conversion, referral/AI/OCR/speech/FHIR/ABDM consent inference or participant collection.

## 5. Platform threat model, production identity/MFA/authorization, secrets, vendor/interop security and incident runbook — BLOCKED

- **Current evidence:** deny-by-default authorization primitives, opaque sessions, locked dependencies, Gitleaks/Trivy CI, non-root image and P11-focused Specs 27/28 exist. P21 admin/production IdP work is not started. The prior Trivy metadata warning `CVE-2026-107891` remains for security-owner disposition.
- **Conditionality:** an exact deployment, vendor, data flow and enabled integration determine the threat surface; no generic draft supplies environment acceptance.
- **Why missing:** no current platform-wide threat assessment, production IdP/proofing/MFA/recovery, institution assignment authority, secret manager/rotation, TLS/encryption deployment evidence, vendor risk/egress, penetration evidence, incident runbook or signed finding register.
- **Accountable reviewers:** security/AppSec, identity/IAM, privacy/legal, institution, supply-chain, vendor/interop, data, SRE/incident and independent security reviewers.
- **Required signed evidence:** exact environment/data-flow threat model; access/object/institution matrix; credential lifecycle; vendor/endpoint/region controls; finding reproduction/disposition; incident communication/evidence; rollback and expiry/re-review.
- **Adversarial/negative cases:** IDOR, role/MFA/header forgery, secret leakage, malicious dependency/artifact, stale scanner database, endpoint/recipient substitution, prompt/file injection, SSRF, incident-owner outage and wrong-environment credential.
- **Residual risk / safer alternative:** platform and vendor risk is not characterized. Keep privileged, upload and external integration paths unavailable; use no production credentials.
- **Hard STOP:** no platform security signoff, vulnerability waiver, production identity, pentest claim, FHIR/ABDM/external processing or pilot risk acceptance.

## 6. P23 E2E, independent accessibility/multilingual validation, performance and observability — BLOCKED

- **Current evidence:** 13 Chromium checks comprise 11 patient checks and two staff-shell checks. One real synthetic-data P7 journey covers session/consent/intake. Static/browser accessibility primitives and privacy-safe PWA behavior exist. `tests/performance` contains only `.gitkeep`; OpenTelemetry is in-process with no approved production exporter.
- **Conditionality:** approved critical journeys, locales, assistive technologies, kiosk/device environments, workloads and operational signals depend on signed scope. No future owner choice is made here.
- **Why missing:** P23-A/B/C/D are not started; 18 integrated journeys are mostly absent/blocked; no complete human keyboard/screen-reader/language review, WCAG certification, workload/target/baseline, field sink/dashboard/alert, trend review or trial evidence capture.
- **Accountable reviewers:** independent QA, qualified accessibility/AT, clinical-language/content, privacy/security, product/institution, SRE/performance/observability and every domain owner.
- **Required signed evidence:** exact-SHA browser/API/DB outcomes and abstention oracles; human AT/language/kiosk audit; approved synthetic workload and reproducible measurements; privacy-reviewed signal/sink/access/retention/dashboard/alert evidence.
- **Adversarial/negative cases:** false integrated success; keyboard trap; hidden help; bad focus/error semantics; language drift; shared-device residue; overload/DB hotspot/timeout cascade; sensitive telemetry; missing or false-healthy alert.
- **Residual risk / safer alternative:** exclusion, unsafe language, performance collapse and blind operation remain possible. Use only bounded engineering demos with no pilot label or measurement claim.
- **Hard STOP:** no `AC-P23` pass, accessibility certification, clinical-language acceptance, performance/SLO claim, production observability acceptance or field monitoring.

## 7. Deployment/rollback, policy/model/resource disable, worker outage, backup/restore, purge and recovery rehearsal — BLOCKED

- **Current evidence:** local Docker/PostgreSQL health, explicit migrations, transactional outbox and process-local job abstractions exist. Optional features default safe/off. These do not establish a durable worker, production deployment, backup, restore, purge, rollback or incident capability.
- **Conditionality:** only an approved scope/environment can determine relevant components and safe-off behavior. A signed human decision must document every non-applicable item.
- **Why missing:** no release artifact/promotion pipeline, SLO/RTO/RPO, durable job lease/restart, owned kill-switch inventory, policy/model/resource lifecycle, database backup/restore design, purge workflow, deployment rollback or real exercise.
- **Accountable reviewers:** SRE/platform/release, incident, data/backup, privacy/records, security, clinical policy, model/resource/integration and affected domain owners.
- **Required signed evidence:** separately authorized synthetic nonproduction rehearsals tied to exact build/config; state/health/privacy oracles; worker crash/replay/outbox duplicate tests; restore/deletion reconciliation; disable/rollback authorization and incident records.
- **Adversarial/negative cases:** partial deploy, migration/version drift, failed rollback, stale policy/model/resource, retry storm, poison job, duplicate/late effect, ambiguous external send, database loss, backup resurrection and purge failure.
- **Residual risk / safer alternative:** recovery and operational authority are unknown. Keep optional features off/unavailable; preserve P7 manual/text/touch and generic help without claiming crisis coverage.
- **Hard STOP:** no drill is executed by this pack; no durability, exactly-once, recoverability, backup/restore, purge, kill-switch or operational-readiness claim.

## 8. Independent release board, residual risk, entry/exit/stopping rules and bounded approval record — BLOCKED

- **Current evidence:** six CI jobs and unsigned P22/P23 evidence inventories exist. P22-A/B/C/D/E and P23-A/B/C/D remain not started; every P24 criterion is live unverified.
- **Conditionality:** an independent human release body decides scope, required signers, non-waivable criteria, conditions, expiry and evidence. Eight review domains here are descriptive only.
- **Why missing:** no release board/authority, candidate manifest, approved criteria, actual safety/accessibility/performance/recovery results, residual-risk register, entry/exit/stopping rules, pilot contact/incident plan or signed decision.
- **Accountable reviewers:** independent release authority; institution/product; clinical/safety; privacy/legal/ethics; security; accessibility/language; SRE/incident; data/records; research/model/interop; independent QA.
- **Required signed evidence:** complete applicable upstream approvals and exact-SHA results; reviewer qualifications/conflict separation; findings/waivers by qualified owners; conditions and remediation verification; monitoring, stop, rollback, expiry and re-review.
- **Adversarial/negative cases:** automated/AI signature; CI-only release; forged/stale/expired approval; wrong build/environment; hidden excluded module; unresolved mandatory criterion; scope creep; release after failed stop/rollback evidence.
- **Residual risk / safer alternative:** no accountable body has accepted risk. Keep P24 not started and the system outside human pilot/production use.
- **Hard STOP:** final `GO`, `CONDITIONAL GO` or `NO-GO` is **NOT RECORDED**. Current technical blocked status is not a human decision.

## 9. Canonical `AC-P24-001..013` compact STOP matrix

Exact wording is reproduced from [Phase Acceptance Criteria](35_PHASE_ACCEPTANCE_CRITERIA.md).

| ID and exact canonical requirement                                                                   | Domain(s) | Current STOP                                                      | Status                |
| ---------------------------------------------------------------------------------------------------- | --------- | ----------------------------------------------------------------- | --------------------- |
| `AC-P24-001` — Required clinical policy approvals exist.                                             | 2, 3      | Required policies remain absent or unapproved.                    | **LIVE NOT VERIFIED** |
| `AC-P24-002` — Mental-health policy/copy/resource approvals exist where the module will be used.     | 2         | Applicability and all policy/copy/resource approvals are pending. | **LIVE NOT VERIFIED** |
| `AC-P24-003` — Self-care knowledge approval exists where the module will be used.                    | 3         | Applicability, policy and corpus approval are pending.            | **LIVE NOT VERIFIED** |
| `AC-P24-004` — Provider/resource registry is verified and current.                                   | 3         | No registry, records or freshness authority exists.               | **LIVE NOT VERIFIED** |
| `AC-P24-005` — Privacy notice and consent text are approved for pilot context.                       | 1, 4      | No pilot context, notice or consent is approved.                  | **LIVE NOT VERIFIED** |
| `AC-P24-006` — Threat model and incident runbook are complete.                                       | 5         | Platform assessment and runbook are absent.                       | **LIVE NOT VERIFIED** |
| `AC-P24-007` — Retention/deletion procedures are documented/tested.                                  | 4, 7      | No approved schedule or executed purge/reconciliation evidence.   | **LIVE NOT VERIFIED** |
| `AC-P24-008` — Safety evaluation has predefined metrics and results.                                 | 2, 8      | No pre-registration or results.                                   | **LIVE NOT VERIFIED** |
| `AC-P24-009` — Multilingual safety evaluation is complete for enabled languages.                     | 2, 6      | No enabled clinical language set or validation.                   | **LIVE NOT VERIFIED** |
| `AC-P24-010` — Rollback, policy rollback, model rollback, and resource-disable drills are completed. | 7         | No applicable approved components or drills.                      | **LIVE NOT VERIFIED** |
| `AC-P24-011` — Backup/restore process is tested where pilot environment requires it.                 | 7         | Environment/applicability and test evidence absent.               | **LIVE NOT VERIFIED** |
| `AC-P24-012` — Ethics/legal/privacy prerequisites required for human pilot are complete.             | 1, 4, 8   | No human-pilot prerequisite package exists.                       | **LIVE NOT VERIFIED** |
| `AC-P24-013` — Final release decision is recorded as `GO`, `CONDITIONAL GO`, or `NO-GO`.             | 8         | Human decision **NOT RECORDED**.                                  | **LIVE NOT VERIFIED** |

## 10. Separate research and product-outcome status

The exact canonical wording and detailed evidence for both groups is in [the companion assessment](P24_PILOT_EVIDENCE_AND_RELEASE_SCOPE_ASSESSMENT.md#b-canonical-acceptance-and-evidence-tables). No row becomes P24 acceptance.

| Research requirement | Current status                                                               |
| -------------------- | ---------------------------------------------------------------------------- |
| `NFR-RESRCH-001`     | **NOT VERIFIED — no institutional/ethics human-participant authority**       |
| `NFR-RESRCH-002`     | **NOT VERIFIED — no predefined owner-approved criteria**                     |
| `NFR-RESRCH-003`     | **NOT VERIFIED — no approved held-out dataset/training separation evidence** |
| `NFR-RESRCH-004`     | **NOT VERIFIED — no measured research/pilot result or claim**                |
| `NFR-RESRCH-005`     | **NOT VERIFIED — demos/fluency/CI cannot justify release**                   |

| Product outcomes   | Current status and applicability boundary                                                                                                                                                                |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AC-PROD-001..014` | All fourteen remain **PRODUCT-LEVEL NOT VERIFIED**. Each requires a separately signed scope/applicability and staged-release decision; P24 status neither waives nor automatically includes any outcome. |

## 11. P24 upstream stop map

| Upstream authority/evidence      | Current state                                                                                 | P24 consequence                                                                                |
| -------------------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Clinical/safety/content/resource | P8/P9 patient Stage 3 blocked; P10/P11 0/9 live; P13/P14/P15 unapproved/not implemented       | No clinical, document, provider/referral, mental-health or self-care scope can be enabled.     |
| Privacy/access/consent           | P4/P7 baseline is narrow and non-transitive; pilot/research/optional-purpose decisions absent | No human data collection, optional processing, external sharing or institutional access.       |
| P22 platform security/retention  | P22-A/B/C/D/E not started; `AC-P22-001..011` live unverified                                  | No platform/pilot security, deletion, recovery or finding acceptance.                          |
| P23 validation                   | P23-A/B/C/D not started; `AC-P23-001..012` live unverified                                    | No integrated-journey, human accessibility, performance, recovery or observability acceptance. |
| Institutional/ethics/release     | No protocol, institution, ethics/legal decision, release board or signed candidate            | No pilot decision may be convened or recorded by this document.                                |

## 12. Unsigned review and decision template

```text
Review/decision ID: PENDING
Release candidate/build SHA and immutable manifest: PENDING
Affected AC, capability and owner: PENDING
Approved scope and excluded modules: PENDING
Population, institution, jurisdiction and environment: PENDING
Authority and intended use: PENDING
Legal/ethics/privacy/institution evidence: PENDING
Clinical policy, language, copy and resource versions: PENDING
Notice/consent purpose and versions: PENDING
Data provenance, rights, minimization, retention and deletion: PENDING
Identity, assignment, MFA and authorization evidence: PENDING
P22/P23 exact-SHA evidence and findings: PENDING
Pre-registered criteria, oracles, results and denominators: PENDING
Accessibility, performance, observability and recovery evidence: PENDING
Incident, rollback, restore, purge and safe-off actions: PENDING
Residual risks and accountable owners: PENDING
Reviewer qualifications and conflict separation: PENDING
Decision category: PENDING — NOT RECORDED
Conditions, stopping rules and post-condition verification: PENDING
Effective, expiry and re-review dates: PENDING
Named signers/signatures/date: PENDING
```

No field is populated, approved or signed.

## 13. Role-owner and risk register

| Area                                    | Required accountable roles                                            | Current unresolved risk / state                                   |
| --------------------------------------- | --------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Scope/institution/ethics                | Institution/product, clinical, ethics/legal/privacy, research         | **BLOCKED** — unauthorized human activity or scope creep          |
| Clinical/mental/language safety         | Qualified clinical safety, mental-health, language/content, resources | **BLOCKED** — harmful or fabricated route/copy/resource           |
| Self-care/provider/referral/document    | Content/source/clinician/document/referral/privacy owners             | **BLOCKED** — misinformation, malicious source or disclosure      |
| Consent/retention/audit                 | Privacy/legal/records, data, consent, audit, provider/SRE             | **BLOCKED** — purpose violation, over-retention or false deletion |
| Threat/identity/vendor/incident         | Security/AppSec, identity, supply chain, institution, incident        | **BLOCKED** — uncharacterized compromise or response failure      |
| Accessibility/performance/observability | Accessibility/language, product, SRE, privacy/security, QA            | **BLOCKED** — exclusion, overload, leakage or blind operation     |
| Rollback/restore/recovery               | Release/SRE, data/records, policy/model/resource/domain owners        | **BLOCKED** — loss, duplicate effect or failed safe-off           |
| Final release/risk acceptance           | Independent board and all mandatory authority owners                  | **BLOCKED** — no signed evidence or accountable decision          |

## 14. Manual next actions and final STOP

1. Assign accountable human roles and verify their authority, independence and conflicts.
2. Define a candidate scope without recruiting, enrolling, processing real data or selecting a site/population through this document.
3. Obtain explicit signed applicability decisions for every conditional module and every one of the 13 pre-pilot artifact categories.
4. Complete applicable clinical/source/language, privacy/legal/ethics, identity/security, P22 and P23 evidence.
5. Pre-register evaluation criteria and authorize only synthetic nonproduction rehearsals through separate prompts.
6. Review actual exact-SHA evidence and residual risks; only a qualified human release process may later record a decision.

> **FINAL STOP:** This unsigned docket authorizes no P22/P23/P24 work, human pilot, recruitment, patient/clinician test, data collection, clinical decision, external integration, institutional participation, production credential, deployment, operational drill, release or rollout. Final `GO`, `CONDITIONAL GO` or `NO-GO` remains **NOT RECORDED**. Missing, stale, disputed, expired, scope-incompatible or unsigned evidence fails closed.
