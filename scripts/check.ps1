$ErrorActionPreference = "Stop"

function Invoke-NativeCommand {
    param([scriptblock]$Command)

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Native command failed with exit code $LASTEXITCODE."
    }
}

if (-not (Test-Path ".venv")) {
    Invoke-NativeCommand { py -m venv .venv }
}
& .\.venv\Scripts\Activate.ps1
Invoke-NativeCommand { python -m pip install -r requirements-dev.txt }
Invoke-NativeCommand { python -m compileall -q main.py config.py routers services tests }
Invoke-NativeCommand { python -m pytest -q }
Write-Host "Checks passed." -ForegroundColor Green
