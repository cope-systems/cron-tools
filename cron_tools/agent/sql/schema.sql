CREATE TABLE jobs(
    job_id INTEGER PRIMARY KEY,
    job_uuid TEXT UNIQUE NOT NULL,
    job_user TEXT NOT NULL,
    job_host TEXT NOT NULL
);