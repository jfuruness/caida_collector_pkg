from .link import Link


class CustomerProviderLink(Link):
    """Stores the customer and provider information"""

    def __init__(self, **kwargs):
        """Saves the link info

        done using kwargs so that it errors if it's not passed in
        """

        for kwarg in ["customer_asn", "provider_asn"]:
            assert kwarg in kwargs, f"Params missing {kwarg}"

        self.__customer_asn = int(kwargs["customer_asn"])
        self.__provider_asn = int(kwargs["provider_asn"])
        super(CustomerProviderLink, self).__init__()

    @property
    def customer_asn(self):
        """Returns customer asn. Done this way for immutability/hashing"""

        return self.__customer_asn

    @property
    def provider_asn(self):
        """Returns provider asn. Done this way for immutability/hashing"""

        return self.__provider_asn

    @property
    def asns(self):
        """Returns asns associated with this link. Used for hashing"""

        return tuple(sorted([self.customer_asn, self.provider_asn]))
