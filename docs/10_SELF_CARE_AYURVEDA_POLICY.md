# 10 — Self-Care and Ayurveda / Gharelu Guidance Policy Framework

> **DRAFT — NO APPROVED REMEDIES, CLINICAL ELIGIBILITY, TREATMENT, MEDICATION ADVICE, PATIENT-FACING GUIDANCE, OR LIVE P15 AUTHORIZATION**

| Evidence field | Value |
|---|---|
| Repository baseline | `main` at `bfba7f5a5993c1572c5ad18b942013a0badc3495` |
| Evidence date | 2026-10-23 |
| Runtime status | P15 is **NOT STARTED** |
| Accountable owners | Qualified clinical, source/content-rights, privacy/legal, security, architecture/data, language, accessibility/content, operations, and institutional owners are unresolved |
| Authority | Process and future architecture only; this draft grants no human approval |

This framework must be read with the [master specification](00_PROJECT_MASTER_SPEC.md), [product requirements](01_PRODUCT_REQUIREMENTS.md), [system architecture](02_SYSTEM_ARCHITECTURE.md), [domain model](04_DOMAIN_MODEL.md), [safety policy](08_SAFETY_AND_TRIAGE_POLICY.md), [privacy and consent specification](26_PRIVACY_CONSENT_SPEC.md), [implementation plan](34_MASTER_IMPLEMENTATION_PLAN.md), and [phase acceptance criteria](implementation/35_PHASE_ACCEPTANCE_CRITERIA.md). “Shall” below describes a constraint on separately authorized future work. It does not describe an implemented or approved clinical capability.

## 1. Scope, terms, and actual baseline

“Self-care guidance” means a future, bounded presentation of qualified-human-approved supportive content after independent authorization and deterministic safety eligibility. “Ayurveda / gharelu” is a content-governance category, not an assertion of efficacy, safety, diagnosis, or treatment authority. No item in that category exists in the repository as approved content.

### 1.1 As-built evidence

| Area | Trusted as-built capability | Explicitly absent or insufficient for P15 |
|---|---|---|
| P4 sessions, identity, consent | Pseudonymous session primitives, server-side actor authorization foundations, and scoped consent records | No P15 purpose, patient-facing identity assurance, guardian/institution decision, or self-care authorization. General-product and `clinical_intake` consent are not transitive. |
| P5 structured clinical context | Versioned structured patient/encounter/fact foundations and provenance contracts | No approved P15 context projection, completeness standard, exclusion evidence, or self-care use authorization. |
| P7 intake | Deterministic, non-diagnostic intake flow with manual text/touch operation | No P15 eligibility result. P7 input cannot itself prove low risk. |
| P8 extraction | Engineering contracts and gated technical extraction work | No patient-facing AI activation or authority to supply P15 clinical facts. P8-C restrictions remain. |
| P9 safety | Synthetic, engineering-only physical-safety decision mechanics | No approved live clinical policy, clinical fixtures, patient activation, or authority to classify a real patient as low risk. P9-C Stage 3 remains **BLOCKED**. |
| P12 language | Draft multilingual/speech specification and readiness inventory | No approved P15 translation, semantic-equivalence evidence, or live speech authorization. Runtime is **NOT STARTED**. |
| P13 provider/resources | Draft routing policy and proposed readiness inventory | No verified production directory or referral runtime. Provider navigation cannot use invented details. |
| P14 mental health | Draft policy framework and readiness inventory | No approved mental-health clinical policy or runtime. P15 cannot absorb or bypass P14 decisions. |
| P21 admin | Draft admin-portal specification | No clinical content workflow, maker-checker implementation, audit viewer, or runtime authority. |
| P15 self-care | Placeholder module and empty clinical knowledge/policy directories | No approved knowledge, eligibility rules, contraindication engine, retrieval corpus, service, API, UI, or runtime registration. |

The repository contains no production knowledge pack, qualified source decision, validated exclusion set, embedding model, vector index, or patient-facing remedy. Empty directories, conceptual types, version constants, synthetic fixtures, green CI, and files titled “policy” are not clinical evidence.

### 1.2 Consent and authority boundary

