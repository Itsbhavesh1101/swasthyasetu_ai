# P13-A Synthetic Directory Domain Design

## Intent

Create the smallest provider/resource domain foundation that is useful before source, verification,
taxonomy, contact, routing, persistence, and release decisions exist. The types are engineering-only
and cannot represent verified or live directory truth.

## Constraints

- No provider/resource source, contact, URL, facility, geography, language, hours, availability,
  eligibility, specialty taxonomy, ranking, referral, consent, API, persistence, migration, event,
  job, feature flag, dependency, UI, or runtime registration.
- No record may claim verification, approval, clinical suitability, availability, endorsement, or
  emergency authority.
- All identifiers and labels must be unmistakably synthetic and all nested values revalidated.
- Timestamps are aware UTC; naive timestamps fail and aware non-UTC values normalize to UTC.
- P7 remains the functioning manual path and every P8-C/P9-C/P10/P11/P12/P13 live gate stays closed.

## Approaches considered

1. Implement the proposed full provider/resource lifecycle and in-memory registry. Rejected because
   lifecycle vocabulary, source truth, contact semantics, and query behavior remain unresolved.
2. Add generic extension/plugin infrastructure. Rejected because compile-time registration is the
   project rule and no runtime adapter is authorized.
3. Implement engineering-synthetic immutable records only. Selected because it creates strict,
   testable domain primitives without pretending that open policy decisions are settled.

## Design

`providers/domain.py` owns shared synthetic source evidence plus provider records because the P13
policy assigns provider/source ownership to that module. `resources/domain.py` owns a separate care
resource record and consumes only the source evidence public contract.

Every record is frozen and slotted. Authority, data classification, and verification have closed
single-value enums: `ENGINEERING_ONLY`, `ENGINEERING_SYNTHETIC`, and `UNVERIFIED`. Constructors
reject strings substituted for enums, unexpected fields, non-synthetic identifiers/labels, invalid
versions/hashes, unbounded values, duplicate codes, naive timestamps, and source timestamps later
than record creation. Nested source evidence is reconstructed so forced mutation cannot bypass
validation.

Provider records carry only an opaque synthetic record ID/version, a clearly synthetic display
label, a symbolic nonclinical service code, source evidence, and creation time. Resource records
carry the analogous symbolic resource code. They deliberately contain no contact or routing data.

## Non-goals and acceptance

This is not a registry, verified directory, clinical mapping, or P13 activation. Acceptance is
focused unit/adversarial coverage, full regression checks, unchanged dependencies/schema/runtime,
and exact-SHA CI. P13 becomes partial only for this bounded engineering foundation; all live P13
acceptance criteria remain not verified.
