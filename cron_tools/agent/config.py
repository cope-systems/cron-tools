from logging import config as logging_config_module

from cron_tools.common.config import ConfigurationException, JSONSourcedConfiguration


class AgentConfiguration(JSONSourcedConfiguration):
    DEFAULT_LISTEN_SOCKET_PATH = "/var/run/cron-tools/agent.sock"
    DEFAULT_DATABASE_PATH = '/var/lib/cron-tools/agent.db'

    OPTIONAL_PARAMETERS = {
        'sqlite_database_path': DEFAULT_DATABASE_PATH,
        'listen_socket_path': DEFAULT_LISTEN_SOCKET_PATH,
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
        },
        'clean_up_policy': {
            'enabled': True,
            'check_interval_minutes': 15,
            'replicated': {
                'min_age_hours': 24*3
            },
            'unreplicated': {
                'min_age_hours': 24*7
            }
        }
    }

    def __init__(self, logging_config=OPTIONAL_PARAMETERS['logging_config'], **kwargs):
        super(AgentConfiguration, self).__init__(**kwargs)
        self.logging_config = logging_config
        logging_config_module.dictConfig(logging_config)

    @classmethod
    def default(cls):
        return cls()
