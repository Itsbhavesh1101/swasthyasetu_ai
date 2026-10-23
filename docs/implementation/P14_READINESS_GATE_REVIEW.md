# P14 MannSetu Mental-Health Readiness-Gate Review

> **DRAFT — PROPOSED, UNAPPROVED P14-SPECIFIC HUMAN-READINESS INVENTORY; NOT AN OFFICIAL APPROVAL PROGRAM OR P14 ACCEPTANCE.**

**Evidence baseline:** `main @ 8a313aabab31bffbbddfa3d94b79aa045cc7a19c`
**Review date:** `2026-10-23`
**Decision:** **NOT READY FOR P14 RUNTIME OR CLINICAL POLICY ACTIVATION**

This inventory accompanies the draft [MannSetu Mental-Health Policy Framework](../09_MENTAL_HEALTH_POLICY.md).
It creates no accepted gate count and does not borrow P11’s official nine-gate model. Every domain
below requires accountable review; labels describe missing evidence, not approval votes.

# 1. Current repository truth

P14 consists only of empty `mental_health` module, policy, and clinical-test placeholders. There is no
registered capability, API/BFF/UI, state machine, ORM/table/migration, approved signal schema,
language safety artifact, deterministic P14 evaluator, clinical policy, resource registry, referral,
provider, model, or clinical corpus. The current patient shell offers generic urgent-help navigation
and truthfully states that verified contacts are not configured. P7 text/touch intake remains
non-diagnostic. P8 extraction and P9 safety subsets are engineering-only/non-authoritative and cannot
be reused as P14 clinical evidence. Alembic remains `p7a_0007`.

The two readable MannSetu PDFs are historical research/design proposals. They do not approve a
population, instrument, cutoff, clinical rule, route, lexicon, crisis resource, retention value,
provider, pilot, or release.

# 2. Proposed review domains

## 2.1 Clinical policy, source, and eligibility — BLOCKED

- **Accountable roles:** appointed mental-health clinical lead and independent reviewers; clinical
  safety; research/ethics; institution/product owner.
- **Repository evidence:** conceptual domain route vocabulary and FR/AC requirements; no approved
  P14 content or artifact.
- **Unresolved decisions/artifacts:** authoritative sources and rights; qualified approvers;
  population, age, jurisdiction, inclusion/exclusion, signal semantics, uncertainty, disallowed
  inference, route rules, precedence, reason codes, effective/expiry dates, revalidation and rollback.
- **Risks/negative tests:** invented criteria, diagnosis, score-based downgrade, out-of-population or
  expired policy, missing approval, stale version, ordinary admin/model activation, harmful false
  reassurance and false-negative review.
- **Possible separately authorized scope:** content-free immutable metadata/contracts using plainly
  nonmedical synthetic symbols only.
- **STOP:** any source, rule, population, authority, validation, or lifecycle decision is missing.

## 2.2 Pseudonymous session, privacy, consent, and retention — BLOCKED

- **Accountable roles:** privacy/legal and consent owner; identity/security; data governance;
  records/retention; institution owner.
- **Repository evidence:** P4 pseudonymous session and central consent primitives; general intake
  consent only.
- **Unresolved decisions/artifacts:** separate P14 purpose/notice/consent and any additional lawful
  requirements; age/minor/guardian/caregiver/assisted use; identity transition/recovery; data fields;
  external processor/region/egress/training; retention/deletion/in-flight/legal hold/backup;
  support/analytics/research access and subject rights.
- **Risks/negative tests:** general-consent substitution, revoked/expired consent, cross-session/IDOR,
  replay/fixation, guardian mismatch, browser/cache/log/analytics/CI leakage, withdrawal race,
  processor-region drift and re-identification.
- **Possible separately authorized scope:** synthetic consent-state and no-store contracts detached
  from conversations or patient data.
- **STOP:** purpose, authority, consent, data flow, processor, retention, rights, or incident decision
  is absent; no real patient data may be processed or sent externally.

## 2.3 Independent backstop and signal extraction — BLOCKED

- **Accountable roles:** clinical safety; mental-health and bilingual language reviewers; P8 owner;
  security; architecture; operations.
- **Repository evidence:** provider-neutral P8 gateway and engineering extraction patterns; no P14
  schema, artifact, prompt, adapter, or backstop.
- **Unresolved decisions/artifacts:** bounded signal schema and evidence semantics; approved language
  artifacts/lexicons; provenance; confidence/ambiguity; strict parsing; deadline/failure behavior;
  backstop isolation, artifact supply chain, testing and monitoring.
- **Risks/negative tests:** current/historical/negated/quoted/third-party text; Hindi/Hinglish/code
  switch; malformed/extra/oversize JSON; timeout/refusal/outage; hallucination; prompt injection;
  contradictory extractor/backstop; missing provenance; model-selected route.
