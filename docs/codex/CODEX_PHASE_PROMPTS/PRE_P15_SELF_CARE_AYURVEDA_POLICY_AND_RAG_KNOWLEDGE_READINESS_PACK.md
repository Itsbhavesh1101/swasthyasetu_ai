# SwasthyaSetu AI — Pre-P15 Self-Care / Ayurveda Policy and RAG Knowledge Readiness Pack

**Work unit:** `PRE-P15-SELFCARE-RAG-SPEC` — specification and accountable-human-review preparation **ONLY**.

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`

**Verified starting `main`:** `bfba7f5a5993c1572c5ad18b942013a0badc3495`

**Previous PR #43:** merged; its merge tree is identical to reviewed security-remediation head `18e1480c9699cd0fbecb9162eedc045fe7ef9037`. Pinned Next.js `16.4.2` and root `eslint-config-next` `16.4.2` must not change in this phase.

**Proposed branch:** `phase/pre-p15-selfcare-rag-policy-readiness`

**Baseline facts:** `docs/10_SELF_CARE_AYURVEDA_POLICY.md` and `docs/17_RAG_KNOWLEDGE_SPEC.md` do **not** exist at the baseline. `backend/app/modules/self_care/` is a placeholder and P15 runtime is **NOT STARTED**. `docs/implementation/38_PROGRESS_TRACKER.md` contains section `# 60. October 2026 Next.js Security Remediation`; the next section is **61**. Alembic head is `p7a_0007`. No clinically approved P15 knowledge, eligibility rules, real remedies, validated patient exclusions, retrieval corpus, model, embedding provider, or live RAG pipeline has been established.

> **Critical safety rule:** Neither a file named “policy” nor a draft RAG specification can make clinical content, citations, diagnoses, dosages, contraindication thresholds, preventive claims, or patient-facing Ayurveda/gharelu remedies authoritative. All actual content, safety criteria, patient data use and release decisions remain with qualified accountable reviewers. Documentation and green CI are **NOT approval**.

## 0 — Preflight: verify repository and authority

1. Fetch the GitHub remote and verify that `origin/main` equals the exact starting SHA above and that PR #43 is merged/tree-equivalent. If it has drifted, **STOP and report**; do not silently rebase or change baseline.
2. Use a **new clean isolated Git worktree and branch**. Do not reset, clean, force-push, or alter any other worktree or pre-existing untracked files. Follow `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`.
3. Read and resolve precedence from actual current files, at minimum:
   - `docs/{00_PROJECT_MASTER_SPEC,01_PRODUCT_REQUIREMENTS,02_SYSTEM_ARCHITECTURE,03_REPOSITORY_STRUCTURE,04_DOMAIN_MODEL,06_API_CONTRACTS,08_SAFETY_AND_TRIAGE_POLICY,09_MENTAL_HEALTH_POLICY,11_PROVIDER_ROUTING_POLICY,13_AI_ORCHESTRATION_SPEC,14_LLM_EXTRACTION_SPEC,16_MULTILINGUAL_SPEECH_SPEC,25_ADMIN_PORTAL_SPEC,26_PRIVACY_CONSENT_SPEC}.md`;
   - `docs/34_MASTER_IMPLEMENTATION_PLAN.md` P15-A through P15-E and phase dependencies;
   - `docs/implementation/{35_PHASE_ACCEPTANCE_CRITERIA,36_DEPENDENCY_MAP,37_DECISION_LOG,38_PROGRESS_TRACKER,P8_C_INTEGRATION_GATE_REVIEW,P9_C_SAFETY_PRESENTATION_GATE_REVIEW,P13_READINESS_GATE_REVIEW,P14_READINESS_GATE_REVIEW}.md`;
   - `docs/research/r3/{R3_FINAL_TECHNOLOGY_STACK,R3_CODEX_DEPENDENCY_POLICY}.md`;
   - any applicable P10/P11/P12 human-readiness records, and actual repository module/composition paths (`self_care`, `safety`, `clinical_intake`, `consent`, `providers`, `resources`, `ai_orchestration`, `feature_management`). Verify true absence rather than infer from roadmap tables.
