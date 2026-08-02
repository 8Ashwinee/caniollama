from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from compat_registry import __version__
from compat_registry.api import health_routes, models_routes, stats_routes, submit_routes
from compat_registry.config import settings

app = FastAPI(
    title="caniollama registry",
    description=(
        "Open, vendor-neutral registry of local Ollama model tool-calling "
        "compatibility results. Metadata only -- see /health, /version, /docs."
    ),
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health_routes.router)
app.include_router(submit_routes.router)
app.include_router(models_routes.router)
app.include_router(stats_routes.router)
