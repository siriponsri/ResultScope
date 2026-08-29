$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    py -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m compileall -q .
python -m pytest -q
Write-Host "Checks passed." -ForegroundColor Green
