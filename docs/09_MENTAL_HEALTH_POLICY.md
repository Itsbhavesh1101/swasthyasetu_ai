# SwasthyaSetu AI

## 09 — MannSetu Mental-Health Policy Framework

> **DRAFT — PRE-P14 TECHNICAL/CLINICAL-GOVERNANCE READINESS FRAMEWORK ONLY; NO CLINICALLY APPROVED MENTAL-HEALTH POLICY, RISK CLASSIFICATION, CRISIS PROTOCOL, PATIENT-FACING COPY, OR LIVE P14 IMPLEMENTATION.**

**Document ID:** `SSAI-MH-009-PRE-P14-DRAFT`
**Evidence baseline:** `main @ 8a313aabab31bffbbddfa3d94b79aa045cc7a19c`
**Evidence date:** `2026-10-23`
**Approval state:** **UNAPPROVED — HUMAN DECISIONS PENDING**
**Accountable roles:** appointed mental-health clinical governance, clinical safety, privacy/legal,
security, identity, language, accessibility/content, resource/referral, operations, research/ethics,
and institution/product owners — assignment, evidence review, and signatures pending

The word “policy” in this filename identifies a reserved canonical framework location. This document
contains no executable or clinically approved mental-health policy. It is subordinate to approved
clinical/safety policy, the [Project Master Specification](00_PROJECT_MASTER_SPEC.md),
[System Architecture](02_SYSTEM_ARCHITECTURE.md), [Product Requirements](01_PRODUCT_REQUIREMENTS.md),
[Privacy and Consent Specification](26_PRIVACY_CONSENT_SPEC.md), and accepted ADRs. Documentation,
source proposals, code, tests, model output, CI, or PR review cannot grant clinical authority.

# 1. Scope, evidence labels, and source reconciliation

## 1.1 Evidence labels

- **AS-BUILT TECHNICAL EVIDENCE** means repository behavior exists at the baseline, with no claim
  beyond its implemented and tested scope.
- **HISTORICAL SOURCE PROPOSAL** means MannSetu research material suggests a design; it is neither an
  adopted standard nor clinical, legal, privacy, security, or operational approval.
- **FUTURE / NOT IMPLEMENTED** means a separately reviewed phase and accountable decisions are
  required.
- **HUMAN DECISION PENDING** means engineering must not supply the missing policy, content, value,
  source, owner, or approval.
- **LIVE NOT VERIFIED** means the P14 acceptance criterion has no live evidence.

## 1.2 Historical MannSetu source audit

Both local source files were readable through offline PDF text extraction:

- [Competitive Landscape and Digital Mental-Health Front Door Research](source_material/mannsetu/MANNSETU_COMPETITIVE_LANDSCAPE.pdf)
  is an eight-page research brief dated September 2026. It compares product and infrastructure
  concepts and proposes a non-diagnostic front-door model, constrained extraction, deterministic
  clinician-authored routing, Indian care-pathway integration, bilingual evaluation, and validation.
- [Complete Implementation Blueprint](source_material/mannsetu/MANNSETU_IMPLEMENTATION_BLUEPRINT.pdf)
  is a 35-page concept blueprint dated September 2026. It proposes product, architecture, clinical
  safety, screening, multilingual, privacy, referral, audit, evaluation, pilot, and operational
  designs while itself stating that clinical content and deployment require qualified review.

These PDFs are historical proposals, not adopted clinical standards. Their cited public claims,
product capabilities, laws, instruments, thresholds, resource details, availability, and links may
change and were not externally revalidated in this work unit. Proposed populations, route matrices,
retention values, instruments, crisis details, metrics, technologies, and rollout gates are not
carried into this framework as decisions. No copyrighted questionnaire or long source passage is
reproduced.

## 1.3 As-built versus future inventory

