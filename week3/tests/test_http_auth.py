from __future__ import annotations

import asyncio

import jwt
import pytest

from week3.server.core.config import HttpAuthConfig
from week3.server.transports.auth import (
    AuthError,
    BearerTokenValidator,
    build_protected_resource_metadata,
    extract_bearer_token,
)


def test_extract_bearer_token_requires_bearer_scheme() -> None:
    with pytest.raises(AuthError, match="missing bearer token"):
        extract_bearer_token(None)

    with pytest.raises(AuthError, match="missing bearer token"):
        extract_bearer_token("Basic abc123")


def test_dev_token_validation_returns_auth_context() -> None:
    config = HttpAuthConfig(
        required=True,
        issuer="https://issuer.example.com",
        audience="weather-mcp",
        resource_server_url="https://weather.example.com",
        dev_bearer_token="local-secret",
    )

    context = asyncio.run(BearerTokenValidator(config).validate_token("local-secret"))

    assert context.client_id == "local-weather-client"
    assert context.scopes == ["weather.read"]


def test_jwt_validation_rejects_wrong_audience() -> None:
    config = HttpAuthConfig(
        required=True,
        issuer="https://issuer.example.com",
        audience="weather-mcp",
        resource_server_url="https://weather.example.com",
        jwt_secret="test-secret",
    )
    token = jwt.encode(
        {
            "iss": "https://issuer.example.com",
            "aud": "different-audience",
            "sub": "student-123",
            "scope": "weather.read",
        },
        "test-secret",
        algorithm="HS256",
    )

    with pytest.raises(AuthError, match="invalid bearer token"):
        asyncio.run(BearerTokenValidator(config).validate_token(token))


def test_protected_resource_metadata_includes_resource_and_auth_server() -> None:
    config = HttpAuthConfig(
        required=True,
        issuer="https://issuer.example.com",
        audience="weather-mcp",
        resource_server_url="https://weather.example.com",
        jwks_url="https://issuer.example.com/.well-known/jwks.json",
    )

    metadata = build_protected_resource_metadata(config)

    assert metadata == {
        "resource": "https://weather.example.com/mcp",
        "authorization_servers": ["https://issuer.example.com"],
        "jwks_uri": "https://issuer.example.com/.well-known/jwks.json",
    }


def test_protected_resource_metadata_for_github_provider_uses_github_auth_server() -> None:
    config = HttpAuthConfig(
        required=True,
        provider="github",
        resource_server_url="https://weather.example.com",
    )

    metadata = build_protected_resource_metadata(config)

    assert metadata == {
        "resource": "https://weather.example.com/mcp",
        "authorization_servers": ["https://github.com"],
        "bearer_methods_supported": ["header"],
    }
