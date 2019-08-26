CREATE TABLE IF NOT EXISTS job(
    job_id INTEGER PRIMARY KEY,
    job_uuid TEXT UNIQUE NOT NULL,
    job_name TEXT NOT NULL,
    job_args_json TEXT NOT NULL,
    job_user TEXT NOT NULL,
    job_host TEXT NOT NULL,
    job_tags_json TEXT NOT NULL,
    job_status_code INTEGER,
    job_start_time_utc_epoch_seconds REAL NOT NULL,
    job_end_time_utc_epoch_seconds REAL,
    created_time_utc_epoch_seconds REAL NOT NULL,
    last_updated_time_utc_epoch_seconds REAL NOT NULL,
    last_updated_sequence_number INTEGER NOT NULL
);

CREATE TABLE counter(
    counter_name TEXT PRIMARY KEY,
    counter_value INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE key_value_store(
    key_name TEXT PRIMARY KEY,
    value_json TEXT NOT NULL
);