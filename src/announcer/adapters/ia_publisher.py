"""Publication sur archive.org avec la bibliothèque internetarchive."""

from pathlib import Path
from urllib.parse import quote

from internetarchive import ArchiveSession

from announcer.ports import Metadata


class InternetArchivePublisher:
    def __init__(self, session: ArchiveSession) -> None:
        self._session = session

    def exists(self, identifier: str) -> bool:
        return bool(self._session.get_item(identifier).exists)

    def download_url(self, identifier: str, filename: str) -> str:
        return f"https://archive.org/download/{identifier}/{quote(filename)}"

    def publish(self, identifier: str, file: Path, metadata: Metadata) -> None:
        if not self._session.access_key:
            raise RuntimeError("Identifiants archive.org absents : lancez `uv run ia configure`")
        self._session.get_item(identifier).upload(
            str(file),
            metadata=dict(metadata),
            verbose=True,
            checksum=True,
            retries=10,
            retries_sleep=30,
            validate_identifier=True,
        )
