from csv import DictWriter
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path
from typing import List, Optional, Type


from ..graph import AS, BGPDAG

# Can't import into class due to mypy issue:
# https://github.com/python/mypy/issues/7045
# File funcs
from .file_reading_funcs import read_file
from .file_reading_funcs import _write_cache_file
from .file_reading_funcs import _download_bz2_file

# HTML funcs
from .html_funcs import _get_url
from .html_funcs import _get_hrefs

# Graph building funcs
from .data_extraction_funcs import _get_ases
from .data_extraction_funcs import _extract_input_clique
from .data_extraction_funcs import _extract_ixp_ases
from .data_extraction_funcs import _extract_provider_customers
from .data_extraction_funcs import _extract_peers


class CaidaCollector:
    """Downloads relationships, determines metadata, and inserts to db"""

    read_file = read_file
    _write_cache_file = _write_cache_file
    _download_bz2_file = _download_bz2_file

    # HTML funcs
    _get_url = _get_url
    _get_hrefs = _get_hrefs

    # Graph building funcs
    _get_ases = _get_ases
    _extract_input_clique = _extract_input_clique
    _extract_ixp_ases = _extract_ixp_ases
    _extract_provider_customers = _extract_provider_customers
    _extract_peers = _extract_peers

    def __init__(self,
                 dl_time: Optional[datetime] = None,
                 base_dir: Optional[Path] = None,
                 dir_: Optional[Path] = None,
                 BaseASCls: Type[AS] = AS,
                 GraphCls: Type[BGPDAG] = BGPDAG,
                 cache_dir: Path = Path("/tmp/caida_collector_cache"),
                 **kwargs):

        self.dl_time: datetime = dl_time if dl_time else self.default_dl_time()

        # Set up base directory
        if base_dir:
            self.base_dir: Path = base_dir  # type: ignore
        elif dir_:
            self.base_dir: Path = dir_  # type: ignore
        else:
            self.base_dir: Path = Path("/tmp/")  # type: ignore

        # Set up directory
        name: str = self.__class__.__name__
        t_str: str = datetime.now().strftime("%Y.%m.%d.%H.%M.%S.%f")
        uid: str = f"{t_str}_{os.getpid()}"
        self.dir_: Path = dir_ if dir_ else self.base_dir / f"{name}.{uid}"
        self.dir_.mkdir(parents=True, exist_ok=True)

        # TSV path
        self.tsv_path: Path = self.dir_ / f"{name}.tsv"

        self.BaseASCls: Type[AS] = BaseASCls
        self.GraphCls: Type[BGPDAG] = GraphCls
        self.cache_dir: Path = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        fmt: str = "%Y.%m.%d"
        self.cache_path: Path = self.cache_dir / self.dl_time.strftime(fmt)

    def run(self, cache: bool = True, tsv: bool = True) -> BGPDAG:
        """Downloads relationships, parses data, and inserts into the db.

        https://publicdata.caida.org/datasets/as-relationships/serial-2/

        Can specify a download time if you want to download an older dataset
        if cache is True it uses the downloaded file that was cached
        """

        file_lines: List[str] = self.read_file(cache)
        cp_links, peer_links, ixps, input_clique = self._get_ases(file_lines)
        bgp_dag: BGPDAG = self.GraphCls(cp_links,
                                        peer_links,
                                        ixps=ixps,
                                        input_clique=input_clique,
                                        BaseASCls=self.BaseASCls)
        if tsv:
            self._write_tsv(bgp_dag)
        return bgp_dag

    def default_dl_time(self) -> datetime:
        """Returns default DL time.

        For most things, we download from 4 days ago
        And for collectors, time must be divisible by 4/8
        """

        # 10 days because sometimes caida takes a while to upload
        # 7 days ago was actually not enough
        dl_time: datetime = datetime.utcnow() - timedelta(days=10)
        return dl_time.replace(hour=0, minute=0, second=0, microsecond=0)

    def _write_tsv(self, dag: BGPDAG):
        """Writes BGP DAG info to a TSV"""

        logging.info("Made graph. Now writing to TSV")
        with self.tsv_path.open(mode="w") as f:
            # Get columns
            cols: List[str] = list(next(iter(dag.as_dict.values())
                                        ).db_row.keys())
            writer = DictWriter(f, fieldnames=cols, delimiter="\t")
            writer.writeheader()
            for x in dag.as_dict.values():
                writer.writerow(x.db_row)
        logging.debug("Wrote TSV")
