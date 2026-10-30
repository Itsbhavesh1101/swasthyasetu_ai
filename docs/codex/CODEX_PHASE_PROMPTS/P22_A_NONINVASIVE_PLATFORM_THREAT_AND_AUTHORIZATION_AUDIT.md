# CODEX IMPLEMENTATION PROMPT — P22-A Non-Invasive Platform Threat & Authorization Audit

**Project:** SwasthyaSetu AI  
**Task classification:** P22-A **bounded engineering audit + synthetic security-regression tests**, not a production control implementation or clinical release.  
**Repository:** `https://github.com/Itsbhavesh1101/swasthyasetu_ai`  
**Expected exact base:** `main @ 55cbcc9c0ea4680366302919dbacd0240f6a5c5f` (independently checked 30 Oct 2026).  
**Proposed branch:** `phase/p22-a-noninvasive-threat-authz-audit`  
**Prompt to commit verbatim at:** `docs/codex/CODEX_PHASE_PROMPTS/P22_A_NONINVASIVE_PLATFORM_THREAT_AND_AUTHORIZATION_AUDIT.md`  
**Decision boundary:** The project tracker §68 and `P22_READINESS_GATE_REVIEW.md` allow only a **new, separately scoped P22-A non-invasive audit**. This prompt provides that narrow engineering authorization; it does **not** confer institutional, AppSec, legal, privacy, clinical, production, or pilot approval.

## 0. STOP FIRST — exact repository, branch, prompt, and authorization boundary

1. Confirm the GitHub `main` HEAD is exactly `55cbcc9c0ea4680366302919dbacd0240f6a5c5f`. If newer, **STOP `BLOCKED`**, give both SHAs, and request prompt re-baselining. Never silently rebase or pull a changed main into this task.
2. Confirm this prompt exists as an unchanged file at the exact path above in the user's worktree. If there are pre-existing edits, preserve them; do **not** delete/reset/stash somebody else's work. Make a clean, isolated **git worktree** rooted at the verified base SHA. Use the proposed branch if free; if occupied, STOP and report the conflict instead of overwriting it. Check `git status --short` before and after.
3. In the isolated worktree, copy/commit this prompt file **byte-for-byte** and only make the changes expressly permitted below. If copied prompt bytes differ from the supplied file, STOP and report. Do not auto-update the prompt or alter its instructions.
4. Confirm the current repository has no unreviewed open PR that overlaps these paths. If conflict, STOP with facts. Never merge PRs yourself.
5. Operate strictly with fabricated/synthetic test subjects, fake session tokens and local/test PostgreSQL. No real patient, user, clinician, institution, production system, external security scanning of a deployed target, vendor, egress, or credentials. No interactive penetration attack, brute-force, traffic flood, exploit campaign, or real-data log collection.

## 1. Mandatory read-first context and precedence

Read the actual files **at the pinned base**, not an older handoff snapshot. Record any discrepancy, conflicting decision, or hard STOP:

