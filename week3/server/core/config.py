from __future__ import annotations

import os
from typing import Self

from pydantic import BaseModel, Field, field_validator


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_csv(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


class WeatherSettings(BaseModel):
    base_url: str = "https://api.open-meteo.com/v1"
    geocoding_base_url: str = "https://geocoding-api.open-meteo.com/v1"
    timeout_seconds: float = Field(default=10.0, gt=0)
    user_agent: str = "week3-mcp-weather-server/1.0"
    retry_attempts: int = Field(default=2, ge=1, le=5)
    backoff_seconds: float = Field(default=0.2, ge=0)

    @classmethod
    def from_env(cls) -> Self:
        return cls(
            base_url=os.getenv("WEATHER_BASE_URL", cls.model_fields["base_url"].default),
            geocoding_base_url=os.getenv(
                "WEATHER_GEOCODING_BASE_URL", cls.model_fields["geocoding_base_url"].default
            ),
            timeout_seconds=float(
                os.getenv(
                    "WEATHER_TIMEOUT_SECONDS",
                    str(cls.model_fields["timeout_seconds"].default),
                )
            ),
            user_agent=os.getenv("WEATHER_USER_AGENT", cls.model_fields["user_agent"].default),
            retry_attempts=int(
                os.getenv(
                    "WEATHER_RETRY_ATTEMPTS",
                    str(cls.model_fields["retry_attempts"].default),
                )
            ),
            backoff_seconds=float(
                os.getenv(
                    "WEATHER_BACKOFF_SECONDS",
                    str(cls.model_fields["backoff_seconds"].default),
                )
            ),
        )


class HttpAuthConfig(BaseModel):
    required: bool = False
    provider: str = "custom_jwt"
    issuer: str | None = None
    audience: str | None = None
    jwks_url: str | None = None
    jwt_secret: str | None = None
    resource_server_url: str = "http://127.0.0.1:8000"
    dev_bearer_token: str | None = None
    dev_client_id: str = "local-weather-client"
    required_scopes: list[str] = Field(default_factory=lambda: ["weather.read"])

    @field_validator("resource_server_url")
    @classmethod
    def validate_resource_server_url(cls, value: str) -> str:
        return value.rstrip("/")

    @classmethod
    def from_env(cls) -> Self:
        provider = os.getenv("MCP_AUTH_PROVIDER", cls.model_fields["provider"].default)
        scope_default = ["read:user"] if provider == "github" else ["weather.read"]
        return cls(
            required=_parse_bool(os.getenv("MCP_AUTH_REQUIRED"), default=False),
            provider=provider,
            issuer=os.getenv("MCP_AUTH_ISSUER"),
            audience=os.getenv("MCP_AUTH_AUDIENCE"),
            jwks_url=os.getenv("MCP_AUTH_JWKS_URL"),
            jwt_secret=os.getenv("MCP_AUTH_JWT_SECRET"),
            resource_server_url=os.getenv(
                "MCP_AUTH_RESOURCE_SERVER_URL",
                cls.model_fields["resource_server_url"].default,
            ),
            dev_bearer_token=os.getenv("MCP_AUTH_DEV_TOKEN"),
            dev_client_id=os.getenv(
                "MCP_AUTH_DEV_CLIENT_ID", cls.model_fields["dev_client_id"].default
            ),
            required_scopes=_parse_csv(
                os.getenv("MCP_AUTH_REQUIRED_SCOPES"),
                scope_default,
            ),
        )


class GitHubOAuthConfig(BaseModel):
    enabled: bool = False
    client_id: str | None = None
    client_secret: str | None = None
    redirect_uri: str | None = None
    scopes: list[str] = Field(default_factory=lambda: ["read:user"])
    authorize_url: str = "https://github.com/login/oauth/authorize"
    access_token_url: str = "https://github.com/login/oauth/access_token"
    api_base_url: str = "https://api.github.com"

    @classmethod
    def from_env(cls) -> Self:
        return cls(
            enabled=_parse_bool(os.getenv("GITHUB_OAUTH_ENABLED"), default=False),
            client_id=os.getenv("GITHUB_CLIENT_ID"),
            client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
            redirect_uri=os.getenv("GITHUB_REDIRECT_URI"),
            scopes=_parse_csv(os.getenv("GITHUB_OAUTH_SCOPES"), ["read:user"]),
            authorize_url=os.getenv(
                "GITHUB_OAUTH_AUTHORIZE_URL",
                cls.model_fields["authorize_url"].default,
            ),
            access_token_url=os.getenv(
                "GITHUB_OAUTH_ACCESS_TOKEN_URL",
                cls.model_fields["access_token_url"].default,
            ),
            api_base_url=os.getenv(
                "GITHUB_API_BASE_URL",
                cls.model_fields["api_base_url"].default,
            ),
        )
