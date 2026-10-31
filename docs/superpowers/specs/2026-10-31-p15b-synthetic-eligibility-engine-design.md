# P15-B Synthetic Eligibility Engine Design

## Intent

Build the narrow P15-B engineering subset permitted by the P15 readiness review: a detached,
deterministic eligibility-state evaluator using only unmistakably synthetic, nonmedical fixtures.
It proves fail-closed ordering and provenance mechanics without claiming that any person is safe or
eligible for self-care.

## Constraints

- Consume only the existing P9 engineering-only physical-safety decision and P15-A synthetic pack.
- Deny staging, pilot, and production environments before evaluation.
- Keep every fixture closed, content-free, bounded, immutable, and hash/version bound.
- Do not add clinical predicates, remedies, thresholds, patient context, retrieval, persistence,
  migrations, APIs, UI, dependencies, feature flags, module registration, or runtime activation.
- Preserve every P8-C, P9-C, P10, P11, and live P15 governance restriction.

## Approaches considered

1. Add a runtime eligibility service and API. Rejected because the live P9 and P15 gates are blocked.
2. Build a generic plugin/rule language. Rejected because it increases attack surface and could be
   mistaken for clinical configuration authority.
3. Use a compile-time, closed synthetic policy with a pure detached evaluator. Selected because it
   exercises the required mechanics while remaining impossible to populate with real clinical data.

## Design

`eligibility.py` owns immutable evaluation, policy, rule, candidate-reference, and result contracts.
All identifiers and predicates use a closed alpha/beta/gamma/delta engineering vocabulary. Policy
and evaluation fingerprints cover every relevant field. Result validation reconstructs nested
objects and binds the exact evaluation, safety decision, knowledge-pack hash, and policy hash.

`synthetic_eligibility.py` owns one compile-time policy fixture whose trusted digest is pinned. It
maps only synthetic include/exclude tokens to P15-A placeholder identities; it contains no readable
content or clinical meaning.

The evaluator applies this order:

1. reject protected environments and malformed inputs;
2. verify exact engineering-only P9 safety provenance;
3. block any safety decision other than the exact synthetic supported-self-care result;
4. require an explicit synthetic completeness token and reject conflicts;
5. apply closed synthetic exclusions before include matches;
6. emit zero or more placeholder references in deterministic order.

Expected uncertainty becomes a fail-closed result (`SYNTHETIC_BLOCKED` or
`SYNTHETIC_CLARIFICATION_REQUIRED`), not an exception. Contract corruption and identity drift raise
stable, content-free errors. `SYNTHETIC_ENGINEERING_CANDIDATE` means only that toy mechanics matched;
it is not approval, retrieval, display authority, or live AC-P15 acceptance.

## Verification

Tests cover direct constructors, protected environments, safety precedence, malformed or forged
safety provenance, missing/comflicting context, exclusion precedence, deterministic matching,
missing/invalid/suspended/expired policy, policy-pack mismatch, hash mutation, clock validation,
context/safety/pack/policy drift, and absence of runtime registration or readable guidance.

## Non-goals

No clinical eligibility, contraindication set, allergy/medication/condition interpretation, age or
pregnancy rules, approved content, RAG, vector store, LLM, admin review, patient display, provider
navigation, consent processing, database, API, event/job, telemetry payload, or production feature.
