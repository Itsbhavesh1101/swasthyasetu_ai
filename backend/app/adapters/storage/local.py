"""Controlled local filesystem object storage for development and tests only.

This adapter is not production object storage and is not an untrusted medical
upload boundary. It makes no durability, encryption, malware, or compliance
guarantees.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
from contextlib import suppress
from pathlib import Path
from uuid import uuid4

from app.shared.storage import (
    InvalidObjectKeyError,
    ObjectAlreadyExistsError,
    ObjectKey,
    ObjectMetadata,
    ObjectNotFoundError,
    ObjectStorageError,
)


class LocalFilesystemObjectStorage:
    """Root-contained development/test adapter using blocking I/O in threads."""

    def __init__(self, root: Path) -> None:
        try:
            self._root = root.resolve()
            self._root.mkdir(parents=True, exist_ok=True)
        except (OSError, RuntimeError):
            raise ObjectStorageError("local object root initialization failed") from None

    def _path_for(self, key: ObjectKey) -> Path:
        if not isinstance(key, ObjectKey):
            raise TypeError("key must be an ObjectKey")
        try:
            candidate = self._root.joinpath(*str(key).split("/")).resolve()
        except (OSError, RuntimeError):
            raise InvalidObjectKeyError("object key cannot be resolved safely") from None
        try:
            candidate.relative_to(self._root)
        except ValueError as exc:
            raise InvalidObjectKeyError("object key escapes configured root") from exc
        return candidate

    async def put_bytes(
        self, key: ObjectKey, data: bytes | bytearray | memoryview, *, overwrite: bool = False
    ) -> ObjectMetadata:
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError("object data must be bytes-like")
        content = bytes(data)
        return await asyncio.to_thread(self._put_bytes, key, content, overwrite)

    def _put_bytes(self, key: ObjectKey, data: bytes, overwrite: bool) -> ObjectMetadata:
        path = self._path_for(key)
        temporary: Path | None = None
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path = self._path_for(key)
            if path.exists() and not overwrite:
                raise ObjectAlreadyExistsError("object already exists")
            temporary = path.parent / f".{path.name}.{uuid4().hex}.tmp"
            temporary.write_bytes(data)
            os.replace(temporary, path)
            return ObjectMetadata(
                key=key,
                size_bytes=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
            )
        except ObjectStorageError:
            raise
        except OSError:
            raise ObjectStorageError("local object write failed") from None
        finally:
            if temporary is not None:
                with suppress(OSError):
                    temporary.unlink(missing_ok=True)

    async def get_bytes(self, key: ObjectKey) -> bytes:
        return await asyncio.to_thread(self._get_bytes, key)

    def _get_bytes(self, key: ObjectKey) -> bytes:
        path = self._path_for(key)
        if not path.is_file():
            raise ObjectNotFoundError("object not found")
        try:
            return path.read_bytes()
        except OSError:
            raise ObjectStorageError("local object read failed") from None

    async def exists(self, key: ObjectKey) -> bool:
        return await asyncio.to_thread(self._exists, key)

    def _exists(self, key: ObjectKey) -> bool:
        return self._path_for(key).is_file()

    async def delete(self, key: ObjectKey) -> None:
        await asyncio.to_thread(self._delete, key)

    def _delete(self, key: ObjectKey) -> None:
        path = self._path_for(key)
        if not path.is_file():
            raise ObjectNotFoundError("object not found")
        try:
            path.unlink()
        except OSError:
            raise ObjectStorageError("local object delete failed") from None
