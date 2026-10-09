# Contributing to SwasthyaSetu AI

All implementation must follow the project Master Spec, System Architecture, Engineering Standards, and Master Implementation Plan.

Core rules:

- Respect bounded module ownership.
- Do not directly mutate another module's tables.
- Put external providers behind adapters.
- Do not invent clinical policy, remedies, thresholds, or provider information.
- Keep generative AI outside the final safety-decision boundary.
- Add tests with implementation.
- Add Alembic migrations for persistent schema changes.
- Do not commit secrets or real patient data.
- Report incomplete work as PARTIAL/BLOCKED rather than claiming completion.
