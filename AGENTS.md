# AGENTS.md

Utilitaire CLI qui diffuse un épisode lost media retrouvé de *Keroro Mission Titar* (VF) : `.torrent` public (DHT, trackers ngosang, webseed archive.org) puis publication sur archive.org.

## Commandes

```sh
uv sync                              # installe tout (dépendances + groupe dev)
uv run announce FICHIER --found-on eMule [--dry-run] [-o X.torrent] [-v]
uv run pytest                        # tests + couverture de branches, échoue sous 100 %
uv run ruff check . && uv run ruff format .
uv run mypy src tests                # mode strict
```

Toute modification doit laisser ces quatre vérifications au vert : la CI (`.github/workflows/verify.yml`, appelé par `main-push.yml` et `pull-request.yml`) les exécute sur Python 3.12 et 3.14 à chaque push sur `main` et à chaque PR.

## Architecture (ports & adapters)

- `domain.py` : `Episode`, parsing du nom de fichier, identifier, comment du torrent, métadonnées IA. Pur, aucune E/S.
- `ports.py` : `Protocol`s `TrackerSource`, `TorrentMaker`, `ArchivePublisher`.
- `app.py` : cas d'usage `announce()` : refuse si l'item IA existe, crée le torrent (webseed = URL de téléchargement IA), puis publie.
- `adapters/` : `ngosang.py` (urllib), `torf_maker.py` (torf + tqdm), `ia_publisher.py` (internetarchive).
- `cli.py` : argparse, logging, câblage des adapters. Seul module qui instancie les adapters.

Le domaine et l'app ne dépendent que des ports. Une nouvelle intégration = un nouveau port + un adapter, jamais d'import de lib tierce dans `domain.py`/`app.py`.

## Règles métier

- Format de nom attendu : `[TV] KERORO MISSION TITAR N°077B « Titre » [Samedi 11 octobre 2008 à 10H40 sur TELETOON].avi`. Le titre IA est le nom du fichier sans extension.
- Référence de rendu : https://archive.org/details/keroro-mission-titar-vf-077b-le-tamama-impact-bloque
- Identifiants IA : `uv run ia configure` ou variables `IA_ACCESS_KEY` / `IA_SECRET_KEY`.

## Conventions

- TDD : écrire le test qui échoue avant le code. Pytest, fakes plutôt que mocks pour les ports.
- Dépendances tierces au strict minimum : stdlib d'abord, une lib seulement si elle évite de réinventer la roue.
- Progression via tqdm, messages via `logging` (jamais `print`, sauf le lien magnet final sur stdout).
- Textes affichés à l'utilisateur en français, sans tiret cadratin ni demi-cadratin.
