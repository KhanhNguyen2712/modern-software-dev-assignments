from __future__ import annotations


class WeatherServiceError(Exception):
    """Base error for user-facing weather service failures."""


class LocationNotFoundError(WeatherServiceError):
    """Raised when the requested location cannot be resolved."""


class EmptyResultError(WeatherServiceError):
    """Raised when the upstream API returns an empty payload."""


class RateLimitError(WeatherServiceError):
    """Raised when the upstream API rate limits requests."""


class UpstreamTimeoutError(WeatherServiceError):
    """Raised when the upstream API times out."""


class UpstreamServiceError(WeatherServiceError):
    """Raised for all other upstream connectivity failures."""

