import unittest
from assertpy import assert_that
from six import binary_type
import threading
import tempfile
import shutil
import os
import asyncore

from cron_tools.common.rpc import BaseRPCClientHandler, BaseRPCServerHandler, RPCException
from cron_tools.wrapper.rpc_client import RPCClient
from cron_tools.agent.rpc_server import AgentUnixStreamRPCServer


class CommonRPCCodeUnitTestCases(unittest.TestCase):
    def test_rpc_client_and_server_handlers_basic_functionality(self):
        """
        Test the basic workings of the RPC Client and Server handlers
        by feeding their inputs and outputs to each other.
        """

        def test_function(foo, bar):
            return foo + bar

        client_handler = BaseRPCClientHandler()
        server_handler = BaseRPCServerHandler()

        server_handler.register_function("test_function", test_function)

        raw_request = client_handler.marshal_request('test_function', {'foo': 1, 'bar': 2})
        server_resp = server_handler.handle_request(raw_request)
        final_resp = client_handler.unmarshal_response(server_resp)
        assert_that(final_resp).is_equal_to(3)
        assert_that(raw_request).is_instance_of(binary_type)
        assert_that(server_resp).is_instance_of(binary_type)

    def test_actual_client_and_server_rpc(self):
        """
        Test the agent and wrapper RPC implementations.
        """
        tempdir = tempfile.mkdtemp()

        def add(a, b):
            return a + b

        def cat(a, b):
            return a + " " + b

        def faulty():
            raise ValueError("???")

        try:
            socket_path = os.path.join(tempdir, "test.socket")
            server = AgentUnixStreamRPCServer(socket_path, ":memory:")
            server.register_function("cat", cat)
            server.register_function("add", add)
            server.register_function("faulty", faulty)

            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.start()

            client = RPCClient(socket_path)
            client.connect()
            assert_that(client.handle_rpc_call("cat", {"a": "foo", "b": "bar"})).is_equal_to(
                "foo bar"
            )
            assert_that(
                client.handle_rpc_call("add", {"a": 4, "b": 10})
            ).is_equal_to(14)
            self.assertRaises(
                RPCException, client.handle_rpc_call,
                "faulty", {}
            )
            client.disconnect()
            server.shutdown()
            server.server_close()
            server_thread.join(5)
        finally:
            shutil.rmtree(tempdir)
