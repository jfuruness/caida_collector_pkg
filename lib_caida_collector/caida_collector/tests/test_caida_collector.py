from itertools import product

import pytest

from .test_read_file_funcs import TestReadFileFuncs


@pytest.mark.caida_collector_base_funcs
class TestCaidaCollector:
    """Tests the functions that reside in caida_collector.py"""

    @pytest.mark.parametrize("cache, cache_written, tsv, mock",
                             product(*[[True, False] for _ in range(4)]))
    def test_run(self,
                 cache,
                 cache_written,
                 tsv,
                 mock,
                 mock_caida_collector,
                 tmp_caida_collector,
                 decoded_path,
                 tmp_path):
        """Just runs with every possible param and cache

        test_run_manual_checks should replace this
        """

        # Write cache file
        if cache_written:
            read_tester = TestReadFileFuncs()
            # Write cache file from mocked
            if mock:
                read_tester.test_write_cache_file_mock(mock_caida_collector,
                                                       decoded_path)
            # Write real cache file
            else:
                read_tester.test_write_cache_file(tmp_caida_collector)

        collector = mock_caida_collector if mock else tmp_caida_collector

        collector.run(cache=cache, tsv=tsv)

        if tsv:
            assert collector.tsv_path.exists()
        
    @pytest.mark.skip(reason="New hire work")
    def test_run_manual_checks(self):
        """Tests the run function

        test with:
            cache False, cache written, tsv False
                cache should be rewritten
                no TSV output
            cache False, cache not written, tsv False
                cache should be written
                no TSV output
            cache True, cache written, TSV false
                cache should be used and not rewritten
                no TSV output
            cache True, cache not written, TSV false
                cache should be written
                no tsv output
            cache False, cache written, tsv True
                cache should be rewritten
                compare TSV file against one that was manually checked
            cache False, cache not written, tsv True
                cache should be written
                compare TSV file against one that was manually checked
            cache True, cache written, TSV True
                cache should be used and not rewritten
                compare TSV file against one that was manually checked
            cache True, cache not written, TSV True
                cache should be written
                compare TSV file against one that was manually checked
        """

        raise NotImplementedError

    @pytest.mark.skip(reason="New hire work")
    def test_write_tsv(self):
        """Checks that the TSV written is correct for a given bgp_dag

        bgp_dag should have every type of AS (stub, mh, input_clique, ixp)
        """

        raise NotImplementedError
