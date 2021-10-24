from yamlable import yaml_info, YamlAble, yaml_info_decorate


@yaml_info(yaml_tag='AS')
class AS(YamlAble):
    """Autonomous System class. Contains attributes of an AS"""

    __slots__ = ["asn", "peers", "customers", "providers", "input_clique",
                 "ixp", "customer_cone_size", "propagation_rank"]

    subclass_to_name_dict = {}
    name_to_subclass_dict = {}

    def __init_subclass__(cls, *args, **kwargs):
        """This method essentially creates a list of all subclasses
        This is allows us to easily assign yaml tags
        """

        super().__init_subclass__(*args, **kwargs)
        # Fix this later once the system test framework is updated
        #cls.yaml_tag = f"!{cls.__name__}"
        yaml_info_decorate(cls, yaml_tag=cls.__name__)
        cls.subclass_to_name_dict[cls] = cls.__name__
        cls.name_to_subclass_dict[cls.__name__] = cls

    def __init__(self,
                 asn: int = None,
                 input_clique=False,
                 ixp=False,
                 peers=None,
                 providers=None,
                 customers=None,
                 customer_cone_size=None,
                 propagation_rank=None):

        assert isinstance(asn, int), asn
        self.asn = asn
        self.peers = peers if peers is not None else set()
        self.customers = customers if customers is not None else set()
        self.providers = providers if providers is not None else set()
        # Read Caida's paper to understand these
        self.input_clique = input_clique
        self.ixp = ixp
        self.customer_cone_size = customer_cone_size
        # Propagation rank. Rank leaves to clique
        self.propagation_rank = propagation_rank

    def __lt__(self, as_obj):
        if isinstance(as_obj, AS):
            return self.asn < as_obj.asn
        else:
            raise NotImplementedError

    def __hash__(self):
        return hash(self.asn)

    @property
    def db_row(self):
        def asns(as_objs: list):
            return "{" + ",".join(str(x.asn) for x in sorted(as_objs)) + "}"

        def _format(x):
            if isinstance(x, list) or isinstance(x, tuple):
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

    @property
    def neighbors(self):
        """Returns customers + peers + providers"""

        return self.customers + self.peers + self.providers

##############
# Yaml funcs #
##############

    def __to_yaml_dict__(self):
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
    def __from_yaml_dict__(cls, dct, yaml_tag):
        """ This optional method is called when you call yaml.load()"""
        return cls(**dct)
