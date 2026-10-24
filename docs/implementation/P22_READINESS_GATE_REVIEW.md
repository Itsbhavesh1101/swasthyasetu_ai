# Pre-P22 — Platform Security, Privacy, Retention and Resilience Readiness Review

> **DRAFT — DESCRIPTIVE ACCOUNTABLE SECURITY/PRIVACY/RESILIENCE REVIEW DOMAINS, NOT AN OFFICIAL GATE COUNT OR P22 IMPLEMENTATION/RELEASE AUTHORIZATION**

**Review date:** 2026-10-25

**Verified baseline:** `main @ 09200acdf5f824a335781249f6a8e56e47b68fcb`

## 1. Decision and source hierarchy

P22 and P22-A/B/C/D/E are **NOT STARTED**. All `AC-P22-001..011` remain **LIVE NOT VERIFIED**. This review is subordinate to approved clinical/safety policy, the Project Master Specification, System Architecture, Product Requirements, Spec 26, accepted ADRs and applicable domain sources. Specs 27/28 remain P11-focused drafts; they are not overwritten or promoted to platform acceptance. Missing Specs 31/32 are not invented.

The eight domains below organize accountable review. They are descriptive categories, not official gates or approval arithmetic. `OPEN` means a bounded review may proceed when evidence exists; `BLOCKED` means a prerequisite authority or decision is absent. Neither status authorizes implementation.

## 2. Eight descriptive review domains

### 1. Production identity, object/institution authorization, privileged MFA and sessions — BLOCKED

- **Actual proof:** opaque high-entropy pseudonymous sessions; provider-neutral identity contracts; server-side deny-by-default permissions; self-subject checks; administrative roles require a trusted `mfa_verified` flag.
- **Missing decisions:** production IdP/proofing, actual MFA and recovery ceremony, actor/role/service-account lifecycle, institution/assignment/object/source/purpose policy, session assurance and revocation.
- **Accountable roles:** identity/IAM, security, institution/employer, privacy, application and operations.
- **Unapproved options:** federated IdP and narrowly scoped service identities behind existing ports; no provider is selected.
- **Evidence/tests:** signed authority matrix; forged role/header/MFA, disabled/revoked actor, stale assignment, wrong patient/institution/object/source, IDOR/enumeration and confused-deputy tests.
- **Residual risk / safe-off:** production trust and cross-institution isolation are unknown; deny without revealing existence and keep P7 pseudonymous flow independent.
- **STOP:** no privileged admin/clinician/source action or live identity claim.

### 2. Browser/BFF/API security, injection/XSS/CSRF, rate limiting and hostile uploads — BLOCKED

- **Actual proof:** same-origin server-only BFF bearer, secure-cookie settings, no-store responses, bounded upstream timeouts, strict response parsing, safe error envelopes, PWA cache allowlist and text-rendering tests.
- **Missing decisions:** protected TLS/header topology, CSP, route-specific CSRF/CORS policy, abuse endpoints/thresholds, upload pattern/types/limits, quarantine/scanner/sandbox and incident handling.
- **Accountable roles:** AppSec, frontend/API, document security, SRE, accessibility/product and independent security reviewer.
- **Unapproved options:** server-streamed or quarantine-only upload; route-specific anti-CSRF and rate controls. No pattern/value/vendor is selected.
- **Evidence/tests:** XSS/malicious link, CSRF/CORS, body/schema bounds, rate bypass, MIME/signature/polyglot/bomb/malware, scanner outage, parser escape, browser cache/storage/error leakage.
- **Residual risk / safe-off:** deployment and hostile-file risks are unmeasured; upload remains unavailable and protected routes fail closed.
- **STOP:** no untrusted file, pilot-hardening or upload-security acceptance claim.

### 3. Purpose/consent/data minimization, external AI and integration egress — BLOCKED

