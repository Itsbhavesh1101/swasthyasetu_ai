from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.modules.self_care.contracts import (
    SelfCareContractCode,
    SelfCareContractError,
    SyntheticGuidancePlaceholder,
    SyntheticKnowledgeItem,
    SyntheticKnowledgePackState,
    SyntheticKnowledgeReviewState,
    SyntheticKnowledgeTag,
    create_synthetic_knowledge_pack,
    validate_synthetic_knowledge_pack,
)
from app.modules.self_care.loader import parse_synthetic_knowledge_pack

NOW = datetime(2026, 10, 31, 19, 0, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64


def item(
    suffix: str = "alpha",
    *,
    placeholder: SyntheticGuidancePlaceholder = SyntheticGuidancePlaceholder.ALPHA,
    tags: tuple[SyntheticKnowledgeTag, ...] = (SyntheticKnowledgeTag.ALPHA,),
) -> SyntheticKnowledgeItem:
    return SyntheticKnowledgeItem(
        guidance_id=f"syn_selfcare_guidance_{suffix}",
        version="engineering.v1",
        placeholder_token=placeholder,
        source_id=f"syn_selfcare_source_{suffix}",
        source_version="engineering.v1",
        source_hash=HASH_A if suffix == "alpha" else HASH_B,
        tags=tags,
    )


def pack(*items: SyntheticKnowledgeItem):
    return create_synthetic_knowledge_pack(
        pack_id="syn_selfcare_pack_fixture",
        pack_version="engineering.v1",
        schema_version="synthetic-self-care-knowledge.v1",
        state=SyntheticKnowledgePackState.TEST_ONLY_UNAPPROVED,
        created_at=NOW,
        items=items or (item(),),
    )


def test_pack_is_hash_bound_immutable_and_cannot_represent_guidance() -> None:
    result = pack()

    assert result.content_hash == "26c632aa0039eb6ef600eb096dfe9fefdfa98dcc8ed8a5573a083323f3e834f5"
    assert result.state is SyntheticKnowledgePackState.TEST_ONLY_UNAPPROVED
    assert result.items[0].review_state is SyntheticKnowledgeReviewState.TEST_ONLY_UNAPPROVED
    assert not hasattr(result.items[0], "content")
    assert not hasattr(result.items[0], "title")
    assert not hasattr(result.items[0], "supportive_actions")
    assert not hasattr(result.items[0], "contraindications")
    with pytest.raises(FrozenInstanceError):
        result.pack_version = "engineering.v2"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("guidance_id", "guidance-real"),
        ("version", "v1"),
        ("placeholder_token", "SYNTHETIC_PLACEHOLDER_ALPHA"),
        ("source_id", "https://private-canary.invalid"),
        ("source_version", "latest"),
        ("source_hash", "not-a-hash"),
        ("tags", ("SYNTHETIC_TAG_ALPHA",)),
        ("review_state", "APPROVED"),
    ],
)
def test_item_direct_constructor_rejects_open_or_nonengineering_values(
    field: str, value: object
) -> None:
    values = {
        "guidance_id": "syn_selfcare_guidance_alpha",
        "version": "engineering.v1",
        "placeholder_token": SyntheticGuidancePlaceholder.ALPHA,
        "source_id": "syn_selfcare_source_alpha",
        "source_version": "engineering.v1",
        "source_hash": HASH_A,
        "tags": (SyntheticKnowledgeTag.ALPHA,),
        "review_state": SyntheticKnowledgeReviewState.TEST_ONLY_UNAPPROVED,
    }
    values[field] = value

    with pytest.raises(SelfCareContractError) as caught:
        SyntheticKnowledgeItem(**values)  # type: ignore[arg-type]

    assert caught.value.code in {
        SelfCareContractCode.INVALID_TYPE,
        SelfCareContractCode.INVALID_VALUE,
    }
    assert "private-canary" not in str(caught.value)


def test_pack_rejects_duplicate_unsorted_and_oversized_nested_values() -> None:
    alpha = item()
    beta = item("beta", placeholder=SyntheticGuidancePlaceholder.BETA)

    with pytest.raises(SelfCareContractError) as duplicate:
        pack(alpha, alpha)
    assert duplicate.value.code is SelfCareContractCode.DUPLICATE_ITEM

    with pytest.raises(SelfCareContractError) as unsorted:
        pack(beta, alpha)
    assert unsorted.value.code is SelfCareContractCode.INVALID_VALUE

    with pytest.raises(SelfCareContractError) as tags:
        item(
            tags=(
                SyntheticKnowledgeTag.ALPHA,
                SyntheticKnowledgeTag.BETA,
                SyntheticKnowledgeTag.DELTA,
                SyntheticKnowledgeTag.GAMMA,
                SyntheticKnowledgeTag.ALPHA,
            )
        )
    assert tags.value.code is SelfCareContractCode.LIMIT_EXCEEDED


