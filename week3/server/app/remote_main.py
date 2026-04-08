from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastmcp import Context, FastMCP

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
	sys.path.insert(0, str(SERVER_ROOT))

from core import OpenMeteoClient, WeatherService, WeatherServiceError
from core.models import build_tool_payload

WeatherUnits = Literal["metric", "imperial"]

@asynccontextmanager
async def weather_lifespan(_: FastMCP):
	client = OpenMeteoClient()
	service = WeatherService(client)
	try:
		yield {"weather_service": service}
	finally:
		await client.aclose()


mcp = FastMCP("Weather MCP", lifespan=weather_lifespan)


def _service_from_context(ctx: Context) -> WeatherService:
	service = ctx.lifespan_context.get("weather_service")
	if not isinstance(service, WeatherService):
		raise RuntimeError("weather service is not available")
	return service



@mcp.tool
async def get_current_weather(
	location: str,
	units: Literal["metric", "imperial"] = "metric",
	ctx: Context = None,
) -> dict[str, object]:
	"""Return current weather details for a location."""
	if ctx is None:  # pragma: no cover
		raise RuntimeError("tool context is required")

	service = _service_from_context(ctx)
	try:
		report = await service.get_current_weather(location=location, units=units)
	except WeatherServiceError as exc:
		return {"error": str(exc), "location": location, "units": units}
	return build_tool_payload(report)

@mcp.tool
async def get_weather_forecast(
	location: str,
	days: int = 3,
	units: Literal["metric", "imperial"] = "metric",
	ctx: Context = None,
) -> dict[str, object]:
	"""Return a multi-day weather forecast for a location."""
	if ctx is None:  # pragma: no cover
		raise RuntimeError("tool context is required")

	service = _service_from_context(ctx)
	try:
		report = await service.get_forecast(
			location=location,
			days=days,
			units=units,
		)
	except WeatherServiceError as exc:
		return {
			"error": str(exc),
			"location": location,
			"days": days,
			"units": units,
		}
	return build_tool_payload(report)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(_: object):
    from starlette.responses import JSONResponse
    return JSONResponse({"status": "ok", "service": "weather-mcp-remote"})


if __name__ == "__main__":
	host = os.getenv("MCP_HOST", "127.0.0.1")
	port = int(os.getenv("MCP_PORT", "8000"))
	mcp.run(transport="http", host=host, port=port)