- `docs/00_PROJECT_MASTER_SPEC.md`; `docs/01_PRODUCT_REQUIREMENTS.md`; `docs/02_SYSTEM_ARCHITECTURE.md`; `docs/26_PRIVACY_CONSENT_SPEC.md`.
- `docs/29_ENGINEERING_STANDARDS.md`; `docs/34_MASTER_IMPLEMENTATION_PLAN.md`, particularly **P22 (§30)**, P23 (§31), master STOP/governance rules.
- `docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md` (**AC-P22-001..011**); `docs/implementation/36_DEPENDENCY_MAP.md`; `docs/implementation/37_DECISION_LOG.md` (accepted ADRs); `docs/implementation/38_PROGRESS_TRACKER.md` (especially **§68–70** and P22/P23/P24 rows).
- `docs/implementation/P22_PLATFORM_SECURITY_PRIVACY_GAP_ASSESSMENT.md`; `docs/implementation/P22_READINESS_GATE_REVIEW.md` (especially final STOP and owner roles); `docs/implementation/P23_READINESS_GATE_REVIEW.md`; `docs/implementation/P24_READINESS_GATE_REVIEW.md`.
- `docs/27_SECURITY_ARCHITECTURE.md` and `docs/28_THREAT_MODEL.md` **as P11-only unsigned drafts**, not platform approvals; `docs/30_TESTING_STRATEGY.md` if present.
- `docs/codex/CODEX_INSTRUCTIONS.md`; `docs/codex/CODEX_CONTEXT_RULES.md`; `docs/codex/CODEX_WORKFLOW.md`; `.github/workflows/ci.yml`.
- Actual implementations: FastAPI `backend/app/main.py`, session, identity, consent, encounter, clinical-intake API/application and repository layers; `backend/app/api/security/` and middleware; relevant patient-web BFF/session storage and browser boundaries for **read-only inventory**.
- Existing security/regression tests, especially:
  `backend/tests/test_identity.py`, `backend/tests/test_actor_context.py`, `backend/tests/test_request_context.py`, `backend/tests/integration/test_postgres_sessions.py`, `backend/tests/integration/test_postgres_consent.py`, `backend/tests/integration/test_postgres_clinical_intake_api.py`, `backend/tests/integration/test_postgres_p5c.py`, and `tests/e2e/patient.spec.ts`.

**Source precedence:** approved clinical/safety sources and canonical requirements > accepted ADRs and module-owned contracts > tracked as-built implementation/evidence > Pre-P22/23/24 unsigned reviews > this prompt. A missing approval or absent feature stays absent. Do not “resolve” conflicts by inventing policy. In the final report distinguish **as-built/verified**, **proposed/unapproved**, **absent**, **unknown**, and **human decision pending**.

## 2. Why this specific unit is eligible; strict scope

P0–P7 are bounded technical foundations; P8–P11 are partial; P12–P24 runtime is not generally authorized. Pre-P22/23/24 packs are documentation only. There are no recorded qualified owner signoffs, P8/P9 real-patient Stage 3 is blocked, P10/P11 live 0/9, P23 live acceptance is unverified and no P24 release/pilot decision exists. **P22-A is the narrowest previously identified safe next work**: inventory current attack surface and prove or surface gaps in *existing* self-session/object/consent boundaries without deploying or changing those boundaries.

**In scope:**

- Read-only source inspection of **current** trust zones, endpoints, identity/authorization and consent; an auditable platform-wide threat/asset/authority register with explicit unknowns and human decision needs.
- Exactly bounded additional **synthetic, local/test PostgreSQL HTTP authorization regression tests** for current P4–P7 behavior. Test existing implementation; do not implement new controls.
- Accurate evidence/coverage linkage to `AC-P22-001` (threat-model **draft**, not signed/accepted), `AC-P22-002` (bounded current-object authorization tests, not comprehensive live approval), plus traceable unresolved status for `AC-P22-003..011`.
- A minimal tracker update that reflects **only** completed bounded audit/testing work and leaves clinical/security/release approval clearly unverified.

**Out of scope — ABSOLUTE:**

- No application code, frontend UI/BFF code, routes, API contracts, database schema/Alembic, production config, feature flags, migrations, dependencies/lockfiles, Docker, workflows/CI definitions, secret policies, rate limits, CSP/CORS/CSRF enforcement, identity provider/MFA, clinician/admin permission upgrades, provider/resources, retention/deletion/hold jobs, external AI/OCR/speech/LLM, FHIR/ABDM, model/RAG/QML work, deployment, observability exporter, tests involving real data, runtime changes or production remediation.
- No P22-B/C/D/E, P23-A/B/C/D, P24 pilot, new P25, or clinical activation. No new official signers, findings severity, signed dispositions, legal determinations, approved scope, retention durations, benchmark outcomes or “security certified” conclusions.
- No modification of existing `docs/27_SECURITY_ARCHITECTURE.md` or `docs/28_THREAT_MODEL.md`; preserve their P11 history. Do not create missing global Specs 31/32.

## 3. Exact file allowlist — four paths, one existing test file

