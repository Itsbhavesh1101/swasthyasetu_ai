# P15 Self-Care / RAG Readiness Gate Review

> **UNAPPROVED PROPOSED REVIEW INVENTORY — NOT AN ACCEPTED NUMBERED HUMAN APPROVAL PROGRAM**

**Evidence baseline:** `main` at `bfba7f5a5993c1572c5ad18b942013a0badc3495` (2026-10-23)

**Implementation status:** P15 **NOT STARTED**

**Live acceptance:** **NOT VERIFIED**

**Authority:** Codex can prepare evidence and tests but cannot approve a clinical policy, source, consent basis, provider, pilot, or release.

This inventory deliberately has no official gate count and must not be reported as `0/N approved`. `OPEN` means a required accountable decision and evidence package does not yet exist. `BLOCKED` means an upstream authority or capability required even to complete that review is absent. Neither status permits runtime work.

Canonical anchors are the [self-care framework](../10_SELF_CARE_AYURVEDA_POLICY.md), [RAG specification](../17_RAG_KNOWLEDGE_SPEC.md), [product requirements](../01_PRODUCT_REQUIREMENTS.md), [safety policy](../08_SAFETY_AND_TRIAGE_POLICY.md), [privacy specification](../26_PRIVACY_CONSENT_SPEC.md), [implementation plan](../34_MASTER_IMPLEMENTATION_PLAN.md), [acceptance criteria](35_PHASE_ACCEPTANCE_CRITERIA.md), and [decision log](37_DECISION_LOG.md).

## 1. Repository evidence and non-authority

- `backend/app/modules/self_care/`, relevant clinical knowledge/policy locations, and self-care test-case locations are placeholders; no P15 runtime is composed.
- P9 contains synthetic engineering mechanics only and is not approved to classify real patients. P9-C Stage 3 remains **BLOCKED**.
- P13 and P14 are draft policy/readiness work; verified provider data and approved mental-health policy are absent.
- P12 and P21 runtime are **NOT STARTED**. There is no approved P15 translation or maker-checker workflow.
- P10 and P11 live human gates remain `0/9 APPROVED`; P11 remains five `OPEN` and four `BLOCKED`.
- Existing P4 general-product/clinical-intake consent does not authorize P15 or RAG processing.
- PostgreSQL is authoritative, while any future index/cache is derived. No pgvector schema, embedding model, corpus, or provider is selected.
- Alembic head remains `p7a_0007`; accepted ADRs remain unchanged.

Green documentation checks or CI prove only repository integrity. They do not change any status below.

## 2. Proposed review domains

### 2.1 Qualified source, content rights, and publication — OPEN

**Evidence:** no production knowledge pack, source register, licensed corpus, approved content, signed review, effective interval, translation set, or withdrawal mechanism exists.

**Accountable roles:** qualified clinical content owner; Ayurveda/gharelu subject-matter reviewer with institutionally accepted qualifications; evidence/source librarian; intellectual-property/legal reviewer; language reviewer; publication owner; independent checker.

**Decisions and artifacts required:** intended non-curative scope; admissible evidence/source categories; rights and license proof; population/language/jurisdiction applicability; immutable pack/item versions; author and independent reviewer proof; effective/expiry/supersession/withdrawal states; publication and recall runbook; source-change review; signed decision records.

**Risks and negative evidence:** fabricated or weak source, rights violation, stale/expired content, silent mutation, withdrawn item remaining visible, population mismatch, translation drift, reviewer conflict, or source citation treated as medical validation.

**Narrow offline work if separately authorized:** schema-only validation against synthetic, unmistakably non-production placeholders; no remedy or real source content.

**STOP:** no real ingestion, pack publication, fixture resembling advice, retrieval, or patient display until all decisions are signed and independently reviewable.

### 2.2 Physical safety, eligibility, and context drift — BLOCKED

