# Pre-P23 — E2E, Accessibility, Performance, Reliability and Observability Accountable Readiness Review

> **DRAFT — EIGHT DESCRIPTIVE OPEN/BLOCKED REVIEW DOMAINS; NOT AN OFFICIAL P23 GATE COUNT, ACCEPTANCE, CLINICAL VALIDATION, ACCESSIBILITY CERTIFICATION OR RELEASE AUTHORIZATION**

**Recorded:** 2026-10-25

**Baseline:** `main @ 4f422146962141c7f427ed083fa2b013e6cddf7f`

**Source hierarchy:** approved clinical/safety policy; Project Master Specification; System Architecture; Product Requirements; privacy/security and domain/API specifications; Engineering Standards; Master Implementation Plan; phase acceptance criteria; this review

**Current phase state:** P23, P23-A/B/C/D and P24 **NOT STARTED**; all `AC-P23-001..012` **LIVE NOT VERIFIED**

The current browser suite contains 13 checks: 11 patient checks, one clinician-foundation check and one admin-foundation check. Its real synthetic-data FastAPI/PostgreSQL P7 journey is bounded technical evidence. It is not a complete cross-module clinical validation suite.

Required reviewers are roles, not invented appointments: qualified physical and mental-health clinical/safety governance; accessibility and supported-language specialists; privacy/legal/consent and records; identity/security/AppSec; SRE/operations/incident/performance/observability; product/institution and patient-content owners; data/domain architecture; P8–P21 capability owners; research/model governance; interoperability; independent quality and release authority. No reviewer name, signature or approval is recorded.

## 1. P7 real bounded journey versus 18 cross-module journeys — OPEN

- **As-built proof:** `tests/e2e/patient.spec.ts` has eleven patient checks, including one synthetic-data P7 intake through real FastAPI/PostgreSQL; `clinician.spec.ts` and `admin.spec.ts` each assert only a foundation heading. PR #52’s six CI jobs passed on the reviewed feature tree.
- **Exact limitation/reason:** P7 proves its manual text/touch, pseudonymous session, consent, draft and privacy boundaries only. Seventeen broader master-plan journeys are absent, detached, blocked or research-unavailable; even journey 1 lacks an approved production clinical pack/population oracle.
- **Accountable reviewers:** P7 product/domain, independent E2E QA, clinical content, consent/privacy, identity/security, database and accessibility owners.
- **Missing decision:** which journeys are critical for each environment/population, their authoritative outcome/abstention oracles, data/fixture rights and allowed trace/evidence retention.
- **Future signed evidence:** version-pinned nonclinical synthetic fixtures; browser/API/PostgreSQL consistency; action and abstention oracles; exact build/config/policy/source hashes; signed scope and independent results.
- **Adversarial scenarios:** cross-session IDOR, stale version, revoked consent, concurrent answer, failed/ambiguous save, unimplemented module falsely shown as success and optional outage blocking P7.
- **Safer fallback:** retain the implemented P7 manual route, generic non-clinical urgent-help navigation and honest unavailable states; never infer missing module results.
- **STOP:** no overall `AC-P23` or product PASS and no cross-module patient test until each owning gate and oracle is separately approved. A future nonclinical synthetic P23-A plan requires a new prompt.

## 2. Physical/mental clinical safety, self-care and qualified oracles — BLOCKED

