import logging
from pathlib import Path
import shutil
from typing import List

import bz2
import requests


def read_file(self, cache: bool = True) -> List[str]:
    """Reads the file from the URL and unzips it and returns the lines

    Also caches the file for later calls
    """

    if not self.cache_path.exists() or cache is False:
        self._write_cache_file()

    with self.cache_path.open(mode="r") as f:
        return [x.strip() for x in f.readlines()]


def _write_cache_file(self):
    """Writes the downloaded file to the cache"""

    logging.info("No file cached from Caida. Downloading Caida file now")

    bz2_path: Path = self.dir_ / "download.bz2"

    self._download_bz2_file(self._get_url(), bz2_path)

    # Unzip and read
    with bz2.open(bz2_path) as bz2_f, self.cache_path.open(mode="w") as cachef:
        # Must decode the bytes into strings
        for bz2_line in bz2_f.readlines():
            cachef.write(bz2_line.decode())


def _download_bz2_file(self, url: str, bz2_path: Path):
    """Downloads file"""

    # https://stackoverflow.com/a/39217788/8903959
    # Download the file
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with bz2_path.open(mode="wb") as f:
            shutil.copyfileobj(r.raw, f)
