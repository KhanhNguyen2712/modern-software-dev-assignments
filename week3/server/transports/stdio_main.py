"""STDIO transport entrypoint for the Week 3 Weather MCP server.

Run command
-----------
>>> python -m week3.server.transports.stdio_main

Or via the module directly:
>>> python week3/server/transports/stdio_main.py

Logging rules for STDIO transport
----------------------------------
The MCP STDIO protocol uses **stdout** exclusively for JSON-RPC messages.
ALL logging MUST go to **stderr** (or a file).  Writing anything extra to
stdout will corrupt the protocol stream and break MCP clients.

This module configures a ``StreamHandler`` targeting ``sys.stderr`` with a
structured format and honours the ``MCP_LOG_LEVEL`` environment variable.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys

from week3.server.core import OpenMeteoClient, WeatherService, WeatherSettings
from week3.server.mcp import create_weather_mcp_server

# ---------------------------------------------------------------------------
# Logging — must stay on stderr for STDIO transport
# ---------------------------------------------------------------------------

_LOG_FORMAT = "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def configure_stdio_logging() -> None:
    """Configure the root logger to write only to *stderr*.

    This is called before any other code so that even import-time log messages
    from sub-modules are captured correctly.
    """
    raw_level = os.getenv("MCP_LOG_LEVEL", "INFO").strip().upper()
    level = getattr(logging, raw_level, logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root = logging.getLogger()
    root.setLevel(level)
    # Remove any existing handlers to avoid duplicate output
    root.handlers.clear()
    root.addHandler(handler)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)


def main() -> None:
    """Bootstrap the STDIO MCP server and start serving.

    Lifecycle
    ---------
    1. Configure stderr-only logging (before any imports that log).
    2. Load settings from environment / .env file.
    3. Build the ``OpenMeteoClient`` → ``WeatherService`` → MCP server.
    4. Run FastMCP in STDIO transport mode (blocking).
    5. On exit (normal or keyboard interrupt), close the HTTP client cleanly.
    """
    configure_stdio_logging()

    logger.info("=== Week3 Weather MCP Server — STDIO transport starting ===")

    weather_settings = WeatherSettings.from_env()
    logger.debug(
        "WeatherSettings loaded: base_url=%s timeout=%.1fs retries=%d",
        weather_settings.base_url,
        weather_settings.timeout_seconds,
        weather_settings.retry_attempts,
    )

    weather_client = OpenMeteoClient(weather_settings)
    weather_service = WeatherService(weather_client)

    bundle = create_weather_mcp_server(
        weather_service,
        name="Week3WeatherSTDIO",
        streamable_http_path="/",
    )

    logger.info(
        "Registered: tools=%s | resources=%s | prompts=%s",
        bundle.tool_names,
        bundle.resource_templates,
        bundle.prompt_names,
    )
    logger.info("MCP server ready — listening on STDIO (stdout=JSON-RPC, stderr=logs)")

    try:
        bundle.server.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("STDIO server interrupted by user.")
    finally:
        # Close the shared httpx client; use a fresh event loop if the main
        # loop has already been torn down by FastMCP's runner.
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule cleanup without blocking — best effort
                loop.create_task(weather_client.aclose())
            else:
                loop.run_until_complete(weather_client.aclose())
        except RuntimeError:
            # All loops closed — create a new one just for cleanup
            asyncio.run(weather_client.aclose())
        logger.info("Weather client closed. Server shutdown complete.")


if __name__ == "__main__":
    main()
