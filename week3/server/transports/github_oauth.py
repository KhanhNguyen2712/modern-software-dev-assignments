from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx

from week3.server.core.config import GitHubOAuthConfig
from week3.server.transports.auth import AuthContext, AuthError


@dataclass(frozen=True)
class GitHubTokenExchange:
    access_token: str
    scope: str
    token_type: str


class GitHubOAuthClient:
    def __init__(
        self,
        config: GitHubOAuthConfig,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.config = config
        self._owns_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient(
            headers={
                "Accept": "application/json",
                "User-Agent": "week3-mcp-weather-server/1.0",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http_client.aclose()

    def create_state(self) -> str:
        return secrets.token_urlsafe(24)

    def build_authorize_url(self, state: str) -> str:
        if not self.config.client_id or not self.config.redirect_uri:
            raise AuthError("GitHub OAuth is not configured")
        query = urlencode(
            {
                "client_id": self.config.client_id,
                "redirect_uri": self.config.redirect_uri,
                "scope": " ".join(self.config.scopes),
                "state": state,
            }
        )
        return f"{self.config.authorize_url}?{query}"

    async def exchange_code(self, code: str) -> GitHubTokenExchange:
        if not self.config.client_id or not self.config.client_secret:
            raise AuthError("GitHub OAuth exchange requires client_id and client_secret")

        response = await self._http_client.post(
            self.config.access_token_url,
            data={
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "code": code,
                "redirect_uri": self.config.redirect_uri,
            },
        )
        response.raise_for_status()
        payload = response.json()
        access_token = payload.get("access_token")
        if not access_token:
            raise AuthError("GitHub OAuth token exchange failed")
        return GitHubTokenExchange(
            access_token=access_token,
            scope=payload.get("scope", ""),
            token_type=payload.get("token_type", "bearer"),
        )

    async def verify_access_token(
        self,
        token: str,
        *,
        required_scopes: list[str],
    ) -> AuthContext:
        verification = None
        if self.config.client_id and self.config.client_secret:
            verification = await self._check_token_with_oauth_app(token)

        if verification is None:
            verification = await self._get_authenticated_user(token)

        scopes = verification["scopes"]
        if required_scopes and not set(required_scopes).issubset(set(scopes)):
            raise AuthError("invalid bearer token")
        return AuthContext(
            client_id=verification["client_id"],
            scopes=scopes,
            subject=verification["subject"],
        )

    async def _check_token_with_oauth_app(self, token: str) -> dict[str, Any] | None:
        response = await self._http_client.post(
            f"{self.config.api_base_url}/applications/{self.config.client_id}/token",
            auth=(self.config.client_id, self.config.client_secret or ""),
            json={"access_token": token},
        )
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            raise AuthError("invalid bearer token")
        payload = response.json()
        user = payload.get("user") or {}
        return {
            "client_id": payload.get("app", {}).get("client_id", self.config.client_id),
            "scopes": payload.get("scopes") or [],
            "subject": user.get("login"),
        }

    async def _get_authenticated_user(self, token: str) -> dict[str, Any]:
        response = await self._http_client.get(
            f"{self.config.api_base_url}/user",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code >= 400:
            raise AuthError("invalid bearer token")
        payload = response.json()
        scope_header = response.headers.get("X-OAuth-Scopes", "")
        scopes = [scope.strip() for scope in scope_header.split(",") if scope.strip()]
        return {
            "client_id": "github-oauth",
            "scopes": scopes,
            "subject": payload.get("login"),
        }
