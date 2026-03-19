from __future__ import annotations

import asyncio

import httpx
from fastapi.testclient import TestClient

from week3.server.core.config import GitHubOAuthConfig, HttpAuthConfig, WeatherSettings
from week3.server.transports.github_oauth import GitHubOAuthClient
from week3.server.transports.http_app import create_http_app


def test_github_authorize_url_contains_expected_parameters() -> None:
    client = GitHubOAuthClient(
        GitHubOAuthConfig(
            enabled=True,
            client_id="github-client-id",
            client_secret="github-client-secret",
            redirect_uri="https://weather.example.com/auth/github/callback",
            scopes=["read:user", "user:email"],
        )
    )

    url = client.build_authorize_url("signed-state")

    assert "client_id=github-client-id" in url
    assert "redirect_uri=https%3A%2F%2Fweather.example.com%2Fauth%2Fgithub%2Fcallback" in url
    assert "scope=read%3Auser+user%3Aemail" in url
    assert "state=signed-state" in url


def test_verify_token_uses_oauth_application_check_endpoint() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path.endswith("/applications/github-client-id/token")
        return httpx.Response(
            200,
            json={
                "token": "gho_valid",
                "scopes": ["read:user"],
                "user": {"login": "octocat", "id": 1},
                "app": {"client_id": "github-client-id"},
            },
        )

    client = GitHubOAuthClient(
        GitHubOAuthConfig(
            enabled=True,
            client_id="github-client-id",
            client_secret="github-client-secret",
            redirect_uri="https://weather.example.com/auth/github/callback",
        ),
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    context = asyncio.run(client.verify_access_token("gho_valid", required_scopes=[]))

    assert context.client_id == "github-client-id"
    assert context.subject == "octocat"


def test_verify_token_falls_back_to_user_endpoint_when_app_check_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path.endswith("/user")
        return httpx.Response(
            200,
            json={"login": "octocat", "id": 1, "html_url": "https://github.com/octocat"},
            headers={"X-OAuth-Scopes": "read:user,user:email"},
        )

    client = GitHubOAuthClient(
        GitHubOAuthConfig(
            enabled=True,
            client_id="github-client-id",
            client_secret=None,
            redirect_uri="https://weather.example.com/auth/github/callback",
        ),
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    context = asyncio.run(client.verify_access_token("gho_valid", required_scopes=["read:user"]))

    assert context.client_id == "github-oauth"
    assert context.subject == "octocat"
    assert "read:user" in context.scopes


def test_exchange_code_returns_access_token_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url == httpx.URL("https://github.com/login/oauth/access_token")
        return httpx.Response(
            200,
            json={
                "access_token": "gho_valid",
                "scope": "read:user,user:email",
                "token_type": "bearer",
            },
        )

    client = GitHubOAuthClient(
        GitHubOAuthConfig(
            enabled=True,
            client_id="github-client-id",
            client_secret="github-client-secret",
            redirect_uri="https://weather.example.com/auth/github/callback",
        ),
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    payload = asyncio.run(client.exchange_code("temporary-code"))

    assert payload.access_token == "gho_valid"
    assert payload.scope == "read:user,user:email"


def test_github_login_route_redirects_to_provider() -> None:
    app = create_http_app(
        weather_settings=WeatherSettings(),
        auth_config=HttpAuthConfig(required=True, provider="github"),
        github_config=GitHubOAuthConfig(
            enabled=True,
            client_id="github-client-id",
            client_secret="github-client-secret",
            redirect_uri="https://weather.example.com/auth/github/callback",
        ),
    )

    with TestClient(app) as client:
        response = client.get("/auth/github/login", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"].startswith("https://github.com/login/oauth/authorize?")
    assert "oauth_state=" in response.headers["set-cookie"]
