# SwasthyaSetu AI
## 22 — UX and User Flows

# Document Control

**Document ID:** `SSAI-UX-022`
**Filename:** `22_UX_AND_USER_FLOWS.md`
**Status:** Canonical P7 Prerequisite / Approved for Implementation
**Version:** `1.0.0`
**Applies to:** Patient web, pseudonymous intake, and future kiosk adaptation
**Depends on:** `07_CLINICAL_INTAKE_SPEC.md`, `23_PATIENT_APP_SPEC.md`, P6 patient-web baseline

---

# 1. Purpose and Scope

This document defines the patient experience from first contact through a completed structured intake
draft. It describes user-visible flow and state, not domain internals or clinical policy. P7-C extends
the real P6 journey without weakening its session, consent, accessibility, or privacy boundaries.

Completion means “your structured draft was saved.” It never means diagnosis, treatment advice,
triage, emergency clearance, or clinician confirmation.

---

# 2. UX Principles

1. Use plain, non-diagnostic language and one clear primary action.
2. Ask only configured questions needed for the active intake.
3. Preserve patient control: review, correct, allowed skip/refusal, abandon, and end session.
4. Explain whether information came from the patient or known history.
5. Treat uncertainty and disagreement as visible states, never silently resolve them.
6. Keep urgent help prominent without inventing local resources or routing decisions.
7. Make failures honest; never claim a save, consent, or valid session without server confirmation.
8. Keep clinical state server-authoritative and out of browser persistence.
9. Preserve keyboard, screen-reader, narrow-screen, forced-colors, and reduced-motion usability.

---

# 3. User Modes

## 3.1 Pseudonymous first contact

This is the activated P7 path. It uses a real `PSEUDONYMOUS` session, SESSION consent, and an exact
session-bound encounter. It intentionally avoids unnecessary identity collection.

## 3.2 Kiosk

P7 may support the existing `KIOSK_INTAKE` encounter type with the same intake semantics. Device
reset, assisted use, and institutional deployment controls require separate operational approval.
The UI must provide large targets and a clear end-session action.

## 3.3 Authenticated continuity

Future authenticated patient continuity may resume longitudinal care through trusted `ActorContext`.
`PATIENT`-subject consent is not activated by this specification. This mode is **DEFERRED** until its
identity/consent contract is approved.

---

# 4. Current P6 Baseline

The implemented journey is:

```text
/
 -> /start
 -> /language
 -> real pseudonymous backend session
 -> /consent
 -> real SESSION / GENERAL_PRODUCT_USE / [clinical_intake] consent
 -> /encounter readiness
```

The opaque bearer remains in a transient `HttpOnly`, `SameSite=Strict`, `Path=/` cookie and is never
available to browser JavaScript. Same-origin BFF handlers forward it to FastAPI. Session closure and
consent withdrawal are real backend operations. P7-C must extend, not redesign, this flow.

---

# 5. Patient First-Contact Flow

```text
Home
 -> start explanation
 -> language choice
 -> private session confirmation
 -> bounded consent notice
 -> encounter readiness
 -> start encounter/intake
 -> presenting concern
 -> deterministic structured questions
 -> known-history confirmation when applicable
 -> contradiction/missing-information clarification
 -> review draft
 -> complete draft intake
```

At every clinical step the UI retains a visible urgent-help entry point and an end-private-session
control. P7 supplies no safety assessment or personalized urgent route.

---

# 6. Pseudonymous Onboarding

The user sees that the flow is private but not promised anonymity beyond the documented behavior.
The language choice creates the session only after explicit continuation. If session creation fails,
the user stays on `/language`, sees a generic retryable error, and no consent or encounter is implied.

Refresh uses the server-side cookie to refetch authoritative state. An expired, closed, revoked, or
invalid session returns the user to a safe onboarding state and clears invalid cookies.

---

# 7. Consent

Consent is a distinct affirmative step. The notice identifies the bounded use and the configured
scope. The checkbox/action must not be preselected. A user may withdraw consent without the UI
claiming that the session was also closed.

