# Pre-P20 — Unified Care Decision Composition and Journey Specification

> **DRAFT — ACCOUNTABLE CLINICAL/SAFETY/PRIVACY/PRODUCT/ARCHITECTURE REVIEW ONLY; NO ACTIVATED CARE ORCHESTRATOR OR P20 PATIENT JOURNEY**

**Recorded:** 2026-10-24

**Verified baseline:** `main @ ec141d4e6c4d843a6d1868e77751bdd30aa01ce0`

**Reviewers required:** clinical governance, physical-safety governance, mental-health safety, privacy/legal, consent, security, architecture, product, accessibility, institutional authorization, data governance, operations/release, and independent quality roles. No approval or signature is recorded here.

## Source precedence

Accepted ADRs and the canonical specifications control this draft. Product requirements and phase acceptance criteria define outcomes; implementation/readiness records define repository truth. Where a clinical, policy, content, identity, consent, or release decision is absent, it is **REQUIRES APPROVAL**. This draft does not supersede ADR-001/002/003/005/008/013/022/023/027/028/032/033/034/038/039/040.

## A. Current product truth and scope

P20 is **NOT STARTED**. Its future objective is a coordinated journey over independently owned and approved capabilities; it is not a shortcut around any upstream gate.

- P4 sessions, consent, identity/authorization foundations; P5 longitudinal facts/provenance; and P7 deterministic manual text/touch intake are implemented within their existing boundaries.
- P8-C patient-facing AI extraction and P9-C patient-facing safety Stage 3 are **BLOCKED**. P9 policy fixtures are synthetic engineering data and may not classify real patients.
- P10 and P11 live use remain `0/9` approved; P11 records five OPEN and four BLOCKED gates.
- P12–P19, P20, and P21 runtime are **NOT STARTED**. P15 has no approved self-care policy or corpus. P16/P17 exchange is unauthorized. P18 has no approved task, dataset, or baseline, so P19 has no comparator. P22 is not complete.
- Patient `/documents`, `/results`, and `/referrals` pages remain unavailable. No live clinician workflow, provider registry, referral transmission, medical RAG, speech, OCR, FHIR/ABDM exchange, or patient risk model is deployed.

Conceptual integration below is neither runtime wiring nor a live safety system. P20-A typed composition, P20-B patient integration, P20-C selective longitudinal/retrieval use, and P20-D cross-module E2E remain separately gated and **NOT STARTED**.

## B. Domain separation and conceptual typed envelopes — design only

These are non-executable review terms, not code, endpoints, database entities, or new clinical authority.

### CareCompositionRequest

A future request would bind opaque subject, session, and encounter references; authenticated actor and institution; exact consent purpose and scope; authorization proof; a versioned longitudinal snapshot; request/evaluation time; requested module capabilities; and correlation/idempotency metadata. It must not contain arbitrary raw narratives or imply that omitted fields are negative, complete, or eligible.

### ModuleEvidence and ModuleAvailability

Each source-owned evidence item would carry its opaque reference, source module/type, source trust and verification state, source/effective/observed time, snapshot/version, reason/provenance references, uncertainty, and relevant policy/model/content/registry version plus proof that the version was effective for that evaluation. Availability is explicit: `NOT_EVALUATED`, `UNKNOWN`, `STALE`, `UNAVAILABLE`, `BLOCKED`, or `PENDING_HUMAN_REVIEW`; none means “negative” or “safe.”

### CareActionCandidate and CareActionDecision

A candidate would name a future action vocabulary item, originating module, evidence/reason references, governing version, uncertainty and time bounds, required consent/authorization, and disclosure restrictions. A decision would preserve every independent candidate and suppression reason; bind the complete evaluated snapshot; record deterministic composition version and current authorization; and authorize only the minimum downstream disclosure. It must never manufacture missing evidence or approval.

The master-plan candidate vocabulary is `URGENT_HELP`, `PRIORITY_CLINICIAN`, `ROUTINE_CLINICIAN`, `SELF_CARE`, `MENTAL_HEALTH_REFERRAL`, `DOCUMENT_REVIEW`, and `CLARIFICATION`. These are future labels pending clinical and UX authorization—not approved actions, routes, copy, or endpoints.

The source module owns its facts, corrections, lifecycle, and policy result. A future composer may consume typed public ports, immutable read models, or governed events; it may not perform arbitrary cross-module ORM writes, fork a hidden clinical history, create approvals, mutate source state, or collapse channels into a universal health score.

## C. Decision precedence and non-interference

Only this partial ordering is supported by accepted policy:

