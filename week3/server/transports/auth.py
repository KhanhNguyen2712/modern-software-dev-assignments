from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from week3.server.core.config import HttpAuthConfig

if TYPE_CHECKING:
    from week3.server.transports.github_oauth import GitHubOAuthClient


class AuthError(Exception):
    """Raised when an incoming bearer token is missing or invalid."""


@dataclass(frozen=True)
class AuthContext:
    client_id: str
    scopes: list[str]
    subject: str | None = None


def extract_bearer_token(header_value: str | None) -> str:
    if not header_value or not header_value.lower().startswith("bearer "):
        raise AuthError("missing bearer token")
    token = header_value.split(" ", 1)[1].strip()
    if not token:
        raise AuthError("missing bearer token")
    return token


class BearerTokenValidator:
    def __init__(
        self,
        config: HttpAuthConfig,
        github_oauth_client: GitHubOAuthClient | None = None,
    ) -> None:
        self.config = config
        self.github_oauth_client = github_oauth_client
        self._jwk_client = jwt.PyJWKClient(config.jwks_url) if config.jwks_url else None

    async def validate_token(self, token: str) -> AuthContext:
        if self.config.dev_bearer_token and token == self.config.dev_bearer_token:
            return AuthContext(
                client_id=self.config.dev_client_id,
                scopes=self.config.required_scopes,
                subject=self.config.dev_client_id,
            )

        if self.config.provider == "github":
            if self.github_oauth_client is None:
                raise AuthError("GitHub OAuth is not configured")
            return await self.github_oauth_client.verify_access_token(
                token,
                required_scopes=self.config.required_scopes,
            )

        claims = self._decode_jwt(token)
        scopes = self._extract_scopes(claims)
        if self.config.required_scopes and not set(self.config.required_scopes).issubset(scopes):
            raise AuthError("invalid bearer token")
        return AuthContext(
            client_id=str(claims.get("client_id") or claims.get("sub") or "unknown-client"),
            scopes=sorted(scopes),
            subject=str(claims.get("sub")) if claims.get("sub") else None,
        )

    def _decode_jwt(self, token: str) -> dict[str, Any]:
        if not self.config.issuer or not self.config.audience:
            raise AuthError("authentication is enabled but issuer/audience are not configured")
        try:
            if self.config.jwt_secret:
                return jwt.decode(
                    token,
                    self.config.jwt_secret,
                    algorithms=["HS256"],
                    audience=self.config.audience,
                    issuer=self.config.issuer,
                )
            if self._jwk_client is not None:
                signing_key = self._jwk_client.get_signing_key_from_jwt(token)
                return jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256", "ES256"],
                    audience=self.config.audience,
                    issuer=self.config.issuer,
                )
        except jwt.PyJWTError as exc:
            raise AuthError("invalid bearer token") from exc

        raise AuthError("authentication is enabled but no token verifier is configured")

    def _extract_scopes(self, claims: dict[str, Any]) -> set[str]:
        scope_claim = claims.get("scope")
        if isinstance(scope_claim, str):
            return {scope for scope in scope_claim.split() if scope}
        scp_claim = claims.get("scp")
        if isinstance(scp_claim, list):
            return {str(scope) for scope in scp_claim}
        return set()


def build_protected_resource_metadata(config: HttpAuthConfig) -> dict[str, Any]:
    metadata: dict[str, Any] = {"resource": f"{config.resource_server_url}/mcp"}
    if config.provider == "github":
        metadata["authorization_servers"] = ["https://github.com"]
        metadata["bearer_methods_supported"] = ["header"]
    elif config.issuer:
        metadata["authorization_servers"] = [config.issuer]
    if config.jwks_url:
        metadata["jwks_uri"] = config.jwks_url
    return metadata


class BearerAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: Any,
        *,
        config: HttpAuthConfig,
        validator: BearerTokenValidator,
    ) -> None:
        super().__init__(app)
        self.config = config
        self.validator = validator

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        if not self.config.required or not request.url.path.startswith("/mcp"):
            return await call_next(request)

        try:
            token = extract_bearer_token(request.headers.get("Authorization"))
            request.state.auth = await self.validator.validate_token(token)
        except AuthError as exc:
            return JSONResponse(
                {"error": str(exc)},
                status_code=401,
                headers={"WWW-Authenticate": 'Bearer realm="weather-mcp"'},
            )
        return await call_next(request)