Starting, viewing, answering, reviewing, completing, or abandoning an intake rechecks consent. If
consent is absent or withdrawn, the UI blocks the clinical action, explains that consent is required,
and offers the consent route or end-session action. Intake state is not erased implicitly.

---

# 8. Language

Current session choices are English (`en`) and Hindi (`hi`). A selected preference controls only
approved available content. It does not guarantee a fully translated Hindi clinical questionnaire.

If an approved localized pack is unavailable, the intake must not silently machine-translate or
claim support. It shows an honest unavailable state and retains non-clinical navigation. Hinglish,
romanized Hindi, language switching during intake, ASR, TTS, and translation are **DEFERRED TO P12**.

Patient wording is preserved alongside configured display/normalized values where clinically relevant.

---

# 9. Intake Start

`/encounter` remains the readiness/start surface. Before showing “Start intake,” the server confirms:

- a valid exact session;
- active matching consent;
- an applicable current encounter/intake state, if one exists.

The primary action creates or resumes the applicable general/kiosk encounter and its unique intake.
Duplicate activation must lead to the same authorized intake, not multiple episodes. On success the
user is navigated to `/intake/{intakeId}`. An opaque ID in the URL grants no access by itself.

If another session owns the resource, the response is a generic authorization/not-found experience
without revealing existence. Unsupported encounter types or terminal encounters show a bounded
unavailable state.

---

# 10. Structured Intake

The intake begins with the presenting concern and proceeds through registered deterministic question
packs. The UI displays configured prompt content, optional context/help, answer control, progress
context, and a single primary continue/save action.

The UI does not choose questions, calculate missing fields, infer contradictions, normalize medical
meaning, or determine completion readiness. It renders server-provided typed state.

Answer success is acknowledged only after the server returns the incremented intake version. During
submission controls are disabled and duplicate activation is prevented. An ambiguous network failure
does not automatically replay the mutation; the client refetches before offering a safe retry.

---

# 11. One-Question Mode

Sensitive and complex sections use one primary question at a time. Each view provides:

- one logical `h1` and one current question heading/legend;
- brief section/progress context without false percent-complete claims;
- a correctly typed input with label, hint, and accessible error association;
- Back/Review without destroying accepted answers;
- “I don't know” or “Prefer not to answer” only when the question configuration allows it;
- Skip only when explicitly allowed by configuration;
- persistent urgent help and end-session controls.

Safety-critical requiredness is not inferred in P7. Any requirement based on a clinical safety policy
is **DEFERRED TO P9 / CLINICAL APPROVAL REQUIRED**.

---

# 12. Known-History Confirmation

When eligible known history is available, the screen shows a concise minimum-necessary value with a
source label such as “From your existing record” and its trust/confirmation distinction. The user is
asked to confirm, disagree, or answer the question where configured.

Known history never appears as if newly typed by the patient. Viewing it does not silently mark an
answer complete. Confirmation creates an intake answer reference; disagreement creates a
contradiction/update candidate. The intake UI does not overwrite the longitudinal record.

For pseudonymous encounters without a patient link, this step is naturally absent.

---

# 13. Contradiction Clarification

Contradiction screens use neutral language such as “We found two different entries” rather than
accusatory or diagnostic wording. They show only the minimum context needed to distinguish the two
referenced values and provide configured correction/clarification choices.

The UI must:

- preserve both original sources;
- never state that one is medically correct;
- allow correction of the current intake answer;
- display unresolved required clarification before completion;
- show a safe generic error if source detail is unavailable.

---

# 14. Missing-Information Clarification

When the engine reports missing configured information, the UI names the question/section in plain
language and the allowed next action. It does not claim medical danger or infer a reason beyond the
machine reason code. Required configured items cannot be bypassed; permitted unknown/refusal/waiver
paths are shown exactly as configured.

`NFR-UX-004` is satisfied by stating when the intake lacks enough configured information.

---

# 15. Review Draft

