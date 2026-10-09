# R3 Repository Verification

**Status:** READY FOR CODEX FOUNDATION IMPLEMENTATION

Verified against the R3 repository package.

## Verified

- Canonical R3 architecture is present at `docs/02_SYSTEM_ARCHITECTURE.md`.
- Canonical R3 engineering standards are present at `docs/29_ENGINEERING_STANDARDS.md`.
- Final dependency map is present at `docs/implementation/36_DEPENDENCY_MAP.md`.
- R3 decisions are recorded in `docs/implementation/37_DECISION_LOG.md`.
- R3 progress status is recorded in `docs/implementation/38_PROGRESS_TRACKER.md`.
- R3 Codex policy is present under `docs/research/r3/`.
- Original SIH and MannSetu source documents are present under `docs/source_material/`.
- Source material has a manifest and is marked immutable.
- No third-party GitHub repositories are vendored into the SwasthyaSetu repository.
- Temporary upstream clone directories are ignored by Git.
- `REPOSITORY_TREE.txt` was regenerated from the actual repository contents.

## Upstream repository rule

Do not permanently clone upstream projects into this repository.

If source inspection is needed during a technical spike, clone an exact tag/commit temporarily into one of:

```text
.external/
upstream/
.tmp/upstream/
```

Retain only the resulting adapter, tests, benchmark results, version/commit, license record, and decision.
