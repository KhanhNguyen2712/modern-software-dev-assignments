"""
MCP Server — STDIO Transport Layer
===================================
Entry-point for running the Weather MCP server over Standard I/O (stdio).
All logging is redirected to sys.stderr so that the JSON-RPC data stream
on sys.stdout remains clean and uninterrupted.

Run with:
    python -m app.stdio_main
    # or
    cd week3/server && python app/stdio_main.py
"""

from __future__ import annotations

import json
import logging
import math
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastmcp import FastMCP, Context
from fastmcp.prompts import Message

# ---------------------------------------------------------------------------
# Logging — redirect everything to stderr so stdout stays JSON-RPC–clean
# ---------------------------------------------------------------------------
_LOG_FORMAT = "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s"
_LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format=_LOG_FORMAT,
    datefmt=_LOG_DATE_FMT,
)
logger = logging.getLogger("mcp.stdio")

# ---------------------------------------------------------------------------
# Ensure the `core` package is importable regardless of how the script is run
# ---------------------------------------------------------------------------
SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from core import WeatherService, OpenMeteoClient, WeatherServiceError  # noqa: E402
from core.models import build_tool_payload  # noqa: E402

# ---------------------------------------------------------------------------
# Simulated research database (for tool_nghien_cuu)
# ---------------------------------------------------------------------------
_RESEARCH_DATABASE: dict[str, dict[str, object]] = {
    "machine learning": {
        "title": "Introduction to Machine Learning",
        "summary": "Machine learning is a subset of artificial intelligence that enables "
                   "systems to learn and improve from experience without being explicitly "
                   "programmed.",
        "key_concepts": ["supervised learning", "unsupervised learning", "reinforcement learning"],
        "sources": 42,
        "last_updated": "2025-12-01",
    },
    "climate change": {
        "title": "Climate Change Research Overview",
        "summary": "Global surface temperature has increased faster since 1970 than in any "
                   "other 50-year period over at least the last 2,000 years.",
        "key_concepts": ["greenhouse gases", "carbon footprint", "renewable energy"],
        "sources": 78,
        "last_updated": "2025-11-15",
    },
    "blockchain": {
        "title": "Blockchain Technology Fundamentals",
        "summary": "Blockchain is a decentralized, distributed ledger technology that records "
                   "transactions across many computers in a verifiable and permanent way.",
        "key_concepts": ["decentralization", "smart contracts", "consensus mechanism"],
        "sources": 35,
        "last_updated": "2025-10-20",
    },
    "quantum computing": {
        "title": "Quantum Computing: State of the Art",
        "summary": "Quantum computing leverages quantum-mechanical phenomena such as "
                   "superposition and entanglement to perform computation.",
        "key_concepts": ["qubits", "quantum supremacy", "error correction"],
        "sources": 29,
        "last_updated": "2025-09-30",
    },
}

# ---------------------------------------------------------------------------
# Lifespan — shared services available via Context
# ---------------------------------------------------------------------------


@asynccontextmanager
async def stdio_lifespan(_: FastMCP):
    """Provide shared services (e.g. WeatherService) to tools via context."""
    logger.info("STDIO server starting up — initialising services …")
    client = OpenMeteoClient()
    service = WeatherService(client)
    try:
        yield {"weather_service": service}
    finally:
        await client.aclose()
        logger.info("STDIO server shut down — resources released.")


# ---------------------------------------------------------------------------
# FastMCP server instance (STDIO mode)
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "Weather MCP (STDIO)",
    lifespan=stdio_lifespan,
)


# =========================================================================
#  TOOLS (02)
# =========================================================================


