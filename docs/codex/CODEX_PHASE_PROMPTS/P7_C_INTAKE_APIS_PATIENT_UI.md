# SwasthyaSetu AI — P7-C: Clinical Intake Application, APIs, Patient BFF & UI

**Governed Codex execution prompt — implementation + verification (not a proposal).**

- **Repository:** `Itsbhavesh1101/swasthyasetu_ai`
- **Verified merged starting point:** `main @ 476f7415de39320f9c5df5bb20c387a2f57a5e88`
- **Required new branch:** `phase/p7-c-intake-apis-patient-ui` (or explain an existing safe P7-C branch before reusing it)
- **Source state:** P0–P6, pre-P7 specs, P7-A, P7-B merged. P7-A migration head `p7a_0007`. P7 remains PARTIAL.
- **Prior reviewed P7-B SHA:** `bb667ccd9a7db63c12d52c47c577efd7a6ae3de6` (included in merged main)
- **Scope:** P7-C only. **Push, do not merge.** Do not continue into P8 or later.
- **Quality principle:** Exact repo implementation and canonical docs beat any assumptions in this prompt. If the starting SHA is no longer `main`, stop and report the discrepancy instead of coding on an unknown base.

## 0. Mandatory read/audit before changes

Read these **from the checked-out repository** (not only this prompt):

1. `docs/00_PROJECT_MASTER_SPEC.md` (master authority);
2. `docs/01_PRODUCT_REQUIREMENTS.md`, especially FR-INTAKE, FR-ENC, FR-PAT, FR-IDENT, FR-CONSENT, FR-LANG, safety/privacy and NFR-UX IDs;
3. `docs/02_SYSTEM_ARCHITECTURE.md`; `docs/03_REPOSITORY_STRUCTURE.md`;
4. `docs/04_DOMAIN_MODEL.md`; `docs/05_DATABASE_SCHEMA.md`; `docs/06_API_CONTRACTS.md`;
5. `docs/07_CLINICAL_INTAKE_SPEC.md` **entire**, especially §§5–8, 16–21, 25–35;
6. `docs/22_UX_AND_USER_FLOWS.md` **entire**;
7. `docs/23_PATIENT_APP_SPEC.md` **entire**;
8. `docs/29_ENGINEERING_STANDARDS.md`; `docs/34_MASTER_IMPLEMENTATION_PLAN.md`;
9. `docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md`; `36_DEPENDENCY_MAP.md`; `37_DECISION_LOG.md`; `38_PROGRESS_TRACKER.md`;
10. `docs/codex/CODEX_INSTRUCTIONS.md`, `CODEX_WORKFLOW.md`, `CODEX_CONTEXT_RULES.md`;
11. `docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md`, `R3_CODEX_DEPENDENCY_POLICY.md` and related R3 reconciliation if installed dependencies change;
12. Earlier exact prompts and review-fix notes: `P7_A_INTAKE_DOMAIN_SCHEMA.md`, `P7_A_REVIEW_FIX_01_LIFECYCLE_PERSISTENCE_GUARD.md`, `P7_B_DETERMINISTIC_ADAPTIVE_ENGINE.md`, `P7_B_REVIEW_FIX_01_ACTIVE_QUESTION_VERSION_AMBIGUITY.md`.

**Required repository inspection** (before any edits):

```bash
git status --short
git branch --show-current
git rev-parse main
git rev-parse HEAD
git log -5 --oneline
```

Inspect the **actual** `backend/app/modules/clinical_intake/{domain,contracts,serialization,infrastructure,engine,history,pack_validation,public}.py`, `backend/app/main.py`, shared module/capability registry, session/consent/encounter/patient **public** interfaces, applicable API/auth helpers, DB transaction/outbox conventions, Alembic lineage; `apps/patient-web/{app,components,lib/onboarding,tests}`, patient PWA/service worker rules and `tests/e2e/patient.spec.ts`. Read existing test utilities/fixtures and six CI workflows.

Known starting observations to verify against code (do not assume if drifted):