| Area | Exact baseline evidence | Boundary |
| --- | --- | --- |
| P7 intake | Deterministic, non-diagnostic text/touch intake with server authority and original-language metadata. | Not mental-health assessment, crisis classification, or P14 consent. |
| Urgent help | Patient shell and intake expose a persistent generic urgent-help link; `/urgent-help` states verified contacts are not configured. | No verified resource list, assessment, dispatch, or promise of response. |
| P8 | Provider-neutral AI gateway and strictly bounded engineering-only extraction subset; P8-C Stage 3 blocked. | LLM/provider output has no P14 route, clinical, or resource authority. |
| P9 | Physical-safety contracts, synthetic deterministic fixture, and detached test-only presentation. | Spec 08 is unapproved physical-safety architecture, not mental-health policy or P14 permission. |
| P13 | Provider/resource/referral specifications and proposed readiness gates only; runtime not started. | No verified registry, real referral, external sharing, or status truth. |
| P4/P6 | Pseudonymous sessions, central consent primitives, secure transient cookies, and patient shell. | Existing general intake consent is not transitive to P14. |
| P12 | Draft multilingual/speech specification and readiness inventory. | No approved speech, translation, Hindi/Hinglish safety lexicon, or P12 runtime. |
| P14 | Empty `mental_health` module, policy, and test-case placeholder directories. | No registration, API/BFF/UI, state, ORM, model, lexicon, provider, policy, or clinical test corpus. |

Alembic head is `p7a_0007`. `app.main` does not register a mental-health module. Canonical future
domain/API/schema concepts are designs, not implemented acceptance evidence.

# 2. Ownership and trust boundaries

The future `mental_health` bounded context would own P14 workflow state, typed mental-health signal
contracts, deterministic decision contracts, policy resolution, and P14-specific application rules.
It must remain distinct from:

- `clinical_intake`, which owns P7 structured non-diagnostic intake;
- `safety`, whose present subset demonstrates synthetic physical-safety mechanics only;
- `ai_orchestration`, which owns operational provider boundaries, never clinical routes;
- `resources` and `referrals`, which would own verified resource truth and external handoff state;
- `consent`, which owns purpose-specific consent records and authoritative checks; and
- P12 language services, which may transform media/text only after approval and never confer meaning
  or safety authority.

P4 pseudonymous sessions and server-side session/actor/consent checks remain authoritative. P7
manual text/touch and generic urgent-help navigation remain independent fallbacks. Client state,
headers, language selection, model confidence, a feature flag, or an opaque ID cannot establish
identity, age/guardian authority, consent, clinical eligibility, resource truth, or route authority.

Appointed clinical and mental-health reviewers must own clinical source suitability, signal meaning,
rules, ambiguity, wording, validation, and changes. Privacy/legal reviewers own purpose, lawful and
governance requirements, consent, population, egress, retention, and rights. Language reviewers own
meaning-preserving multilingual evidence; accessibility/content reviewers own usable approved copy;
security/identity reviewers own trust and abuse boundaries; operations and institution owners own
response expectations, incidents, pilot scope, and release. This framework implies no therapist
relationship, diagnosis, monitoring, dispatch, or continuously staffed human response.

# 3. Future signal and decision contracts — design only

```text
pseudonymous message
    -> independent language-aware safety backstop
    -> bounded structured mental-health signal extraction
    -> strict schema, provenance, uncertainty, and contradiction validation
    -> clinician-approved deterministic mental-health policy, only if later authorized
    -> ROUTE_A | ROUTE_B | ROUTE_C | CLARIFICATION_REQUIRED | DEGRADED_SAFE_FALLBACK
```

The five identifiers are canonical route-state vocabulary from the domain model, not assigned
outcomes or approved clinical semantics. This document defines no signal-to-route mapping.

Future contracts must be immutable, strictly typed, bounded, versioned, reject unknown fields, and
carry opaque workflow identity, session/encounter scope where approved, original-language evidence
references, language metadata, explicit missing/unknown/uncertain/contradictory state, bounded reason
codes, schema version, policy ID/revision, source/reviewer approval references, and timezone-aware UTC
decision time. A raw score, prose response, provider confidence, translation, or model classification
cannot be a route.

Policy resolution must fail closed when policy content or approval evidence is missing, invalid,
expired, suspended, incompatible, or outside its population, language, jurisdiction, or environment.
The system must reject malformed inputs rather than coerce them. `FR-MH-008` reserves precedence for
approved future high-risk criteria; it does not authorize this document or an LLM to define them.

