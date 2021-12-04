from datetime import datetime
import os
from pathlib import Path
from shutil import copyfile
from unittest.mock import patch

import pytest

from ..caida_collector import CaidaCollector

# https://stackoverflow.com/a/12233889/8903959
file_path = os.path.abspath(__file__)
example_dir = Path(file_path.replace("conftest.py", "examples"))
_dl_time = datetime(2021, 9, 20)
_html_path = example_dir / "serial_2.html"
_bz2_path = example_dir / "20210901.as-rel2.txt.bz2"
_decoded_path = example_dir / "20210901.as-rel2.decoded"

@pytest.fixture(scope="function")
def html_path():
    return _html_path

@pytest.fixture(scope="function")
def bz2_path():
    return _bz2_path

@pytest.fixture(scope="function")
def decoded_path():
    return _decoded_path



 
# https://stackoverflow.com/a/28507806/8903959 
# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self):
            with open(_html_path, mode="r") as f:
                self.text = f.read()
            self.status_code = 200
        def raise_for_status(*args, **kwargs):
            pass
        def close(*args, **kwargs):
            pass

    return MockResponse()

def mocked_download_file(url: str, path: str):
    copyfile(str(_bz2_path), path) 

@pytest.fixture(scope="function")
def mock_caida_collector(tmp_path):
    """Returns a CaidaCollector obj that has custom input files

    Clears cache and tsv before yielding"""

    with patch("lib_utils.helper_funcs.requests.get", mocked_requests_get):
        with patch("lib_utils.file_funcs.download_file", mocked_download_file):
            collector = CaidaCollector(dir_=tmp_path,
                                       dir_exist_ok=True,
                                       dl_time=_dl_time)
            collector.cache_path.unlink(missing_ok=True)
            collector.tsv_path.unlink(missing_ok=True)
            yield collector

@pytest.fixture(scope="function")
def tmp_caida_collector(tmp_path):
    """Returns a CaidaCollector obj that has _dir=tmp_path

    Also clears all paths
    """

    collector = CaidaCollector(dir_=tmp_path,
                               dir_exist_ok=True,
                               dl_time=_dl_time)
    collector.cache_path.unlink(missing_ok=True)
    collector.tsv_path.unlink(missing_ok=True)
    return collector
