"""
FastAPI application that mounts the Weather MCP server.

Run with:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
How auth works
--------------
1. Register a GitHub OAuth App at https://github.com/settings/developers
2. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in your .env
3. Your MCP client (or test script) completes the GitHub OAuth flow and
   receives an access_token.
4. Include the token in every MCP request:
       Authorization: Bearer <github_access_token>
5. GitHubAuthMiddleware validates the token by calling api.github.com/user.
   Valid tokens pass through; invalid ones get a 401 JSON response.

Skip auth for local testing
----------------------------
Set  GITHUB_AUTH_REQUIRED=false  in .env (default is true).
"""
from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from app.remote_main import mcp  # noqa: E402

logger = logging.getLogger("mcp.auth")

# ---------------------------------------------------------------------------
# GitHub token validator with a short in-memory cache (avoid spamming GH API)
# ---------------------------------------------------------------------------

_TOKEN_CACHE: dict[str, tuple[dict[str, Any], float]] = {}
_CACHE_TTL = 60  # seconds


async def _validate_github_token(token: str) -> dict[str, Any] | None:
    """
    Call GitHub's /user endpoint to validate an OAuth access token.
    Returns the parsed user object on success, or None on failure.
    Results are cached for _CACHE_TTL seconds to reduce API calls.
    """
    now = time.monotonic()
    cached = _TOKEN_CACHE.get(token)
    if cached:
        user, expires_at = cached
        if now < expires_at:
            return user

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
        if resp.status_code == 200:
            user = resp.json()
            _TOKEN_CACHE[token] = (user, now + _CACHE_TTL)
            logger.info("GitHub token validated for user: %s", user.get("login"))
            return user
        else:
            logger.warning(
                "GitHub token validation failed: HTTP %d", resp.status_code
            )
            return None
    except httpx.RequestError as exc:
        logger.error("GitHub API request error: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

# Paths that don't require authentication
_PUBLIC_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc"}


class GitHubAuthMiddleware(BaseHTTPMiddleware):
    """
    Validates GitHub OAuth bearer tokens on all /mcp/* requests.
    Requests to public paths (/, /health, /docs …) are always allowed.
    Auth can be disabled entirely by setting GITHUB_AUTH_REQUIRED=false.
    """

    def __init__(self, app, auth_required: bool = True) -> None:
        super().__init__(app)
        self.auth_required = auth_required
        if not auth_required:
            logger.warning(
                "⚠️  GitHub auth is DISABLED (GITHUB_AUTH_REQUIRED=false). "
                "Do NOT use this setting in production."
            )

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip auth for public paths and non-MCP routes
        path = request.url.path
        if (
            not self.auth_required
            or path in _PUBLIC_PATHS
            or not path.startswith("/mcp")
            or request.method == "OPTIONS"
        ):
            return await call_next(request)

        # Extract bearer token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.lower().startswith("bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "error": "missing_token",
                    "error_description": (
                        "Authorization header with Bearer token is required. "
                        "Obtain a GitHub OAuth token and pass it as: "
                        "Authorization: Bearer <token>"
                    ),
                },
            )

        token = auth_header[7:].strip()
        user = await _validate_github_token(token)
        if user is None:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "invalid_token",
                    "error_description": (
                        "GitHub token validation failed. "
                        "The token may be expired, revoked, or invalid."
                    ),
                },
            )

        # Attach GitHub user info to request state for downstream use
        request.state.github_user = user
        return await call_next(request)

mcp_app = mcp.http_app(path="/")
_auth_required = os.getenv("GITHUB_AUTH_REQUIRED", "true").strip().lower() not in (
    "false", "0", "no", "off"
)

app = FastAPI(
    title="Weather MCP Server",
    description=(
        "A FastAPI application that exposes a Model Context Protocol (MCP) "
        "weather server backed by the Open-Meteo API."
    ),
    version="1.0.0",
    lifespan=mcp_app.lifespan,
)
# Register GitHub auth middleware BEFORE mounting the MCP sub-app
app.add_middleware(GitHubAuthMiddleware, auth_required=_auth_required)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:6274",
        "http://127.0.0.1:6274",
    ],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root() -> JSONResponse:
    return JSONResponse(
        {
            "service": "Weather MCP Server",
            "status": "ok",
            "mcp_endpoint": "/mcp",
            "docs": "/docs",
        }
    )


@app.get("/health", tags=["meta"])
async def health() -> JSONResponse:
    """Liveness probe."""
    return JSONResponse({"status": "ok"})

app.mount("/mcp", mcp_app)