1. Deterministic physical hard-safety restrictions dominate optional recommendations.
2. Mental-health crisis handling remains deterministic and independent of LLM prose.
3. Independent high-priority physical and mental-health channels cannot suppress one another.
4. Unknown, contradictory, unavailable, stale, or unevaluated safety input never becomes low risk.
5. Self-care is suppressed by any red flag/exclusion and requires separately reviewed, current safety, eligibility, content, and consent decisions.
6. ML, QML, LLM, and risk outputs cannot downgrade hard safety, promote a diagnosis or confirmed fact, invent a provider/contact/remedy, or delay an urgent route.
7. AI-extracted candidates cannot silently become clinician-confirmed facts.

A strict priority or combined response for simultaneous physical and mental-health emergencies is **REQUIRES APPROVAL** from qualified clinical/safety and UX owners. Thresholds, scripts, intervention wording, and escalation content are likewise **REQUIRES APPROVAL**.

## D. Longitudinal context, corrections, provenance, concurrency and privacy

Only a purpose-authorized, minimum-necessary P5/P7 snapshot may be considered. Every input must bind subject and encounter, tenant/institution authorization, provenance, trust/verification state, correction/supersession lineage, source and effective time, and snapshot version. Verified human corrections supersede lower-trust extracted candidates according to source-owned rules.

Composition must fail closed on subject/tenant/institution mismatch, authorization drift, revoked or wrong-purpose consent, stale evidence, changed policy/content/registry versions, or optimistic-concurrency conflict. Results from distinct effective times may not be silently combined as current eligibility. Read authorization must be checked before retrieval and again before any future side effect or disclosure.

No raw clinical narrative, patient data, prompts, personal identifiers, embeddings, FHIR payloads, document binaries, or consent artifacts belong in generic telemetry, browser persistence, CI fixtures, caches without approved isolation, or unapproved transport. The existing general-product/clinical-intake consent does not authorize speech, OCR, RAG, external LLM, research, referral sharing, clinician/institution access, FHIR/ABDM, or any other purpose. Physical-safety and care use requires separately approved data and consent scope.

## E. Future source-of-authority matrix

| Future input                                             | Owner and as-built truth                                                                                                        | Authorized output / trust                                                                                  | Preconditions, expiry, and uncertainty                                                                                                                                   | Safe failure / required future approval                                                        |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| P4/P5/P7 identity, consent, intake, longitudinal context | Sessions/identity/consent, patients/encounters/provenance, and clinical-intake owners; bounded APIs and P7 manual journey exist | Current authoritative first-party records only within existing scopes; explicit source/verification states | Current session/actor/institution, exact purpose, ownership, snapshot and source versions; corrections respected                                                         | Deny mismatch/staleness; approve any new cross-module read/disclosure and institutional policy |
| P8 AI extraction                                         | AI orchestration/intake extraction; detached synthetic Stage 2 only                                                             | Unconfirmed, non-authoritative candidate                                                                   | P8-C Stage 3 clinical, role, consent, egress, retention, confirmation and production gates                                                                               | Keep manual P7; live use remains BLOCKED                                                       |
| P9 physical safety                                       | Safety module; deterministic synthetic fixtures only                                                                            | No real-patient route or “safe” claim                                                                      | Clinician-approved policy, signals, population, version/effective proof, UX and lifecycle                                                                                | No recommendation when unavailable; real activation remains BLOCKED                            |
| P14 mental-health safety                                 | Policy draft; no runtime                                                                                                        | Future independent deterministic crisis route, not LLM authority                                           | Qualified policy, approved resources, language/UX, population, expiry and clinical validation                                                                            | Generic urgent-help path only; no invented clinical rule or resource                           |
| P15 self-care                                            | Draft; no approved policy, corpus, eligibility engine or RAG                                                                    | None live; future supportive content only                                                                  | Current safety + eligibility + approved content/source/version + exclusions + consent                                                                                    | Hard suppress; all clinical/source decisions remain pending                                    |
| P13 providers/resources/referrals                        | Drafts and placeholders; no verified registry or referral runtime                                                               | Future verified registry facts and minimal referral                                                        | Verification/expiry, purpose, recipient authority; explicit active purpose-specific `REFERRAL_SHARING` consent plus every other applicable lawful/governance requirement | No fabricated contact/link; no external disclosure until approved                              |
| P10 clinician summary/review                             | Synthetic immutable summary contracts only; live `0/9`                                                                          | No clinician-confirmed fact or live access                                                                 | Trusted assignment/institution, source access, correction authority, concurrency, audit and retention                                                                    | No clinician action; all live gates remain unapproved                                          |
| P11 OCR/document evidence                                | Synthetic lifecycle/OCR/classification/candidate contracts; live `0/9`, five OPEN/four BLOCKED                                  | Detached unconfirmed evidence only in tests                                                                | Ownership/consent, secure upload/storage, source access, provenance, human review                                                                                        | Manual intake; no upload, processing, UI, persistence, or patient data                         |
| P12 speech/language                                      | Draft only                                                                                                                      | None live                                                                                                  | Language quality, consent, recording/retention, provider, accessibility and clinical review                                                                              | Preserve text/touch/manual path                                                                |
| P16 FHIR / P17 ABDM                                      | Documentation only                                                                                                              | No import/export/exchange                                                                                  | Exact purpose, patient/institution match, profiles, conformance, consent, authorization and external terms                                                               | No exchange; unauthorized                                                                      |
| P18 classical ML / P19 QML                               | Research drafts/placeholders; no P18 baseline and no P19 comparator                                                             | No patient prediction or clinical authority                                                                | Approved task/data/split/metrics/baseline/model governance; trusted artifacts; isolated runtime                                                                          | Ignore/unavailable; never block intake or lower safety                                         |
| P21 administration/governance                            | Spec draft/placeholders; runtime not started                                                                                    | No approval, registry, or policy administration                                                            | Authenticated accountable workflows, segregation of duties, audit and release controls                                                                                   | No activation or hidden approval                                                               |
| P22 release/security                                     | Not complete                                                                                                                    | No release authorization                                                                                   | Security/privacy/clinical validation, incident and bounded-release evidence                                                                                              | Remain safe-off                                                                                |
| RAG                                                      | No live service                                                                                                                 | Only a future scoped P11 private-document or P15 approved-knowledge retrieval result                       | Versioned approved use, corpus/source rights, access control, provenance, injection defense, freshness and exact purpose                                                 | No retrieval or generic medical advice; manual path remains                                    |

