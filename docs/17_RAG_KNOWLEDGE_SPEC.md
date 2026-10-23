# 17 — Retrieval-Augmented Knowledge Specification

> **DRAFT — FUTURE DESIGN, NOT AN APPROVED CORPUS, EMBEDDING MODEL, RAG SERVICE OR PATIENT-FACING MEDICAL OUTPUT**

| Evidence field | Value |
|---|---|
| Repository baseline | `main` at `bfba7f5a5993c1572c5ad18b942013a0badc3495` |
| Evidence date | 2026-10-23 |
| P15 status | **NOT STARTED** |
| Selection status | No corpus, model, provider, index design, threshold, package, region, or runtime is selected |

This is a platform retrieval design with an explicit P15 boundary. It is subordinate to the [master specification](00_PROJECT_MASTER_SPEC.md), [architecture](02_SYSTEM_ARCHITECTURE.md), [self-care policy framework](10_SELF_CARE_AYURVEDA_POLICY.md), [privacy specification](26_PRIVACY_CONSENT_SPEC.md), accepted ADRs in the [decision log](implementation/37_DECISION_LOG.md), and accountable human decisions. It grants no medical, privacy, security, content, vendor, pilot, or production approval.

## 1. As-built state and prerequisites

The repository has no active P15 retrieval corpus, RAG pipeline, embedding model, pgvector schema, clinical-content ingestion process, reranker, or provider permission. The `self_care`, clinical knowledge, and self-care policy paths are placeholders. No P15 service is registered and no P15 API or UI exists.

PostgreSQL remains authoritative for future transactional approval, source/version, authorization, and lifecycle data. Embeddings, vector indexes, caches, lexical indexes, and search projections are derived, rebuildable, non-authoritative views. An index hit can never establish source approval, consent, eligibility, or clinical truth.

Three retrieval classes must remain distinct:

| Class | Authority and permission boundary |
|---|---|
| Approved self-care knowledge | Future curated, licensed, versioned P15 content; only after P15 authorization and deterministic eligibility |
| Private patient documents | P11-owned source access and document permissions; no implicit admission to a shared corpus or P15 use |
| Structured clinical queries | Authoritative structured records and purpose-scoped access; not automatically converted into embeddings or free-text retrieval |

Data, consent, indexes, access decisions, and caches cannot be shared among these classes merely because they use a common database or retrieval interface. P11/P15 cross-use requires its own approved purpose, ownership, isolation, retention, and deletion design.

## 2. Accepted architecture and deliberately deferred choices

Consistent with R3, ADR-008, ADR-034, and ADR-038, future implementation should expose a narrow project-owned `RetrievalService` and `EmbeddingProvider`. PostgreSQL/pgvector may be activated only when an approved RAG use case requires vector retrieval. An optional `RerankerProvider` requires independent review and must remain replaceable.

Sentence Transformers is only a candidate. Any future choice requires an exact revision, license and redistribution review, supported-language evidence, medical-domain benchmark, security review, hosting/egress decision, resource profile, and reproducibility evidence. LangChain and LlamaIndex are not core dependencies. Haystack or any other orchestration product would require a later justified decision; none is selected here.

This specification intentionally does **not** select an embedding model, vendor, index metric, search cutoff, corpus, chunking algorithm, region, hosting architecture, latency target, or package. It adds no dependency and activates no pgvector extension. Research mentions are candidates, not authorization.

### 2.1 Conceptual narrow interfaces

A future retrieval request must carry an authorized purpose; subject/tenant scope where applicable; approved corpus and language/jurisdiction scope; authoritative eligibility decision ID/version; content-version constraints; bounded query representation; and result limit. A future result must return only immutable item/source/version identifiers, approved evidence spans or fields, applicability metadata, retrieval lineage, and non-authoritative scores.

The service contract must support abstention with machine-readable reasons. It must not expose unrestricted generated prose as an authoritative result. Interface details remain future design, not executable contracts in this phase.

## 3. Content admission and withdrawal lifecycle

Future corpus admission must proceed in this order:

1. source identity, rights, license, jurisdiction, and intended-use review;
2. immutable provenance and content version assignment;
3. qualified clinical/content and language review with independent evidence;
4. explicit approved state and effective interval through an approved workflow;
5. private, integrity-checked ingestion into the trusted source store;
6. derived index build with source/version/model/configuration lineage;
7. controlled visibility after consistency and authorization proof;
8. expiry, withdrawal, revocation, rejection, or supersession enforcement;
9. reindex, cache invalidation, rollback, reconciliation, and immutable audit.

Reindexing cannot create or extend clinical approval. Internet scraping, implicit crawling, unauthorized datasets, public uploads, and unreviewed translations are prohibited. A source change produces a new immutable version and new review; it must not mutate an approved version in place.

At query time, the service must prove authoritative source state and that each derived index generation is current for that state. Unknown index age, missing lineage, incomplete invalidation, or source/index inconsistency forces fail-closed abstention until reconciliation. Withdrawal must suppress ordinary retrieval immediately at the authoritative filter even if background deletion is incomplete.

## 4. Trust and retrieval contract

Retrieval is permitted only after subject/actor/institution authorization, purpose validation, and authoritative deterministic safety eligibility. The request must minimize context and bind:

- approved corpus and exact source/item versions;
- language, jurisdiction, and intended population applicability;
- tenant/subject and role/field access filters;
- approved/effective/not-expired/not-withdrawn lifecycle state;
- matching eligibility-decision and policy versions;
- minimum-necessary structured context with provenance and freshness;
- bounded query, result count, and processing time;
- original-language evidence and translation lineage.