4. Ground exact traceability against canonical `FR-SELF-001..017`, `AC-P15-001..010`, global `SAFE-*` (especially `SAFE-008` and `SAFE-009`), privacy/consent/accessibility requirements, and ADRs (especially **ADR-003, ADR-008, ADR-014, ADR-023, ADR-027, ADR-028, ADR-034, ADR-038**). If a document conflicts with an accepted ADR, record the conflict instead of silently changing it. Do not create or supersede an ADR in this PR.
5. Confirm that `docs/27_SECURITY_ARCHITECTURE.md` and `docs/28_THREAT_MODEL.md` are **P11-focused drafts**, not completed whole-platform/P15 security reviews. Do not treat an empty clinical knowledge directory, conceptual schema, a version constant, or synthetic fixture as a reviewed health knowledge source.

## 1 — Deliverable A: `docs/10_SELF_CARE_AYURVEDA_POLICY.md` (NEW)

Create a canonical **unapproved policy-framework draft**, titled **10 — Self-Care and Ayurveda / Gharelu Guidance Policy Framework**. Prominently mark **DRAFT — NO APPROVED REMEDIES, CLINICAL ELIGIBILITY, TREATMENT, MEDICATION ADVICE, PATIENT-FACING GUIDANCE, OR LIVE P15 AUTHORIZATION**. Include evidence baseline SHA, date, unresolved human owners, and as-built-vs-future language. Define **process and architecture only**, never clinical content.

Required topics:

**A. Scope and actual baseline:** distinguish P4 consent/P5 structured context/P7 deterministic non-diagnostic intake, P8 technical extraction, P9 synthetic physical-safety mechanics, P13 draft provider/resource directory, P14 draft mental-health governance, P12 draft languages, P21 draft admin workflow, and empty P15 runtime. Document exactly which trusted capabilities exist, which do not, and why existing general-product/intake consent does not authorize self-care or retrieval of patient data.

**B. Separate governance owners:** define separation among (1) curated content and source provenance, (2) clinician-owned eligibility/safety policy, (3) deterministic personalization/contraindication filters based **only on authorized, trustworthy context**, (4) source-bound explanation/rendering, (5) approvals/maker-checker/audit, and (6) independent verified provider/urgent-care navigation. Admin UI visibility does not authorize clinical content or override clinical decisions.

**C. Future knowledge-pack contract — non-executable, no example remedy:** align to `SelfCareGuidanceDefinition` and the master plan, including pack/manifest identifiers, immutable item ID+version, source/license/reference/category, author/reviewer proof, review state, effective/expiry/supersession/withdrawal, intended population/language/jurisdiction, approved supportive content, context tags, contraindications, validated medication/chronic-condition exclusions, optional age/pregnancy constraints, observation limits and stop/escalation conditions, translations, testing and release records. Preserve strict provenance and no silent version mutation. Distinguish the *conceptual* review states from any *approved* production workflow; none exists now.

**D. Safety and eligibility design:** state the non-negotiable future order: approved **physical-safety determination and active exclusions** -> explicit context completeness/uncertainty -> age/pregnancy where approved and known -> allergies, validated medication/chronic-condition conflicts and other contraindications -> approved, current, applicable knowledge retrieval -> safe source-bound presentation. Unknown, unverified, expired, missing, stale, ambiguous or conflicting clinical inputs **cannot be assumed eligible**. This is an ordering contract, not a rule for any patient. No invented red flags, thresholds, diagnoses, dosages, recipes, treatment instructions, or escalation scripts. P9 live policy/activation remains blocked: therefore P15 cannot label any real patient low-risk or enable self-care.

**E. Retrieval vs final authority:** explain that database, vector indexes, search scores, an LLM, and semantic similarity are **never** eligibility or clinical governance authority. They may discover candidate approved content after authorization and deterministic gating, but must not introduce remedies or overwrite contraindications. Cite approved knowledge ID/version and governing eligibility-policy version in conceptual decision provenance; never treat model memory as the corpus. A missing/failed model, retrieval service, schema, translation, source or governance authorization must not produce a patient remedy.

**F. Future UI/content/translation:** describe required review of supportive, non-curative framing; provenance/version/caveats; mandatory stop/escalation conditions; source and freshness indicators; accessible exclusions and honest unavailable states; approved language equivalence and missing-locale behavior; doctor navigation only through independently verified P13 sources. No actual patient-facing self-care/clinical copy or real Ayurveda example. Generic urgent-help navigation and P7 manual text/touch intake must stay independently usable.