**Evidence:** P9 has closed synthetic mechanics but no approved live clinical policy. P15 cannot determine that any real patient is low risk. No approved context-completeness or drift contract is implemented.

**Accountable roles:** clinical safety lead; emergency/triage policy owner; patient-safety officer; clinical informatics owner; privacy owner; safety engineering owner; institutional release authority.

**Decisions and artifacts required:** approved physical-safety authority and version; active exclusion behavior; trustworthy context inputs and freshness; uncertainty/conflict handling; no-downgrade precedence; eligibility decision provenance; context snapshot and pre-display drift checks; independently reviewed fallback and incident plan.

**Risks and negative evidence:** false low-risk inference, stale safety result, later rule/model/admin downgrade, incomplete context treated as eligible, consent or subject drift, race between eligibility and display, and optional dependency failure removing urgent navigation.

**Narrow offline work if separately authorized:** engineering-only state-machine/property tests with synthetic labels and no clinical thresholds.

**STOP:** P9 clinical policy/activation and accountable validation are prerequisites. No real patient eligibility or self-care result.

### 2.3 Contraindications and contextual exclusions — BLOCKED

**Evidence:** no validated allergy, medication, chronic-condition, age, pregnancy, interaction, or other P15 exclusion set exists; no trustworthy P15 projection is approved.

**Accountable roles:** qualified prescribing/medication-safety reviewer where applicable; clinical specialty owners; pharmacovigilance/clinical safety owner; clinical informatics/data-quality owner; privacy/legal owner; independent validator.

**Decisions and artifacts required:** approved rule sources and versions; fields and confidence/freshness requirements; purpose and authority to use each field; explicit unknown/contradictory behavior; validated rule interactions; change control; held-out clinical validation; rollback and incident evidence.

**Risks and negative evidence:** unknown value interpreted as false, medication name mismatch, stale history, contradictory facts, age/pregnancy inference, missing-data bypass, order-dependent rules, or non-clinical admin override.

**Narrow offline work if separately authorized:** generic fail-closed engine interfaces using non-medical synthetic predicates only.

**STOP:** no clinical exclusions may be invented, inferred from roadmap prose, or activated without qualified review and approved trustworthy inputs.

### 2.4 Knowledge retrieval and RAG — OPEN

**Evidence:** no approved corpus, ingestion pipeline, pgvector schema, embedding/reranker model, provider, region, metric, cutoff, benchmark, or retrieval service exists. The repository’s R3 material describes candidates and boundaries only.

**Accountable roles:** architecture/data owner; security architect; privacy/legal and data-protection owner; clinical/content owner; ML/retrieval evaluation owner; operations owner; institutional technology authority.

**Decisions and artifacts required:** approved use case and proof vector retrieval is necessary; source-to-index lineage; strict corpus/tenant/subject filters; source version/expiry/retraction enforcement; embedding/provider/version/license/region decision; multilingual and medical-domain benchmark; injection and poisoning defense; deterministic post-filter; abstention; index rebuild/rollback/reconciliation plan.

**Risks and negative evidence:** prompt injection, wrong-tenant retrieval, filter bypass, poisoned embeddings, stale indexes, mixed rebuild generations, source substitution, approximate false positives, semantic mismatch, fabricated citations, generated additions, or retrieval before authorization.

**Narrow offline work if separately authorized:** provider-neutral interface or benchmark-shape design with synthetic, non-medical text; no package, model, index, content, or provider activation.

**STOP:** an index or similarity score cannot create approval or eligibility. Missing lineage/consistency/authorization yields abstention.

### 2.5 Privacy, legal, consent, and identity — OPEN

**Evidence:** current consent covers declared general-product/clinical-intake scope only. No P15 purpose, notice, guardian/institution policy, patient-context authority, embedding classification, egress decision, or lifecycle exists.

**Accountable roles:** privacy officer/data-protection officer; legal/compliance owner; consent/product owner; identity and institution-authorization owner; security owner; data governance/records owner.

