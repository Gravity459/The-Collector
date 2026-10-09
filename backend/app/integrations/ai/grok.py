"""Grok adapter (xAI's OpenAI-compatible API via AsyncOpenAI, structured output)."""
from __future__ import annotations

import asyncio

import httpx
from openai import AsyncOpenAI

from app.integrations.ai.planner import SYSTEM_PROMPT, TIMEOUT_S, PlannerError, user_prompt
from app.integrations.ai.schemas import LayoutMap

XAI_BASE_URL = "https://api.x.ai/v1"


class GrokPlanner:
    def __init__(self, *, api_key: str, model: str, http: httpx.AsyncClient) -> None:
        self._api_key = api_key
        self._model = model
        self._http = http

    async def build_layout(self, grid_text: str, feedback: str | None = None) -> LayoutMap:
        if not self._api_key or not self._model:
            raise PlannerError("AI_API_KEY / AI_MODEL are not set")
        client = AsyncOpenAI(
            api_key=self._api_key,
            base_url=XAI_BASE_URL,
            http_client=self._http,
            max_retries=1,
        )
        try:
            async with asyncio.timeout(TIMEOUT_S):
                completion = await client.chat.completions.parse(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt(grid_text, feedback)},
                    ],
                    response_format=LayoutMap,
                    temperature=0,
                )
        except TimeoutError as exc:
            raise PlannerError(f"Grok did not answer within {TIMEOUT_S:.0f}s") from exc
        except Exception as exc:  # SDK/HTTP/parse errors of any kind: retryable
            raise PlannerError(f"Grok request failed: {exc}") from exc

        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise PlannerError("Grok returned no layout (refused or empty)")
        return parsed
