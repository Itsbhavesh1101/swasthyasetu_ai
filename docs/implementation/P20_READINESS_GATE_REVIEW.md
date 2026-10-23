# P20 Unified Care Orchestration Readiness Review

> **DRAFT — EIGHT DESCRIPTIVE REVIEW DOMAINS; NOT AN OFFICIAL GATE COUNT, CLINICAL APPROVAL OR P20 IMPLEMENTATION AUTHORIZATION**

**Recorded:** 2026-10-24

**Verified baseline:** `main @ ec141d4e6c4d843a6d1868e77751bdd30aa01ce0`

**Runtime truth:** P20 and P20-A/B/C/D are **NOT STARTED**. All live `AC-P20-001..010` and product-level `AC-PROD-001..014` outcomes remain **NOT VERIFIED**.

`OPEN` and `BLOCKED` describe unresolved evidence, not approval arithmetic. Roles below are accountable functions, not fabricated people or signatures. A green documentation PR is not clinical validation, P22 approval, or release authorization.

## 1. P4/P5/P7 context, identity, purpose, longitudinal corrections and provenance — OPEN

- **As-built evidence:** server-side sessions and consent, identity/authorization foundations, P5 PostgreSQL patient/encounter/fact/provenance data, guarded supersession, timeline APIs, and P7 deterministic manual intake exist. Their existing scopes do not establish cross-institution orchestration authority.
- **Accountable roles:** identity/security, consent/privacy/legal, patient-record and provenance owners, institutional data steward, clinical governance, architecture.
- **Missing decisions:** trustworthy subject/encounter binding; actor assignment and institution boundaries; exact orchestration purposes; minimum facts; correction priority; snapshot/effective-time rules; withdrawal; retention; cross-institution access.
- **Future artifact:** approved authorization/purpose matrix, snapshot and provenance contract, correction/supersession policy, data-flow assessment, and institutional access decision.
- **Negative tests:** IDOR; tenant/institution mismatch; wrong purpose; revoked consent midflight; stale fact/version; corrected fact displaced by extraction; mixed-time snapshot; unauthorized side effect.
- **STOP:** no broader P5/P7 retrieval, cross-institution view, or disclosure.
- **Possible synthetic work:** opaque-reference and concurrency contract tests only under a separate prompt; no patient data or new access.

## 2. P9 physical safety, independent P14 mental-health crisis safety, and conflict precedence — BLOCKED

- **As-built evidence:** P9 has immutable contracts and deterministic synthetic fixtures only. P9-C Stage 3 is blocked. P14 is an unapproved policy/readiness draft with no runtime or approved crisis-resource pack.
- **Accountable roles:** physical-safety clinical governance, mental-health clinical governance, emergency/crisis policy owner, accessibility/content/localization, privacy, product, independent clinical validation.
- **Missing decisions:** source-backed policies, populations, validated signals, thresholds, uncertainty, effective/expiry lifecycle, simultaneous physical/mental emergencies, independent escalation, exact route UX and resources.
- **Future artifact:** independently approved/versioned policies, conflict/non-interference specification, clinical validation protocol/results, resource registry, copy pack, rollback and incident plan.
- **Negative tests:** simultaneous signals; contradictory/unknown/missing input; either/both engines unavailable; LLM/model downgrade; expired policy/resource; independent route suppression.
- **STOP:** no real evaluation, triage, “safe” claim, route, or strict cross-channel priority. The simultaneous-emergency behavior is **REQUIRES APPROVAL**.
- **Possible synthetic work:** nonmedical symbolic mechanics may be separately authorized; it cannot establish clinical validity.

## 3. P15 self-care, approved content, exclusions, and RAG knowledge controls — BLOCKED

- **As-built evidence:** P15 specification/readiness documents are drafts; there is no approved remedy, corpus, eligibility/contraindication policy, RAG service, vector index, or live self-care output.
- **Accountable roles:** clinical self-care/Ayurveda governance, medication safety, content/source governance, privacy, security, knowledge/retrieval engineering, accessibility, release.
- **Missing decisions:** permitted population/use, source admission and licensing, exact exclusions, allergy/medication/chronic-condition/age/pregnancy rules, safety dependency, content review/expiry, retrieval boundary and injection defense.
- **Future artifact:** signed policy/content packs, source manifest, eligibility and suppression policy, versioned RAG threat/data-flow review, evaluation and expiry/recall plan.
- **Negative tests:** red flag; unknown safety; missing eligibility; contraindication pack expired; unapproved/injected/stale source; uncited result; LLM/model-memory remedy; consent mismatch.
- **STOP:** no remedy, self-care eligibility, retrieval, or fallback-generated medical content.
- **Possible synthetic work:** engineering-only nonmedical corpus/contract experiments under a later narrow prompt.

