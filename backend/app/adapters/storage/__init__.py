"""Object-storage adapter implementations."""

from app.adapters.storage.local import LocalFilesystemObjectStorage

__all__ = ["LocalFilesystemObjectStorage"]
