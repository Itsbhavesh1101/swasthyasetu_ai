"""Test-only FastAPI composition for deterministic browser acceptance."""

from datetime import UTC, datetime

from app.config import Environment, Settings
from app.main import create_app
from app.modules.self_care.guidance_contracts import (
    GuidanceCitation,
    GuidanceProviderError,
    GuidanceProviderFailureCode,
    GuidanceProviderRequest,
    GuidanceProviderResult,
    SourceAnnotation,
)


class BrowserAcceptanceGuidanceProvider:
    """Network-free provider that never enters production application composition."""

    async def generate(self, request: GuidanceProviderRequest) -> GuidanceProviderResult:
        if "unavailable" in request.question.casefold():
            raise GuidanceProviderError(GuidanceProviderFailureCode.UNAVAILABLE)
        return GuidanceProviderResult(
            answer="Gentle hydration habits may support general wellbeing.",
            citations=(GuidanceCitation(title="World Health Organization", url="https://who.int"),),
            annotations=(SourceAnnotation(start=0, end=6, citation_index=0),),
            retrieved_at=datetime(2026, 11, 3, 12, tzinfo=UTC),
        )


settings = Settings()
if settings.environment not in {Environment.LOCAL, Environment.TEST}:
    raise RuntimeError("browser acceptance app is restricted to local and test environments")

app = create_app(
    settings,
    guidance_provider_factory=BrowserAcceptanceGuidanceProvider,
)
