from tqdm import tqdm

from .base_as import AS


class BGPDAG:
    """BGP Topology from caida which is a DAG"""

    # Slots are used here to allow for fast access (1/3 faster)
    # And also because it allows others to easily see the instance attrs
    __slots__ = ["as_dict", "propagation_ranks"]

    def __init__(self,
                 cp_links: set,
                 peer_links: set,
                 ixps=set(),
                 input_clique=set(),
                 BaseASCls=AS,
                 ):
        """Reads in relationship data from a TSV and generate graph"""

        self.as_dict = dict()
        print("gen graph")
        # Just adds all ASes to the dict, and adds ixp/input_clique info
        self._gen_graph(cp_links, peer_links, ixps, input_clique, BaseASCls)
        print("gen graph done")
        # Adds references to all relationships
        self._add_relationships(cp_links, peer_links)
        print("add rels done")
        # Remove duplicates from relationships and sort
        self._make_relationships_tuples()
        print("typles done")
        # Assign propagation rank to each AS
        self._assign_propagation_ranks()
        print("assigned prop ranks")
        # Get the ranks for the graph
        self.propagation_ranks = self._get_propagation_ranks()
        print("got prop ranks")
        self._get_customer_cone_size()

    def _gen_graph(self, cp_links, peer_links, ixps, input_clique, BaseAsCls):
        """Generates a graph of AS objects"""

        msg = "Shouldn't have a customer-provider that is also a peer!"
        assert len(cp_links) + len(peer_links) == len(cp_links | peer_links), msg

        # Add all links to the graph. Sorted for deterministicness
        for link in (cp_links | peer_links):
            for asn in link.asns:
                self.as_dict[asn] = self.as_dict.get(asn, BaseAsCls(asn))

        # Add all IXPs to the graph. Sorted for deterministicness
        for asn in (ixps):
            self.as_dict[asn] = self.as_dict.get(asn, BaseAsCls(asn))
            self.as_dict[asn].ixp = True

        # Add all input cliques to the graph. Sorted for deterministicness
        for asn in (input_clique):
            self.as_dict[asn] = self.as_dict.get(asn, BaseAsCls(asn))
            self.as_dict[asn].input_clique = True

    def _add_relationships(self, cp_links, peer_links):
        """Adds relationships to the graph as references"""

        # Sorted for deterministicness
        for cp_link in (cp_links):
            # Extract customer and provider obj
            customer = self.as_dict[cp_link.customer_asn]
            provider = self.as_dict[cp_link.provider_asn]
            # Store references
            customer.providers.add(provider)
            provider.customers.add(customer)

        # Sorted to preserve deterministic
        for peer_link in (peer_links):
            # Extract as objects for peers
            asn1, asn2 = peer_link.asns
            p1, p2 = self.as_dict[asn1], self.as_dict[asn2]
            # Add references to peers
            p1.peers.add(p2)
            p2.peers.add(p1)

    def _make_relationships_tuples(self):
        """Make relationships tuples"""
        
        for as_obj in tqdm(self.as_dict.values(), total=len(self.as_dict)):
            for rels in ["peers", "customers", "providers"]:
                setattr(as_obj, rels, tuple(getattr(as_obj, rels)))

    def _assign_propagation_ranks(self):
        """Assigns propagation ranks from the leafs to input_clique"""

        for as_obj in self.as_dict.values():
            self._assign_ranks_helper(as_obj, 0)

    def _assign_ranks_helper(self, as_obj, rank):
        """Assigns ranks to all ases in customer/provider chain recursively"""

        if as_obj.propagation_rank is None or as_obj.propagation_rank < rank:
            as_obj.propagation_rank = rank
            # Only update it's providers if it's rank becomes higher
            # This avoids a double for loop of writes
            for provider_obj in as_obj.providers:
                self._assign_ranks_helper(provider_obj, rank + 1)

    def _get_propagation_ranks(self):
        """Orders ASes by rank"""

        max_rank = max(x.propagation_rank for x in self.as_dict.values())
        # Create a list of empty lists
        ranks = list(list() for _ in range(max_rank + 1))
        # Append the ASes into their proper rank
        for as_obj in self.as_dict.values():
            ranks[as_obj.propagation_rank].append(as_obj)
        # Sort the ASes for deterministic
        for i, rank in enumerate(ranks):
            ranks[i] = tuple(sorted(rank))
        # Tuples are faster
        return tuple(ranks)

    def _get_customer_cone_size(self):
        """Gets the AS rank by customer cone, the same way Caida does it"""

        # Recursively assign the customer cone size
        for as_obj in self.as_dict.values():
            self._get_cone_size_helper(as_obj)

    def _get_cone_size_helper(self, as_obj):
        """Recursively determines the cone size of an as"""

        # Put here just to avoid repeating
        if as_obj.customer_cone_size is not None:
            return
        else:
            agg_cone_size = 0
            for customer in as_obj.customers:
                if customer.customer_cone_size is None:
                    self._get_cone_size_helper(customer)
                agg_cone_size += customer.customer_cone_size
            as_obj.customer_cone_size = agg_cone_size

######################
### Iterator funcs ###
######################

# https://stackoverflow.com/a/7542261/8903959
# Way too slow to use, can't do a list of all values at scale
#    def __getitem__(self, index):
#        return list(self.as_dict.values())[index]

    def __len__(self):
        return len(self.as_dict)
