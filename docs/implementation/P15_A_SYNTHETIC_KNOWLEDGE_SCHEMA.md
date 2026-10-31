# P15-A - Synthetic Knowledge Schema and Pack Loader

**Status:** complete bounded engineering subset; live P15 remains blocked and unapproved.

The detached `self_care` module defines immutable engineering-only pack and item contracts. Closed
nonmedical tokens replace content, sources, and tags, and the only lifecycle value is
`TEST_ONLY_UNAPPROVED`. A SHA-256 digest binds the exact pack/schema versions, UTC creation time,
authority labels, ordered items, sources, placeholders, and tags. Direct validation reconstructs all
nested values so forced mutation fails closed.

The in-memory parser accepts exact mappings only and rejects unknown or missing fields, arbitrary
text, forged approval/state/hash, invalid identifiers, duplicate or unordered values, noncanonical
or future timestamps, hostile mappings, and exceeded bounds using stable content-free errors.

There is no readable guidance, remedy, advice, real source, approval, eligibility, patient context,
retrieval, model, vector index, persistence, API, admin workflow, UI, dependency, or runtime import.
Every live P15 acceptance criterion remains unverified.