**Decisions and artifacts required:** purpose and data-flow inventory; notice and explicit scope; applicable consent and all additional lawful/governance requirements; subject/guardian/institution authority; minimum-necessary fields; record/field permissions; provider/egress/region terms; retention, deletion, backup and revocation; audit/incident plan without raw narratives; threat/privacy assessment specific to P15.

**Risks and negative evidence:** consent transitivity, cross-subject or cross-institution access, revoked purpose still retrieving, embeddings assumed anonymous, raw narrative in logs/traces/analytics, provider reuse, backup/index deletion gaps, or existence leakage.

**Narrow offline work if separately authorized:** synthetic data-flow and authorization-model tests only.

**STOP:** no real patient data, narrative, query, embedding, egress, analytics, or browser persistence before signed decisions and enforceable controls.

### 2.6 Admin, maker-checker, audit, and rollback — BLOCKED

**Evidence:** P21 runtime is **NOT STARTED**. No approved P15 role model, clinical review queue, source-change workflow, maker-checker enforcement, signature mechanism, audit viewer, or rollback control exists.

**Accountable roles:** clinical governance chair; content/source owner; independent approver; identity/authorization owner; audit/compliance owner; security owner; operations/release owner.

**Decisions and artifacts required:** role separation; reviewer qualification/independence; conflict-of-interest handling; state-transition authority; strong authentication and administrative MFA gate; immutable signatures/evidence; policy/content separation; audit scope; emergency withdrawal; rollback; periodic recertification.

**Risks and negative evidence:** self-approval, stale role, privileged bypass, approval by UI visibility, editing an approved version, audit tampering, policy changed through content, rollback to withdrawn content, or feature flag used as authority.

**Narrow offline work if separately authorized:** authorization-matrix and transition-model tests using synthetic principals, with no production admin workflow.

**STOP:** no UI, database flag, role, or feature flag can approve or override clinical content. P21 absence blocks live workflow.

### 2.7 Patient content, language, accessibility, and navigation — BLOCKED

**Evidence:** no approved self-care copy, escalation wording, language-equivalence set, accessible presentation, P15 UI, or verified P13 production provider directory exists. P12/P13/P14 runtime is **NOT STARTED**.

**Accountable roles:** qualified clinical content owner; plain-language and health-literacy owner; language/translation reviewers; accessibility owner; P13 source-verification owner; patient-safety/usability owner; legal/privacy owner.

**Decisions and artifacts required:** supportive/non-curative copy; exact source/version/freshness presentation; approved caveats and stop/escalation text; accessible block/unavailable states; language fallback/abstention; translation equivalence; verified current provider navigation; P7 and generic urgent-help independence; usability and assistive-technology evidence.

**Risks and negative evidence:** curative implication, omitted exclusion, stale source, unsafe translation, locale fallback presented as approved, inaccessible warning, invented provider/contact, mental-health route interference, or optional AI outage breaking core navigation.

**Narrow offline work if separately authorized:** generic non-clinical unavailable-state accessibility prototypes, isolated from patient routes and without medical copy.

**STOP:** missing approved content, locale, accessibility, or verified provider source means no advice. P7 manual intake and generic urgent-help paths must remain independent.

### 2.8 Validation, operations, pilot, and release — BLOCKED

**Evidence:** no approved clinical test corpus, representative held-out benchmark, false-allow analysis, operational telemetry plan, incident process, staged runtime, pilot protocol, or production decision exists.

**Accountable roles:** clinical validation owner; patient-safety/risk owner; QA and security testing owners; accessibility/language validators; privacy/legal owner; SRE/operations owner; institutional pilot and production release authorities.

**Decisions and artifacts required:** approved synthetic and held-out cases; expected outcomes signed by qualified reviewers; false-allow/harmful-content analysis; source/translation/version drift tests; privacy/security/adversarial evidence; safe-off staging isolation; monitoring without sensitive content; incident/recall drills; pilot population and stop rules; separate production release record.