Existing general-product and clinical-intake authorization covers only its declared purpose and scope. It does not authorize self-care personalization, retrieval using patient context, embeddings, provider egress, publication, or reuse. Future processing requires an explicit purpose, notice, applicable consent and/or other lawful requirements as determined by accountable privacy/legal reviewers, subject/guardian/institution authority where relevant, and enforceable withdrawal and deletion behavior. A feature flag, session, authentication event, admin role, or accepted document cannot substitute for that review.

## 2. Separation of duties and authority

Future P15 work must keep these authorities separate and independently reviewable:

1. **Curated content and provenance.** Qualified source/content-rights owners establish source legitimacy, rights, immutable versions, population and jurisdiction scope, and withdrawal. They do not determine patient eligibility.
2. **Clinical eligibility and safety policy.** Accountable clinical/safety owners define and approve deterministic eligibility, exclusions, uncertainty behavior, and escalation. A content editor cannot change these rules.
3. **Deterministic personalization filters.** Engineering applies approved rules only to authorized, sufficiently trustworthy context. It must not infer missing clinical data or turn retrieval similarity into eligibility.
4. **Source-bound explanation and rendering.** Content/language/accessibility owners approve faithful rendering of already eligible, approved content. Generative output cannot add advice, omit exclusions, or alter authority.
5. **Approval, maker-checker, and audit.** Separately accountable reviewers control state transitions, signed evidence, release, rollback, and immutable audit. P21 is not implemented, so no repository UI currently supplies this authority.
6. **Provider and urgent-care navigation.** Independently verified P13 sources govern any future provider destination. Navigation cannot be invented or treated as P15 content approval.

Admin visibility, a database row, a retrieval score, or a privileged role does not grant clinical approval or override an active safety decision.

## 3. Future knowledge-pack contract

This section is a non-executable contract aligned with the conceptual `SelfCareGuidanceDefinition`. It contains no example remedy and defines no approved workflow.

### 3.1 Manifest and item identity

A future pack requires a manifest identifier and immutable manifest version; each item requires an immutable guidance ID and content version. The manifest binds item hashes, schema version, release evidence, language variants, dependency versions, and lifecycle state. Published bytes must never be silently mutated. A correction creates a new version with explicit supersession; withdrawal preserves history and prevents ordinary use.

### 3.2 Required item metadata

An item must be rejected from admission if any required field lacks approved evidence:

- source identity, license/rights evidence, reference, and source category;
- authorship and independent reviewer identity proof through an approved signing mechanism;
- conceptual review state, effective interval, expiry, supersession, withdrawal, and reason metadata;
- intended population, language, jurisdiction, and applicability limits;
- qualified-human-approved supportive content and context tags;
- contraindications and only validated medication/chronic-condition exclusions;
- optional age or pregnancy constraints only when specifically approved and representable;
- observation/duration limit where approved as relevant, plus mandatory stop/escalation conditions;
- translation lineage, semantic-equivalence evidence, test evidence, and release record.

