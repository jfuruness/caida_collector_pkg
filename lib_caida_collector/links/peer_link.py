from .link import Link


class PeerLink(Link):
    """Stores the info for a peer link"""

    def __init__(self, peer1_asn, peer2_asn):
        """Saves the link info"""

        self.__peer_asns = tuple(sorted([int(peer1_asn), int(peer2_asn)]))
        super(PeerLink, self).__init__()

    @property
    def peer_asns(self):
        """Returns peer asns. Done this way for immutability/hashing"""

        return self.__peer_asns

    @property
    def asns(self):
        """Returns asns associated with this link"""

        return tuple(sorted(self.peer_asns))