## 4. P13 verified providers/resources/referrals and P21 governance — BLOCKED

- **As-built evidence:** provider/resource/referral module paths are placeholders; patient referral UI is unavailable. P13/P21 specifications are review drafts; no verified registry, recipient workflow, admin approval runtime, or external referral exists.
- **Accountable roles:** provider-directory/resource steward, clinical operations, referral governance, consent/privacy/legal, identity/institution security, P21 administration, audit/operations.
- **Missing decisions:** authoritative sources, verification/expiry, permitted filters, recipient identity/authority, minimal payload, withdrawal/in-flight behavior, status truth, auditing, segregation of duties.
- **Future artifact:** approved registry/source contract, verification workflow, referral protocol, exact `REFERRAL_SHARING` purpose/notice, recipient agreement, admin controls and incident plan.
- **Negative tests:** fabricated/expired/unverified provider; empty registry; wrong recipient; general consent substituted; revoked consent; overbroad payload; retry/duplicate disclosure; LLM-generated contact.
- **STOP:** actual referral sharing requires explicit, active, purpose-specific `REFERRAL_SHARING` consent and every additional applicable lawful/governance requirement. General product consent never authorizes it.
- **Possible synthetic work:** obviously synthetic registry mechanics without real contacts or transmission, only if separately authorized.

## 5. P10 clinician correction, P11 documents/OCR, P12 language and continuity — BLOCKED

- **As-built evidence:** P10 source-backed summary contracts and P11 lifecycle/OCR/classification/evidence contracts are synthetic and detached. P10/P11 live gates remain `0/9`; P11 is five OPEN/four BLOCKED. P12 is documentation only. Clinician web is a shell; `/documents` is unavailable.
- **Accountable roles:** clinician workflow and institutional assignment, provenance/data governance, document security/privacy, language/speech quality, accessibility, clinical content, architecture, operations.
- **Missing decisions:** clinician access/assignment; correction authority; source-detail permissions; upload ownership/consent; storage/encryption/retention; OCR/classification quality; unconfirmed-fact confirmation; language quality and recording; accessible fallback.
- **Future artifact:** signed P10/P11 decisions, document threat/privacy design, source-access contract, clinical correction/concurrency policy, P12 validation/consent pack, continuity and fallback tests.
- **Negative tests:** unauthorized clinician/source; broken provenance; malicious or unsupported file; low-confidence extraction promoted; corrected fact overwritten; wrong language; speech outage; inaccessible manual path.
- **STOP:** no live clinician access, file upload/storage/processing, OCR use, speech capture, or fact promotion.
- **Possible synthetic work:** existing detached fixtures only; further work needs a separate bounded prompt.

## 6. P8 extraction, P18/P19 research, external AI, and P16/P17 interoperability — BLOCKED

- **As-built evidence:** P8 extraction is disabled, synthetic, detached, and non-authoritative; Stage 3 is blocked. P18 has no approved dataset/task/baseline; P19 has no comparator. P16/P17 are documentation only, with no exchange. No external clinical-data egress is approved.
- **Accountable roles:** AI/model governance, clinical validation, privacy/legal, security, architecture, research/biostatistics, data custodian/ethics, interoperability/terminology, institutional authorization, release.
- **Missing decisions:** extraction provider/egress and confirmation; research task/data/split/metrics; artifact trust; model lifecycle; FHIR mappings/profiles; ABDM authority; patient/institution match; per-purpose consent.
- **Future artifact:** approved provider/data-flow and confirmation design; research protocol/baseline/model cards; interoperability crosswalk/conformance evidence; consent and external-party agreements.
- **Negative tests:** model authority promotion; urgent-route downgrade; hallucination; provider/model outage; QML exhaustion; untrusted artifact; unauthorized data/export; profile mismatch; withdrawn consent.
- **STOP:** no external AI, prediction, training, inference, FHIR/ABDM exchange, or model-driven clinical action.
- **Possible synthetic work:** isolated nonmedical contract/replay tests only if separately authorized; they do not satisfy live acceptance.

## 7. P20 typed orchestration boundaries, versioned decisions, privacy, security, and resilience — OPEN

