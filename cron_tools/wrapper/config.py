import json

from cron_tools.common.config import ConfigurationException


class WrapperConfiguration(object):
    def __init__(self):
        pass

    @classmethod
    def load_and_validate_raw(cls, raw_config):
        if not isinstance(raw_config, dict):
            raise ConfigurationException("Configuration must be a dict/object type!")
        return cls()

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as f:
            return cls.load_and_validate_raw(json.load(f))
