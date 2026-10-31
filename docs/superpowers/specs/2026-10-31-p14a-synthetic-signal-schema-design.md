# P14-A Synthetic Signal Schema Design

## Intent

Provide strict content-free engineering mechanics for synthetic extraction contracts without
representing a patient, clinical signal, or route.

## Canonical reconciliation

The master plan permits signal-schema mechanics while production policy remains blocked. P14
Readiness §§2.1 and 2.3 narrow that allowance to immutable nonmedical synthetic symbols and detached
parser/timeout mechanics. Therefore this unit uses only fixed ALPHA/BETA/GAMMA/DELTA tokens and
supplies no prompt, adapter, backstop, policy, route, or patient-facing behavior.

## Design

`app.modules.mental_health.contracts` owns frozen, slotted fixture-artifact, request, observation,
result, and failure contracts. All values are engineering-only, engineering-synthetic, and
unverified. Constructors and binding functions snapshot nested values, enforce exact identities,
canonical UTC, deadlines, deterministic signal ordering, and parsed/abstained consistency.

The parser accepts an exact dictionary/list wire shape, rejects unknown/missing fields and all
nonfixture signal values, and reports stable error codes without echoing rejected content.
`SyntheticSignalExtractorPort` defines only a provider-neutral asynchronous boundary; no adapter or
runtime registration exists.

## Non-goals and acceptance

No clinical content, patient data, screening, inference, safety backstop, route, resource, API,
persistence, UI, or activation is in scope. Acceptance requires focused adversarial tests, full
regression, unchanged dependencies/schema/runtime, and exact-SHA CI. All live P14 criteria remain
unverified.