`/intake/{intakeId}/review` groups a concise draft into:

- patient-provided information;
- known-history reused information with source/trust labels;
- clarified or changed information;
- unresolved optional missing information;
- allowed unknown/refusal states.

Each editable section offers a non-destructive “Review or change” action. The page contains no
diagnosis summary, treatment advice, clinical score, safety clearance, or clinician-confirmed badge.

“Complete draft” is enabled only when the server reports completion-ready. The confirmation copy
states that information will be saved as a draft for later governed use.

---

# 16. Intake Completion

On completion, the server atomically transitions the intake to `COMPLETED`, returns `completed_at`
and the final version, and the UI shows:

- “Your intake draft has been saved”;
- what completion does and does not mean;
- a read-only review path while session authorization and consent remain valid;
- an end-private-session action.

Completion does not complete the encounter automatically and does not imply diagnosis, treatment,
triage, clinician review, or safe self-care eligibility.

---

# 17. Resume and Incomplete Flow

Refresh or return to `/encounter` refetches authorized server state. If an `IN_PROGRESS` intake exists,
the primary action is “Continue intake” and returns to the server-selected next question or review.
No answer state is reconstructed from browser storage.

`ABANDONED` is read-only and cannot be reopened in P7. Whether the user can explicitly abandon is the
open endpoint decision in `07_CLINICAL_INTAKE_SPEC.md`. A merely closed browser tab does not claim
abandonment.

---

# 18. Abandon and End-Session Flow

End session is always distinct from intake completion or abandonment. The confirmation explains that
ending the private session closes access on this device and clears session cookies; it does not claim
to delete governed server records.

If an explicit abandon action is activated in P7-C, it requires confirmation, the current intake
version, valid session/consent, and a server-confirmed terminal response. Failure leaves the displayed
state unconfirmed and offers refetch/retry. No browser-only status mutation is allowed.

---

# 19. Error and Degraded Flow

| Condition | UX response |
|---|---|
| session missing/expired | Clear invalid cookies, return to language/start, do not expose resource state. |
| consent missing/withdrawn | Block intake operation and link to consent/end-session choices. |
| stale version | Refetch, explain that the draft changed, and require review before resubmission. |
| validation error | Associate a plain error with the relevant field; do not echo unrelated sensitive data. |
| backend unavailable | Honest temporary-unavailable state; no success claim or automatic mutation replay. |
| pack/localization unavailable | Bounded unavailable state; do not invent questions or translations. |
| forbidden/not found | Generic safe state that does not reveal another subject's resource. |

Optional AI, OCR, speech, QML, and provider services are not required for P7 and cannot block its
structured text/touch path.

---

# 20. Offline Behavior

Offline behavior remains the P6 generic fallback:

- no intake start or continuation;
- no clinical response cache;
- no answer queue, background sync, or mutation replay;
- no assertion that session or consent remains valid;
- no cached draft or known-history data;
- no invented urgent resource.

The offline page tells the user to reconnect and notes that clinical workflows are unavailable.

---

# 21. Urgent-Help Behavior

Urgent help remains visible and keyboard reachable on start, question, review, completion, error, and
offline surfaces. P7 uses the existing generic safe wording. It must not claim that intake completion
has evaluated emergencies, invent contact details, or make a personalized route. Real emergency
criteria and routing are P9-governed.

---

# 22. Accessibility

P7-C carries forward the P6 baseline:

- semantic header/navigation/main/footer landmarks;
- one logical page `h1` and semantic form groups;
- programmatic labels, instructions, status, and error associations;
- keyboard-only completion with visible focus and deterministic route focus;
- 44px representative targets;
- 320px and 390px reflow without horizontal page scrolling;
- WCAG 2.2 AA-oriented contrast, forced-colors, and reduced-motion support;
- errors not communicated by color alone;
- focus moves to validation summary/current question only when useful and predictable;
- progress descriptions remain understandable without visual layout.

Audio guidance is not falsely activated; it remains P12 work.

---

