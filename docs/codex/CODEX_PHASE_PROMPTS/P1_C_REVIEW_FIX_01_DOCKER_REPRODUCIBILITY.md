# P1-C Review Fix 01 — Restore Docker Build Reproducibility

**Project:** SwasthyaSetu AI
**Review fix ID:** `SSAI-P1C-REVIEW-FIX-01`
**Branch:** `phase/p1-c-docker-ci-foundation`
**Expected starting HEAD:** `77d54c100bd2bbf40b837046c1c8b2ba6f522b2f`

## Context

P1-C implementation and remote CI are otherwise healthy, but review found one material reproducibility issue in:

```text
infra/docker/backend.Dockerfile
```

The Dockerfile pins the Python base image by immutable digest, but then executes:

```dockerfile
apk upgrade --no-cache
```

in both the builder and runtime stages.

That makes the effective operating-system package set depend on the mutable Alpine package repositories at build time. A rebuild from the same Git commit and the same pinned base-image digest may therefore produce different OS packages and different vulnerability results.

This conflicts with the P1-C requirement for a reproducible, pinned backend container baseline.

## Required correction

Work only on the existing P1-C branch.

Do not merge.

Do not start P2.

### 1. Preflight

Run:

```text
git branch --show-current
git status --short
git rev-parse HEAD
git remote -v
```

Expected:

```text
branch: phase/p1-c-docker-ci-foundation
HEAD: 77d54c100bd2bbf40b837046c1c8b2ba6f522b2f
working tree: clean
```

If the branch has legitimately advanced, inspect the commits before continuing.

### 2. Remove mutable package upgrading

Remove the unconditional:

```dockerfile
apk upgrade --no-cache
```

operations from the backend Dockerfile.

Do not replace them with:

```text
apk update
apk upgrade
unversioned apk add of unnecessary packages
curl | sh
```

The image should consume the package state already contained in the selected immutable base-image digest.

The runtime still needs to create the non-root user/group. Use the utilities already present in the base image.

### 3. Validate the current pinned Python image

Rebuild using the existing pinned Python base digest first.

Run the same Trivy HIGH/CRITICAL image gate.

If the current pinned base image passes without `apk upgrade`, retain it.

If the current pinned image has HIGH/CRITICAL OS vulnerabilities after removing `apk upgrade`:

1. select a newer official supported Python 3.12 Alpine image;
2. pin it by immutable digest;
3. verify it is an official Python image;
4. scan the image without mutating/upgrading its OS packages at build time;
5. do not add vulnerability ignores or broad exceptions;
6. update the recorded runtime baseline if the selected tag/digest changes.

Do not switch Python major/minor.

### 4. Preserve existing behavior

The corrected image must still:

```text
install backend dependencies from backend/uv.lock
contain production dependencies only
run as 10001:10001
start app.main:app with Uvicorn
expose port 8000
pass /health/live
pass /health/ready
contain no secrets
```

No backend application behavior should change.

### 5. Re-run Docker verification

Run at least:

```text
docker build using infra/docker/backend.Dockerfile
docker image inspect runtime user
container startup
GET /health/live
GET /health/ready
Trivy HIGH/CRITICAL image scan
docker history --no-trunc inspection for accidental secrets
```

Clean up only resources created for this verification.

Do not prune unrelated Docker resources.

### 6. Re-run regression quality gates

Run:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

If practical also run:

```text
pnpm e2e:test
```

Do not weaken existing gates.

### 7. CI

Commit the correction with a focused message, for example:

```text
fix: make backend Docker build reproducible
```

Push the same feature branch.

Wait for the P1-C GitHub Actions workflow.

All five mandatory jobs must remain green:

```text
Backend quality
Frontend quality
Docker and PostgreSQL
Playwright Chromium
Security scans
```

Do not merge.

### 8. Documentation

If the Python image tag/digest changes, update:

```text
deployments/local/README.md
docs/implementation/38_PROGRESS_TRACKER.md
README.md only if its factual runtime statement changes
```

If the image does not change, add only a concise post-review remediation note to the P1-C completion record in:

```text
docs/implementation/38_PROGRESS_TRACKER.md
```

The note should state that mutable `apk upgrade` steps were removed after review and that the corrected image/CI security gate passed.

Do not rewrite historical commits or pretend the original P1-C implementation already had the correction.

## Scope restrictions

Do not add:

```text
SQLAlchemy
Alembic
PostgreSQL driver
Redis/Valkey
object storage
Keycloak
AI/ML/QML
clinical/business logic
new runtime services
vulnerability ignores
```

Do not change frontend behavior.

Do not alter source material.

## Final report

Return:

### STATUS

`COMPLETE`, `PARTIAL`, `BLOCKED`, or `FAILED`.

### GIT

Report starting SHA, correction commit SHA, remote SHA, clean/dirty state.

### DOCKER REPRODUCIBILITY FIX

State exactly what was changed and why.

### FINAL PYTHON BASE

Report exact tag and digest.

### VERIFICATION

Report results for:

```text
Docker build
runtime user
container startup
health endpoints
Trivy image scan
Docker history review
backend quality gate
frontend quality gate
Playwright if run
```

### CI

Report workflow run ID/URL and all five mandatory job conclusions.

### GOVERNANCE

Explicitly state:

```text
No vulnerability ignore added: YES/NO
No mutable OS package upgrade remains in Dockerfile: YES/NO
No P2 work introduced: YES/NO
No application behavior changed: YES/NO
```

### MERGE

State:

```text
MERGE PERFORMED: NO
```

Stop after this correction.
