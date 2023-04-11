import copy
import os.path
import warnings

from sqlalchemy import MetaData, Table, insert, Column, select, text

from sqlite_dataset.utils import create_sqlite_db_engine


class SQLiteDataset(object):
    schema = None

    @classmethod
    def create(cls, db_path, schema=None):
        if cls.schema is None and schema is None:
            raise ValueError(
                'Schema not found. To create a dataset, either override the schema field or pass in a schema when '
                'calling create(db_path, schema=schema). To load an existing dataset without specifying schema, '
                'or create an empty dataset to use with pandas, instantiate SQLiteDataset(db_path) directly.'
            )
        db = cls(db_path, schema=schema)
        db.build()
        return db

    def __init__(self, db_path, schema=None):
        self.db_path = db_path
        self.engine = create_sqlite_db_engine(db_path)
        self.metadata = MetaData()
        if schema is not None:
            self.schema = schema
        if self.schema is not None:
            self.add_tables(self.schema)
        elif not os.path.exists(self.db_path):
            warnings.warn(
                'Database file does not exist. To to create a dataset, call create(db_path). '
                'Refer to documentation for more details.'
            )
        else:
            self.reflect()
        self.db_connection = None

    @property
    def connection(self):
        if self.db_connection is None:
            raise ValueError('Dataset not connected.')
        return self.db_connection

    @connection.setter
    def connection(self, value):
        if self.db_connection is not None and value is not None:
            warnings.warn('Overriding database connection.')
        self.db_connection = value

    def build(self):
        self.metadata.create_all(self.engine)

    def connect(self):
        self.connection = self.engine.connect()

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def reflect(self):
        self.metadata.reflect(bind=self.engine)

    def vacuum(self):
        self.connection.execute(text("vacuum"))

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_table(self, name: str):
        return self.metadata.tables[name]

    def add_table(self, name, cols):
        self.add_tables({name: cols})

    def add_tables(self, tables: dict[str, list[Column]]):
        for name, cols in tables.items():
            Table(name, self.metadata, *copy.deepcopy(cols))

    def delete_table(self, name: str):
        self.delete_tables([name])

    def delete_tables(self, tables: list[str]):
        for name in tables:
            self.get_table(name).drop(self.connection)
        self.connection.commit()

    def get_column(self, table: str, col: str):
        return getattr(self.metadata.tables[table].c, col)

    def insert_data(self, entity: str, records: list[dict]):
        stmt = insert(self.get_table(entity))
        self.connection.execute(stmt, records)
        self.connection.commit()

    def read_data(self, table, return_tuple=False, cols=None, chunk=None, limit=None):
        if cols:
            stmt = select(*[self.get_column(table, col) for col in cols])
        else:
            stmt = select(self.get_table(table))
        if type(limit) == int and limit > 0:
            stmt = stmt.limit(limit)

        if chunk:
            def iterator(chk, itr, rt=False):
                while data := itr.fetchmany(chk):
                    if rt:
                        yield [r.tuple() for r in data]
                    else:
                        yield [r._asdict() for r in data]
            return iterator(chunk, self.connection.execute(stmt), rt=return_tuple)
        else:
            res = self.connection.execute(stmt).fetchall()
            if return_tuple:
                return [r.tuple() for r in res]
            else:
                return [r._asdict() for r in res]
