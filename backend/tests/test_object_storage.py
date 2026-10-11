"""Provider-neutral object storage and controlled local adapter tests."""

import hashlib
from pathlib import Path

import pytest

from app.adapters.storage import LocalFilesystemObjectStorage
from app.shared.storage import (
    InvalidObjectKeyError,
    ObjectAlreadyExistsError,
    ObjectKey,
    ObjectNotFoundError,
    ObjectStoragePort,
)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "/absolute.bin",
        "../escape.bin",
        "synthetic/../../escape.bin",
        "a/./b",
        "a//b",
        "C:/escape.bin",
        "synthetic\\escape.bin",
        "a\x00b",
    ],
)
def test_object_key_rejects_unsafe_values(value: str) -> None:
    with pytest.raises(InvalidObjectKeyError):
        ObjectKey(value)


async def test_local_storage_round_trip_checksum_overwrite_and_delete(tmp_path: Path) -> None:
    storage: ObjectStoragePort = LocalFilesystemObjectStorage(tmp_path / "objects")
    key = ObjectKey("synthetic/123/example.bin")
    content = b"synthetic bytes"

    metadata = await storage.put_bytes(key, content)
    assert metadata.key == key
    assert metadata.size_bytes == len(content)
    assert metadata.sha256 == hashlib.sha256(content).hexdigest()
    assert await storage.exists(key) is True
    assert await storage.get_bytes(key) == content

    with pytest.raises(ObjectAlreadyExistsError):
        await storage.put_bytes(key, b"replacement")
    replaced = await storage.put_bytes(key, bytearray(b"replacement"), overwrite=True)
    assert replaced.size_bytes == len(b"replacement")
    assert await storage.get_bytes(key) == b"replacement"

    await storage.delete(key)
    assert await storage.exists(key) is False
    with pytest.raises(ObjectNotFoundError):
        await storage.get_bytes(key)
    with pytest.raises(ObjectNotFoundError):
        await storage.delete(key)


async def test_storage_errors_do_not_leak_root_or_object_content(tmp_path: Path) -> None:
    storage = LocalFilesystemObjectStorage(tmp_path / "private-root")
    key = ObjectKey("synthetic/missing.bin")

    with pytest.raises(ObjectNotFoundError) as caught:
        await storage.get_bytes(key)

    rendered = repr(caught.value)
    assert str(tmp_path) not in rendered
    assert "private-root" not in rendered


async def test_symlink_escape_is_rejected_where_supported(tmp_path: Path) -> None:
    root = tmp_path / "objects"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    link = root / "linked"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc.__class__.__name__}")

    storage = LocalFilesystemObjectStorage(root)
    key = ObjectKey("linked/escape.bin")
    with pytest.raises(InvalidObjectKeyError):
        await storage.put_bytes(key, b"must stay contained")
    with pytest.raises(InvalidObjectKeyError):
        await storage.exists(key)
    assert not (outside / "escape.bin").exists()
