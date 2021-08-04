class Relationships_Table(Generic_Table):
    name = "as_data"
    columns = ["asn", "peers", "customers", "providers", "stubs", "stub",
                "multihomed", "as_type"]

    def _create_tables(self):
        sql = f"""CREATE UNLOGGED TABLE IF NOT EXISTS {self.name}(
              asn BIGINT,
              peers BIGINT[],
              customers BIGINT[],
              providers BIGINT[],
              stubs BIGINT[],
              stub BOOLEAN,
              multihomed BOOLEAN,
              as_type SMALLINT);"""
        self.execute(sql)


    def fill_table(self):
        class AS:
            def __init__(self, asn):
                self.asn = asn
                self.peers = set()
                self.customers = set()
                self.providers = set()
                self.as_type = 0

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
                        self.as_type]

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

        with ASes_Table() as db:
            ases_rows = db.get_all()

        with Peers_Table() as db:
            peers_rows = db.get_all()

        with Provider_Customers_Table() as db:
            provider_customers_rows = db.get_all()

        ases = set([x["asn"] for x in ases_rows])
        ases = {x: AS(x) for x in ases}
        for peer_row in peers_rows:
            p1, p2 = (peer_row["peer_as_1"], peer_row["peer_as_2"])
            ases[p1].peers.add(ases[p2])
            ases[p2].peers.add(ases[p1])

        for provider_customers_row in provider_customers_rows:
            customer = provider_customers_row["customer_as"]
            provider = provider_customers_row["provider_as"]
            ases[customer].providers.add(ases[provider])
            ases[provider].customers.add(ases[customer])

        rows = [x.db_row for x in ases.values()]
        utils.rows_to_db(rows, "/tmp/relationship.csv", Relationships_Table)
