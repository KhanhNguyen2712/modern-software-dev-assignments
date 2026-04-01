from __future__ import annotations

import asyncio
from typing import Any

import httpx

from .config import WeatherSettings
from .errors import (
    EmptyResultError,
    LocationNotFoundError,
    RateLimitError,
    UpstreamServiceError,
    UpstreamTimeoutError,
)
from .models import ResolvedLocation


class OpenMeteoClient:
    def __init__(
        self,
        settings: WeatherSettings | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or WeatherSettings.from_env()
        self._owns_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient(
            timeout=self.settings.timeout_seconds,
            headers={"User-Agent": self.settings.user_agent},
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http_client.aclose()

    async def resolve_location(self, location: str) -> ResolvedLocation:
        payload = await self._request_json(
            f"{self.settings.geocoding_base_url}/search",
            params={"name": location, "count": 1, "language": "en", "format": "json"},
        )
        results = payload.get("results") or []
        if not results:
            raise LocationNotFoundError(f"could not find a weather location for '{location}'")

        first = results[0]
        return ResolvedLocation(
            name=first["name"],
            latitude=first["latitude"],
            longitude=first["longitude"],
            country=first.get("country"),
            timezone=first.get("timezone") or "auto",
            admin1=first.get("admin1"),
        )

    async def get_forecast_payload(
        self,
        *,
        latitude: float,
        longitude: float,
        days: int,
        temperature_unit: str,
        wind_speed_unit: str,
        precipitation_unit: str,
        timezone: str,
    ) -> dict[str, Any]:
        payload = await self._request_json(
            f"{self.settings.base_url}/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": ",".join(
                    [
                        "temperature_2m",
                        "apparent_temperature",
                        "weather_code",
                        "wind_speed_10m",
                        "wind_direction_10m",
                        "is_day",
                    ]
                ),
                "daily": ",".join(
                    [
                        "weather_code",
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "precipitation_sum",
                    ]
                ),
                "forecast_days": days,
                "timezone": timezone,
                "temperature_unit": temperature_unit,
                "wind_speed_unit": wind_speed_unit,
                "precipitation_unit": precipitation_unit,
            },
        )

        if not payload.get("current") and not payload.get("daily"):
            raise EmptyResultError("weather provider returned an empty forecast payload")
        return payload

    async def _request_json(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        attempts = max(self.settings.retry_attempts, 1)
        last_error: Exception | None = None

        for attempt in range(attempts):
            try:
                response = await self._http_client.get(
                    url,
                    params=params,
                    headers={"User-Agent": self.settings.user_agent},
                )
                if response.status_code == 429:
                    raise RateLimitError("weather provider rate limit reached")
                response.raise_for_status()
                return response.json()
            except RateLimitError as exc:
                last_error = exc
            except httpx.TimeoutException:
                last_error = UpstreamTimeoutError("weather provider request timed out")
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code >= 500:
                    last_error = UpstreamServiceError("weather provider is unavailable right now")
                else:
                    last_error = UpstreamServiceError(
                        f"weather provider request failed with status {exc.response.status_code}"
                    )
            except httpx.RequestError as exc:
                last_error = UpstreamServiceError(f"weather provider request failed: {exc}")

            if attempt + 1 < attempts:
                await asyncio.sleep(self.settings.backoff_seconds * (2**attempt))

        assert last_error is not None
        raise last_error

