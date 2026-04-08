from __future__ import annotations

import re
from typing import Literal
from urllib.parse import unquote

from pydantic import BaseModel, Field, field_validator

Units = Literal["metric", "imperial"]


def normalize_location(value: str) -> str:
    normalized = unquote(value.strip())
    normalized = normalized.replace("+", " ")
    normalized = re.sub(r"[_-]+", " ", normalized)
    normalized = re.sub(r"([a-z])([A-Z])", r"\1 \2", normalized)
    normalized = normalized.strip(" \t\r\n,;:!?/")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if not normalized:
        raise ValueError("location is required")
    return normalized


class WeatherRequest(BaseModel):
    location: str = Field(..., description="Human-readable location to resolve.")
    units: Units = "metric"

    @field_validator("location")
    @classmethod
    def validate_location(cls, value: str) -> str:
        return normalize_location(value)


class ForecastRequest(WeatherRequest):
    days: int = Field(default=3)

    @field_validator("days")
    @classmethod
    def validate_days(cls, value: int) -> int:
        if value < 1 or value > 7:
            raise ValueError("days must be between 1 and 7")
        return value


class ResolvedLocation(BaseModel):
    name: str
    latitude: float
    longitude: float
    country: str | None = None
    timezone: str = "auto"
    admin1: str | None = None

    @property
    def display_name(self) -> str:
        if self.country:
            return f"{self.name}, {self.country}"
        return self.name


class CurrentWeather(BaseModel):
    time: str
    temperature: float
    apparent_temperature: float | None = None
    wind_speed: float
    wind_direction: float | None = None
    weather_code: int
    weather_description: str
    is_day: bool


class ForecastDay(BaseModel):
    date: str
    temperature_max: float
    temperature_min: float
    precipitation_sum: float
    weather_code: int
    weather_description: str


class WeatherReport(BaseModel):
    location: ResolvedLocation
    units: Units
    summary: str
    current: CurrentWeather | None = None
    forecast: list[ForecastDay] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def build_tool_payload(report: WeatherReport) -> dict[str, object]:
    payload: dict[str, object] = {
        "summary": report.summary,
        "location": report.location.model_dump(),
        "units": report.units,
        "warnings": report.warnings,
    }
    if report.current is not None:
        payload["current"] = report.current.model_dump()
    if report.forecast:
        payload["forecast"] = [day.model_dump() for day in report.forecast]
    return payload


def build_resource_text(report: WeatherReport) -> str:
    lines = [report.summary]
    if report.current is not None:
        lines.append(
            "Current:"
            f" {report.current.temperature}{temperature_symbol(report.units)},"
            f" {report.current.weather_description},"
            f" wind {report.current.wind_speed} {wind_speed_symbol(report.units)}"
        )
    if report.forecast:
        lines.append("Forecast:")
        for day in report.forecast:
            lines.append(
                f"- {day.date}: {day.weather_description}, "
                f"high {day.temperature_max}{temperature_symbol(report.units)}, "
                f"low {day.temperature_min}{temperature_symbol(report.units)}, "
                f"precipitation {day.precipitation_sum}{precipitation_symbol(report.units)}"
            )
    if report.warnings:
        lines.append("Warnings: " + "; ".join(report.warnings))
    return "\n".join(lines)


def temperature_symbol(units: Units) -> str:
    return "°F" if units == "imperial" else "°C"


def wind_speed_symbol(units: Units) -> str:
    return "mph" if units == "imperial" else "km/h"


def precipitation_symbol(units: Units) -> str:
    return "in" if units == "imperial" else "mm"
