import socket
import struct
from six.moves import socketserver

from cron_tools.common.rpc import BaseRPCServerHandler
from cron_tools.common.models import AgentJob
from cron_tools.agent.queries import immediate_transaction_manager, add_job, update_job_end_time_and_status, \
    get_all_jobs

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
    def __init__(self, socket_addr, bind_and_activate=True):
        self.handler = BaseRPCServerHandler()
        socketserver.ThreadingUnixStreamServer.__init__(
            self,
            socket_addr,
            AgentRPCHandler,
            bind_and_activate=bind_and_activate
        )

    def register_function(self, name, function):
        return self.handler.register_function(name, function)


def attach_agent_functions(agent_server, connection_pool):
    def ping():
        return {
            "response": "pong"
        }

    agent_server.register_function("ping", ping)

    def add_new_job(raw_job_record):
        job_record = AgentJob.deserialize(raw_job_record)
        connection = connection_pool.get()
        with immediate_transaction_manager(connection) as t:
            record = add_job(t, job_record)
        return {
            'record': record.serialize()
        }

    agent_server.register_function("add_new_job", add_new_job)

    def update_job_end_time_and_status_code(job_uuid, job_end_time, job_status_code):
        connection = connection_pool.get()
        with immediate_transaction_manager(connection) as t:
            updated_info = update_job_end_time_and_status(t, job_uuid, job_end_time, job_status_code)
        return {
            'updated_info': updated_info
        }

    agent_server.register_function("update_job_end_time_and_status_code", update_job_end_time_and_status_code)

    def get_recent_jobs(limit, offset):
        connection = connection_pool.get()
        jobs = get_all_jobs(connection, limit=limit, offset=offset, order_by="job_start_time_utc_epoch_seconds DESC")
        return {
            'recent_jobs': [j.serialize() for j in jobs]
        }

    agent_server.register_function("get_recent_jobs", get_recent_jobs)

    def send_job_alert(job_uuid, alert_message):
        pass  # TODO: Implement this.

    agent_server.register_function("send_job_alert", send_job_alert)
