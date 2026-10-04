"""Cas d'usage : annoncer un épisode retrouvé."""

import logging
from pathlib import Path

from announcer.domain import Episode
from announcer.ports import ArchivePublisher, TorrentMaker, TrackerSource

log = logging.getLogger(__name__)


class AlreadyPublishedError(Exception):
    pass


def announce(
    episode: Episode,
    output: Path,
    trackers: TrackerSource,
    torrents: TorrentMaker,
    archive: ArchivePublisher,
    *,
    dry_run: bool = False,
) -> str:
    identifier = episode.identifier
    if archive.exists(identifier):
        raise AlreadyPublishedError(f"L'item archive.org {identifier} existe déjà")

    tracker_urls = trackers.fetch()
    log.info("%d trackers récupérés", len(tracker_urls))
    webseed = archive.download_url(identifier, episode.path.name)
    magnet = torrents.make(episode.path, tracker_urls, webseed, episode.torrent_comment, output)
    log.info("Torrent écrit : %s", output)

    if dry_run:
        log.info(
            "Simulation : pas d'envoi sur archive.org. Métadonnées : %s", episode.archive_metadata
        )
    else:
        archive.publish(identifier, episode.path, episode.archive_metadata)
        log.info("Publié : https://archive.org/details/%s", identifier)
    return magnet
