from collections.abc import Mapping
from pathlib import Path

import pytest

from announcer.app import AlreadyPublishedError, announce
from announcer.domain import Episode, parse_episode

STEM = (
    "[TV] KERORO MISSION TITAR N°077B « Le Tamama Impact bloqué » "
    "[Samedi 11 octobre 2008 à 10H40 sur TELETOON]"
)


class FakeTrackers:
    def fetch(self) -> list[str]:
        return ["udp://a/announce", "udp://b/announce"]


class FakeTorrents:
    def __init__(self) -> None:
        self.calls: list[tuple[Path, list[str], str, str, Path]] = []

    def make(
        self, file: Path, trackers: list[str], webseed: str, comment: str, output: Path
    ) -> str:
        self.calls.append((file, trackers, webseed, comment, output))
        return "magnet:?xt=urn:btih:abc"


class FakeArchive:
    def __init__(self, existing: bool = False) -> None:
        self.existing = existing
        self.published: list[tuple[str, Path, Mapping[str, str | list[str]]]] = []

    def exists(self, identifier: str) -> bool:
        return self.existing

    def download_url(self, identifier: str, filename: str) -> str:
        return f"https://ia/{identifier}/{filename}"

    def publish(self, identifier: str, file: Path, metadata: Mapping[str, str | list[str]]) -> None:
        self.published.append((identifier, file, metadata))


@pytest.fixture
def episode() -> Episode:
    return parse_episode(Path(f"{STEM}.avi"), "eMule")


def test_announce_makes_torrent_with_webseed_then_publishes(episode: Episode) -> None:
    torrents, archive = FakeTorrents(), FakeArchive()

    magnet = announce(episode, Path("out.torrent"), FakeTrackers(), torrents, archive)

    assert magnet == "magnet:?xt=urn:btih:abc"
    assert torrents.calls == [
        (
            episode.path,
            ["udp://a/announce", "udp://b/announce"],
            f"https://ia/{episode.identifier}/{STEM}.avi",
            episode.torrent_comment,
            Path("out.torrent"),
        )
    ]
    assert archive.published == [(episode.identifier, episode.path, episode.archive_metadata)]


def test_announce_refuses_existing_item(episode: Episode) -> None:
    torrents = FakeTorrents()

    with pytest.raises(AlreadyPublishedError, match=episode.identifier):
        announce(episode, Path("out.torrent"), FakeTrackers(), torrents, FakeArchive(True))

    assert torrents.calls == []


def test_announce_dry_run_skips_publication(episode: Episode) -> None:
    torrents, archive = FakeTorrents(), FakeArchive()

    announce(episode, Path("out.torrent"), FakeTrackers(), torrents, archive, dry_run=True)

    assert len(torrents.calls) == 1
    assert archive.published == []
