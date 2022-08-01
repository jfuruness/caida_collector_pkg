from typing import Any, Dict, List, Optional, Set
from typing import Tuple, Type, TYPE_CHECKING, Union

from yamlable import yaml_info, YamlAble, yaml_info_decorate

if TYPE_CHECKING:
    from .base_as import AS as ASTypeHint
else:
    ASTypeHint = "AS"

SETUP_REL = Optional[Set[ASTypeHint]]
REL = Tuple[ASTypeHint, ...]

SLOTS = ("asn", "peers", "customers", "providers", "input_clique",
         "ixp", "customer_cone_size", "propagation_rank")


@yaml_info(yaml_tag='AS')
class AS(YamlAble):
    """Autonomous System class. Contains attributes of an AS"""

    __slots__ = SLOTS

    subclass_to_name_dict: Dict[Type[ASTypeHint], str] = {}
    name_to_subclass_dict: Dict[str, Type[ASTypeHint]] = {}

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
                 peers_setup_set: SETUP_REL = None,
                 providers_setup_set: SETUP_REL = None,
                 customers_setup_set: SETUP_REL = None,
                 peers: REL = tuple(),
                 providers: REL = tuple(),
                 customers: REL = tuple(),
                 customer_cone_size: Optional[int] = None,
                 propagation_rank: Optional[int] = None):

        if isinstance(asn, int):
            self.asn: int = asn
        else:
            raise Exception("ASN must be int")

        # While setting up, use sets for speed
        self.peers_setup_set: SETUP_REL = peers_setup_set
        self.customers_setup_set: SETUP_REL = customers_setup_set
        self.providers_setup_set: SETUP_REL = providers_setup_set

        # Afterwards convert to tuples
        # Copy over to a new attr due to mypy and readability
        self.peers: REL = peers
        self.providers: REL = providers
        self.customers: REL = customers

        # Read Caida's paper to understand these
        self.input_clique: bool = input_clique
        self.ixp: bool = ixp
        self.customer_cone_size: Optional[int] = customer_cone_size
        # Propagation rank. Rank leaves to clique
        self.propagation_rank: Optional[int] = propagation_rank

    def __lt__(self, as_obj: Any) -> bool:
        if isinstance(as_obj, AS):
            return self.asn < as_obj.asn
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.asn)

    @property
    def db_row(self) -> Dict[str, str]:
        def asns(as_objs: Union[List[ASTypeHint], Tuple[ASTypeHint]]) -> str:
            return "{" + ",".join(str(x.asn) for x in sorted(as_objs)) + "}"

        def _format(x: Any) -> str:
            if ((isinstance(x, list) or isinstance(x, tuple))
                    and all([isinstance(y, AS) for y in x])):
                return asns(x)  # type: ignore
            elif x is None:
                return ""
            elif isinstance(x, str) or isinstance(x, int):
                return str(x)
            else:
                raise Exception(f"improper format type: {type(x)} {x}")

        attrs = SLOTS + ("stubs", "stub", "multihomed", "transit")
        return {attr: _format(getattr(self, attr)) for attr in attrs}

    def __str__(self):
        return "\n".join(str(x) for x in self.db_row.items())

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
    def stubs(self) -> Tuple[ASTypeHint, ...]:
        """Returns a list of any stubs connected to that AS"""

        return tuple([x for x in self.customers if x.stub])

    @property
    def neighbors(self) -> Tuple[ASTypeHint, ...]:
        """Returns customers + peers + providers"""

        return self.customers + self.peers + self.providers

##############
# Yaml funcs #
##############

    def __to_yaml_dict__(self) -> Dict[str, Any]:
        """ This optional method is called when you call yaml.dump()"""
        return {"asn": self.asn,
                "customers": tuple([x.asn for x in self.customers]),
                "peers": tuple([x.asn for x in self.peers]),
                "providers": tuple([x.asn for x in self.providers]),
                "input_clique": self.input_clique,
                "ixp": self.ixp,
                "customer_cone_size": self.customer_cone_size,
                "propagation_rank": self.propagation_rank}

    @classmethod
    def __from_yaml_dict__(cls, dct: Dict[Any, Any], yaml_tag: str):
        """ This optional method is called when you call yaml.load()"""
        return cls(**dct)


# Needed for mypy type hinting
__all__ = ["AS"]
