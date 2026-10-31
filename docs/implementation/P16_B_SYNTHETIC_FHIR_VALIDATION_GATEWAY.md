# P16-B — Synthetic FHIR Validation Gateway

**Status:** complete bounded detached engineering subset; live P16 remains unapproved.

The interoperability module now exposes a provider-neutral validation port, immutable validation
request/result contracts, and an offline validation gateway bound to the exact P16-A mapping context
and result. A deterministic test-only fake represents structural pass, structural rejection,
provider unavailability, and unavailable profile/package modes using content-free machine states.

Only synthetic structural mechanics can pass. `PROFILE` and `PROFILE_AND_TERMINOLOGY` always fail
closed because no approved package, terminology source, validator, or license exists. The gateway
rejects mapping drift, forged provider identity, invalid clocks, inconsistent result shapes, provider
exceptions, and protected environments before input or provider inspection.

No FHIR JSON is parsed or validated. No profile, terminology, schema package, HAPI sidecar, remote
client, endpoint, credential, network call, authorization decision, consent evaluation, patient data,
API, persistence, migration, dependency, feature flag, ABDM behavior, or runtime registration is
added.

This is offline contract evidence only. A synthetic structural pass is not FHIR conformance,
clinical validity, exchange authorization, profile approval, or proof of live `FR-FHIR-001..011` or
`AC-P16-001..010` acceptance. All existing governance restrictions remain in force.
