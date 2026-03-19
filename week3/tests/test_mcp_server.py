from __future__ import annotations

import asyncio

from week3.server.core.models import CurrentWeather, ForecastDay, ResolvedLocation, WeatherReport
from week3.server.mcp.factory import create_weather_mcp_server


def sample_report() -> WeatherReport:
    return WeatherReport(
        location=ResolvedLocation(
            name="Da Nang",
            latitude=16.0471,
            longitude=108.2068,
            country="Vietnam",
            timezone="Asia/Ho_Chi_Minh",
            admin1="Da Nang",
        ),
        units="metric",
        summary="Current weather for Da Nang, Vietnam: 29.4°C, light rain, wind 9.1 km/h.",
        current=CurrentWeather(
            time="2026-03-19T14:00",
            temperature=29.4,
            apparent_temperature=31.0,
            wind_speed=9.1,
            wind_direction=180,
            weather_code=61,
            weather_description="Light rain",
            is_day=True,
        ),
        forecast=[
            ForecastDay(
                date="2026-03-19",
                temperature_max=31.2,
                temperature_min=24.6,
                precipitation_sum=6.3,
                weather_code=61,
                weather_description="Light rain",
            )
        ],
        warnings=[],
    )


class FakeWeatherService:
    async def get_current_weather(
        self, location: str, units: str = "metric"
    ) -> WeatherReport:
        report = sample_report()
        report.summary = f"Current weather for {location}, Vietnam: 29.4°C, light rain."
        report.units = units
        return report

    async def get_forecast(
        self, location: str, days: int = 3, units: str = "metric"
    ) -> WeatherReport:
        report = sample_report()
        report.summary = f"{days}-day forecast for {location}, Vietnam."
        report.units = units
        return report


def test_create_weather_mcp_server_exposes_expected_capabilities() -> None:
    bundle = create_weather_mcp_server(FakeWeatherService())

    assert bundle.tool_names == ("get_current_weather", "get_forecast")
    assert bundle.resource_templates == (
        "weather://current/{location}",
        "weather://forecast/{location}?days={days}",
    )
    assert bundle.prompt_names == ("weather_trip_brief",)


def test_registered_tool_handler_returns_summary_and_structured_data() -> None:
    bundle = create_weather_mcp_server(FakeWeatherService())

    payload = asyncio.run(bundle.tool_handlers["get_current_weather"]("Da Nang", "metric"))

    assert payload["summary"] == "Current weather for Da Nang, Vietnam: 29.4°C, light rain."
    assert payload["location"]["name"] == "Da Nang"
    assert payload["current"]["weather_description"] == "Light rain"


def test_registered_prompt_mentions_weather_tools() -> None:
    bundle = create_weather_mcp_server(FakeWeatherService())

    prompt = bundle.prompt_handlers["weather_trip_brief"]("Da Nang", days=2, units="metric")

    assert "Da Nang" in prompt
    assert "get_forecast" in prompt
    assert "2-day" in prompt

