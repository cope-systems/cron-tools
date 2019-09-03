from psycopg2.extras import DictRow, DictCursor
from psycopg2.pool import ThreadedConnectionPool
import psycopg2
from six import string_types
from functools import wraps
from contextlib import contextmanager


class AlteredDictRow(DictRow):
    def __getitem__(self, item):
        if isinstance(item, string_types):
            return super(AlteredDictRow, self).__getitem__(item.lower())
        else:
            return super(AlteredDictRow, self).__getitem__(item)

    def get(self, x, default=None):
        if isinstance(x, string_types):
            return super(AlteredDictRow, self).get(x.lower(), default=default)
        else:
            return super(AlteredDictRow, self).get(x, default=default)


@contextmanager
def transaction_wrapper(connection):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("BEGIN TRANSACTION")
        yield connection
    except Exception:
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        if cursor:
            cursor.close()


@contextmanager
def cursor_manager(connection):
    cursor = None
    try:
        cursor = connection.cursor()
        yield cursor
    finally:
        if cursor:
            cursor.close()


@wraps(psycopg2.connect)
def create_pg_connection(*args, **kwargs):
    def cursor_factory(*cursor_args, **cursor_kwargs):
        cursor_kwargs['row_factory'] = AlteredDictRow
        return DictCursor(*cursor_args, **cursor_kwargs)

    kwargs.update(cursor_factory=cursor_factory)
    connection = psycopg2.connect(*args, **kwargs)
    return connection


@wraps(ThreadedConnectionPool)
def create_pg_connection_pool(*args, **kwargs):
    def cursor_factory(*cursor_args, **cursor_kwargs):
        cursor_kwargs['row_factory'] = AlteredDictRow
        return DictCursor(*cursor_args, **cursor_kwargs)

    kwargs.update(cursor_factory=cursor_factory)
    return ThreadedConnectionPool(*args, **kwargs)
