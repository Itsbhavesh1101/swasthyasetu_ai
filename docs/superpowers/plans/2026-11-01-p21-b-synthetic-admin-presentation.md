# P21-B Synthetic Admin Presentation Implementation Plan

1. Establish the exact merged `origin/main` baseline in an isolated worktree and run the admin-web
   test baseline.
2. Write failing tests for the closed presentation states, fail-closed environment/state behavior,
   inaccessible authority claims, sensitive-content absence, capability absence, and production
   import isolation.
3. Implement the smallest immutable fixture below the test support boundary and make the focused
   tests pass.
4. Record scope and acceptance truth in implementation documentation and the progress tracker.
5. Run formatting, lint, type checking, unit tests, builds, backend regression, migration, privacy,
   security, and diff checks; review the complete diff.
6. Commit and push the phase branch, open a PR, verify all six CI jobs on the exact SHA, merge only
   after success, and verify all six jobs again on merged `main`.
