from __future__ import annotations

from fastapi import APIRouter, Depends

from compat_registry.aggregation import build_stats
from compat_registry.api.deps import get_storage
from compat_registry.config import settings
from compat_registry.schemas.aggregate import RegistryStats
from compat_registry.storage.base import StorageBackend

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=RegistryStats)
async def get_stats(storage: StorageBackend = Depends(get_storage)) -> RegistryStats:
    records = await storage.all()
    return build_stats(records, current_suite_version=settings.current_suite_version)
