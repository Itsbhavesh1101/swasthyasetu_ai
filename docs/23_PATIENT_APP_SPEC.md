# SwasthyaSetu AI
## 23 — Patient Application Specification

# Document Control

**Document ID:** `SSAI-PATIENT-APP-023`
**Filename:** `23_PATIENT_APP_SPEC.md`
**Status:** Canonical P7-C Prerequisite / Approved for Implementation
**Version:** `1.0.0`
**Application:** `apps/patient-web`
**Depends on:** `07_CLINICAL_INTAKE_SPEC.md`, `22_UX_AND_USER_FLOWS.md`, `06_API_CONTRACTS.md`, implemented P6 baseline

---

# 1. Purpose, Scope, and Non-Goals

This document defines how the patient Next.js application will integrate the P7 structured-intake
contracts. It is an implementation-facing boundary specification, not authorization, clinical policy,
or a substitute for backend domain rules.

P7-C scope is a server-authoritative pseudonymous text/touch intake, resume, review, and completed-draft
experience. It must preserve the existing P6 App Router shell, same-origin BFF, transient secure
cookies, accessibility baseline, PWA cache restrictions, and real FastAPI/PostgreSQL integration.

Non-goals include frontend clinical rules, diagnosis, treatment, triage, AI chat, speech/translation,
offline clinical behavior, document/result/referral activation, authenticated continuity, and
client-side health-data persistence.

---

# 2. Existing P6 Architecture

The merged application already provides:

- App Router routes for home, onboarding, consent, encounter readiness, unavailable future features,
  urgent help, and generic offline fallback;
- server-only `lib/onboarding/server.ts` BFF helpers;
- same-origin onboarding route handlers;
- opaque session ID/token in transient `HttpOnly`, `SameSite=Strict`, `Path=/` cookies, with `Secure`
  in production/non-loopback environments;
- server-side bearer forwarding only in `Authorization`;
- `Cache-Control: no-store` for onboarding responses;
- an explicit service-worker shell allowlist that bypasses `/api/**` and keeps navigation network-only;
- keyboard/focus, reflow, touch-target, contrast, forced-colors, and reduced-motion baselines.

P7-C adds to these boundaries; it does not replace them.

---

# 3. Routing Map

Existing routes remain:

```text
/
/start
/language
/consent
/encounter
/documents
/results
/urgent-help
/referrals
/offline
```

Minimal P7-C additions are:

```text
/intake/[intakeId]
/intake/[intakeId]/review
```

`/encounter` becomes the authorized readiness/start/resume controller. `/intake/[intakeId]` renders
the current server-selected question or clarification. `/intake/[intakeId]/review` renders the
structured draft and completion action. Opaque route IDs are locators only, never authorization.

No separate page is needed for each section or question; pack-driven state prevents route explosion.
`/documents`, `/results`, and `/referrals` remain explicitly unavailable.

---

# 4. State Ownership

| State | Authority | Browser representation |
|---|---|---|
| session and bearer | sessions backend | transient HttpOnly cookies; bearer never readable by JS |
| consent | consent backend | minimized state fetched through BFF |
| encounter | encounters backend | minimized authorized view |
| intake aggregate/version | clinical_intake backend/PostgreSQL | current response/render state only |
| answers/missing/contradictions | clinical_intake backend/PostgreSQL | minimized current view only |
| question packs/rules | backend compile-time registry | question presentation contract only |
| transient form input | React component memory | cleared/reconciled after server response/navigation |
| offline shell | service worker | generic approved shell resources only |

Refresh and resume always refetch authorized server state. The browser never becomes a recovery or
conflict-resolution database.

---

# 5. BFF Boundary

The path remains:

```text
patient UI -> same-origin Next route handler -> FastAPI /api/v1 -> PostgreSQL
```

P7 BFF code:

- reads session ID and bearer only server-side from the existing cookies;
- builds backend paths from validated UUIDs and fixed route templates;
- forwards the bearer only as `Authorization: Bearer ...`;
- uses the configured validated `SWASTHYASETU_BACKEND_URL` and bounded timeout;
- sends `Accept: application/json`, typed JSON, and `cache: "no-store"`;
- validates backend response shape before returning minimized typed JSON;
- sets `Cache-Control: no-store` on every success and error;
- never returns or logs bearer, raw headers, consent payload, or unrelated clinical context;
- rejects cross-origin mutation requests using the established origin check;
- never blindly retries a side-effecting request.

Suggested same-origin route families are:

```text
/api/intake/encounters/[encounterId]/start
/api/intake/[intakeId]
/api/intake/[intakeId]/answers
/api/intake/[intakeId]/complete
/api/intake/[intakeId]/abandon       # only if the open decision is activated
```

