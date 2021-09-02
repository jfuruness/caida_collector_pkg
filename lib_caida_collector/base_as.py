class AS:
    """Autonomous System class. Contains attributes of an AS"""

    __slots__ = ["asn", "peers", "customers", "providers", "input_clique",
                 "ixp", "as_rank", "propagation_rank"]

    def __init__(self, asn, input_clique=False, ixp=False):
        self.asn = asn
        self.peers = set()
        self.customers = set()
        self.providers = set()
        # Read Caida's paper to understand these
        self.input_clique = input_clique
        self.ixp = ixp
        # AS Rank from caida AS rank querier
        self.as_rank = None
        # Propagation rank. Rank leaves to clique
        self.propagation_rank = None

    def __lt__(self, as_obj):
        if isinstance(as_obj, AS):
            return True if self.asn < as_obj.asn else False
        else:
            raise NotImplementedError

    def __hash__(self):
        return hash(self.asn)

    @property
    def db_row(self):
        def asns(as_objs: list):
            return "{" + ",".join(str(x.asn) for x in sorted(as_objs)) + "}"

        def _format(x):
            if isinstance(x, list):
                return asns(x)
            elif x is None:
                return ""
            else:
                return x

        attrs = self.__slots__ + ["stubs", "stub", "multihomed", "transit"]
        return {attr: _format(getattr(self, attr)) for attr in attrs}

    @property
    def stub(self):
        """Returns True if AS is a stub by RFC1772"""

        if len(self.peers) + len(self.customers) + len(self.providers) == 1:
            return True
        else:
            return False

    @property
    def multihomed(self):
        """Returns True if AS is multihomed by RFC1772"""

        if (len(self.customers) == 0
                and len(self.peers) + len(self.providers) > 1):
            return True
        else:
            return False

    @property
    def transit(self):
        """Returns True if AS is a transit AS by RFC1772"""

        return True if len(self.customers) > 1 else False

    @property
    def stubs(self):
        """Returns a list of any stubs connected to that AS"""

        return [x for x in self.customers if x.stub]
