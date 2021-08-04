class ASesTable(GenericTable):
    name = "ases"
    id_col = None

    def create_table(self):
        sql = """CREATE UNLOGGED TABLE {self.name}(
              asn BIGINT UNIQUE,
              peers BIGINT[],
              customers BIGINT[],
              providers BIGINT[],
              stubs BIGINT[],
              stub BOOLEAN,
              multihomed BOOLEAN,
              transit BOOLEAN,
              input_clique BOOLEAN,
              ixp BOOLEAN);"""
        self.execute(sql)
