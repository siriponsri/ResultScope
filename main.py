from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import settings
from routers.chat import router as chat_router
from routers.images import router as images_router
from routers.admin import router as admin_router
from routers.conversation import router as conversation_router
from routers.business import router as business_router
from routers.business_ops import router as business_ops_router
from routers.site import router as site_router
from services.conversation_transport import ConversationError
from fastapi.responses import JSONResponse

BASE_DIR = Path(__file__).resolve().parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(
    title=settings.APP_NAME,
    description="Multilingual, LLM-led laboratory conversations grounded in traceable references.",
    version="3.0.0",
)

cors_origins = [
    origin.strip()
    for origin in settings.CORS_ALLOWED_ORIGINS.split(",")
    if origin.strip()
]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
    )

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.include_router(chat_router)
app.include_router(images_router)
app.include_router(admin_router)
app.include_router(conversation_router)
app.include_router(business_router)
app.include_router(business_ops_router)
app.include_router(site_router)

@app.exception_handler(ConversationError)
async def business_error(request: Request, exc: ConversationError):
    return JSONResponse({"code": exc.code, "message": str(exc)}, status_code=exc.status, headers={"Cache-Control": "no-store"})


@app.middleware("http")
async def request_boundary(request: Request, call_next):
    # v1 remains a local migration surface, never a cloud safety bypass.
    if os.getenv("VERCEL") and request.url.path.startswith("/api/v1"):
        return JSONResponse({"code": "legacy_disabled", "message": "Use the current conversation API."}, status_code=410)
    if request.url.path.startswith(("/api/v2", "/api/business")) and request.method in {"POST", "PUT", "PATCH"}:
        limit = 4 * 1024 * 1024
        try:
            if int(request.headers.get("content-length", "0")) > limit:
                return JSONResponse({"message": "The request exceeds the 4 MB limit."}, status_code=413)
        except ValueError:
            return JSONResponse({"message": "Invalid request size."}, status_code=400)
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > limit:
                return JSONResponse({"message": "The request exceeds the 4 MB limit."}, status_code=413)
        request._body = bytes(body)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith(("/api/v2", "/api/business")):
        response.headers["Cache-Control"] = "no-store"
    # Coursework simulation: never ask search engines to index simulated clinics or prices.
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    html_page = not request.url.path.startswith(("/static", "/api", "/lab", "/admin", "/settings", "/docs", "/redoc", "/openapi.json"))
    if html_page or request.url.path.startswith("/api/business"):
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; connect-src 'self'; frame-src 'self' https://www.google.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
    return response


@app.get("/settings")
async def connection_settings(request: Request):
    return templates.TemplateResponse(request, "settings.html", {"app_name": settings.APP_NAME})


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }


@app.get("/app")
async def business_app(request: Request):
    return templates.TemplateResponse(request, "workspace.html", {"staff_mode": False, "title": "Your workspace — ResultScope"})

@app.get("/staff")
async def business_staff(request: Request):
    return templates.TemplateResponse(request, "workspace.html", {"staff_mode": True, "title": "Service desk — ResultScope"})

@app.get("/lab")
async def lab_workspace(request: Request):
    return templates.TemplateResponse(request, "conversation.html", {"app_name": settings.APP_NAME, "tagline": settings.APP_TAGLINE})