- **Actual proof:** centralized versioned purpose-specific consent for P7; consent events; minimum-context and raw-provider-retention guards in synthetic P8 contracts; provenance boundaries.
- **Missing decisions:** external provider/purpose/notice, lawful/governance basis, recipient, minimum fields, region/subprocessors, training/human review, vendor retention/deletion, cross-border handling and in-flight withdrawal.
- **Accountable roles:** privacy/legal/consent, institution, vendor/integration security, clinical/source and data governance.
- **Unapproved options:** operation-specific egress allowlist with an additional consent/notice decision where required; provider remains unselected.
- **Evidence/tests:** general-consent substitution, wrong/expired/revoked purpose, withdrawal during dispatch, recipient/endpoint/region substitution, excessive/raw payload, prompt/tool injection and production/research mixing.
- **Residual risk / safe-off:** external processing legality and supplier risk are unknown; no egress and existing deterministic P7 fallback.
- **STOP:** authentication or general product consent never authorizes referral, AI, research, FHIR/ABDM or other external sharing.

### 4. Retention, withdrawal/deletion, derived copies, provider deletion, legal holds and backup/restore — BLOCKED

- **Actual proof:** revocation blocks later protected P7 operations; no retention/purge/hold/restore system exists.
- **Missing decisions:** per-purpose data-class schedule and authority across database, events/outbox, objects, OCR/text/vector, caches, telemetry, backup, worker and provider copies; deletion rights, hold precedence, in-flight semantics and restore reconciliation.
- **Accountable roles:** privacy/legal/records, data governance, source-domain owners, provider/vendor and SRE/backup owners.
- **Unapproved options:** tombstone/generation state, idempotent purge, provider receipt and restore reconciliation; no duration or legal conclusion is proposed.
- **Evidence/tests:** partial purge, duplicate/retry, queued late result, orphan derivative, provider refusal, expired hold, concurrent grant/revoke/delete and backup resurrection.
- **Residual risk / safe-off:** over-retention and resurrection risk unknown; make no deletion promise and run no purge.
- **STOP:** `PRIV-003/004` and `AC-P22-007/008` remain unverified until approved execution and recovery evidence exists.

### 5. Audit, logs/traces/metrics, sensitive search, evidence integrity and incident monitoring — BLOCKED

- **Actual proof:** content-free request logging, opaque correlation, safe errors, telemetry primitives, consent/outbox events. Audit module/viewer is absent.
- **Missing decisions:** closed event catalog, source-domain ownership, access/audience, tamper evidence, audit-of-audit, search/export, retention/hold, alerting and breach evidence.
- **Accountable roles:** audit/data governance, privacy/legal/records, security/incident, domain event and institution owners.
- **Unapproved options:** minimized append-only/tamper-evident records and scoped viewer; no storage/cryptographic design is selected.
- **Evidence/tests:** omitted/tampered/reordered event, wrong institution/object read, audit bypass, unrestricted raw search/bulk export, CSV injection and seeded narrative/token/secret canaries across logs/traces/metrics/errors/reports.
- **Residual risk / safe-off:** outbox does not prove audit integrity; no viewer/export and no raw transcript/document/prompt search.
- **STOP:** no compliance or audit-completeness claim.

### 6. Dependency outages, timeouts, feature kill switches, recoverability and P7/urgent-help independence — OPEN

- **Actual proof:** P7 manual text/touch and generic urgent help; safe-off feature flags; disabled adapters; bounded AI deadlines/retries; honest typed degradation; transactional outbox and process-local worker foundations.
- **Missing decisions:** dependency criticality, operational owners, high-risk switch inventory/authority, target recovery behavior, durable job recovery, monitoring, rollback and disaster exercises.
- **Accountable roles:** SRE/platform, incident, product, clinical safety, integration/domain owners and accessibility/content.
- **Unapproved options:** independently scoped server-side switches plus rehearsed rollback; flags remain neither authorization nor clinical policy.
- **Evidence/tests:** LLM/OCR/speech/referral/FHIR/ABDM/model/RAG outage, timeout/retry storm, duplicate callback, poison job, switch authorization/race/bypass, partial deploy and failed rollback while P7/urgent help stay usable.
- **Residual risk / safe-off:** current unimplemented capabilities reduce exposure but do not prove future recovery; keep optional paths unavailable.
- **STOP:** no P22 kill-switch or resilience acceptance from current flags/tests.

