import argparse
import asyncore
import socket
import struct

from cron_tools.agent.config import AgentConfiguration

agent_argument_parser = argparse.ArgumentParser()
agent_argument_parser.add_argument("config_file", type=str, help="JSON Configuration file for the agent.")

MAGIC_BYTE = b'\x5A'


class AgentRPCHandler(asyncore.dispatcher_with_send):
    def handle_read(self):
        magic_byte = self.read(1)
        if magic_byte != MAGIC_BYTE or not magic_byte:
            self.close()
        raw_length = self.read(4)
        if not raw_length:
            self.close()
        length, = struct.unpack('!L', raw_length)
        raw_payload = self.read(length)

        raw_response = b''
        self.send(MAGIC_BYTE + struct.pack('!L', len(raw_response)))
        self.send(raw_response)


class AgentServer(asyncore.dispatcher):
    def __init__(self, listen_path, listen_depth=10):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.bind(listen_path)
        self.listen(listen_depth)

    def handle_accepted(self, sock, addr):
        AgentRPCHandler(sock)


def main():
    args = agent_argument_parser.parse_args()
    config = AgentConfiguration.from_file(args.config_file)
    server = AgentServer(config.listen_socket_path)
    asyncore.loop()

