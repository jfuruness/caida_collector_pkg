import logging
from pathlib import Path
from lib_utils import base_classes, file_funcs

from ..graph import AS, BGPDAG


class CaidaCollector(base_classes.Base):
    """Downloads relationships, determines metadata, and inserts to db"""

    def __init__(self,
                 *args,
                 BaseASCls=AS,
                 GraphCls=BGPDAG,
                 cache_dir=Path("/tmp/caida_collector_cache"),
                 **kwargs):
        super(CaidaCollector, self).__init__(*args, **kwargs)
        self.BaseASCls = BaseASCls
        self.GraphCls = GraphCls
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = self.cache_dir / self.dl_time.strftime("%Y.%m.%d")

    def run(self, cache=True, tsv=True) -> BGPDAG:
        """Downloads relationships, parses data, and inserts into the db.

        https://publicdata.caida.org/datasets/as-relationships/serial-2/

        Can specify a download time if you want to download an older dataset
        if cache is True it uses the downloaded file that was cached
        """

        file_lines = self.read_file(cache)
        cp_links, peer_links, ixps, input_clique = self._get_ases(file_lines)
        bgp_dag = self.GraphCls(cp_links,
                                peer_links,
                                ixps=ixps,
                                input_clique=input_clique,
                                BaseASCls=self.BaseASCls)
        if tsv:
            self._write_tsv(bgp_dag)
        return bgp_dag

    # File funcs
    from .file_reading_funcs import read_file
    from .file_reading_funcs import _write_cache_file
    from .file_reading_funcs import _get_url

    # Graph building funcs
    from .data_extraction_funcs import _get_ases
    from .data_extraction_funcs import _extract_input_clique
    from .data_extraction_funcs import _extract_ixp_ases
    from .data_extraction_funcs import _extract_provider_customers
    from .data_extraction_funcs import _extract_peers

    def _write_tsv(self, bgp_dag):
        """Writes BGP DAG info to a TSV"""

        logging.info("Made graph. Now writing to TSV")
        rows = []
        for x in bgp_dag.as_dict.values():
            rows.append(x.db_row)
        file_funcs.write_dicts_to_tsv(rows, self.tsv_path)
        logging.debug("Wrote TSV")
