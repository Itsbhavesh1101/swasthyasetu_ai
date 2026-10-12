# SwasthyaSetu AI
## 06 — API Contracts Specification

**Document ID:** `SSAI-API-006`  
**Filename:** `06_API_CONTRACTS.md`  
**Status:** Foundation / API Source of Truth  
**Version:** `1.0.0-draft`  
**Protocol:** HTTPS REST initially  
**Base prefix:** `/api/v1`

---

# 1. Purpose

This document defines the initial HTTP API contract strategy for SwasthyaSetu AI.

It establishes:

- API versioning;
- common request/response conventions;
- authorization expectations;
- endpoint families;
- error envelopes;
- pagination;
- idempotency;
- async job behavior;
- patient/clinician/admin/research/interoperability boundaries.

Exact payloads may be refined by module-specific specs, but Codex must not create incompatible ad hoc contracts.

---

# 2. API Principles

- **API-P-001:** all normal REST endpoints use `/api/v1`.
- **API-P-002:** requests/responses are typed.
- **API-P-003:** ORM models never leak directly through HTTP.
- **API-P-004:** authorization is enforced server-side.
- **API-P-005:** errors use one stable envelope.
- **API-P-006:** side-effecting retry-prone operations use idempotency where needed.
- **API-P-007:** safety/risk outputs are explicitly decision-support, not diagnosis.
- **API-P-008:** external integrations remain behind application services/adapters.
- **API-P-009:** long-running work returns explicit processing state.
- **API-P-010:** patient-facing APIs never fabricate providers, remedies, or safety outcomes.

---

# 3. Common Headers

Recommended:

```text
Authorization: Bearer <token>
X-Request-ID: <optional-client-generated-id>
Idempotency-Key: <opaque-key>
Content-Type: application/json
```

File uploads may use `multipart/form-data` or a presigned-upload workflow.

---

# 4. Error Envelope

Canonical response:

```json
{
  "error": {
    "code": "CONSENT_REQUIRED",
    "message": "Consent is required for this operation.",
    "request_id": "req_...",
    "details": {}
  }
}
```

Rules:

- `code` is stable and machine-readable;
- `message` is safe to expose;
- `details` must not leak stack traces/secrets;
- internal exception class names are not public API.

---

# 5. Initial Error Codes

```text
VALIDATION_ERROR
AUTHENTICATION_REQUIRED
AUTHORIZATION_DENIED
RESOURCE_NOT_FOUND
RESOURCE_CONFLICT
INVALID_STATE_TRANSITION
FEATURE_DISABLED
CONSENT_REQUIRED
SESSION_EXPIRED
RATE_LIMITED
DEPENDENCY_TIMEOUT
DEPENDENCY_UNAVAILABLE
PROCESSING_FAILED
POLICY_UNAVAILABLE
INSUFFICIENT_INFORMATION
UNSUPPORTED_MEDIA_TYPE
PAYLOAD_TOO_LARGE
```

Modules may extend this registry through documented contracts.

---

# 6. HTTP Status Mapping

Typical:

```text
200 OK
201 Created
202 Accepted
204 No Content
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
413 Payload Too Large
415 Unsupported Media Type
422 Validation Error
429 Too Many Requests
503 Service Unavailable
```

Do not always return `200` with an internal success flag.

---

# 7. Pagination

Potentially large collections use a consistent bounded pagination model.

Initial preference: opaque cursor pagination.

Example:

```text
GET /api/v1/providers?limit=20&cursor=...
```

Response:

```json
{
  "items": [],
  "next_cursor": null
}
```

Rules:

- bounded `limit`;
- deterministic ordering;
- cursor opaque to client.

---

# 8. Health APIs

## GET `/health/live`

Response:

```json
{"status": "ok"}
```

Purpose: process liveness.

## GET `/health/ready`

Example:

```json
{
  "status": "ready",
  "required": {
    "database": "ok"
  },
  "optional": {
    "llm": "degraded",
    "ocr": "ok"
  }
}
```

Optional AI/QML dependencies should not block readiness unless an enabled critical feature explicitly requires them.

