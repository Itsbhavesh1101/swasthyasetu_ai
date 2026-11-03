# SwasthyaSetu AI synthetic project demonstration

This guide runs the complete college-project demonstration on synthetic engineering data. It does
not enable real clinical decisions, production identity, external providers, patient-data exchange,
or a pilot release.

## Prerequisites

- Windows 10/11 with PowerShell.
- Docker Desktop running with Linux containers.
- Python available through `py`.
- `uv` available through `py -m uv` for the optional offline engineering replays.
- Node.js 24 with Corepack enabled.
- Ports `5432`, `8000`, `3100`, `3101`, and `3102` available on loopback.

## Start everything

From the repository root:

```powershell
py scripts/demo.py plan
py scripts/demo.py start
```

The launcher installs the locked frontend workspace, creates the ignored local Compose environment
file when absent, starts PostgreSQL, builds the backend, explicitly applies Alembic migrations,
checks backend readiness, and starts all three web applications in hidden background processes.
Logs are written below the ignored `.demo/logs` directory.

Open:

- Patient application: <http://127.0.0.1:3100>
- Clinician synthetic review: <http://127.0.0.1:3101>
- Administration shell: <http://127.0.0.1:3102>
- Backend readiness: <http://127.0.0.1:8000/health/ready>

Check the current state without changing anything:

```powershell
py scripts/demo.py status
```

## Main patient walkthrough

1. Open the patient application and choose **Get started**.
2. Continue to language selection, choose **English**, and select **Continue to consent**.
3. Read the synthetic privacy notice, select the agreement checkbox, and choose
   **Agree and continue**.
4. Confirm that the encounter page reports the private session and consent as ready.
5. Choose **Start intake**.
6. For “What would you like to share?”, enter exactly `I report synthetic pain`.
7. Choose **Save and continue**, review the draft, then choose **Complete draft**.
8. Choose **Open offline synthetic preview**.
9. Verify that the page clearly labels the output as engineering test data, shows **Synthetic pain**,
   marks extraction as unconfirmed, and requires clinician review. It is not a diagnosis or urgency
   assessment.
10. Use **End private session** when finished.

The patient navigation also exposes isolated synthetic previews for referral discovery, MannSetu,
self-care safety, FHIR mapping, and the ABDM failure boundary. These previews intentionally contain
no real provider contact, treatment guidance, exchange, or external network action.

## Clinician and administrator walkthrough

At the clinician URL, verify that the document receipt is **UNCONFIRMED**, source-backed summary
evidence is stale/not authorized, controls are disabled, and no patient data is displayed.

At the administrator URL, verify that the administration foundation loads. Live administrative
identity, approval, policy mutation, and persistent audit workflows remain intentionally disabled.

## Offline engineering replays

The later research and governance foundations are demonstrated through deterministic local commands:

```powershell
Push-Location backend
py -m uv run python -m app.modules.care_orchestration.demo --environment test
py -m uv run python -m app.modules.admin_governance.demo --environment test
py -m uv run python -m app.validation.demo --environment test
Pop-Location

py -m uv run --project backend python -m ml.research.demo --environment LOCAL
py -m uv run --project backend python -m ml.quantum.demo --environment LOCAL
```

The readiness replay must report `BLOCKED_NOT_RELEASE_ELIGIBLE`, `UNVERIFIED`, `NOT_EXECUTED`,
`NOT_ELIGIBLE`, and `NOT_RECORDED`. These are honest engineering demonstrations, not release proof.

## Stop everything

```powershell
py scripts/demo.py stop
```

The stop command terminates only the three frontend process trees recorded for this exact repository
and brings down the named `swasthyasetu-local` Compose project. The synthetic PostgreSQL volume is
preserved for the next run. The launcher never runs a broad Docker prune or deletes the database
volume.

If startup fails, inspect `.demo/logs`, confirm the required ports are free, verify Docker Desktop is
running, and rerun `py scripts/demo.py stop` before trying again.
