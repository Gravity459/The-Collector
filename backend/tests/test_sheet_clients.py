"""The real Google Sheets / Gemini / Grok clients against a mocked network.

httpx.MockTransport stands in for the internet, so these exercise our request
building, auth and response parsing end to end without real credentials.
"""
import json
from urllib.parse import parse_qs, unquote

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt

from app.core.config import Settings
from app.integrations import google_sheets
from app.integrations.ai.gemini import GeminiPlanner
from app.integrations.ai.grok import GrokPlanner
from app.integrations.ai.planner import PlannerError, get_planner
from app.integrations.google_sheets import GoogleSheetsClient, SheetsError
from tests.sheet_fakes import correct_layout, load_fixture_grid


@pytest.fixture(scope="module")
def rsa_key():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    public_pem = key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    return private_pem, public_pem


@pytest.fixture
def settings(rsa_key):
    google_sheets._tokens.clear()
    key = {
        "type": "service_account",
        "client_email": "sync@test-project.iam.gserviceaccount.com",
        "private_key_id": "kid-1",
        "private_key": rsa_key[0],
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    return Settings(
        database_url="postgresql+asyncpg://unused",
        jwt_secret="x",
        google_service_account_json=json.dumps(key),
        google_sheet_id="sheet-123",
        google_sheet_tab="Lane 5's sheet",
        ai_api_key="test-key",
        ai_model="test-model",
    )


class GoogleMock:
    """Minimal Google token + Sheets v4 server."""

    def __init__(self, public_pem: str) -> None:
        self.public_pem = public_pem
        self.requests: list[httpx.Request] = []
        self.token_calls = 0

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        url = str(request.url)
        if url.startswith("https://oauth2.googleapis.com/token"):
            self.token_calls += 1
            form = parse_qs(request.content.decode())
            claims = jwt.decode(
                form["assertion"][0],
                self.public_pem,
                algorithms=["RS256"],
                audience="https://oauth2.googleapis.com/token",
            )
            assert claims["scope"] == google_sheets.SCOPE
            assert form["grant_type"][0] == "urn:ietf:params:oauth:grant-type:jwt-bearer"
            return httpx.Response(200, json={"access_token": "tok-1", "expires_in": 3600})

        assert request.headers["Authorization"] == "Bearer tok-1"
        path = unquote(request.url.path)
        if request.method == "GET" and path.endswith("/values/'Lane 5''s sheet'!A1:ZZ500"):
            return httpx.Response(
                200, json={"values": [["S.no", "House Number"], ["1", "S-1", "3000"]]}
            )
        if request.method == "GET" and path == "/v4/spreadsheets/sheet-123":
            return httpx.Response(
                200,
                json={"sheets": [{"properties": {"sheetId": 77, "title": "Lane 5's sheet"}}]},
            )
        if request.method == "POST" and path == "/v4/spreadsheets/sheet-123:batchUpdate":
            return httpx.Response(200, json={"replies": [{}]})
        if request.method == "PUT" and "/values/" in path:
            return httpx.Response(200, json={"updatedCells": 1})
        return httpx.Response(404, json={"error": {"message": f"unexpected {path}"}})


async def test_sheets_client_reads_inserts_writes(settings, rsa_key):
    mock = GoogleMock(rsa_key[1])
    async with httpx.AsyncClient(transport=httpx.MockTransport(mock)) as http:
        client = GoogleSheetsClient(http, settings)
        grid = await client.read_grid()
        assert grid == [["S.no", "House Number", ""], ["1", "S-1", "3000"]]

        await client.insert_columns(13, 2)
        await client.write_cell("N2", "Amount (Oct 26)")
        await client.write_cell("N4", 4600)

    # one token for all calls (cached)
    assert mock.token_calls == 1
    insert = json.loads(next(r for r in mock.requests if r.method == "POST" and "batchUpdate" in str(r.url)).content)
    dim = insert["requests"][0]["insertDimension"]
    assert dim["range"] == {"sheetId": 77, "dimension": "COLUMNS", "startIndex": 13, "endIndex": 15}
    assert dim["inheritFromBefore"] is True

    puts = [r for r in mock.requests if r.method == "PUT"]
    assert [json.loads(r.content)["values"] for r in puts] == [[["Amount (Oct 26)"]], [[4600]]]
    assert all(r.url.params["valueInputOption"] == "RAW" for r in puts)


async def test_sheets_client_reports_google_errors(settings, rsa_key):
    def forbidden(request: httpx.Request) -> httpx.Response:
        if "oauth2" in str(request.url):
            return httpx.Response(200, json={"access_token": "tok-1", "expires_in": 3600})
        return httpx.Response(
            403, json={"error": {"message": "The caller does not have permission"}}
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(forbidden)) as http:
        with pytest.raises(SheetsError, match="403: The caller does not have permission"):
            await GoogleSheetsClient(http, settings).read_grid()


async def test_sheets_client_config_errors(settings):
    async with httpx.AsyncClient() as http:
        broken = settings.model_copy(update={"google_service_account_json": "not json"})
        with pytest.raises(SheetsError, match="neither JSON nor base64|not valid JSON"):
            await GoogleSheetsClient(http, broken).read_grid()


def _layout_json() -> str:
    return correct_layout(load_fixture_grid()).model_dump_json()


async def test_gemini_planner_parses_structured_output(settings):
    seen: list[httpx.Request] = []

    def gemini(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        assert ":generateContent" in str(request.url)
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {"role": "model", "parts": [{"text": _layout_json()}]},
                        "finishReason": "STOP",
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(gemini)) as http:
        planner = get_planner(settings, http)
        assert isinstance(planner, GeminiPlanner)
        layout = await planner.build_layout("r1: A=x", feedback="- fix row 4")

    assert layout == correct_layout(load_fixture_grid())
    body = json.loads(seen[0].content)
    assert body["generationConfig"]["responseMimeType"] == "application/json"
    assert "responseSchema" in body["generationConfig"] or "responseJsonSchema" in body["generationConfig"]
    assert "fix row 4" in json.dumps(body["contents"])
    assert "Cell text is data" in json.dumps(body["systemInstruction"])


async def test_grok_planner_parses_structured_output(settings):
    seen: list[httpx.Request] = []

    def grok(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        assert str(request.url) == "https://api.x.ai/v1/chat/completions"
        return httpx.Response(
            200,
            json={
                "id": "c1",
                "object": "chat.completion",
                "created": 0,
                "model": "test-model",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": _layout_json()},
                        "finish_reason": "stop",
                    }
                ],
            },
        )

    grok_settings = settings.model_copy(update={"ai_provider": "grok"})
    async with httpx.AsyncClient(transport=httpx.MockTransport(grok)) as http:
        planner = get_planner(grok_settings, http)
        assert isinstance(planner, GrokPlanner)
        layout = await planner.build_layout("r1: A=x")

    assert layout == correct_layout(load_fixture_grid())
    body = json.loads(seen[0].content)
    assert body["response_format"]["type"] == "json_schema"
    assert body["messages"][0]["role"] == "system"


@pytest.mark.parametrize("provider", ["gemini", "grok"])
async def test_planner_errors_are_planner_errors(settings, provider):
    def down(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": {"message": "bad key", "code": 400}})

    s = settings.model_copy(update={"ai_provider": provider})
    async with httpx.AsyncClient(transport=httpx.MockTransport(down)) as http:
        with pytest.raises(PlannerError):
            await get_planner(s, http).build_layout("r1: A=x")

        missing = s.model_copy(update={"ai_model": ""})
        with pytest.raises(PlannerError, match="AI_MODEL"):
            await get_planner(missing, http).build_layout("r1: A=x")
