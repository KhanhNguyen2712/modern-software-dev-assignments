from __future__ import annotations

import asyncio
import logging
import os
import sys

from week3.server.core import OpenMeteoClient, WeatherService, WeatherSettings
from week3.server.mcp import create_weather_mcp_server


def configure_stdio_logging() -> None:
    level = os.getenv("MCP_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, stream=sys.stderr, force=True)


def main() -> None:
    configure_stdio_logging()
    weather_settings = WeatherSettings.from_env()
    weather_client = OpenMeteoClient(weather_settings)
    weather_service = WeatherService(weather_client)
    bundle = create_weather_mcp_server(
        weather_service,
        name="Week3WeatherSTDIO",
        streamable_http_path="/",
    )

    try:
        bundle.server.run(transport="stdio")
    finally:
        asyncio.run(weather_client.aclose())


if __name__ == "__main__":
    main()

