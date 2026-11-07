"""Opt-in submission to the public registry.

Hard rule: the ONLY thing constructed and sent here is a SubmissionPayload
(see models.py), which is structurally incapable of holding a prompt or a raw
model output. Nothing in this module should ever import or touch case
prompts/messages/content -- if a future change makes that necessary, it is a
sign the privacy boundary is being violated and should be reconsidered, not
routed around.

The prompt is shown every run, after results are already displayed -- never
before, never silently skipped, never persisted as a "don't ask again"
default. See https://anjallll.github.io/caniollama/privacy/ for the full data-handling explanation shown to
users.
"""

from __future__ import annotations

import httpx
from rich.console import Console

from compat_check.config import settings
from compat_check.models import RunReport


def prompt_for_submission_consent(console: Console | None = None) -> bool:
    console = console or Console()
    console.print(
        "\n[bold]Share this result with the public caniollama registry?[/]\n"
        "Only this gets sent, nothing else: model name, quantization, Ollama "
        "version, suite version, OS, and pass/fail per test case.\n"
        "[dim]Prompts and model output are never sent. See https://anjallll.github.io/caniollama/privacy/[/]\n"
    )
    answer = console.input("Submit? [y/N] ").strip().lower()
    return answer in ("y", "yes")


async def submit_result(report: RunReport, base_url: str | None = None) -> bool:
    """Returns True on a confirmed, successful submission. Never raises on
    network failure -- a failed submission should never crash a local run."""

    payload = report.to_submission_payload()
    url = f"{(base_url or settings.registry_base_url).rstrip('/')}/submissions"

    try:
        async with httpx.AsyncClient(timeout=settings.submit_timeout_seconds) as client:
            resp = await client.post(url, json=payload.model_dump(mode="json"))
            return resp.status_code in (200, 201)
    except httpx.RequestError:
        return False
