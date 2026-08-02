import pytest

from tests.conftest import SAMPLE_SUBMISSION


@pytest.mark.asyncio
async def test_submit_creates_record(client):
    async with client as c:
        resp = await c.post("/submissions", json=SAMPLE_SUBMISSION)
    assert resp.status_code == 201
    body = resp.json()
    assert body["model_name"] == "qwen2.5-coder:7b"
    assert "id" in body


@pytest.mark.asyncio
async def test_submit_rejects_missing_required_field(client):
    bad = dict(SAMPLE_SUBMISSION)
    del bad["ollama_version"]
    async with client as c:
        resp = await c.post("/submissions", json=bad)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_submitted_record_appears_in_model_list(client):
    async with client as c:
        await c.post("/submissions", json=SAMPLE_SUBMISSION)
        resp = await c.get("/models")
    assert resp.status_code == 200
    names = [m["model_name"] for m in resp.json()]
    assert "qwen2.5-coder:7b" in names


@pytest.mark.asyncio
async def test_unknown_model_returns_404(client):
    async with client as c:
        resp = await c.get("/models/does-not-exist")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_health_and_version(client):
    async with client as c:
        health = await c.get("/health")
        version = await c.get("/version")
    assert health.status_code == 200
    assert version.status_code == 200
    assert "current_suite_version" in version.json()
