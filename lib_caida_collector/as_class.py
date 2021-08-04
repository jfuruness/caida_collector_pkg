from .policies import Policies

class AS:
    """Autonomous System class. Contains attributes of an AS"""

    def __init__(self, asn, input_clique=False, ixp=False):
        self.asn = asn
        self.peers = set()
        self.customers = set()
        self.providers = set()
        self.as_type = Policies.BGP
        # Read Caida's paper to understand these
        self.input_clique = input_clique
        self.ixp = ixp

    @property
    def db_row(self):
        def asns(as_objs: list):
            return "{" + ",".join(str(x.asn) for x in as_objs) + "}"

        return [self.asn,
                asns(self.peers),
                asns(self.customers),
                asns(self.providers),
                asns(self.stubs),
                self.stub,
                self.multihomed,
                self.as_type.value]

    @property
    def stub(self):
        if len(self.peers) == 0 and len(self.customers) == 0:
            return True
        else:
            return False

    @property
    def multihomed(self):
        if len(self.providers) > 1 and self.stub:
            return True
        else:
            return False

    @property
    def stubs(self):
        return [x for x in self.customers if x.stub]
