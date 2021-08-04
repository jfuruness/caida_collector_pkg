class AS:
    """Autonomous System class. Contains attributes of an AS"""

    def __init__(self, asn, input_clique=False, ixp=False):
        self.asn = asn
        self.peers = set()
        self.customers = set()
        self.providers = set()
        # Read Caida's paper to understand these
        self.input_clique = input_clique
        self.ixp = ixp

    def __lt__(self, as_obj):
        if isinstance(as_obj, AS):
            return True if self.asn < as_obj.asn else False
            

    @property
    def db_row(self):
        def asns(as_objs: list):
            return "{" + ",".join(str(x.asn) for x in sorted(as_objs)) + "}"

        return {"asn": self.asn,
                "peers": asns(self.peers),
                "customers": asns(self.customers),
                "providers": asns(self.providers),
                "stubs": asns(self.stubs),
                "stub": self.stub,
                "multihomed": self.multihomed,
                "transit": self.transit,
                "input_clique": self.input_clique,
                "ixp": self.ixp}

    @property
    def stub(self):
        """Returns True if AS is a stub by RFC1772"""

        if len(self.peers) + len(self.customers) + len(providers) == 1:
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
