from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Protocol

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from week3.server.core.models import WeatherReport, build_resource_text, build_tool_payload


class WeatherServiceProtocol(Protocol):
    async def get_current_weather(self, location: str, units: str = "metric") -> WeatherReport:
        ...

    async def get_forecast(
        self, location: str, days: int = 3, units: str = "metric"
    ) -> WeatherReport:
        ...


@dataclass(frozen=True)
class WeatherMcpBundle:
    server: FastMCP
    tool_names: tuple[str, ...]
    resource_templates: tuple[str, ...]
    prompt_names: tuple[str, ...]
    tool_handlers: dict[str, Callable[..., Awaitable[dict[str, Any]]]]
    resource_handlers: dict[str, Callable[..., Awaitable[str]]]
    prompt_handlers: dict[str, Callable[..., str]]


def create_weather_mcp_server(
    weather_service: WeatherServiceProtocol,
    *,
    name: str = "Week3WeatherServer",
    host: str = "127.0.0.1",
    streamable_http_path: str = "/",
    transport_security: TransportSecuritySettings | None = None,
) -> WeatherMcpBundle:
    mcp = FastMCP(
        name=name,
        host=host,
        stateless_http=True,
        json_response=True,
        streamable_http_path=streamable_http_path,
        transport_security=transport_security,
    )

    tool_handlers: dict[str, Callable[..., Awaitable[dict[str, Any]]]] = {}
    resource_handlers: dict[str, Callable[..., Awaitable[str]]] = {}
    prompt_handlers: dict[str, Callable[..., str]] = {}

    @mcp.tool()
    async def get_current_weather(
        location: str, units: str = "metric"
    ) -> dict[str, Any]:
        """Resolve a location and return the current weather."""
        report = await weather_service.get_current_weather(location, units)
        return build_tool_payload(report)

    tool_handlers["get_current_weather"] = get_current_weather

    @mcp.tool()
    async def get_forecast(
        location: str, days: int = 3, units: str = "metric"
    ) -> dict[str, Any]:
        """Resolve a location and return a multi-day weather forecast."""
        report = await weather_service.get_forecast(location, days, units)
        return build_tool_payload(report)

    tool_handlers["get_forecast"] = get_forecast

    @mcp.resource("weather://current/{location}")
    async def current_weather_resource(location: str) -> str:
        report = await weather_service.get_current_weather(location)
        return build_resource_text(report)

    resource_handlers["weather://current/{location}"] = current_weather_resource

    @mcp.resource("weather://forecast/{location}/{days}")
    async def forecast_weather_resource(location: str, days: int = 3) -> str:
        report = await weather_service.get_forecast(location, days=days)
        return build_resource_text(report)

    resource_handlers["weather://forecast/{location}/{days}"] = forecast_weather_resource

    @mcp.prompt()
    def weather_trip_brief(location: str, days: int = 3, units: str = "metric") -> str:
        return (
            f"Use the `get_forecast` weather tool to inspect a {days}-day forecast for {location} "
            f"in {units} units, then summarize clothing advice, rain risk, and any timing issues "
            "for outdoor plans. Mention uncertainty and quote concrete highs, lows, and precipitation."
        )

    prompt_handlers["weather_trip_brief"] = weather_trip_brief

    return WeatherMcpBundle(
        server=mcp,
        tool_names=("get_current_weather", "get_forecast"),
        resource_templates=(
            "weather://current/{location}",
            "weather://forecast/{location}/{days}",
        ),
        prompt_names=("weather_trip_brief",),
        tool_handlers=tool_handlers,
        resource_handlers=resource_handlers,
        prompt_handlers=prompt_handlers,
    )

