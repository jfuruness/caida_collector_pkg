import logging
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup as Soup
import bz2
import requests



def _get_url(self) -> str:
    """Gets urls to download relationship files"""

    # Api url
    prepend = 'http://data.caida.org/datasets/as-relationships/serial-2/'
    # Gets all URLs. Keeps only the link for the proper download time
    return [prepend + x for x in self._get_hrefs(prepend)
            if self.dl_time.strftime("%Y%m01") in x][0]

def _get_hrefs(self, url: str) -> list:
    """Returns hrefs from a tags at a given url"""

    # Query URL
    with requests.get(url, stream=True, timeout=30) as r:
        # Check for errors
        r.raise_for_status()
        # Get soup
        soup = Soup(r.text, "html.parser")
        # Extract hrefs from a tags
        return [x.get("href") for x in soup.select("a")
                if x.get("href") is not None]
