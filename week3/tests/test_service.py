from __future__ import annotations

import asyncio

import httpx
import pytest

from week3.server.core.client import OpenMeteoClient
from week3.server.core.config import WeatherSettings
from week3.server.core.errors import LocationNotFoundError, RateLimitError, UpstreamTimeoutError
from week3.server.core.service import WeatherService


def build_service(handler: httpx.MockTransport) -> WeatherService:
    settings = WeatherSettings(timeout_seconds=0.1, retry_attempts=1, backoff_seconds=0.0)
    http_client = httpx.AsyncClient(transport=handler)
    client = OpenMeteoClient(settings=settings, http_client=http_client)
    return WeatherService(client)


def test_get_current_weather_returns_resolved_location_and_summary() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "geocoding-api.open-meteo.com" in str(request.url):
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "name": "Ho Chi Minh City",
                            "latitude": 10.8231,
                            "longitude": 106.6297,
                            "country": "Vietnam",
                            "timezone": "Asia/Ho_Chi_Minh",
                            "admin1": "Ho Chi Minh",
                        }
                    ]
                },
            )

        return httpx.Response(
            200,
            json={
                "current": {
                    "time": "2026-03-19T14:00",
                    "temperature_2m": 32.1,
                    "apparent_temperature": 36.0,
                    "wind_speed_10m": 11.2,
                    "wind_direction_10m": 215,
                    "weather_code": 1,
                    "is_day": 1,
                },
                "daily": {
                    "time": ["2026-03-19"],
                    "weather_code": [1],
                    "temperature_2m_max": [34.8],
                    "temperature_2m_min": [27.2],
                    "precipitation_sum": [0.0],
                },
            },
        )

    service = build_service(httpx.MockTransport(handler))

    report = asyncio.run(service.get_current_weather("Ho Chi Minh City"))

    assert report.location.name == "Ho Chi Minh City"
    assert report.current is not None
    assert report.current.temperature == 32.1
    assert report.summary.startswith("Current weather for Ho Chi Minh City, Vietnam")


def test_get_forecast_rejects_invalid_days() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        raise AssertionError("upstream should not be called for invalid day count")

    service = build_service(httpx.MockTransport(handler))

    with pytest.raises(ValueError, match="days must be between 1 and 7"):
        asyncio.run(service.get_forecast("Da Nang", days=0))


def test_geocoding_empty_results_raise_location_not_found() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": []})

    service = build_service(httpx.MockTransport(handler))

    with pytest.raises(LocationNotFoundError, match="could not find a weather location"):
        asyncio.run(service.get_current_weather("Xyzqwe Unknown"))


def test_rate_limit_error_is_exposed_cleanly() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "geocoding-api.open-meteo.com" in str(request.url):
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "name": "Da Nang",
                            "latitude": 16.0471,
                            "longitude": 108.2068,
                            "country": "Vietnam",
                            "timezone": "Asia/Ho_Chi_Minh",
                        }
                    ]
                },
            )
        return httpx.Response(429, json={"reason": "Too many requests"})

    service = build_service(httpx.MockTransport(handler))

    with pytest.raises(RateLimitError, match="rate limit"):
        asyncio.run(service.get_forecast("Da Nang", days=3))


def test_timeout_error_is_exposed_cleanly() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "geocoding-api.open-meteo.com" in str(request.url):
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "name": "Da Nang",
                            "latitude": 16.0471,
                            "longitude": 108.2068,
                            "country": "Vietnam",
                            "timezone": "Asia/Ho_Chi_Minh",
                        }
                    ]
                },
            )
        raise httpx.ReadTimeout("timed out", request=request)

    service = build_service(httpx.MockTransport(handler))

    with pytest.raises(UpstreamTimeoutError, match="timed out"):
        asyncio.run(service.get_current_weather("Da Nang"))
