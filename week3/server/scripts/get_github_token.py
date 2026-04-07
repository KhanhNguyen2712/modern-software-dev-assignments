"""
scripts/get_github_token.py
===========================
Quick OAuth helper — opens the browser to GitHub, listens on a local
callback server, and prints the access_token you can use with the MCP server.

Usage:
    python scripts/get_github_token.py

Requirements: pip install httpx python-dotenv
"""
from __future__ import annotations

import os
import secrets
import sys
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load .env from week3/ root
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=True)

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://127.0.0.1:9999/callback")
SCOPES = os.getenv("GITHUB_OAUTH_SCOPES", "read:user")

if not CLIENT_ID or not CLIENT_SECRET:
    sys.exit(
        "❌  GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET must be set in your .env file.\n"
        "    See .env.example for instructions."
    )

_state = secrets.token_urlsafe(16)
_code: str | None = None


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        global _code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if params.get("state", [None])[0] != _state:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"State mismatch - possible CSRF. Close this tab.")
            return

        _code = params.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(
            b"<h2>Authorization successful!</h2>"
            b"<p>You can close this tab and check your terminal.</p>"
        )

    def log_message(self, *args):  # suppress server logs
        pass


def main() -> None:
    callback_port = int(urllib.parse.urlparse(REDIRECT_URI).port or 9999)

    auth_url = (
        "https://github.com/login/oauth/authorize?"
        + urllib.parse.urlencode(
            {
                "client_id": CLIENT_ID,
                "redirect_uri": REDIRECT_URI,
                "scope": SCOPES,
                "state": _state,
            }
        )
    )

    print("Opening GitHub OAuth page in your browser …")
    print(f"  URL: {auth_url}\n")
    webbrowser.open(auth_url)

    # Wait for the callback
    server = HTTPServer(("127.0.0.1", callback_port), _CallbackHandler)
    print(f"Listening for GitHub callback on port {callback_port} …")
    server.handle_request()

    if not _code:
        sys.exit("❌  Did not receive an authorization code from GitHub.")

    # Exchange code for access token
    resp = httpx.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": _code,
            "redirect_uri": REDIRECT_URI,
        },
        headers={"Accept": "application/json"},
        timeout=10.0,
    )
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        sys.exit(f"❌  GitHub token exchange failed: {data['error']} — {data.get('error_description')}")

    token = data["access_token"]
    print("\n" + "=" * 60)
    print("✅  GitHub access token:")
    print(f"\n    {token}\n")
    print("Use it in your MCP requests:")
    print(f'    Authorization: Bearer {token}')
    print("\nQuick curl test:")
    print(f'    curl -H "Authorization: Bearer {token}" http://127.0.0.1:8000/health')
    print("=" * 60)


if __name__ == "__main__":
    main()