- **As-built evidence:** module registrations and typed public ports exist for implemented bounded contexts, but no P20 module, composer, contract, route, persistence, feature flag, or UI exists.
- **Accountable roles:** architecture, domain owners, clinical/safety governance, privacy/legal/consent, application security, platform/operations, observability, incident/release, independent quality.
- **Missing decisions:** precise ownership and ports; immutable snapshot; partial ordering; independent channels; version/effective proof; per-purpose data access; retries/idempotency/concurrency; telemetry minimization; rollback and deletion.
- **Future artifact:** approved typed-contract ADR/spec, threat/privacy assessment, data-flow diagram, version lifecycle, failure/degraded-state contract, observability plan, rollback/runbook, and independent architecture review.
- **Negative tests:** god-service write; direct cross-module ORM access; universal score; hidden approval; wrong purpose; stale snapshot; policy drift; external egress; sensitive logs; unapproved flag; non-deterministic replay.
- **STOP:** no composer, registered capability, data store, endpoint, UI, or activation.
- **Possible synthetic work:** a future P20-A minimal-contract preflight may be considered only after separate authorization and must remain data-free and nonclinical.

## 8. E2E journey, accessibility, clinical/quality validation, and bounded release — BLOCKED

- **As-built evidence:** P7 manual text/touch flow and generic urgent-help navigation exist. The broader P20 journey and product outcomes do not. P22 is not complete; P23/P24 do not authorize blocked patient/clinician features.
- **Accountable roles:** product, patient safety/clinical governance, mental-health governance, privacy/legal, security, accessibility/localization, independent QA/clinical validation, SRE/incident, institutional and release authorities.
- **Missing decisions:** approved journey/copy; unavailable/contradictory states; kiosk/manual continuity; clinical-quality protocol; accessibility evidence; pilot population/environment; monitoring, incident response, stop/rollback and release authorization.
- **Future artifact:** approved journey map, clinical/quality validation report, accessibility audit, end-to-end threat/privacy tests, bounded-release plan, incident exercises, P22 evidence and signed release decision.
- **Negative tests:** all disabled/unavailable combinations; network failure; keyboard/screen-reader/kiosk use; conflicting safety; stale policy/content; privacy leak; rollback; no emergency resource; unauthorized release.
- **STOP:** no patient P20 journey, pilot, production activation, or claim that documentation/CI proves clinical safety.
- **Possible synthetic work:** offline journey-state prototypes only under a separate prompt and with no clinical output.

## Unsigned decision and evidence template

This blank template records no approval. A future record is effective only through an authenticated, authorized, auditable mechanism accepted by accountable governance.

| Field                                                  | Pending record |
| ------------------------------------------------------ | -------------- |
| Decision/evidence ID and bounded policy/task           | **PENDING**    |
| Population, environment, institution and excluded uses | **PENDING**    |
| Source artifact, immutable version/hash and provenance | **PENDING**    |
| Effective date, expiry date and review/recall trigger  | **PENDING**    |
| Clinical and safety review scope                       | **PENDING**    |
| Privacy/legal and exact consent/lawful purposes        | **PENDING**    |
| Security/threat/source/architecture review             | **PENDING**    |
| Product/accessibility/content/localization review      | **PENDING**    |
| Phase/environment approval and explicit prohibitions   | **PENDING**    |
| Related `AC-P20`, `AC-PROD`, requirements and ADRs     | **PENDING**    |
| Positive, negative, adversarial and rollback evidence  | **PENDING**    |
| Monitoring, incident owner, stop and recovery          | **PENDING**    |
| Named reviewer identity/signature and date             | **PENDING**    |

## Risk and accountable-owner register

| Risk                                           | Accountable roles                               | Current disposition | Required evidence / STOP                                         |
| ---------------------------------------------- | ----------------------------------------------- | ------------------- | ---------------------------------------------------------------- |
| Cross-subject, institution, or purpose leakage | Identity, institutional, privacy, security      | OPEN                | Authorization/purpose matrix and IDOR tests; no expanded read    |
| Clinical precedence invented by engineering    | Physical/MH clinical governance, UX             | BLOCKED             | Approved independent-channel policy; no real routing             |
| Self-care shown without complete current gates | Self-care, safety, content/source               | BLOCKED             | Approved safety/eligibility/corpus evidence; hard suppress       |
| Fabricated or stale provider/resource          | Directory/resource steward, clinical operations | BLOCKED             | Verified/expiring registry; no contact output                    |
| AI candidate promoted to truth                 | Clinical, provenance, AI governance             | BLOCKED             | Human confirmation and atomic correction contract; detached only |
| Optional dependency blocks core journey        | Architecture, resilience, accessibility         | OPEN                | P7 fallback and degraded-state E2E evidence                      |
| Sensitive data leaves approved boundary        | Privacy/legal, security, vendor governance      | BLOCKED             | Data-flow/processor/egress approval; no transmission             |
| Research/model gains clinical authority        | Research/model and clinical governance          | BLOCKED             | Approved task/baseline/lifecycle; no inference                   |
| Documentation treated as release approval      | Release, P22, independent quality               | BLOCKED             | Signed bounded release and incident evidence; no activation      |

