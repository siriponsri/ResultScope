from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import threading
import time
from dataclasses import dataclass

from fastapi import Request, Response

from config import settings


ADMIN_SESSION_COOKIE = "resultscope_admin_session"
ADMIN_CSRF_COOKIE = "resultscope_admin_csrf"
DEFAULT_ADMIN_USERNAME = "admin"
# PBKDF2 hash for the local-demo default only; production refuses the fallback.
DEFAULT_LOCAL_DEMO_PASSWORD_HASH = "pbkdf2_sha256$240000$ABEiM0RVZneImaq7zN3u_w$bFvlA8WxLQnsXYytWQ-ttF16gNMdmzbvaOHnUsSBLug"
_HASH_ITERATIONS = 240_000


@dataclass
class AdminSession:
    username: str
    csrf_token: str
    expires_at: float


_sessions: dict[str, AdminSession] = {}
_sessions_lock = threading.RLock()
_login_windows: dict[str, tuple[float, int]] = {}
_login_lock = threading.Lock()


def local_demo_enabled() -> bool:
    environment = settings.APP_ENV.lower().strip()
    return bool(
        settings.LOCAL_DEMO_MODE
        and environment in {"local", "development", "test"}
        and not os.getenv("VERCEL")
    )


def secure_cookie(request: Request | None = None) -> bool:
    if settings.APP_ENV.lower().strip() in {"production", "staging"}:
        return True
    return bool(request and request.url.scheme == "https")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _HASH_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        _HASH_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii").rstrip("="),
        base64.urlsafe_b64encode(digest).decode("ascii").rstrip("="),
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_text, digest_text = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_text + "=" * (-len(salt_text) % 4))
        expected = base64.urlsafe_b64decode(digest_text + "=" * (-len(digest_text) % 4))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except (TypeError, ValueError, UnicodeError):
        return False


def configured_admin_hash() -> str:
    if settings.ADMIN_PASSWORD_HASH.strip():
        return settings.ADMIN_PASSWORD_HASH.strip()
    # The known password is reachable only behind the explicit local-demo guard.
    return DEFAULT_LOCAL_DEMO_PASSWORD_HASH


def login_allowed(client_key: str) -> bool:
    now = time.monotonic()
    limit = max(1, settings.ADMIN_LOGIN_RATE_LIMIT_REQUESTS)
    window = max(1, settings.ADMIN_LOGIN_RATE_LIMIT_WINDOW_SECONDS)
    with _login_lock:
        started, count = _login_windows.get(client_key, (now, 0))
        if now - started >= window:
            _login_windows[client_key] = (now, 1)
            return True
        if count >= limit:
            return False
        _login_windows[client_key] = (started, count + 1)
        return True


def clear_rate_limits() -> None:
    with _login_lock:
        _login_windows.clear()


def create_session(username: str) -> tuple[str, AdminSession]:
    token = secrets.token_urlsafe(32)
    session = AdminSession(
        username=username,
        csrf_token=secrets.token_urlsafe(24),
        expires_at=time.time() + max(60, settings.ADMIN_SESSION_TTL_SECONDS),
    )
    with _sessions_lock:
        _sessions[token] = session
    return token, session


def get_session(request: Request) -> tuple[str, AdminSession] | None:
    token = request.cookies.get(ADMIN_SESSION_COOKIE)
    if not token:
        return None
    with _sessions_lock:
        session = _sessions.get(token)
        if session is None:
            return None
        if session.expires_at <= time.time():
            _sessions.pop(token, None)
            return None
        return token, session


def require_csrf(request: Request, session: AdminSession) -> bool:
    supplied = request.headers.get("x-csrf-token", "")
    cookie = request.cookies.get(ADMIN_CSRF_COOKIE, "")
    return bool(supplied and cookie and hmac.compare_digest(supplied, session.csrf_token) and hmac.compare_digest(cookie, session.csrf_token))


def set_session_cookies(response: Response, request: Request, token: str, session: AdminSession) -> None:
    secure = secure_cookie(request)
    response.set_cookie(
        ADMIN_SESSION_COOKIE,
        token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=max(60, settings.ADMIN_SESSION_TTL_SECONDS),
        path="/",
    )
    response.set_cookie(
        ADMIN_CSRF_COOKIE,
        session.csrf_token,
        httponly=False,
        secure=secure,
        samesite="lax",
        max_age=max(60, settings.ADMIN_SESSION_TTL_SECONDS),
        path="/",
    )


def clear_session(response: Response, request: Request) -> None:
    with _sessions_lock:
        token = request.cookies.get(ADMIN_SESSION_COOKIE)
        if token:
            _sessions.pop(token, None)
    response.delete_cookie(ADMIN_SESSION_COOKIE, path="/")
    response.delete_cookie(ADMIN_CSRF_COOKIE, path="/")
