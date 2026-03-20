from __future__ import annotations

import contextlib
import logging
import os
import uuid
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from week3.server.core import (
    GitHubOAuthConfig,
    HttpAuthConfig,
    OpenMeteoClient,
    WeatherService,
    WeatherSettings,
)
from week3.server.mcp import create_weather_mcp_server
from week3.server.transports.auth import (
    AuthError,
    BearerAuthMiddleware,
    BearerTokenValidator,
    build_protected_resource_metadata,
)
from week3.server.transports.github_oauth import GitHubOAuthClient


def configure_logging() -> None:
    level = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, force=True)


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class NormalizeMcpPathMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        if request.scope["path"] == "/mcp":
            request.scope["path"] = "/mcp/"
            request.scope["raw_path"] = b"/mcp/"
        return await call_next(request)


def create_http_app(
    weather_settings: WeatherSettings | None = None,
    auth_config: HttpAuthConfig | None = None,
    github_config: GitHubOAuthConfig | None = None,
    github_client: GitHubOAuthClient | None = None,
) -> FastAPI:
    configure_logging()
    logger = logging.getLogger(__name__)
    weather_settings = weather_settings or WeatherSettings.from_env()
    auth_config = auth_config or HttpAuthConfig.from_env()
    github_config = github_config or GitHubOAuthConfig.from_env()

    weather_client = OpenMeteoClient(weather_settings)
    weather_service = WeatherService(weather_client)
    github_oauth_client = github_client or (
        GitHubOAuthClient(github_config) if github_config.enabled else None
    )
    bundle = create_weather_mcp_server(
        weather_service,
        name="Week3WeatherHTTP",
        streamable_http_path="/",
    )

    @contextlib.asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        async with contextlib.AsyncExitStack() as stack:
            await stack.enter_async_context(bundle.server.session_manager.run())
            try:
                yield
            finally:
                await weather_client.aclose()
                if github_client is None and github_oauth_client is not None:
                    await github_oauth_client.aclose()

    app = FastAPI(title="Week 3 MCP Weather HTTP Server", lifespan=lifespan)
    app.add_middleware(NormalizeMcpPathMiddleware)
    app.add_middleware(RequestIdMiddleware)
    if auth_config.required:
        app.add_middleware(
            BearerAuthMiddleware,
            config=auth_config,
            validator=BearerTokenValidator(auth_config, github_oauth_client),
        )
    app.mount("/mcp", bundle.server.streamable_http_app())

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/auth/github/login")
    async def github_login() -> RedirectResponse | JSONResponse:
        if github_oauth_client is None:
            return JSONResponse({"error": "GitHub OAuth is not configured"}, status_code=503)
        missing_settings = [
            name
            for name, value in (
                ("GITHUB_CLIENT_ID", github_config.client_id),
                ("GITHUB_REDIRECT_URI", github_config.redirect_uri),
            )
            if not value
        ]
        if missing_settings:
            return JSONResponse(
                {
                    "error": "GitHub OAuth is missing required settings",
                    "missing": missing_settings,
                },
                status_code=503,
            )
        state = github_oauth_client.create_state()
        try:
            authorize_url = github_oauth_client.build_authorize_url(state)
        except AuthError as exc:
            return JSONResponse({"error": str(exc)}, status_code=503)
        response = RedirectResponse(url=authorize_url, status_code=307)
        response.set_cookie(
            "oauth_state",
            state,
            httponly=True,
            secure=auth_config.resource_server_url.startswith("https://"),
            samesite="lax",
        )
        return response

    @app.get("/auth/github/callback")
    async def github_callback(code: str, state: str, request: Request) -> JSONResponse:
        if github_oauth_client is None:
            return JSONResponse({"error": "GitHub OAuth is not configured"}, status_code=404)
        cookie_state = request.cookies.get("oauth_state")
        if not cookie_state or cookie_state != state:
            return JSONResponse({"error": "invalid oauth state"}, status_code=400)

        try:
            token = await github_oauth_client.exchange_code(code)
            auth_context = await github_oauth_client.verify_access_token(
                token.access_token,
                required_scopes=auth_config.required_scopes,
            )
        except AuthError as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)

        response = JSONResponse(
            {
                "access_token": token.access_token,
                "token_type": token.token_type,
                "scope": token.scope,
                "subject": auth_context.subject,
                "instructions": "Use this bearer token in Authorization headers for the /mcp endpoint.",
            }
        )
        response.delete_cookie("oauth_state")
        return response

    @app.get("/auth/github/me")
    async def github_me(request: Request) -> JSONResponse:
        if github_oauth_client is None:
            return JSONResponse({"error": "GitHub OAuth is not configured"}, status_code=404)
        try:
            from week3.server.transports.auth import extract_bearer_token

            token = extract_bearer_token(request.headers.get("Authorization"))
            auth_context = await github_oauth_client.verify_access_token(
                token,
                required_scopes=auth_config.required_scopes,
            )
        except AuthError as exc:
            return JSONResponse({"error": str(exc)}, status_code=401)
        return JSONResponse(
            {
                "subject": auth_context.subject,
                "client_id": auth_context.client_id,
                "scopes": auth_context.scopes,
            }
        )

    @app.get("/.well-known/oauth-protected-resource")
    @app.get("/.well-known/oauth-protected-resource/mcp")
    async def protected_resource_metadata(request: Request) -> JSONResponse:
        logger.info(
            "served protected resource metadata",
            extra={"request_id": getattr(request.state, "request_id", None)},
        )
        return JSONResponse(build_protected_resource_metadata(auth_config))

    return app


app = create_http_app()
