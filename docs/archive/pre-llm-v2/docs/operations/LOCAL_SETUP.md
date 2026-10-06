# Local setup

Use this procedure to inspect **ResultScope Laboratory Assistant** on one machine. It preserves existing configuration and keeps LLM, OCR, and SystemOne transport disabled. Use synthetic or de-identified inputs.

## Before starting

Open a terminal in the repository root. Keep an existing `.env`, Windows `.venv`, local settings file, and provider ledger intact. Do not replace a Windows virtual environment with a Linux environment. Provider credentials are not required to view the workspace or run mocked tests.

Installing dependencies may require package-network access. The provider guard controls application provider requests; it does not control dependency downloads or separately configured storage services. The commands below select local SQLite explicitly so an existing Upstash configuration is not used for this review.

## Windows / PowerShell

```powershell
if (!(Test-Path .venv)) { py -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
$env:APP_ENV = "development"
$env:PROVIDER_NETWORK_ENABLED = "false"
$env:STORAGE_BACKEND = "sqlite"
python -m uvicorn main:app --host 127.0.0.1 --port 8765
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765). Stop with `Ctrl+C`. The environment assignments apply to this PowerShell process and do not rewrite `.env`. If the existing environment cannot activate, inspect its interpreter and dependencies before recreating anything.

## macOS / Linux

Use an environment outside the checkout so a shipped Windows `.venv` remains untouched:

```bash
if [ ! -d ../resultscope-local-venv ]; then
  python3 -m venv ../resultscope-local-venv
fi
. ../resultscope-local-venv/bin/activate
python -m pip install -r requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
fi
APP_ENV=development PROVIDER_NETWORK_ENABLED=false STORAGE_BACKEND=sqlite \
  python -m uvicorn main:app --host 127.0.0.1 --port 8765
```

Use a different unused environment location if the suggested directory belongs to another project. Do not overwrite it.

## What an offline run can show

| Action | Expected boundary |
|---|---|
| Open the workspace and guide | Real HTML, CSS, fonts, and JavaScript are served locally |
| Check `/health` | Confirms the app process responds; it does not validate providers or readiness |
| Enter an unrelated question | Scope refusal can be handled locally |
| Enter laboratory values | Deterministic analysis is local; an explanation may abstain or report unavailable evidence/provider |
| Upload a JPEG/PNG | Input validation is local; actual OCR cannot complete with transport disabled |
| Test a provider with a mock | Exercises the adapter test path without a live request |

Offline mode is not an automatic successful-answer simulator. Screenshots that demonstrate a successful mocked explanation or extraction must say so.

The default `KNOWLEDGE_MODE` is `release`; absent approved content it fails closed. Optional `PUBLIC_REFERENCE_ENABLED=true` allows local public-source lookup, but generated explanations still require authorized provider transport. `KNOWLEDGE_MODE=synthetic` is for local development/test fixtures only and displays a synthetic-data notice. Neither mode approves sources for release.

## Optional local administration

To enable the local settings UI, stop the server, set `LOCAL_DEMO_MODE=true` in the same process, and start again with the same network guard. Keep `APP_ENV=development` and bind to `127.0.0.1`.

```powershell
$env:LOCAL_DEMO_MODE = "true"
$env:PROVIDER_NETWORK_ENABLED = "false"
python -m uvicorn main:app --host 127.0.0.1 --port 8765
```

Open `/admin/login`. The fallback credentials are `admin` / `1234` only for this explicitly enabled local demonstration, when no custom administrator password hash is configured. A configured hash changes the accepted password. Never expose this mode or these fallback credentials online. Read the [administrator guide](ADMIN_GUIDE.md) before changing settings.

## Checks

The repository's required Windows check installs development dependencies, compiles Python, and runs pytest:

```powershell
$env:PROVIDER_NETWORK_ENABLED = "false"
$env:STORAGE_BACKEND = "sqlite"
powershell -ExecutionPolicy Bypass -File .\scripts\check.ps1
```

The platform-independent components can be run from an appropriate activated environment:

```bash
python -m pip install -r requirements-dev.txt
python -m compileall -q main.py config.py routers services tests
PROVIDER_NETWORK_ENABLED=false STORAGE_BACKEND=sqlite python -m pytest -q
PROVIDER_NETWORK_ENABLED=false STORAGE_BACKEND=sqlite python scripts/provider_verification_runner.py
```

Do not add `--live` to the runner for an offline review. Report actual results with the candidate identifier; do not copy a historical pass count.

## Troubleshooting

| Symptom | Action |
|---|---|
| Port 8765 is occupied | Stop the known local process or choose another loopback port; do not terminate unrelated processes |
| Admin returns 404 | Confirm explicit local-demo mode, development/test/local environment, and absence of the Vercel runtime flag |
| No explanation appears | Read the visible source/provider message; offline or release-corpus blocking may be expected |
| Image extraction is unavailable | Check the documented OCR dependency; use text entry for an offline inspection |
| Session changes after restart | Without a configured session-signing key, the process generates a temporary signing key |
| Corpus integrity fails | Inspect the manifest and source bytes; do not disable validation or silently promote source eligibility |
| An earlier instruction recreates `.venv` or copies `.env` unconditionally | Use this preservation procedure instead |

No deployment, provider-budget creation, key change, or live validation is part of this startup procedure.
