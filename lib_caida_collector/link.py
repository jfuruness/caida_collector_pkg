class Link:
    """Contains a relationship link in a BGP topology"""

    def __init__(self):
        # Make sure we have asns
        assert hasattr(self, "asns")
        # Make sure the asns is a tuple
        assert isinstance(self.asns, tuple)
        # Make sure the asns is sorted
        assert tuple(sorted(self.asns)) == self.asns

    def __hash__(self):
        """Hashes used in sets"""

        return hash(self.asns)
