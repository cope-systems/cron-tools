"""
Common Remote Procedure Call (rpc) library, both client and server, based loosely off of the JSON-RPC 2.0 standard.
"""
import json
import inspect


def serialize(o):
    return json.dumps(o).encode('utf-8')


def deserialize(i):
    return json.loads(i.decode('utf-8'))


class BaseRPCClientHandler(object):
    @staticmethod
    def marshal_request(name, params):
        return serialize({
            "method": name,
            "params": params
        })

    @staticmethod
    def unmarshal_response(raw_response):
        response = deserialize(raw_response)
        return response['result']


class RPCMethod(object):
    def __init__(self, func):
        self.func = func

    def handle(self, raw_params):
        return self.func(
            **raw_params
        )


class RPCError(Exception):
    pass


class BaseRPCServerHandler(object):
    def __init__(self):
        self.registered_functions = {}

    def register_function(self, name, function):
        if not callable(function):
            raise ValueError("register_function requires a callable for the function parameter!")
        self.registered_functions[name] = RPCMethod(
            function
        )

    def handle_request(self, raw_request):
        parsed = deserialize(raw_request)
        method = parsed['method']
        params = parsed['params']
        result = self.registered_functions[method].handle(params)
        response = {
            "result": result
        }
        return serialize(response)
