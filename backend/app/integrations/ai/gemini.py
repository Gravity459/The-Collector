"""Gemini adapter (google-genai, async API, structured JSON output)."""
from __future__ import annotations

import asyncio

import httpx
from google import genai
from google.genai import types
from pydantic import ValidationError

from app.integrations.ai.planner import SYSTEM_PROMPT, TIMEOUT_S, PlannerError, user_prompt
from app.integrations.ai.schemas import LayoutMap


class GeminiPlanner:
    def __init__(self, *, api_key: str, model: str, http: httpx.AsyncClient) -> None:
        self._api_key = api_key
        self._model = model
        self._http = http

    async def build_layout(self, grid_text: str, feedback: str | None = None) -> LayoutMap:
        if not self._api_key or not self._model:
            raise PlannerError("AI_API_KEY / AI_MODEL are not set")
        client = genai.Client(
            api_key=self._api_key,
            http_options=types.HttpOptions(httpx_async_client=self._http),
        )
        try:
            async with asyncio.timeout(TIMEOUT_S):
                response = await client.aio.models.generate_content(
                    model=self._model,
                    contents=user_prompt(grid_text, feedback),
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        response_schema=LayoutMap,
                        temperature=0,
                    ),
                )
        except TimeoutError as exc:
            raise PlannerError(f"Gemini did not answer within {TIMEOUT_S:.0f}s") from exc
        except Exception as exc:  # SDK/HTTP errors of any kind: retryable
            raise PlannerError(f"Gemini request failed: {exc}") from exc

        try:
            return LayoutMap.model_validate_json(response.text or "")
        except ValidationError as exc:
            raise PlannerError(f"Gemini returned an unusable layout: {exc}") from exc
