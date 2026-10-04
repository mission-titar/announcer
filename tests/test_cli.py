import logging
from collections.abc import Mapping
from pathlib import Path

import pytest

from announcer import cli

STEM = (
    "[TV] KERORO MISSION TITAR N°077B « Le Tamama Impact bloqué » "
    "[Samedi 11 octobre 2008 à 10H40 sur TELETOON]"
)


class FakeTrackers:
    def fetch(self) -> list[str]:
        return ["udp://a/announce"]


class FakePublisher:
    existing = False
    published: list[str]

    def __init__(self, session: object) -> None:
        self.session = session
        FakePublisher.published = []

    def exists(self, identifier: str) -> bool:
        return self.existing

    def download_url(self, identifier: str, filename: str) -> str:
        return "https://ia/x"

    def publish(self, identifier: str, file: Path, metadata: Mapping[str, object]) -> None:
        FakePublisher.published.append(identifier)


@pytest.fixture
def media(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(cli, "NgosangTrackers", FakeTrackers)
    monkeypatch.setattr(cli, "InternetArchivePublisher", FakePublisher)
    monkeypatch.setattr(cli, "get_session", lambda: "session")
    FakePublisher.existing = False
    file = tmp_path / f"{STEM}.avi"
    file.write_bytes(b"x" * 1000)
    return file


def test_main_announces_and_prints_magnet(media: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main([str(media), "--found-on", "eMule"]) == 0

    assert media.with_name(f"{STEM}.avi.torrent").exists()
    assert FakePublisher.published == ["keroro-mission-titar-vf-077b-le-tamama-impact-bloque"]
    assert capsys.readouterr().out.startswith("magnet:?xt=urn:btih:")


def test_main_dry_run_with_custom_output(media: Path) -> None:
    output = media.parent / "out.torrent"

    assert cli.main([str(media), "--found-on", "eMule", "-o", str(output), "--dry-run"]) == 0

    assert output.exists()
    assert FakePublisher.published == []


def test_main_verbose_enables_debug_logs(media: Path) -> None:
    cli.main([str(media), "--found-on", "eMule", "--dry-run", "-v"])
    assert logging.getLogger().level == logging.DEBUG


def test_main_fails_when_item_exists(media: Path, caplog: pytest.LogCaptureFixture) -> None:
    FakePublisher.existing = True

    assert cli.main([str(media), "--found-on", "eMule"]) == 1

    assert "existe déjà" in caplog.text
    assert not media.with_name(f"{STEM}.avi.torrent").exists()


def test_main_rejects_existing_output(media: Path, capsys: pytest.CaptureFixture[str]) -> None:
    media.with_name(f"{STEM}.avi.torrent").touch()

    with pytest.raises(SystemExit) as exit_info:
        cli.main([str(media), "--found-on", "eMule"])

    assert exit_info.value.code == 2
    assert "existe déjà" in capsys.readouterr().err


def test_main_rejects_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        cli.main([str(tmp_path / f"{STEM}.avi"), "--found-on", "eMule"])

    assert "introuvable" in capsys.readouterr().err


def test_main_rejects_unexpected_name(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    file = tmp_path / "keroro.avi"
    file.touch()

    with pytest.raises(SystemExit):
        cli.main([str(file), "--found-on", "eMule"])

    assert "Nom de fichier inattendu" in capsys.readouterr().err
