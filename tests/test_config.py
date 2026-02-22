from pathlib import Path

from cmdstash import config


def test_get_default_data_dir_uses_platformdirs(monkeypatch) -> None:
    expected = Path("/tmp/cmdstash-test-data")
    captured: dict[str, object] = {}

    def fake_user_data_path(
        appname: str | None = None,
        *,
        ensure_exists: bool = False,
        **_: object,
    ) -> Path:
        captured["appname"] = appname
        captured["ensure_exists"] = ensure_exists
        return expected

    monkeypatch.setattr(config, "user_data_path", fake_user_data_path)

    result = config.get_default_data_dir()

    assert result == expected
    assert captured["appname"] == "cmdstash"
    assert captured["ensure_exists"] is True


def test_get_default_db_path_appends_db_filename(monkeypatch) -> None:
    base_dir = Path("/tmp/cmdstash-test-data")
    monkeypatch.setattr(config, "get_default_data_dir", lambda: base_dir)

    result = config.get_default_db_path()

    assert result == base_dir / "cmdstash.db"


def test_get_supported_python_specifier_from_metadata(monkeypatch) -> None:
    class FakeMetadata:
        def get(self, key: str) -> str | None:
            if key == "Requires-Python":
                return ">=3.14,<3.15"
            return None

    monkeypatch.setattr(config, "metadata", lambda _: FakeMetadata())

    result = config.get_supported_python_specifier()

    assert result == ">=3.14,<3.15"


def test_get_supported_python_specifier_falls_back_to_unknown(monkeypatch) -> None:
    def fake_metadata(_: str) -> object:
        raise config.PackageNotFoundError

    monkeypatch.setattr(config, "metadata", fake_metadata)

    result = config.get_supported_python_specifier()

    assert result == "Unknown"