- **As-built proof:** P9 has isolated deterministic synthetic policy/engine/presentation tests. P8-C/P9-C Stage 3 are blocked. P14/P15 are unapproved documentation; the patient app has generic urgent-help navigation.
- **Exact limitation/reason:** no real-patient physical safety policy, mental-health A/B/C/crisis policy, verified crisis resources, self-care eligibility/contraindication rules, approved medical corpus, simultaneous-channel precedence or clinical outcome oracle exists.
- **Accountable reviewers:** qualified physical safety, mental-health safety, self-care/medication/subject experts, clinical language/content, institution patient-safety, privacy and independent clinical validation roles.
- **Missing decision:** population, exclusions, signals, thresholds, versions/effective dates, ambiguity/negation handling, channel precedence, resources/copy, self-care eligibility, acceptable failure and predeclared validation criteria.
- **Future signed evidence:** clinician-authored held-out/adversarial corpus by supported language, hard-override and non-interference results, resource-source/freshness proof, independent clinical review and incident/rollback evidence.
- **Adversarial scenarios:** model downgrade, simultaneous physical/mental signal, quoted/historical/negated language, ambiguity, missing context, policy/resource outage, stale version and self-care continuation despite unavailable safety.
- **Safer fallback:** no clinical route or self-care output; preserve P7 and generic help without invented emergency content, contacts or reassurance.
- **STOP:** no P9/P14/P15 patient-facing result, live route, clinical claim, crisis assertion or `AC-P23-002/005/006` acceptance. Synthetic planning requires separate authorization.

## 3. Clinician/document/provider/referral/interop/research continuity — BLOCKED

- **As-built proof:** P10 summary and P11 OCR/document contracts are synthetic/detached; P18/P19 are documentation and planning only; clinician/admin apps are foundations. P10/P11 live gates remain 0/9; P11 is five OPEN/four BLOCKED. P13, P16, P17, P18 and P19 runtime is not started.
- **Exact limitation/reason:** no trusted clinician/assignment, upload/storage/scanner/source viewer, verified provider/resource registry, referral lifecycle, speech service, FHIR/ABDM exchange, approved classical task/baseline or QML comparator exists.
- **Accountable reviewers:** clinician identity/institution, P10/P11 document security and clinical source, P12 language, P13 source/referral, privacy/consent, P16/P17 interoperability, P18/P19 research/model governance and independent QA.
- **Missing decision:** authority/source/recipient, assignment, file and source-access policy, active purpose-specific `REFERRAL_SHARING` consent plus all additional lawful/governance controls, profiles/endpoints, research protocol/data/split/metrics and artifact trust.
- **Future signed evidence:** source-backed clinician disposition; hostile-file and source-access tests; verified registry lifecycle; referral idempotency/status; conformance evidence; replayable P18 package and comparable P19 result.
- **Adversarial scenarios:** role/header forgery, cross-patient source, malicious file, stale provider, wrong-purpose sharing, duplicate referral, invalid FHIR profile, identity mismatch, data leakage and unfair research comparison.
- **Safer fallback:** unavailable module with manual entry/navigation; no provider contact, upload, source preview, external sharing, exchange, research inference or patient prediction.
- **STOP:** no `AC-P23-003/004` or product journey acceptance. No external, government or provider endpoint may be invoked. A future nonclinical contract plan still needs a new prompt.

## 4. Accessibility, human assistive review, locales/kiosk and PWA privacy — OPEN

- **As-built proof:** P6/P7 provides landmarks, headings, labels, focus/keyboard checks, contrast calculations, forced-colors/reduced-motion CSS, representative touch targets, 320/390px reflow, a privacy-safe five-path PWA shell, no browser clinical storage, and session closure.
- **Exact limitation/reason:** coverage is a bounded automated subset; no complete critical-journey inventory, independent screen-reader/browser matrix, kiosk deployment review, approved Hindi clinical flow, speech/translation, mental-health language review or working staff flow exists.
- **Accountable reviewers:** qualified accessibility/assistive-technology, UX/content, supported-language and clinical-language reviewers, privacy/security, kiosk institution/operator and each application owner.
- **Missing decision:** critical-flow list, supported AT/browser/device/locale matrix, severity/remediation rule, reviewed copy, kiosk timeout/reset/assistance and evidence-retention/access policy.
- **Future signed evidence:** human keyboard/screen-reader/zoom/contrast/forced-colors/reflow audits; reviewed language equivalence; shared-device privacy checks; reproducible findings tied to exact build and remediation decisions.
- **Adversarial scenarios:** keyboard trap, inaccessible error/status, hidden urgent help, stale focus, bad dialog semantics, failed language switch, clipped content, compromised cache and residual kiosk session.
- **Safer fallback:** text/touch manual flow and honest unavailable copy; no audio, translation or conformance claim.
- **STOP:** `NFR-ACCESS-001`’s WCAG 2.2 AA target is not certification; `AC-P23-008/009` remain unverified. A future nonclinical P23-B audit plan requires separate authorization.