### 7. Secrets, supply chain, scanners, container/CI infrastructure and signed dispositions — OPEN

- **Actual proof:** locked dependencies, pinned Actions, Gitleaks/Trivy CI, non-root backend image, reproducible image pins and separated dependency profiles.
- **Missing decisions:** deployed secret manager/rotation, protected environments, SBOM/provenance/signing, advisory/license ownership, scanner database freshness, exception process and production artifact promotion.
- **Accountable roles:** supply-chain security, SRE, AppSec, CI/release, model/artifact governance and independent reviewer.
- **Unapproved options:** phase-activated secret/artifact infrastructure under ADR-040; no product/provider is selected.
- **Evidence/tests:** leaked/rotated credential, tampered lock/action/image/model/hash, unsigned or wrong-environment artifact, stale scanner DB, compromised build secret and rollback.
- **Residual risk / safe-off:** scan success is point-in-time evidence only. The prior Trivy metadata warning for `CVE-2026-107891` requires owner review; it proves neither vulnerability nor resolution.
- **STOP:** no suppression, vulnerability disposition or pilot risk acceptance is created here.

### 8. Platform-wide threat model, independent reviews, incident/rollback and P22/P23/P24 release — BLOCKED

- **Actual proof:** P11-focused Specs 27/28, domain readiness dossiers, six-job CI and local engineering tests. No current platform-wide threat model, penetration assessment, incident exercise or bounded pilot decision exists.
- **Missing decisions:** actual deployment/data flows, asset/threat ownership, independent security/privacy review, finding disposition, incident/rollback, pilot population/environment, release criteria and expiry/re-review.
- **Accountable roles:** security/AppSec, privacy/legal, identity/institution, clinical/safety, platform/incident, accessibility/product, research/interop/vendor and release/pilot owners.
- **Unapproved options:** P22-A non-invasive inventory first, followed only by separately authorized P22-B/C/D/E evidence.
- **Evidence/tests:** complete threat/control traceability, attack-surface regression, finding reproduction/disposition, incident/tabletop, backup/restore and rollback exercise tied to exact code/build/environment.
- **Residual risk / safe-off:** platform risk is not formally characterized or accepted; no pilot/release.
- **STOP:** `AC-P22-011` requires real accountable bounded resolution or acceptance; CI, this review and LLM statements cannot waive a high/critical finding.

## 3. Exact requirements and acceptance traceability

The wording below is verbatim from the baseline canonical sources. “Bounded evidence” is not P22 acceptance.

### 3.1 `AC-P22-001..011`

**Canonical source for every row:** `docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md` at the verified baseline.

