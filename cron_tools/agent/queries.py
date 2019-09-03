from sqlite3 import dbapi2 as sqlite
from sqlite3 import Row
from contextlib import contextmanager
import os
import json
import threading
import datetime
from functools import wraps

from cron_tools.common.models import AgentJob
from cron_tools.common.time import local_now, from_any_time_to_utc_seconds
from cron_tools.agent import SQL_DIR

with open(os.path.join(SQL_DIR, "schema.sql")) as f:
    AGENT_SCHEMA = f.read()


@wraps(sqlite.connect)
def create_connection(*args, **kwargs):
    conn = sqlite.connect(*args, **kwargs)
    conn.row_factory = Row
    conn.isolation_level = None
    return conn


class SimpleConnectionPool(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.pool = {}

    @property
    def thread_ident(self):
        return threading.current_thread().ident

    def get(self):
        if self.thread_ident in self.pool:
            return self.pool[self.thread_ident]
        else:
            self.pool[self.thread_ident] = conn = create_connection(*self.args, **self.kwargs)
            return conn

    def close(self):
        ident = self.thread_ident
        if ident in self.pool:
            self.pool[ident].close()
            del self.pool[ident]

    def close_all(self):
        for conn in self.pool.values():
            conn.close()
        self.pool = {}


@contextmanager
def cursor_manager(connection):
    cursor = connection.cursor()
    yield cursor
    cursor.close()


@contextmanager
def transaction_manager(connection):
    try:
        connection.execute("BEGIN TRANSACTION")
        yield connection
    except BaseException:
        connection.execute("ROLLBACK")
        raise
    else:
        connection.execute("COMMIT")


@contextmanager
def immediate_transaction_manager(connection):
    try:
        connection.execute("BEGIN IMMEDIATE TRANSACTION")
        yield connection
    except BaseException:
        connection.execute("ROLLBACK")
        raise
    else:
        connection.execute("COMMIT")


def write_schema(connection):
    connection.executescript(AGENT_SCHEMA)


def cleanup_db(connection):
    connection.execute("VACUUM")


def get_and_increment_counter(transaction, counter_name, default_value=0):
    with cursor_manager(transaction) as c:
        c.execute("SELECT counter_value FROM counter WHERE counter_name=?", (counter_name,))
        row = c.fetchone()
        if not row:
            c.execute(
                "INSERT INTO counter(counter_name, counter_value) VALUES (? , ?)",
                (counter_name, default_value+1)
            )
            return default_value
        if row:
            c.execute(
                "UPDATE counter SET counter_value=counter_value+1 WHERE counter_name=?",
                (counter_name,)
            )
            return row["counter_value"]


def set_key_value_pair(transaction, key_name, value):
    encoded_value = json.dumps(value)
    with cursor_manager(transaction) as c:
        c.execute(
            """
            REPLACE INTO key_value_store(
                key_name, value_json
            ) VALUES (
                ?, ?
            )
            """,
            (key_name, encoded_value)
        )


def del_key_value_pair(transaction, key_name):
    with cursor_manager(transaction) as c:
        c.execute(
            "DELETE FROM key_value_store WHERE key_name = ?",
            (key_name,)
        )


def get_key_value_pair(connection, key_name, default=None):
    with cursor_manager(connection) as c:
        c.execute(
            "SELECT value_json FROM key_value_store WHERE key_name = ?",
            (key_name,)
        )
        row = c.fetchone()
        if row:
            return json.loads(row['value_json'])
        else:
            return default


def get_all_key_value_pairs(connection):
    with cursor_manager(connection) as c:
        c.execute(
            "SELECT key_name, value_json FROM key_value_store"
        )
        return {
            row['key_name']: json.loads(row['value_json']) for row in c.fetchall()
        }


def get_all_jobs(connection, limit=None, offset=None, order_by=None):
    query = "SELECT * FROM job"
    params = []
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
    if offset is not None:
        query += " OFFSET ?"
        params.append(offset)
    if order_by is not None:
        query += " ORDER BY {0} ".format(order_by)
    with cursor_manager(connection) as c:
        c.execute(
            query,
            params
        )
        return [AgentJob.from_row(r) for r in c.fetchall()]


def get_all_active_jobs(connection, limit=None, offset=None, order_by=None):
    query = "SELECT * FROM job WHERE job_end_time_utc_epoch_seconds IS NULL "
    params = []
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
    if offset is not None:
        query += " OFFSET ?"
        params.append(offset)
    if order_by is not None:
        query += " ORDER BY {0} ".format(order_by)
    with cursor_manager(connection) as c:
        c.execute(
            query,
            params
        )
        return [AgentJob.from_row(r) for r in c.fetchall()]


def add_job(transaction, new_job_record, sequence_counter_name='REPLICATION_COUNTER'):
    counter_value = get_and_increment_counter(transaction, sequence_counter_name)
    new_job_record.last_updated_sequence_number = counter_value
    new_job_record.created_time = new_job_record.last_updated_time = local_now()
    with cursor_manager(transaction) as c:
        c.execute(
            "INSERT INTO job("
            "  job_uuid, job_name, job_args_json, job_user, job_host,"
            "  job_tags_json, job_status_code, job_start_time_utc_epoch_seconds, "
            "  job_end_time_utc_epoch_seconds, created_time_utc_epoch_seconds,"
            "  last_updated_time_utc_epoch_seconds, last_updated_sequence_number"
            ") VALUES ("
            "  :job_uuid, :job_name, :job_args_json, :job_user, :job_host,"
            "  :job_tags_json, :job_status_code, :job_start_time_utc_epoch_seconds, "
            "  :job_end_time_utc_epoch_seconds, :created_time_utc_epoch_seconds,"
            "  :last_updated_time_utc_epoch_seconds, :last_updated_sequence_number"
            ")",
            new_job_record.to_row()
        )
        new_job_record.job_id = c.lastrowid
    return new_job_record


def update_job(transaction, job_record, sequence_counter_name='REPLICATION_COUNTER'):
    counter_value = get_and_increment_counter(transaction, sequence_counter_name)
    job_record.last_updated_sequence_number = counter_value
    job_record.last_updated_time = local_now()
    with cursor_manager(transaction) as c:
        c.execute(
            """
            UPDATE job
            SET job_uuid = :job_uuid,
                job_name = :job_name,
                job_args_json = :job_args_json,
                job_user = :job_user,
                job_host = :job_host,
                job_tags_json = :job_tags,
                job_status_code = :job_status_code,
                job_start_time_utc_epoch_seconds = :job_start_time_utc_epoch_seconds,
                job_end_time_utc_epoch_seconds = :job_end_time_utc_epoch_seconds,
                created_time_utc_epoch_seconds = :created_time_utc_epoch_seconds,
                last_updated_time_utc_epoch_seconds = :last_updated_time_utc_epoch_seconds,
                last_updated_sequence_number = :last_updated_sequence_number
            WHERE job_id = :job_id
            """,
            job_record.to_row()
        )
    return job_record


def update_job_end_time_and_status(transaction, job_uuid, job_end_time, job_status_code,
                                   sequence_counter_name='REPLICATION_COUNTER'):
    last_updated_sequence_number = get_and_increment_counter(transaction, sequence_counter_name)
    last_updated_time = local_now()
    with cursor_manager(transaction) as c:
        c.execute(
            """
            UPDATE job
            SET job_status_code=?,
                job_end_time_utc_epoch_seconds=?,
                last_updated_time_utc_epoch_seconds=?,
                last_updated_sequence_number=?
            WHERE job_uuid=?
            """,
            (
                job_status_code,
                from_any_time_to_utc_seconds(job_end_time),
                from_any_time_to_utc_seconds(last_updated_time),
                last_updated_sequence_number,
                job_uuid
            )
        )
    return {
        'job_status_code': job_status_code,
        'job_end_time_utc_epoch_seconds': from_any_time_to_utc_seconds(job_end_time),
        'job_updated_time_utc_epoch_seconds': from_any_time_to_utc_seconds(last_updated_time),
        'job_updated_sequence_number': last_updated_sequence_number,
        'job_uuid': job_uuid
    }


def remove_old_jobs(transaction, minimum_age_hours, maximum_sequence_number=None):
    min_utc_seconds = from_any_time_to_utc_seconds(local_now() - datetime.timedelta(hours=minimum_age_hours))
    query = "DELETE FROM job " \
            "WHERE job_end_time_utc_epoch_seconds IS NOT NULL "\
            "AND job_end_time_utc_epoch_seconds < ? "
    params = [min_utc_seconds]
    if maximum_sequence_number is not None:
        query += "AND last_updated_sequence_number <= ?"
        params.append(maximum_sequence_number)
    with cursor_manager(transaction) as c:
        c.execute(
            query,
            params
        )
