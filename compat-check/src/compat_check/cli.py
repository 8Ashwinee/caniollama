from __future__ import annotations

import asyncio

import typer
from rich.console import Console

from compat_check import __version__
from compat_check.config import settings
from compat_check.discovery import current_os, discover_models, discover_ollama_version
from compat_check.models import RunReport
from compat_check.ollama_client import OllamaClient
from compat_check.report import render_report
from compat_check.submission import prompt_for_submission_consent, submit_result
from compat_check.suite.runner import run_suite
from compat_check.suite.version import SUITE_VERSION

app = typer.Typer(
    name="caniollama",
    help="Does this local Ollama model actually support tool calling? Find out in seconds.",
    no_args_is_help=False,
)
console = Console()


@app.command()
def version() -> None:
    """Show the package and test-suite versions."""
    console.print(f"caniollama {__version__} (test suite {SUITE_VERSION})")


@app.command()
def check(
    model: str = typer.Argument(
        None, help="Model to test, e.g. 'qwen2.5-coder:7b'. Omit to test all pulled models."
    ),
    ollama_url: str = typer.Option(settings.ollama_base_url, help="Ollama base URL."),
    submit: bool = typer.Option(
        None,
        "--submit/--no-submit",
        help="Skip the interactive prompt: always/never submit. Default is to ask.",
    ),
    registry_url: str = typer.Option(settings.registry_base_url, help="Registry base URL."),
) -> None:
    """Run the compatibility test suite against a local Ollama model (or all pulled models)."""
    asyncio.run(_check_async(model, ollama_url, submit, registry_url))


async def _check_async(
    model: str | None, ollama_url: str, submit_flag: bool | None, registry_url: str
) -> None:
    client = OllamaClient(base_url=ollama_url)

    try:
        ollama_version = await discover_ollama_version(client)
    except Exception as exc:
        console.print(f"[bold red]Could not reach Ollama at {ollama_url}: {exc}[/]")
        raise typer.Exit(code=1) from exc

    targets: list[tuple[str, str | None]]
    if model:
        targets = [(model, None)]
    else:
        discovered = await discover_models(client)
        if not discovered:
            console.print("[yellow]No locally pulled models found.[/]")
            raise typer.Exit(code=0)
        targets = [(m.name, m.quantization) for m in discovered]

    for target_name, target_quantization in targets:
        console.print(f"[dim]Running suite against {target_name}...[/]")
        results = await run_suite(client, target_name)
        report = RunReport(
            model_name=target_name,
            model_quantization=target_quantization,
            ollama_version=ollama_version,
            suite_version=SUITE_VERSION,
            os_name=current_os(),
            results=results,
        )
        render_report(report, console)

        should_submit = submit_flag
        if should_submit is None:
            should_submit = prompt_for_submission_consent(console)

        if should_submit:
            ok = await submit_result(report, base_url=registry_url)
            if ok:
                console.print("[green]Submitted. Thanks for contributing to the registry![/]\n")
            else:
                console.print("[yellow]Submission failed -- registry may be unreachable.[/]\n")
        else:
            console.print("[dim]Not submitted.[/]\n")


if __name__ == "__main__":
    app()
