import runpy

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
