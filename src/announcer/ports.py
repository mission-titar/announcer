"""Ports : ce dont le cas d'usage a besoin du monde extérieur."""

from collections.abc import Mapping
from pathlib import Path
from typing import Protocol

Metadata = Mapping[str, str | list[str]]


class TrackerSource(Protocol):
    def fetch(self) -> list[str]: ...


class TorrentMaker(Protocol):
    def make(
        self, file: Path, trackers: list[str], webseed: str, comment: str, output: Path
    ) -> str:
        """Écrit le .torrent dans `output` et renvoie son lien magnet."""
        ...


class ArchivePublisher(Protocol):
    def exists(self, identifier: str) -> bool: ...

    def download_url(self, identifier: str, filename: str) -> str: ...

    def publish(self, identifier: str, file: Path, metadata: Metadata) -> None: ...