- P7-A provides **three tables** (`clinical_intakes`, `intake_answers`, `questionnaire_instances`) and typed repositories/serializers; **no P7 runtime registration/API**.
- P7-B provides pure `AdaptiveIntakeEngine`, strict `PackRegistry.activate()` and `validate_question_identities()`: **simultaneously active `question_id` values must be globally unique regardless of question version**. Different versions can be independently registered/activated. `InvalidQuestionPackError` must propagate as a safe typed failure. Engine cannot perform I/O.
- P7-A repository `save()` has an explicit **authoritative persisted terminal-lifecycle guard**; do not weaken it.
- `backend/app/main.py` currently registers identity, sessions, consent, patients, encounters and provenance; P7 needs an explicit registration and public bindings, not runtime discovery.
- `apps/patient-web/app/encounter/page.tsx` currently shows P6 readiness only; real P7 UI, `/intake/[intakeId]`, `/review`, intake BFF and related tests do not exist.
- P6 bearer is held only by transient `HttpOnly`, `SameSite=Strict`, `Path=/` BFF cookies and forwarded server-side; PWA allows only a minimal **generic** cache; current real onboarding works against FastAPI/PostgreSQL.

**Before implementation, produce a short internal audit and a concise P7-C design/ownership map**. Resolve each ambiguity against canonical docs. For material architecture or clinical conflicts use `STATUS: BLOCKED` with evidence rather than guessing. Keep unrelated baseline behavior intact.

## 1. Objective and precise ownership

Ship a **real, deterministic, server-authoritative** pseudonymous text/touch journey:

```
P6 start -> language -> real session -> consent
    -> encounter readiness -> start/resume authorized GENERAL_INTAKE
    -> start/resume UNIQUE intake with pinned pack identities
    -> server-selected next question / clarification
    -> validated answer + persisted draft / review / edit / resume
    -> server-authorized completion -> saved structured DRAFT (read-only)
```

**P7-C owns:** clinical-intake application orchestration, explicit runtime capability registration, typed FastAPI endpoints, exact-session authorization/consent, encounter coordination, approved/engineering-only pack selection, contextual history boundary, answer/instance/projection synchronization, P7 BFF, patient screens/components, accessibility, real DB/API/Playwright regressions, and documentation/progress.

**OUT OF SCOPE:** AI chat and `/intakes/{id}/messages`, LLM/model/speech/translation/OCR, real emergency triage or risk decisions, clinician confirmation, diagnosis/treatment/medication/screening scores, provider/referrals, self-care/Ayurveda content, FHIR/ABDM activation, authenticated patient continuity, PATIENT-subject consent, offline clinical work, new general-purpose framework or external provider. **Do not introduce a seventh mandatory CI job.**

## 2. Explicit design decisions for P7-C

### 2.1 Abandon endpoint

**Do not activate the optional P7-C intake-abandon HTTP endpoint/UI in this unit.** End private session remains a **distinct** P6 action. Closing the tab/session must not implicitly mutate an intake to `ABANDONED` or delete intake records. An `IN_PROGRESS` draft is server-authoritative and can be continued while the same session remains authorized; terminal `ABANDONED` remains protected/read-only if present from governed setup. Clearly note this documented P7 open decision in docs, no invented resume after a revoked session. If a higher-priority canonical doc *requires* activation, flag the discrepancy rather than silently changing scope.

### 2.2 No invented clinical/localized content

Canonical P7 specs leave final question wording/requiredness, clinical options, eligible history-trust suppression and approved Hindi localization undecided. Do **not** declare an unapproved questionnaire or threshold clinically approved.

Implement a **project-owned, explicit, immutable, engineering-safe CORE pack** with only neutral data-collection wording/structure needed to prove the P7-C flow; label as an **engineering/demonstration fixture**, and **gate patient-facing activation to explicitly configured local/test profiles only** until approved content exists. Avoid any medical interpretation or speculative clinical requiredness. Preserve distinct pack/content/schema versions. In pilot/staging/production without approved content and explicit enablement, return a safe `FEATURE_DISABLED` / `POLICY_UNAVAILABLE` / configured error rather than silently activating engineering fixtures. The test fixture MUST NOT be represented as clinical approval. It may populate a minimal chief complaint and neutral structured fields and use synthetic inputs for extended HPI/history/ROS/AYUSH contract demonstrations. **Do not generate or pretend to have approved full Hindi clinical content**: `hi` may remain selected for onboarding, but without an approved pack the intake must show an honest unavailable state; no forced English fallback or dynamic translation.

