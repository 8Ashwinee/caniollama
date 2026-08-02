from __future__ import annotations

from fastapi import APIRouter

from compat_registry import __version__
from compat_registry.config import settings

router = APIRouter(tags=["meta"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/version")
async def version() -> dict[str, str]:
    """Lets an old `caniollama` CLI install notice its suite_version is behind
    and print an upgrade nudge -- closes the loop on stale local test suites."""
    return {
        "service_version": __version__,
        "current_suite_version": settings.current_suite_version,
    }