| ID and exact wording                                                                           | Baseline evidence                                                   | Domain / missing decision, test or artifact                                                 | Responsible reviewer                                              | Live status           |
| ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | --------------------- |
| `AC-P22-001` — Threat model exists and reflects current architecture.                          | P11-only Spec 28 draft.                                             | Domain 8; current platform data-flow/threat model and independent review absent.            | Security/AppSec, privacy, architecture.                           | **LIVE NOT VERIFIED** |
| `AC-P22-002` — Backend authorization/object-level access tests pass.                           | Bounded P4/P5/P7 unit/API/PostgreSQL tests.                         | Domain 1; platform actor/object/institution/source matrix and cross-module evidence absent. | Identity/security, institution, QA.                               | **LIVE NOT VERIFIED** |
| `AC-P22-003` — Secrets are absent from repository.                                             | Gitleaks CI/local evidence for exact commits.                       | Domain 7; deployed secret inventory, history/artifact scope and accountable review absent.  | Security/supply chain.                                            | **LIVE NOT VERIFIED** |
| `AC-P22-004` — Sensitive logging review completed.                                             | Privacy-safe logging tests and design rules.                        | Domain 5; platform sinks/configs/vendors and independent review absent.                     | Privacy/security/observability.                                   | **LIVE NOT VERIFIED** |
| `AC-P22-005` — Upload security controls tested.                                                | Synthetic P11 metadata guards only; no bytes/upload.                | Domain 2; route, scanner/quarantine/sandbox and hostile-byte evidence absent.               | AppSec/document security.                                         | **LIVE NOT VERIFIED** |
| `AC-P22-006` — Rate limits exist for abuse-prone endpoints.                                    | Rate-limit error vocabulary only.                                   | Domain 2; endpoint inventory, policy, implementation and bypass tests absent.               | AppSec/product/SRE.                                               | **LIVE NOT VERIFIED** |
| `AC-P22-007` — Retention/purge workflow executes successfully.                                 | No purge workflow.                                                  | Domain 4; approved policies, execution and reconciliation absent.                           | Privacy/legal/records/data/SRE.                                   | **LIVE NOT VERIFIED** |
| `AC-P22-008` — Purge failure is observable.                                                    | No purge workflow or signal.                                        | Domain 4; failure state, alert, retry and incident evidence absent.                         | Records/data/SRE/incident.                                        | **LIVE NOT VERIFIED** |
| `AC-P22-009` — LLM/OCR/provider/integration failure modes are tested.                          | Bounded synthetic LLM/OCR contracts and P7 fallback tests.          | Domains 3/6; live provider/integration, egress and environment evidence absent.             | Integration security, QA, domain owners.                          | **LIVE NOT VERIFIED** |
| `AC-P22-010` — Kill switches work for defined high-risk optional features.                     | Safe-off configuration flags; no accepted high-risk switch program. | Domain 6; inventory, independent authority, monitoring and drills absent.                   | SRE, security, clinical/product owners.                           | **LIVE NOT VERIFIED** |
| `AC-P22-011` — High/critical security findings are resolved or formally accepted before pilot. | No bounded pilot finding register or signed acceptance.             | Domains 7/8; real risk owner, scope, expiry, safeguards and evidence required.              | Accountable risk/release owner and independent security reviewer. | **LIVE NOT VERIFIED** |

### 3.2 `NFR-SEC-001..014`

**Canonical source for every row:** `docs/01_PRODUCT_REQUIREMENTS.md` at the verified baseline.