# 4. Independent backstop, ambiguity, and failures

This section specifies mechanics, not clinical rules. A future backstop must execute independently of
the LLM/provider path and use only source-verifiable, versioned, language-specific artifacts approved
by accountable reviewers. No actual lexical hit list, pattern, threshold, classification, or fallback
route is supplied here.

Future review and tests must address current versus historical discussion, negation, quotation,
third-party speech, hypothetical text, incomplete context, Hindi, English, Hinglish, code switching,
transliteration, misspelling, idiom, ambiguity, silence, contradictions, and attempts to instruct the
system to ignore policy or call tools. A match is not a diagnosis. Ambiguity must produce governed
clarification or a safer approved behavior rather than a guessed route.

Malformed/extra/oversize JSON, incompatible schema, missing provenance, low or non-finite confidence,
provider refusal, timeout, cancellation, outage, contradictory backstop/extractor state, and stale
policy must never fabricate a signal, silently lower concern, enable self-care, or remove independent
help navigation. The generic urgent-help page remains reachable during LLM, database, provider, or
normal conversation failure. Verified crisis contacts and approved emergency copy are not configured,
and the application must never imply live emergency monitoring or response.

# 5. Future patient workflow and copy governance

Any later patient workflow requires approved disclosure that it is AI-assisted and is not therapy,
diagnosis, emergency response, or a substitute for professional care. An accessible urgent-help action
must remain predictable and persistent. Users require privacy-respecting opt-out/stop behavior and an
honest distinction among clarification, uncertainty, unavailable policy, unavailable resources, and
technical failure. A future clinically governed crisis interaction must minimize unnecessary
conversation and use only approved, source-backed human-support navigation.

Age, minor, guardian, caregiver, assisted-use, kiosk, capacity, session recovery, and anonymous-to-
identified transitions are **HUMAN DECISIONS PENDING**. No chatbot auto-start, coercive disclosure,
hidden escalation, or promise that a person was notified is authorized. All mental-health, crisis,
questionnaire, helpline, route, and triage wording remains pending accountable clinical, content,
language, accessibility, privacy, and institution review. Static state labels in engineering design
must not become patient crisis guidance.

# 6. PHQ-9/GAD-7 and other screening instruments — decision gate only

The historical blueprint discusses PHQ-9, GAD-7, other named screening instruments, and structured
screening concepts. They are candidates only. Before any use, accountable clinical/legal/content owners must decide and
record licensing and attribution, exact authorized wording/version, intended population and age,
language/cultural validation, administration fidelity, accessibility, scoring interpretation,
limitations, crisis interaction, psychometric evidence, storage, and revalidation.

This framework reproduces no questionnaire, score, cutoff, interpretation, risk class, or route rule.
A screening result is not a diagnosis and cannot independently choose or downgrade a route. An LLM
must not score, paraphrase, or substitute for an approved instrument. The appointed clinical assessor
owns whether and how any instrument may contribute to a later approved deterministic policy.

# 7. Privacy, consent, security, and retention

Current `GENERAL_PRODUCT_USE` consent with `clinical_intake` scope authorizes only the implemented
onboarding/intake boundary. It is not transitive to P14 conversation, processing, persistence,
external AI, mental-health records, crisis escalation, referral, analytics, support access, or
research. Future purpose-specific notice, consent and any additional lawful/governance basis require
accountable decisions and server-side enforcement.

Open decisions include population and purpose; pseudonymity limits; minor/guardian/caregiver and
assisted use; re-identification and session recovery; processor/provider, region, egress, training and
retention; research separation and de-identification; support/admin access; subject rights; withdrawal,
deletion, in-flight work, legal hold, backups, audit and incident response. No region, basis, provider,
retention date, deletion guarantee, or production population is selected here.

Raw narratives/transcripts, extracted sensitive content, credentials, session bearers, consent bodies,
resource contacts, or patient examples must not enter generic logs, metrics, traces, analytics,
support tools, URLs/query strings, browser persistent storage, service-worker caches, CI artifacts, or
unapproved exports. Future APIs/BFFs require strict `no-store`, bounded payloads, safe errors,
authorization, object/session isolation, replay/idempotency controls, and no automatic retry of an
ambiguous side effect. No real patient data may be sent externally until all applicable privacy,
security, clinical, institutional, processor, region, consent, and release decisions are approved.