---

# 9. Session APIs

## POST `/api/v1/sessions`

Purpose: create a pseudonymous or kiosk session in P4-A. Authenticated creation is deferred to P4-B.

Request:

```json
{
  "session_type": "PSEUDONYMOUS",
  "language_preference": "en"
}
```

Response `201`:

```json
{
  "session_id": "uuid",
  "session_token": "opaque",
  "session_type": "PSEUDONYMOUS",
  "status": "ACTIVE",
  "expires_at": "ISO-8601"
}
```

Rules:

- pseudonymous session must not require a name;
- request objects reject unrecognized identity fields such as `name`;
- the opaque token is returned only by this creation response;
- active and recovery token hashes are never returned;
- all session responses use `Cache-Control: no-store`.

## GET `/api/v1/sessions/{session_id}`

Returns authorized session metadata.

Requires `Authorization: Bearer <session_token>`. Unknown IDs, wrong tokens, and cross-session
tokens return the same `AUTHENTICATION_REQUIRED` response. Expired sessions return
`SESSION_EXPIRED`; closed/revoked sessions are not treated as active. Tokens are not accepted in
paths, query parameters, or cookies.

## POST `/api/v1/sessions/{session_id}/close`

Transitions session to closed state.

Requires the exact session bearer token. Only `ACTIVE -> CLOSED` is valid. Repeat close returns
`INVALID_STATE_TRANSITION`; an expired close returns `SESSION_EXPIRED`.

---

# 10. Consent APIs

## POST `/api/v1/consents`

Creates a purpose-specific consent grant. SESSION subjects require the exact session bearer token
and validation through `sessions.validate`. ACTOR subjects require a trusted server-side
`ActorContext` for the same actor. PATIENT subjects remain deferred pending the governed onboarding
authorization flow and return `VALIDATION_ERROR`. The server
derives actor attribution; `actor_id`, metadata, and arbitrary extra fields are rejected.

Request:

```json
{
  "subject_type": "SESSION",
  "subject_id": "uuid",
  "purpose": "GENERAL_PRODUCT_USE",
  "scope": ["clinical_intake"],
  "notice_version": "privacy-v1"
}
```

Response:

```json
{
  "consent_id": "uuid",
  "status": "GRANTED",
  "purpose": "GENERAL_PRODUCT_USE",
  "notice_version": "privacy-v1",
  "granted_at": "ISO-8601"
}
```

## POST `/api/v1/consents/{consent_id}/revoke`

Revokes an authorized active grant. Repeat revocation fails with `INVALID_STATE_TRANSITION` and
time-expired consent cannot be revoked as active consent. The reason is a bounded machine code,
not free text.

Request:

```json
{
  "reason": "user_requested"
}
```

## GET `/api/v1/consents`

Requires both `subject_type` and `subject_id`; unscoped listing is rejected. Optional purpose and
status filters may further narrow the authorized subject-scoped result. SESSION and ACTOR subject
authorization follows the same rules as grant/revoke, and cross-subject access fails closed.

All consent success and error responses use `Cache-Control: no-store`. No public consent-check,
get-by-ID, update, or delete endpoint exists. Internal callers use the centralized `consent.check`
capability, which requires exact subject and purpose plus requested-scope subset coverage. General
product consent never implies `REFERRAL_SHARING`; referral workflows must request that purpose
explicitly when they are implemented.

---

# 11. Patient APIs

## POST `/api/v1/patients`

Minimal initial request:

```json
{
  "preferred_language": "en",
  "demographics": {}
}
```

Response:

```json
{
  "patient_id": "uuid",
  "status": "ACTIVE",
  "created_at": "ISO-8601"
}
```

## GET `/api/v1/patients/{patient_id}`

Requires authenticated `patient:read:self` authorization with a matching trusted subject. Returns
the patient profile without identifier values. `POST /patients` derives `patient_id` from the same
trusted subject and rejects client-selected IDs.

## GET `/api/v1/patients/{patient_id}/facts`

