"""Vercel entry point (see [tool.vercel] in pyproject.toml)."""

import sys
from pathlib import Path

# Vercel may not install this project as a package; make src/ importable either way.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from compat_registry.main import app

__all__ = ["app"]