| ID and exact wording                                                                                | Bounded evidence / missing artifact                                                  | Domain and reviewer                | Status                                           |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------------- | ------------------------------------------------ |
| `NFR-SEC-001` — All production network traffic SHALL use TLS.                                       | No production topology/TLS validation.                                               | 2; AppSec/SRE.                     | LIVE NOT VERIFIED                                |
| `NFR-SEC-002` — Sensitive data SHALL be encrypted at rest using appropriate platform controls.      | Local PostgreSQL/object adapter is not production encryption proof.                  | 4/7; security/data/SRE.            | LIVE NOT VERIFIED                                |
| `NFR-SEC-003` — Administrative accounts SHALL require MFA.                                          | Boolean gate tests do not establish an MFA ceremony.                                 | 1; identity/security.              | LIVE NOT VERIFIED                                |
| `NFR-SEC-004` — Authorization SHALL use least-privilege RBAC or equivalent.                         | Small deny-by-default P4 map; full object/institution/source scope absent.           | 1; identity/institution/AppSec.    | BOUNDED TECHNICAL EVIDENCE — NOT P22 ACCEPTANCE  |
| `NFR-SEC-005` — Secrets SHALL NOT be committed to source control.                                   | Gitleaks evidence is point-in-time; deployed/history/artifact review pending.        | 7; supply-chain security.          | BOUNDED TECHNICAL EVIDENCE — NOT P22 ACCEPTANCE  |
| `NFR-SEC-006` — Uploaded files SHALL undergo security validation.                                   | No live upload or byte scanner.                                                      | 2; document/AppSec.                | LIVE NOT VERIFIED                                |
| `NFR-SEC-007` — Patient/user-generated content SHALL be safely rendered to prevent XSS.             | Current React/text and browser tests are bounded.                                    | 2; frontend/AppSec.                | BOUNDED TECHNICAL EVIDENCE — NOT P22 ACCEPTANCE  |
| `NFR-SEC-008` — The application SHALL implement rate limiting for abuse-prone endpoints.            | No rate limiter/endpoints policy.                                                    | 2; AppSec/product/SRE.             | LIVE NOT VERIFIED                                |
| `NFR-SEC-009` — Session tokens SHALL be high entropy and appropriately protected.                   | 32-byte opaque token, hashed persistence and server-only cookie/BFF path are tested. | 1/2; identity/security.            | BOUNDED TECHNICAL EVIDENCE — NOT P22 ACCEPTANCE  |
| `NFR-SEC-010` — Dependencies SHALL be scanned for known vulnerabilities.                            | CI Trivy filesystem scan; ownership/disposition/freshness review pending.            | 7; supply-chain security.          | BOUNDED TECHNICAL EVIDENCE — NOT P22 ACCEPTANCE  |
| `NFR-SEC-011` — Production container images SHOULD be scanned.                                      | Backend CI image is scanned; production promotion scope absent.                      | 7; security/release.               | BOUNDED TECHNICAL EVIDENCE — NOT P22 ACCEPTANCE  |
| `NFR-SEC-012` — LLM prompt injection SHALL NOT be able to bypass deterministic policy.              | Synthetic prompt/authority tests; patient-facing AI remains blocked.                 | 3/6; AI/AppSec/clinical safety.    | BOUNDED TECHNICAL EVIDENCE — NOT LIVE ACCEPTANCE |
| `NFR-SEC-013` — External AI providers SHALL receive the minimum context required for the operation. | Contracts minimize context; no approved real provider/operation.                     | 3; privacy/vendor/AI.              | LIVE NOT VERIFIED                                |
| `NFR-SEC-014` — Sensitive request/response bodies SHALL not be logged by default.                   | Logging/middleware tests are bounded; platform sink review absent.                   | 5; privacy/security/observability. | BOUNDED TECHNICAL EVIDENCE — NOT P22 ACCEPTANCE  |

### 3.3 `PRIV-001..009`

**Canonical source for every row:** `docs/01_PRODUCT_REQUIREMENTS.md` at the verified baseline.

| ID and exact wording                                                                                                        | Bounded evidence / missing artifact                               | Domain and reviewer          | Status                                          |
| --------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ---------------------------- | ----------------------------------------------- |
| `PRIV-001` — Only data required for the active purpose SHOULD be collected.                                                 | P7 minimization exists; future module fields/purposes undecided.  | 3/4; privacy/product/domain. | PARTIAL / LIVE NOT VERIFIED                     |
| `PRIV-002` — Data SHALL be used according to documented purposes and consent/governance.                                    | Central P7 consent; no transitive future authorization.           | 3; privacy/legal/consent.    | PARTIAL / LIVE NOT VERIFIED                     |
| `PRIV-003` — Sensitive transient data SHALL have explicit retention rules.                                                  | Retention ideas are not rules; no schedules approved.             | 4; records/privacy/data.     | LIVE NOT VERIFIED                               |
| `PRIV-004` — Applicable deletion/withdrawal workflows SHALL be supported.                                                   | Consent revoke exists; deletion/purge/restore does not.           | 4; privacy/records/SRE.      | PARTIAL / LIVE NOT VERIFIED                     |
| `PRIV-005` — Referral sharing SHALL use a minimized payload.                                                                | Referral runtime absent; explicit consent still required.         | 3; referral/privacy.         | LIVE NOT VERIFIED                               |
| `PRIV-006` — Anonymous-feeling mental-health first-contact mode SHALL avoid intentional collection of unnecessary identity. | Pseudonymous session primitive; P14 runtime absent.               | 1/3; privacy/mental-health.  | LIVE NOT VERIFIED FOR P14                       |
| `PRIV-007` — Operational logs SHALL exclude raw sensitive content by default.                                               | Content-free logging baseline; full sink review pending.          | 5; privacy/security.         | BOUNDED TECHNICAL EVIDENCE — NOT P22 ACCEPTANCE |
| `PRIV-008` — Research datasets/workspaces SHALL be separated from normal production patient data access.                    | ADR-032 and no production research flow; deployment proof absent. | 3/7; research/data/security. | LIVE NOT VERIFIED                               |
| `PRIV-009` — Institutional aggregate analytics SHOULD avoid exposing identifiable individual mental-health conversations.   | No institutional analytics runtime.                               | 3/5; privacy/institution.    | LIVE NOT VERIFIED                               |