Allow **only** these tracked file changes:

1. `backend/tests/integration/test_postgres_clinical_intake_api.py` — append narrowly focused test(s) using the existing real-Postgres `intake_client`, `_onboard`, `_start`, and `_answer_request` helpers. Do **not** change existing assertions or fixtures unless strictly necessary to avoid shared-state failures; if unavoidable, STOP rather than touching another file.
2. `docs/implementation/P22_A_PLATFORM_THREAT_AND_AUTHORIZATION_AUDIT.md` — **new** evidence-based unsigned technical audit report.
3. `docs/implementation/38_PROGRESS_TRACKER.md` — add a self-contained chronological **§71. P22-A Non-Invasive Platform Threat and Authorization Audit — Bounded Technical Evidence**, with exact status, scope, hashes/results, and STOP. Update P22 phase row only if justified by the tested result, and mark at most **PARTIAL**. Preserve §68–70 and all prior history exactly.
4. `docs/codex/CODEX_PHASE_PROMPTS/P22_A_NONINVASIVE_PLATFORM_THREAT_AND_AUTHORIZATION_AUDIT.md` — byte-identical prompt committed verbatim.

No other tracked changes. Do not modify any pre-existing tests merely to make new tests pass, and never update snapshots/expected errors to hide a security finding. Untracked transient test reports, virtualenvs and outputs must not appear in the commit. One focused feature commit is preferred.

## 4. Read-only threat and authorization inventory deliverable

Create `P22_A_PLATFORM_THREAT_AND_AUTHORIZATION_AUDIT.md` with the following **specific sections**:

1. **Purpose, as-of revision, status and evidence tier:** exact baseline commit, date, P22-A *technical-audit scope only*, unsigned/no institutional approval; explicit distinction from Pre-P22 prose and from the P11-only threat draft.
2. **As-built asset/data-flow/trust-zone map:** patient browser/cache → BFF → FastAPI → sessions/identity/consent → PostgreSQL/outbox; current P7 intake; inactive/absent clinician/admin/API/external/worker/storage/model/interop/research/deployment boundaries. Cite actual repository file paths, contracts and test paths **per row**. Separate data classifications (credentials/session bearer, consent metadata, structured clinical narrative, raw docs, extracted candidates, audit traces) and point out where future collection *does not* exist. Do not diagram future architecture as deployed.
3. **Current API attack surface and authority matrix:** each implemented current P4–P7 route group, available auth material (pseudonymous bearer vs trusted actor context), subject and object ownership checks, relevant consent purpose+scope, mutable operation, expected denial and tests present/missing. Include “institution assignment”, “clinician MFA”, “production IdP”, and “research purpose” as **unapproved/absent**, not working controls. Cross-reference the actual route functions and enforcement points; avoid misleadingly blanket labels.
4. **Threat/control-gap table:** at minimum stolen/missing/invalid bearer, cross-session IDOR (encounter/intake/consent/session), forged actor/role/MFA headers, revoked consent, closed/expired session, guessed object identifiers, malformed/hostile schema, BFF cookie/storage/error leaks, stale/versioned writes, and optional-AI/outbox/logging/worker risk. Use STRIDE-like categories only as a descriptive convention, not as a substitute for proof. Each row must say *evidence*, *actual behavior*, *missing proof*, *owner class*, *proposed separate mitigation (if any, UNAPPROVED)*, *remaining risk/unknown*, and *STOP*. **No invented CVSS/severity scores**.
5. **Test/evidence matrix:** every newly added test name and existing relevant test name, fixture isolation, actual command and result (only if run), targeted operation/expected denial, database non-mutation check, privacy/error envelope assertions, any failure/reproduction ID, and limits. If no local PostgreSQL available, mark not run and rely only on explicitly verified exact-SHA CI evidence later.
6. **Acceptance traceability:** AC-P22-001..011 with *exact canonical text*, present technical evidence vs missing live acceptance, and human approval needs. State explicitly that all **LIVE P22 AC** remain unverified until qualified review. Further note P23/P24 remain NOT STARTED and unauthorised for release/pilot.
7. **Unsigned owner decision docket:** identity/institution, AppSec, privacy/consent, data governance, clinical, platform/SRE, independent reviewer; deployment topology, issuer trust, privileged actor proofing, purpose/recipient data authority, risk rubric and disposition, time-bound review. All signatures and decisions **PENDING**, no fictional names.
8. **Residual risks, next separated steps, and final STOP:** actionable ranked *owner-review questions* (not arbitrary technical severity), P22-B–E requests requiring new independent authorization, P7 deterministic/manual unaffected, no pilot/clinical permission.

