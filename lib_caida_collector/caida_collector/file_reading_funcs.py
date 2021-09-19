import logging
from pathlib import Path
from typing import List

import bz2

from lib_utils import file_funcs, helper_funcs


def read_file(self, cache=True) -> List[str]:
    """Reads the file from the URL and unzips it and returns the lines

    Also caches the file for later calls
    """

    cache_path = self.cache_dir / self.dl_time.strftime("%Y.%m.%d.txt")

    if not cache_path.exists() or cache is False:
        self._write_cache_file(cache_path)

    with cache_path.open(mode="r") as f:
        return [x.strip() for x in f.readlines()]


def _write_cache_file(self, cache_path: Path):
    """Writes the downloaded file to the cache"""

    logging.info("No file cached from Caida. Downloading Caida file now")
    url = self._get_url()

    path_str = str(self._dir / "download.bz2")
    # Create a temp path for the bz2
    with file_funcs.temp_path(path_str=path_str) as path:
        file_funcs.download_file(url, path)
        # Unzip and read
        with bz2.open(path) as f:
            # Decode bytes into str
            data = [x.decode() for x in f.readlines()]
    # Write the file to the cache path
    with cache_path.open(mode="w") as f:
        for line in data:
            f.write(line)


def _get_url(self) -> str:
    """Gets urls to download relationship files"""

    # Api url
    prepend = 'http://data.caida.org/datasets/as-relationships/serial-2/'
    # Gets all URLs. Keeps only the link for the proper download time
    return [prepend + x for x in helper_funcs.get_hrefs(prepend)
            if self.dl_time.strftime("%Y%m01") in x][0]
