import json
import logging
from logging import config as logging_config_module

from cron_tools.common.config import ConfigurationException, JSONSourcedConfiguration


class AgentConfiguration(JSONSourcedConfiguration):
    DEFAULT_LISTEN_SOCKET_PATH = "/var/run/cron-tools/agent.sock"

    REQUIRED_PARAMETERS = [
        'sqlite_database_path'
    ]

    OPTIONAL_PARAMETERS = {
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
        }
    }

    def __init__(self, logging_config=OPTIONAL_PARAMETERS['logging_config'], **kwargs):
        super(AgentConfiguration, self).__init__(**kwargs)
        self.logging_config = logging_config
        logging_config_module.dictConfig(logging_config)

