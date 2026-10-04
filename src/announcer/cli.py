"""Point d'entrée en ligne de commande : câble les adapters sur le cas d'usage."""

import argparse
import logging
from pathlib import Path

from internetarchive import get_session

from announcer.adapters.ia_publisher import InternetArchivePublisher
from announcer.adapters.ngosang import NgosangTrackers
from announcer.adapters.torf_maker import TorfMaker
from announcer.app import AlreadyPublishedError, announce
from announcer.domain import parse_episode

log = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="announce",
        description="Crée le .torrent public d'un épisode retrouvé et le publie sur archive.org.",
    )
    parser.add_argument("file", type=Path, help="fichier de l'épisode retrouvé")
    parser.add_argument("--found-on", required=True, help="où il a été retrouvé (ex : eMule)")
    parser.add_argument("-o", "--output", type=Path, help="chemin du .torrent (défaut : à côté)")
    parser.add_argument("--dry-run", action="store_true", help="ne publie pas sur archive.org")
    parser.add_argument("-v", "--verbose", action="store_true", help="logs de débogage")
    args = parser.parse_args(argv)

    logging.basicConfig(format="%(levelname)s %(message)s")
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else logging.INFO)

    file: Path = args.file
    output: Path = args.output or file.with_name(f"{file.name}.torrent")
    if not file.is_file():
        parser.error(f"fichier introuvable : {file}")
    if output.exists():
        parser.error(f"le torrent existe déjà : {output}")
    try:
        episode = parse_episode(file, args.found_on)
    except ValueError as error:
        parser.error(str(error))

    publisher = InternetArchivePublisher(get_session())
    try:
        magnet = announce(
            episode, output, NgosangTrackers(), TorfMaker(), publisher, dry_run=args.dry_run
        )
    except AlreadyPublishedError as error:
        log.error("%s", error)
        return 1
    print(magnet)
    return 0