## F. Fail-closed composition and degraded-state design

Failure or uncertainty in safety, consent, authorization, provenance, or effective-version proof means no clinical recommendation and no “safe” claim. Optional OCR, LLM, ML, QML, RAG, or provider lookup failure preserves P7 manual/text/touch intake and a non-clinical generic urgent-help fallback, but never creates clinical content.

The UI must distinguish `NOT_EVALUATED` from a negative result, stale from current, unavailable from patient-declined, revoked from never granted, and unverified provider from unavailable provider. If both safety channels are unavailable, neither may be shown as negative. No fallback may fabricate direct links, contacts, remedies, or route copy. Intervention content and clinical route wording require separate qualified approval.

## G. End-to-end future patient journey inventory

This is an unimplemented dependency graph, not a screen list:

`purpose + notice + consent` → `language/accessibility choice` → `authorized identity/context` → `concern + P7 manual intake` → `current approved independent safety evaluations` → `only applicable approved optional evidence` → `reviewed action composition` → `authorized clinician/referral handoff` → `source-owned continuity/corrections`.

Today the chain stops at the existing P7 journey. P8 extraction, P9 real safety, P14 mental-health routing, P15 self-care, P13 registry/referrals, P10 clinician workflows, P11 documents, P12 speech, P16/P17 exchange, and P18/P19 models each require their own gate before a transition. Missing P12 or registry preserves manual navigation. Missing P14/P15 clinical review means no real mental-health risk route or self-care. There is no referral transmission, medical-document processing, clinician confirmation, patient-facing prediction, or FHIR/ABDM export. Every blocked transition is STOP.

## H. Future independent test and threat matrix

Synthetic proof must remain distinct from real clinical validation. A future authorized test plan must cover:

| Area                       | Required positive, negative, regression, and adversarial evidence                                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Independent safety         | simultaneous physical/mental signals; conflicting and unknown safety; one/both channels unavailable; model tries to override urgent route; no channel suppression  |
| Eligibility/context        | missing eligibility; expired contraindication pack; stale/contradictory effective times; clinician correction supersedes extraction; deterministic replay          |
| Consent/access             | wrong-purpose consent; revocation midflight; patient/tenant/institution mismatch; authorization drift; unauthorized referral; minimum disclosure                   |
| Concurrency/provenance     | stale snapshot under concurrent update; broken document provenance; reason/version binding; cache invalidation; rollback safe-off                                  |
| Untrusted/optional systems | hallucinated clinical decision/remedy/provider; provider unverified/expired/empty; OCR/LLM/RAG/model outage; QML exhaustion; injected or stale vector/index source |
| Activation                 | upstream stage unapproved despite enabled flag; untrusted artifact; expired policy/content/registry; no hidden activation                                          |
| Resilience/accessibility   | P7 manual/kiosk/keyboard path on network failure; honest disabled/unavailable states; generic urgent help remains available                                        |
| Privacy/observability      | no raw clinical data, identifiers, prompts, documents, embeddings, or consent artifacts in logs, metrics, traces, browser storage, or CI                           |

