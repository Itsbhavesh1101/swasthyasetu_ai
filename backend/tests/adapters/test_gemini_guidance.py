"""Official-SDK boundary tests for grounded Gemini guidance."""

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from pydantic import SecretStr

from app.adapters.ai.fake_guidance import FakeGuidanceProvider
from app.adapters.ai.gemini_guidance import GeminiGuidanceProvider
from app.modules.self_care.guidance_contracts import (
    GuidanceCitation,
    GuidanceProviderError,
    GuidanceProviderRequest,
    GuidanceProviderResult,
    SourceAnnotation,
)

NOW = datetime(2026, 11, 3, 12, tzinfo=UTC)


def response(*, text: str = "Gentle hydration habits may support general wellbeing.") -> object:
    web = SimpleNamespace(uri="https://who.int/advice", title="WHO")
    metadata = SimpleNamespace(
        grounding_chunks=[SimpleNamespace(web=web)],
        grounding_supports=[
            SimpleNamespace(
                segment=SimpleNamespace(start_index=0, end_index=6),
                grounding_chunk_indices=[0],
            )
        ],
    )
    return SimpleNamespace(text=text, candidates=[SimpleNamespace(grounding_metadata=metadata)])


class Models:
    def __init__(self, outcome: object) -> None:
        self.outcome = outcome
        self.calls: list[dict[str, object]] = []

    async def generate_content(self, **values: object) -> object:
        self.calls.append(values)
        if isinstance(self.outcome, Exception):
            raise self.outcome
        if isinstance(self.outcome, asyncio.Event):
            await self.outcome.wait()
        return self.outcome


class Client:
    def __init__(self, outcome: object) -> None:
        self.aio = SimpleNamespace(models=Models(outcome), aclose=self.aclose)
        self.closed = False

    async def aclose(self) -> None:
        self.closed = True


async def test_gemini_uses_one_grounded_request_and_parses_stable_citations() -> None:
    client = Client(response())
    factory_calls: list[dict[str, object]] = []

    def factory(**values: object) -> Client:
        factory_calls.append(values)
        return client

    provider = GeminiGuidanceProvider(
        api_key=SecretStr("do-not-expose"),
        model="gemini-test",
        deadline_seconds=2,
        client_factory=factory,
        clock=lambda: NOW,
    )
    result = await provider.generate(GuidanceProviderRequest(question="How can I stay hydrated?"))

    assert len(client.aio.models.calls) == 1
    call = client.aio.models.calls[0]
    assert call["model"] == "gemini-test"
    assert call["contents"] == "How can I stay hydrated?"
    config = call["config"]
    assert config.tools[0].google_search is not None
    assert "diagnos" in str(config.system_instruction).casefold()
    assert result.citations == (GuidanceCitation(title="WHO", url="https://who.int/advice"),)
    assert result.annotations == (SourceAnnotation(start=0, end=6, citation_index=0),)
    assert factory_calls == [{"api_key": "do-not-expose"}]
    assert client.closed
    assert "do-not-expose" not in repr(provider)
    assert "How can I stay hydrated?" not in repr(provider)


async def test_gemini_timeout_is_content_free_closes_client_and_never_retries() -> None:
    pending = asyncio.Event()
    client = Client(pending)
    provider = GeminiGuidanceProvider(
        api_key=SecretStr("secret"),
        model="gemini-test",
        deadline_seconds=0.01,
        client_factory=lambda **_: client,
        clock=lambda: NOW,
    )
    with pytest.raises(GuidanceProviderError) as captured:
        await provider.generate(GuidanceProviderRequest(question="A private health question"))
    assert str(captured.value) == "UNAVAILABLE"
    assert captured.value.__cause__ is None
    assert "private" not in repr(captured.value).casefold()
    assert len(client.aio.models.calls) == 1
    assert client.closed


async def test_gemini_propagates_cancellation_and_rejects_malformed_grounding() -> None:
    pending = asyncio.Event()
    client = Client(pending)
    provider = GeminiGuidanceProvider(
        api_key=SecretStr("secret"),
        model="gemini-test",
        deadline_seconds=30,
        client_factory=lambda **_: client,
        clock=lambda: NOW,
    )
    task = asyncio.create_task(
        provider.generate(GuidanceProviderRequest(question="A bounded wellness question"))
    )
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert client.closed

    malformed = Client(SimpleNamespace(text="raw unsafe text", candidates=[]))
    provider = GeminiGuidanceProvider(
        api_key=SecretStr("secret"),
        model="gemini-test",
        deadline_seconds=2,
        client_factory=lambda **_: malformed,
        clock=lambda: NOW,
    )
    with pytest.raises(GuidanceProviderError) as captured:
        await provider.generate(GuidanceProviderRequest(question="A bounded wellness question"))
    assert str(captured.value) == "INVALID_RESPONSE"
    assert len(malformed.aio.models.calls) == 1


async def test_fake_provider_is_deterministic_and_network_free() -> None:
    expected = GuidanceProviderResult(
        answer="Gentle hydration habits may support general wellbeing.",
        citations=(GuidanceCitation(title="WHO", url="https://who.int/advice"),),
        annotations=(SourceAnnotation(start=0, end=6, citation_index=0),),
        retrieved_at=NOW,
    )
    fake = FakeGuidanceProvider((expected,))
    request = GuidanceProviderRequest(question="How can I stay hydrated?")
    assert await fake.generate(request) == expected
    assert fake.requests == (request,)
    with pytest.raises(GuidanceProviderError):
        await fake.generate(request)
