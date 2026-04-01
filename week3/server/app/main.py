"""
FastAPI application that mounts the Weather MCP server.

Run with:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from app.remote_main import mcp  # noqa: E402

mcp_app = mcp.http_app(path="/")

app = FastAPI(
    title="Weather MCP Server",
    description=(
        "A FastAPI application that exposes a Model Context Protocol (MCP) "
        "weather server backed by the Open-Meteo API."
    ),
    version="1.0.0",
    lifespan=mcp_app.lifespan,
)


@app.get("/", include_in_schema=False)
async def root() -> JSONResponse:
    return JSONResponse(
        {
            "service": "Weather MCP Server",
            "status": "ok",
            "mcp_endpoint": "/mcp",
            "docs": "/docs",
        }
    )


@app.get("/health", tags=["meta"])
async def health() -> JSONResponse:
    """Liveness probe."""
    return JSONResponse({"status": "ok"})


app.mount("/mcp", mcp_app)
