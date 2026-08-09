FROM python:3.11-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/
COPY data/ ./data/

RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "compat_registry.main:app", "--host", "0.0.0.0", "--port", "8000"]
