"""Explicit engineering-only metadata registry for synthetic P12 providers."""

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from app.modules.language.contracts import ProviderAuthority

_PROVIDER_ID = re.compile(r"^[a-z][a-z0-9.-]{0,127}$")
_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
MAX_PROVIDER_DESCRIPTORS: Final = 32


class LanguageCapability(StrEnum):
    SPEECH_TO_TEXT = "speech.transcribe"
    LANGUAGE_DETECTION = "language.detect"
    TRANSLITERATION = "language.transliterate"
    TRANSLATION = "language.translate"
    TEXT_TO_SPEECH = "speech.synthesize"


class ProviderDisposition(StrEnum):
    MOCK_ONLY = "MOCK_ONLY"


class RegistryCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_ID = "INVALID_ID"
    INVALID_VERSION = "INVALID_VERSION"
    INVALID_CAPABILITY = "INVALID_CAPABILITY"
    DUPLICATE_CAPABILITY = "DUPLICATE_CAPABILITY"
    INVALID_AUTHORITY = "INVALID_AUTHORITY"
    INVALID_DISPOSITION = "INVALID_DISPOSITION"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    AMBIGUOUS_PIN = "AMBIGUOUS_PIN"
    UNKNOWN_PROVIDER = "UNKNOWN_PROVIDER"
    INCOMPATIBLE_CAPABILITY = "INCOMPATIBLE_CAPABILITY"
    UNPINNED_CAPABILITY = "UNPINNED_CAPABILITY"


class RegistryError(ValueError):
    """Content-free deterministic registry failure."""

    def __init__(self, code: RegistryCode) -> None:
        self.code = code
        super().__init__(code.value)


def _fail(code: RegistryCode) -> RegistryError:
    return RegistryError(code)


def _provider_id(value: object) -> str:
    if type(value) is not str or _PROVIDER_ID.fullmatch(value) is None or "://" in value:
        raise _fail(RegistryCode.INVALID_ID)
    return value


def _version(value: object) -> str:
    if type(value) is not str or _VERSION.fullmatch(value) is None:
        raise _fail(RegistryCode.INVALID_VERSION)
    return value


@dataclass(frozen=True, slots=True)
class LanguageProviderDescriptor:
    provider_id: str
    provider_version: str
    capabilities: tuple[LanguageCapability, ...]
    authority: ProviderAuthority
    disposition: ProviderDisposition

    def __post_init__(self) -> None:
        _provider_id(self.provider_id)
        _version(self.provider_version)
        if type(self.capabilities) is not tuple or not self.capabilities:
            raise _fail(RegistryCode.INVALID_CAPABILITY)
        if any(type(item) is not LanguageCapability for item in self.capabilities):
            raise _fail(RegistryCode.INVALID_CAPABILITY)
        if len(set(self.capabilities)) != len(self.capabilities):
            raise _fail(RegistryCode.DUPLICATE_CAPABILITY)
        if self.capabilities != tuple(sorted(self.capabilities, key=lambda item: item.value)):
            raise _fail(RegistryCode.INVALID_CAPABILITY)
        if type(self.authority) is not ProviderAuthority or (
            self.authority is not ProviderAuthority.ENGINEERING_ONLY
        ):
            raise _fail(RegistryCode.INVALID_AUTHORITY)
        if type(self.disposition) is not ProviderDisposition or (
            self.disposition is not ProviderDisposition.MOCK_ONLY
        ):
            raise _fail(RegistryCode.INVALID_DISPOSITION)


@dataclass(frozen=True, slots=True)
class LanguageProviderPin:
    capability: LanguageCapability
    provider_id: str
    provider_version: str

    def __post_init__(self) -> None:
        if type(self.capability) is not LanguageCapability:
            raise _fail(RegistryCode.INVALID_CAPABILITY)
        _provider_id(self.provider_id)
        _version(self.provider_version)


type _DescriptorSnapshot = tuple[
    str,
    str,
    tuple[LanguageCapability, ...],
    ProviderAuthority,
    ProviderDisposition,
]


def _snapshot_descriptor(value: object) -> _DescriptorSnapshot:
    if type(value) is not LanguageProviderDescriptor:
        raise _fail(RegistryCode.INVALID_TYPE)
    validated = LanguageProviderDescriptor(
        provider_id=value.provider_id,
        provider_version=value.provider_version,
        capabilities=value.capabilities,
        authority=value.authority,
        disposition=value.disposition,
    )
    return (
        validated.provider_id,
        validated.provider_version,
        validated.capabilities,
        validated.authority,
        validated.disposition,
    )


def _restore_descriptor(value: _DescriptorSnapshot) -> LanguageProviderDescriptor:
    return LanguageProviderDescriptor(
        provider_id=value[0],
        provider_version=value[1],
        capabilities=value[2],
        authority=value[3],
        disposition=value[4],
    )