They are BFF surfaces, not new domain APIs.

---

# 6. Session Handling

P7 reuses `swasthyasetu_session_id` and `swasthyasetu_session_token`; it creates no new credential or
client-visible token. Every BFF request requires both cookies and forwards the token only to FastAPI.

Missing credentials return a minimized `SESSION_UNAVAILABLE` state. Backend authentication failure,
expiry, closure, or revocation clears both cookies and does not reveal intake existence. Closing a
session remains an explicit existing operation and does not falsely report intake deletion or
abandonment.

---

# 7. Consent Handling

The BFF does not accept purpose/scope/notice values from the intake UI. The current controlled values
remain:

```text
subject_type = SESSION
purpose = GENERAL_PRODUCT_USE
scope = ["clinical_intake"]
notice_version = privacy-v1
```

FastAPI performs centralized consent checks on every clinical operation. The BFF may preflight the
existing minimized consent state for UX, but preflight is not authorization. Consent withdrawal
blocks subsequent intake operations while preserving server state under governed retention.

`PATIENT`-subject consent is not activated.

---

# 8. PWA and Cache Boundary

The existing service worker remains root-scoped and may cache only:

```text
/offline
/manifest.webmanifest
/icons/icon-192.png
/icons/icon-512.png
/icons/icon-maskable-512.png
```

P7 must not add intake routes, BFF/API responses, question packs, localization containing clinical
questions, answers, drafts, consent/session state, or known history to Cache Storage. `/api/**`
continues to bypass the service worker. Navigations remain network-only and may show only the generic
offline fallback after network failure.

No background sync, queue, mutation replay, push payload, or custom install-prompt persistence is
authorized.

---

# 9. P7 Intake Route Architecture

## 9.1 `/encounter`

Server/client boundary loads minimized readiness. States: checking, session unavailable, consent
required, ready to start, resumable intake, completed draft, and unavailable. Start is a mutation and
navigates only after a validated response.

## 9.2 `/intake/[intakeId]`

The route validates the ID shape, obtains the current intake through the BFF, and renders one of:

- current typed question;
- known-history confirmation;
- contradiction clarification;
- missing-information clarification;
- completion-ready link to review;
- completed/abandoned read-only state;
- safe unavailable/error state.

The client does not derive next-question order.

## 9.3 `/intake/[intakeId]/review`

The route obtains a fresh authorized snapshot and renders grouped source-aware draft content. Edit
links return to a server-supported question/section state. Complete submits the displayed version;
success renders the completed draft. Stale conflict forces refetch/review.

---

# 10. Component Architecture

P7-C should remain feature-oriented. A suggested structure is:

```text
components/intake/
  intake-readiness.tsx
  intake-question.tsx
  answer-control.tsx
  history-confirmation.tsx
  contradiction-clarification.tsx
  missing-information.tsx
  intake-progress.tsx
  intake-review.tsx
  source-label.tsx
  intake-actions.tsx

lib/intake/
  client.ts
  server.ts
  contracts.ts
  validation.ts
```

This is a P7-C layout recommendation, not an instruction to create code during this specification
pack. Components consume discriminated typed views. Shared visual behavior should reuse existing
patient primitives rather than clone buttons, banners, panels, or urgent-help controls.

The UI must not contain a giant question-ID switch with clinical behavior. `answer_type` selects a
generic control; server configuration supplies allowed presentation metadata.

---

# 11. API Client Architecture

`lib/intake/server.ts` owns server-only backend calls and response validators. `lib/intake/client.ts`
owns a small same-origin fetch wrapper returning discriminated results. `contracts.ts` contains
minimized UI contracts, not duplicated backend domain entities.

Recommended client result:

```text
{ ok: true, data: T }
| { ok: false, error: { code: SafeErrorCode, message: string } }
```

Only a bounded allowlist of backend error codes reaches the browser. Unknown/malformed responses map
to a generic backend-request failure. Sensitive validation values are never echoed. Requests use
`credentials: same-origin`, `cache: no-store`, and no `Authorization` header in browser JavaScript.

The current intake view includes opaque IDs, status, version, typed current-question presentation,
bounded source labels, missing/contradiction summaries, and timestamps. It excludes bearer material,
raw consent records, unrestricted patient facts, internal ORM fields, event payloads, and rule code.

---

# 12. Form and Input Patterns

All forms use semantic labels/fieldsets, explicit submit buttons, accessible hints/errors, and native
controls where practical. The closed answer-type mapping is:

