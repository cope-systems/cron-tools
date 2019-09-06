"""
Initial schema for aggregator application.
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
CREATE TABLE IF NOT EXISTS job(
  job_id BIGSERIAL,
  job_uuid UUID UNIQUE NOT NULL,
  job_name TEXT NOT NULL,
  job_args JSONB NOT NULL,
  job_user TEXT NOT NULL,
  job_host TEXT NOT NULL,
  job_tags JSONB NOT NULL,
  job_status_code INTEGER,
  job_start_time TIMESTAMP WITH TIME ZONE,
  job_end_time TIMESTAMP WITH TIME ZONE,
  created_time TIMESTAMP WITH TIME ZONE,
  last_updated_time TIMESTAMP WITH TIME ZONE
);
        """
    )
]
