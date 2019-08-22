import unittest
from assertpy import assert_that
from six import binary_type

from cron_tools.common.rpc import BaseRPCClientHandler, BaseRPCServerHandler


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
