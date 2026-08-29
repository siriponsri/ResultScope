$ErrorActionPreference = "Stop"

if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    throw "npx not found. Install Node.js first, then run this script again."
}

Write-Host "Installing/updating Hallmark design skill..." -ForegroundColor Cyan
npx skills add nutlope/hallmark
Write-Host "Hallmark installed. For project-scoped Codex usage, verify it is available under .codex/skills/hallmark or your Codex skills directory." -ForegroundColor Green
