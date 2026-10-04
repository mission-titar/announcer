"""Trackers publics de la liste ngosang/trackerslist."""

from urllib.request import urlopen

TRACKERS_URL = "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"


class NgosangTrackers:
    def fetch(self) -> list[str]:
        with urlopen(TRACKERS_URL, timeout=30) as response:
            text: str = response.read().decode()
        return [line.strip() for line in text.splitlines() if line.strip()]
