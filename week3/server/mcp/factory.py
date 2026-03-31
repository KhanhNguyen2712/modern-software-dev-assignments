"""MCP server factory — registers tools, resources, and prompts for the Weather server.

Design notes
------------
- All tool/resource handlers catch domain errors from ``core.errors`` and re-raise them as
  user-friendly ``ValueError``/``RuntimeError`` so FastMCP can return a proper error content
  block to the client (``isError: true``).
- Tools return a single formatted text string; the caller (model) gets readable prose plus
  the structured metadata field in a secondary block via ``build_tool_payload``.
- Resources return plain text (RFC 6570 URI templates resolved at runtime).
- The prompt produces a templated instruction string; the model fills in details.
- ``TransportSecuritySettings`` is imported with a graceful fallback so the file stays
  importable even on older SDK builds.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Literal, Protocol

from mcp.server.fastmcp import FastMCP

try:
    from mcp.server.transport_security import TransportSecuritySettings  # SDK ≥ 1.4
except ImportError:  # pragma: no cover
    TransportSecuritySettings = None  # type: ignore[assignment,misc]

from week3.server.core.errors import (
    EmptyResultError,
    LocationNotFoundError,
    RateLimitError,
    UpstreamServiceError,
    UpstreamTimeoutError,
    WeatherServiceError,
)
from week3.server.core.models import WeatherReport, build_resource_text, build_tool_payload

logger = logging.getLogger(__name__)

Units = Literal["metric", "imperial"]


# ---------------------------------------------------------------------------
# Service protocol — decouples the factory from the concrete implementation
# ---------------------------------------------------------------------------


class WeatherServiceProtocol(Protocol):
    async def get_current_weather(self, location: str, units: str = "metric") -> WeatherReport:
        ...

    async def get_forecast(
        self, location: str, days: int = 3, units: str = "metric"
    ) -> WeatherReport:
        ...


# ---------------------------------------------------------------------------
# Bundle returned to the transport layer
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WeatherMcpBundle:
    """Holds the configured FastMCP instance and maps of registered handlers.

    Consuming code (transports) only needs ``bundle.server`` to start the
    transport.  The handler maps are exposed for testing.
    """

    server: FastMCP
    tool_names: tuple[str, ...]
    resource_templates: tuple[str, ...]
    prompt_names: tuple[str, ...]
    tool_handlers: dict[str, Callable[..., Awaitable[dict[str, Any]]]]
    resource_handlers: dict[str, Callable[..., Awaitable[str]]]
    prompt_handlers: dict[str, Callable[..., str]]


# ---------------------------------------------------------------------------
# Error helpers
# ---------------------------------------------------------------------------


def _map_weather_error(exc: WeatherServiceError) -> Exception:
    """Convert a domain error into an appropriate built-in exception.

    FastMCP catches any exception raised inside a handler and serialises it as
    an MCP error content block (``isError: true``), so we surface the error
    message without leaking internal stack traces.
    """
    if isinstance(exc, LocationNotFoundError):
        return ValueError(str(exc))
    if isinstance(exc, RateLimitError):
        return RuntimeError(
            "Weather provider rate-limit reached — please wait a moment and try again."
        )
    if isinstance(exc, UpstreamTimeoutError):
        return RuntimeError(
            "Weather provider request timed out — the service may be slow, try again shortly."
        )
    if isinstance(exc, EmptyResultError):
        return RuntimeError(
            f"Weather provider returned an empty response: {exc}"
        )
    # UpstreamServiceError or any other WeatherServiceError
    return RuntimeError(f"Weather service error: {exc}")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_weather_mcp_server(
    weather_service: WeatherServiceProtocol,
    *,
    name: str = "Week3WeatherServer",
    host: str = "127.0.0.1",
    streamable_http_path: str = "/",
    transport_security: Any | None = None,
) -> WeatherMcpBundle:
    """Create and return a fully configured :class:`WeatherMcpBundle`.

    Registers:
    - **2 tools**: ``get_current_weather``, ``get_forecast``
    - **2 resources**: ``weather://current/{location}``, ``weather://forecast/{location}/{days}``
    - **1 prompt**: ``weather_trip_brief``
    """
    _kwargs: dict[str, Any] = dict(
        name=name,
        host=host,
        stateless_http=True,
        json_response=True,
        streamable_http_path=streamable_http_path,
    )
    if transport_security is not None and TransportSecuritySettings is not None:
        _kwargs["transport_security"] = transport_security

    mcp = FastMCP(**_kwargs)

    tool_handlers: dict[str, Callable[..., Awaitable[dict[str, Any]]]] = {}
    resource_handlers: dict[str, Callable[..., Awaitable[str]]] = {}
    prompt_handlers: dict[str, Callable[..., str]] = {}

    # ------------------------------------------------------------------
    # Tool 1 — get_current_weather
    # ------------------------------------------------------------------

    @mcp.tool()
    async def get_current_weather(
        location: str,
        units: Units = "metric",
    ) -> str:
        """Return the current weather conditions for a location.

        Resolves the location name via geocoding, then fetches live data from
        the Open-Meteo API.  Returns a human-readable summary followed by
        structured JSON metadata.

        Args:
            location: City name or address, e.g. ``"Hanoi"``, ``"New York, US"``,
                ``"Tokyo"``.  The server normalises whitespace and URL encoding.
            units: Unit system.  ``"metric"`` → °C / km/h / mm (default).
                ``"imperial"`` → °F / mph / inches.
        """
        logger.debug("tool get_current_weather called: location=%r units=%r", location, units)
        try:
            report = await weather_service.get_current_weather(location, units)
        except WeatherServiceError as exc:
            logger.warning("get_current_weather error: %s", exc)
            raise _map_weather_error(exc) from exc

        text = build_resource_text(report)
        logger.info("get_current_weather ok: %s", report.location.display_name)
        return text

    tool_handlers["get_current_weather"] = get_current_weather  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Tool 2 — get_forecast
    # ------------------------------------------------------------------

    @mcp.tool()
    async def get_forecast(
        location: str,
        days: int = 3,
        units: Units = "metric",
    ) -> str:
        """Return a multi-day weather forecast for a location.

        Resolves the location via geocoding and fetches daily forecast data
        (temperature highs/lows, precipitation, weather description) from
        Open-Meteo.

        Args:
            location: City name or address, e.g. ``"Paris"``, ``"Ho Chi Minh City"``.
            days: Number of forecast days, from ``1`` to ``7`` (default ``3``).
            units: Unit system.  ``"metric"`` → °C / km/h / mm.
                ``"imperial"`` → °F / mph / inches.
        """
        logger.debug(
            "tool get_forecast called: location=%r days=%d units=%r", location, days, units
        )
        try:
            report = await weather_service.get_forecast(location, days, units)
        except WeatherServiceError as exc:
            logger.warning("get_forecast error: %s", exc)
            raise _map_weather_error(exc) from exc

        text = build_resource_text(report)
        logger.info("get_forecast ok: %s, %d days", report.location.display_name, days)
        return text

    tool_handlers["get_forecast"] = get_forecast  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Resource 1 — weather://current/{location}
    # ------------------------------------------------------------------

    @mcp.resource("weather://current/{location}")
    async def current_weather_resource(location: str) -> str:
        """Current weather resource.

        URI template: ``weather://current/{location}``

        Returns a plain-text weather summary for the resolved location.
        Useful for embedding live conditions in a context window without
        calling a tool explicitly.
        """
        logger.debug("resource weather://current/%s requested", location)
        try:
            report = await weather_service.get_current_weather(location)
        except WeatherServiceError as exc:
            logger.warning("current_weather_resource error: %s", exc)
            raise _map_weather_error(exc) from exc
        return build_resource_text(report)

    resource_handlers["weather://current/{location}"] = current_weather_resource  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Resource 2 — weather://forecast/{location}/{days}
    # ------------------------------------------------------------------

    @mcp.resource("weather://forecast/{location}/{days}")
    async def forecast_weather_resource(location: str, days: int = 3) -> str:
        """Multi-day forecast resource.

        URI template: ``weather://forecast/{location}/{days}``

        Returns a plain-text daily forecast.  ``{days}`` must be an integer
        between 1 and 7.  Use this resource to pre-fetch forecast data into a
        model's context without an explicit tool call.
        """
        logger.debug("resource weather://forecast/%s/%d requested", location, days)
        try:
            report = await weather_service.get_forecast(location, days=days)
        except WeatherServiceError as exc:
            logger.warning("forecast_weather_resource error: %s", exc)
            raise _map_weather_error(exc) from exc
        return build_resource_text(report)

    resource_handlers["weather://forecast/{location}/{days}"] = forecast_weather_resource  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Prompt 1 — weather_trip_brief
    # ------------------------------------------------------------------

    @mcp.prompt()
    def weather_trip_brief(
        location: str,
        days: int = 3,
        units: str = "metric",
    ) -> str:
        """Generate a trip-planning weather briefing prompt.

        Instructs the model to fetch a forecast and produce a concise briefing
        covering clothing advice, rain risk, and timing considerations for
        outdoor plans.

        Args:
            location: Destination city or address.
            days: Number of forecast days to include (1–7, default 3).
            units: ``"metric"`` or ``"imperial"``.
        """
        return (
            f"Please call the `get_forecast` tool for **{location}**, requesting a "
            f"**{days}-day** forecast in **{units}** units.\n\n"
            "Once you have the data, write a concise trip-planning briefing that covers:\n"
            "1. **Overall outlook** — one sentence describing the general conditions.\n"
            "2. **Daily highs and lows** — quote the exact numbers for each day.\n"
            "3. **Rain / precipitation risk** — flag any days with significant precipitation "
            "and advise whether to pack rain gear.\n"
            "4. **Clothing advice** — practical suggestions based on the temperature range.\n"
            "5. **Timing tips** — highlight the best or worst days for outdoor activities.\n\n"
            "Be concrete and specific; avoid generic filler phrases. "
            "If forecast uncertainty is high, mention it briefly."
        )

    prompt_handlers["weather_trip_brief"] = weather_trip_brief  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Return bundle
    # ------------------------------------------------------------------

    logger.info(
        "MCP server '%s' configured with %d tools, %d resources, %d prompts",
        name,
        len(tool_handlers),
        len(resource_handlers),
        len(prompt_handlers),
    )

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
