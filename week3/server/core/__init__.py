from __future__ import annotations

from .client import OpenMeteoClient
from .config import GitHubOAuthConfig, HttpAuthConfig, WeatherSettings
from .errors import (
    EmptyResultError,
    LocationNotFoundError,
    RateLimitError,
    UpstreamServiceError,
    UpstreamTimeoutError,
    WeatherServiceError,
)
from .models import CurrentWeather, ForecastDay, ResolvedLocation, WeatherReport
from .service import WeatherService

__all__ = [
    "CurrentWeather",
    "EmptyResultError",
    "ForecastDay",
    "GitHubOAuthConfig",
    "HttpAuthConfig",
    "LocationNotFoundError",
    "OpenMeteoClient",
    "RateLimitError",
    "ResolvedLocation",
    "UpstreamServiceError",
    "UpstreamTimeoutError",
    "WeatherReport",
    "WeatherService",
    "WeatherServiceError",
    "WeatherSettings",
]
