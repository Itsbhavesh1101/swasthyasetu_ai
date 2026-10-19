# SwasthyaSetu AI — P10-A Review Fix 01: Direct Domain Invariants & New-Source Drift

**Work unit:** Narrow review repair for **existing PR #30**, engineering-only P10-A subset. **DO NOT MERGE** until independent re-review.

- **Repo:** `Itsbhavesh1101/swasthyasetu_ai`
- **Branch:** `phase/p10-a-source-backed-summary-domain`
- **PR:** https://github.com/Itsbhavesh1101/swasthyasetu_ai/pull/30
- **Reviewed head:** `7e00afce20dc156b4b4b7f0aaba5aa2e3d0c61fb`
- **Base/main:** `9498972eceaa1ec6c647fd8e4dcb7f2e84748583`
- **Reviewed CI:** run `39308727225`, all six mandatory jobs successful at exact head.
- **Existing Alembic head:** `p7a_0007`, unchanged.
- **Governance:** P10 live clinician access **0/9 approved**; P10-B, sensitive P10-C, P10-D **BLOCKED**; P8-C/P9-C Stage 3 **BLOCKED**. This repair grants no clinical, institutional, or production approval.

## Decision: REVIEW FIX REQUIRED, KEEP PR OPEN

The existing implementation is narrow, inert, synthetic, CI-clean, and separates P5/P7 sources in the **builder**. Nevertheless, some critical output invariants are enforced only in `build_engineering_draft()`, **not** by the public frozen domain constructors; also, the freshness checker can report `CURRENT` when a newly present source is supplied. Fix these narrow issues without expanding scope.

### Finding 1 — `SummarySection` accepts forged trust/readiness states when directly constructed

**Affected:** `backend/app/modules/summaries/domain.py`, `SummarySection.__post_init__`.

Current constructor validates enum membership, per-section count, source section matching, and `review_required` versus conflict flags. It does **not** validate the meaning of `readiness` relative to the supplied assertions. Therefore a direct `SummarySection` can claim `RECORDED` for a P7 patient-reported assertion (or P5 `EXTRACTED`), or claim `NOT_RECORDED`, `UNKNOWN` or `UNAVAILABLE` while actually containing assertions, or mark an empty section `RECORDED`. `ClinicalSummaryDraft` accepts such sections if its reference list matches. The normal builder happens to compute readiness correctly, but a frozen data class is not trustworthy when its own invariants can be bypassed.

**Required repair:** Enforce at the typed domain boundary:

1. For nonempty `assertions`, allow only `RECORDED` **iff all** sources are P5 facts with `CLINICIAN_CONFIRMED`; otherwise require `UNVERIFIED`. (An unresolved conflict may additionally imply review-required, without promoting any claims.) Reject fabricated `NOT_RECORDED`, `UNKNOWN`, or `UNAVAILABLE` for a populated section.
2. For empty `assertions`, allow only `UNKNOWN`, `NOT_RECORDED`, or `UNAVAILABLE`. `NOT_RECORDED` remains an *explicit caller-supplied synthetic coverage claim*, never inferred by the domain from emptiness. The builder must still compute it only from `SourceCoverage.COMPLETE`.
3. Preserve exact typed, bounded, content-free `SummaryValidationError` on inconsistency; never echo labels/IDs. Do not mutate input or grant real clinical authority.

**Regression tests:** Directly instantiate `SummarySection` with a valid P7 assertion and `RECORDED`, a P5 `EXTRACTED` assertion and `RECORDED`, a confirmed P5 assertion and `NOT_RECORDED`/`UNAVAILABLE`/`UNKNOWN`, and empty `RECORDED`/`UNVERIFIED`. Assert typed refusal. Keep builder-produced positive cases (P5 all-confirmed `RECORDED`, mixed P5/P7 or unverified P5 `UNVERIFIED`, empty `UNKNOWN`/`NOT_RECORDED`/`UNAVAILABLE`) green.

### Finding 2 — `ClinicalSummaryDraft` accepts duplicate source or assertion identities when directly constructed

**Affected:** `backend/app/modules/summaries/domain.py`, `ClinicalSummaryDraft.__post_init__` (and optionally `SummarySection`).

The builder's `_validate_input()` rejects duplicate `source_id` and `assertion_id` globally, but the `ClinicalSummaryDraft` domain constructor only checks fixed section order, scope, creatable status, and `source_references == flattened_assertion_sources`. A directly constructed draft with duplicate assertion IDs and/or multiple uses of the same source identity can satisfy this equality and be treated as a valid draft.

**Required repair:** Validate **global** identity uniqueness across all sections in `ClinicalSummaryDraft`, not only inside `build_engineering_draft`, for both `assertion_id` and the exact source-identity policy the builder already enforces. Fail with bounded `DUPLICATE_IDENTITY` and no content echo. Preserve requirement that `source_references` exactly matches canonical assertion order, and that each reference belongs to the same encounter and matching section. Do not add a live source lookup or pretend UUID equality proves authorization. If you choose a composite identity (e.g. kind + source ID), document it and keep builder, domain and freshness checker consistent; changing identity semantics beyond the existing design is **not** required for this repair.

