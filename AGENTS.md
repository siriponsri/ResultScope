# AGENTS.md — ResultScope local development rules

## Goal

Turn the Week 7 FastAPI/Vercel chatbot starter into a credible lab-intelligence product prototype without breaking the simple deployment path.

## Non-negotiables

1. Preserve FastAPI + `api/index.py` + Vercel compatibility.
2. Keep OpenAI-compatible provider portability.
3. Do not expose API keys to the browser or commit `.env`.
4. Unrelated prompts must be rejected before LLM invocation.
5. Do not turn the product into a general medical chatbot.
6. Do not add diagnosis, prescribing, dose changes, or treatment plans.
7. Prefer user-supplied units/reference ranges; do not hard-code universal “normal” ranges as truth.
8. Keep local setup Windows-friendly.
9. Every significant behavior change must include or update a test.
10. Do not add heavy frameworks unless the current HTML/CSS/JS + FastAPI stack cannot meet the requirement.

## Design rules

Use Hallmark when available as an audit/redesign critic.

Avoid:
- gradient-heavy AI aesthetics;
- glass cards;
- decorative blobs/orbs;
- generic 3-column SaaS feature-card grids;
- excessive pills;
- robot/brain/sparkle iconography;
- ChatGPT visual cloning.

Prefer:
- clinical/editorial information design;
- strong typography and hierarchy;
- clear data affordances;
- accessible contrast/focus states;
- responsive behavior;
- calm, precise language;
- visible lab-only product boundary.

## Architecture direction

`scope gate → store → LLM`, not `LLM decides everything`.

For the coursework branch, do not add OCR, RAG, authentication, billing, or full patient profiles unless explicitly requested.

## Before marking work complete

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check.ps1
```

Then manually test:
- desktop;
- narrow mobile viewport;
- one in-scope lab prompt;
- one lab follow-up;
- one out-of-scope prompt;
- new-analysis reset;
- missing API-key error;
- Vercel environment assumptions.
