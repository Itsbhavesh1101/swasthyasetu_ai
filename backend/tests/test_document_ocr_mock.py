"""Deterministic zero-I/O MockOCRAdapter tests."""

from dataclasses import replace

import pytest
from ocr_support.fixtures import request, result
from ocr_support.mock_ocr import MockFailure, MockFailureCode, MockOCRAdapter

from app.modules.documents.contracts import ResultErrorCode, ResultStatus


@pytest.mark.asyncio
async def test_mock_is_deterministic_and_matches_exact_request_identity() -> None:
    expected = result()
    adapter = MockOCRAdapter({request().request_id: expected})
    assert await adapter.extract(request()) == expected
    assert await adapter.extract(request()) is expected


@pytest.mark.asyncio
@pytest.mark.parametrize("code", list(MockFailureCode))
async def test_mock_failure_scenarios_are_typed_and_content_free(code: MockFailureCode) -> None:
    adapter = MockOCRAdapter({request().request_id: MockFailure(code)})
    with pytest.raises(MockFailure) as raised:
        await adapter.extract(request())
    assert raised.value.code is code
    assert "CANARY_PRIVATE_TEXT" not in repr(raised.value)


@pytest.mark.asyncio
async def test_mock_rejects_unknown_and_forged_results() -> None:
    with pytest.raises(MockFailure):
        await MockOCRAdapter({}).extract(request())
    forged = replace(result(), document_id=request(document_id_seed=99).document_id)
    with pytest.raises(MockFailure) as raised:
        await MockOCRAdapter({request().request_id: forged}).extract(request())
    assert raised.value.code is MockFailureCode.MALFORMED_RESULT


def test_mock_fixture_covers_partial_failed_and_fallback_results() -> None:
    assert result(status=ResultStatus.PARTIAL).error_code is ResultErrorCode.PAGE_FAILED
    assert result(status=ResultStatus.FAILED).status is ResultStatus.FAILED
    assert result(status=ResultStatus.NEEDS_FALLBACK).status is ResultStatus.NEEDS_FALLBACK
