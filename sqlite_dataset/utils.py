import sys

from sqlalchemy import create_engine, Engine, NullPool

if sys.platform.startswith('win'):
    uri_prefix = 'sqlite:///'
else:
    uri_prefix = 'sqlite:////'


def create_sqlite_db_engine(db_path: str) -> Engine:
    return create_engine(f'{uri_prefix}{db_path}', poolclass=NullPool)