No test may invent real clinical thresholds, patient examples, diagnoses, or scripts.

## I. Traceability and future phase slices

### AC-P20 phase acceptance — live not verified

| ID         | Verbatim criterion                                                              | Draft evidence | Missing decision/artifact                                     | Status            |
| ---------- | ------------------------------------------------------------------------------- | -------------- | ------------------------------------------------------------- | ----------------- |
| AC-P20-001 | One coherent patient journey uses shared longitudinal context.                  | §§D/G          | Every upstream module approval and E2E journey evidence       | LIVE NOT VERIFIED |
| AC-P20-002 | Care orchestrator combines typed module outputs without becoming a god service. | §§B/E          | Approved contracts and independent architecture tests         | LIVE NOT VERIFIED |
| AC-P20-003 | Physical safety route dominates lower-priority actions.                         | §C             | Approved real policy and precedence validation                | LIVE NOT VERIFIED |
| AC-P20-004 | Mental-health crisis route remains independent of LLM prose.                    | §C             | Approved P14 policy/runtime and validation                    | LIVE NOT VERIFIED |
| AC-P20-005 | Self-care is blocked when safety/eligibility requires it.                       | §§C/E/F        | Approved P9/P15 policy, content and tests                     | LIVE NOT VERIFIED |
| AC-P20-006 | Provider recommendations come only from verified registry.                      | §E             | Approved P13 registry and expiry controls                     | LIVE NOT VERIFIED |
| AC-P20-007 | ML/QML failure does not block routine intake/navigation.                        | §§E/F          | Approved isolated model adapters and E2E degradation tests    | LIVE NOT VERIFIED |
| AC-P20-008 | OCR failure does not block manual intake.                                       | §§E/F          | Approved P11 integration and manual fallback tests            | LIVE NOT VERIFIED |
| AC-P20-009 | LLM failure produces safe degraded behavior.                                    | §§C/F          | Approved P8 integration and independent failure tests         | LIVE NOT VERIFIED |
| AC-P20-010 | RAG, if introduced, is limited to approved retrieval use cases.                 | §E             | Approved scoped P11/P15 retrieval and access-control evidence | LIVE NOT VERIFIED |

### Product-level acceptance — not P20 acceptance

| ID          | Verbatim eventual product outcome                                                                                                                                             | Upstream owner | Status                     |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | -------------------------- |
| AC-PROD-001 | A patient can begin an encounter, provide symptoms, answer adaptive follow-up questions and generate a structured draft history.                                              | P4/P5/P7       | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-002 | A patient can upload a supported medical document, receive structured extracted data with provenance, and see it incorporated into a timeline after appropriate confirmation. | P11/P5         | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-003 | A configured physical-health red flag prevents self-care and produces the governed urgent route.                                                                              | P9/P15         | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-004 | A pseudonymous Hindi/English/Hinglish mental-health conversation produces structured signals, while deterministic policy determines the route.                                | P12/P14        | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-005 | A crisis-resource path remains available even when the normal LLM path is unavailable.                                                                                        | P14/P13        | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-006 | A low-risk eligible context retrieves approved self-care guidance and displays escalation conditions.                                                                         | P15/RAG        | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-007 | A contraindication or red flag blocks self-care output.                                                                                                                       | P9/P15         | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-008 | The patient receives appropriate verified provider/service options without LLM-fabricated contact details.                                                                    | P13            | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-009 | The user can explicitly consent to a minimal referral and track its status.                                                                                                   | P4/P13         | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-010 | A clinician can review the summary, see source/provenance, and correct/confirm extracted data.                                                                                | P10/P11        | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-011 | Selected structured data can be transformed into validated FHIR-compatible resources.                                                                                         | P16            | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-012 | A benchmark dataset can be preprocessed, trained on classical baselines and evaluated reproducibly.                                                                           | P18            | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-013 | The same task can be evaluated using at least one hybrid QML approach and compared fairly against classical baselines.                                                        | P19            | PRODUCT-LEVEL NOT VERIFIED |
| AC-PROD-014 | A sample new feature module can be added using documented extension contracts without modifying unrelated core modules.                                                       | Platform/P22   | PRODUCT-LEVEL NOT VERIFIED |

### Core requirements — verbatim

