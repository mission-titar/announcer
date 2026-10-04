"""Épisode retrouvé et règles de diffusion propres à Keroro Mission Titar VF."""

import datetime
import html
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

FILE_NAME = re.compile(
    r"\[TV\] KERORO MISSION TITAR N°(?P<number>\w+) « (?P<name>.+) » "
    r"\[(?P<weekday>\w+) (?P<day>\d{1,2}) (?P<month>\w+) (?P<year>\d{4}) "
    r"à (?P<hour>\d{1,2})H(?P<minute>\d{2}) sur (?P<channel>.+)\]",
    re.IGNORECASE,
)
MONTHS = [
    "janvier",
    "fevrier",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "aout",
    "septembre",
    "octobre",
    "novembre",
    "decembre",
]
CHANNELS = {"TELETOON": "Télétoon"}
SUBJECTS = ["keroro", "vf", "french", "français"]
TEAM = "LOST MEDIA KERORO MISSION TITAR VF"


def _ascii(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return decomposed.encode("ascii", "ignore").decode()


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", _ascii(text).lower()).strip("-")


@dataclass(frozen=True)
class Episode:
    path: Path
    number: str
    name: str
    broadcast: str
    date: str
    channel: str
    found_on: str

    @property
    def title(self) -> str:
        return self.path.stem

    @property
    def identifier(self) -> str:
        return f"keroro-mission-titar-vf-{self.number.lower()}-{_slug(self.name)}"

    def _lines(self) -> list[str]:
        channel = CHANNELS.get(self.channel, self.channel)
        return [
            f"Keroro Mission Titar - Épisode {self.number.lstrip('0')} « {self.name} » (VF)",
            f"Enregistrement de la diffusion {channel} du {self.broadcast}.",
            f"Épisode considéré perdu, retrouvé sur {self.found_on} par l'équipe {TEAM}.",
        ]

    @property
    def torrent_comment(self) -> str:
        return "\n".join([*self._lines(), "Merci de rester en seed pour préserver l'épisode !"])

    @property
    def archive_metadata(self) -> dict[str, str | list[str]]:
        description = "\n".join(
            f"<p>{html.escape(line, quote=False)}</p>" for line in self._lines()
        )
        return {
            "title": self.title,
            "mediatype": "movies",
            "collection": "opensource_movies",
            "creator": "Sunrise",
            "date": self.date,
            "language": "fre",
            "subject": [*SUBJECTS, self.channel.lower(), "titar"],
            "sound": "sound",
            "color": "color",
            "description": description,
        }


def parse_episode(path: Path, found_on: str) -> Episode:
    match = FILE_NAME.fullmatch(path.stem)
    try:
        if not match:
            raise ValueError
        month = MONTHS.index(_ascii(match["month"].lower())) + 1
        date = datetime.date(int(match["year"]), month, int(match["day"]))
    except ValueError:
        raise ValueError(
            f"Nom de fichier inattendu : {path.name!r}. Format attendu : "
            "[TV] KERORO MISSION TITAR N°077B « Titre » "
            "[Samedi 11 octobre 2008 à 10H40 sur TELETOON].avi"
        ) from None
    weekday, day, hour = match["weekday"].lower(), match["day"], match["hour"]
    return Episode(
        path=path,
        number=match["number"],
        name=match["name"],
        broadcast=f"{weekday} {day} {match['month'].lower()} {match['year']}, "
        f"{hour}h{match['minute']}",
        date=date.isoformat(),
        channel=match["channel"],
        found_on=found_on,
    )
