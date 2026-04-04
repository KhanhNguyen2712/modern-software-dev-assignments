"""Quick verification script for stdio_main.py components."""
import sys
import asyncio
from pathlib import Path

# Add server root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.stdio_main import mcp


async def main():
    print("=" * 50)
    print(f"  MCP Server: {mcp.name}")
    print("=" * 50)

    tools = await mcp.get_tools()
    print(f"\n✅ Tools ({len(tools)}):")
    for name, tool in tools.items():
        print(f"   • {name}: {tool.description[:60]}...")

    resources = await mcp.get_resources()
    print(f"\n✅ Resources ({len(resources)}):")
    for uri, res in resources.items():
        print(f"   • {uri}: {res.name}")

    prompts = await mcp.get_prompts()
    print(f"\n✅ Prompts ({len(prompts)}):")
    for name, prompt in prompts.items():
        print(f"   • {name}: {prompt.description[:60]}...")

    print("\n" + "=" * 50)
    print("  All components registered successfully!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