No embedding search may occur before authoritative authorization and eligibility checks. Similarity, lexical rank, reranking, or generated text cannot bypass a rule or expand the approved population. Retrieval must abstain on missing, ambiguous, stale, conflicting, or unsupported context.

After retrieval, an independent deterministic post-filter must recheck authorization, lifecycle, applicability, exact source/version lineage, eligibility binding, and presentation allowlist. Presentation may use only approved fields from the selected item; any generated text remains disallowed until separately reviewed and validated. A citation is provenance evidence, not proof that an output is medically valid.

## 5. Attack and integrity boundaries

Corpus text and metadata are untrusted inputs even after source admission. Future threat modeling and adversarial validation must cover:

- instructions embedded in corpus text, source files, metadata, or translated fields;
- malicious URLs, markup, control characters, hidden text, or metadata structures;
- poisoned or substituted embeddings and wrong-model index generations;
- wrong-tenant, wrong-subject, or wrong-corpus content and filter bypass;
- unreviewed translation or source-language substitution;
- stale vector/lexical caches following expiry, withdrawal, or consent revocation;
- index rebuild races and mixed source/index generations;
- embedding model, tokenizer, configuration, or version drift;
- content-version substitution and fabricated or mismatched citations;
- approximate-search false positives and semantic mismatch;
- output that invents, combines, expands, or contradicts approved content.

Tests must exercise authorization and deterministic gating both before and after retrieval, including empty/degraded results, malicious-output stripping, exact provenance binding, race conditions, and rollback. Retrieved instructions must be treated as data and must never alter the system’s authority hierarchy.

Integrity evidence should bind source bytes, item/version, admission decision, index generation, embedding configuration, query-policy version, eligibility decision, post-filter result, and presentation version. Any broken binding results in abstention.

## 6. Privacy and security

Real patient text, queries, embeddings, restricted knowledge, or derived sensitive attributes must not enter logs, traces, metrics, analytics, browser storage, URLs, unrelated model providers, research workspaces, or development fixtures. Embeddings are not presumed anonymous, de-identified, harmless, or freely transferable.

Before any implementation, accountable reviewers must decide:

- processing purpose, notice, consent and/or other applicable lawful requirements;
- patient, guardian, institution, actor, and service authority;
- corpus and query data classification and minimum necessary fields;
- record- and field-level permissions and tenant isolation;
- local/provider execution, region, egress, contractual terms, subprocessors, and key ownership;
- encryption, secret management, network boundaries, abuse limits, and incident handling;
- source, query, embedding, index, cache, audit, backup, and deletion retention;
- withdrawal/revocation propagation and proof of deletion or lawful retention;
- query audit that is useful without retaining raw narratives.

There is no authorization in this phase to embed, persist, transfer, or process patient narrative. Future fixtures must be synthetic, clearly labeled, isolated, and incapable of production activation.

## 7. Evaluation, operations, and rollout conditions

Accountable owners must approve a representative held-out benchmark before runtime. It must address intended languages, sources, jurisdictions, and populations; source attribution and faithfulness; approval/expiry correctness; false allow and harmful-content blocking; retrieval/post-filter disagreement; version/model/index drift; unavailable dependencies; injection and isolation; accessibility; latency/resource bounds; and reproducibility.

Operational evidence must cover deterministic builds, signed manifests, index freshness and reconciliation, health without sensitive data, abuse and capacity limits, incident playbooks, source/model/configuration change control, rollback, backup/restore, and withdrawal drills. Thresholds and release criteria remain unapproved pending qualified owners. CI success, matching a source, or a good similarity score is not clinical validation.

Rollout requires separately signed security, privacy/legal, source-rights, clinical/content, language/accessibility, operations, architecture/data, and institutional decisions. Staging must be isolated and safe-off. Pilot and production are distinct decisions and cannot be inferred from documentation or an engineering demo.

## 8. P15 interface and non-RAG fallback

P15 must first prove an approved deterministic physical-safety and eligibility result. Only then may it retrieve approved, current variants whose population, language, jurisdiction, and version match that result. Structured approved lookup should be preferred where sufficient; vector RAG is optional. No LLM explanation is allowed until it has separate source-bound design, evaluation, privacy/security review, and approval.

On a missing authorization, failed eligibility gate, empty result, expired source, inconsistent index, model/provider failure, unapproved locale, or any uncertain binding, the result is abstention—never an invented remedy. P7 manual text/touch intake and generic urgent-help navigation remain independently available. P13 provider information may appear only from a separately verified, current source.

### 8.1 Separately authorized future steps

Each requires its own prompt and approval evidence: authoritative source store and schema; content admission and withdrawal workflow; access-control and consent integration; embedding/provider selection; pgvector migration; deterministic indexing; retrieval/post-filter service; multilingual benchmark; attack evaluation; source-bound presentation; monitoring and incident controls; staged release and rollback.

### 8.2 STOP triggers

Stop before retrieval or presentation when any approval, authorization, context, source/version, lifecycle, eligibility, tenant filter, index lineage, language evidence, provider permission, privacy/egress decision, benchmark, safe fallback, or rollback proof is missing, stale, ambiguous, inconsistent, or revoked. Stop if any implementation would weaken P7, P8-C, P9-C, P10, P11, P12, P13, P14, P21, privacy, safety, or accepted ADR restrictions.

P15 remains **NOT STARTED** and live acceptance remains **NOT VERIFIED**.
