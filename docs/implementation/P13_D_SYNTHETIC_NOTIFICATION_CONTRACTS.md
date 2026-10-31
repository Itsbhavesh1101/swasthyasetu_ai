# P13-D - Synthetic Notification Failure Contracts

**Status:** complete bounded engineering subset; live P13 notifications remain partial and
unapproved

**Baseline:** merged main at `86eaccba6010dbe64c612f7fe66bb97b33f8df70`

## Implemented

- Immutable, strictly validated engineering-only template metadata and safe symbolic variables.
- Content-free synthetic intent and simulated-failure contracts.
- Pure exact-binding recorder that validates template identity, variable keys, chronology, and
  nested values before returning a deterministic failure receipt.
- Stable content-free errors, UTC normalization, hidden hashes/fingerprints in representations, and
  adversarial direct-constructor/mutation coverage.

## Deliberately absent

There is no copy/body, recipient, contact, channel, provider, adapter, delivery port, success or
delivery state, retry/deadline policy, webhook/signature, preference/consent, or referral mutation.
There is also no API, persistence, migration, event, job, network access, dependency, feature flag,
or runtime registration.

## Governance truth

This subset implements only the P13 readiness Gate 6 allowance for adapter-neutral intent/failure
contracts with non-sensitive synthetic fixtures and no delivery. It resolves none of the pending
human decisions and cannot authorize or claim notification delivery or referral sharing.
`FR-NOTIF-001..006`, `FR-REF-001..013`, and `AC-P13-001..011` remain live-not-verified. P7 remains
the supported manual intake path; all P8-C/P9-C/P10/P11/P12 restrictions remain active.
