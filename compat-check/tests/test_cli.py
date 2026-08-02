from typer.testing import CliRunner

from compat_check.cli import app

runner = CliRunner()


def test_version_command_runs():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "caniollama" in result.stdout


def test_check_fails_cleanly_when_ollama_unreachable():
    result = runner.invoke(app, ["check", "--ollama-url", "http://127.0.0.1:1"])
    assert result.exit_code == 1
