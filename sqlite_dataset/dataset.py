import abc
import os.path
import warnings

from sqlalchemy import MetaData, Table, insert, Column, String, Integer

from sqlite_dataset.utils import create_sqlite_db_engine


class SQLiteDataset(object):

    schema = None

    @classmethod
    def create(cls, db_path, tables: dict[str, list[Column]]):
        db = cls(db_path)
        db.build()
        db.add_tables(tables)
        return db

    def __init__(self, db_path):
        self.db_path = db_path
        self.engine = create_sqlite_db_engine(db_path)
        self.metadata = MetaData()
        self.db_connection = None

    @property
    def connection(self):
        if self.db_connection is None:
            raise ValueError('Dataset not connected.')
        return self.db_connection

    @connection.setter
    def connection(self, value):
        # FIXME validate connection
        if self.db_connection is not None:
            # raise ValueError('Connection is not None')
            pass
        self.db_connection = value

    @abc.abstractmethod
    def tables(self):
        pass

    def build(self):
        self.metadata.create_all(self.engine)

    def connect(self):
        if not os.path.exists(self.db_path):
            warnings.warn('Dataset does not exist. To to create a dataset, use "create(db_path)".')
        self.metadata.reflect(bind=self.engine)
        self.connection = self.engine.connect()

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_table(self, name: str):
        return self.metadata.tables[name]

    def add_tables(self, tables: dict[str, list[Column]]):
        for name, cols in tables.items():
            Table(name, self.metadata, *cols)
        self.build()

    def add_table(self, name, cols):
        self.add_tables({name: cols})

    def get_column(self, table: str, col: str):
        return getattr(self.metadata.tables[table].c, col)

    def add_many(self, entity, records):
        stmt = insert(self.get_table(entity))
        self.connection.execute(stmt, records)
        self.connection.commit()

    def read_table(self, table, cols=None, chunk=None, limit=None, **args):
        pass

    def head(self, table, limit):
        self.read_table(table, limit=limit)


if __name__ == '__main__':
    # ds = SQLiteDataset.create('test.db', {'my_table': [Column('name', String)]})
    # with SQLiteDataset('test.db') as ds:
    #     ds.add_many('my_table', [{'name': 'user1'}])
    # ds = SQLiteDataset('test.db')
    # ds.connect()
    # ds.add_many('my_table', [{'name': 'user2'}])
    # ds.close()
    import pandas as pd
    with SQLiteDataset('test.db') as ds:
        df = pd.read_sql(
            ds.get_table('my_table').select(),
            ds.connection
        )
        print(df)

    # ds = SQLiteDataset.create(
    #     'test.db',
    #     {'my_table': [
    #         Column('name', String),
    #         Column('age', Integer)
    #     ]}
    # )
    # ds.connect()
    # ds.add_many('my_table', [{'name': 'user1', 'age': 25},{'name': 'user2', 'age': 26},{'name': 'user3', 'age': 27}])
    # ds.close()