Returns bounded, self-authorized fact summaries. Optional `fact_type`, `verification_state`,
`limit`, and opaque `cursor` filters are supported. Raw structured values and provenance source
text/references are excluded.

## GET `/api/v1/patients/{patient_id}/timeline`

Query parameters:

```text
limit?
cursor?
entry_type?
from?
to?
```

Returns a paginated longitudinal read model containing only `CLINICAL_FACT` and `ENCOUNTER`
entries. Ordering is `occurred_at DESC, entry_type ASC, entry_id ASC`; timestamps must be UTC and
the cursor is an opaque, versioned keyset position.

---

# 12. Encounter APIs

## POST `/api/v1/encounters`

Request:

```json
{
  "session_id": "uuid",
  "patient_id": "uuid-or-null",
  "encounter_type": "GENERAL_INTAKE"
}
```

Response:

```json
{
  "encounter_id": "uuid",
  "status": "CREATED",
  "started_at": "ISO-8601"
}
```

## GET `/api/v1/encounters/{encounter_id}`

Returns encounter metadata/state. Patient-bound access requires trusted self authorization;
pseudonymous access validates the exact bearer against the encounter session.

## POST `/api/v1/encounters/{encounter_id}/complete`

Validates state transition before completing.

## POST `/api/v1/encounters/{encounter_id}/abandon`

Marks incomplete encounter as abandoned.

---

# 13. Clinical Intake APIs

## POST `/api/v1/encounters/{encounter_id}/intake`

Starts intake.

Response:

```json
{
  "intake_id": "uuid",
  "status": "IN_PROGRESS",
  "next_question": {}
}
```

## GET `/api/v1/intakes/{intake_id}`

Returns structured intake state.

## POST `/api/v1/intakes/{intake_id}/answers`

Request:

```json
{
  "question_id": "hpi.duration",
  "answer": {
    "value": "2 days"
  },
  "source_type": "PATIENT_TOUCH"
}
```

Response:

```json
{
  "status": "IN_PROGRESS",
  "next_question": {},
  "missing_information": [],
  "requires_safety_evaluation": false
}
```

## POST `/api/v1/intakes/{intake_id}/messages`

AI-assisted conversational input.

Request:

```json
{
  "text": "I have had fever for two days."
}
```

Response:

```json
{
  "message_id": "uuid",
  "candidate_updates": [],
  "next_question": {},
  "extraction_status": "VALID"
}
```

This endpoint must not return an authoritative diagnosis.

## POST `/api/v1/intakes/{intake_id}/complete`

Transitions the intake to its next governed state.

---

# 14. Physical Safety API

## POST `/api/v1/encounters/{encounter_id}/safety/evaluate`

Server should load structured safety inputs from authoritative state rather than trust arbitrary client-supplied red-flag decisions.

Response:

```json
{
  "decision_id": "uuid",
  "route": "CLARIFICATION_REQUIRED",
  "reason_codes": ["MISSING_REQUIRED_SIGNAL"],
  "policy_id": "physical-red-flags",
  "policy_version": "dev-synthetic-v1",
  "requires_clarification": true,
  "blocks_self_care": true
}
```

Rules:

- policy version required;
- response is routing/safety support, not diagnosis;
- synthetic policy cannot be presented as real clinical policy in production.

---

# 15. Clinical Fact Review APIs

## GET `/api/v1/patients/{patient_id}/facts`

Authorized, filtered fact list.

## POST `/api/v1/clinical-facts/{fact_id}/confirm`

Clinician/governed confirmation.

## POST `/api/v1/clinical-facts/{fact_id}/reject`

Rejects candidate/extracted fact while preserving provenance.

## POST `/api/v1/clinical-facts/{fact_id}/correct`

Creates a corrected/superseding fact rather than erasing source history.

---

# 16. Summary APIs

## POST `/api/v1/encounters/{encounter_id}/summaries`

Generates draft summary from structured facts only.

Can return `201`/`200` synchronously or `202` if generation becomes async.

## GET `/api/v1/encounters/{encounter_id}/summaries/latest`

