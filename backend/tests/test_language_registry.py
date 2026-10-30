from dataclasses import replace
from typing import Any, cast

import pytest

from app.modules.language.registry import (
    LanguageCapability,
    LanguageProviderDescriptor,
    LanguageProviderPin,
    LanguageProviderRegistry,
    ProviderAuthority,
    ProviderDisposition,
    RegistryCode,
    RegistryError,
    build_synthetic_language_registry,
)


def descriptor(
    *,
    provider_id: str = "synthetic.stt",
    provider_version: str = "v1",
    capabilities: tuple[LanguageCapability, ...] = (LanguageCapability.SPEECH_TO_TEXT,),
) -> LanguageProviderDescriptor:
    return LanguageProviderDescriptor(
        provider_id=provider_id,
        provider_version=provider_version,
        capabilities=capabilities,
        authority=ProviderAuthority.ENGINEERING_ONLY,
        disposition=ProviderDisposition.MOCK_ONLY,
    )


def test_synthetic_registry_has_exact_version_pins_for_all_five_capabilities() -> None:
    registry = build_synthetic_language_registry()

    assert tuple(item.provider_id for item in registry.descriptors) == (
        "synthetic.language-detection",
        "synthetic.speech-to-text",
        "synthetic.text-to-speech",
        "synthetic.translation",
        "synthetic.transliteration",
    )
    for capability in LanguageCapability:
        resolved = registry.resolve(capability)
        assert resolved.capabilities == (capability,)
        assert resolved.provider_version == "v1"
        assert resolved.authority is ProviderAuthority.ENGINEERING_ONLY
        assert resolved.disposition is ProviderDisposition.MOCK_ONLY
        assert not hasattr(resolved, "adapter")
        assert not hasattr(resolved, "endpoint")


def test_registry_lookup_is_deterministic_and_returns_detached_metadata() -> None:
    original = descriptor()
    registry = LanguageProviderRegistry(
        descriptors=(original,),
        pins=(LanguageProviderPin(LanguageCapability.SPEECH_TO_TEXT, "synthetic.stt", "v1"),),
    )

    first = registry.lookup(provider_id="synthetic.stt", provider_version="v1")
    second = registry.resolve(LanguageCapability.SPEECH_TO_TEXT)

    assert first == second
    assert first is not original
    assert first is not second


@pytest.mark.parametrize(
    ("descriptors", "pins", "code"),
    [
        (
            (descriptor(), descriptor()),
            (),
            RegistryCode.DUPLICATE_IDENTITY,
        ),
        (
            (descriptor(),),
            (
                LanguageProviderPin(LanguageCapability.SPEECH_TO_TEXT, "synthetic.stt", "v1"),
                LanguageProviderPin(LanguageCapability.SPEECH_TO_TEXT, "synthetic.stt", "v1"),
            ),
            RegistryCode.AMBIGUOUS_PIN,
        ),
        (
            (descriptor(),),
            (LanguageProviderPin(LanguageCapability.TRANSLATION, "synthetic.stt", "v1"),),
            RegistryCode.INCOMPATIBLE_CAPABILITY,
        ),
        (
            (descriptor(),),
            (LanguageProviderPin(LanguageCapability.SPEECH_TO_TEXT, "synthetic.missing", "v1"),),
            RegistryCode.UNKNOWN_PROVIDER,
        ),
    ],
)
def test_registry_rejects_duplicate_ambiguous_unknown_or_incompatible_metadata(
    descriptors: tuple[LanguageProviderDescriptor, ...],
    pins: tuple[LanguageProviderPin, ...],
    code: RegistryCode,
) -> None:
    with pytest.raises(RegistryError) as caught:
        LanguageProviderRegistry(descriptors=descriptors, pins=pins)
    assert caught.value.code is code


def test_descriptor_rejects_invalid_version_duplicate_capability_or_nonengineering_authority() -> (
    None
):
    with pytest.raises(RegistryError, match=RegistryCode.INVALID_VERSION.value):
        replace(descriptor(), provider_version="latest/current")
    with pytest.raises(RegistryError, match=RegistryCode.DUPLICATE_CAPABILITY.value):
        replace(
            descriptor(),
            capabilities=(LanguageCapability.SPEECH_TO_TEXT, LanguageCapability.SPEECH_TO_TEXT),
        )
    with pytest.raises(RegistryError, match=RegistryCode.INVALID_AUTHORITY.value):
        replace(descriptor(), authority=cast(Any, "PRODUCTION_APPROVED"))
    with pytest.raises(RegistryError, match=RegistryCode.INVALID_DISPOSITION.value):
        replace(descriptor(), disposition=cast(Any, "ACTIVE"))


def test_registry_revalidates_mutated_descriptor_instead_of_trusting_frozen_shell() -> None:
    supplied = descriptor()
    object.__setattr__(supplied, "provider_id", "https://provider.invalid")

    with pytest.raises(RegistryError, match=RegistryCode.INVALID_ID.value):
        LanguageProviderRegistry(descriptors=(supplied,))


def test_resolve_requires_an_exact_pin_and_strict_capability_type() -> None:
    registry = LanguageProviderRegistry(descriptors=(descriptor(),))

    with pytest.raises(RegistryError, match=RegistryCode.UNPINNED_CAPABILITY.value):
        registry.resolve(LanguageCapability.SPEECH_TO_TEXT)
    with pytest.raises(RegistryError, match=RegistryCode.INVALID_TYPE.value):
        registry.resolve(cast(Any, "speech.transcribe"))


def test_registry_constructor_rejects_unknown_fields() -> None:
    with pytest.raises(TypeError):
        cast(Any, LanguageProviderRegistry)(descriptors=(), adapters=())
