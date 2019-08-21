CREATE TABLE jobs(
    job_id INTEGER PRIMARY KEY,
    job_uuid TEXT UNIQUE NOT NULL,
    job_name TEXT NOT NULL,
    job_args_json TEXT NOT NULL,
    job_user TEXT NOT NULL,
    job_host TEXT NOT NULL,
    job_tags_json TEXT NOT NULL,
    job_start_time_utc_epoch_seconds REAL NOT NULL,
    job_end_time_utc_epoch_seconds REAL,
    created_time_utc_epoch_seconds REAL NOT NULL,
    last_updated_time_utc_epoch_seconds REAL NOT NULL
);