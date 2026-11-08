# Masked Aadhaar Profile Design

## Intent

Make the patient profile feel like a real application by asking for an Aadhaar number as exactly
12 ASCII digits, while preventing the full number from becoming durable application data. Remove
the synthetic/demo Aadhaar language from every current runtime surface. The application retains
only the last four digits and always masks them when displayed.

## Goals

- Label the field **Aadhaar number** in first-login setup and later profile editing.
- Accept exactly 12 ASCII digits with no spaces, punctuation, Unicode digits, or letters.
- Keep the complete number only in transient browser and request memory until submission finishes.
- Persist only the final four digits in PostgreSQL.
- Return only the last four digits from backend and BFF read responses.
- Display a persisted value only as `•••• •••• 1234`.
- Let a patient replace the stored last four digits by entering a new 12-digit number.
- Preserve the stored last four digits when the completed-profile editor is saved without a new
  Aadhaar number.
- Remove current user-facing `demo`, `demonstration`, and `synthetic` wording associated with the
  Aadhaar field.

## Non-goals

- Aadhaar authentication, verification, checksum validation, OTP, e-KYC, UIDAI integration, ABHA
  linkage, document upload, or identity proofing.
- Returning or reconstructing the complete number after submission.
- Searching, deduplicating, or authorizing patients by Aadhaar.
- Logging, tracing, analytics, telemetry, or browser persistence of any Aadhaar digits.
- Removing governance labels from unrelated engineering-only features. This change is limited to
  the patient-profile Aadhaar experience.
- Rewriting the already-applied `patient_details_0010` migration or historical implementation
  plans. Historical files remain immutable evidence; a forward migration removes the old runtime
  column.

## Approaches

1. **Store all 12 digits in plaintext.** Rejected because database access or a backup leak would
   expose complete government identifiers.
2. **Encrypt and retain all 12 digits.** Rejected because the product has no need to recover the
   number and does not yet have an approved encryption-key lifecycle, rotation, or recovery model.
3. **Retain only the last four digits — selected.** This supports a familiar masked profile display
   and replacement flow without retaining the complete identifier. A fingerprint is intentionally
   omitted because the application has no lookup or duplicate-detection requirement; an unkeyed
   fingerprint would be brute-forceable and a keyed fingerprint would add unnecessary secret
   management.

## Domain and persistence

`PatientDemographics` replaces `demo_aadhaar_reference` with
`aadhaar_last_four: str | None`. The value is either null or exactly four ASCII digits and remains
non-authoritative profile metadata.

A new forward-only Alembic revision after `patient_details_0010`:

1. adds nullable `patient_demographics.aadhaar_last_four VARCHAR(4)`;
2. adds a named ASCII four-digit check constraint;
3. drops `demo_aadhaar_reference` and its synthetic-format constraint;
4. deliberately does not copy old demonstration values into the new field; and
5. reverses cleanly by restoring the old nullable column and removing the new column.

Existing patient rows remain valid with a null Aadhaar suffix. No full Aadhaar number appears in
the ORM model, domain model, database schema, migration data, fixtures, or logs.

## API and BFF contract

The authenticated backend write contract accepts transient `aadhaar_number: SecretStr | None`.
When supplied, it must match `^[0-9]{12}$` and is converted immediately to its last four digits
before constructing the domain object. Backend responses expose only
`aadhaar_last_four: str | None`.

During an update, `aadhaar_number = null` preserves the currently stored suffix. The handler reads
the existing self-scoped patient before constructing replacement demographics; the existing
optimistic timestamp still rejects concurrent changes. There is no public Aadhaar lookup endpoint.

The same-origin BFF uses `aadhaarNumber` only in write submissions and `aadhaarLastFour` only in
read profiles. Both boundaries retain exact key allowlists, `no-store` responses, bounded requests,
origin validation, authenticated self-scoping, and minimized errors. Neither account nor session
responses gain Aadhaar fields.

## User experience

The first-login tile says **Aadhaar number** and uses a numeric input with a 12-character maximum.
Inline validation says **Enter a 12-digit Aadhaar number.** The review step immediately masks the
entry and never renders all 12 digits back to the page.

After saving, the completed-profile editor displays the retained value as
`Aadhaar ending in 1234` / `•••• •••• 1234`. Its input is blank and labelled **Replace Aadhaar
number (optional)**; leaving it blank preserves the stored suffix. Entering a new valid number
replaces the suffix. The UI explains, in normal product language, that only the last four digits
are retained and that the field does not verify identity.

## Security and privacy invariants

- The full number is never stored in PostgreSQL, browser storage, logs, URLs, error messages,
  analytics, telemetry, test snapshots, or response payloads.
- Validation uses ASCII `[0-9]`, not `\d`, so Unicode digit lookalikes fail closed.
- API request representations use `SecretStr` so framework/model representations redact the value.
- UI error messages never echo submitted digits.
- Masking occurs before the review tile renders and on every persisted-profile display.
- Aadhaar remains profile metadata only and grants no authentication, authorization, consent,
  clinical, ABHA, or identity-verification authority.

## Verification

- Direct-constructor tests accept four-digit suffixes and reject malformed/Unicode values.
- API tests prove 12-digit input becomes only a four-digit response and malformed values fail.
- PostgreSQL tests prove the full number is absent from persisted columns and the suffix constraint
  rejects invalid direct SQL.
- Migration tests prove a clean upgrade, existing-row compatibility, no copying of historical demo
  values, downgrade/upgrade reversibility, and a single Alembic head.
- BFF tests prove exact request/response separation, no full-number response, no-store behavior,
  anonymous denial, and preservation when no replacement is supplied.
- UI tests prove exact 12-digit validation, Unicode/space rejection, masked review, replacement,
  preservation, and absence of Aadhaar demo wording.
- Repository privacy scans reject committed 12-digit fixtures outside narrowly generated runtime
  values and confirm no Aadhaar logging or browser storage.
- Full backend, frontend, PostgreSQL, Playwright, Docker, and security gates must pass before merge.
