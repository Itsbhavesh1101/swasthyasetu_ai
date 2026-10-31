# P14-F - Synthetic Adversarial Harness

**Status:** complete bounded offline engineering subset; live P14 and P14-E remain blocked.

The pytest-only harness composes existing P14-A/B/C strict contracts, the deterministic test-only
backstop, and the test-only toy policy fixture. Its fixed nonmedical cases exercise deterministic
standard and override behavior, clarification, no-match, missing-policy, conflicting sources,
untrusted extra fields, and protected-environment denial. Stable machine states and content-free
errors are the only outputs.

No production module imports the harness. It adds no patient or clinical text, language processing,
score, threshold, resource, recipient, referral, consent, API, persistence, dependency, UI, network,
or runtime activation. It is not a clinical corpus or release evidence, and every live P14
acceptance criterion remains unverified.
