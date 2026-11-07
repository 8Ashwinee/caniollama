from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("compat-registry")
except PackageNotFoundError:  # running from source without install (e.g. Vercel)
    __version__ = "0.0.0+source"
