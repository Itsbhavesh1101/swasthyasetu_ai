"""Offline synthetic benchmark mechanics without provider selection."""

import traceback

import pytest
from ocr_support.benchmark import (
    BenchmarkContractError,
    SyntheticBenchmarkFixture,
    evaluate_fixture,
)
from ocr_support.fixtures import result

from app.modules.documents.contracts import ResultStatus


def fixture() -> SyntheticBenchmarkFixture:
    return SyntheticBenchmarkFixture(
        fixture_id="synthetic.case.alpha",
        fixture_version="v1",
        origin="SYNTHETIC_ENGINEERING_ONLY",
        configuration_version="config.v1",
        expected_pages=(1, 2),
        expected_tokens=((1, ("SYNTHETIC_TOKEN_1",)), (2, ("SYNTHETIC_TOKEN_2",))),
    )


def test_benchmark_has_explicit_denominators_and_exact_retention() -> None:
    report = evaluate_fixture(fixture(), result())
    assert (report.covered_pages, report.expected_page_count) == (2, 2)
    assert (report.retained_tokens, report.expected_token_count) == (2, 2)
    assert report.failed_pages == 0
    assert report.reproducibility_token


def test_benchmark_reports_partial_and_failed_pages_without_pass_threshold() -> None:
    report = evaluate_fixture(fixture(), result(status=ResultStatus.PARTIAL))
    assert report.failed_pages == 1
    assert report.covered_pages == 1
    assert not hasattr(report, "passed")


def test_fixture_order_is_canonical_and_versions_are_strict() -> None:
    with pytest.raises(BenchmarkContractError):
        SyntheticBenchmarkFixture("synthetic.case.alpha", "v1", "EXTERNAL", "config.v1", (2, 1), ())
    with pytest.raises(BenchmarkContractError):
        SyntheticBenchmarkFixture(
            "synthetic.case.alpha", "unknown", "SYNTHETIC_ENGINEERING_ONLY", "config.v1", (1,), ()
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"fixture_id": False},
        {"configuration_version": ["private-canary"]},
        {"expected_pages": [1]},
        {"expected_pages": (False,)},
        {"expected_pages": (1, 1)},
        {"expected_pages": tuple(range(1, 34))},
        {"expected_pages": (33,), "expected_tokens": ((33, ()),)},
        {"expected_tokens": ([1, ()],)},
        {"expected_tokens": ((1,),)},
        {"expected_tokens": ((1, ["SYNTHETIC_TOKEN_1"]),)},
        {"expected_tokens": ((1, (False,)),)},
        {"expected_tokens": ((1, ("SYNTHETIC_TOKEN_1", "SYNTHETIC_TOKEN_1")),)},
        {"expected_tokens": ((1, tuple(f"SYNTHETIC_TOKEN_{i}" for i in range(129))),)},
        {"expected_tokens": ((1, ("SYNTHETIC_" + "A" * 129,)),)},
        {"expected_tokens": ((2, ("SYNTHETIC_TOKEN_1",)),)},
    ],
)
def test_fixture_rejects_hostile_unbounded_and_ambiguous_values_content_free(
    changes: dict[str, object],
) -> None:
    values: dict[str, object] = {
        "fixture_id": "synthetic.case.alpha",
        "fixture_version": "v1",
        "origin": "SYNTHETIC_ENGINEERING_ONLY",
        "configuration_version": "config.v1",
        "expected_pages": (1,),
        "expected_tokens": ((1, ("SYNTHETIC_TOKEN_1",)),),
    }
    values.update(changes)
    with pytest.raises(BenchmarkContractError) as raised:
        SyntheticBenchmarkFixture(**values)  # type: ignore[arg-type]
    assert str(raised.value) == "INVALID_FIXTURE"
    assert "private-canary" not in "".join(traceback.format_exception(raised.value))
