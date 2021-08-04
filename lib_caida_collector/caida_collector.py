import bz2
from typing import List, Dict

from lib_utils import file_funcs, helper_funcs

from .as_class import AS
from .tables import ASesTable


class CaidaCollector:
    """Downloads relationships, determines metadata, and inserts to db"""

    def run(self, url=None):
        """Downloads relationships, parses data, and inserts into the db.

        https://publicdata.caida.org/datasets/as-relationships/serial-2/

        Can specify a URL if you want to download an older dataset
        """

        url = url if url else self._get_url()
        file_lines = self._read_file(url)
        ases: List[AS] = self._get_ases(file_lines)
        # Insert into database
        with ASesTable(clear=True) as db:
            db.bulk_insert([x.db_row for x in ases])

    def _get_url(self) -> str:
        """Gets urls to download relationship files"""

        # Api url
        prepend = 'http://data.caida.org/datasets/as-relationships/serial-2/'
        # Get all html tags that might have links, and return the third to last
        return prepend + helper_funcs.get_tags(prepend, 'a')[-3]["href"]

    def _read_file(self, url: str) -> List[str]:
        """Reads the file from the URL and unzips it and returns the lines"""

        # Delete path, and delete again when out of scope
        with file_funcs.temp_path(path_append=".bz2") as path:
            file_funcs.download_file(url, path)
            # Unzip and read
            with bz2.open(path) as f:
                # Decode bytes into str
                return [x.decode().strip() for x in f.readlines()]

    def _get_ases(self, lines: List[str]) -> List[AS]:
        """Fills the initial AS dict and adds the following info:

        Creates AS dict with peers, providers, customers, input clique, ixps
        """

        ases = dict()
        for line in lines:
            # Get Caida input clique. See paper on site for what this is
            if line.startswith("# input clique"):
                self._extract_input_clique(line, ases)
            # Get detected Caida IXPs. See paper on site for what this is
            elif line.startswith("# IXP ASes"):
                self._extract_ixp_ases(line, ases)
            # Not a comment, must be a relationship
            elif not line.startswith("#"):
                # Extract all customer provider pairs
                if "-1" in line:
                    self._extract_provider_customers(line, ases)
                # Extract all peers
                else:
                    self._extract_peers(line, ases)
        return ases.values()

    def _extract_input_clique(self, line: str, ases: Dict[int, AS]):
        """Adds all ASNs within input clique line to ases dict"""

        # Gets all input ASes for clique
        for asn in line.split(":")[-1].strip().split(" "):
            # This AS should not be in the graph already
            # Since this is the first line of real input
            assert int(asn) not in ases
            # Insert AS into graph
            ases[int(asn)] = AS(int(asn), input_clique=True)

    def _extract_ixp_ases(self, line: str, ases: Dict[int, AS]):
        """Adds all ASNs that are detected IXPs to ASes dict"""

        # Get all IXPs that Caida lists
        for asn in line.split(":")[-1].strip().split(" "):
            # Ensure that the ASN is not in the graph alrady
            # Since this is the second line of real input
            # And no IXPs are in the top clique (first line of input)
            assert int(asn) not in ases
            # Insert IXP
            ases[int(asn)] = AS(int(asn), ixp=True)

    def _extract_provider_customers(self, line: str, ases: Dict[int, AS]):
        """Extracts provider customers: <provider-as>|<customer-as>|-1"""

        provider_asn, customer_asn, _, source = line.split("|")
        provider_asn, customer_asn = int(provider_asn), int(customer_asn)

        # Insert ASes if they do not exist
        if provider_asn not in ases:
            ases[provider_asn] = AS(provider_asn)
        if customer_asn not in ases:
            ases[customer_asn] = AS(customer_asn)

        # Add relationships
        ases[provider_asn].customers.add(ases[customer_asn])
        ases[customer_asn].providers.add(ases[provider_asn])

    def _extract_peers(self, line: str, ases: Dict[int, AS]):
        """Extracts peers: <peer-as>|<peer-as>|0|<source>"""

        peer1_asn, peer2_asn, _, source = line.split("|")
        peer_asn1, peer_asn2 = int(peer1_asn), int(peer2_asn)

        # Insert ASes if they do not exist
        for peer_asn in [peer_asn1, peer_asn2]:
            if peer_asn not in ases:
                ases[peer_asn] = AS(peer_asn)

        # Add relationships
        ases[peer_asn1].peers.add(ases[peer_asn2])
        ases[peer_asn2].peers.add(ases[peer_asn1])