# 23. Mobile and Kiosk

Mobile uses a single-column question layout, reachable primary action, short readable line lengths,
and no hover-only affordance. Kiosk uses the same contracts with larger targets and clear privacy/end
session controls. Neither mode stores clinical draft state locally.

Shared/public devices must not display a prior subject's intake after session closure. Device-level
kiosk hardening is a deployment concern and **OPEN DESIGN DECISION**.

---

# 24. Multilingual Boundaries

Question definitions reference content keys; language packs own approved wording. IDs, answer values,
rules, and persisted machine state are language-neutral. Original patient text records its language
code where known.

No UI may claim medically reviewed Hindi content until the corresponding pack/version is approved.
Fallback language behavior must be explicit and consented where it affects comprehension. P12 owns
speech, machine translation, transliteration, and language-detection infrastructure.

---

# 25. Privacy Expectations

The UI collects the minimum configured data for the current purpose. It does not expose the bearer,
put intake content in URLs/query strings, log raw answers, or persist health data in localStorage,
sessionStorage, IndexedDB, Cache Storage, analytics payloads, or service-worker queues.

Browser history contains only opaque route IDs. Pages and BFF responses use `no-store`. Operational
telemetry uses request/operation/status/duration/error codes and non-sensitive machine IDs only.

---

# 26. Future Authenticated Continuity

Future continuity may provide patient-linked known history and cross-session resume through trusted
identity. It must use server-side patient-self authorization, a separately approved consent contract,
and the same source/provenance distinctions. P7 does not infer or activate this from pseudonymous
session creation.

---

# 27. Deferred Future Flows

- conversational free-text extraction: P8;
- physical safety/triage and personalized urgent routing: P9;
- clinician summary/review: P10;
- document upload/OCR: P11;
- speech/translation: P12;
- provider/referral activation: P13;
- mental-health workflow: P14;
- Ayurveda interpretation/self-care: P15;
- caregiver/delegated access and patient-subject consent: future governed work.

The existing `/documents`, `/results`, and `/referrals` routes remain honest unavailable surfaces.

---

# 28. Screen and State Inventory

| Route/surface | Primary states |
|---|---|
| `/` | introduction, primary start, urgent help |
| `/start` | private-session explanation, continue |
| `/language` | language choice, creating, creation error |
| `/consent` | notice, granting, granted, revoked, unavailable |
| `/encounter` | checking, not ready, ready to start, resumable, completed, unavailable |
| `/intake/{intakeId}` | loading, current question, saving, validation error, conflict/refetch, clarification, unavailable |
| `/intake/{intakeId}/review` | loading, grouped draft, incomplete, completion-ready, completing, completed/read-only, unavailable |
| `/offline` | generic reconnect guidance only |
| global shell | urgent help, end session, skip navigation, route focus |

State is derived from authorized server responses, never URL possession or browser persistence.

---

# 29. Acceptance Traceability

| Acceptance | UX evidence planned for P7-C |
|---|---|
| `AC-P7-001` | User starts/resumes through structured BFF/API without LLM. |
| `AC-P7-002` | Presenting concern question and review representation. |
| `AC-P7-003` | Configured HPI questions and review groups. |
| `AC-P7-004` | History sections render typed questions and source labels. |
| `AC-P7-005` | ROS and prior-investigation sections render without interpretation. |
| `AC-P7-006` | UI follows deterministic server-selected next question. |
| `AC-P7-007` | Known history is explicitly shown and confirmed/disagreed. |
| `AC-P7-008` | Pack identity/version is transparent to state, not hard-coded page branching. |
| `AC-P7-009` | AYUSH UI appears only for an approved enabled pack; no invented content. |
| `AC-P7-010` | Review/completion copy consistently says draft and contains no diagnosis. |

P7-C implements these flows with an explicitly gated English engineering fixture. Production
clinical-content approval, Hindi clinical localization, AYUSH content, and safety interpretation
remain unavailable and cannot be inferred from engineering acceptance evidence.
