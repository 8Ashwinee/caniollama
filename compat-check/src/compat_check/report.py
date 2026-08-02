"""Builds the local, human-readable summary of a run. This is the ONLY place
detailed results are shown -- rich detail stays local, never leaves the machine
except as the reduced SubmissionPayload (see models.py)."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from compat_check.models import CaseOutcome, RunReport

_OUTCOME_STYLE = {
    CaseOutcome.STRUCTURED_PASS: ("[bold green]structured pass[/]", "✅"),
    CaseOutcome.JSON_IN_CONTENT_FALLBACK: ("[yellow]json fallback[/]", "⚠️"),
    CaseOutcome.REJECTED_BY_BACKEND: ("[bold red]rejected by backend[/]", "⛔"),
    CaseOutcome.TIMEOUT_OR_ERROR: ("[red]error / timeout[/]", "❌"),
}


def render_report(report: RunReport, console: Console | None = None) -> None:
    console = console or Console()

    console.print(
        f"\n[bold]{report.model_name}[/] "
        f"(quant: {report.model_quantization or 'unknown'}, "
        f"ollama {report.ollama_version}, suite {report.suite_version})\n"
    )

    table = Table(show_header=True, header_style="bold")
    table.add_column("Case")
    table.add_column("Outcome")
    table.add_column("Latency")
    table.add_column("Detail")

    for result in report.results:
        label, icon = _OUTCOME_STYLE[result.outcome]
        latency = f"{result.latency_ms} ms" if result.latency_ms is not None else "-"
        table.add_row(result.case_id, f"{icon} {label}", latency, result.detail or "")

    console.print(table)

    passed = sum(1 for r in report.results if r.outcome == CaseOutcome.STRUCTURED_PASS)
    total = len(report.results)
    console.print(f"\n[bold]{passed}/{total}[/] cases returned structured tool calls.\n")