def test_aware_non_utc_pack_time_normalizes_and_naive_time_fails() -> None:
    aware = create_synthetic_knowledge_pack(
        pack_id="syn_selfcare_pack_fixture",
        pack_version="engineering.v1",
        schema_version="synthetic-self-care-knowledge.v1",
        state=SyntheticKnowledgePackState.TEST_ONLY_UNAPPROVED,
        created_at=NOW.astimezone(timezone(timedelta(hours=5, minutes=30))),
        items=(item(),),
    )
    assert aware.created_at == NOW
    assert aware.created_at.tzinfo is UTC

    with pytest.raises(SelfCareContractError) as naive:
        create_synthetic_knowledge_pack(
            pack_id="syn_selfcare_pack_fixture",
            pack_version="engineering.v1",
            schema_version="synthetic-self-care-knowledge.v1",
            state=SyntheticKnowledgePackState.TEST_ONLY_UNAPPROVED,
            created_at=NOW.replace(tzinfo=None),
            items=(item(),),
        )
    assert naive.value.code is SelfCareContractCode.INVALID_TYPE


def test_validation_rejects_forced_nested_mutation_and_forged_hash() -> None:
    original = pack()
    object.__setattr__(original.items[0], "source_hash", HASH_B)

    with pytest.raises(SelfCareContractError) as mutation:
        validate_synthetic_knowledge_pack(original)
    assert mutation.value.code is SelfCareContractCode.HASH_MISMATCH

    clean = pack()
    with pytest.raises(SelfCareContractError) as forged:
        replace(clean, content_hash="0" * 64)
    assert forged.value.code is SelfCareContractCode.HASH_MISMATCH


def test_no_approved_or_patient_facing_state_exists() -> None:
    with pytest.raises(ValueError):
        SyntheticKnowledgeReviewState("APPROVED")
    with pytest.raises(ValueError):
        SyntheticKnowledgePackState("APPROVED")


def payload(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "contract_version": "synthetic-self-care-knowledge.v1",
        "pack_id": "syn_selfcare_pack_fixture",
        "pack_version": "engineering.v1",
        "schema_version": "synthetic-self-care-knowledge.v1",
        "content_hash": "26c632aa0039eb6ef600eb096dfe9fefdfa98dcc8ed8a5573a083323f3e834f5",
        "state": "TEST_ONLY_UNAPPROVED",
        "created_at": "2026-10-31T19:00:00Z",
        "items": [
            {
                "guidance_id": "syn_selfcare_guidance_alpha",
                "version": "engineering.v1",
                "placeholder_token": "SYNTHETIC_PLACEHOLDER_ALPHA",
                "source_id": "syn_selfcare_source_alpha",
                "source_version": "engineering.v1",
                "source_hash": HASH_A,
                "tags": ["SYNTHETIC_TAG_ALPHA"],
                "review_state": "TEST_ONLY_UNAPPROVED",
            }
        ],
    }
    value.update(overrides)
    return value


def test_parser_loads_only_exact_unapproved_synthetic_pack() -> None:
    result = parse_synthetic_knowledge_pack(payload(), observed_at=NOW)

    assert result == pack()
    assert result.items[0].placeholder_token is SyntheticGuidancePlaceholder.ALPHA


@pytest.mark.parametrize(
    "field",
    [
        "content",
        "remedy",
        "source_url",
        "approved",
        "contraindications",
        "translations",
        "patient_id",
    ],
)
def test_parser_rejects_prose_clinical_authority_and_identity_fields(field: str) -> None:
    value = payload(**{field: "private-canary"})

    with pytest.raises(SelfCareContractError) as caught:
        parse_synthetic_knowledge_pack(value, observed_at=NOW)

    assert caught.value.code is SelfCareContractCode.UNKNOWN_FIELD
    assert "private-canary" not in str(caught.value)


@pytest.mark.parametrize(
    ("overrides", "code"),
    [
        ({"state": "APPROVED"}, SelfCareContractCode.INVALID_VALUE),
        ({"content_hash": "0" * 64}, SelfCareContractCode.HASH_MISMATCH),
        ({"created_at": "2026-10-31T19:00:01Z"}, SelfCareContractCode.INVALID_VALUE),
        ({"created_at": "2026-11-01T00:30:00+05:30"}, SelfCareContractCode.INVALID_VALUE),
        ({"created_at": "2026-10-31T19:00:00.0000Z"}, SelfCareContractCode.INVALID_VALUE),
    ],
)
def test_parser_rejects_forged_state_hash_or_noncanonical_time(
    overrides: dict[str, object], code: SelfCareContractCode
) -> None:
    with pytest.raises(SelfCareContractError) as caught:
        parse_synthetic_knowledge_pack(payload(**overrides), observed_at=NOW)

    assert caught.value.code is code


def test_parser_rejects_missing_nested_and_hostile_mappings_content_free() -> None:
    missing = payload()
    del missing["items"]
    with pytest.raises(SelfCareContractError) as absent:
        parse_synthetic_knowledge_pack(missing, observed_at=NOW)
    assert absent.value.code is SelfCareContractCode.MISSING_FIELD

    nested = payload()
    nested["items"] = [{"guidance_id": "syn_selfcare_guidance_alpha"}]
    with pytest.raises(SelfCareContractError) as incomplete:
        parse_synthetic_knowledge_pack(nested, observed_at=NOW)
    assert incomplete.value.code is SelfCareContractCode.MISSING_FIELD

    class Hostile(dict[object, object]):
        def keys(self):
            raise AssertionError("private-canary")

    with pytest.raises(SelfCareContractError) as hostile:
        parse_synthetic_knowledge_pack(Hostile(), observed_at=NOW)
    assert hostile.value.code is SelfCareContractCode.INVALID_TYPE
    assert "private-canary" not in str(hostile.value)
