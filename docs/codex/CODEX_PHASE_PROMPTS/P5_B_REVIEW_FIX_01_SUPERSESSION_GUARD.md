# P5-B Review Fix 01 — Enforce Supersession Trust Rules in Persistence

Continue on:
`phase/p5-b-persistence-migrations`

Reviewed head:
`624fd0a4bbe2e8bf304c6929db404af7a7f4c56d`

Do not merge.

## Required fix

`PostgresClinicalFactRepository.persist_supersession()` currently trusts any manually constructed
`FactSupersession`. Because `FactSupersession` itself has no invariant validation, a caller can bypass
the P5-A `supersede_fact()` trust rules and persist a lower-trust replacement over a clinician-confirmed fact.

Fix this so persistence independently fails closed.

Required behavior:
- load the authoritative existing fact from PostgreSQL;
- validate the requested replacement using the canonical P5-A supersession rules before any mutation;
- reject scope/type/terminal/lower-trust/self-ID violations;
- do not trust the supplied `superseded` snapshot as authority;
- only after validation insert the replacement and mark the authoritative existing fact SUPERSEDED;
- preserve atomic rollback.

Add real PostgreSQL tests proving:
1. clinician-confirmed -> EXTRACTED manual/bypassed `FactSupersession` is rejected and DB stays unchanged;
2. mismatched patient/encounter/fact type manual supersession is rejected;
3. valid clinician-confirmed -> clinician-confirmed correction still succeeds;
4. rollback/atomicity regression remains green.

Keep scope narrow:
- no migration/schema/dependency/API/frontend changes;
- Alembic head stays `p5b_0006`;
- all six CI jobs must pass on the new final SHA.

Commit to the same branch, push, do not merge, and return the new SHA + CI run.
