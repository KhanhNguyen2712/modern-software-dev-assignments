from __future__ import annotations

from .client import OpenMeteoClient
from .errors import EmptyResultError
from .models import (
    CurrentWeather,
    ForecastDay,
    ForecastRequest,
    WeatherReport,
    WeatherRequest,
    precipitation_symbol,
    temperature_symbol,
    wind_speed_symbol,
)

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}


class WeatherService:
    def __init__(self, client: OpenMeteoClient) -> None:
        self.client = client

    async def get_current_weather(
        self, location: str, units: str = "metric"
    ) -> WeatherReport:
        request = WeatherRequest(location=location, units=units)
        resolved = await self.client.resolve_location(request.location)
        payload = await self.client.get_forecast_payload(
            latitude=resolved.latitude,
            longitude=resolved.longitude,
            days=1,
            temperature_unit=self._temperature_unit(request.units),
            wind_speed_unit=self._wind_speed_unit(request.units),
            precipitation_unit=self._precipitation_unit(request.units),
            timezone=resolved.timezone,
        )
        current = self._build_current(payload)
        forecast = self._build_forecast(payload)
        summary = (
            f"Current weather for {resolved.display_name}: "
            f"{current.temperature}{temperature_symbol(request.units)}, "
            f"{current.weather_description.lower()}, "
            f"wind {current.wind_speed} {wind_speed_symbol(request.units)}."
        )
        return WeatherReport(
            location=resolved,
            units=request.units,
            summary=summary,
            current=current,
            forecast=forecast[:1],
            warnings=[],
        )

    async def get_forecast(
        self, location: str, days: int = 3, units: str = "metric"
    ) -> WeatherReport:
        request = ForecastRequest(location=location, days=days, units=units)
        resolved = await self.client.resolve_location(request.location)
        payload = await self.client.get_forecast_payload(
            latitude=resolved.latitude,
            longitude=resolved.longitude,
            days=request.days,
            temperature_unit=self._temperature_unit(request.units),
            wind_speed_unit=self._wind_speed_unit(request.units),
            precipitation_unit=self._precipitation_unit(request.units),
            timezone=resolved.timezone,
        )
        current = self._build_current(payload)
        forecast = self._build_forecast(payload)[: request.days]
        if not forecast:
            raise EmptyResultError("weather provider returned no forecast days")
        summary = (
            f"{request.days}-day forecast for {resolved.display_name}: "
            f"{forecast[0].weather_description.lower()} today, "
            f"high {forecast[0].temperature_max}{temperature_symbol(request.units)}, "
            f"low {forecast[0].temperature_min}{temperature_symbol(request.units)}, "
            f"precipitation {forecast[0].precipitation_sum}{precipitation_symbol(request.units)}."
        )
        return WeatherReport(
            location=resolved,
            units=request.units,
            summary=summary,
            current=current,
            forecast=forecast,
            warnings=[],
        )

    def _build_current(self, payload: dict[str, object]) -> CurrentWeather:
        current_payload = payload.get("current")
        if not isinstance(current_payload, dict):
            raise EmptyResultError("weather provider returned an empty current weather payload")
        weather_code = int(current_payload["weather_code"])
        return CurrentWeather(
            time=str(current_payload["time"]),
            temperature=float(current_payload["temperature_2m"]),
            apparent_temperature=float(current_payload.get("apparent_temperature", 0.0)),
            wind_speed=float(current_payload["wind_speed_10m"]),
            wind_direction=float(current_payload.get("wind_direction_10m", 0.0)),
            weather_code=weather_code,
            weather_description=self._describe_weather_code(weather_code),
            is_day=bool(current_payload["is_day"]),
        )

    def _build_forecast(self, payload: dict[str, object]) -> list[ForecastDay]:
        daily_payload = payload.get("daily")
        if not isinstance(daily_payload, dict):
            raise EmptyResultError("weather provider returned an empty daily forecast payload")
        dates = daily_payload.get("time") or []
        codes = daily_payload.get("weather_code") or []
        highs = daily_payload.get("temperature_2m_max") or []
        lows = daily_payload.get("temperature_2m_min") or []
        precipitation = daily_payload.get("precipitation_sum") or []
        if not dates:
            raise EmptyResultError("weather provider returned no forecast days")

        forecast: list[ForecastDay] = []
        for date, code, high, low, rain in zip(dates, codes, highs, lows, precipitation):
            code_int = int(code)
            forecast.append(
                ForecastDay(
                    date=str(date),
                    temperature_max=float(high),
                    temperature_min=float(low),
                    precipitation_sum=float(rain),
                    weather_code=code_int,
                    weather_description=self._describe_weather_code(code_int),
                )
            )
        return forecast

    def _describe_weather_code(self, code: int) -> str:
        return WEATHER_CODES.get(code, f"Weather code {code}")

    def _temperature_unit(self, units: str) -> str:
        return "fahrenheit" if units == "imperial" else "celsius"

    def _wind_speed_unit(self, units: str) -> str:
        return "mph" if units == "imperial" else "kmh"

    def _precipitation_unit(self, units: str) -> str:
        return "inch" if units == "imperial" else "mm"