# 8. Verified crisis resources and P13 referrals

No number, URL, facility, counselor, availability claim, or geographic coverage is approved or
reproduced here. Future resource selection may use only an approved, currently verified registry or
an approved human-maintained bundled fallback with source, owner, jurisdiction, version, verification
time, expiry, suspension/revocation, correction, and incident controls. Generic urgent-help navigation
is not a verified contact list. Absent, stale, expired, disputed, suspended, or revoked evidence must
fail safely and must not be replaced by model memory.

Future professional-support handoff depends on P13, which is not implemented. Any external sharing
requires explicit, active, purpose-specific `REFERRAL_SHARING` consent plus every additionally
applicable legal/governance requirement. General product, intake, or P14 engagement cannot authorize
sharing. Consent must be bound to the approved recipient, purpose, and minimized payload and rechecked
before the side effect. Raw transcript is excluded by default. No `SENT`, `ACKNOWLEDGED`, `SCHEDULED`,
or `COMPLETED` status may be inferred without owning-service or validated external evidence.

# 9. Future policy lifecycle, evidence, and negative tests

A future policy artifact would require an immutable ID/revision, exact source manifest, approved
population/language/jurisdiction/environment, qualified authors and independent reviewers, approval
evidence, effective/expiry interval, schema/reason-code compatibility, activation/suspension/
retirement state, supersession history, monitoring and incident owner, rollback target, revalidation
trigger, and immutable linkage from each decision. Final vocabulary and authority remain human
decisions. Feedback and corrections preserve history rather than rewriting prior decisions.

Required future adversarial evidence includes:

- current versus historical, negated, quoted, third-party, hypothetical, ambiguous, incomplete, or
  silent statements;
- English/Hindi/Hinglish code-switch, transliteration, idiom, spelling, locale mismatch, and missing
  approved language artifact;
- disagreement among backstop, extractor, questionnaire candidate, and model advisory without model
  override;
- malformed/extra/oversize JSON, invalid confidence/time/version/provenance, prompt injection, fake
  tool instructions, provider timeout/refusal/outage, and stale or unavailable policy;
- false reassurance, self-care leakage, unsupported diagnosis/medication language, and prolonged
  conversation after an approved future crisis state;
- absent/stale/expired/revoked resource, malicious URL, P13 outage, ambiguous external effect,
  duplicate referral, and absent/expired/revoked sharing consent;
- minor/guardian/assisted-use mismatch, session fixation/replay, cross-session/cross-subject IDOR,
  concurrent withdrawal/evaluation/send, and impersonated reviewer/source;
- keyboard, focus, screen-reader, forced-colors, 320/390px reflow, approved-language parity,
  opt-out, no-store/browser-residue, and nonleaking telemetry/CI artifacts.

These are proposed test classes, not executed P14 clinical evidence. A future clinical validation
corpus and harmful-error taxonomy require qualified review, source/licensing approval, representative
coverage, predeclared acceptance criteria, false-negative analysis, correction handling, and signed
release decisions.

# 10. Requirements and acceptance traceability

Every live P14 criterion is **NOT VERIFIED**.

## 10.1 `FR-MH-001..020`

