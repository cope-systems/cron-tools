from logging import config as logging_config_module

from cron_tools.common.config import JSONSourcedConfiguration


class AggregatorConfiguration(JSONSourcedConfiguration):
    DEFAULT_DATABASE_URL = 'postgres://localhost'
    DEFAULT_BIND_ADDRESS = '127.0.0.1'
    DEFAULT_BIND_PORT = 8081

    OPTIONAL_PARAMETERS = {
        'bind_address': DEFAULT_BIND_ADDRESS,
        'bind_port': DEFAULT_BIND_PORT,
        'postgres_database_url': DEFAULT_DATABASE_URL,
        'logging_config': {
            'version': 1,
            'formatters': {
                'detailed': {
                    'fmt': '%(asctime)s %(levelname)-3s [%(module)s:%(lineno)d] %(message)s'
                }
            },
            'handlers': {
                'stderr': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'detailed',
                    'level': 'WARNING',
                    'stream': 'ext://sys.stderr'
                }
            },
            'root': {
                'handler': 'stderr',
                'level': 'WARNING'
            }
        }
    }

    def __init__(self, logging_config=OPTIONAL_PARAMETERS['logging_config'], **kwargs):
        super(AggregatorConfiguration, self).__init__(**kwargs)
        self.logging_config = logging_config
        logging_config_module.dictConfig(logging_config)

    @classmethod
    def default(cls):
        return cls()