**G. Privacy and lifecycle:** minimize patient context and access scope; define future need for patient/guardian/institution authorization, separate purpose/notice/consent and lawful review, privacy/egress, query/embedding content classification, retention/deletion/revocation, log/trace/index/cache protections, audit without raw narratives, signed reviewer authorization and rollback. Never embed or send patient narrative externally in this phase.

**H. Explicit future test catalogue:** absent/expired/unapproved/superseded guidance; forged source/approval; stale policy; hard safety exclusion; unknown allergy/medication/age/pregnancy; conflicting history; patient-context drift between eligibility and display; revoked consent; wrong subject/institution; prompt injection in retrieved content; LLM invented remedy; unsafe translation; source/DB/vector outage; cache/index stale after revocation; override attempts via flags/admin; inaccessible warning; P7 and urgent-help independence. Name failure expectations conceptually only, not a clinically validated test outcome.

**I. Traceability and conditional phases:** map every `FR-SELF-001..017` and `AC-P15-001..010` to exact canonical wording, draft section, missing human decision, and **LIVE NOT VERIFIED**. Map relevant safety, privacy, accessibility, and P9/P12/P13/P14/P21 dependencies. Distinguish P15-A knowledge pack/contracts, P15-B eligibility, P15-C governance/admin, P15-D patient UI/provider escalation, P15-E regression tests as **future work requiring separate prompts**, not implicit authorization. Final STOP conditions: no clinical/content/source approval, no production source and license, no validated exclusions, no trusted current safety policy, no consent/privacy/legal/security/language/accessible copy, no version/lifecycle or safe fallback, no approved release.

## 2 — Deliverable B: `docs/17_RAG_KNOWLEDGE_SPEC.md` (NEW)

Create **17 — Retrieval-Augmented Knowledge Specification**, prominent **DRAFT — FUTURE DESIGN, NOT AN APPROVED CORPUS, EMBEDDING MODEL, RAG SERVICE OR PATIENT-FACING MEDICAL OUTPUT**. Make it a **platform retrieval design with explicit P15 scope**, not a free-standing model activation. Cover:

1. **As-built and prerequisites.** There is no active P15 retrieval corpus, RAG pipeline, embedding model, pgvector schema, clinical-content ingestion or provider permission. PostgreSQL remains authoritative for transactional/approval data; embeddings/caches/indexes are derived and non-authoritative. Differentiate retrieval of approved self-care knowledge from private patient-document retrieval (P11) and structured clinical queries; they have distinct permissions and cannot share data implicitly.
2. **Accepted R3/ADR architecture.** A narrow project-owned `RetrievalService` and `EmbeddingProvider`, PostgreSQL/pgvector **only when an approved RAG use case activates**, optional independently reviewed `RerankerProvider`. Sentence Transformers is a **candidate** requiring exact revision/license/language/medical benchmark; LangChain/LlamaIndex are **not core dependencies**. Select no actual embedding model, vendor, index metric, cutoff, corpus, chunking algorithm, region, hosting architecture, latency threshold or package in this PR.
3. **Content admission lifecycle.** Source/rights review -> provenance/version -> qualified clinical/content/language review -> explicit approved status and effective interval -> private trusted ingestion -> derived index build with lineage -> controlled visibility -> expiry/withdrawal/revocation/supersession -> reindex/rollback/audit. Document fail-closed queries when source index age/consistency cannot be proven; reindexing does not create clinical approval. No internet scraping or unauthorized dataset import.
4. **Trust and retrieval contract.** Approved corpus, source IDs/versions, language/jurisdiction/population applicability, access filters, approval status, effective date, and expiry date, matching deterministic eligibility decision, minimum-necessary structured context, source evidence, original-language preservation, bounded search/results, abstention/unknown. No embedding search before authoritative eligibility/authorization checks; a similarity hit may not bypass a rule. Define future deterministic post-filter and presentation allowlist independent of any generated text.
5. **Attack and integrity boundaries.** Injected instructions in corpus/docs, malicious metadata/URL, poisoned embeddings, wrong-tenant content, metadata filter bypass, unreviewed translations, stale vector cache, index rebuild race, embedding-model/version drift, content-version substitution, approximate-search false positives, semantic mismatch and fabricated citations. Require tests for both pre- and post-retrieval gating, empty/degraded results, malicious output stripping, and exact provenance binding; never claim an output medically valid merely from a citation.
6. **Privacy/security.** No real patient text, embeddings or restricted knowledge in logs, browser storage, analytics, unrelated model providers, research space or development fixtures. Future embedding/egress/provider terms, authorized roles, record-level and field-level permissions, retention, deletion/backups and query auditing must be explicitly reviewed. Do not assume embeddings are anonymized or make storage/transfer decisions.
7. **Evaluation/operations and rollout conditions.** Future representative multilingual/source-grounded benchmark, source attribution/faithfulness, retrieved-item approval and expiry correctness, false-allow/harmful-content blocking, version drift, unavailable index, model failure, security review, incidents, change-control and rollback. State criteria are **unapproved pending human owners**; CI quality and source matching are not clinical validation.
8. **P15 interface and non-RAG fallback.** First prove deterministic safety eligibility, then allow only approved knowledge variants; ordinary structured approved lookup may be sufficient and vector RAG is optional. No LLM explanation until separately reviewed and validated. On failure, no invented remedy; retain existing P7 text/touch and generic urgent help. List separately authorized future service/data/model steps and STOP triggers.

