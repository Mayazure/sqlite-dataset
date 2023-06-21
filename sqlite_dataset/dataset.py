import inspect
import os
import warnings
from collections import OrderedDict

from sqlalchemy import MetaData, Table, insert, Column, select, text

from sqlite_dataset.fields import Field, DataTable
from sqlite_dataset.utils import create_sqlite_db_engine


def _get_fields_by_mro(klass):
    mro = inspect.getmro(klass)
    return sum(
        (
            _get_fields(
                getattr(base, "_declared_fields", base.__dict__)
            )
            for base in mro[:0:-1]
        ),
        [],
    )


def is_class(val, klass):
    try:
        return issubclass(val, klass)
    except TypeError:
        return isinstance(val, klass)


def is_field_class(val):
    return is_class(val, Field)


def is_table_class(val):
    return is_class(val, DataTable)


def _get_fields(attrs):
    fields = [
        (field_name, field_value)
        for field_name, field_value in attrs.items()
        if is_field_class(field_value)
    ]
    return fields


def _get_table_fields(attrs):
    table_fields = []
    for table_name, table_value in attrs.items():
        if is_table_class(table_value):
            use_tablename = table_value.tablename or table_name
            for (field_name, field_value) in table_value.fields:
                field_value.tablename = use_tablename
                if field_value.name is None:
                    field_value.name = field_name
                table_fields.append((f'{table_name}_{field_name}', field_value))
    return table_fields


class DatasetMeta(type):

    def __new__(mcs, name, bases, attrs):
        __defaulttable__ = attrs.get('__defaulttable__', 'data')
        cls_fields = _get_fields(attrs)
        table_fields = _get_table_fields(attrs)
        for field_name, field_col in cls_fields:
            if field_col.tablename is None:
                field_col.tablename = __defaulttable__
            del attrs[field_name]
        klass = super().__new__(mcs, name, bases, attrs)
        inherited_fields = _get_fields_by_mro(klass)
        klass._declared_fields = mcs.get_declared_fields(
            cls_fields=[*cls_fields, *table_fields],
            inherited_fields=inherited_fields,
        )
        return klass

    @classmethod
    def get_declared_fields(
            mcs,
            cls_fields: list,
            inherited_fields: list
    ):
        return OrderedDict(inherited_fields + cls_fields)


class SQLiteDataset(object, metaclass=DatasetMeta):

    def __init__(self, db_path):
        self.db_path = db_path
        self.engine = create_sqlite_db_engine(db_path)
        self.metadata = MetaData()
        self.schema = {}

        if self._declared_fields:
            for name, field in self._declared_fields.items():
                if not self.schema.get(field.tablename):
                    self.schema[field.tablename] = []
                self.schema[field.tablename].append(field.new_column(name=name))
            self.add_tables(self.schema)
            if not os.path.exists(self.db_path):
                self.build()
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
            Table(name, self.metadata, *cols)

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