Review exact docs and tests; do not misstate what they prove. Update current diagrams/tables in this **new** report only, no modification of canonical baseline specs.

## 5. One narrow new authorization regression suite — actual implementation in this task

Inside **only** `backend/tests/integration/test_postgres_clinical_intake_api.py`, using the existing test database fixture and API helpers, add a focused test or concise parameterized tests covering *gaps* not already asserted by the existing tests. **Before adding, enumerate the existing tests and avoid duplicate cases**; if every candidate is already covered, add only an independently useful non-mutation/security assertion, or STOP with evidence that no distinct allowed change can be safely made.

Mandatory scenario if the actual code supports it:

- Create two independent **synthetic PSEUDONYMOUS sessions**, with their own scoped `GENERAL_PRODUCT_USE`/`clinical_intake` consents and encounters. For **session A's valid encounter before intake creation**, attempt `POST /api/v1/encounters/{encounter_A}/intake` as **session B**. This cross-object **start authorization** is not covered by the existing per-intake cross-session read/answer/complete test. Assert documented **deny** result (prefer the exact contract; never relax to a permissive success code). Check `Cache-Control: no-store`, safe error shape, no token or synthetic narrative reflected, and query the **real test database** to prove **no new intake/questionnaire/answer records** appeared for A. Then have A legitimately start and read its own intake to prove the allowed path remains usable.
- If supported by exact as-built routes, extend this same test minimally to session B attempts to read and mutate **session A's encounter** (`GET /api/v1/encounters/{id}` and a supported terminal transition). Assert refusal and **no state/version change**, and ensure A may still perform permitted actions after rejection. Do not perform a real mutation as B and don't assume denial status text; inspect current contracts. If doing so requires additional nonallowlisted changes, document untested instead of proceeding.
- Check missing/invalid bearer and forged `X-Actor-ID`/`X-Roles`/`X-MFA-Verified`-style headers (or actual known trusted-context spoof vectors from as-built code) **only where those headers are not authentication authority**; assert they cannot authorize any protected existing P7 operations. Do not guess that a header is processed; record inspected behavior. Do not assert a fabricated attack route or guessed role-based privilege semantics.
- Prove unauthorized request(s) do not leak raw bearer/token or synthetic sensitive marker into error response body or relevant test logger capture; ensure unauthorized responses are non-cacheable. Do not assert identical HTTP status for unknown IDs versus cross-subject requests unless canonical contract requires it; document any enumeration concern as owner-review gap.
- If there is an already-covered scenario (e.g., consent revoke or cross-intake access), reference the existing test by its real name and **do not** duplicate it. Keep direct write APIs, mutations, migrations and fixture source intact.

All tests must run against **a dedicated disposable PostgreSQL test database** selected by existing `SWASTHYASETU_TEST_DATABASE_URL` fixture: the fixture itself truncates tables. **Never run against a production, staging, shared or unclear database.** If no provably disposable test DB is available, don't set an arbitrary URL or invoke destructive fixtures; mark PostgreSQL local tests NOT RUN and let exact-feature-SHA CI run the existing controlled PostgreSQL job. Standard pytest `postgres` marker applies. Use only deterministic artificial cases; never real data.

If these tests expose an actual authorization/privacy regression, **do not fix application code under this prompt**, do not weaken the test, and do not misstate success. Return `BLOCKED` with sanitized reproduction steps (no bearer, token or patient data), affected path, observable result, and recommended separately authorized P22-B remediation. Do not push/PR on a failing security regression without explicit new instruction.

