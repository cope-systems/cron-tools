import json


class ConfigurationException(Exception):
    pass


class JSONSourcedConfiguration(object):
    REQUIRED_PARAMETERS = []
    OPTIONAL_PARAMETERS = {}

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def __getattr__(self, item):
        if item in self._kwargs:
            return self._kwargs[item]
        else:
            raise AttributeError('No such configuration attribute: {0}'.format(item))

    def __delattr__(self, item):
        if item in self._kwargs:
            del self._kwargs[item]
        else:
            return super(JSONSourcedConfiguration, self).__delattr__(item)

    @classmethod
    def validate(cls, raw_config):
        if not isinstance(raw_config, dict):
            raise ConfigurationException("Configuration must be a dict/object type!")
        for param in cls.REQUIRED_PARAMETERS:
            if param not in raw_config:
                raise ConfigurationException("Missing necessary config parameter: {0}".format(param))

    @classmethod
    def load(cls, raw_config):
        cls.validate(raw_config)
        kwargs = dict(cls.OPTIONAL_PARAMETERS)
        kwargs.update(raw_config)
        return cls(**kwargs)

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as f:
            return cls.load(json.load(f))