## 5. Performance workload, baselines, measurements and regression thresholds — BLOCKED

- **As-built proof:** `tests/performance/.gitkeep` is empty. CI builds three web applications and runs functional tests; no load/performance job or result exists.
- **Exact limitation/reason:** no approved environment, workload, population, data class, measurement method, pilot load/SLO, latency/error budget, regression threshold, sample size or baseline exists.
- **Accountable reviewers:** product, clinical operations, SRE/performance, database, privacy/security, accessibility and owners of each measured module/external dependency.
- **Missing decision:** exact objective, scope, synthetic workload, warmup/repetition/concurrency, clocks, percentiles/errors/timeouts, DB analysis, uncertainty/outliers, budget, evidence retention and third-party restrictions.
- **Future signed evidence:** versioned experiment plan and isolated environment; exact SHA/config; reproducible raw aggregate measurements and analysis; independent review against owner-approved criteria.
- **Adversarial scenarios:** cold/warm drift, overload, rate-limit interaction, DB hotspot, queue saturation, timeout cascade, measurement leakage, noisy neighbor and unapproved third-party load.
- **Safer fallback:** no result or target; optional dependencies remain off/unavailable and P7 is not subjected to unapproved load.
- **STOP:** no P23-C run, invented milliseconds/RPS/availability/threshold, performance baseline or `AC-P23-010` acceptance. Future planning requires separate authorization.

## 6. Retries, outbox/jobs, worker/recovery and optional-dependency failure — BLOCKED

- **As-built proof:** PostgreSQL transactional outbox tests, explicit dispatcher status/retry foundations, typed timeout/degraded guards and process-local `InProcessJobBackend`/`InProcessWorker` tests exist. P7 is independent of disabled optional modules.
- **Exact limitation/reason:** no integrated durable worker backend, lease/heartbeat, deployment restart, dead-letter/poison handling, owned kill-switch inventory, backup/restore, projection rebuild or cross-module recovery drill exists. The outbox does not claim exactly once.
- **Accountable reviewers:** SRE/incident, data/application architecture, outbox/job owners, affected domain/clinical owners, privacy/security and release engineering.
- **Missing decision:** durability backend, claim/lease/idempotency model, retry/deadline/backoff, ordering/late result, cancellation/tombstone, recovery objective, monitoring, kill-switch authority and rollback/incident process.
- **Future signed evidence:** crash at each side-effect boundary, lease expiry, duplicate/late delivery, retry/replay, restart/reconnect, consent withdrawal/correction races, network partition, rollback and version-drift evidence on approved infrastructure.
- **Adversarial scenarios:** poison job, retry storm, ambiguous external side effect, stale generation commit, DB restart, outbox duplicate, optional LLM/OCR/speech/RAG/provider/FHIR/ABDM/model outage and false success.
- **Safer fallback:** honest `UNAVAILABLE`/`NOT_EVALUATED`, no partial authoritative mutation, preserve P7/manual and generic help; no fake provider substitution.
- **STOP:** no durable recovery, exactly-once, kill-switch or `AC-P23-011` acceptance. A future nonclinical P23-D plan requires a new prompt and owning infrastructure approval.

## 7. Observability, privacy, error states, evidence capture and trend review — BLOCKED

