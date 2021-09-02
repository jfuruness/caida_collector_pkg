from .base_as import AS


class BGPDAG:
    """BGP Topology. Must be a DAG"""

    # Slots are used here to allow for fast access (1/3 faster)
    # And also because it allows others to easily see the instance attrs
    __slots__ = ["as_dict", "propogation_ranks"]

    def __init__(self,
                 cp_links: set,
                 peer_links: set,
                 ixps: set,
                 input_clique: set,
                 BaseASCls=AS,
                 ):
        """Reads in relationship data from a TSV and generate graph"""

        self.as_dict = dict()
        # Just adds all ASes to the dict, and adds ixp/input_clique info
        self._gen_graph(cp_links, peer_links, ixps, input_clique, BaseAsCls)
        # Adds references to all relationships
        self._add_relationships(cp_links, peer_links)
        # Remove duplicates from relationships and sort
        self._make_relationships_tuples()
        # self._assert_dag()
        # Assign propagation rank to each AS
        self._assign_propagation_ranks()
        # Get the ranks for the graph
        self.propagation_ranks = self._get_propagation_ranks()

    def _gen_graph(self, cp_links, peer_links, ixps, input_clique, BaseAsCls):
        """Generates a graph of AS objects"""

        msg = "Shouldn't have a customer-provider that is also a peer!"
        assert len(cp_links) + len(peer_links) == cp_links | peer_links, msg

        # Add all links to the graph. Sorted for deterministicness
        for link in sorted(cp_links | peer_links):
            for asn in link.asns:
                self.as_dict[asn] = self.as_dict.get(asn, BaseAsCls(asn))

        # Add all IXPs to the graph. Sorted for deterministicness
        for asn in sorted(ixps):
            self.as_dict[asn] = self.as_dict.get(asn, BaseAsCls(asn))
            self.as_dict[asn].ixp = True

        # Add all input cliques to the graph. Sorted for deterministicness
        for asn in sorted(input_clique):
            self.as_dict[asn] = self.as_dict.get(asn, BaseAsCls(asn))
            self.as_dict[asn].input_clique = True

    def _add_relationships(self, cp_links, peer_links):
        """Adds relationships to the graph as references"""

        # Sorted for deterministicness
        for cp_link in sorted(cp_links):
            # Extract customer and provider obj
            customer = self.as_dict[cp_link.customer_asn]
            provider = self.as_dict[cp_link.provider_asn]
            # Store references
            customer.providers.add(provider)
            provider.customers.add(customer)

        # Sorted to preserve deterministic
        for peer_link in sorted(peer_links):
            # Extract as objects for peers
            asn1, asn2 = peer_link.asns
            p1, p2 = self.as_dict[asn1], self.as_dict[asn2]
            # Add references to peers
            p1.peers.add(p2)
            p2.peers.add(p1)

    def _make_relationships_tuples(self):
        """Make relationships tuples and sort to preserve deterministic"""
        
        for as_obj in self:
            for rels in ["peers", "customers", "providers"]:
                setattr(as_obj, rels, tuple(sorted(getattr(as_obj, rels)))

    def _assert_dag(self):
        """Asserts that graph is a DAG for provider customers"""

        # I know it could be done with dynamic programming. idc.
        for asn, as_obj in self.as_dict.items():
            # Make sure there are no provider or provider loops
            for attr in ["customers", "providers"]:
                self._assert_dag_helper(as_obj, set([as_obj.asn]), attr)
            

    def _assert_dag_helper(self, og_as_obj, set_of_asns: set, attr: str):
        """Recursive func to make sure there are no cycles"""

        for as_obj in getattr(og_as_obj, attr):
            # Make sure we aren't cycling
            assert as_obj.asn not in set_of_asns, "Not a DAG"
            # Make a new set and add the current AS object to it
            temp_set_of_asns = set_of_asns.copy()
            temp_set_of_asns.add(as_obj.asn)
            # Continue recursively searching
            self._assert_dag_helper(as_obj, temp_set_of_asns, attr)

    def _assign_propagation_ranks(self):
        """Assigns propagation ranks from the leafs to input_clique"""

        for as_obj in self:
            self._assign_ranks_helper(as_obj, 0)

    def _assign_ranks_helper(self, as_obj, rank):
        """Assigns ranks to all ases in customer/provider chain recursively"""

        if as_obj.rank is None or as_obj.rank < rank:
            as_obj.rank = rank
            # Only update it's providers if it's rank becomes higher
            # This avoids a double for loop of writes
            for provider_obj in as_obj.providers:
                self._assign_ranks_helper(provider_obj, rank + 1)

    def _get_propagation_ranks(self):
        """Orders ASes by rank"""

        max_rank = max(x.propagation_rank for x in self)
        # Create a list of empty lists
        ranks = list(list() for _ in range(max_rank + 1))
        # Append the ASes into their proper rank
        for as_obj in self:
            ranks[as_obj.rank].append(as_obj)
        # Sort the ASes for deterministic
        for i, rank in enumerate(ranks):
            ranks[i] = tuple(sorted(rank))
        # Tuples are faster
        return tuple(ranks)

######################
### Iterator funcs ###
######################

    # https://stackoverflow.com/a/7542261/8903959
    def __getitem__(self, index):
        return list(self.as_dict.values())[index]

    def __len__(self):
        return len(self.as_dict)