Returns latest draft/confirmed summary.

## POST `/api/v1/summaries/{summary_id}/confirm`

Clinician-only.

## POST `/api/v1/summaries/{summary_id}/revise`

Creates a new summary version.

---

# 17. Document Upload APIs

The detailed upload pattern is finalized in the OCR/document spec.

Two allowed initial patterns:

## Pattern A — Direct multipart

### POST `/api/v1/documents`

Response:

```json
{
  "document_id": "uuid",
  "status": "QUEUED"
}
```

## Pattern B — Presigned upload

### POST `/api/v1/documents/upload-intents`

Returns controlled upload destination.

### POST `/api/v1/documents/{document_id}/finalize`

Finalizes uploaded object metadata.

---

# 18. Document Status APIs

## GET `/api/v1/documents/{document_id}`

Example:

```json
{
  "document_id": "uuid",
  "document_type": "LAB_REPORT",
  "status": "PROCESSING",
  "uploaded_at": "ISO-8601",
  "processing": {
    "stage": "OCR"
  }
}
```

## GET `/api/v1/documents/{document_id}/extractions`

Authorized view of candidate structured data.

## POST `/api/v1/documents/{document_id}/reprocess`

Authorized/idempotent processing retry.

---

# 19. Speech API

Potential initial endpoint:

## POST `/api/v1/speech/transcriptions`

Request: audio payload or authorized storage reference.

Response:

```json
{
  "transcription_id": "uuid",
  "text": "...",
  "language": "hi",
  "confidence": 0.91
}
```

Rules:

- failed transcription does not become clinical fact;
- original audio retention is separately governed.

---

# 20. Provider Search API

## GET `/api/v1/providers`

Possible query parameters:

```text
care_category?
specialty?
city?
language?
teleconsultation?
limit?
cursor?
```

Response:

```json
{
  "items": [
    {
      "provider_id": "uuid",
      "display_name": "Example",
      "specialties": ["..."],
      "languages": ["en", "hi"],
      "verification_status": "ACTIVE",
      "verified_at": "ISO-8601"
    }
  ],
  "next_cursor": null
}
```

Only registry-backed data may be returned.

---

# 21. Resource APIs

## GET `/api/v1/resources`

Filters:

```text
resource_type
geography
language
institution_id
```

## POST `/api/v1/urgent`

Returns urgent/crisis resources without normal LLM dependency.

This endpoint should work even when the conversational model is unavailable.

---

# 22. Referral APIs

## POST `/api/v1/referrals`

Request:

```json
{
  "encounter_id": "uuid",
  "destination_type": "PROVIDER",
  "destination_id": "uuid",
  "consent_id": "uuid",
  "priority": "ROUTINE"
}
```

Header:

```text
Idempotency-Key: <opaque>
```

Response:

```json
{
  "referral_id": "uuid",
  "status": "CONSENTED",
  "created_at": "ISO-8601"
}
```

Rules:

- consent validated server-side;
- destination must be valid/eligible;
- full chat transcript excluded by default.

## GET `/api/v1/referrals/{referral_id}`

Authorized referral state.

## GET `/api/v1/referrals/status/{scoped_token}`

Optional pseudonymous status route.

## POST `/api/v1/referrals/{referral_id}/cancel`

Allowed only for valid state transitions.

---

# 23. Referral Webhooks

Potential:

## POST `/api/v1/webhooks/referrals/{adapter}`

Must enforce:

- signature validation;
- timestamp/replay protection;
- schema validation;
- idempotency;
- state transition validation.

---

# 24. Mental-Health APIs

## POST `/api/v1/mental-health/sessions`

May create mental-health-specific workflow state or reuse base sessions.

## POST `/api/v1/mental-health/sessions/{session_id}/messages`

Request:

```json
{
  "text": "..."
}
```

Response:

```json
{
  "assistant_message": "...",
  "route_state": "CLARIFICATION_REQUIRED",
  "urgent_help_available": true,
  "resources": []
}
```

Rules:

- route state is deterministic-policy output;
- assistant text is non-diagnostic;
- crisis resources can be returned even when model extraction fails.

## GET `/api/v1/mental-health/sessions/{session_id}/resources`

Returns verified current resources.

---

# 25. Self-Care API

## POST `/api/v1/encounters/{encounter_id}/self-care/evaluate`

Server loads relevant patient/encounter context.

Blocked response:

```json
{
  "eligible": false,
  "reason_codes": ["SAFETY_BLOCK"],
  "guidance": []
}
```

Eligible response:

```json
{
  "eligible": true,
  "reason_codes": [],
  "guidance": [
    {
      "guidance_id": "uuid",
      "version": "v1",
      "title": "...",
      "supportive_actions": [],
      "contraindications": [],
      "duration_limit": null,
      "escalation_conditions": []
    }
  ]
}
```

Only approved/versioned guidance may be returned.

---

# 26. Clinician API

Composite clinician reads may use a dedicated namespace.

## GET `/api/v1/clinician/encounters`

Returns clinician-authorized queue.

## GET `/api/v1/clinician/patients/{patient_id}/overview`

Example:

```json
{
  "patient": {},
  "current_encounter": {},
  "medications": [],
  "allergies": [],
  "timeline": [],
  "safety_decisions": [],
  "latest_summary": {},
  "feature_panels": {}
}
```

Composite read models do not imply cross-module write ownership.

---

# 27. Admin APIs

Prefix:

```text
/api/v1/admin
```

Potential endpoints:

```text
GET/POST/PATCH /admin/providers
GET/POST/PATCH /admin/resources
GET /admin/policies
GET /admin/models
GET /admin/referrals
GET /admin/audit
GET/PATCH /admin/feature-flags
```

Rules:

- strong authorization;
- changes audited;
- ordinary admin cannot bypass clinical-governance rules.

---

# 28. FHIR APIs

## POST `/api/v1/interoperability/fhir/export`

Request:

```json
{
  "patient_id": "uuid",
  "resource_types": ["Patient", "Encounter", "Observation"]
}
```

Response:

```json
{
  "exchange_id": "uuid",
  "bundle": {}
}
```

## POST `/api/v1/interoperability/fhir/import`

Requires authorization and provenance.

FHIR validation failures are explicit.

---

# 29. ABDM APIs

Exact production-facing ABDM routes are deferred to `21_ABDM_INTEGRATION_SPEC.md`.

Do not invent current ABDM semantics in this contract.

---

# 30. Risk / Model API

Potential governed endpoint:

## POST `/api/v1/risk-assessments`

Request references an approved model task and server-side data.

Response:

```json
{
  "assessment_id": "uuid",
  "task": "example",
  "model_id": "model-x",
  "model_version": "1.0",
  "input_quality": "VALID",
  "risk_probability": 0.71,
  "risk_band": "ELEVATED",
  "calibration_version": "cal-v1"
}
```

Rules:

- not diagnosis;
- only approved model versions;
- cannot override urgent deterministic safety.

---

# 31. Research APIs

Prefix:

```text
/api/v1/research
```

Potential endpoints:

```text
POST /research/datasets/validate
POST /research/experiments
GET  /research/experiments/{run_id}
GET  /research/models
POST /research/models/{model_id}/promote
```

Research endpoints are role-restricted.

Model promotion requires governance.

---

# 32. Async Job Contract

Long-running actions return `202 Accepted`.

Example:

```json
{
  "job_id": "uuid",
  "status": "QUEUED",
  "resource_ref": {
    "type": "document",
    "id": "uuid"
  }
}
```

Async UI must display honest processing state.

---

# 33. Idempotency Contract

For side-effecting operations:

- accept `Idempotency-Key`;
- scope key to actor + operation;
- same key + equivalent request returns same logical result;
- same key + conflicting request returns `409`.

Likely use cases:

```text
referral creation
external sync
notification enqueue
upload finalization
webhook processing
```

---

# 34. Authorization Contract

Every mature endpoint spec should declare:

```text
authentication
required roles/permissions
object-level access rule
consent requirement
```