- **As-built proof:** request correlation, structured content-free logging, in-process OpenTelemetry spans/metrics, safe error envelopes and synthetic privacy tests exist.
- **Exact limitation/reason:** Docs 31/32 are absent; no approved exporter/sink, access, retention/deletion, dashboard/query, SLO, alert, clinical signal, trial-evidence capture or incident ownership exists.
- **Accountable reviewers:** SRE/observability, privacy/legal/records, security, incident, audit/data governance, clinical/domain owners, accessibility/product and infrastructure/vendor owners.
- **Missing decision:** signal catalog and semantics; low-cardinality labels; sink/region/vendor; access; retention/deletion/legal hold; alerts/escalation; dashboard audience; evidence integrity and review cadence.
- **Future signed evidence:** canary tests proving no raw narrative/token/prompt/file/credential; sink/config inspection; query/dashboard/alert tests; outage and alert-failure drill; trend-review record tied to exact versions.
- **Adversarial scenarios:** raw sensitive capture, subject/encounter linkability, high-cardinality exhaustion, missing failure signal, false healthy aggregation, unauthorized dashboard/export and telemetry outage.
- **Safer fallback:** collect no new signal under this pack; use content-free local errors and distinguish `NOT_EVALUATED`, `UNAVAILABLE`, failure and healthy states.
- **STOP:** CI success is not field monitoring; no raw patient search or comprehensive `AC-P23-012` claim. Future synthetic evidence planning requires a new prompt and privacy/security review.

## 8. Independent release readiness, clinical/security/privacy approval, risk owner and P24 boundary — BLOCKED

- **As-built proof:** six CI jobs, P22 evidence/readiness documents and upstream gate dossiers exist. P22-A/B/C/D/E and P24 are not started; no live P23 criterion is verified.
- **Exact limitation/reason:** no completed platform-wide P22 assessment/control/retention/resilience program, integrated P23 evidence, qualified approval package, incident exercise, bounded pilot protocol or accountable release decision exists.
- **Accountable reviewers:** independent security/privacy, clinical/safety, accessibility, institutional/product, data/records, SRE/incident, research/interop, risk and release authorities.
- **Missing decision:** pilot population/institution/environment, entry/exit/stopping criteria, accepted evidence and severity rubric, residual-risk owner, unresolved finding disposition, rollback/incident and expiry/re-review.
- **Future signed evidence:** P22 completion evidence; P23-A/B/C/D exact-SHA reports; clinical/accessibility/security/privacy approvals; resolved or formally bounded findings; P24 rehearsal and pre-registered release record.
- **Adversarial scenarios:** forged/stale signature, scope creep, expired approval, CI-only release, unresolved high/critical finding, wrong build/environment and rollback failure.
- **Safer fallback:** keep all unapproved modules safe-off; retain P7 bounded path and no pilot/production label.
- **STOP:** green CI never grants release. No P24 entry, pilot, production, risk acceptance or P23 completion follows from this review.

## 9. Unsigned bounded decision template

```text
Decision ID: PENDING
Affected AC / journey / phase: PENDING
Intended population, institution and environment: PENDING
Authority and intended use: PENDING
Risk, clinical or security classification: PENDING
Sources, versions, code/build SHA and test run: PENDING
Data provenance and fixture rights: PENDING
Consent, privacy, retention and deletion: PENDING
Identity, institution and assignment: PENDING
Criteria and independent oracle ownership: PENDING
Performance, recovery and assistive baseline: PENDING
Result, evidence links, expiry and re-review trigger: PENDING
Independent reviewer qualifications: PENDING
Operational rollback and incident actions: PENDING
Residual risk and owner: PENDING
Named signers and date: PENDING
Signatures: PENDING
```

This template assigns no person, authority, signature, result or approval.

## 10. Owner and risk register

| Decision/evidence area               | Required accountable roles                                         | Current unresolved risk / state                           |
| ------------------------------------ | ------------------------------------------------------------------ | --------------------------------------------------------- |
| P23-A journey/oracle inventory       | Product, domain, clinical, privacy, identity, independent QA       | OPEN — false cross-module success or omitted journey      |
| Physical/mental safety/self-care     | Qualified clinical and language/content governance                 | BLOCKED — no live policy/oracle/resource authority        |
| Clinician/document/provider/referral | Identity/institution, source, P10/P11/P13, privacy/security        | BLOCKED — unauthorized access, hostile data or disclosure |
| P23-B accessibility/locales/kiosk    | Accessibility/AT, language, product, privacy/institution           | OPEN — exclusion or shared-device exposure                |
| P23-C performance                    | Product, clinical ops, SRE/performance, data/privacy               | BLOCKED — misleading workload, result or threshold        |
| P23-D recovery                       | SRE/incident, data/architecture, domain, security/privacy          | BLOCKED — loss, duplicate effects or false recovery       |
| Observability/evidence               | SRE, privacy/security, audit/data, clinical/domain                 | BLOCKED — blind spot or sensitive leakage                 |
| P22/P24 release boundary             | Independent risk, institution, clinical, security/privacy, release | BLOCKED — unaccepted platform and pilot risk              |

