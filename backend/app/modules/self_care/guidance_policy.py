"""Deterministic display guards for external wellness guidance."""

import re
from urllib.parse import urlsplit

from app.modules.self_care.guidance_contracts import GuidanceProviderResult, GuidanceQuestion

_UNSUPPORTED_QUERY = re.compile(
    r"\b(diagnos(?:e|is)|dosage|dose|emergency|chest pain|pregnan(?:t|cy)|infant|baby|"
    r"suicid(?:e|al)|self[- ]harm|prescri(?:be|ption)|drug interaction)\b",
    re.IGNORECASE,
)
_FORBIDDEN_OUTPUT = re.compile(
    r"\b(guaranteed cure|cures?\b|stop (?:your )?(?:prescribed )?medication|"
    r"replaces? emergency care|diagnos(?:e|is)|prescri(?:be|ption)|\d+\s*(?:mg|ml)\b)",
    re.IGNORECASE,
)


class GuidancePolicyError(ValueError):
    """Content-free post-validation failure."""

    def __init__(self) -> None:
        super().__init__("GUIDANCE_POLICY_REJECTED")


class GuidancePolicy:
    def __init__(self, allowed_source_domains: tuple[str, ...]) -> None:
        if (
            type(allowed_source_domains) is not tuple
            or not allowed_source_domains
            or len(allowed_source_domains) != len(set(allowed_source_domains))
        ):
            raise ValueError("allowed guidance domains must be unique")
        self._allowed = frozenset(allowed_source_domains)

    def supports(self, question: GuidanceQuestion) -> bool:
        return _UNSUPPORTED_QUERY.search(question.text) is None

    def validate_result(self, result: GuidanceProviderResult) -> GuidanceProviderResult:
        if _FORBIDDEN_OUTPUT.search(result.answer):
            raise GuidancePolicyError
        if any(
            urlsplit(citation.url).hostname not in self._allowed for citation in result.citations
        ):
            raise GuidancePolicyError
        cited = {annotation.citation_index for annotation in result.annotations}
        if cited != set(range(len(result.citations))):
            raise GuidancePolicyError
        return result


__all__ = ["GuidancePolicy", "GuidancePolicyError"]
