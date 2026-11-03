"""Google GenAI adapter for one bounded Google Search-grounded request."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from contextlib import suppress
from datetime import datetime
from typing import Any

from google import genai
from google.genai import types
from pydantic import SecretStr

from app.modules.self_care.guidance_contracts import (
    GuidanceCitation,
    GuidanceProviderError,
    GuidanceProviderFailureCode,
    GuidanceProviderRequest,
    GuidanceProviderResult,
    SourceAnnotation,
)

_SYSTEM_INSTRUCTION = """Provide concise general-wellness educational information only.
Do not diagnose, prescribe, recommend dosage or medication changes, promise a cure, or replace
emergency or qualified care. Use Google Search grounding and make every claim attributable."""


class GeminiGuidanceProvider:
    def __init__(
        self,
        *,
        api_key: SecretStr,
        model: str,
        deadline_seconds: float,
        clock: Callable[[], datetime],
        client_factory: Callable[..., Any] = genai.Client,
    ) -> None:
        if not model.strip() or not 0 < deadline_seconds <= 60:
            raise ValueError("Gemini guidance configuration is invalid")
        self._api_key = api_key
        self._model = model
        self._deadline_seconds = deadline_seconds
        self._clock = clock
        self._client_factory = client_factory

    def __repr__(self) -> str:
        return f"{type(self).__name__}(configured=True)"

    async def generate(self, request: GuidanceProviderRequest) -> GuidanceProviderResult:
        client: Any | None = None
        try:
            client = self._client_factory(api_key=self._api_key.get_secret_value())
            response = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model=self._model,
                    contents=request.question,
                    config=types.GenerateContentConfig(
                        system_instruction=_SYSTEM_INSTRUCTION,
                        temperature=0,
                        max_output_tokens=1_000,
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                    ),
                ),
                timeout=self._deadline_seconds,
            )
            return self._parse(response)
        except asyncio.CancelledError:
            raise
        except TimeoutError:
            raise GuidanceProviderError(GuidanceProviderFailureCode.UNAVAILABLE) from None
        except GuidanceProviderError:
            raise
        except Exception:
            raise GuidanceProviderError(GuidanceProviderFailureCode.UNAVAILABLE) from None
        finally:
            if client is not None:
                with suppress(Exception):
                    await client.aio.aclose()

    def _parse(self, response: Any) -> GuidanceProviderResult:
        try:
            answer = response.text
            candidates = response.candidates
            if type(answer) is not str or not candidates:
                raise ValueError
            metadata = candidates[0].grounding_metadata
            chunks = metadata.grounding_chunks
            supports = metadata.grounding_supports
            if not chunks or not supports:
                raise ValueError

            source_by_old_index: dict[int, GuidanceCitation] = {}
            raw_annotations: list[tuple[int, int, int]] = []
            for support in supports:
                indices = support.grounding_chunk_indices
                if not indices or type(indices[0]) is not int:
                    raise ValueError
                old_index = indices[0]
                web = chunks[old_index].web
                source_by_old_index[old_index] = GuidanceCitation(title=web.title, url=web.uri)
                raw_annotations.append(
                    (support.segment.start_index, support.segment.end_index, old_index)
                )
            citations = tuple(sorted(source_by_old_index.values(), key=lambda item: item.url))
            new_index = {citation.url: index for index, citation in enumerate(citations)}
            annotations = tuple(
                sorted(
                    SourceAnnotation(
                        start=start,
                        end=end,
                        citation_index=new_index[source_by_old_index[old].url],
                    )
                    for start, end, old in raw_annotations
                )
            )
            return GuidanceProviderResult(
                answer=answer,
                citations=citations,
                annotations=annotations,
                retrieved_at=self._clock(),
            )
        except GuidanceProviderError:
            raise
        except Exception:
            raise GuidanceProviderError(GuidanceProviderFailureCode.INVALID_RESPONSE) from None


__all__ = ["GeminiGuidanceProvider"]