def _snapshot_pin(value: object) -> LanguageProviderPin:
    if type(value) is not LanguageProviderPin:
        raise _fail(RegistryCode.INVALID_TYPE)
    return LanguageProviderPin(
        capability=value.capability,
        provider_id=value.provider_id,
        provider_version=value.provider_version,
    )


@dataclass(frozen=True, slots=True, init=False)
class LanguageProviderRegistry:
    _descriptors: Mapping[tuple[str, str], _DescriptorSnapshot] = field(repr=False)
    _pins: Mapping[LanguageCapability, tuple[str, str]] = field(repr=False)

    def __init__(
        self,
        *,
        descriptors: tuple[LanguageProviderDescriptor, ...],
        pins: tuple[LanguageProviderPin, ...] = (),
    ) -> None:
        if type(descriptors) is not tuple or type(pins) is not tuple:
            raise _fail(RegistryCode.INVALID_TYPE)
        if len(descriptors) > MAX_PROVIDER_DESCRIPTORS:
            raise _fail(RegistryCode.LIMIT_EXCEEDED)

        registered: dict[tuple[str, str], _DescriptorSnapshot] = {}
        for supplied in descriptors:
            snapshot = _snapshot_descriptor(supplied)
            identity = (snapshot[0], snapshot[1])
            if identity in registered:
                raise _fail(RegistryCode.DUPLICATE_IDENTITY)
            registered[identity] = snapshot

        configured: dict[LanguageCapability, tuple[str, str]] = {}
        for supplied_pin in pins:
            pin = _snapshot_pin(supplied_pin)
            if pin.capability in configured:
                raise _fail(RegistryCode.AMBIGUOUS_PIN)
            identity = (pin.provider_id, pin.provider_version)
            descriptor = registered.get(identity)
            if descriptor is None:
                raise _fail(RegistryCode.UNKNOWN_PROVIDER)
            if pin.capability not in descriptor[2]:
                raise _fail(RegistryCode.INCOMPATIBLE_CAPABILITY)
            configured[pin.capability] = identity

        object.__setattr__(self, "_descriptors", MappingProxyType(registered.copy()))
        object.__setattr__(self, "_pins", MappingProxyType(configured.copy()))

    @property
    def descriptors(self) -> tuple[LanguageProviderDescriptor, ...]:
        return tuple(
            _restore_descriptor(snapshot)
            for _, snapshot in sorted(self._descriptors.items(), key=lambda item: item[0])
        )

    def lookup(
        self, *, provider_id: object, provider_version: object
    ) -> LanguageProviderDescriptor:
        if type(provider_id) is not str or type(provider_version) is not str:
            raise _fail(RegistryCode.INVALID_TYPE)
        snapshot = self._descriptors.get((provider_id, provider_version))
        if snapshot is None:
            raise _fail(RegistryCode.UNKNOWN_PROVIDER)
        return _restore_descriptor(snapshot)

    def resolve(self, capability: LanguageCapability) -> LanguageProviderDescriptor:
        if type(capability) is not LanguageCapability:
            raise _fail(RegistryCode.INVALID_TYPE)
        identity = self._pins.get(capability)
        if identity is None:
            raise _fail(RegistryCode.UNPINNED_CAPABILITY)
        descriptor = self.lookup(provider_id=identity[0], provider_version=identity[1])
        if capability not in descriptor.capabilities:
            raise _fail(RegistryCode.INCOMPATIBLE_CAPABILITY)
        return descriptor


_SYNTHETIC_PROVIDERS: Final = (
    ("synthetic.language-detection", LanguageCapability.LANGUAGE_DETECTION),
    ("synthetic.speech-to-text", LanguageCapability.SPEECH_TO_TEXT),
    ("synthetic.text-to-speech", LanguageCapability.TEXT_TO_SPEECH),
    ("synthetic.translation", LanguageCapability.TRANSLATION),
    ("synthetic.transliteration", LanguageCapability.TRANSLITERATION),
)


def build_synthetic_language_registry() -> LanguageProviderRegistry:
    """Build inert exact-pin metadata without registering adapters or capabilities."""

    descriptors = tuple(
        LanguageProviderDescriptor(
            provider_id=provider_id,
            provider_version="v1",
            capabilities=(capability,),
            authority=ProviderAuthority.ENGINEERING_ONLY,
            disposition=ProviderDisposition.MOCK_ONLY,
        )
        for provider_id, capability in _SYNTHETIC_PROVIDERS
    )
    pins = tuple(
        LanguageProviderPin(
            capability=capability,
            provider_id=provider_id,
            provider_version="v1",
        )
        for provider_id, capability in _SYNTHETIC_PROVIDERS
    )
    return LanguageProviderRegistry(descriptors=descriptors, pins=pins)


__all__ = [
    "LanguageCapability",
    "LanguageProviderDescriptor",
    "LanguageProviderPin",
    "LanguageProviderRegistry",
    "ProviderAuthority",
    "ProviderDisposition",
    "RegistryCode",
    "RegistryError",
    "build_synthetic_language_registry",
]
