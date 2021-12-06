from pathlib import Path
from typing import List

import pytest

from ..caida_collector import CaidaCollector


@pytest.mark.read_file_funcs
class TestReadFileFuncs:
    def test_get_url(self,
                     mock_caida_collector: CaidaCollector,
                     tmp_caida_collector: CaidaCollector):
        """Tests that the URL collected from Caida is accurate

        Get an example html and ensure that the URL is what we expect
        """

        test_url: str = ("http://data.caida.org/datasets/as-relationships/"
                         "serial-2/20210901.as-rel2.txt.bz2")
        # This is from the test html file
        assert mock_caida_collector._get_url() == test_url
        # This is from their website. Just to make sure their website
        # format hasn't changed
        tmp_caida_collector._get_url()

    def test_write_cache_file_mock(self,
                                   mock_caida_collector: CaidaCollector,
                                   decoded_path: Path):
        """Tests that the file is correctly decoded and written to the cache"""

        # This is from the test bz2 file
        mock_caida_collector._write_cache_file()
        with mock_caida_collector.cache_path.open(mode="r") as rawf:
            with decoded_path.open(mode="r") as ground_truth_f:
                assert rawf.read() == ground_truth_f.read()

    def test_write_cache_file(self, tmp_caida_collector: CaidaCollector):
        """Tests that caida can write to the cache file"""

        # This is from their website just to make sure it works normally
        tmp_caida_collector._write_cache_file()
        assert tmp_caida_collector.cache_path.exists()

    @pytest.mark.parametrize("exists, cache", [[True, False],
                                               [True, True],
                                               [False, False],
                                               [False, True]])
    def test_read_file(self,
                       mock_caida_collector: CaidaCollector,
                       decoded_path: Path,
                       tmp_path: Path,
                       exists: bool,
                       cache: bool):
        """Tests the read file function if the file was cached"""

        if exists:
            # Write cache file
            self.test_write_cache_file_mock(mock_caida_collector, decoded_path)
        else:
            mock_caida_collector.cache_path.unlink(missing_ok=True)

        with decoded_path.open(mode="r") as f:
            decoded: List[str] = [x.strip() for x in f.readlines()]
            assert mock_caida_collector.read_file(cache=cache) == decoded

    @pytest.mark.skip(reason="New hire work")
    def test_read_file_cache_overwrite(self):
        """Tests that the cache file gets overwritten correctly

        Tests that when the cache file exists but the cache
        parameter is False that the old cache file gets overwritten
        """

        raise NotImplementedError