## 11. Planned evidence dependency by future slice

| Slice | Must exist before a future implementation/validation claim                                                                                                                                       |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| P23-A | Owning-module runtime approvals; exact 18-journey applicability; synthetic fixture rights; independent action/abstention oracles; identity/consent/privacy scope; browser/API/DB evidence design |
| P23-B | Critical-flow inventory; approved locales/copy; AT/browser/device/kiosk matrix; qualified human-review protocol; privacy-safe evidence handling                                                  |
| P23-C | Approved experiment environment/workload/method/budget; synthetic data rules; observability support; third-party prohibition/authorization; independent statistical review                       |
| P23-D | Approved durable components and failure semantics; idempotency/cancellation/rollback; monitoring and kill-switch authority; incident/recovery environment                                        |

P22 controls remain upstream. P24 release review consumes, but cannot replace, complete and independently reviewed P23 evidence.

## 12. Compact `AC-P23-001..012` STOP crosswalk

| Criterion    | Review domain(s) | Current STOP                                                            |
| ------------ | ---------------- | ----------------------------------------------------------------------- |
| `AC-P23-001` | 1, 4             | P7 bounded evidence only; production critical journey/oracle unapproved |
| `AC-P23-002` | 2                | No live physical safety policy/route                                    |
| `AC-P23-003` | 3, 6             | No upload/storage/OCR/source workflow                                   |
| `AC-P23-004` | 3, 6             | No verified registry/referral lifecycle or exact consent flow           |
| `AC-P23-005` | 2, 3, 4          | No approved mental-health A/B/C policy/resources/language evidence      |
| `AC-P23-006` | 2, 6, 7          | Generic help is not an approved crisis fallback                         |
| `AC-P23-007` | 3, 4, 6          | Speech runtime absent; P7 text/touch is bounded evidence only           |
| `AC-P23-008` | 4                | No complete qualified human keyboard audit                              |
| `AC-P23-009` | 4                | No complete qualified screen-reader review                              |
| `AC-P23-010` | 5, 7             | No approved measurement plan or baseline                                |
| `AC-P23-011` | 6                | No integrated durable worker/recovery proof                             |
| `AC-P23-012` | 7, 8             | No approved production signal/sink/dashboard/alert gap review           |

All twelve remain **LIVE NOT VERIFIED**.

## 13. Separate P24 entry requirements

P24 remains **NOT STARTED**. Before any P24 entry, accountable owners must provide the canonical pre-pilot artifacts: approved clinical and mental-health policies, approved self-care content, verified resource registry, privacy notice and consent text, platform threat model, incident runbook, retention policy, release checklist, pilot protocol, model/dataset cards where applicable, complete P22 control evidence, exact-SHA P23-A/B/C/D results, unresolved-finding disposition, rollback/backup/restore/purge/provider-outage rehearsal and separately authorized institutional pilot criteria. A human pilot must never begin solely because software tests pass.

## 14. Final STOP and accountable next action

Named qualified clinical/safety, accessibility, privacy/legal, security, infrastructure/SRE, product/institution, domain, research/interop, independent quality and release owners must review exact current evidence and sign narrowly bounded decisions. Missing, stale, disputed, expired or unsigned evidence fails closed.

> **FINAL STOP:** This review authorizes no P23-A/B/C/D engineering, patient/clinical test, load measurement, accessibility certification, external integration, observability collection, P24 pilot or release. A new separate prompt and satisfied owning gates are mandatory for every future slice.