### 3.4 `NFR-RES-001..007`

**Canonical source for every row:** `docs/01_PRODUCT_REQUIREMENTS.md` at the verified baseline.

| ID and exact wording                                                                                                          | Bounded evidence / missing artifact                                       | Domain and reviewer               | Status                                          |
| ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | --------------------------------- | ----------------------------------------------- |
| `NFR-RES-001` — Core intake and safety functions SHOULD remain usable during failure of optional research modules.            | P7 is isolated; integrated outage evidence pending.                       | 6; architecture/SRE/safety.       | BOUNDED TECHNICAL EVIDENCE — NOT P22 ACCEPTANCE |
| `NFR-RES-002` — Mental-health crisis fallback SHALL remain available during generative-model outage.                          | Generic urgent help exists; P14 policy/runtime absent.                    | 6; clinical/product/SRE.          | LIVE NOT VERIFIED FOR P14                       |
| `NFR-RES-003` — Text/touch intake SHALL remain available when voice processing fails.                                         | P7 text/touch exists; voice runtime absent.                               | 6; P12/product/SRE.               | BOUNDED TECHNICAL EVIDENCE — NOT P22 ACCEPTANCE |
| `NFR-RES-004` — Manual entry SHALL remain possible when OCR fails.                                                            | P7 manual intake exists; live OCR absent.                                 | 6; P11/product/SRE.               | BOUNDED TECHNICAL EVIDENCE — NOT P22 ACCEPTANCE |
| `NFR-RES-005` — The product SHALL expose honest failure/degraded states rather than falsely indicating successful assessment. | Typed errors and unavailable states exist; cross-platform review pending. | 2/6; product/accessibility/QA.    | PARTIAL / LIVE NOT VERIFIED                     |
| `NFR-RES-006` — Critical external integrations SHOULD define timeouts and bounded retries.                                    | BFF/AI/outbox bounds exist; future integrations absent.                   | 3/6; integration/SRE.             | PARTIAL / LIVE NOT VERIFIED                     |
| `NFR-RES-007` — Independent kill switches SHOULD exist for sufficiently risky optional integrations/policies.                 | Safe-off flags are not accepted kill switches.                            | 6; SRE/security/clinical/product. | LIVE NOT VERIFIED                               |

### 3.5 `FR-AUDIT-001..007`

**Canonical source for every row:** `docs/01_PRODUCT_REQUIREMENTS.md` at the verified baseline.

| ID and exact wording                                                                                  | Bounded evidence / missing artifact                                    | Domain and reviewer           | Status                                          |
| ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ----------------------------- | ----------------------------------------------- |
| `FR-AUDIT-001` — Safety/policy changes SHALL be auditable.                                            | No live policy change/audit store.                                     | 5; safety/audit governance.   | LIVE NOT VERIFIED                               |
| `FR-AUDIT-002` — Provider/resource changes SHALL be auditable.                                        | Provider/resource runtime absent.                                      | 5; P13/audit governance.      | LIVE NOT VERIFIED                               |
| `FR-AUDIT-003` — Consent changes SHALL be auditable.                                                  | Transactional consent events exist; viewer/retention/integrity absent. | 5; consent/audit/privacy.     | BOUNDED TECHNICAL EVIDENCE — NOT P22 ACCEPTANCE |
| `FR-AUDIT-004` — Sensitive administrative actions SHALL be auditable.                                 | P21 actions and audit viewer absent.                                   | 5; P21/audit/security.        | LIVE NOT VERIFIED                               |
| `FR-AUDIT-005` — Clinician corrections to AI-extracted clinical information SHOULD be auditable.      | P5 correction history guard; live P10 correction absent.               | 5; clinical/provenance/audit. | LIVE NOT VERIFIED                               |
| `FR-AUDIT-006` — Model promotion/release SHALL be auditable.                                          | No approved P18 model/P19 comparator/promotion.                        | 5/7; model/audit/release.     | LIVE NOT VERIFIED                               |
| `FR-AUDIT-007` — Auditability MUST NOT require indiscriminate storage of raw sensitive conversations. | Privacy/logging rules prohibit raw content; audit store absent.        | 5; privacy/audit/security.    | LIVE NOT VERIFIED                               |

