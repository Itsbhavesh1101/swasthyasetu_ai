# SwasthyaSetu patient health hub demo

This is the working college-project demonstration. It is designed for synthetic or demonstration
data on one local computer. It is not a hospital system, medical device, diagnostic service, or a
replacement for a qualified professional or emergency service.

## What works

- Patient registration with name, email, and password, followed by sign-in and sign-out.
- A private patient profile and six structured medical-history categories.
- Corrections that preserve the earlier record instead of silently overwriting it.
- A longitudinal timeline of encounters and medical facts.
- A private PDF/JPEG/PNG document vault with validation, download, and removal.
- A consented structured health-intake journey saved against the authenticated patient.
- Optional source-backed home-care and general-wellness guidance through Gemini and Google Search
  grounding. The integration is off by default and is deliberately not a diagnosis or prescription.

MannSetu mental-health diagnosis is not activated. Historical synthetic preview routes remain in the
repository for engineering tests, but they are not shown in the primary patient navigation.

## Prerequisites

- Windows 10/11 with PowerShell.
- Docker Desktop running with Linux containers.
- Python available through `py`.
- Node.js 24 with Corepack enabled.
- Loopback ports `5432`, `8000`, and `3100` available.

The launcher supplies PostgreSQL automatically. You do not need to install or manually connect a
database. Data is kept in the Docker volume `swasthyasetu-local-postgres-data`; uploaded document
bytes are kept separately in `swasthyasetu-local-patient-documents`.

## Optional Gemini configuration

Copy the local environment template before starting if you want live grounded guidance:

```powershell
Copy-Item deployments/local/.env.example deployments/local/.env
```

Edit the ignored `deployments/local/.env` file and set:

```text
GEMINI_ENABLED=true
GEMINI_API_KEY=your-key-kept-only-on-this-computer
GEMINI_MODEL=your-supported-gemini-model-id
```

Never commit the key. The browser never receives it. Without these values the rest of the patient
product works normally and the guidance page reports that its provider is unavailable. Guidance
requires explicit external-processing consent and accepts only citations from the configured
official-source allowlist.

## Start the product

From the repository root:

```powershell
py scripts/demo.py plan
py scripts/demo.py start
```

The launcher installs the locked frontend workspace, creates the ignored local configuration only
when it is absent, starts PostgreSQL, builds the backend, applies migrations explicitly, waits for
database-aware backend readiness, and starts the patient application in a hidden background process.
Logs are written under the ignored `.demo/logs` directory.

Open <http://127.0.0.1:3100>.

Check the product without changing it:

```powershell
py scripts/demo.py status
```

Both `backend` and `patient` should be `true`. Backend status probes `/health/ready`, so `true` also
confirms that PostgreSQL is reachable.

## Demonstration walkthrough

1. Select **Create account** and register with a demonstration name, email, and a password of at
   least 12 characters.
2. Open **Profile**, enter optional demographic details, and save.
3. Open **History**. Add demonstration entries across problems, medications, allergies, procedures,
   observations, and investigations. Correct one entry and confirm that the earlier version remains
   in the record as superseded.
4. Open **Timeline** and confirm the patient-owned encounter and history entries appear in
   deterministic newest-first order.
5. Open **Documents**. Upload a small synthetic PDF, JPEG, or PNG; download it; then remove it. Files
   over 10 MiB or with mismatched content are rejected.
6. Open **Health journey**, explicitly allow structured intake, answer the neutral questions, review
   the draft, and complete it. Completion records a patient-provided draft, not a diagnosis.
7. Open **Home guidance**. If Gemini is configured, read the notice, grant the exact external-AI
   consent, and ask a low-risk general-wellness question. Confirm that the result has official-source
   citations. High-risk, diagnostic, treatment, dosage, or emergency requests fail closed.
8. Sign out and sign back in. Confirm that the profile, history, timeline, and document metadata are
   still associated only with the same account.

Use only synthetic demonstration content. Do not upload real medical documents or enter real health
information in this local college setup.

## Privacy and safety boundaries

- Opaque credentials are held in transient `HttpOnly`, `SameSite=Strict` cookies and forwarded to
  FastAPI only by same-origin server handlers.
- The service worker caches only the public offline shell, manifest, and project-owned icons. It does
  not cache account, API, profile, history, timeline, document, intake, guidance, consent, or bearer
  data.
- Every private backend operation derives the patient from the authenticated session; browser-sent
  patient identifiers cannot substitute another patient.
- Gemini guidance is bounded general information with source validation. It cannot diagnose,
  prescribe, recommend dosage, promise a cure, or replace urgent or professional care.
- Local PostgreSQL and document volumes are suitable for this controlled demonstration, not a
  production deployment or shared hospital environment.

## Stop the product

```powershell
py scripts/demo.py stop
```

This stops only the recorded patient process tree and the named `swasthyasetu-local` Compose project.
It preserves the database and document volumes. It never performs broad process discovery, Docker
pruning, or volume deletion.

If startup fails, inspect `.demo/logs`, confirm ports `5432`, `8000`, and `3100` are free, verify
Docker Desktop is running, then run `py scripts/demo.py stop` before retrying.