## Acceptance maps

| Criterion  | Draft evidence only | Required future proof                                   | Status            |
| ---------- | ------------------- | ------------------------------------------------------- | ----------------- |
| AC-P20-001 | Domains 1/8         | Authorized shared-context E2E journey                   | LIVE NOT VERIFIED |
| AC-P20-002 | Domain 7            | Typed composer implementation and boundary tests        | LIVE NOT VERIFIED |
| AC-P20-003 | Domain 2            | Clinician-approved physical policy and precedence tests | LIVE NOT VERIFIED |
| AC-P20-004 | Domain 2            | Approved independent P14 runtime/outage evidence        | LIVE NOT VERIFIED |
| AC-P20-005 | Domains 2/3         | Approved P9/P15 hard-suppression E2E evidence           | LIVE NOT VERIFIED |
| AC-P20-006 | Domain 4            | Verified registry provenance/expiry evidence            | LIVE NOT VERIFIED |
| AC-P20-007 | Domain 6            | ML/QML outage E2E evidence                              | LIVE NOT VERIFIED |
| AC-P20-008 | Domain 5            | OCR-outage/manual-intake E2E evidence                   | LIVE NOT VERIFIED |
| AC-P20-009 | Domain 6            | LLM failure and honest degraded-state evidence          | LIVE NOT VERIFIED |
| AC-P20-010 | Domains 3/6         | Approved-use RAG access/provenance/injection evidence   | LIVE NOT VERIFIED |

| Product criteria | Primary owners | Status                     |
| ---------------- | -------------- | -------------------------- |
| AC-PROD-001      | P4/P5/P7       | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-002      | P11/P5         | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-003      | P9/P15         | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-004      | P12/P14        | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-005      | P14/P13        | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-006      | P15/RAG        | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-007      | P9/P15         | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-008      | P13            | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-009      | P4/P13         | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-010      | P10/P11        | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-011      | P16            | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-012      | P18            | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-013      | P19 after P18  | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-014      | Platform/P22   | PRODUCT-LEVEL NOT VERIFIED |

## Real versus synthetic boundaries and missing predecessors

| Area            | Repository evidence                                    | Missing predecessor / boundary                                  |
| --------------- | ------------------------------------------------------ | --------------------------------------------------------------- |
| P4/P5/P7        | Real bounded first-party foundations and manual intake | No implied permission for new purpose or institution            |
| P8/P9           | Synthetic/detached engineering evidence                | Both patient-facing Stage 3 gates blocked                       |
| P10/P11         | Synthetic contracts/drafts                             | Live `0/9`; P11 five OPEN/four BLOCKED                          |
| P12/P13/P14/P15 | Documentation/placeholders                             | Runtime not started; clinical/content/resource approvals absent |
| P16/P17         | Documentation                                          | Exchange unauthorized                                           |
| P18/P19         | Documentation/placeholders                             | No approved P18 baseline; therefore no P19 comparator           |
| P20/P21         | No runtime                                             | Not started                                                     |
| P22             | Incomplete                                             | No platform release authorization                               |

## STOP matrix

| Proposed step                                         | Mandatory response now                                                        |
| ----------------------------------------------------- | ----------------------------------------------------------------------------- |
| Read new longitudinal data or cross institutions      | STOP pending exact purpose, identity, consent and institutional authorization |
| Compose a real physical or mental-health decision     | STOP pending separately approved policies and conflict UX                     |
| Display self-care or retrieve medical knowledge       | STOP pending P9/P15/RAG clinical/source approval                              |
| Recommend a provider or transmit referral             | STOP pending verified registry and explicit `REFERRAL_SHARING` authority      |
| Process documents, speech, external LLM, FHIR or ABDM | STOP pending each dedicated gate and per-purpose authority                    |
| Use ML/QML in patient care                            | STOP; P18 baseline and P19 comparator do not exist                            |
| Implement P20-A/B/C/D                                 | STOP pending a new bounded phase prompt and applicable review                 |
| Pilot, deploy, or call CI clinical validation         | STOP pending P22 and signed bounded release evidence                          |

## Possible future P20-A preflight — only if separately authorized

A later prompt could permit data-free immutable contract prototypes for module availability, evidence references, action candidates, version/effective-time binding, and deterministic replay. It must not add clinical policy, route precedence, patient data, ORM/schema/migration, API/UI, provider contact, content, model, external call, or runtime registration. Architecture, clinical safety, privacy/security, and source-module owners must approve its exact boundary first.

> **STOP:** this unsigned review inventory authorizes nothing. P20 remains NOT STARTED; no patient journey, clinical decision, data access, integration, pilot, or release may proceed from this document.
