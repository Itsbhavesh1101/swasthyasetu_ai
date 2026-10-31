# P15-A Synthetic Knowledge Schema - Design

## Decision

Implement a detached `self_care` contract and mapping loader for engineering-only knowledge-pack
placeholders. Application code may represent only fixed nonmedical tokens and a single
`TEST_ONLY_UNAPPROVED` state; it cannot represent guidance prose, a remedy, a source claim, clinical
eligibility, or publication approval.

## Approaches considered

1. **Strict synthetic schema and in-memory mapping loader — selected.** This exercises versioning,
   deterministic hashing, exact-field parsing, immutable manifests, and pack extensibility without
   content or runtime activation.
2. Generic predicate eligibility engine — deferred because P15-B requires approved safety/context
   authority and would risk inventing exclusion semantics.
3. Database-backed knowledge store or vector index — rejected because source governance, schema,
   retrieval need, dependencies, retention, and release authority are unresolved.

## Contracts and integrity

- A pack binds contract/schema/pack versions, test-only state, canonical UTC creation time, ordered
  items, and all item metadata through a SHA-256 content hash.
- Items contain only closed synthetic identity, placeholder, source, and tag tokens. No free text,
  URI, clinical category, score, threshold, contraindication, escalation, or translation exists.
- Constructors and parser revalidate nested values, ordering, uniqueness, limits, chronology, and
  exact fields. Errors are stable and content-free.
- The module has no registry capability, API, persistence, file/network loader, or application import.

## Non-goals

No approved knowledge, remedy/advice, real source, rights decision, content publication, eligibility,
patient context, safety integration, RAG/vector search, model/provider, admin review, UI, database,
migration, dependency, feature flag, event/job, or runtime activation.
