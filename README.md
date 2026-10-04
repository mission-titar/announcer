# announcer

Diffuse un épisode retrouvé de *Keroro Mission Titar* (VF) : crée un `.torrent` public (DHT, trackers [ngosang](https://github.com/ngosang/trackerslist), webseed archive.org) et publie le fichier sur archive.org.

## Prérequis

L'outil s'installe et se lance avec [uv](https://docs.astral.sh/uv/).  
Pour l'installer, voir sa [documentation d'installation](https://docs.astral.sh/uv/getting-started/installation/).  
uv se charge aussi de fournir la bonne version de Python.

## Utilisation sans cloner

```sh
uvx --from internetarchive ia configure   # une seule fois : identifiants archive.org
uvx --from git+https://github.com/mission-titar/announcer announce "[TV] KERORO MISSION TITAR N°077B « Le Tamama Impact bloqué » [Samedi 11 octobre 2008 à 10H40 sur TELETOON].avi" --found-on eMule
```

`--dry-run` crée le torrent sans rien envoyer. Le lien magnet s'affiche à la fin.

## Développement

```sh
git clone https://github.com/mission-titar/announcer && cd announcer
uv sync
uv run announce FICHIER --found-on eMule
```
