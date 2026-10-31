# P17-A Synthetic ABDM Boundary Contracts

**Status:** BOUNDED ENGINEERING-SYNTHETIC FOUNDATION ONLY
**Baseline:** `origin/main @ 09742c6ef7144e41d469597eb2114b63eac17788`
**Branch:** `phase/p17-a-synthetic-abdm-boundary`

## Decision

The live P17-A approved-flow interface cannot be implemented from the current repository evidence.
The ABDM/ABHA specification remains an unapproved draft, no current official protocol source or
participant role is adopted, and the identity, consent, recipient, FHIR-conformance, partner,
security, privacy and release decisions remain unresolved.

The separately authorized implementation therefore stops at an inactive, provider-neutral contract
boundary using only the `SYNTHETIC_OFFLINE_MOCK` taxonomy already proposed by Spec 21. It does not
convert that proposal into approval and does not satisfy any live P17 acceptance criterion.

## Implemented engineering evidence

- Immutable request, artifact-reference and result contracts with strict direct-constructor checks.
- Closed meaningless operation tokens and conspicuously synthetic identifiers.
- Exact request fingerprint binding, canonical UTC clocks and result chronology checks.
- Content-free accepted, rejected and unavailable outcomes with exact issue-state invariants.
- A provider-neutral adapter protocol with no implementation, endpoint or transport semantics.
- Environment validation that permits synthetic offline mechanics only in `LOCAL` and `TEST` and
  denies them in staging, pilot and production.
- Adversarial tests for forged enums, naive clocks, nested mutation, request drift, identity drift,
  mismatched outcome issues and protected environments.

## Deliberately absent

- ABHA or other real identifiers, identity linkage, discovery, QR or authentication behavior.
- Official ABDM operation names, API schemas, payloads, callbacks, consent artifacts or workflow
  semantics.
- Adapter/mock implementation, sandbox, endpoint, credential, network access or external traffic.
- FHIR resources, clinical or patient data, import/export, provenance promotion or clinical trust.
- Authorization or consent evaluation, retry policy, persistence, migration, API/BFF, UI, event,
  job, configuration wiring, feature flag, dependency or runtime/module registration.

## Acceptance truth

`FR-ABDM-001..007` and `AC-P17-001..007` remain **LIVE NOT VERIFIED**. In particular:

- an unapproved draft plus synthetic contracts does not satisfy `AC-P17-001`;
- a port without an adapter or access path does not satisfy `AC-P17-002`;
- there is no exchange on which to enforce consent, so `AC-P17-003` remains unverified;
- no mock adapter or official sandbox exists, so `AC-P17-004` remains unverified;
- no clinical data, import/export, supported official operation, retry or failure workflow exists,
  so `AC-P17-005..007` remain unverified.

All P8-C/P9-C Stage 3, P10/P11 live, P15 clinical, P16 live-conformance and P17 live-integration
restrictions remain in force.

## Next gate

An independent review may assess these detached contracts. P17-B is limited to a deterministic
zero-egress test adapter only if separately authorized. Any official sandbox or live P17 work still
requires current official sources and the accountable identity, consent, clinical, architecture,
privacy, security, partner/legal, operations and release decisions recorded in the P17 readiness
review.
