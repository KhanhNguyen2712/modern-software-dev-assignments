# Week 3 MCP Weather Server

This week implements a Python MCP server that wraps the Open-Meteo APIs. It exposes weather data as MCP tools, resources, and a prompt, supports a local STDIO transport for Claude Desktop/Cursor, and includes a Railway-friendly remote HTTP transport protected with GitHub OAuth bearer tokens.

## Upstream API Endpoints

- Geocoding: `https://geocoding-api.open-meteo.com/v1/search`
- Forecast/current weather: `https://api.open-meteo.com/v1/forecast`

## Features

- `get_current_weather` tool for current conditions.
- `get_forecast` tool for multi-day forecasts.
- `weather://current/{location}` resource template.
- `weather://forecast/{location}/{days}` resource template.
- `weather_trip_brief` prompt for travel/outdoor planning.
- Graceful errors for invalid locations, empty results, timeouts, rate limits, and upstream failures.
- STDIO-safe logging to `stderr`.
- Remote HTTP auth backed by GitHub OAuth token verification.
- Railway deployment config via `railway.json`.

## Project Structure

- `week3/server/core/`: config, typed models, Open-Meteo client, service logic, error mapping.
- `week3/server/mcp/`: MCP capability registration.
- `week3/server/transports/stdio_main.py`: local STDIO entrypoint.
- `week3/server/transports/http_app.py`: remote HTTP app for `uvicorn`.
- `week3/server/transports/auth.py`: bearer-token validation and metadata helpers.
- `week3/server/transports/github_oauth.py`: GitHub OAuth login, code exchange, and token verification.
- `week3/tests/`: service, MCP registration, and auth tests.

## Prerequisites

1. Activate the Python environment you use for this repo.
2. Install dependencies from the repo root:

```bash
poetry install
```

3. For local development, copy `week3/.env.example` to `week3/.env` and fill in the GitHub OAuth values you actually use.

The app now auto-loads environment variables from:

- repo root `.env`
- `week3/.env`

If the same key exists in both places, `week3/.env` wins.

## Environment Variables

For local development, the easiest path is:

```bash
cp week3/.env.example week3/.env
```

Then edit `week3/.env`.

### Core weather settings

- `WEATHER_BASE_URL`
  Default: `https://api.open-meteo.com/v1`
- `WEATHER_GEOCODING_BASE_URL`
  Default: `https://geocoding-api.open-meteo.com/v1`
- `WEATHER_TIMEOUT_SECONDS`
  Default: `10`
- `WEATHER_USER_AGENT`
  Default: `week3-mcp-weather-server/1.0`
- `WEATHER_RETRY_ATTEMPTS`
  Default: `2`
- `WEATHER_BACKOFF_SECONDS`
  Default: `0.2`
- `MCP_LOG_LEVEL`
  Default: `INFO`

### HTTP auth settings

- `MCP_AUTH_REQUIRED`
  Set to `true` to protect the HTTP transport.
- `MCP_AUTH_PROVIDER`
  Use `github` for Railway deployment with GitHub bearer-token verification. Default: `custom_jwt`
- `MCP_AUTH_ISSUER`
  Authorization server issuer URL.
- `MCP_AUTH_AUDIENCE`
  Expected audience for incoming bearer tokens.
- `MCP_AUTH_JWKS_URL`
  JWKS endpoint for public-key JWT verification.
- `MCP_AUTH_JWT_SECRET`
  Optional shared secret for local HS256 testing.
- `MCP_AUTH_DEV_TOKEN`
  Optional exact bearer token for quick local smoke tests.
- `MCP_AUTH_DEV_CLIENT_ID`
  Default: `local-weather-client`
- `MCP_AUTH_REQUIRED_SCOPES`
  Default: `read:user` when `MCP_AUTH_PROVIDER=github`, otherwise `weather.read`
- `MCP_AUTH_RESOURCE_SERVER_URL`
  Public base URL for the remote server. Default: `http://127.0.0.1:8000`

### GitHub OAuth settings

- `GITHUB_OAUTH_ENABLED`
  Set to `true` to enable `/auth/github/*` routes.
- `GITHUB_CLIENT_ID`
  GitHub OAuth App client ID.
- `GITHUB_CLIENT_SECRET`
  GitHub OAuth App client secret.
