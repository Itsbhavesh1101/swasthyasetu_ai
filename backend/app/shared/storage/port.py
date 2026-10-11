"""Provider-neutral object-storage port."""

from typing import Protocol

from app.shared.storage.types import ObjectKey, ObjectMetadata


class ObjectStoragePort(Protocol):
    """Minimal asynchronous interface for individually addressed byte objects."""

    async def put_bytes(
        self, key: ObjectKey, data: bytes | bytearray | memoryview, *, overwrite: bool = False
    ) -> ObjectMetadata: ...

    async def get_bytes(self, key: ObjectKey) -> bytes: ...

    async def exists(self, key: ObjectKey) -> bool: ...

    async def delete(self, key: ObjectKey) -> None: ...
