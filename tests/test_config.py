from pathlib import Path

from cmdstash import config


def test_get_default_data_dir_uses_platformdirs() -> None:
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

    result = config.get_default_data_dir(data_dir_resolver=fake_user_data_path)

    assert result == expected
    assert captured["appname"] == "cmdstash"
    assert captured["ensure_exists"] is True


def test_get_default_db_path_appends_db_filename() -> None:
    base_dir = Path("/tmp/cmdstash-test-data")
    result = config.get_default_db_path(data_dir=base_dir)

    assert result == base_dir / "cmdstash.db"


def test_get_supported_python_specifier_from_metadata() -> None:
    class FakeMetadata:
        def get(self, key: str) -> str | None:
            if key == "Requires-Python":
                return ">=3.14,<3.15"
            return None

    result = config.get_supported_python_specifier(metadata_reader=lambda _: FakeMetadata())

    assert result == ">=3.14,<3.15"


def test_get_supported_python_specifier_falls_back_to_unknown() -> None:
    def fake_metadata(_: str) -> object:
        raise config.PackageNotFoundError

    result = config.get_supported_python_specifier(metadata_reader=fake_metadata)

    assert result == "Unknown"