@mcp.tool(
    name="tool_nghien_cuu",
    description=(
        "Research tool — accepts a keyword and returns simulated research data "
        "including title, summary, key concepts, and source count."
    ),
)
async def tool_nghien_cuu(keyword: str, ctx: Context) -> str:
    """
    Receive a keyword and return simulated research data.

    Parameters
    ----------
    keyword : str
        The research topic to look up (e.g. "machine learning").
    """
    logger.info("tool_nghien_cuu called with keyword=%r", keyword)
    normalized = keyword.strip().lower()

    if not normalized:
        error_payload = {
            "error": "INVALID_INPUT",
            "message": "Keyword must not be empty.",
        }
        logger.warning("tool_nghien_cuu — empty keyword received")
        return json.dumps(error_payload, ensure_ascii=False)

    # Try an exact match first, then a fuzzy (substring) match
    result = _RESEARCH_DATABASE.get(normalized)
    if result is None:
        for key, value in _RESEARCH_DATABASE.items():
            if normalized in key or key in normalized:
                result = value
                break

    if result is None:
        # Return a generated placeholder when the topic is unknown
        result = {
            "title": f"Research: {keyword.title()}",
            "summary": (
                f"No pre-existing data for '{keyword}'. This is auto-generated "
                f"simulated research data for demonstration purposes."
            ),
            "key_concepts": [keyword, "data analysis", "further research needed"],
            "sources": 0,
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        }
        logger.info("tool_nghien_cuu — no match; returning generated placeholder")
    else:
        logger.info("tool_nghien_cuu — found data for %r", normalized)

    payload = {
        "status": "success",
        "keyword": keyword,
        "data": result,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


@mcp.tool(
    name="tool_tinh_toan",
    description=(
        "Calculation tool — performs simple arithmetic or logic operations. "
        "Supported operators: add, subtract, multiply, divide, power, sqrt, modulo."
    ),
)
async def tool_tinh_toan(
    operator: str,
    a: float,
    b: float | None = None,
    ctx: Context = None,
) -> str:
    """
    Perform a simple arithmetic / logic calculation.

    Parameters
    ----------
    operator : str
        One of: add, subtract, multiply, divide, power, sqrt, modulo.
    a : float
        First operand (always required).
    b : float | None
        Second operand (optional for unary operators like sqrt).
    """
    logger.info("tool_tinh_toan called: operator=%r, a=%s, b=%s", operator, a, b)
    op = operator.strip().lower()

    try:
        if op == "add":
            result = a + (b if b is not None else 0)
        elif op == "subtract":
            result = a - (b if b is not None else 0)
        elif op == "multiply":
            result = a * (b if b is not None else 1)
        elif op == "divide":
            if b is None or b == 0:
                raise ZeroDivisionError("Division by zero or missing divisor.")
            result = a / b
        elif op == "power":
            result = a ** (b if b is not None else 2)
        elif op == "sqrt":
            if a < 0:
                raise ValueError("Cannot compute square root of a negative number.")
            result = math.sqrt(a)
        elif op == "modulo":
            if b is None or b == 0:
                raise ZeroDivisionError("Modulo by zero or missing divisor.")
            result = a % b
        else:
            payload = {
                "status": "error",
                "message": (
                    f"Unknown operator '{operator}'. "
                    f"Supported: add, subtract, multiply, divide, power, sqrt, modulo."
                ),
            }
            logger.warning("tool_tinh_toan — unknown operator %r", operator)
            return json.dumps(payload, ensure_ascii=False)

        payload = {
            "status": "success",
            "expression": f"{op}({a}, {b})" if b is not None else f"{op}({a})",
            "result": result,
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.info("tool_tinh_toan — result=%s", result)
        return json.dumps(payload, ensure_ascii=False, indent=2)

    except (ZeroDivisionError, ValueError) as exc:
        payload = {
            "status": "error",
            "message": str(exc),
        }
        logger.error("tool_tinh_toan — %s", exc)
        return json.dumps(payload, ensure_ascii=False)


# =========================================================================
#  RESOURCES (02)
# =========================================================================


@mcp.resource(
    "resource://config/settings",
    name="System Configuration",
    description="Returns the current system configuration as a JSON object.",
    mime_type="application/json",
)
def resource_config_settings() -> str:
    """Provide system-level configuration in JSON format."""
    logger.info("resource://config/settings requested")
    config = {
        "server": {
            "name": "Weather MCP Server",
            "version": "1.0.0",
            "transport": "stdio",
            "protocol": "MCP (Model Context Protocol)",
        },
        "weather_api": {
            "provider": "Open-Meteo",
            "base_url": "https://api.open-meteo.com/v1",
            "geocoding_url": "https://geocoding-api.open-meteo.com/v1",
            "timeout_seconds": 10,
            "retry_attempts": 2,
        },
        "features": {
            "tools": ["tool_nghien_cuu", "tool_tinh_toan"],
            "resources": [
                "resource://config/settings",
                "resource://docs/readme",
            ],
            "prompts": ["prompt_tro_ly_phan_tich"],
        },
        "logging": {
            "level": "INFO",
            "output": "stderr",
            "format": _LOG_FORMAT,
        },
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


@mcp.resource(
    "resource://docs/readme",
    name="User Guide",
    description="Returns the user guide / README documentation for the MCP server.",
    mime_type="text/plain",
)
def resource_docs_readme() -> str:
    """Provide usage instructions for the MCP server."""
    logger.info("resource://docs/readme requested")
    return (
        "═══════════════════════════════════════════════════════════════\n"
        "  Weather MCP Server — User Guide\n"
        "═══════════════════════════════════════════════════════════════\n"
        "\n"
        "1. OVERVIEW\n"
        "   This server exposes weather data and utility tools through\n"
        "   the Model Context Protocol (MCP) over STDIO transport.\n"
        "\n"
        "2. AVAILABLE TOOLS\n"
        "   ┌──────────────────┬────────────────────────────────────┐\n"
        "   │ tool_nghien_cuu  │ Research a keyword — returns       │\n"
        "   │                  │ simulated academic research data.  │\n"
        "   ├──────────────────┼────────────────────────────────────┤\n"
        "   │ tool_tinh_toan   │ Arithmetic / logic calculations.   │\n"
        "   │                  │ Ops: add, subtract, multiply,      │\n"
        "   │                  │ divide, power, sqrt, modulo.       │\n"
        "   └──────────────────┴────────────────────────────────────┘\n"
        "\n"
        "3. AVAILABLE RESOURCES\n"
        "   • resource://config/settings  → System config (JSON)\n"
        "   • resource://docs/readme      → This user guide\n"
        "\n"
        "4. AVAILABLE PROMPTS\n"
        "   • prompt_tro_ly_phan_tich     → Analysis assistant prompt\n"
        "\n"
        "5. RUNNING THE SERVER\n"
        "   $ cd week3/server\n"
        "   $ python app/stdio_main.py\n"
        "\n"
        "6. INTEGRATION\n"
        "   Configure Claude Desktop or your MCP client to launch\n"
        "   this server via stdio transport.\n"
        "\n"
        "═══════════════════════════════════════════════════════════════\n"
    )


# =========================================================================
#  PROMPTS (01)
# =========================================================================


@mcp.prompt(
    name="prompt_tro_ly_phan_tich",
    description="Analysis assistant prompt — guides the AI on how to analyse data from tools.",
)
def prompt_tro_ly_phan_tich(keyword: str, operator: str = "add") -> list[Message]:
    """
    Generate a structured analysis prompt that instructs the AI how to use
    the research and calculation tools to produce an insightful report.

    Parameters
    ----------
    keyword : str
        The research topic to investigate with tool_nghien_cuu.
    operator : str
        The arithmetic operation to demonstrate with tool_tinh_toan.
    """
    logger.info(
        "prompt_tro_ly_phan_tich generated: keyword=%r, operator=%r",
        keyword, operator,
    )
    return [
        Message(
            role="user",
            content=(
                f"You are a senior data analyst. Your task is to perform a comprehensive "
                f"analysis using the following MCP tools available on this server:\n"
                f"\n"
                f"── STEP 1: Research Phase ──────────────────────────────────\n"
                f"Use the 'tool_nghien_cuu' tool with the keyword \"{keyword}\" to retrieve "
                f"simulated research data. Examine the returned JSON carefully, paying "
                f"attention to:\n"
                f"  • The title and summary of the research\n"
                f"  • The list of key concepts\n"
                f"  • The number of sources cited\n"
                f"  • The last updated date\n"
                f"\n"
                f"── STEP 2: Computation Phase ─────────────────────────────\n"
                f"Use the 'tool_tinh_toan' tool with operator=\"{operator}\" to perform "
                f"a sample calculation that is relevant to the research topic. For example, "
                f"you could compute the ratio of sources, growth percentages, or any metric "
                f"that adds quantitative depth to your analysis.\n"
                f"\n"
                f"── STEP 3: Synthesis & Report ────────────────────────────\n"
                f"Combine the research data and the computation result into a clear, "
                f"structured analysis report. The report should include:\n"
                f"  1. Executive Summary (2-3 sentences)\n"
                f"  2. Key Findings from the research data\n"
                f"  3. Quantitative Analysis using the calculation result\n"
                f"  4. Conclusions & Recommendations\n"
                f"\n"
                f"── OUTPUT FORMAT ─────────────────────────────────────────\n"
                f"Present the final report in Markdown format with clear headings, "
                f"bullet points, and a professional tone."
            ),
        ),
        Message(
            role="assistant",
            content=(
                "Understood. I will now execute the analysis workflow:\n"
                "1. First, I will call `tool_nghien_cuu` to gather research data.\n"
                "2. Then, I will call `tool_tinh_toan` for quantitative analysis.\n"
                "3. Finally, I will synthesise both results into a structured report.\n\n"
                "Let me begin with the research phase."
            ),
        ),
    ]


# =========================================================================
#  Entry-point
# =========================================================================

if __name__ == "__main__":
    logger.info("Starting MCP server on STDIO transport …")
    mcp.run(transport="stdio")
