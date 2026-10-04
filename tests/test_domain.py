from pathlib import Path

import pytest

from announcer.domain import Episode, parse_episode

STEM = (
    "[TV] KERORO MISSION TITAR N°077B « Le Tamama Impact bloqué » "
    "[Samedi 11 octobre 2008 à 10H40 sur TELETOON]"
)


@pytest.fixture
def episode() -> Episode:
    return parse_episode(Path(f"tmp/{STEM}.avi"), found_on="eMule")


def test_parse_reads_fields_from_file_name(episode: Episode) -> None:
    assert episode.path == Path(f"tmp/{STEM}.avi")
    assert episode.title == STEM
    assert episode.number == "077B"
    assert episode.name == "Le Tamama Impact bloqué"
    assert episode.broadcast == "samedi 11 octobre 2008, 10h40"
    assert episode.date == "2008-10-11"
    assert episode.channel == "TELETOON"
    assert episode.found_on == "eMule"


def test_parse_accepts_unaccented_month() -> None:
    stem = STEM.replace("Samedi 11 octobre", "Lundi 4 fevrier")
    assert parse_episode(Path(f"{stem}.mkv"), "eMule").date == "2008-02-04"


@pytest.mark.parametrize(
    "stem",
    [
        "Keroro 77B.avi",
        STEM.replace("octobre", "brumaire"),
        STEM.replace("11 octobre", "31 novembre"),
    ],
)
def test_parse_rejects_unexpected_name(stem: str) -> None:
    with pytest.raises(ValueError, match="Nom de fichier inattendu"):
        parse_episode(Path(f"{stem}.avi"), "eMule")


def test_identifier_is_ascii_slug(episode: Episode) -> None:
    assert episode.identifier == "keroro-mission-titar-vf-077b-le-tamama-impact-bloque"


def test_torrent_comment(episode: Episode) -> None:
    assert episode.torrent_comment == (
        "Keroro Mission Titar - Épisode 77B « Le Tamama Impact bloqué » (VF)\n"
        "Enregistrement de la diffusion Télétoon du samedi 11 octobre 2008, 10h40.\n"
        "Épisode considéré perdu, retrouvé sur eMule par l'équipe "
        "LOST MEDIA KERORO MISSION TITAR VF.\n"
        "Merci de rester en seed pour préserver l'épisode !"
    )


def test_archive_metadata(episode: Episode) -> None:
    assert episode.archive_metadata == {
        "title": STEM,
        "mediatype": "movies",
        "collection": "opensource_movies",
        "creator": "Sunrise",
        "date": "2008-10-11",
        "language": "fre",
        "subject": ["keroro", "vf", "french", "français", "teletoon", "titar"],
        "sound": "sound",
        "color": "color",
        "description": (
            "<p>Keroro Mission Titar - Épisode 77B « Le Tamama Impact bloqué » (VF)</p>\n"
            "<p>Enregistrement de la diffusion Télétoon du samedi 11 octobre 2008, 10h40.</p>\n"
            "<p>Épisode considéré perdu, retrouvé sur eMule par l'équipe "
            "LOST MEDIA KERORO MISSION TITAR VF.</p>"
        ),
    }


def test_description_escapes_html() -> None:
    episode = parse_episode(Path(f"{STEM}.avi"), found_on="<b>Kazaa</b>")
    assert "retrouvé sur &lt;b&gt;Kazaa&lt;/b&gt; par" in str(
        episode.archive_metadata["description"]
    )


def test_unknown_channel_is_kept_as_is() -> None:
    episode = parse_episode(Path(f"{STEM.replace('TELETOON', 'GULLI')}.avi"), "eMule")
    assert "diffusion GULLI du" in episode.torrent_comment
    assert "gulli" in episode.archive_metadata["subject"]
