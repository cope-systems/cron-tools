"""
Common Remote Procedure Call (rpc) library, both client and server, based loosely off of the JSON-RPC 2.0 standard.
"""
import json
import inspect
import collections
import six
import threading

RPCErrorCode = collections.namedtuple('RPCErrorCode', ('value', 'message', 'description'))


# Taken from the JSON-RPC 2.0 specification
# https://www.jsonrpc.org/specification
class RPCErrorCodes(object):
    PARSE_ERROR = RPCErrorCode(
        -32700, 'Parse Error',
        "Invalid JSON was received by the server. An error occurred on the server while parsing the JSON text."
    )
    INVALID_REQUEST = RPCErrorCode(
        -32600, "Invalid Request",
        "The JSON sent is not a valid Request object."
    )
    METHOD_NOT_FOUND = RPCErrorCode(
        -32601, "Method Not Found",
        "The method does not exist / is not available."
    )
    INVALID_PARAMETERS = RPCErrorCode(
        -32602, "Invalid Parameters",
        "Invalid method parameter(s)."
    )
    INTERNAL_ERROR = RPCErrorCode(
        -32603, "Internal Error",
        "Internal JSON-RPC Error"
    )


class RPCException(Exception):
    def __init__(self, message, rpc_error_code=None):
        super(RPCException, self).__init__(message)
        self.rpc_error_code = rpc_error_code


def serialize(o):
    return json.dumps(o).encode('utf-8')


def deserialize(i):
    return json.loads(i.decode('utf-8'))


class BaseRPCClientHandler(object):
    def __init__(self):
        self._counter = 1
        self._lock = threading.Lock()

    @property
    def current_id(self):
        with self._lock:
            value = self._counter
            self._counter += 1
            return value

    def marshal_request(self, name, params):
        return serialize({
            "json-rpc": "2.0",
            "id": self.current_id,
            "method": name,
            "params": params
        })

    def unmarshal_response(self, raw_response):
        try:
            response = deserialize(raw_response)
        except ValueError:
            raise RPCException(
                "Malformed response from server", None
            )
        if not isinstance(response, dict):
            raise RPCException(
                "Incorrectly structured JSON payload from server", None
            )
        if "result" in response:
            return response['result']
        elif "error" in response:
            raise RPCException(
                response["error"].get("message", "Unknown"),
                response["error"].get("code")
            )
        else:
            raise RPCException(
                "Incorrectly structured JSON payload from server", None
            )


class RPCMethod(object):
    def __init__(self, func):
        self.func = func

    @property
    def params(self):
        if six.PY2:
            return inspect.getargspec(self.func)[0]
        else:
            return inspect.signature(self.func).parameters.keys()

    @property
    def documentation(self):
        return inspect.getdoc(self.func)

    def handle(self, raw_params):
        return self.func(
            **raw_params
        )


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
        try:
            parsed = deserialize(raw_request)
        except ValueError as e:
            return serialize({
                "json-rpc": "2.0",
                "error": {
                    "message": repr(e),
                    "code": RPCErrorCodes.PARSE_ERROR.value
                }
            })
        if not (isinstance(parsed, dict) and "method" in parsed and "params" in parsed):
            return serialize({
                "json-rpc": "2.0",
                "error": {
                    "message": RPCErrorCodes.INVALID_REQUEST.message,
                    "code": RPCErrorCodes.INVALID_REQUEST.value
                }
            })
        method = parsed['method']
        params = parsed['params']
        if method not in self.registered_functions:
            return serialize({
                "json-rpc": "2.0",
                "error": {
                    "message": RPCErrorCodes.METHOD_NOT_FOUND.message,
                    "code": RPCErrorCodes.METHOD_NOT_FOUND.value
                }
            })
        try:
            result = self.registered_functions[method].handle(params)
            response = {
                "result": result
            }
        except Exception as e:
            return serialize({
                "json-rpc": "2.0",
                "error": {
                    "message": repr(e),
                    "code": RPCErrorCodes.INTERNAL_ERROR.value
                }
            })
        else:
            return serialize(response)
