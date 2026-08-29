$ErrorActionPreference = "Stop"

Write-Host "ResultScope local starter" -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    py -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env. Add your LLM_API_KEY before testing AI responses." -ForegroundColor Yellow
}

Write-Host "Opening http://127.0.0.1:8000" -ForegroundColor Green
Start-Process "http://127.0.0.1:8000"
uvicorn main:app --reload --host 127.0.0.1 --port 8000