| ID          | Verbatim requirement                                                                                                                                                        | Draft mapping      |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| FR-CORE-001 | The product SHALL expose patient, clinician, administrative and research capabilities through a coherent SwasthyaSetu platform.                                             | A/G; eventual only |
| FR-CORE-002 | Applicable modules SHALL use one governed longitudinal patient context rather than independently maintaining conflicting patient histories.                                 | B/D                |
| FR-CORE-003 | Major functional domains SHALL be independently evolvable modules.                                                                                                          | B/E                |
| FR-CORE-004 | Failure or disablement of an optional feature SHALL NOT cause unrelated core workflows to fail.                                                                             | F                  |
| FR-CORE-005 | Cross-module communication SHALL use typed, documented contracts.                                                                                                           | B                  |
| FR-CORE-006 | Externally consumed APIs and event contracts SHALL be versioned.                                                                                                            | B/D                |
| FR-CORE-007 | The product SHALL clearly distinguish:<br>- patient-reported information;<br>- AI-extracted information;<br>- predictive risk output;<br>- clinician-confirmed information. | B/D/E              |
| FR-CORE-008 | AI-extracted clinical facts MUST NOT silently become clinician-confirmed facts.                                                                                             | C/D                |
| FR-CORE-009 | Safety-sensitive and operational behavior that is expected to change over time SHOULD be configurable and versioned rather than hard-coded across the codebase.             | B/C                |
| FR-CORE-010 | Each external dependency SHALL define user-visible degraded behavior.                                                                                                       | F/H                |

### Safety principles — verbatim

| ID       | Verbatim requirement                                                                                                            | Draft mapping |
| -------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| SAFE-001 | The system MUST NOT present an LLM-generated interpretation or predictive score as a confirmed medical diagnosis.               | C/E           |
| SAFE-002 | The system MUST NOT prescribe medication or independently alter an existing prescription.                                       | C/E           |
| SAFE-003 | Deterministic safety rules MUST take priority over self-care suggestions, LLM recommendations and predictive-model output.      | C             |
| SAFE-004 | Clinician-confirmed information and clinical decisions SHALL remain distinct from AI-generated or AI-extracted information.     | B/C/D         |
| SAFE-005 | When safety-critical information is ambiguous, the system MUST clarify or choose the safer governed action rather than guess.   | C/F           |
| SAFE-006 | Failure of an LLM, ML model, QML model, OCR service or other optional AI dependency MUST NOT remove emergency/crisis resources. | F             |
| SAFE-007 | LLMs MUST NOT invent doctor contacts, hospital contacts, counsellor contacts, helpline numbers or other referral resources.     | C/E/F         |
| SAFE-008 | LLMs MUST NOT create unrestricted remedies from model memory for patient-facing use.                                            | C/E/F         |
| SAFE-009 | Self-care content MUST NOT be shown when a configured exclusion or urgent-red-flag condition is active.                         | C/E           |
| SAFE-010 | Safety-sensitive decisions SHALL record sufficient version metadata to make the route reproducible.                             | B/D/H         |

### Impacted requirement families and accepted decisions

The future design must preserve `FR-INTAKE-001..032`, `FR-PAT-001..014`, `FR-ENC-001..006`, `FR-SAFE-001..012`, `FR-MH-001..020`, `FR-SELF-001..017`, `FR-DIR-001..017`, `FR-REF-001..013`, `FR-PROV-001..007`, `FR-DOC-001..023`, `FR-CLIN-001..013`, `FR-RAG-001..007`, `FR-ML-001..017`, `FR-QML-001..018`, `FR-CONSENT-001..009`, `FR-EXT-001..012`, applicable `PRIV-*`, and `NFR-*` without implying they are implemented or verified. Particularly, `FR-REF-002` requires explicit referral consent; general consent cannot authorize sharing.

ADR-001/002 preserve bounded modules and provider ports; ADR-003 makes deterministic safety authoritative; ADR-005/032 isolate research; ADR-008 keeps PostgreSQL transactional authority; ADR-013 prohibits a universal score; ADR-022/023 prohibit invented clinical policy and production truth; ADR-027 preserves core paths during optional-AI failure; ADR-028 rejects raw chat as the clinical record; ADR-033 reserves model approval to SwasthyaSetu governance; ADR-034 bounds RAG; ADR-038/039 isolate dependency profiles and require trusted hashed artifacts; ADR-040 keeps heavy infrastructure phase-activated. No conflict was found; none is modified.

P20-A, P20-B, P20-C, and P20-D are each **NOT STARTED**. Existing P7 evidence proves neither full P20 nor any blocked product outcome.

> **STOP:** no P20 code, policy, UI, data access, or activation may begin without a new bounded prompt, applicable qualified clinical/safety/privacy/security/release approvals, and independently verified upstream prerequisites.
