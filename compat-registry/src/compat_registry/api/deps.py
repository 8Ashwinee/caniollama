from __future__ import annotations

from functools import lru_cache

from compat_registry.config import settings
from compat_registry.rate_limit import RateLimiter
from compat_registry.storage.base import StorageBackend
from compat_registry.storage.file_backend import FileStorageBackend


@lru_cache
def get_storage() -> StorageBackend:
    if settings.storage_backend == "db":
        from compat_registry.storage.db_backend import SQLiteStorageBackend

        return SQLiteStorageBackend(settings.data_dir / "registry.sqlite3")
    return FileStorageBackend(settings.data_dir)


@lru_cache
def get_rate_limiter() -> RateLimiter:
    return RateLimiter(max_per_minute=settings.rate_limit_per_minute)
