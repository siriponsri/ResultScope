# Phase 3 Baseline Evidence

Date: 2026-10-02
Repository: `C:\Users\User\Desktop\myProject\ResultScope`
Branch: `main`
Base HEAD: `f9d27dd6cea707783262ddb8c237193c90f9bd0b`

## Repository state

- `git status --short --branch`: `main...origin/main [ahead 7]`; no tracked or visible worktree changes before the Phase 3 packet/implementation work. The owner-only `PROMPT.md` remains local and ignored by `.git/info/exclude`.
- `git cat-file -e HEAD:routers/images.py`: FAIL as expected; the path did not exist at the base.
- `git cat-file -e HEAD:services/image_extraction.py`: FAIL as expected; the path did not exist at the base.
- `git cat-file -e HEAD:services/extraction_store.py`: FAIL as expected; the path did not exist at the base.
- `git show HEAD:templates/index.html | rg 'image-input|image-review'`: no matches.
- `git show HEAD:requirements.txt | rg 'Pillow|python-multipart'`: no matches.

## Runtime baseline

- `\.venv\Scripts\python.exe -m pytest -q`: **PASS**, 110 passed, one existing Starlette/httpx deprecation warning.
- `powershell -ExecutionPolicy Bypass -File .\scripts\check.ps1`: **PASS**, compile check and 110 tests.
- `git diff --check`: **PASS**.
- Image upload, extraction, confirmation, and browser review behavior: **NOT_RUN / absent at baseline**.
- Live Vision provider/OCR: **NOT_RUN**. No credential was read, printed, stored, or used.

## Orchestration evidence

The canonical `run-implementation-review.ps1` helper was invoked once with the Phase 3 IMPLEMENT and REVIEW packets. It failed before route dispatch in `dispatch-route.ps1` because the loaded PowerShell/.NET runtime does not provide `System.IO.Path.IsPathFullyQualified`. No IMPLEMENT or REVIEW worker inspected or changed the repository. The launcher was not retried and no global Agent Kit/account setting was changed. Independent review remains **NOT_RUN**.