**Risks and negative evidence:** engineering tests mistaken for clinical validation, test leakage, fabricated expected outcomes, unsafe silent fallback, incomplete monitoring, production data in staging, unverifiable incident response, or pilot treated as production approval.

**Narrow offline work if separately authorized:** non-clinical contract/property/security tests with clearly synthetic fixtures and no runtime route.

**STOP:** CI is not clinical approval. Pilot and production require separate accountable decisions after all dependencies are satisfied.

## 3. Traceability to missing evidence

### 3.1 FR-SELF-001..017

| Requirement | Review domain(s) | Missing evidence; status remains LIVE NOT VERIFIED |
|---|---|---|
| FR-SELF-001 configured low-risk only | 2, 8 | Approved P9 authority, eligibility configuration, validation and release |
| FR-SELF-002 supportive/non-curative framing | 1, 7 | Approved clinical/legal/language/accessibility content |
| FR-SELF-003 curated versioned source | 1, 4 | Licensed approved corpus and enforced version lifecycle |
| FR-SELF-004 source/reference category | 1 | Approved taxonomy and verified source evidence |
| FR-SELF-005 approval/review state | 1, 6 | Approved workflow, qualified signers and immutable audit |
| FR-SELF-006 active safety exclusion blocks | 2 | Live policy, hard precedence and no-downgrade proof |
| FR-SELF-007 known allergy consideration | 3, 5 | Authorized trustworthy allergy context and validated rule |
| FR-SELF-008 validated medication conflicts | 3 | Qualified validated rules/data and change control |
| FR-SELF-009 known chronic-condition exclusions | 3 | Qualified validated rules and trustworthy context |
| FR-SELF-010 age restrictions | 3, 5 | Approved restriction and verified authorized age data |
| FR-SELF-011 pregnancy restrictions | 3, 5 | Approved restriction and explicitly available authorized data |
| FR-SELF-012 observation/duration limits | 1, 7 | Clinically approved item content and accessible rendering |
| FR-SELF-013 stop/escalation conditions | 1, 7 | Approved copy and independently verified navigation |
| FR-SELF-014 LLM cannot leave approved system | 4, 8 | Deterministic allowlist, attacks, abstention and validation |
| FR-SELF-015 clinical review before production | 1, 6, 8 | Qualified independent decisions and signed release |
| FR-SELF-016 delivered version traceability | 1, 4, 6 | End-to-end immutable lineage and audit |
| FR-SELF-017 add pack without engine change | 1, 4 | Approved versioned schema, compatibility tests and loader |

### 3.2 AC-P15-001..010

| Acceptance criterion | Review domain(s) | Missing evidence; status remains LIVE NOT VERIFIED |
|---|---|---|
| AC-P15-001 safety before self-care | 2 | Approved live safety gate and integration proof |
| AC-P15-002 approved/versioned store | 1, 4 | Approved store, corpus, lifecycle and access enforcement |
| AC-P15-003 no normal display of unapproved/expired | 1, 4, 7 | Lifecycle filtering, cache/index invalidation and UI tests |
| AC-P15-004 contraindication engine | 3 | Approved rules, implementation and clinical validation |
| AC-P15-005 allergies affect eligibility | 3, 5 | Authorized data projection and validated behavior |
| AC-P15-006 medication/condition exclusions | 3 | Approved configurations and validation |
| AC-P15-007 age/pregnancy enforcement | 3, 5 | Approved constraints, reliable context and tests |
| AC-P15-008 displayed escalation/stop conditions | 1, 7 | Approved, translated, accessible content |
| AC-P15-009 LLM cannot introduce absent remedy | 4, 8 | Source-bound post-filter and adversarial proof |
| AC-P15-010 synthetic placeholder is non-production | 1, 8 | Isolation, unmistakable labeling and activation prevention |

### 3.3 SAFE and upstream gates