| Answer type | Patient control |
|---|---|
| `TEXT` | bounded text input or textarea |
| `SINGLE_CHOICE` | radio group |
| `MULTI_CHOICE` | checkbox group |
| `BOOLEAN` | explicit yes/no radio group |
| `NUMBER` | numeric input with server-provided representational bounds/unit |
| `DATE` | accessible date input with text fallback where needed |
| `DURATION` | numeric value plus configured unit selection |
| `SEVERITY_SCALE` | labeled configured scale controls; no interpretation |

The browser may enforce obvious representation constraints for usability, but FastAPI/domain
validation remains authoritative. Unknown/refusal/skip choices appear only when the question says
they are allowed. Raw clinical input is never placed in URLs.

---

# 13. One-Question Interaction Pattern

The current question is the primary task. On route/question change:

1. update the document title with non-sensitive section context;
2. move focus predictably to main/current-question heading;
3. announce server validation/status through an appropriate live region;
4. retain a visible Back/Review action when allowed;
5. retain persistent urgent help and end-session controls.

Submit is disabled only while required client representation is absent or a request is in flight.
Disablement is not the sole error explanation. Double submission is prevented in the component and
by server concurrency/idempotency semantics.

No false percentage is computed from dynamic packs. Progress may state the current section and
whether review is available.

---

# 14. Review-Draft Pattern

Review groups are keyed by canonical sections and label each item as patient-provided, reused known
history, or clarified/changed. Source labels are concise and do not expose internal provenance
metadata unnecessarily.

Unresolved required items display a link/action supplied by the server state. Optional unknown or
refused answers remain visible without shaming language. “Complete draft” sends `expected_version`.
No client calculation can enable completion when the server says it is not ready.

After completion, controls become read-only and the page says “draft,” not “diagnosis,” “assessment,”
“safe,” “cleared,” or “clinician approved.”

---

# 15. Loading, Error, Empty, and Disabled States

- Loading uses a clear text status and does not reveal stale prior-subject data.
- Initial empty means no intake and offers start only after server readiness.
- Validation errors focus/associate with the relevant question.
- Stale version errors refetch and require review; unsaved input is not silently resubmitted.
- Dependency failure offers retry after state refetch and never claims save success.
- Session/consent failure routes to the existing controlled recovery flow.
- A disabled control exposes the reason in text.
- Terminal intake state is read-only.

Error boundaries must not render raw exception messages, request bodies, or identifiers beyond the
opaque resource already in the route.

---

# 16. Accessibility

P7-C must test and preserve:

- keyboard-only start, answer, back/review, completion, and session-close journeys;
- one logical `h1`, landmarks, semantic forms, labels, descriptions, and error associations;
- deterministic focus after client navigation and failed submission;
- visible 3:1 non-text focus indication and WCAG 2.2 AA-oriented text contrast;
- at least 44px representative touch targets;
- 320px/390px reflow with no page-level horizontal overflow;
- forced-colors usability and reduced-motion behavior;
- status/error announcements that do not rely on color;
- urgent help reachable in a predictable location.

Audio is not used as an accessibility claim in P7; P12 owns governed audio guidance.

---

# 17. Mobile and Kiosk

Mobile defaults to a single column, avoids fixed-width question content, and keeps primary/secondary
actions distinguishable and reachable. Long option labels wrap without clipping.

Kiosk adaptation uses the same server contracts and privacy rules, larger targets, timeout/session
closure appropriate to deployment, and an obvious privacy exit. P7-C must not invent a device
management or kiosk credential system.

---

# 18. Language Behavior

The route reads the server-confirmed session language. Content keys resolve only against approved
available packs. English and Hindi session choices remain supported, but clinical Hindi availability
must be explicit per pack version.

Machine identifiers and answer values are language-neutral. Patient original text may carry `en` or
`hi` metadata. The browser does not machine-translate, transliterate, detect language, or activate
speech. Missing localization produces an honest unavailable state.

---

# 19. Privacy and Browser-Storage Rules

The following are prohibited for intake content or state:

```text
localStorage
sessionStorage
IndexedDB
Cache Storage
service-worker runtime caches
background sync queues
URLs/query strings
analytics/session-replay payloads
browser-readable cookies
```

Only ephemeral controlled component memory may hold a current unsent answer. It is discarded on
navigation/reload unless the server confirmed it. The BFF and FastAPI return `Cache-Control: no-store`.
Autocomplete behavior must be conservative for health-sensitive free text.

---

# 20. Security Rules

1. The bearer never enters a client component, prop, response body, log, or browser `Authorization` header.
2. Every object read/mutation is authorized server-side against the exact session/encounter.
3. UUID knowledge is never authority; cross-session IDOR attempts fail closed.
4. Mutation route handlers reject cross-origin requests and validate content type/shape/size.
5. Client input cannot choose consent purpose/scope, pack versions, rule IDs, source trust, or terminal status.
6. React renders text as text; no untrusted clinical HTML is supported.
7. Backend URLs are server-only, allowlisted by scheme/shape, and bounded by timeout.
8. Errors and logs exclude raw answers, consent bodies, tokens, and unnecessary identifiers.
9. No clinical mutation is automatically retried after an ambiguous response.