`PRIV-003/004` are not satisfied by proposed retention mechanics. `NFR-SEC-006` is not satisfied by the P11 paper design. `NFR-SEC-003` is not satisfied by a synthetic `mfa_verified` check. No audit viewer exists. Related P7–P21 and P23/P24 gates remain independently owned and unchanged.

## 4. Unsigned scoped decision template

```text
Decision ID: PENDING
Phase/unit/domain: PENDING
Asset/system and environment: PENDING
Exact subject/object/actor/institution/purpose: PENDING
Approved authority versus absent authority: PENDING
Evidence hash, code/build SHA and test run: PENDING
Threat severity rubric, only if independently approved: PENDING
Alternatives and excluded scope: PENDING
Risk owner and residual risk: PENDING
Reviewer name, qualification and independence: PENDING
Decision date, expiry and re-review triggers: PENDING
Rollback, withdrawal and incident actions: PENDING
Signatures: PENDING
```

No field is approved, no person is appointed and no signature is supplied by this document.

## 5. Owner and risk register

| Decision area              | Required accountable roles                                   | Status / principal unresolved risk                          |
| -------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------- |
| Identity/session/privilege | Identity/IAM, institution, security, privacy, operations     | BLOCKED — false or cross-scope authority.                   |
| Browser/API/upload         | AppSec, API/frontend, document security, SRE                 | BLOCKED — injection, abuse or hostile bytes.                |
| Consent/egress             | Privacy/legal/consent, vendor/integration, clinical/source   | BLOCKED — unauthorized processing or disclosure.            |
| Retention/restore          | Records/privacy, data governance, SRE/provider               | BLOCKED — over-retention, failed rights or resurrection.    |
| Audit/telemetry            | Audit/data, privacy/security, domain owners, incident        | BLOCKED — leakage, omission, tamper or unauthorized search. |
| Resilience/switches        | SRE/incident, product, clinical safety, domain owners        | OPEN — unsafe activation or failed fallback.                |
| Supply chain/secrets       | Supply-chain security, CI/release, SRE, artifact owners      | OPEN — compromise or unsigned disposition.                  |
| Threat/pilot/release       | Independent security/privacy, clinical, institution, release | BLOCKED — uncharacterized/unaccepted platform risk.         |

## 6. Final STOP and accountable action

Named qualified clinical/safety, identity/institution, security/AppSec, privacy/legal/records, data-governance, accessibility/product, platform/SRE, incident, research/interoperability/vendor and release owners must review current threat/data-flow evidence and sign exact bounded decisions. They must independently validate any severity rubric, vulnerability disposition, retention/legal basis, provider term, safeguard, incident plan, pilot scope and expiry.

P7 deterministic manual text/touch intake and generic urgent help remain the available patient path. P8-C/P9-C Stage 3 remain BLOCKED; P10/P11 live remain 0/9 approved, with P11 five OPEN/four BLOCKED; P12–P21 runtime remains NOT STARTED where applicable; P13/P14/P15/P16/P17/P18/P19/P20/P21 restrictions remain; P23/P24 remain NOT STARTED.

> **FINAL STOP:** Only a new separately authorized P22-A prompt may conduct a safe non-invasive threat/authorization audit. P22-B/C/D/E implementation, P23/P24, real patient integrations, privileged actions, retention execution, pilot and release remain unauthorized. This dossier grants no security, privacy, legal, clinical, institutional, risk or production approval.