`SAFE-001..010` apply across domains 1–8. The minimum evidence must show no autonomous diagnosis/prescription; deterministic precedence; human clinical authority; safe uncertainty; urgent/crisis independence from optional models; no invented resources; no unrestricted model-memory remedies (`SAFE-008`); no content under active exclusion/urgent red flag (`SAFE-009`); and versioned decisions. No current P15 artifact satisfies live acceptance.

Upstream dependencies remain unresolved: P8-C and P9-C Stage 3 are **BLOCKED**; P10 and P11 live gates remain `0/9 APPROVED`; P11 is five `OPEN` and four `BLOCKED`; P12/P13/P14/P15/P21 runtime remains **NOT STARTED**; P13’s eight proposed/unapproved gates remain four `OPEN` and four `BLOCKED`; neither P14 nor P15 has an official approved gate count. P7 manual intake remains the independent supported fallback. P22 is not complete.

## 4. Unsigned human decision and evidence template

> Copy only into an accountable review system after governance owners approve that system. A filled draft is not approval without verified signer identity and authority.

| Field | Required entry |
|---|---|
| Review domain and decision ID | `[PENDING]` |
| Decision requested and bounded scope | `[PENDING]` |
| Alternatives considered | `[PENDING]` |
| Evidence locations, immutable versions, and hashes | `[PENDING]` |
| Requirements/risks addressed | `[PENDING]` |
| Preconditions and dependencies | `[PENDING]` |
| Negative tests and observed results | `[PENDING]` |
| Residual risks and owner | `[PENDING]` |
| Effective/expiry/review dates | `[PENDING]` |
| Rollback/withdrawal/incident trigger | `[PENDING]` |
| Qualified maker identity/role/signature | **UNSIGNED — PENDING** |
| Independent checker identity/role/signature | **UNSIGNED — PENDING** |
| Privacy/legal/security/clinical countersignatures where required | **UNSIGNED — PENDING** |
| Outcome | **NO DECISION RECORDED** |

Codex must not populate a human signature, mark an approval, choose clinical expected outcomes, or infer authority from a repository account.

## 5. Owner and risk register

| Risk/decision area | Accountable role(s) not yet assigned by name | Present state |
|---|---|---|
| Content efficacy/safety and intended scope | Qualified clinical content and Ayurveda/gharelu reviewers | OPEN |
| Sources, evidence quality, license and withdrawal | Source librarian, rights/legal, publication owner | OPEN |
| Physical safety and low-risk eligibility | Clinical safety and institutional patient-safety authorities | BLOCKED by live P9 approval |
| Contraindications and trusted context | Clinical specialty/medication safety and informatics owners | BLOCKED by approved rules/data |
| Consent, identity, privacy, retention and egress | Privacy/legal, identity, data governance, institutional owners | OPEN |
| Retrieval/model/index security and evaluation | Architecture/data, security, ML evaluation, operations owners | OPEN |
| Maker-checker and audit | Clinical governance, IAM, compliance/audit owners | BLOCKED by P21 implementation |
| Language, content safety and accessibility | Qualified language, clinical content, accessibility owners | BLOCKED by approved artifacts |
| Provider/urgent navigation | P13 source-verification and clinical safety owners | BLOCKED by verified runtime sources |
| Validation, pilot and production | Clinical validation, risk, operations and institutional release authorities | BLOCKED by all preceding evidence |

## 6. Final STOP and next action

P15-A/B/C/D/E remain future conditional phases requiring separate prompts. No runtime code, migration, API, storage, corpus, model, index, content, feature flag, provider, UI, pilot, or release is authorized by this review.

**STOP** until accountable owners are assigned and independently record the necessary evidence and decisions. The next action is human review of these draft contracts: confirm scope and source admissibility; establish live safety ownership; approve or reject each data purpose; decide whether non-vector structured retrieval is sufficient; define reviewer identity and workflow; approve language/accessibility and verified navigation requirements; and establish validation, incident, pilot, and production decision paths. Unknown evidence stays pending and fails closed.
