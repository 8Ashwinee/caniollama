from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from compat_registry.aggregation import build_model_list, build_model_summary
from compat_registry.api.deps import get_storage
from compat_registry.schemas.aggregate import ModelCompatSummary, ModelListEntry
from compat_registry.storage.base import StorageBackend

router = APIRouter(tags=["models"])


@router.get("/models", response_model=list[ModelListEntry])
async def list_models(storage: StorageBackend = Depends(get_storage)) -> list[ModelListEntry]:
    records = await storage.all()
    return build_model_list(records)


@router.get("/models/{model_name:path}", response_model=ModelCompatSummary)
async def get_model(
    model_name: str, storage: StorageBackend = Depends(get_storage)
) -> ModelCompatSummary:
    records = await storage.for_model(model_name)
    if not records:
        raise HTTPException(status_code=404, detail=f"No reports found for '{model_name}'.")
    return build_model_summary(model_name, records)
