# P13-D Synthetic Notification Contracts Design

## Intent

Add content-free engineering contracts that can prove deterministic validation and simulated
failure recording without selecting a recipient, channel, provider, message, or delivery policy.

## Canonical reconciliation

The product and domain documents describe future notification intents and attempts, but P13
Readiness Gate 6 leaves delivery decisions unresolved. Its only permitted implementation subset is
adapter-neutral intent/failure contracts using non-sensitive synthetic templates, with no delivery,
provider dependency, or network. Therefore this unit models only inert metadata and simulated
failure evidence. It provides no notification port and no success or delivery receipt.

## Constraints

- No message copy/body, recipient, contact, channel, provider, endpoint, locale, preference,
  consent, retry/deadline, signature, webhook, retention, delivery semantics, or correction flow.
- No referral/patient/session/encounter/actor/institution identifiers or state mutation.
- No persistence, migration, API, event, job, worker, feature flag, dependency, network, or runtime
  registration.
- Every identifier and variable is reserved synthetic data; authority is permanently
  engineering-only, engineering-synthetic, and unverified.

## Design

`app.modules.notifications.domain` owns frozen, slotted safe-variable, template-metadata, intent,
simulated-failure, and failure-receipt contracts. Constructors enforce exact types, bounds,
reserved identifiers, UTC timestamps, fixed authority, and hidden artifact hashes.

`record_synthetic_failure` revalidates all nested inputs, requires exact notification and template
identity, exact variable-key coverage, and valid chronology, then returns an immutable receipt with
a deterministic intent fingerprint. It performs no I/O or side effect and cannot produce a success
or delivery claim.

## Non-goals and acceptance

This does not satisfy live notification or referral acceptance. Acceptance is focused adversarial
coverage, full regression, unchanged schema/dependencies/runtime, and exact-SHA CI.
`FR-NOTIF-001..006`, `FR-REF-001..013`, and `AC-P13-001..011` remain live-not-verified.
