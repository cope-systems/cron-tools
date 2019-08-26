import unittest
from assertpy import assert_that
from six import binary_type
import threading
import tempfile
import shutil
import os
import asyncore

from cron_tools.wrapper.rpc_client import RPCClient
from cron_tools.agent.config import AgentConfiguration
from cron_tools.agent.app import build_app, agent_argument_parser
from cron_tools.common.models import AgentJob


class CronToolsAgentApplicationUnitTest(unittest.TestCase):
    def test_basic_agent_start_and_communication_functionality(self):
        tempdir = tempfile.mkdtemp()
        socket_path = os.path.join(tempdir, "test.socket")
        database_path = os.path.join(tempdir, "test.db")
        raw_config = {
            "sqlite_database_path": database_path,
            "logging_config": {"version": 1, "incremental": True},
            "listen_socket_path": socket_path
        }
        config = AgentConfiguration.load(raw_config)
        args = agent_argument_parser.parse_args(args=["no-such-config-file"])

        try:
            run, shutdown = build_app(args=args, config=config)
            server_thread = threading.Thread(target=run)
            server_thread.start()
            client = RPCClient(socket_path)
            client_2 = RPCClient(socket_path)
            assert_that(client.handle_rpc_call("ping", {})).is_equal_to({"response": "pong"})
            assert_that(client_2.handle_rpc_call("ping", {})).is_equal_to({"response": "pong"})
            client.disconnect()
            client_2.disconnect()
            shutdown()
            server_thread.join(5)
        finally:
            shutil.rmtree(tempdir)