Examples:

```text
patient self read -> patient:read:self
clinician overview -> encounter:read:assigned
provider admin -> provider:manage
```

The backend guard is authoritative: `401 AUTHENTICATION_REQUIRED` means there is no valid trusted
authenticated actor, while `403 AUTHORIZATION_DENIED` means an authenticated actor lacks the
permission, object scope, or required authentication strength. Frontend visibility is not a
security boundary. Administrative authorization requires a trusted provider principal indicating
MFA was satisfied; client headers cannot supply actor identity, roles, or MFA state.

P4-B adds no identity HTTP endpoint. The external IdP remains unconfigured and replaceable behind
the provider-neutral authentication contract.

---

# 35. Feature Disabled Behavior

Final status code policy belongs in `33_ERROR_HANDLING_POLICY.md`.

The API must at minimum return a stable:

```text
FEATURE_DISABLED
```

error rather than pretending the feature worked.

---

# 36. Versioning Rules

Breaking public contract changes require:

- explicit migration;
- coordinated consumer update;
- or a new API version.

HTTP API versioning is separate from event-schema versioning.

---

# 37. Date/Time Format

Use ISO-8601/RFC3339 with timezone.

Persistence normalizes authoritative timestamps to UTC.

---

# 38. Enum Serialization

Use stable symbolic values such as:

```text
IN_PROGRESS
CLINICIAN_CONFIRMED
PRIORITY_REVIEW
```

Do not expose internal DB-enum implementation details.

---

# 39. Validation Boundary

Pydantic performs structural validation.

Application/domain services enforce business validation.

Example:

```text
UUID shape -> schema validation
provider active -> business validation
consent covers referral -> consent/application validation
```

---

# 40. Client-Generated IDs

Server generates authoritative IDs by default.

Client-generated IDs are only allowed for specifically designed idempotent/offline workflows.

---

# 41. Partial Updates

Use `PATCH` where partial update is appropriate.

Do not expose unrestricted patching of safety-critical policy/content.

---

# 42. File Download

Sensitive documents should use authorized streaming or short-lived signed access URLs.

Never expose permanent public object-storage URLs.

---

# 43. API Logging

Log:

```text
method
route
status
latency
request_id
actor class
error code
```

Do not log full sensitive bodies by default.

---

# 44. Rate Limit Response

Use `429 RATE_LIMITED`.

Retry hints may be returned when useful.

---

# 45. Dependency Failure Response

Typical:

```json
{
  "error": {
    "code": "DEPENDENCY_UNAVAILABLE",
    "message": "This feature is temporarily unavailable.",
    "request_id": "..."
  }
}
```

Safety-critical flows may additionally include an approved fallback action/resource.

---

# 46. Contract Tests

Every public endpoint should eventually test:

- success;
- validation error;
- authentication;
- authorization;
- not found;
- conflict/state transition;
- dependency failure where relevant;
- idempotency where relevant.

Safety endpoints additionally test deterministic precedence.

---

# 47. OpenAPI

FastAPI-generated OpenAPI is treated as contract evidence.

Frontend types should be generated or validated from OpenAPI where feasible.

Avoid incompatible hand-written duplicate contracts.

---

# 48. New Feature API Rule

A new feature should normally add:

```text
/api/v1/<feature>
```

or extend an existing owning resource.

Do not create new top-level API namespaces casually.

---

# 49. Non-Goals

This initial contract does not define:

- GraphQL;
- gRPC;
- WebSocket-first architecture;
- current production ABDM routes;
- final auth-provider token claims;
- final specialty taxonomy;
- production clinical-policy payloads.

These require later specifications.

---

# 50. API Invariants

```text
1. Public responses are typed.
2. ORM entities do not leak.
3. Backend enforces authorization.
4. Safety decisions are not diagnoses.
5. Predictive risk is not diagnosis.
6. Provider/resource truth is registry-backed.
7. Self-care output is approved-knowledge-backed.
8. Referral sends require consent.
9. Async operations expose honest status.
10. Errors are stable and privacy-safe.
```
