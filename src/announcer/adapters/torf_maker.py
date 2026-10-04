"""Création du .torrent avec torf."""

from pathlib import Path

import torf
from tqdm import tqdm


class TorfMaker:
    def make(
        self, file: Path, trackers: list[str], webseed: str, comment: str, output: Path
    ) -> str:
        torrent = torf.Torrent(
            path=file,
            trackers=trackers,
            webseeds=[webseed],
            comment=comment,
            created_by="announcer",
        )
        with tqdm(total=torrent.pieces, desc="Hachage", unit="pièce") as bar:

            def progress(_torrent: torf.Torrent, _path: str, done: int, _total: int) -> None:
                bar.update(done - bar.n)

            torrent.generate(callback=progress, interval=0.5)
        torrent.write(output)
        return str(torrent.magnet())