- **Possible separately authorized scope:** nonmedical synthetic schema and detached timeout/parser
  mechanics that cannot represent a patient or route.
- **STOP:** no-LLM safety path, clinical/language approval, strict contract, or fail-closed behavior is
  absent. P8 provider success never creates authority.

## 2.4 Deterministic A/B/C/clarify/degraded policy — BLOCKED

- **Accountable roles:** mental-health clinical governance; clinical safety; policy owner;
  architecture; audit/governance; release owner.
- **Repository evidence:** conceptual route identifiers only; P9 synthetic physical-safety engine is
  not P14 policy.
- **Unresolved decisions/artifacts:** approved mappings, high-risk override criteria and precedence,
  ambiguity/degraded behavior, versioned policy artifact, activation/suspension/rollback, immutable
  decision linkage and independent validation.
- **Risks/negative tests:** lower model/questionnaire score downgrade, missing/expired/tampered policy,
  conflicting equal precedence, non-determinism, unsafe default, feature-flag bypass and stale policy.
- **Possible separately authorized scope:** toy symbolic ordering/fail-closed mechanics in local/test,
  never real signal names or patient-facing routes.
- **STOP:** any policy content or approval is missing; do not invent scoring, thresholds, route rules,
  or fallback clinical disposition.

## 2.5 Urgent-help resources and operational response — BLOCKED

- **Accountable roles:** resource/source governance; clinical safety; privacy/legal; content/language;
  operations/incident response; jurisdiction/institution owner.
- **Repository evidence:** generic urgent-help navigation with no verified contacts; P13 resources not
  implemented.
- **Unresolved decisions/artifacts:** verified sources/rights; jurisdiction/coverage; owner; freshness,
  expiry, correction, suspension/revocation; approved bundled fallback; crisis copy/translations;
  service availability and staffing expectations; outage/incident/alerting evidence.
- **Risks/negative tests:** invented or malicious contact/URL, stale/expired/revoked source, wrong
  locale/jurisdiction, source outage, unstaffed-service promise, hidden urgent control, unsafe cache.
- **Possible separately authorized scope:** generic unavailable/degraded state tests without contacts.
- **STOP:** no current approved resource evidence and copy; never infer continuous availability or
  substitute model memory.

## 2.6 Professional-support referrals — BLOCKED

- **Accountable roles:** P13 referral/integration owner; privacy/legal and consent owner; identity;
  resource governance; security; operations.
- **Repository evidence:** `REFERRAL_SHARING` consent vocabulary exists; P13 runtime does not.
- **Unresolved decisions/artifacts:** recipient/destination authority; minimized field allowlist;
  explicit notice and active sharing consent; external adapter; transaction/outbox/idempotency;
  status evidence, webhook/reconciliation, retry/ambiguous-effect, withdrawal and correction.
- **Risks/negative tests:** inferred/general consent, revoked consent race, recipient substitution,
  raw transcript sharing, duplicate send, spoofed/replayed webhook, false delivery/completion state.
- **Possible separately authorized scope:** synthetic `unavailable`, `unknown`, and `failed` view-state
  tests with no recipient, payload, network, or side effect.
- **STOP:** P13, recipient, minimization, exact consent, status truth, or incident handling is absent.

## 2.7 Patient content, multilingual safety, and accessibility — BLOCKED

- **Accountable roles:** clinical/content; Hindi/English/Hinglish language reviewers; accessibility;
  privacy; patient experience; P12 owner; institution owner.
- **Repository evidence:** P6/P7 responsive accessible shell, English/Hindi preference, manual input,
  and generic urgent-help control; no P12/P14 content or conversation UI.
- **Unresolved decisions/artifacts:** non-therapy/non-diagnostic/non-emergency disclosure; approved
  conversation/crisis/clarification/degraded copy and translations; opt-out; age/guardian states;
  keyboard/focus/screen-reader/forced-color/reflow patterns; source warnings and language parity.
- **Risks/negative tests:** translation semantic drift, missing locale, inaccessible urgent action,
  chatbot auto-start, false promise of response, coercive copy, diagnosis/medication wording, 320/390px
  overflow and persistent browser residue.
- **Possible separately authorized scope:** static synthetic unavailable-state accessibility tests,
  without crisis guidance or clinical text.
- **STOP:** approved source copy, translations, accessibility, age/authority, or P12 evidence is absent.

## 2.8 Safety regression, governance, incident, and pilot/release — BLOCKED

- **Accountable roles:** clinical safety and independent validators; research/ethics; security/privacy;
  operations/SRE; audit/model governance; product/institution release owner.