CSRF defense relies on SameSite=Strict cookies plus origin checks for mutations; backend bearer and
object-level authorization remain mandatory.

---

# 21. Telemetry Boundaries

Permitted operational attributes:

```text
request_id
operation
status
duration
safe error code
question_id / question_version
pack_id / pack_version
intake lifecycle state
```

Prohibited attributes include raw chief complaint/HPI, answers, medication/allergy/family/personal
history, known-history values, contradiction values, consent payload, bearer, cookie values, and full
request/response bodies. Do not use third-party session replay for intake.

---

# 22. Testing Strategy

## 22.1 Unit/component

- every answer type renders semantic labeled controls;
- question, history, contradiction, missing, review, loading, disabled, conflict, and error states;
- safe response validators reject malformed/extra data;
- no diagnosis or false safety language;
- route metadata/titles and focus behavior;
- no browser storage or direct FastAPI URL/bearer use in client code.

## 22.2 BFF contract

- exact backend path/method/body/header mapping;
- server-only cookie read and bearer forwarding;
- consent/session failure handling and cookie clearing;
- `no-store`, timeout, origin checks, response minimization, and error allowlist;
- no automatic mutation retry;
- malformed backend response fails safely.

## 22.3 Real API/PostgreSQL

- start uniqueness, answer atomicity, stale versions, resume, review, complete, and terminal rejection;
- exact-session authorization and cross-session IDOR denial;
- active/withdrawn consent behavior;
- one encounter/intake relationship and pack/version persistence.

## 22.4 Playwright

- full real P6 onboarding -> encounter -> intake -> review -> completed draft;
- refresh/resume from PostgreSQL;
- keyboard-only journey and logical focus;
- 320px/390px reflow and representative 44px targets;
- consent withdrawal and session close regression;
- no bearer/browser clinical persistence;
- Cache Storage remains the exact generic shell allowlist;
- offline navigation shows generic fallback and cannot submit/replay answers;
- cross-session resource attempt fails safely;
- no diagnosis wording.

Existing backend, migration, Docker/PostgreSQL, frontend, and security CI jobs remain mandatory.

---

# 23. P7-C Acceptance Mapping

| Criterion | Patient-app evidence |
|---|---|
| `AC-P7-001` | Start/resume uses deterministic structured APIs without AI dependency. |
| `AC-P7-002` | Presenting-concern control and review item. |
| `AC-P7-003` | Generic typed controls represent every HPI field. |
| `AC-P7-004` | Review groups represent required history sections. |
| `AC-P7-005` | ROS/prior-investigation typed controls and review. |
| `AC-P7-006` | Browser renders server-selected question and contains no selection policy. |
| `AC-P7-007` | Known-history confirmation preserves source and disagreement. |
| `AC-P7-008` | UI is pack-driven rather than specialty hard-coded. |
| `AC-P7-009` | AYUSH appears only for approved registered pack; no bundled invented content. |
| `AC-P7-010` | Completion and all final copy identify a non-diagnostic draft. |

Acceptance remains pending until P7-C implementation and real E2E evidence exist.

---

# 24. Deferred Features

- AI chat and `/messages`: P8.
- red flags, safety evaluation, triage, emergency thresholds: P9.
- clinician review/summary: P10.
- documents/results: P11 and later.
- speech/translation/full clinical localization: P12.
- providers/referrals: P13.
- mental-health workflow: P14.
- self-care/Ayurveda interpretation: P15.
- authenticated patient continuity, caregiver delegation, PATIENT consent: future governed work.
- encrypted offline intake: deferred pending an approved threat model.

---

# 25. Open Decisions

1. **OPEN DESIGN DECISION:** whether P7-C exposes `/api/intake/[intakeId]/abandon` and the matching
   FastAPI endpoint or leaves incomplete work `IN_PROGRESS` when a session ends.
2. **OPEN DESIGN DECISION:** approved core pack wording, option sets, requiredness, and reviewed Hindi
   localization. Engineering fixtures must be synthetic and non-production.
3. **OPEN DESIGN DECISION:** institution-specific kiosk timeout/reset policy.
4. **CLINICAL APPROVAL REQUIRED:** any clinical requiredness, severity interpretation, AYUSH field
   content, or rule capable of changing care/safety behavior.

These decisions do not block P7-A domain/schema scaffolding, but they block production activation of
the corresponding content or behavior.
