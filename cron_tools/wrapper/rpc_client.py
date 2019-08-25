from cron_tools.common.rpc import BaseRPCClientHandler
import socket
import struct


MAGIC_BYTE = b'\x5A'


class RPCClient(object):
    def __init__(self, socket_addr, socket_family=socket.AF_UNIX):
        self.socket_addr = socket_addr
        self.socket_family = socket_family
        self.socket_type = socket.SOCK_STREAM
        self.client_handler = BaseRPCClientHandler()
        self.socket = None

    def connect(self):
        if self.socket is None:
            self.socket = socket.socket(self.socket_family, self.socket_type)
            self.socket.connect(self.socket_addr)

    def disconnect(self):
        if self.socket is not None:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            self.socket = None

    def handle_rpc_call(self, name, parameters):
        if not self.socket:
            self.connect()
        request = self.client_handler.marshal_request(name, parameters)
        self.socket.send(MAGIC_BYTE)
        self.socket.send(struct.pack('!L', len(request)))
        self.socket.send(request)

        resp_magic_byte = self.socket.recv(1)
        if resp_magic_byte != MAGIC_BYTE:
            self.disconnect()
            raise Exception("Bad RPC magic byte on response.")
        raw_length = self.socket.recv(struct.calcsize("!L"))
        length, = struct.unpack("!L", raw_length)
        raw_response = self.socket.recv(length)
        return self.client_handler.unmarshal_response(raw_response)