Conceptual lifecycle states are `DRAFT`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`, `RETIRED`, and `EXPIRED`, consistent with the domain model. These labels do not establish a production workflow. No such approved workflow exists. “Approved” can become operational only after accountable reviewers define identity, signature, segregation, evidence, expiry, withdrawal, rollback, and audit controls.

## 4. Safety and eligibility ordering contract

For separately authorized future operation, evaluation order is non-negotiable:

1. an approved physical-safety determination and its active exclusions;
2. explicit context completeness, freshness, consistency, and uncertainty checks;
3. approved age and pregnancy constraints, only when relevant data is authorized and known;
4. known allergies, validated medication/chronic-condition conflicts, and other approved contraindications;
5. retrieval of an approved, current, applicable, version-bound knowledge item;
6. safe, source-bound, approved-language presentation.

This order is a software and governance contract, not a clinical rule for any patient. Unknown, unverified, expired, missing, stale, ambiguous, conflicting, or changed input cannot be treated as eligible. The safe outcome is abstention/unavailable state and the independently approved next action, not an invented assumption.

No red flag, threshold, diagnosis, dose, recipe, treatment instruction, or escalation script is defined here. Until an approved live P9 policy can establish authoritative physical-safety input, P15 cannot label a real patient low-risk and cannot enable self-care guidance. Later filters may only make the result more restrictive; they cannot downgrade an earlier safety block.

Eligibility provenance must bind the subject/context snapshot, authorized purpose, eligibility-policy ID/version, matched exclusion IDs, knowledge ID/version, evaluation time, and outcome. Before display, drift checks must prove those bindings remain current. A mismatch forces re-evaluation or abstention.

## 5. Retrieval is not clinical authority

PostgreSQL records, vector indexes, caches, search scores, semantic similarity, rerankers, and language models are never clinical eligibility or governance authority. After authorization and deterministic gating, retrieval may discover candidate items already admitted to the approved corpus. It must then apply authoritative metadata filters and an exact presentation allowlist.

Retrieval must not:

- introduce an item absent from approved knowledge;
- use model memory as the corpus;
- weaken or overwrite an exclusion;
- infer approval, applicability, diagnosis, or safety from similarity;
- replace source/version and eligibility-policy provenance with a citation-like string.

A missing or failed model, retrieval service, schema, translation, source, lifecycle proof, or governance authorization produces no patient remedy. Ordinary structured lookup may be sufficient; vector retrieval and generated explanation are optional future capabilities, not prerequisites.

## 6. Future presentation, language, and accessibility

Any later UI requires accountable review of supportive, non-curative framing; exact provenance and version; applicable caveats; mandatory stop/escalation conditions; source and freshness indicators; and accessible exclusion or unavailable states. It must disclose when authorized content is missing rather than substitute another locale or generate content.

Translations require version-bound source linkage, qualified language review, clinical semantic-equivalence evidence, withdrawal propagation, and accessibility validation. Missing approved locale means no translated guidance. Doctor navigation may use only independently verified, current P13 sources. Generic urgent-help navigation and P7 manual text/touch intake must remain usable without P15, AI, vector search, speech, or optional providers.

This draft contains no patient-facing self-care wording and no real Ayurveda/gharelu example.

## 7. Privacy, security, and lifecycle

Future design must minimize patient context and access scope before retrieval. It requires accountable decisions for subject/guardian/institution authority; purpose and notice; consent and lawful processing; egress; query and embedding classification; provider terms and region; retention, deletion, withdrawal, backups, and derived-index erasure; and incident response.

Controls must include record- and field-level authorization, tenant/subject binding, encryption in transit and at rest, secret isolation, input/output size bounds, provenance integrity, index/cache invalidation, signed release evidence, rollback, and audit events that exclude raw narratives and restricted content. Logs, traces, metrics, analytics, browser storage, URLs, fixtures, and support tooling must not contain patient narratives, sensitive queries, embeddings, or unapproved knowledge.

No patient narrative may be embedded or sent externally in this phase. Embeddings must not be assumed anonymous. Consent withdrawal or source withdrawal must fail closed while source, indexes, caches, replicas, and presentations converge, with reconciliation evidence before reuse.

## 8. Required future negative-test catalogue

Each expectation below is conceptual and requires accountable owners to approve fixtures and expected outcomes. It is not clinical validation.

| Test class | Required safe expectation |
|---|---|
| Absent, expired, unapproved, superseded, or withdrawn guidance | No ordinary display; explicit unavailable/abstain state and auditable reason |
| Forged source, review, signature, or release evidence | Admission/display rejected; integrity incident surfaced |
| Stale eligibility policy or changed policy version | Re-evaluation required; no reuse of earlier allow result |
| Active hard-safety exclusion | Self-care blocked; later filters, flags, admins, retrieval, or models cannot downgrade it |
| Unknown allergy, medication, chronic-condition, age, or pregnancy context | No assumption of eligibility; approved clarification or unavailable path only |
| Conflicting history or insufficiently trusted fact | Fail closed and preserve conflict provenance |
| Context drift between eligibility and display | Bound snapshot comparison fails and presentation is suppressed |
| Revoked/absent purpose authorization | Retrieval and presentation denied; derived-data lifecycle initiated where applicable |
| Wrong subject, actor, session, institution, or tenant | Denied without existence or sensitive metadata leakage |
| Prompt injection in retrieved content/metadata | Instructions treated as untrusted data; allowlist and provenance checks hold |
| Model invents, substitutes, or expands a remedy | Output rejected; no patient presentation |
| Unsafe, stale, or unapproved translation | No fallback masquerading as approved localized guidance |
| Source, PostgreSQL, vector, model, or network outage | No invented remedy; independently usable P7/generic urgent-help path retained |
| Cache/index stale after expiry, revocation, or withdrawal | No display until authoritative consistency is proven |
| Feature flag or admin override attempt | Cannot bypass consent, safety, lifecycle, or clinical approval |
| Inaccessible warning or unavailable state | Release blocked until accessible equivalence is verified |
| P15 unavailable | P7 manual intake and generic urgent-help navigation remain independent |

## 9. Requirement and acceptance traceability

All entries are **LIVE NOT VERIFIED**. Exact wording is copied from the canonical requirements and acceptance criteria; drafting a section is not acceptance.

### 9.1 FR-SELF requirements

| ID | Exact canonical wording | Draft anchor | Missing accountable decision/evidence | Status |
|---|---|---|---|---|
| FR-SELF-001 | The self-care module SHALL operate only on configured low-risk contexts. | §4 | Approved P9 safety authority and clinical eligibility configuration | LIVE NOT VERIFIED |
| FR-SELF-002 | Patient-facing content SHALL be framed as supportive self-care/wellness information, not guaranteed disease cure. | §6 | Clinically, legally, and accessibly approved content | LIVE NOT VERIFIED |
| FR-SELF-003 | Patient-facing remedies/guidance SHALL come from a curated, versioned knowledge source. | §3, §5 | Approved sources, rights, corpus, and lifecycle | LIVE NOT VERIFIED |
| FR-SELF-004 | Every approved guidance item SHALL record a source/reference category. | §3 | Approved taxonomy and source evidence | LIVE NOT VERIFIED |
| FR-SELF-005 | Every guidance item SHALL have an approval/review state. | §3 | Signed maker-checker workflow and state authority | LIVE NOT VERIFIED |
| FR-SELF-006 | An active safety exclusion SHALL block self-care guidance. | §4 | Approved safety policy and integration | LIVE NOT VERIFIED |
| FR-SELF-007 | Where relevant, self-care eligibility SHALL consider known allergy information. | §4 | Authorized trustworthy allergy projection and approved rules | LIVE NOT VERIFIED |
| FR-SELF-008 | Where supported by validated rules/data, self-care eligibility SHOULD consider medication conflicts. | §4 | Validated rules/data and clinical review | LIVE NOT VERIFIED |
| FR-SELF-009 | Relevant known chronic-condition exclusions SHOULD be considered. | §4 | Validated condition exclusions and context governance | LIVE NOT VERIFIED |
| FR-SELF-010 | Age restrictions SHALL be enforceable where defined. | §3–§4 | Approved restrictions and verified age context | LIVE NOT VERIFIED |
| FR-SELF-011 | Pregnancy-related restrictions SHALL be enforceable where defined and when the relevant data is explicitly available. | §3–§4 | Approved restrictions, purpose, and explicit trusted data | LIVE NOT VERIFIED |
| FR-SELF-012 | Approved guidance SHOULD state an observation/duration limit where clinically relevant. | §3, §6 | Qualified review and approved presentation | LIVE NOT VERIFIED |
| FR-SELF-013 | Approved guidance SHALL state when to stop self-care and seek professional/urgent care. | §3, §6 | Approved escalation content and verified navigation | LIVE NOT VERIFIED |
| FR-SELF-014 | An LLM MUST NOT generate patient-facing treatment outside the approved knowledge system. | §5 | Enforced allowlist and adversarial validation | LIVE NOT VERIFIED |
| FR-SELF-015 | Safety-relevant self-care rules/content SHALL require appropriate clinical review before production use. | §2–§3 | Accountable reviewers, signatures, workflow, and evidence | LIVE NOT VERIFIED |
| FR-SELF-016 | Every delivered guidance item SHALL be traceable to its content version. | §3, §5 | End-to-end version binding and audit | LIVE NOT VERIFIED |
| FR-SELF-017 | New self-care knowledge packs SHALL be addable without changing the core self-care engine. | §3 | Approved schema, compatibility policy, and loader | LIVE NOT VERIFIED |

### 9.2 P15 acceptance criteria

| ID | Exact canonical wording | Draft anchor | Missing accountable decision/evidence | Status |
|---|---|---|---|---|
| AC-P15-001 | Self-care runs only after safety gating. | §4 | Approved live safety gate | LIVE NOT VERIFIED |
| AC-P15-002 | Knowledge is retrieved from approved/versioned content store. | §3, §5 | Approved store, corpus, and lifecycle | LIVE NOT VERIFIED |
| AC-P15-003 | Unapproved/expired content is not displayed normally. | §3, §8 | Implemented fail-closed enforcement and tests | LIVE NOT VERIFIED |
| AC-P15-004 | Contraindication engine exists. | §4 | Clinically approved rules and implemented engine | LIVE NOT VERIFIED |
| AC-P15-005 | Relevant known allergies can affect eligibility. | §4 | Authorized data and validated rules | LIVE NOT VERIFIED |
| AC-P15-006 | Configured medication/chronic-condition exclusions can affect eligibility. | §4 | Validated exclusion configurations | LIVE NOT VERIFIED |
| AC-P15-007 | Age/pregnancy constraints are enforceable when defined. | §4 | Approved constraints and reliable context | LIVE NOT VERIFIED |
| AC-P15-008 | Displayed guidance includes escalation/stop conditions. | §3, §6 | Approved content and accessible rendering | LIVE NOT VERIFIED |
| AC-P15-009 | LLM cannot introduce a remedy absent from approved knowledge. | §5, §8 | Enforced source-bound allowlist and attack tests | LIVE NOT VERIFIED |
| AC-P15-010 | Synthetic placeholder knowledge is clearly non-production when approved content is unavailable. | §1, §8 | Approved isolation/labeling controls for separately authorized fixtures | LIVE NOT VERIFIED |

### 9.3 Safety and upstream dependencies

Global `SAFE-001..010` remain governing constraints: no autonomous diagnosis or prescription; deterministic rules precede optional models; humans retain clinical authority; uncertainty takes the safer action or clarification route; optional-model failure cannot remove emergency/crisis handling; resources cannot be invented; model memory cannot supply unrestricted remedies; active exclusions or urgent red flags prohibit self-care content; and every decision requires version metadata. In particular, `SAFE-008` and `SAFE-009` are hard boundaries for §4–§5.

Privacy/consent decisions in §1.2 and §7, accessibility/language decisions in §6, P9 live safety approval, P12 translation approval, P13 verified navigation, P14 independent mental-health governance, and P21 approval-workflow implementation are unresolved dependencies. None is inherited from a green build or another phase’s consent.

Accepted ADRs constrain future work: ADR-003 preserves deterministic safety precedence; ADR-008 keeps PostgreSQL authoritative and indexes derived; ADR-014 permits only approved/versioned self-care knowledge; ADR-023 forbids fabricated real remedies/resources and requires synthetic labeling; ADR-027 keeps core paths independent of optional AI; ADR-028 keeps structured validated facts authoritative over raw chat; ADR-034 requires a narrow retrieval architecture; ADR-038 preserves dependency-profile boundaries. This draft records no ADR conflict and creates no new ADR.

## 10. Conditional future phases and STOP conditions

The following remain separate future work requiring separate prompts and human decisions:

- **P15-A:** knowledge-pack schema, admission contracts, lifecycle, and controlled loader;
- **P15-B:** deterministic eligibility and contraindication engine;
- **P15-C:** governance/admin review and audit workflow;
- **P15-D:** patient presentation and verified-provider escalation integration;
- **P15-E:** adversarial, regression, operational, and approval evidence.

**STOP** before any runtime, pilot, or release if any of these is absent: qualified clinical/content/source approval; licensed production source; validated exclusions; trustworthy current safety policy; explicit privacy/legal/consent purpose and authority; security and egress review; approved language and accessible copy; immutable version/lifecycle enforcement; verified safe fallback; signed accountable release decision. Unknown or disputed evidence is absence, not approval.

P15 remains **NOT STARTED**. This document cannot authorize patient-facing Ayurveda/gharelu guidance, medication advice, clinical triage, retrieval over patient data, a medical RAG model, publication, pilot, or production use.