## 6. Verification and security gates

In the isolated worktree:

1. Audit exact diff, tracked paths, source status, all newly added assertions and fixture isolation. Verify the prompt bytes against the supplied original if obtainable. Refuse unauthorized file changes.
2. Run appropriate locally available formatting/lint/type checks and **targeted** pytest tests. Run a full local backend unit suite and, only when a provably isolated disposable PostgreSQL test DB is available, the real Postgres integration tests. Do not make up results for unavailable dependencies.
3. Run the repository's approved **Gitleaks** procedure with actual exit status. Do not mask or suppress warnings, rewrite scanner policies, or alter secrets. Check git diff for token/PHI/canary contents. No real secrets in docs/test fixtures or logs.
4. Existing canonical CI includes **six named jobs**: Backend quality; Frontend quality; Persistence integration; Docker and PostgreSQL; Playwright Chromium; Security scans. Commit, push only this isolated branch and open a **draft-or-normal PR without merging** after testable local checks succeed. Verify all six jobs at the **exact final feature-head SHA**. If any job is pending, report `PARTIAL` / review pending; never claim `COMPLETE` or merge approval. If a required job fails, return `BLOCKED` (with link/run ID) and do not ask user to merge.
5. No extra tracked files, no CI modifications, no force-push and no access/approval changes. If GitHub permissions or tooling prevent CI inspection, report what is unknown; do not infer success from a local run. The assistant will independently review diff/CI before user manually merges.

## 7. Tracker rules and final result

The tracker addendum §71 must clearly distinguish **P22-A bounded technical audit/test evidence** from **P22 full acceptance**. Do not label P22-A fully signed/complete, do not reclassify Pre-P22 as a completed runtime phase, and do not mark any live `AC-P22-001..011` verified based on a draft or synthetic test. The P22 top-level row may become `PARTIAL` **only** if the new bounded audit and tests are actually delivered and pass; include explicit “P22-B/C/D/E NOT STARTED, P22 LIVE AC unverified, independent owner signoff pending.” Otherwise leave `NOT STARTED` and explain the blocked unit. Never change P23/P24 status or release decision.

**Report exactly:**

```text
STATUS: COMPLETE (bounded P22-A technical task only) / PARTIAL / BLOCKED / FAILED
BRANCH:
BASE MAIN SHA:
FINAL LOCAL SHA:
FINAL REMOTE SHA:
PR URL / NUMBER: OPEN, NOT MERGED (or reason absent)
FOUR FILE ALLOWLIST: PASS / FAIL (names + diff stat)
PROMPT BYTE IDENTITY: PASS / FAIL / UNVERIFIABLE
THREAT/AUTHORIZATION EVIDENCE: [source-backed summary and undecided owner gates]
NEW TESTS + SCENARIOS:
EXISTING TESTS REUSED (NOT DUPLICATED):
TARGETED TESTS:
LOCAL BACKEND:
REAL POSTGRES (dedicated disposable test DB only):
FRONTEND / PLAYWRIGHT / DOCKER (as run):
GITLEAKS:
SIX CI JOBS AT EXACT FEATURE SHA: [individual statuses, link/run ID]
AC-P22-001..011 LIVE: NOT VERIFIED
P22-B/C/D/E, P23, P24: NOT STARTED / BLOCKED
HUMAN APPROVALS / PILOT: NONE
NEW DEPENDENCIES / MIGRATIONS / RUNTIME CHANGES: NONE
FINDINGS / UNRESOLVED RISKS / REPRODUCTION IDs:
NEXT MANUAL ACTION: independent ChatGPT PR and CI review; user merges only after approval
```

**Final hard STOP:** No authorization to deploy, start human/clinical activity, enable optional integrations, invent clinical/security/retention policy, accept findings, change protected runtime, advance directly to P23/P24 or issue a release decision. If safe bounded audit cannot proceed within this prompt, stop and explain the smallest specific blocker rather than expanding scope.
