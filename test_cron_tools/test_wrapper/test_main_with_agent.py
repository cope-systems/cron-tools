import unittest
from assertpy import assert_that
import threading
import tempfile
import shutil
import os

from cron_tools.common.rpc_client import RPCClient
from cron_tools.agent.config import AgentConfiguration
from cron_tools.agent.app import build_app, agent_argument_parser
from cron_tools.wrapper.main import main, wrapper_argument_parser
from cron_tools.wrapper.config import WrapperConfiguration


class CronToolsWrapperIntegrationTest(unittest.TestCase):
    def test_wrapper_to_agent_functionality(self):
        tempdir = tempfile.mkdtemp()
        socket_path = os.path.join(tempdir, "test.socket")
        database_path = os.path.join(tempdir, "test.db")
        raw_config = {
            "sqlite_database_path": database_path,
            "logging_config": {"version": 1, "incremental": True},
            "listen_socket_path": socket_path
        }
        agent_config = AgentConfiguration.load(raw_config)
        agent_args = agent_argument_parser.parse_args(args=["no-such-config-file"])
        shutdown = None
        server_thread = None
        client = None
        client_2 = None

        try:
            run, shutdown = build_app(args=agent_args, config=agent_config)
            server_thread = threading.Thread(target=run)
            server_thread.daemon = True
            server_thread.start()
            client = RPCClient(socket_path)
            client_2 = RPCClient(socket_path)
            assert_that(client.handle_rpc_call("ping", {})).is_equal_to({"response": "pong"})
            assert_that(client_2.handle_rpc_call("ping", {})).is_equal_to({"response": "pong"})
            assert_that(client.handle_rpc_call("get_recent_jobs", {"limit": None, "offset": None})).is_equal_to(
                {"recent_jobs": []}
            )

            wrapper_config = WrapperConfiguration.load({
                'agent_socket_path': socket_path,
                'logging_config': {"version": 1, "incremental": True}
            })
            wrapper_args = wrapper_argument_parser.parse_args(args=["--job-name", "foo", "--", "sleep", "3"])
            try:
                main(args=wrapper_args, config=wrapper_config)
            except SystemExit as e:
                if e.code != 0:
                    raise AssertionError("Unexpected exit code: {0}".format(e.code))
            recent_jobs = client.handle_rpc_call("get_recent_jobs", {"limit": None, "offset": None})
            assert_that(recent_jobs).contains_key("recent_jobs")
            assert_that(recent_jobs["recent_jobs"]).is_not_empty()
            assert_that(recent_jobs["recent_jobs"][0]["job_args"]).is_equal_to(["sleep", "3"])
        finally:
            if client:
                client.disconnect()
            if client_2:
                client_2.disconnect()
            if shutdown is not None:
                shutdown()
            if server_thread is not None:
                server_thread.join(5)
            shutil.rmtree(tempdir)
