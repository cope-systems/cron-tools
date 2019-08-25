import socket
import struct
from six.moves import socketserver

from cron_tools.common.rpc import BaseRPCServerHandler

MAGIC_BYTE = b'\x5A'


class AgentRPCHandler(socketserver.BaseRequestHandler):
    def recv_bytes(self, amount):
        data = bytearray()
        delta = True
        while len(data) < amount and delta:
            delta = self.request.recv(min(8192, amount))
            data.extend(delta)
        return data

    def handle(self):
        while True:
            magic_byte = self.request.recv(1)
            if magic_byte != MAGIC_BYTE or not magic_byte:
                self.request.shutdown(socket.SHUT_RDWR)
                self.request.close()
                return
            raw_length = self.recv_bytes(struct.calcsize('!L'))
            if not raw_length:
                self.request.shutdown(socket.SHUT_RDWR)
                self.request.close()
                return
            length, = struct.unpack('!L', raw_length)
            raw_payload = self.recv_bytes(length)
            if not raw_payload:
                self.request.shutdown(socket.SHUT_RDWR)
                self.request.close()
                return
            raw_response = self.server.handler.handle_request(raw_payload)
            self.request.sendall(MAGIC_BYTE + struct.pack('!L', len(raw_response)))
            self.request.sendall(raw_response)


class AgentUnixStreamRPCServer(socketserver.ThreadingUnixStreamServer):
    def __init__(self, socket_addr, database_addr, bind_and_activate=True):
        self.handler = BaseRPCServerHandler()
        self.database_addr = database_addr
        socketserver.ThreadingUnixStreamServer.__init__(
            self,
            socket_addr,
            AgentRPCHandler,
            bind_and_activate=bind_and_activate
        )

    def register_function(self, name, function):
        return self.handler.register_function(name, function)
