class Link:
    """Contains a relationship link in a BGP topology"""

    __slots__ = []

    def __init__(self):
        # Make sure we have asns
        # Make sure the asns is a tuple
        assert isinstance(self.asns, tuple)
        # Make sure the asns is sorted
        assert tuple(sorted(self.asns)) == self.asns

    def __hash__(self):
        """Hashes used in sets"""

        return hash(self.asns)

    def __lt__(self, other):
        if isinstance(other, Link):
            return self.__hash__() < other.__hash__()
        else:
            raise NotImplementedError
