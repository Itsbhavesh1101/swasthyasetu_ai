# Patient Profile Details, First-Login Wizard, and Setup Checklist Design

## Intent

Extend the first authenticated profile setup with a mobile number, self-reported blood group, and
an explicitly synthetic Aadhaar demonstration reference. Present every initial detail in a focused,
one-question-at-a-time floating-tile wizard, then help patients discover the existing
medical-history, document, and intake features through an optional dashboard checklist. The profile
should remain quick to complete and should not turn self-reported information into verified
clinical or government identity data.

## Goals

- Store mobile number and blood group as real patient-demographic fields in PostgreSQL.
- Store only a clearly non-real Aadhaar demonstration reference; reject genuine 12-digit input.
- Collect both fields during initial profile setup and allow later edits.
- Accept mobile numbers only in normalized international E.164 form.
- Restrict blood group to `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`, or `UNKNOWN`.
- Clearly label blood group as self-reported and allow `UNKNOWN`.
- Show one initial-profile question per floating tile with Back, Next, progress, validation, and a
  final review step.
- Use the wizard only while creating the profile for the first time; later profile edits use the
  complete profile form.
- Add a dashboard checklist linking to profile, conditions, medicines, allergies, procedures,
  documents, and guided intake.
- Avoid claiming a task is complete unless the application can derive that fact from authoritative
  stored data.

## Non-goals

- Phone-based login, verification, OTP, recovery, or notifications.
- Real Aadhaar collection, validation, authentication, verification, masking, linkage, or ABDM use.
- Treating a synthetic demonstration reference as proof of identity.
- Treating the mobile number as an emergency contact.
- Verifying blood group or using it for transfusion or treatment decisions.
- Adding a separate checklist-progress table or storing cosmetic completion flags.
- Making medical-history, documents, or intake mandatory before dashboard access.

## Chosen approach

Add nullable `mobile_number`, `blood_group`, and `demo_aadhaar_reference` columns to
`patient_demographics` through one Alembic migration. Extend the immutable domain type, persistence
mapper, patient API contracts, patient-web BFF guards, TypeScript contracts, and profile form.
Existing profiles remain valid; new profile setup requires a valid mobile number, an explicit
blood-group choice including `UNKNOWN`, and a non-real demonstration reference matching
`DEMO-AADHAAR-` followed by four digits. Genuine 12-digit values are never accepted. The dashboard
renders an action-oriented checklist backed by links to existing product features; it does not
invent completion percentages.

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
- The demo Aadhaar reference accepts only `DEMO-AADHAAR-` plus four digits, is labelled synthetic,
  and is never described as verified identity, Aadhaar authentication, or ABDM linkage.
- The interface warns users not to enter a real Aadhaar number, and 12-digit input is rejected.
- Existing optimistic-concurrency behavior remains unchanged.

## First-login tile flow

When `profileComplete` is false, `/profile?setup=1` uses a keyboard-accessible floating-tile wizard.
Each tile contains one field, its label, concise helper text, an inline validation message, and
Back/Next controls. A visible progress label announces the current step through an `aria-live`
region. Enter advances only when the current field is valid; Back preserves entered values. The
sequence is:

1. full name;
2. preferred language;
3. date of birth (age is calculated and shown as supporting text);
4. sex recorded for healthcare;
5. height;
6. weight (BMI is calculated and shown as supporting text);
7. mobile number;
8. self-reported blood group;
9. synthetic Aadhaar demonstration reference;
10. optional gender identity;
11. optional pregnancy status;
12. optional city or location;
13. review and save.

Optional steps provide Skip. Closing or refreshing before the final save does not persist a partial
profile, and no values are placed in browser storage. Once saved, the user is sent to the dashboard.
Returning to `/profile` after completion shows the ordinary complete edit form, not the wizard.

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
- Adversarial tests proving real-looking 12-digit Aadhaar input is rejected and the synthetic
  reference cannot be interpreted as verified identity.
- PostgreSQL migration, constraint, persistence round-trip, and rollback checks.
- HTTP tests for authenticated profile read/update and invalid inputs.
- BFF contract and privacy tests.
- Profile-form tests for initial setup, editing, labels, normalization, and validation.
- Wizard tests for step order, Back/Next/Skip, keyboard behavior, progress announcements, preserved
  in-memory values, no browser persistence, final review, single save, and completed-profile edit
  behavior.
- Dashboard tests confirming all checklist destinations and absence of false completion claims.
- Full backend, frontend, migration, Docker/PostgreSQL, browser, and security regression gates.
