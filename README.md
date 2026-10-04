# announcer

Diffuse un épisode retrouvé de *Keroro Mission Titar* (VF) : crée un `.torrent` public (DHT, trackers [ngosang](https://github.com/ngosang/trackerslist), webseed archive.org) et publie le fichier sur archive.org.

```sh
uv sync
uv run ia configure     # une seule fois : identifiants archive.org
uv run announce "[TV] KERORO MISSION TITAR N°077B « Le Tamama Impact bloqué » [Samedi 11 octobre 2008 à 10H40 sur TELETOON].avi" --found-on eMule
```

`--dry-run` crée le torrent sans rien envoyer. Le lien magnet s'affiche à la fin.
