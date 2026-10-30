# P13-B Synthetic Symbolic Routing and Abstention Design

## Intent

Add the smallest deterministic P13-B engineering primitive allowed while the real taxonomy,
clinical mapping, source registry, geography, eligibility, ranking, and release decisions remain
unapproved. The primitive maps one reserved synthetic signal to one reserved synthetic service code
or abstains. It cannot select a provider or produce a patient-facing result.

## Constraints

- Inputs, policies, rules, and outputs are engineering-synthetic and permanently unverified.
- Matching is exact and case-sensitive. No free text, symptom, clinical fact, model output, fuzzy
  matching, threshold, inference, default route, or fallback is accepted.
- Zero matches and multiple matches abstain. Rule order never resolves ambiguity or ranks services.
- No provider record, contact, resource, geography, eligibility, availability, safety route,
  urgency, clinical category, patient/subject, persistence, API, UI, or runtime registration.
- P7 remains the functioning manual path; all P8-C/P9-C/P10/P11/P12 live restrictions remain.

## Approaches considered

1. Implement the documented future directory query and specialty-first routing. Rejected because
   its taxonomy, clinical authority, verified sources, filters, ranking, and release scope are open.
2. Query P13-A records in memory. Rejected because that could make unverified synthetic records look
   selectable and would prematurely define registry/query semantics.
3. Implement an exact symbolic evaluator detached from records and runtime. Selected because it
   proves deterministic matching, ambiguity handling, and fail-closed behavior without clinical or
   provider authority.

## Design

`app.modules.providers.routing` owns frozen, slotted request, rule, policy, and decision contracts.
Reserved prefixes make every identifier visibly synthetic. Policies bind an immutable version and
SHA-256 artifact identity; all timestamps require timezone awareness and normalize to UTC. Closed
authority, classification, and verification states remain `ENGINEERING_ONLY`,
`ENGINEERING_SYNTHETIC`, and `UNVERIFIED`.

The pure `evaluate_symbolic_route` function revalidates nested objects, validates temporal order,
and performs exact equality only. Exactly one matching rule returns `SYMBOLIC_MATCH`; zero returns
`NO_SYMBOLIC_MATCH`; more than one returns `AMBIGUOUS_SYMBOLIC_MATCH`. Both non-singleton cases
return `ABSTAIN` with no service code or rule ID. The rule `order` supplies a canonical inspection
order only and cannot break ambiguity or rank a service/provider.

## Non-goals and acceptance

This is not clinical routing, specialty selection, provider discovery, verified query, ranking, or
P13 activation. Acceptance requires adversarial direct-constructor tests, exact-match and
abstention tests, full backend regression, unchanged schema/dependencies/runtime, and exact-SHA CI.
Every live P13 acceptance criterion remains not verified.
