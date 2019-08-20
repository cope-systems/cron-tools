import json

from cron_tools.common.config import ConfigurationException


class AgentConfiguration(object):
    def __init__(self, sqlite_database_url):
        self.sqlite_database_url = sqlite_database_url

    @classmethod
    def load_and_validate_raw(cls, raw_config):
        if not isinstance(raw_config, dict):
            raise ConfigurationException("Configuration must be a dict/object type!")
        if "database_url" not in raw_config:
            raise ConfigurationException("No SQLite3 database_url specified in agent configuration!")
        return cls(
            raw_config["database_url"]
        )

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as f:
            return cls.load_and_validate_raw(json.load(f))