- **Repository evidence:** CI and synthetic P8/P9 tests are engineering evidence only; no P14 corpus or
  clinical results.
- **Unresolved decisions/artifacts:** licensed, representative, clinically reviewed held-out corpus;
  harmful-error taxonomy; false-negative/disagreement review; predeclared acceptance criteria;
  protected-environment safe-off; audit without transcripts; monitoring; incident/rollback drills;
  pilot population/environment and signed time-bounded release.
- **Risks/negative tests:** benchmark leakage, post-hoc thresholds, mock in protected mode, audit/log
  leakage, expired approval, configuration drift, undetected harmful error, failed rollback and manual
  fallback dependence.
- **Possible separately authorized scope:** offline synthetic harness structure with no clinical cases,
  thresholds, data, or release claim.
- **STOP:** any validation, governance, ethics, incident, monitoring, pilot, expiry, or release evidence
  is absent. CI/model score/PR review cannot substitute.

# 3. Requirements and acceptance truth

The framework maps all `FR-MH-001..020`, all `AC-P14-001..013`, and relevant global safety,
privacy, consent, accessibility, P8/P9/P12/P13/P21 dependencies. Every live P14 criterion remains
**NOT VERIFIED**. No P14 clinical/test approval is created by the proposed negative-test inventory.

# 4. Owner and risk register

| Decision domain | Accountable role(s), assignment pending | Principal risk |
| --- | --- | --- |
| Clinical policy/source/population | Mental-health clinical and clinical-safety owners | Harmful invented or out-of-scope route |
| Privacy/consent/retention | Privacy/legal, consent and records owners | Sensitive processing/disclosure without authority |
| Backstop/extraction/language | Clinical-language, P8, architecture and security owners | Missed or misread safety-relevant meaning |
| Deterministic policy lifecycle | Clinical policy, audit and release owners | Model downgrade or unapproved activation |
| Crisis resources/operations | Source governance, clinical safety and operations | False/stale resource or response promise |
| Referral | P13, consent, identity and integration owners | Unauthorized sharing or false status |
| Patient content/accessibility | Clinical content, language and accessibility owners | Misleading or inaccessible safety interaction |
| Validation/pilot/incident | Independent clinical validation, ethics, SRE and institution owners | Unmeasured harmful error or unsafe release |

# 5. Unsigned decision and evidence checklist

```text
Decision ID / domain / artifact version:
Population / age / jurisdiction / languages / environment:
Authoritative sources and licenses reviewed:
Clinical rules, exclusions, ambiguity and prohibited inferences:
Privacy purpose, notice, consent, processing and retention:
Identity / minor / guardian / assisted-use authority:
Provider / processor / region / egress / training controls:
Resource source, verification, expiry and incident owner:
Referral recipient, minimized payload and consent evidence:
Validation corpus, harmful-error taxonomy and acceptance evidence:
Accessibility and approved copy/translation evidence:
Monitoring, incident, rollback and re-review expiry:
Clinical maker name/role/date/signature:                 [PENDING]
Independent clinical checker name/role/date/signature:   [PENDING]
Privacy/legal name/role/date/signature:                  [PENDING]
Security name/role/date/signature:                       [PENDING]
Language/accessibility name/role/date/signature:         [PENDING]
Operations/institution release signature:               [PENDING]
Outcome: APPROVED / REJECTED / DEFERRED                  [UNSIGNED]
```

No field is signed by this work. Documentation, a historical source proposal, generic urgent-help
UI, CI, P9 synthetic tests, an LLM score, PR review, or a model benchmark cannot substitute for
clinical or other accountable approval.

# 6. Preserved upstream restrictions and final STOP rule

- P8-C and P9-C Stage 3 remain **BLOCKED**.
- P10 live remains **0/9 APPROVED**.
- P11 live remains **0/9 APPROVED (5 OPEN, 4 BLOCKED)**.
- P12, P13, and P21 runtime remain **NOT STARTED**.
- P13’s eight proposed gates remain **4 OPEN / 4 BLOCKED** and are not an approval program.
- P7 deterministic manual text/touch intake and generic urgent-help navigation remain independent.
- P14 remains **NOT STARTED** and has no accepted gate count or clinical/test approval.
- Alembic remains `p7a_0007`; no runtime, dependency, schema, API, UI, policy, provider, resource,
  consent behavior, or accepted ADR changes are authorized.

**STOP** before P14 implementation until a separately reviewed prompt defines a safe scope and every
applicable accountable decision/evidence above is recorded. This documentation does not authorize
mental-health conversations, patient-data processing, screening, triage, crisis guidance, verified
resources, referrals, clinical evaluation, pilot, or production release.