Ground all statements in current accepted specs, avoid selecting a production product/tool just because research lists it, and make no runtime or medical approval claim.

## 3 — Deliverable C: `docs/implementation/P15_SELF_CARE_RAG_READINESS_GATE_REVIEW.md` (NEW)

Create **an unapproved proposed review inventory**, **NOT an accepted numbered human approval program**. Do not borrow P11's nine-gate count or claim `0/N approved`. Give each review domain an explicit OPEN/BLOCKED descriptive status, actual as-built repository evidence, accountable **roles** (no fabricated names/signatures), unresolved decisions, future artifacts, risks/negative tests, narrowly possible offline work **only if separately authorized**, and STOP conditions. Cover at minimum:

1. Qualified clinical source/content rights, versioned knowledge, Ayurveda/gharelu evidence quality and scope, population/language, independent review and publication/withdrawal.
2. Approved safety gating/eligibility/exclusions, patient-context confidence and drift, P9 hard-safety authority and no unapproved low-risk inference.
3. Contraindication/medication/condition/age/pregnancy rule governance, missing/contradictory context and clinician validation.
4. Knowledge retrieval/RAG architecture, corpus-index provenance, strict source/tenant filters, version/expiry/retraction, benchmarks, injection defense, model/provider/region approval.
5. Purpose-specific privacy/legal/consent, patient/session/guardian/institution identity, minimum-necessary processing, retention/deletion, embedding/egress and audit/incident handling.
6. P15 admin/maker-checker workflow, policy/content separation, reviewer independence, audit, clinical source-change approval, rollback; P21 remains unimplemented.
7. Patient content, translations and accessible states, P12 language dependency, verified P13 provider navigation, no advice on missing approval, independent generic urgent-help/P7 fallback.
8. Validation/regression/operational/clinical release, held-out cases requiring reviewer approval, false-allow analysis, safe-off/staging isolation, monitoring, incident, pilot and production decisions.

Explicitly map `FR-SELF-001..017`, `AC-P15-001..010`, applicable `SAFE-*`, and upstream gates to missing evidence. Include an **unsigned** human decision/evidence template and owner/risk register. P15 implementation remains **NOT STARTED**, live acceptance remains **NOT VERIFIED**; no clinical policy, source or release approval can be signed by Codex.

## 4 — Progress tracker and exact changed-path allowlist

Modify **ONLY these five paths**:

```text
docs/10_SELF_CARE_AYURVEDA_POLICY.md                                  # NEW, UNAPPROVED
docs/17_RAG_KNOWLEDGE_SPEC.md                                          # NEW, UNAPPROVED
docs/implementation/P15_SELF_CARE_RAG_READINESS_GATE_REVIEW.md        # NEW, UNAPPROVED
docs/implementation/38_PROGRESS_TRACKER.md                           # minimal current status and #61
docs/codex/CODEX_PHASE_PROMPTS/PRE_P15_SELF_CARE_AYURVEDA_POLICY_AND_RAG_KNOWLEDGE_READINESS_PACK.md # byte-identical copy of this prompt
```

