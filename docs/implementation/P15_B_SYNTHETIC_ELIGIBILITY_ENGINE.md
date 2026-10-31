# P15-B - Synthetic Eligibility Engine

**Status:** complete bounded engineering subset; live P15 remains blocked and unapproved.

The detached `self_care` module now contains a pure eligibility-state evaluator for closed,
nonmedical engineering fixtures. It consumes an exact synthetic P9 safety decision, an immutable
P15-A placeholder pack, a closed context snapshot, and a hash-bound compile-time toy policy.

Evaluation is denied in staging, pilot, and production before inputs are inspected. In local/test,
the order is fixed: validate exact safety provenance, preserve every safety block, require synthetic
context completeness, reject conflict, apply exclusions, then produce deterministic placeholder
references. Missing, suspended, invalid, not-yet-effective, or expired policy states fail closed.
Every result binds the exact evaluation, safety decision, knowledge pack, policy, and decision time;
drift in any artifact invalidates reuse.

`SYNTHETIC_ENGINEERING_CANDIDATE` is a toy mechanical outcome only. It is not a clinical eligibility
decision, approved retrieval result, or display authorization. There is no readable guidance,
clinical predicate, patient context, real contraindication, remedy, RAG/model, persistence, API,
admin workflow, UI, dependency, or runtime registration. All live P15 criteria remain unverified.
