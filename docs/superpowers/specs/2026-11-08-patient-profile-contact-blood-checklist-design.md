# Patient Profile Contact, Blood Group, and Setup Checklist Design

## Intent

Extend the first authenticated profile setup with a mobile number and self-reported blood group,
then help patients discover the existing medical-history, document, and intake features through an
optional dashboard checklist. The profile should remain quick to complete and should not turn
self-reported information into verified clinical data.

## Goals

- Store mobile number and blood group as real patient-demographic fields in PostgreSQL.
- Collect both fields during initial profile setup and allow later edits.
- Accept mobile numbers only in normalized international E.164 form.
- Restrict blood group to `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`, or `UNKNOWN`.
- Clearly label blood group as self-reported and allow `UNKNOWN`.
- Add a dashboard checklist linking to profile, conditions, medicines, allergies, procedures,
  documents, and guided intake.
- Avoid claiming a task is complete unless the application can derive that fact from authoritative
  stored data.

## Non-goals

- Phone-based login, verification, OTP, recovery, or notifications.
- Treating the mobile number as an emergency contact.
- Verifying blood group or using it for transfusion or treatment decisions.
- Adding a separate checklist-progress table or storing cosmetic completion flags.
- Making medical-history, documents, or intake mandatory before dashboard access.

## Chosen approach

Add nullable `mobile_number` and `blood_group` columns to `patient_demographics` through one
Alembic migration. Extend the immutable domain type, persistence mapper, patient API contracts,
patient-web BFF guards, TypeScript contracts, and profile form. Existing profiles remain valid;
new profile setup requires a valid mobile number and an explicit blood-group choice, including
`UNKNOWN`. The dashboard renders an action-oriented checklist backed by links to existing product
features; it does not invent completion percentages.

## Approaches considered

1. **Real profile fields plus action checklist — selected.** This keeps patient data authoritative
   and makes existing features easier to discover without duplicating their state.
2. **Persisted onboarding checklist.** Rejected because it creates synchronization problems and an
   unnecessary table when the underlying medical records remain the source of truth.
3. **Profile fields only.** Rejected because it does not provide the guided post-registration setup
   requested for the patient experience.

## Validation and privacy

- Mobile numbers are trimmed and must match E.164 (`+` followed by 7–15 digits, first digit 1–9).
- Mobile numbers never appear in logs, URLs, navigation, or unauthenticated responses.
- Blood group is a closed enum with `UNKNOWN`; arbitrary text is rejected at domain, API, BFF, and
  database boundaries.
- The UI states that blood group is self-reported and must not be used for emergency decisions.
- Existing optimistic-concurrency behavior remains unchanged.

## Dashboard behavior

After profile completion, the dashboard shows a “Complete your health record” section with links to:

- review personal profile;
- add conditions;
- add medicines;
- add allergies;
- add procedures;
- upload reports or prescriptions;
- complete a guided health journey.

These are optional actions. The section uses action language rather than checkmarks or percentages
unless actual stored data is available to prove completion.

## Verification

- Direct-constructor domain tests for valid and invalid mobile numbers and blood groups.
- PostgreSQL migration, constraint, persistence round-trip, and rollback checks.
- HTTP tests for authenticated profile read/update and invalid inputs.
- BFF contract and privacy tests.
- Profile-form tests for initial setup, editing, labels, normalization, and validation.
- Dashboard tests confirming all checklist destinations and absence of false completion claims.
- Full backend, frontend, migration, Docker/PostgreSQL, browser, and security regression gates.