- `GITHUB_REDIRECT_URI`
  Must match the callback URL configured in the GitHub OAuth App.
- `GITHUB_OAUTH_SCOPES`
  Default: `read:user`
- `GITHUB_OAUTH_AUTHORIZE_URL`
  Default: `https://github.com/login/oauth/authorize`
- `GITHUB_OAUTH_ACCESS_TOKEN_URL`
  Default: `https://github.com/login/oauth/access_token`
- `GITHUB_API_BASE_URL`
  Default: `https://api.github.com`

## Run The Local STDIO Server

From the repo root:

```bash
poetry run python -m week3.server.transports.stdio_main
```

This is the transport to use for the rubric baseline and Claude Desktop/Cursor integration.

### Claude Desktop configuration example

Add an MCP server entry similar to this in your Claude Desktop config:

```json
{
  "mcpServers": {
    "week3-weather": {
      "command": "poetry",
      "args": [
        "run",
        "python",
        "-m",
        "week3.server.transports.stdio_main"
      ],
      "cwd": "/absolute/path/to/modern-software-dev-assignments"
    }
  }
}
```

After restarting Claude Desktop, you can type prompts such as:

- `Use get_current_weather for Ho Chi Minh City in metric units.`
- `Use get_forecast for Da Nang for 3 days.`
- `Read the weather://forecast/Da Nang/2 resource.`
- `Use the weather_trip_brief prompt for Hoi An for 2 days.`

## Run The Remote HTTP Server

From the repo root:

```bash
poetry run uvicorn week3.server.transports.http_app:app --host 0.0.0.0 --port 8000
```

The MCP endpoint is:

```text
http://127.0.0.1:8000/mcp
```

Protected-resource metadata is exposed at:

```text
http://127.0.0.1:8000/.well-known/oauth-protected-resource
http://127.0.0.1:8000/.well-known/oauth-protected-resource/mcp
```

### Local GitHub OAuth example

```powershell
$env:MCP_AUTH_REQUIRED="true"
$env:MCP_AUTH_PROVIDER="github"
$env:MCP_AUTH_RESOURCE_SERVER_URL="http://127.0.0.1:8000"
$env:GITHUB_OAUTH_ENABLED="true"
$env:GITHUB_CLIENT_ID="your-github-client-id"
$env:GITHUB_CLIENT_SECRET="your-github-client-secret"
$env:GITHUB_REDIRECT_URI="http://127.0.0.1:8000/auth/github/callback"
$env:MCP_AUTH_REQUIRED_SCOPES="read:user"
poetry run uvicorn week3.server.transports.http_app:app --host 0.0.0.0 --port 8000
```

Then:

1. Open `http://127.0.0.1:8000/auth/github/login`
2. Sign in with GitHub and approve the OAuth App
3. Copy the returned `access_token`
4. Call the helper route:

```bash
curl http://127.0.0.1:8000/auth/github/me \
  -H "Authorization: Bearer YOUR_GITHUB_ACCESS_TOKEN"
```

5. Use the same bearer token for MCP requests:

```text
Authorization: Bearer YOUR_GITHUB_ACCESS_TOKEN
```

If your client does not support remote MCP directly, use `mcp-remote` as a local proxy and point it at `http://127.0.0.1:8000/mcp`.

## Deploy To Railway

This repo includes [railway.json](d:/Admin/Documents/ML&Iot%20Lab/modern-software-dev-assignments/railway.json) so Railway can start the MCP server with:

```bash
uvicorn week3.server.transports.http_app:app --host 0.0.0.0 --port ${PORT}
```

### Railway setup

1. Push the repository to GitHub.
2. Create a new Railway project from the repo.
3. Add these environment variables in Railway:

```text
MCP_AUTH_REQUIRED=true
MCP_AUTH_PROVIDER=github
MCP_AUTH_RESOURCE_SERVER_URL=https://your-railway-domain.up.railway.app
MCP_AUTH_REQUIRED_SCOPES=read:user
GITHUB_OAUTH_ENABLED=true
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
GITHUB_REDIRECT_URI=https://your-railway-domain.up.railway.app/auth/github/callback
```

Railway injects these as real environment variables at runtime, so it does not need `week3/.env`.

