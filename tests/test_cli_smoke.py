import runpy
import subprocess
import sys

from cmdstash import cli


def test_cli_main_calls_app(monkeypatch) -> None:
    called = False

    def fake_app() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(cli, "app", fake_app)
    cli.main()

    assert called is True


def test_module_main_invokes_cli_main(monkeypatch) -> None:
    called = False

    def fake_main() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr("cmdstash.cli.main", fake_main)
    runpy.run_module("cmdstash.__main__", run_name="__main__")

    assert called is True


def _run_cmdstash(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        [sys.executable, "-m", "cmdstash", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_add_command_placeholder_output() -> None:
    result = _run_cmdstash("add", "echo hello")

    assert result.returncode == 0
    assert "cmdstash add (stub)" in result.stdout
    assert "echo hello" in result.stdout


def test_find_command_placeholder_output() -> None:
    result = _run_cmdstash("find", "git")

    assert result.returncode == 0
    assert "cmdstash find (stub)" in result.stdout
    assert "git" in result.stdout


def test_tags_command_placeholder_output() -> None:
    result = _run_cmdstash("tags")

    assert result.returncode == 0
    assert "cmdstash tags (stub)" in result.stdout
    assert "not wired yet" in result.stdout


def test_add_requires_command_argument() -> None:
    result = _run_cmdstash("add")

    assert result.returncode != 0
    assert "requires an argument" in result.stderr


def test_add_uses_consistent_stub_renderer(monkeypatch) -> None:
    captured: dict[str, str] = {}

    def fake_print_stub(title: str, body: str, *, border_style: str = "cyan") -> None:
        captured["title"] = title
        captured["body"] = body
        captured["border_style"] = border_style

    monkeypatch.setattr(cli, "_print_stub", fake_print_stub)
    cli.add("echo hello")

    assert captured["title"] == "cmdstash add (stub)"
    assert "echo hello" in captured["body"]
    assert captured["border_style"] == "cyan"


def test_find_uses_consistent_stub_renderer(monkeypatch) -> None:
    captured: dict[str, str] = {}

    def fake_print_stub(title: str, body: str, *, border_style: str = "cyan") -> None:
        captured["title"] = title
        captured["body"] = body
        captured["border_style"] = border_style

    monkeypatch.setattr(cli, "_print_stub", fake_print_stub)
    cli.find("git")

    assert captured["title"] == "cmdstash find (stub)"
    assert "git" in captured["body"]
    assert captured["border_style"] == "blue"


def test_tags_uses_consistent_stub_renderer(monkeypatch) -> None:
    captured: dict[str, str] = {}

    def fake_print_stub(title: str, body: str, *, border_style: str = "cyan") -> None:
        captured["title"] = title
        captured["body"] = body
        captured["border_style"] = border_style

    monkeypatch.setattr(cli, "_print_stub", fake_print_stub)
    cli.tags()

    assert captured["title"] == "cmdstash tags (stub)"
    assert "not wired yet" in captured["body"]
    assert captured["border_style"] == "magenta"