**Regression tests:** Construct a `ClinicalSummaryDraft` *without* calling `build_engineering_draft()` with (a) two distinct assertions sharing an ID and (b) two assertions sharing a source ID but not the assertion ID, within a section and across different sections. Supply a matching `source_references` tuple to ensure only the new invariant rejects these. Verify no fabricated duplicate can be frozen as a valid draft. Preserve builder positive/deterministic fixtures.

### Finding 3 — Newly supplied source can be ignored by the freshness checker

**Affected:** `backend/app/modules/summaries/projection.py`, `_check_source_freshness()`; optionally `domain.py` `SourceDriftReason`.

Current checker indexes all `current.sources`, but iterates only the draft's referenced sources. If `current.sources` contains every unchanged draft source **plus a previously unseen source** with the same `encounter_id` and an unchanged supplied `snapshot_token`, and `conflict_sections` is empty, there is no reason or affected section. It incorrectly reports `CURRENT`. This violates the required handling of newly relevant source data and allows silent omission from a draft. Because `snapshot_token` is only supplied engineering metadata—not a trusted computed hash—the checker must not assume a caller always changes it.

**Required repair:** Treat `CurrentSourceSnapshot.sources` as the complete **relevant scoped source set** for the supplied synthetic comparison (state that contract explicitly). Compare all current source identities against the draft's source identities, not only the other way around. For a newly present, well-typed source in that complete set, mark the relevant `section_id` affected and report **non-CURRENT** (typically `STALE` with a clear bounded reason such as `NEW_SOURCE`, or an existing nonmisleading equivalent). If it is explicitly flagged in `conflict_sections`, retain `REVIEW_REQUIRED` precedence. Do not infer medical contradictions or synthesize a claim from the new source. Reject new sources with the wrong encounter scope, duplicate IDs or malformed shape with a content-free typed failure. Preserve removal/unavailable/rejected/superseded/version-change/snapshot-change behavior and canonical deterministic reason and section order.

**Regression tests:**

- unchanged referenced source + additional same-encounter source (unchanged `snapshot_token`, empty `conflict_sections`) **MUST NOT** return `CURRENT`, and must identify the added source's section;
- added source in a formerly empty section still marks that section affected;
- newly added source plus explicit conflict marks review required;
- a completely unchanged source set still returns `CURRENT`;
- cross-encounter extra source fails closed;
- input ordering does not alter freshness output;
- existing version/deletion/inaccessibility/terminal/conflict cases remain passing.

Do not create a source-content diff, DB query, UI, network call, inferred medical semantics, or new canonical persisted summary status.

## Allowed paths and scope lock

Work only in these existing PR-owned paths as needed:

```text
backend/app/modules/summaries/domain.py
backend/app/modules/summaries/contracts.py                 # only if type contract clarification needed
backend/app/modules/summaries/projection.py
backend/tests/test_summary_domain.py
backend/tests/test_summary_projection.py
backend/tests/test_summary_boundaries.py                   # only if appropriate

docs/03_REPOSITORY_STRUCTURE.md                           # only if inventory meaning changes
docs/implementation/38_PROGRESS_TRACKER.md                # only if precise claim changes
docs/codex/CODEX_PHASE_PROMPTS/P10_A_REVIEW_FIX_01_DOMAIN_INVARIANTS_AND_NEW_SOURCE_DRIFT.md
```

**Forbidden:** P10-B/C/D or clinician live functionality; new summary/patient APIs/BFF/UI; patient/clinician data access; approval/identity/assignment/consent simulation; P5/P7 writes; ORM, migration, SQL, audit/outbox, persistence; third-party providers/AI/LLM; P8-C/P9-C Stage 3 activation, safety routing or self-care; dependencies, lockfiles, CI/security weakening; new clinical words/symptoms/narratives, or any fixture with real patient data. Preserve P10 live approval matrix **0/9** and P10 macro **IN PROGRESS/PARTIAL**, never COMPLETE.

## Execution and verification

1. Confirm branch/PR head is still `7e00afce20dc156b4b4b7f0aaba5aa2e3d0c61fb`, base main is unchanged and worktree clean. Read the P10-A implementation prompt and both canonical P10 specs. On drift stop and report, without resetting user changes.
2. Implement the three findings with the smallest typed changes; keep deterministic behavior, synthetic-only vocabulary, frozen contracts and content-free errors. Add adversarial regressions that **instantiate domain objects directly**, not merely via the builder.
3. Run focused P10-A tests, all network-free backend tests (record skip count), real PostgreSQL suite and Alembic verification (`p7a_0007`), P8/P9 focus, Ruff format/lint, strict mypy, full frontend tests/3 builds, Playwright Chromium, Docker/PostgreSQL/readiness, security/privacy checks, and `git diff --check`. No test disablement/xfail/skip changes.
4. Commit and push the **existing branch** to **existing PR #30**. Verify all six mandatory GitHub Actions jobs (`Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`) succeed on the **new exact final head**. **DO NOT MERGE.**
5. Report final local/remote SHA, PR URL, tests and CI run, precise outcomes for all three findings, Alembic/dependency status, changed paths, and open 0/9 governance approval gates. Stop for independent re-review.

**End state:** PR #30 remains OPEN. Only the inert, nonclinical P10-A engineering subset is potentially mergeable after independent code and exact-head CI review.
