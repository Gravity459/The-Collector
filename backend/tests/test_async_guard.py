"""Keep the backend async-first: no blocking clients or calls in app code."""
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app"

BANNED = {
    r"^\s*(import|from)\s+requests\b": "requests is sync; use httpx.AsyncClient",
    r"^\s*(import|from)\s+gspread\b": "gspread is sync; use integrations.google_sheets",
    r"^\s*(import|from)\s+googleapiclient\b": "google-api-python-client is sync",
    r"^\s*(import|from)\s+google\.auth\b": "google-auth refresh is sync; sign the JWT with python-jose",
    r"^\s*(import|from)\s+google\.oauth2\b": "google-auth refresh is sync",
    r"\btime\.sleep\(": "blocks the event loop; use await asyncio.sleep",
    r"\bOpenAI\(": "sync OpenAI client; use AsyncOpenAI",
    r"(?<!\.aio)\.models\.generate_content\(": "sync Gemini call; use client.aio.models",
    r"\bcreate_engine\(": "sync engine; use create_async_engine",
    r"\bpsycopg2\b": "sync driver; use asyncpg",
}


def test_no_blocking_io_in_app():
    problems = []
    for path in APP.rglob("*.py"):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for pattern, why in BANNED.items():
                if re.search(pattern, line):
                    problems.append(f"{path.relative_to(APP)}:{lineno}: {why}\n    {line.strip()}")
    assert not problems, "\n".join(problems)


def test_routes_are_async():
    from app.main import app

    sync_routes = [
        route.path
        for route in app.routes
        if hasattr(route, "endpoint")
        and not __import__("inspect").iscoroutinefunction(route.endpoint)
        and route.path not in ("/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc")
    ]
    assert not sync_routes, sync_routes