4. In GitHub OAuth App settings, add the same callback URL.
5. Generate a Railway public domain.
6. Deploy. Your MCP endpoint will be:

```text
https://your-railway-domain.up.railway.app/mcp
```

### Railway OAuth flow

- Browser login starts at `/auth/github/login`
- GitHub redirects back to `/auth/github/callback`
- The callback exchanges the code for a GitHub access token
- The server verifies that token via GitHub OAuth application token check or the `/user` endpoint
- The same bearer token is then accepted for `/mcp`

## Tool Reference

### `get_current_weather`

- Parameters:
  - `location: str`
  - `units: "metric" | "imperial" = "metric"`
- Behavior:
  - Resolves the location through Open-Meteo geocoding.
  - Fetches current weather plus the same-day forecast slice.
  - Returns a summary plus structured location/current/forecast metadata.
- Example input:

```json
{
  "location": "Ho Chi Minh City",
  "units": "metric"
}
```

- Example output shape:

```json
{
  "summary": "Current weather for Ho Chi Minh City, Vietnam: 32.1°C, mainly clear, wind 11.2 km/h.",
  "location": {
    "name": "Ho Chi Minh City",
    "latitude": 10.8231,
    "longitude": 106.6297,
    "country": "Vietnam",
    "timezone": "Asia/Ho_Chi_Minh",
    "admin1": "Ho Chi Minh"
  },
  "current": {
    "time": "2026-03-19T14:00",
    "temperature": 32.1,
    "weather_description": "Mainly clear"
  }
}
```

### `get_forecast`

- Parameters:
  - `location: str`
  - `days: int = 3`
  - `units: "metric" | "imperial" = "metric"`
- Behavior:
  - Validates `days` in the range `1..7`.
  - Resolves the location, fetches a daily forecast, and returns a summary plus structured days.
- Example input:

```json
{
  "location": "Da Nang",
  "days": 3,
  "units": "metric"
}
```

- Example output shape:

```json
{
  "summary": "3-day forecast for Da Nang, Vietnam: light rain today, high 31.2°C, low 24.6°C, precipitation 6.3mm.",
  "forecast": [
    {
      "date": "2026-03-19",
      "temperature_max": 31.2,
      "temperature_min": 24.6,
      "precipitation_sum": 6.3,
      "weather_description": "Light rain"
    }
  ]
}
```

## Resource Reference

- `weather://current/{location}`
  Returns a text rendering of current weather for the resolved location.
- `weather://forecast/{location}/{days}`
  Returns a text rendering of the forecast with day-by-day details.

Location values are normalized before geocoding, so multi-word cities can be supplied as plain text or path-safe variants such as `Ho Chi Minh City`, `Ho-Chi-Minh-City`, `Ho_Chi_Minh_City`, `Ho+Chi+Minh+City`, or `Ho%20Chi%20Minh%20City`. The server does not expand city aliases automatically.

## Prompt Reference

- `weather_trip_brief(location, days=3, units="metric")`
  Produces a planning prompt instructing the model to call `get_forecast` and summarize clothing advice, rain risk, and timing concerns.

## Reliability Notes

- Blank locations are rejected before any upstream call.
- `days` must be between 1 and 7.
- Timeouts are surfaced as clear weather-provider timeout errors.
- HTTP 429 maps to a rate-limit error.
- Empty geocoding results map to a location-not-found error.
- Other upstream failures map to a general provider-unavailable error.
- Remote GitHub bearer tokens are verified against GitHub before the request reaches `/mcp`.

## Run Tests

From the repo root:

```bash
poetry run pytest week3/tests
```

## Manual Acceptance Checklist

- Start the STDIO server and verify Claude Desktop/Cursor lists the weather tools.
- Call `get_current_weather` and `get_forecast` with a valid city.
- Read both resource templates from an MCP client.
- Fetch the `weather_trip_brief` prompt from an MCP client.
- Start the HTTP server and confirm `/health` returns `{"status":"ok"}`.
- Confirm `/auth/github/login` redirects to GitHub.
- Confirm `/auth/github/callback` returns an access token after OAuth approval.
- Confirm `/auth/github/me` accepts a valid GitHub bearer token.
- Confirm protected-resource metadata is available when HTTP auth is enabled.
- Verify HTTP `/mcp` rejects missing or invalid bearer tokens when auth is enabled.
