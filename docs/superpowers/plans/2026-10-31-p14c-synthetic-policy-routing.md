# P14-C Synthetic Policy-Routing Mechanics - Implementation Plan

1. Reconcile the master plan, P14 policy, accepted deterministic-authority ADR, acceptance criteria,
   and P14 readiness STOP rules.
2. Limit implementation to section 2.4's toy symbolic ordering and fail-closed mechanics.
3. Add strict immutable policy/evaluation/decision contracts and a protected-environment-denied pure
   evaluator with exact content and provenance binding.
4. Keep the only executable rule mapping in test support and add direct-constructor, mutation,
   conflict, lifecycle, protected-environment, and forbidden-authority tests.
5. Run full backend/frontend, migration, Docker/PostgreSQL, browser, and security verification.
6. Merge only after exact-SHA six-job CI and repeat all six gates on the resulting main SHA.
