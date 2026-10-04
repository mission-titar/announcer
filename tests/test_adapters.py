import io
from pathlib import Path
from typing import Any, cast

import pytest
import torf
from internetarchive import ArchiveSession

from announcer.adapters import ngosang
from announcer.adapters.ia_publisher import InternetArchivePublisher
from announcer.adapters.torf_maker import TorfMaker


def test_ngosang_fetches_non_empty_lines(monkeypatch: pytest.MonkeyPatch) -> None:
    requested: list[tuple[str, float]] = []

    def urlopen(url: str, timeout: float) -> io.BytesIO:
        requested.append((url, timeout))
        return io.BytesIO(b"udp://a/announce\n\nhttp://b/announce\n\n")

    monkeypatch.setattr(ngosang, "urlopen", urlopen)

    assert ngosang.NgosangTrackers().fetch() == ["udp://a/announce", "http://b/announce"]
    assert requested == [(ngosang.TRACKERS_URL, 30)]


def test_torf_maker_writes_public_torrent(tmp_path: Path) -> None:
    file = tmp_path / "épisode.avi"
    file.write_bytes(b"x" * 100_000)
    output = tmp_path / "épisode.avi.torrent"

    magnet = TorfMaker().make(
        file, ["udp://a/announce", "udp://b/announce"], "https://ia/x", "Bonjour", output
    )

    torrent = torf.Torrent.read(output)
    assert torrent.name == "épisode.avi"
    assert torrent.trackers == [["udp://a/announce"], ["udp://b/announce"]]
    assert torrent.webseeds == ["https://ia/x"]
    assert torrent.comment == "Bonjour"
    assert not torrent.private
    assert torrent.created_by == "announcer"
    assert magnet == str(torrent.magnet())


class FakeItem:
    def __init__(self, exists: bool) -> None:
        self.exists = exists
        self.uploads: list[tuple[str, dict[str, Any]]] = []

    def upload(self, file: str, **kwargs: Any) -> list[object]:
        self.uploads.append((file, kwargs))
        return []


class FakeSession:
    def __init__(self, access_key: str | None = "key", exists: bool = False) -> None:
        self.access_key = access_key
        self.item = FakeItem(exists)
        self.requested: list[str] = []

    def get_item(self, identifier: str) -> FakeItem:
        self.requested.append(identifier)
        return self.item


def publisher(session: FakeSession) -> InternetArchivePublisher:
    return InternetArchivePublisher(cast(ArchiveSession, session))


@pytest.mark.parametrize("exists", [True, False])
def test_ia_exists(exists: bool) -> None:
    session = FakeSession(exists=exists)
    assert publisher(session).exists("my-id") is exists
    assert session.requested == ["my-id"]


def test_ia_download_url_quotes_file_name() -> None:
    url = publisher(FakeSession()).download_url("my-id", "[TV] N°1 « é ».avi")
    assert (
        url
        == "https://archive.org/download/my-id/%5BTV%5D%20N%C2%B01%20%C2%AB%20%C3%A9%20%C2%BB.avi"
    )


def test_ia_publish_uploads_with_metadata() -> None:
    session = FakeSession()

    publisher(session).publish("my-id", Path("a.avi"), {"title": "A"})

    assert session.requested == ["my-id"]
    assert session.item.uploads == [
        (
            "a.avi",
            {
                "metadata": {"title": "A"},
                "verbose": True,
                "checksum": True,
                "retries": 10,
                "retries_sleep": 30,
                "validate_identifier": True,
            },
        )
    ]


def test_ia_publish_requires_credentials() -> None:
    session = FakeSession(access_key=None)

    with pytest.raises(RuntimeError, match="ia configure"):
        publisher(session).publish("my-id", Path("a.avi"), {"title": "A"})

    assert session.item.uploads == []
