"""Gontains functions needed to build graph and it's references"""

from typing import Set, Type

from .base_as import AS
from ..links import CustomerProviderLink as CPLink
from ..links import PeerLink


def _gen_graph(self,
               cp_links: Set[CPLink],
               peer_links: Set[PeerLink],
               ixps: Set[int],
               input_clique: Set[int],
               BaseAsCls: Type[AS]):
    """Generates a graph of AS objects"""

    msg = "Shouldn't have a customer-provider that is also a peer!"
    assert len(cp_links) + len(peer_links) == len(cp_links | peer_links), msg

    def _gen_as(asn):
        return BaseAsCls(asn,
                         peers_setup_set=set(),
                         customers_setup_set=set(),
                         providers_setup_set=set())

    # Add all links to the graph
    for link in cp_links | peer_links:
        for asn in link.asns:
            self.as_dict[asn] = self.as_dict.get(asn, _gen_as(asn))

    # Add all IXPs to the graph
    for asn in ixps:
        self.as_dict[asn] = self.as_dict.get(asn, _gen_as(asn))
        self.as_dict[asn].ixp = True

    # Add all input cliques to the graph
    for asn in input_clique:
        self.as_dict[asn] = self.as_dict.get(asn, _gen_as(asn))
        self.as_dict[asn].input_clique = True


def _add_relationships(self,
                       cp_links: Set[CPLink],
                       peer_links: Set[PeerLink]):
    """Adds relationships to the graph as references"""

    for cp_link in cp_links:
        # Extract customer and provider obj
        customer = self.as_dict[cp_link.customer_asn]
        provider = self.as_dict[cp_link.provider_asn]
        # Store references
        customer.providers_setup_set.add(provider)
        provider.customers_setup_set.add(customer)

    for peer_link in peer_links:
        # Extract as objects for peers
        asn1, asn2 = peer_link.asns
        p1, p2 = self.as_dict[asn1], self.as_dict[asn2]
        # Add references to peers
        p1.peers_setup_set.add(p2)
        p2.peers_setup_set.add(p1)


def _make_relationships_tuples(self):
    """Make relationships tuples"""

    rel_attrs = ("peers", "customers", "providers")
    setup_rel_attrs = ("peers_setup_set",
                       "providers_setup_set",
                       "customers_setup_set")

    for as_obj in self:
        for rel_attr, setup_rel_attr in zip(rel_attrs, setup_rel_attrs):
            # Conver the setup attribute to tuple
            setattr(as_obj, rel_attr, tuple(getattr(as_obj, setup_rel_attr)))
            # Delete the setup attribute
            delattr(as_obj, setup_rel_attr)
