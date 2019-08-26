"""
Common record types for both the agent and aggregator.
"""
import uuid
import json

from cron_tools.common.time import from_any_time_to_utc_seconds, from_utc_seconds_to_datetime, \
    from_any_time_to_datetime


class AgentJob(object):
    def __init__(self, job_id, uuid, name, args, user, host, tags, status_code, start_time, end_time,
                 created_time, last_updated_time, last_updated_sequence_number):
        self.job_id = job_id
        self.uuid = uuid
        self.name = name
        self.args = args
        self.user = user
        self.host = host
        self.tags = tags
        self.status_code = status_code
        self.start_time = start_time
        self.end_time = end_time
        self.created_time = created_time
        self.last_updated_time = last_updated_time
        self.last_updated_sequence_number = last_updated_sequence_number

    def to_row(self):
        return {
            'job_id': self.job_id,
            'job_uuid': self.uuid,
            'job_name': self.name,
            'job_args_json': json.dumps(self.args),
            'job_user': self.user,
            'job_host': self.host,
            'job_tags_json': json.dumps(self.tags),
            'job_status_code': self.status_code,
            'job_start_time_utc_epoch_seconds': from_any_time_to_utc_seconds(self.start_time),
            'job_end_time_utc_epoch_seconds': from_any_time_to_utc_seconds(self.end_time),
            'created_time_utc_epoch_seconds': from_any_time_to_utc_seconds(self.created_time),
            'last_updated_time_utc_epoch_seconds': from_any_time_to_utc_seconds(self.last_updated_time),
            'last_updated_sequence_number': self.last_updated_sequence_number
        }

    @classmethod
    def from_row(cls, row):
        return cls(
            job_id=row['job_id'],
            uuid=row['job_uuid'],
            name=row['job_name'],
            args=json.loads(row['job_args_json']),
            user=row['job_user'],
            host=row['job_host'],
            tags=json.loads(row['job_tags_json']),
            status_code=row['job_status_code'],
            start_time=from_utc_seconds_to_datetime(row['job_start_time_utc_epoch_seconds']),
            end_time=from_utc_seconds_to_datetime(row['job_end_time_utc_epoch_seconds']),
            created_time=from_utc_seconds_to_datetime(row['created_time_utc_epoch_seconds']),
            last_updated_time=from_utc_seconds_to_datetime(row['last_updated_time_utc_epoch_seconds']),
            last_updated_sequence_number=row['last_updated_sequence_number']
        )

    def serialize(self):
        return {
            'job_id': self.job_id,
            'job_uuid': self.uuid,
            'job_name': self.name,
            'job_args_json': self.args,
            'job_user': self.user,
            'job_host': self.host,
            'job_tags_json': self.tags,
            'job_status_code': self.status_code,
            'job_start_time_utc_epoch_seconds': from_any_time_to_utc_seconds(self.start_time),
            'job_end_time_utc_epoch_seconds': from_any_time_to_utc_seconds(self.end_time),
            'created_time_utc_epoch_seconds': from_any_time_to_utc_seconds(self.created_time),
            'last_updated_time_utc_epoch_seconds': from_any_time_to_utc_seconds(self.last_updated_time),
            'last_updated_sequence_number': self.last_updated_sequence_number
        }

    @classmethod
    def deserialize(cls, raw_agent_job):
        if not isinstance(raw_agent_job, dict):
            raise ValueError("raw_agent_job must be dict or dict subclass!")
        return cls(
            job_id=raw_agent_job['job_id'],
            uuid=raw_agent_job['job_uuid'],
            name=raw_agent_job['job_name'],
            args=raw_agent_job['job_args_json'],
            user=raw_agent_job['job_user'],
            host=raw_agent_job['job_host'],
            tags=raw_agent_job['job_tags_json'],
            status_code=raw_agent_job['job_status_code'],
            start_time=from_any_time_to_datetime(raw_agent_job['job_start_time_utc_epoch_seconds']),
            end_time=from_any_time_to_datetime(raw_agent_job['job_end_time_utc_epoch_seconds']),
            created_time=from_any_time_to_datetime(raw_agent_job['created_time_utc_epoch_seconds']),
            last_updated_time=from_any_time_to_datetime(raw_agent_job['last_updated_time_utc_epoch_seconds']),
            last_updated_sequence_number=raw_agent_job['last_updated_sequence_number']
        )

class AggregatorJob(object):
    pass