| ID and exact canonical requirement | Framework location and missing evidence | Live status |
| --- | --- | --- |
| `FR-MH-001` — The product SHALL expose a mental-health first-contact workflow. | §§2,5; no P14 workflow exists. | NOT VERIFIED |
| `FR-MH-002` — The mental-health first-contact workflow SHALL support pseudonymous use. | §§2,7; P4 sessions exist, P14 binding absent. | NOT VERIFIED |
| `FR-MH-003` — The workflow SHALL explain that it is AI-assisted, not therapy, not diagnosis, and not an emergency service. | §5; actual copy and workflow unapproved/absent. | NOT VERIFIED |
| `FR-MH-004` — An urgent-help action SHALL remain visible before and during applicable mental-health conversations. | §§1,4–5; generic control exists, P14 conversation absent. | NOT VERIFIED FOR P14 |
| `FR-MH-005` — The LLM SHALL output typed mental-health signals rather than a free-form clinical judgement. | §3; P8 contracts do not define P14 signals. | NOT VERIFIED |
| `FR-MH-006` — Final mental-health route selection SHALL be determined by policy independent of LLM prose. | §§3–4; no approved P14 policy/evaluator. | NOT VERIFIED |
| `FR-MH-007` — The system SHALL use a language-aware safety backstop independent of the LLM. | §4; no lexicon/artifact/backstop exists. | NOT VERIFIED |
| `FR-MH-008` — Explicit current high-risk self-harm/suicide indicators SHALL dominate lower-risk scores and protective factors according to approved policy. | §§3,6,9; criteria/precedence require clinical approval. | NOT VERIFIED |
| `FR-MH-009` — Ambiguous safety-relevant language SHALL trigger focused clarification or safer routing. | §§3–4,9; approved ambiguity behavior absent. | NOT VERIFIED |
| `FR-MH-010` — The system SHALL support low-risk self-help/psychoeducation with optional professional support. | Route vocabulary only; eligibility/content not approved. | NOT VERIFIED |
| `FR-MH-011` — The system SHALL support professional/counsellor referral for non-imminent but meaningful concern. | §8; P13 and clinical criteria absent. | NOT VERIFIED |
| `FR-MH-012` — The system SHALL support urgent/crisis human-support routing. | §§4–5,8; policy/resources/copy absent. | NOT VERIFIED |
| `FR-MH-013` — A high-risk lexical hit during LLM failure SHALL trigger a configured safe fallback. | §4; no approved lexical criteria or fallback outcome. | NOT VERIFIED |
| `FR-MH-014` — The mental-health chatbot MUST NOT tell the user they definitively have a mental-health disorder. | §§2,5–6; chatbot absent; prohibition preserved. | NOT VERIFIED FOR LIVE P14 |
| `FR-MH-015` — The mental-health chatbot MUST NOT prescribe or change medication. | §§2,5; chatbot absent; prohibition preserved. | NOT VERIFIED FOR LIVE P14 |
| `FR-MH-016` — When crisis routing is active, the product SHOULD minimize unnecessary prolonged chatbot interaction. | §5; crisis interaction/copy not approved. | NOT VERIFIED |
| `FR-MH-017` — Crisis resources SHALL come from a verified resource registry or bundled fallback. | §8; neither approved registry nor bundle exists. | NOT VERIFIED |
| `FR-MH-018` — Expired/stale crisis resources SHALL be prevented from normal display where possible and SHOULD trigger operational alerts. | §§8–9; resource lifecycle/alerts absent. | NOT VERIFIED |
| `FR-MH-019` — Professional-support referrals SHALL be trackable beyond “message sent”. | §8; P13 state/runtime absent. | NOT VERIFIED |
| `FR-MH-020` — Release of mental-health routing changes SHALL require safety regression evaluation. | §9; approved corpus/protocol/release authority absent. | NOT VERIFIED |

## 10.2 Global safety, privacy, accessibility, and dependencies

The global safety requirements remain binding and are not replaced by this P14 framework:

| Requirement | P14 application | Status |
| --- | --- | --- |
| `SAFE-001` | No autonomous diagnosis. | BINDING; LIVE P14 NOT VERIFIED |
| `SAFE-002` | No autonomous prescribing. | BINDING; LIVE P14 NOT VERIFIED |
| `SAFE-003` | Deterministic safety policy outranks model output. | BINDING; P14 POLICY ABSENT |
| `SAFE-004` | Human clinical authority remains final. | BINDING; WORKFLOW ABSENT |
| `SAFE-005` | Uncertainty must be explicit and handled safely. | BINDING; P14 RULES ABSENT |
| `SAFE-006` | Timeout, outage, and malformed-output behavior must remain safe. | BINDING; P14 FALLBACK ABSENT |
| `SAFE-007` | The system must not invent emergency or referral resources. | BINDING; VERIFIED REGISTRY ABSENT |
| `SAFE-008` | The system must not invent remedies or clinical claims. | BINDING; LIVE P14 CONTENT ABSENT |
| `SAFE-009` | Self-care is allowed only after approved safety gating. | BINDING; P14 GATE ABSENT |
| `SAFE-010` | Decisions must be reproducible against explicit policy/version evidence. | BINDING; P14 VERSIONED POLICY ABSENT |

