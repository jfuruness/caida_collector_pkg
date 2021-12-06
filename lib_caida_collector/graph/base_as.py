from typing import Any, List, Optional, Tuple, TYPE_CHECKING

from yamlable import yaml_info, YamlAble, yaml_info_decorate



@yaml_info(yaml_tag='AS')
class AS(YamlAble):
    """Autonomous System class. Contains attributes of an AS"""

    __slots__ = ["asn", "peers", "customers", "providers", "input_clique",
                 "ixp", "customer_cone_size", "propagation_rank"]

    subclass_to_name_dict: dict = {}
    name_to_subclass_dict: dict = {}

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to easily assign yaml tags
        """

        super().__init_subclass__(*args, **kwargs)
        yaml_info_decorate(cls, yaml_tag=cls.__name__)
        cls.subclass_to_name_dict[cls] = cls.__name__
        cls.name_to_subclass_dict[cls.__name__] = cls

    def __init__(self,
                 asn: Optional[int] = None,
                 input_clique: bool = False,
                 ixp: bool = False,
                 peers=None,
                 providers=None,
                 customers=None,
                 customer_cone_size: Optional[int] = None,
                 propagation_rank: Optional[int] = None):

        assert isinstance(asn, int), asn
        self.asn: Optional[int] = asn
        # FOR DEVS: These are sets initially for speed
        # But are later changed to tuples for immutability
        # I'll fix that weirdness later
        self.peers = peers if peers is not None else set()
        self.customers = customers if customers is not None else set()
        self.providers = providers if providers is not None else set()
        # Read Caida's paper to understand these
        self.input_clique: bool = input_clique
        self.ixp: bool = ixp
        self.customer_cone_size: Optional[int] = customer_cone_size
        # Propagation rank. Rank leaves to clique
        self.propagation_rank: Optional[int] = propagation_rank

    def __lt__(self, as_obj: Any):
        if isinstance(as_obj, AS):
            return self.asn < as_obj.asn
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.asn)

    @property
    def db_row(self) -> dict:
        def asns(as_objs: List["AS"]) -> str:
            return "{" + ",".join(str(x.asn) for x in sorted(as_objs)) + "}"

        def _format(x) -> str:
            if isinstance(x, list) or isinstance(x, tuple):
                return asns(x)
            elif x is None:
                return ""
            else:
                return x

        attrs = self.__slots__ + ["stubs", "stub", "multihomed", "transit"]
        return {attr: _format(getattr(self, attr)) for attr in attrs}

    @property
    def stub(self) -> bool:
        """Returns True if AS is a stub by RFC1772"""

        return len(self.neighbors) == 1

    @property
    def multihomed(self) -> bool:
        """Returns True if AS is multihomed by RFC1772"""

        return (len(self.customers) == 0
                and len(self.peers) + len(self.providers) > 1)

    @property
    def transit(self) -> bool:
        """Returns True if AS is a transit AS by RFC1772"""

        return len(self.customers) > 1

    @property
    def stubs(self) -> Tuple["AS"]:
        """Returns a list of any stubs connected to that AS"""

        return tuple([x for x in self.customers if x.stub])

    @property
    def neighbors(self):
        """Returns customers + peers + providers"""

        return self.customers + self.peers + self.providers

##############
# Yaml funcs #
##############

    def __to_yaml_dict__(self) -> dict:
        """ This optional method is called when you call yaml.dump()"""
        return {"asn": self.asn,
                "customers": [x.asn for x in self.customers],
                "peers": [x.asn for x in self.peers],
                "providers": [x.asn for x in self.providers],
                "input_clique": self.input_clique,
                "ixp": self.ixp,
                "customer_cone_size": self.customer_cone_size,
                "propagation_rank": self.propagation_rank}

    @classmethod
    def __from_yaml_dict__(cls, dct: dict, yaml_tag: str):
        """ This optional method is called when you call yaml.load()"""
        return cls(**dct)
