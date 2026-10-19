"""Deterministic in-memory benchmark mechanics with no provider ranking."""

import re
from dataclasses import dataclass
from hashlib import sha256

from app.modules.documents.contracts import DocumentProcessingResult, PageStatus

_TOKEN = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")


class BenchmarkContractError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class SyntheticBenchmarkFixture:
    fixture_id: str
    fixture_version: str
    origin: str
    configuration_version: str
    expected_pages: tuple[int, ...]
    expected_tokens: tuple[tuple[int, tuple[str, ...]], ...]

    def __post_init__(self) -> None:
        if (
            _TOKEN.fullmatch(self.fixture_id) is None
            or self.fixture_version != "v1"
            or self.origin != "SYNTHETIC_ENGINEERING_ONLY"
            or _TOKEN.fullmatch(self.configuration_version) is None
        ):
            raise BenchmarkContractError("INVALID_FIXTURE")
        if (
            not self.expected_pages
            or self.expected_pages != tuple(sorted(set(self.expected_pages)))
            or any(page < 1 for page in self.expected_pages)
        ):
            raise BenchmarkContractError("INVALID_FIXTURE")
        if tuple(page for page, _ in self.expected_tokens) != self.expected_pages:
            raise BenchmarkContractError("INVALID_FIXTURE")
        if any(
            tokens != tuple(sorted(set(tokens)))
            or any(not token.startswith("SYNTHETIC_") for token in tokens)
            for _, tokens in self.expected_tokens
        ):
            raise BenchmarkContractError("INVALID_FIXTURE")


@dataclass(frozen=True, slots=True)
class BenchmarkReport:
    expected_page_count: int
    covered_pages: int
    failed_pages: int
    expected_token_count: int
    retained_tokens: int
    unexpected_tokens: int
    reproducibility_token: str


def evaluate_fixture(
    fixture: SyntheticBenchmarkFixture, result: DocumentProcessingResult
) -> BenchmarkReport:
    if result.requested_pages.pages != fixture.expected_pages:
        raise BenchmarkContractError("IDENTITY_MISMATCH")
    expected = {(page, token) for page, tokens in fixture.expected_tokens for token in tokens}
    actual = {(page.page_number, block.text) for page in result.pages for block in page.blocks}
    covered = sum(page.status is PageStatus.SUCCEEDED for page in result.pages)
    canonical = "|".join(f"{page}:{token}" for page, token in sorted(actual))
    return BenchmarkReport(
        expected_page_count=len(fixture.expected_pages),
        covered_pages=covered,
        failed_pages=len(result.pages) - covered,
        expected_token_count=len(expected),
        retained_tokens=len(expected & actual),
        unexpected_tokens=len(actual - expected),
        reproducibility_token=sha256(canonical.encode()).hexdigest(),
    )
