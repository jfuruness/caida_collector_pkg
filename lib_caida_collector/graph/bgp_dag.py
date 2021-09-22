import logging

from .base_as import AS


class BGPDAG:
    """BGP Topology from caida which is a DAG"""

    # Slots are used here to allow for fast access (1/3 faster)
    # And also because it allows others to easily see the instance attrs
    __slots__ = ["as_dict", "propagation_ranks", "ases"]

    def __init__(self,
                 cp_links: set,
                 peer_links: set,
                 ixps=set(),
                 input_clique=set(),
                 BaseASCls=AS,
                 ):
        """Reads in relationship data from a TSV and generate graph"""

        self.as_dict = dict()
        logging.debug("gen graph")
        # Just adds all ASes to the dict, and adds ixp/input_clique info
        self._gen_graph(cp_links, peer_links, ixps, input_clique, BaseASCls)
        logging.debug("gen graph done")
        # Adds references to all relationships
        self._add_relationships(cp_links, peer_links)
        # Used for iteration
        self.ases = list(self.as_dict.values())
        logging.debug("add rels done")
        # Remove duplicates from relationships and sort
        self._make_relationships_tuples()
        logging.debug("typles done")
        # Assign propagation rank to each AS
        self._assign_propagation_ranks()
        logging.debug("assigned prop ranks")
        # Get the ranks for the graph
        self.propagation_ranks = self._get_propagation_ranks()
        logging.debug("got prop ranks")
        # Determine customer cones of all ases
        self._get_customer_cone_size()
        logging.debug("Customer cones complete")


    # Graph building functionality
    from .graph_building_funcs import _gen_graph
    from .graph_building_funcs import _add_relationships
    from .graph_building_funcs import _make_relationships_tuples

    # propagation rank building funcs
    from .propagation_rank_funcs import _assign_propagation_ranks
    from .propagation_rank_funcs import _assign_ranks_helper
    from .propagation_rank_funcs import _get_propagation_ranks

    # Customer cone funcs
    from .customer_cone_funcs import _get_customer_cone_size
    from .customer_cone_funcs import _get_cone_size_helper
    
##################
# Iterator funcs #
##################

    # https://stackoverflow.com/a/7542261/8903959
    def __getitem__(self, index):
        return self.ases[index]

    def __len__(self):
        return len(self.as_dict)