`FR-SAFE-001..012` describe physical-safety requirements
and do not become P14 policy. Relevant privacy requirements demand minimization, documented purpose,
explicit retention, withdrawal/deletion, minimized referral sharing, pseudonymous first contact,
content-free logs, research separation, and safe aggregate analytics. P7 accessibility/browser
privacy remains the minimum UI baseline. P12 language behavior, P13 resources/referrals, P21 review,
and all P8/P9/P10/P11 gates retain their own authority.

## 10.3 `AC-P14-001..013`

| Criterion (exact canonical wording) | Required future evidence | Live status |
| --- | --- | --- |
| `AC-P14-001` — Pseudonymous mental-health first-contact path works. | Real P14 session/workflow tests. | LIVE NOT VERIFIED |
| `AC-P14-002` — AI-assisted/non-therapy/non-diagnostic disclosure is present. | Approved copy and accessible UI evidence. | LIVE NOT VERIFIED |
| `AC-P14-003` — Urgent-help action remains accessible. | P14 keyboard/screen-reader/reflow/outage tests. | LIVE NOT VERIFIED |
| `AC-P14-004` — Mental-health extractor emits typed signals, not authoritative route. | Approved strict schema, provenance and non-authority tests. | LIVE NOT VERIFIED |
| `AC-P14-005` — Independent language-aware safety backstop exists. | Approved artifact plus outage/language/adversarial tests. | LIVE NOT VERIFIED |
| `AC-P14-006` — Deterministic policy owns A/B/C route. | Clinically approved policy/evaluator/version evidence. | LIVE NOT VERIFIED |
| `AC-P14-007` — Explicit high-risk rule cannot be overridden by lower model/questionnaire score. | Approved criteria and hard-override regression corpus. | LIVE NOT VERIFIED |
| `AC-P14-008` — Ambiguous high-risk language triggers clarification or safer governed behavior. | Approved ambiguity rules and multilingual cases. | LIVE NOT VERIFIED |
| `AC-P14-009` — LLM timeout/invalid JSON still leaves crisis fallback available. | Independent fallback and degraded-mode integration tests. | LIVE NOT VERIFIED |
| `AC-P14-010` — Crisis resources come only from verified registry/bundled fallback. | Source, freshness, protected-mode and outage evidence. | LIVE NOT VERIFIED |
| `AC-P14-011` — Route-B referral uses P13 consent/referral flow. | Implemented P13 plus consent/minimization/idempotency tests. | LIVE NOT VERIFIED |
| `AC-P14-012` — Safety regression corpus includes negation, historical mention, quotes, Hinglish, ambiguity, and prompt-injection cases. | Clinically reviewed/licensed corpus and results. | LIVE NOT VERIFIED |
| `AC-P14-013` — If final approved policy is unavailable, real production triage remains explicitly blocked. | Protected-environment safe-off and release-control evidence. | LIVE NOT VERIFIED; BLOCKING RULE PRESERVED |

# 11. Conditional phase outline and final STOP rule

This is not a new accepted implementation plan. A separately reviewed prompt might later authorize
documentation or nonmedical synthetic contracts, detached deterministic failure mechanics, or static
unavailable states. Later work would still require distinct approval for clinically governed policy,
patient UI, verified resource registry, and P13 referral integration. Nothing in this PR authorizes
P14-A/B/C/D/E/F or live collection/processing.

**STOP** before implementation or activation while any applicable item is absent: approved clinical
sources, signals, rules, precedence, instruments, reason codes and wording; qualified reviewer
authority; supported population, age, language, jurisdiction, and exclusions; real verified resources;
P13 referral capability and exact sharing consent; P14 privacy/notice/retention/deletion/egress and
identity decisions; security/threat review; validated clinical corpus and predeclared acceptance;
operations, incident, rollback and monitoring; or scoped pilot/production release. Missing policy must
produce no real route—not a guessed default, model-selected outcome, or invented resource.
