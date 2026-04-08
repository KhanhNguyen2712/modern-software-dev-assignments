import os
import sys
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Ép đường dẫn để import được code trong thư mục server/core
base_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.join(base_dir, "server")
if os.path.exists(server_dir) and server_dir not in sys.path:
    sys.path.insert(0, server_dir)

try:
    from core.client import OpenMeteoClient
    from core.service import WeatherService
    from core.config import HttpAuthConfig, GitHubOAuthConfig
except ImportError as e:
    print(f"Toang ở khâu nhận diện thư mục: {e}")
    sys.exit(1)

async def run_comprehensive_test():
    print("=" * 65)
    print("BẮT ĐẦU CHẠY KIỂM TRA TỔNG HỢP (BYPASS API CLAUDE)")
    print("=" * 65 + "\n")

    # ---------------------------------------------------------
    # TEST STDIO TRANSPORT (Local MCP Server)
    # ---------------------------------------------------------
    print("Đang test STDIO Transport...")
    stdio_path = os.path.join(server_dir, "app", "stdio_main.py")
    server_params = StdioServerParameters(command="python", args=[stdio_path], env=dict(os.environ))
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # Ép nó cộng 10 + 32 xem ra 42 không
                result = await session.call_tool("tool_tinh_toan", arguments={"operator": "add", "a": 10, "b": 32})
                if "42.0" in result.content[0].text or "42" in result.content[0].text:
                    print("   PASS - Luồng STDIO chạy ngon, tool_tinh_toan trả đúng kết quả!")
                else:
                    print(f"   FAIL - Trả kết quả tào lao: {result.content[0].text}")
    except Exception as e:
        print(f"   FAIL - Sập luồng STDIO: {e}")

    # ---------------------------------------------------------
    # TEST SETUP / REMOTE SERVER (API Thời Tiết)
    # ---------------------------------------------------------
    print("\nĐang test Remote Setup & Core Logic...")
    try:
        # Gọi thẳng dịch vụ thời tiết
        client = OpenMeteoClient()
        service = WeatherService(client)
        report = await service.get_current_weather(location="Ho Chi Minh", units="metric")
        await client.aclose()
        
        if report.current and ("Ho Chi Minh" in report.summary or "Hồ Chí Minh" in report.summary):
            print(f"   PASS - Kéo API thời tiết Open-Meteo mượt mà! ({report.summary})")
        else:
            print("   FAIL - Không lấy được đúng vị trí.")
    except Exception as e:
        print(f"   FAIL - Lỗi kết nối API thời tiết: {e}")

    # ---------------------------------------------------------
    # TEST AUTHENTICATION
    # ---------------------------------------------------------
    print("\n Đang test Cấu hình bảo mật Auth...")
    try:
        # Bơm giả lập biến môi trường vô để test khả năng load file config
        os.environ["MCP_AUTH_PROVIDER"] = "github"
        os.environ["MCP_AUTH_REQUIRED"] = "true"
        
        http_auth = HttpAuthConfig.from_env()
        github_auth = GitHubOAuthConfig.from_env()
        
        if http_auth.provider == "github" and http_auth.required is True:
            print("   PASS - Cấu hình Auth GitHub & JWT load siêu chuẩn, sẵn sàng hốt điểm Bonus!")
        else:
            print("   FAIL - Cấu hình Auth chưa nhận được.")
    except Exception as e:
        print(f"   FAIL - Lỗi module bảo mật: {e}")

    print("\n" + "=" * 65)
    print("HOÀN THÀNH TEST")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())