Use **server-owned pack IDs and versions**. A client may request `pack_ids` only from the allowed registry (e.g. `core.intake`); never accept client-supplied pack version, approval state, rule text, history eligibility/trust, section requiredness or engine result. Pin selected `(pack_id,version)` in `questionnaire_instances` on first start. Resume/review must use **those exact persisted versions**, not reinterpret existing records under a newer default pack. Missing/deactivated historical pack must return an explicit safe error, **not silently upgrade**.

### 2.3 Encounter start consistency

The existing encounters public transition capability uses its own transaction; do not fake atomicity by reaching into encounters' ORM/repository from intake. P7 spec permits intake creation for `GENERAL_INTAKE` / `KIOSK_INTAKE` encounters in `CREATED` or `IN_PROGRESS`, and a `CREATED -> IN_PROGRESS` transition is **optional**. Prefer **leave the encounter status `CREATED` at intake creation** unless an approved public coordinated transaction design can guarantee correct ownership/rollback. Do not leave a false claim of atomic encounter+intake transition. Intake completion must not complete the encounter. No unsupported encounter types or terminal states.

P6 currently has no session-scoped active encounter lookup. Design a narrow, authorized **start/continue controller** that keeps the first-contact user from accidentally creating multiple episodes on refresh/repeated clicks. If supporting session-level find-or-create requires a new **encounters public capability**, add only a narrowly scoped typed read capability and its tested persistence query; coordinate concurrent starts with real PostgreSQL locking/constraint semantics **without** cross-module ORM writes. Never manufacture a competing patient record for a pseudonymous encounter. If stronger session-wide uniqueness is not prescribed or safely achievable without an architecture decision, state the exact supported idempotency boundary explicitly and test it (the spec's non-negotiable uniqueness is **one intake per encounter**). Do not claim race protection you have not proven.

### 2.4 History in pseudonymous first contact

Session-bound pseudonymous encounter without `patient_id` has **no authoritative longitudinal patient facts**; return no known-history step (not fake sample records). Where a linked, authorized patient path is **actually governed**, adapt only the patients **public read/facts capabilities** to immutable `HistoryContext`, retaining source and verification status, filtering `REJECTED`/`SUPERSEDED`, enforcing question-specific explicit reuse policy and paginating correctly. Do not activate PATIENT-subject consent or authenticated continuity by stealth. No cross-module ORM access and **no longitudinal fact mutation** from intake answers/confirmation/disagreement. Use pure/fake capability tests for linked-context behavior if required without exposing a new unauthorized patient UI mode.

## 3. Backend: registration, services and API

### 3.1 Explicit bounded registration

Implement `clinical_intake`'s `build_..._registration`/service composition and bind existing `INTAKE_START`, `INTAKE_READ`, `INTAKE_ANSWER`, `INTAKE_COMPLETE`, `INTAKE_NEXT_QUESTION` in the project's typed registry. Expose `/intakes` and nested `/encounters/{encounter_id}/intake` correctly below the existing `/api/v1` (router prefix conventions matter). Avoid circular imports by following P5-C `public.py` composition patterns. Keep domain pure, adapters separate and per-app dependency instances isolated. The module manifest must declare accurate required capabilities, routes/events and data ownership. No global mutable singleton/plugin scan. Retain existing tests and router registration injection behavior.

### 3.2 Authorization first and on EVERY operation

For **start, read, answer, complete, and any P7 readiness or resume lookup**:

- Validate `Authorization: Bearer ...` via the existing parser and public `SESSIONS_VALIDATE` for **the encounter's exact session ID** (not a caller-invented identity).
- Require current `SESSION / GENERAL_PRODUCT_USE / clinical_intake` consent using **central `CONSENT_CHECK`**; never trust a P6 UI readiness flag or earlier grant.
- Verify exact encounter-to-intake association, `GENERAL_INTAKE`/`KIOSK_INTAKE` eligibility, allowed status, and authorization for the current pseudonymous session. The path UUID is a locator only; never a permission. Reject cross-session attempts even if an attacker knows an intake, encounter or question ID.
- Do not activate authenticated/PATIENT consent paths; if an encounter is patient-bound but that access contract is not approved, fail closed.
- Same exact-session/consent gates must apply to **read**, review and completed-draft re-read, not just mutations. Withdrawal must block subsequent access without erasing data.
- Avoid existence leaks: absent/foreign IDs give a safe generic status without disclosing foreign patient/encounter facts. No actor/session identity headers trusted from browser input.
- Test session expiration, closure/revocation, malformed bearer, invalid/missing consent, race between consent check and mutation where applicable, cross-session IDOR, and client attempts to tamper with session scope.

Design request-time revalidation and mutation transaction boundaries to fail closed on revoked consent and terminal/changed session/encounter, including relevant concurrency; don't merely authorize once at UI load and then apply unprotected writes. If independent module transactions constrain strict atomic consent revocation ordering, use the established public capabilities and document the supported consistency model rather than bypass ownership; add race tests for what the architecture can enforce.

### 3.3 Application-layer engine orchestration

- Intake IDs, answer IDs, question/pack identities and per-encounter questionnaire instances are distinct and stable. No ambiguous `(question_id,question_version)` lookup across active packs; reuse P7-B **global active-question-ID guard** unchanged.
- On first start, resolve configured pack identities server-side, persist exactly the active instances and initial aggregate in PostgreSQL; one intake per encounter. Duplicate start for **same authorized encounter and same pack request** returns its existing intake; conflicting requested pack set or attempts to mutate terminal intake return typed conflict. Handle racing inserts with actual UNIQUE constraint; no duplicate `questionnaire_instances` or orphan answers. Don't treat any duplicate as safe if different pack content was requested.
- On read, reconstruct `EngineInput` only from authorized persisted intake + stored pack/version instances + actual answers + safe eligible public history + contradictions, then compute `EngineResult` deterministically. Missing engine inputs, pack drift or inconsistent persistence must fail safely, not return `CompletionReady` accidentally. Never place I/O in engine.
- **Typed `NextQuestion` / `ClarificationRequired` / `Incomplete` / `CompletionReady`** are authoritative; UI never calculates selection, requiredness, missing state, clarification priority, or readiness.
- For each submitted answer, reject unregistered/incorrect question ID, version, type, control/value, unsupported language, invalid selected options or unit, unapproved skip/UNKNOWN/refusal, unavailable pack, illegal source provenance, and client-supplied trust status. Call P7-B answer validation via a *public supported path* (or extracted reusable validator), not a second inconsistent validator. `REUSED_HISTORY` cannot be impersonated by a patient POST.
- A mutation must be validated against the **persisted latest version and state** in the authoritative DB; `expected_version` required and positive. Server generates ID and trustworthy UTC time. Insert answer, update questionnaire response reference(s), recompute typed aggregate (chief complaint, HPI, history, ROS/investigations where corresponding configured questions support them), recompute missing/contradictions and increment intake version **once**, all in one PostgreSQL transaction. Existing answer/projection referential integrity and source-of-truth guarantees are not optional.
- Later correction of the same question must become the authoritative latest answer deterministically even under equal wall-clock timestamps / injected fixed clock. Retain immutable prior answer records and provenance. Do not let UUID/timestamp tie-breaking randomly restore a stale earlier value. Version reconciliation and order of accepted edits must be explicit and tested.
- In `questionnaire_instances.responses`, store matching pack identity, correct `answer_refs`/`skipped_question_refs`, selected question ID and engine version; the instance is an **index**, not a competing answer store. Preserve every applicable instance and synchronize terminal state with intake completion. Handle missing, mismatched, duplicated or terminal instances explicitly.
- Reuse known history only when explicitly eligible. A confirmation/refusal/contradiction must reference **both source sides** where applicable; do not fabricate or silently resolve conflicts. Unresolved required contradiction blocks completion. Avoid leaking unrelated patient history into the P7 response.
- Record original patient wording (when given) distinct from any configured display key; never assign clinical normalized codes without an approved mapping. No arbitrary unrestricted patient JSON storage.
- On completion, **re-evaluate under the same authoritative persisted transaction/snapshot**, require `CompletionReady` and no unresolved required missing/contradiction; write `COMPLETED` + UTC `completed_at`, synchronize instances and version, and respond read-only. Repeated authorized complete is idempotent when already completed; stale conflicting writes/answer-after-complete/attempt to reopen fail `409` without partial state. `ABANDONED` is terminal and not reopened.
- Outbox events, if added per the canonical event contract, must be versioned, metadata-only and enqueued in the same DB transaction with the write. Never emit clinical answer text as ordinary events/logs. Do not invent events that bypass current module ownership; if outbox is not in-scope for a particular operation, document why rather than fake reliable publication.

### 3.4 HTTP endpoints and typed safe responses

Implement the canonical P7 endpoints with Pydantic v2 `extra="forbid"`, explicit bounded fields, existing standard error envelope and correct HTTP status codes:

```
POST /api/v1/encounters/{encounter_id}/intake
GET  /api/v1/intakes/{intake_id}
POST /api/v1/intakes/{intake_id}/answers
POST /api/v1/intakes/{intake_id}/complete
```

The existing encounter-create API may be used by the authorized BFF workflow; any dedicated session-scoped read/start helper must be narrowly justified/documented, not an ad hoc anonymous leak. No `/messages` and **no `/abandon`** in this unit.

- Start body follows `{"pack_ids":["core.intake"]}` with **server-controlled versions**. Use exact status for new vs already-existing and document replay semantics.
- Answer follows the canonical `question_id`, `question_version`, `answer` (`schema_version="intake-answer.v1"`), allowed patient source type and `expected_version`. Reject unknown/extra fields, invalid finite/decimal/date shape, payload over limits, unsupported modes, malicious extras. Body must never permit caller-chosen answer UUID, `answered_at`, `created_at`, `REUSED_HISTORY`, `verification_state`, source fact ID, rule, pack version, policy override or terminal state.
- Complete `{ "expected_version": n }`. Completed state means **saved structured draft only**; do not include diagnosis/score/safety clearance.
- GET returns minimized versioned typed data sufficient for display/review: status, version, current server-selected question/render metadata, allowed answer choices/constraints, accepted answer references/sections, source labels, missing and contradictions, completion readiness; never a full unrelated patient context. Question text comes only from approved/explicitly local engineering content registry, not LLM or generic fallback.
- All P7 successes **and errors** have `Cache-Control: no-store`, no credential echo. Stable mapped codes (`AUTHENTICATION_REQUIRED`, `SESSION_EXPIRED`, `CONSENT_REQUIRED`, `AUTHORIZATION_DENIED`/`RESOURCE_NOT_FOUND`, `RESOURCE_CONFLICT`, `INVALID_STATE_TRANSITION`, `VALIDATION_ERROR`, `POLICY_UNAVAILABLE`/`FEATURE_DISABLED` as configured); no Python exception class/SQL string or raw submitted answer in errors.
- Idempotency key (if supported) is scoped to actor/session + operation + exact request fingerprint. Same key/different payload -> `409`, same key/same payload -> original equivalent result without another answer/version/outbox mutation. Never implement a superficial in-memory map or claim durable idempotency without durable transactional support. Without a durable general idempotency implementation, prioritize one-intake unique start, server version conflicts, client refetch/reconcile, and **no blind retry**; document the supported boundary.

## 4. Next.js BFF and patient application

### 4.1 BFF contract

Add same-origin routes (fixed templates; validated UUID path segments) such as:

```
/api/intake/encounters/[encounterId]/start
/api/intake/[intakeId]
/api/intake/[intakeId]/answers
/api/intake/[intakeId]/complete
```

A carefully scoped `/api/intake/.../readiness` or `/start` helper may orchestrate existing encounter and intake if necessary; list exact chosen endpoints in docs. Reuse P6 `lib/onboarding/server.ts` credential, strict cookie, backend URL validation, timeout, no-store, origin protections **without copying unsafe accessors to client code**. Refactor shared server-only code only if narrow and covered by P6 regression tests. Forward the bearer **only** server-to-FastAPI; credentials must not be in JS, HTML props, logs, URLs, responses or client Authorization headers. Validate response bodies against explicit runtime type guards/schemas, minimize fields, bound requests, reject cross-origin mutations, no automatic retry of POSTs after timeout. Clear invalid session cookies only on proven invalid/expired/closed backend result; do not treat ordinary 409 version conflicts as a reason to clear valid credentials. Preserve HTTP/cache/content-type behavior and safe error allowlist. Server-only `SWASTHYASETU_BACKEND_URL` must remain non-browser-visible.

### 4.2 Pages and states

Keep all current P6 routes functioning. Add:

```
/intake/[intakeId]
/intake/[intakeId]/review
```

Extend `/encounter` from readiness into a genuine **start/continue** controller only on verified server session+consent+applicable state. Call backend, never construct fake clinical results. Start accepts an existing authorized eligible encounter/intake or creates/uses a correctly controlled session-bound general encounter. Prevent duplicate clicks/client replay; handle multi-tab/reload with server-authoritative lookup/race semantics. Route IDs never authorize.

Question page must render server-selected **one question**, appropriate typed input for all 8 `AnswerType`s (TEXT, SINGLE_CHOICE, MULTI_CHOICE, BOOLEAN, NUMBER, DATE, DURATION, SEVERITY_SCALE) where configured, allowed unknown/refusal/skip controls only when permitted, help text, section context, truthful non-percent progress, source labels and next/review actions. Severity scale is **not a clinical risk score**; only represent a configured validated scale. Do not invent medical scales or options.

- On submit, disable duplicate requests, retain transient unsent input only in component memory; success only after server ack + new version; on ambiguous network error/409 **refetch and ask user to review** before re-entering (no silent replay/overwrite).
- Support optional known-history confirmation/neutral contradiction screen **only if backend has legitimate references**; otherwise do not display invented evidence. Missing required information must be visible with server-provided reasons and actionable clarification; no implicit waiver.
- Review page groups typed saved answers and sections by origin (patient-reported, reused history, changed/clarified), shows unknown/refused and remaining missing; editable answers use server-authorized correction and expected_version, with stale-state reconciliation. Completion button enabled only by backend `CompletionReady` and only while intake `IN_PROGRESS`; send current version.
- Completion: “Your intake draft has been saved,” read-only review, accurate timestamp/version, caveat no diagnosis/treatment/triage/clinician approval; completion **does not** transition encounter automatically.
- Failure states: `NO_SESSION`, `NO_CONSENT`, forbidden/not-found, unsupported `hi` pack, approval-gated feature, stale version, backend down, invalid server payload, unknown/invalid pack, terminal intake. Distinct “End private session” action remains usable and does **not** pretend data deleted or intake abandoned. Keep generic urgent-help accessible on every page including offline/errors.

### 4.3 Browser/security/accessibility

- Do **not** put clinical state in localStorage, sessionStorage, IndexedDB, Cache Storage, service-worker runtime cache, analytics/session replay, query strings, browser-readable cookies, or offline queue. No background sync/replay, clinical GET caching, stateful HTML caching. Component memory only for unsent inputs; refresh always refetches from backend.
- Preserve P6 PWA allowlist and network-only HTML behavior, `/api/**` bypass; offline shows **generic** fallback and cannot resume/submit intake. No `dangerouslySetInnerHTML` with patient text.
- Keyboard-only start/answer/review/complete/close; real form labels, association of validation errors, one page `h1`, stable predictable focus (including after question change/error), accessible live status. 44px touch targets, 320/390px reflow, contrast/focus, forced-colors, reduced-motion. User-friendly non-diagnostic text.
- Do not claim full Hindi clinical translation if unavailable. Never translate clinical text by prompt/user-agent/browser shortcuts.

## 5. Cross-layer invariant and failure checklist — implement NEGATIVE tests now

**P7-A/P7-B previously needed review fixes for implicit authority/version ambiguities. Don't repeat that pattern.** For every check below, identify where the invariant is enforced, how a bypass is attempted and the exact regression test proving it.

1. **Identifiers:** exact intake ↔ encounter ↔ session binding; immutable question/pack IDs and versions; no unknown pack/answer references; no ambiguous `question_id` even across versions; activation independent of caller order.
2. **Authorization:** no resource access by UUID possession, spoofed session IDs/headers, wrong bearer, other session, closed/expired session, foreign encounter; read and POST protected equally.
3. **Consent:** exact SESSION subject/purpose/scope, active at every operation, revoked/expired blocking, no PATIENT-subject shortcut.
4. **Lifecycle:** `IN_PROGRESS` only editable; `COMPLETED`/`ABANDONED` terminal even with forged dataclasses/repository access; encounter lifecycle never bypassed; completion draft only.
5. **Concurrency:** `expected_version` on every mutation, single increment, answer and all typed projections/instance updates atomic, stale submit returns 409 with unchanged DB, concurrent start unique per encounter, double complete no duplicate mutation; tests use **real PostgreSQL** with competing transactions/requests.
6. **Idempotency/replay:** no extra answer from a double-click, no duplicate start/instances, identical replays as specified, changed bodies with reused key conflict if keys supported; a timeout is not considered success.
7. **History/provenance:** patient facts via public capability only; `REJECTED`/`SUPERSEDED` excluded; confirmation/disagreement cannot modify facts; references are accurate and minimal; no fake demo patient data in production.
8. **Answer contract:** all eight types validated end to end; numeric finite constraints, option IDs, date and duration units, severity-scale metadata, skip refusal configuration, immutable ID/time provenance, original wording; mismatch cannot pass through alternate route or serialized shape.
9. **Determinism:** engine result matches same persisted pack versions/answers/history/contradictions; deterministic next-question ordering; no random model, network or time in pure engine; correction beats earlier answer even under fixed/equal timestamps.
10. **Failure rollback:** injected answer-save, instance-save, aggregate-save, outbox-save errors leave **zero partial writes**; no version increment or fake completion after transaction failure. Observe real DB rows.
11. **Browser/server:** no token in JS or response bodies, no clinical browser persistence including service-worker runtime cache, no clinical answer in URL; invalid backend shape rejected and sanitized; origin check on all mutations.
12. **Feature gate:** engineering fixture cannot run in production/pilot by accidental env/default; missing approved content is honest; unavailable Hindi and AYUSH packs do not become implicit English/clinical fallbacks.
13. **No out-of-scope activation:** no `/messages`, unsafe medical advice, generated helplines/providers, clinician diagnosis, AI package, new general broker, unwanted migration or UI route explosion.

Test explicit by-design negative outcomes rather than only positive happy paths. Keep fixtures synthetic, never commit real clinical data/secrets.

## 6. Test plan and six required CI gates

**Backend unit/API:** typed contracts, 8 answer controls/serializers, version drift, pack gating, deterministic engine bridging, mapped safe errors, mock capability/boundary tests, no cross-module imports. Preserve all pre-existing P1–P7 tests.

**Real PostgreSQL integration:** start and unique replay; two-request race; exact session+consent; cross-session IDOR read/write; withdrawn consent; invalid/terminal encounter; answer atomic persistence and correct aggregate/HPI/history projections; conflicting versions; corrections with equal clock; multiple pack-instance consistency; completion/terminal protection; injected rollback after each write stage (including outbox if used); real migration upgrade/downgrade if a migration is justified. Assert no extra tables and current head remains `p7a_0007` when no migration is needed. **Do not substitute SQLite/mocks for these claims.**

**Frontend unit/BFF:** backend request mapping; strict runtime response checks; GET/POST no-store; current HttpOnly cookie isolation and origin enforcement; explicit backend failures; timeout/no retry; invalid session vs stale-write differentiated; all 8 conditional answer controls; missing/contradiction/review/error/approval-disabled states; keyboard/focus; privacy/cache restrictions.

**Playwright Chromium (real API + PostgreSQL):** new P7 journey from **real P6 onboarding** to saved draft; refresh/resume; revised answer; no diagnosis; keyboard-only focus path; 320/390px reflow and targets; withdrawal blocks intake; session close; wrong-session IDOR; service-worker allowlist; offline unavailable/no queue. Existing P6 tests remain green; replace outdated “intake not available” expectations only where local/test fixture activation explicitly makes it available. Browser must not depend on mocked clinical APIs for final E2E proof.

Keep existing required six jobs (exact names in repo): **Backend quality; Frontend quality; Persistence integration; Docker and PostgreSQL; Playwright Chromium; Security scans.** Run local relevant formatting, Ruff, mypy, pytest, PostgreSQL, pnpm lint/typecheck/tests/build, Playwright, migration checks; push and verify branch CI. **Do not weaken/delete/skip valid tests or alter CI just to get green.** If an environment cannot run a test, mark NOT VERIFIED and do not claim complete.

## 7. Documentation, diff audit, acceptance

Update the actual canonical contract docs **only for genuine approved P7-C implementation detail** (`06_API_CONTRACTS.md`, `07_CLINICAL_INTAKE_SPEC.md`, `22_UX_AND_USER_FLOWS.md`, `23_PATIENT_APP_SPEC.md`, `05_DATABASE_SCHEMA.md` only if a schema change, backend/frontend READMEs, `38_PROGRESS_TRACKER.md`, and `REPOSITORY_TREE.txt` as appropriate). Preserve unresolved approved-content/consent/privacy/AYUSH decisions, do not silently rewrite source requirements or change clinical authority. If a new persistent change is truly required, create reviewed minimal Alembic migration and test both directions; otherwise **no schema/migration dependency creep**. R3 dependency-class policy applies to every new package.

Map implementation evidence to **AC-P7-001 through AC-P7-010** and global mandatory acceptance criteria. Classify separate outcomes accurately: engineering/test flow complete **does not** mean clinical production-pack approval or pilot readiness. If critical required acceptance is blocked by an absent approved pack/transactional design, report **PARTIAL/BLOCKED** with the precise evidence, not fabricated success.

Before pushing inspect:

```bash
git status --short
git diff --stat
git diff --check
git diff
# Confirm no secrets, unsupported dependencies, accidental migrations,
# raw patient info, stale docs, hardcoded clinical thresholds, or weakened tests.
```

Push **only** the P7-C feature branch, **do not merge**, and ensure the reviewed local commit equals remote head. If a PR is customary, open a PR **without merging**. Check branch CI and report relevant run IDs/conclusions. Don't advance into P8.

## 8. Final report — compact and falsifiable

Return only:

```
STATUS: COMPLETE / PARTIAL / BLOCKED / FAILED
BRANCH:
BASE MAIN SHA: 476f7415de39320f9c5df5bb20c387a2f57a5e88
FINAL LOCAL SHA:
REMOTE SHA (must equal local):
PR URL / NUMBER (if created):
ALEMBIC HEAD / NEW MIGRATION:
P7-C SCOPE DELIVERED: (brief)
CLINICAL CONTENT ACTIVATION: approved / gated engineering fixture / unavailable
TESTS: (backend, real PostgreSQL, frontend, Playwright)
CI: six jobs + run ID + precise conclusions
OPEN DECISIONS / LIMITATIONS:
UNRELATED CHANGES: none / explain
MERGED: NO
```

**STOP after reporting.** ChatGPT will verify actual code/diff/CI before advising merge; a Codex self-report alone is not merge authorization.
