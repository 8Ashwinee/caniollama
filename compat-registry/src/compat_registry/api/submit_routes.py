from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status

from compat_registry.api.deps import get_rate_limiter, get_storage
from compat_registry.rate_limit import RateLimiter, get_client_ip
from compat_registry.schemas.submission import SubmissionIn, SubmissionRecord
from compat_registry.storage.base import StorageBackend

router = APIRouter(tags=["submissions"])


@router.post("/submissions", response_model=SubmissionRecord, status_code=status.HTTP_201_CREATED)
async def create_submission(
    submission: SubmissionIn,
    request: Request,
    storage: StorageBackend = Depends(get_storage),
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> SubmissionRecord:
    """Open, unauthenticated write endpoint -- rate-limited per IP, per the
    project's 'open data, no account wall' principle. No auth by design."""
    limiter.check(get_client_ip(request))
    return await storage.put(submission)