- In tracker section **Before P15**, change the two missing-document rows to **DRAFT — ACCOUNTABLE CLINICAL/SOURCE/PRIVACY/ARCHITECTURE REVIEW PENDING; NO P15 RUNTIME APPROVAL**. Do not label approved or phase complete.
- Add exactly **`# 61. Pre-P15 Self-Care / Ayurveda Policy and RAG Knowledge Readiness Pack`** including baseline SHA, previous PR #43 merge/tree equivalence, docs, synthetic-vs-production truth, dependencies/requirements, no-approvals status, explicit STOP/next human review; keep older section #60 and historical entries unchanged.
- **Preserve statuses:** P7 manual intake supported; P8-C/P9-C Stage 3 **BLOCKED**; P10 and P11 live **0/9 APPROVED** (P11 5 OPEN/4 BLOCKED); P12/P13/P14/P15/P21 runtime **NOT STARTED**; P13 eight **proposed/unapproved** gates remain 4 OPEN/4 BLOCKED; no official P14/P15 gate counts; accepted ADRs and Alembic `p7a_0007` unchanged; P22 not complete.
- Do not modify package manifests, security-remediation record, lockfiles or CI; Next.js security fix from PR #43 stays intact. Record residual security warnings if relevant, but do not broaden scope.

**Strictly prohibited**: new app/backend/test code, executable clinical policy or pack fixtures, actual remedies, self-care patient copy, diagnoses, dosage/recipe, thresholds, questionnaire content, real human source approvals, provider/helpline contacts, scraping/downloads, embedding/index building, pgvector activation, RAG/LLM/provider integration, API/BFF/UI, ORM/migrations, registration, feature flags, external egress, test shortcuts, security scans altered, infrastructure, dependencies/lockfiles or unrelated changes. If a real clinical decision/source is missing, **record as PENDING; do not infer or choose**.

## 5 — Verification, PR, and handoff

1. Independently compare every requirement ID and exact wording to `01_PRODUCT_REQUIREMENTS.md` and every AC to `35_PHASE_ACCEPTANCE_CRITERIA.md`; audit P9/P12/P13/P14/P21/P22 governance language. Check that no actual advice, patient examples, clinical exclusion thresholds, approvals, model/version/provider selections or invented sources are introduced. Validate all internal Markdown links and section numbers; no repeated tracker heading. Check exact 5-path allowlist, byte-identical recorded prompt, `git diff --check`, no secrets, Alembic and dependencies untouched.
2. Run existing local backend/frontend quality checks, build/test/Playwright checks as feasible and report actual results/retries, without weakening CI. All **six** GitHub jobs must conclude **SUCCESS on the exact final PR head SHA**: Backend quality; Frontend quality; Persistence integration; Docker and PostgreSQL; Playwright Chromium; Security scans. Report existing Trivy/`braces` advisories honestly without changing unrelated dependencies.
3. Commit/push **one new isolated feature branch**, open **one PR** targeting the verified baseline main, and verify local SHA = remote SHA = PR head = CI SHA. **DO NOT MERGE** and do not start P15-A/B/C/D/E runtime. Stop for independent review.

### Required concise completion report

```text
STATUS: COMPLETE PRE-P15 DOCUMENTATION ONLY / PARTIAL / BLOCKED
BRANCH: phase/pre-p15-selfcare-rag-policy-readiness
BASE MAIN SHA: bfba7f5a5993c1572c5ad18b942013a0badc3495
FINAL LOCAL SHA:
FINAL REMOTE SHA:
PR URL / NUMBER:
10 SELF-CARE POLICY — AS-BUILT, UNAPPROVED CLINICAL CONTENT AND P15-A..E:
17 RAG SPEC — AUTHORITY, CORPUS, MODEL/PGVECTOR DEFERRED, ABSTENTION:
P15 READINESS — REVIEW DOMAINS, HUMAN DECISIONS, STOP CONDITIONS:
FR-SELF-001..017 / AC-P15-001..010 / SAFE / DEPENDENCY TRACEABILITY:
PRIVACY/CONSENT / AGE / CONTRAINDICATION / P9 SAFETY / VERSION GUARDS:
UPSTREAM GATES / P15 NOT STARTED:
CHANGED PATHS / ALEMBIC / DEPENDENCIES / UNRELATED CHANGES:
LOCAL TESTS / RETRIES / WARNINGS:
CI RUN ID / EXACT FINAL SHA / SIX JOB CONCLUSIONS:
MERGED: NO
```

**STOP after opening the PR.** This pack supports future human decisions only; it does not authorize patient-facing Ayurveda/gharelu guidance, medication advice, clinical triage, embedding of patient data, a medical RAG model, clinical content publication, pilot, or production release.
