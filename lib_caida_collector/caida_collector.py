import bz2

from lib_utils import file_funcs, helper_funcs

from .as_class import AS


class CaidaCollector:
    """Downloads relationships, determines metadata, and inserts to db"""

    

    def run(self, url=None):
        """Downloads relationships, parses data, and inserts into the db.

        https://publicdata.caida.org/datasets/as-relationships/serial-2/

        Can specify a URL if you want to download an older dataset
        """

        url = url if url else self._get_url()
        file_lines = self._read_file(url)
        ases = self._get_ases(file_lines)
        self._assign_ranks(ases)

    def _get_url(self):
        """Gets urls to download relationship files"""

        # Api url
        prepend = 'http://data.caida.org/datasets/as-relationships/serial-2/'
        # Get all html tags that might have links, and return the third to last
        return prepend + helper_funcs.get_tags(prepend, 'a')[-3]["href"]

    def _read_file(self, url) -> list:
        """Reads the file from the URL and unzips it and returns the lines"""

        # Delete path, and delete again when out of scope
        with file_funcs.temp_path(path_append=".bz2") as path:
            file_funcs.download_file(url, path)
            # Unzip and read
            with bz2.open(path) as f:
                # Decode bytes into str
                return [x.decode() for x in f.readlines()]

    def _get_ases(self, lines):
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
            else:
                raise Exception("More lines than expected?")

    def _extract_input_clique(self, line, ases):
        """Adds all ASNs within input clique line to ases dict"""

        # Gets all input ASes for clique
        for asn in line.split(":")[-1].strip().split(" "):
            # This AS should not be in the graph already
            # Since this is the first line of real input
            assert int(asn) not in ases
            # Insert AS into graph
            ases[int(asn)] = AS(int(asn), input_clique=True)

    def _extract_ixp_ases(line, ases):
        """Adds all ASNs that are detected IXPs to ASes dict"""

        # Get all IXPs that Caida lists
        for asn in line.split(":")[-1].strip().split(" "):
            # Ensure that the ASN is not in the graph alrady
            # Since this is the second line of real input
            # And no IXPs are in the top clique (first line of input)
            assert int(asn) not in ases
            # Insert IXP
            ases[int(asn)] = AS(int(asn), ixp=True)

    def _extract_provider_customers(self, line, ases):
        """Extracts provider customers: <provider-as>|<customer-as>|-1"""

        provider_asn, customer_asn, _ = line.split("|")
        provider_asn, customer_asn = int(provider_asn), int(customer_asn)

        # Insert ASes if they do not exist
        if provider_asn not in ases:
            ases[provider_asn] = AS(provider_asn)
        if customer_asn not in ases:
            ases[customer_asn] = AS(customer_asn)

        # Add relationships
        ases[provider_asn].customers.add(ases[customer_asn])
        ases[customer_asn].providers.add(ases[provider_asn])

    def _extract_peers(self, line, ases):
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

    def assign_ranks(self, ases):
        """Caida always publishes a DAG, for which we can assign ranks to

        If we did not assign ranks, we would not have a good order
        in which to choose announcements to propogate. We'd need a
        state machine, where every announcement propogates on it's own,
        until the graph does not change.
        Instead, we can propogate everything at once, only once. Because
        we can start at the lowest ASNs, and propogate up, sideways, and down
        To do this we assign ranks, starting from the bottom
        """

        stubs = [x for x in ases if x.stub]
        for stub in stubs:
            self._assign_ranks_helper(stub, 0)

    def _assign_ranks_helper(self, as_obj: AS, rank):
        if as_obj.rank < rank:
            as_obj.rank = rank
            for provider in as_obj.providers:
                self._assign_ranks_helper(provider, rank + 1)
