import argparse
import time
import signal
from threading import Thread, Event

from cron_tools.agent.config import AgentConfiguration
from cron_tools.agent.rpc_server import AgentUnixStreamRPCServer, attach_agent_functions
from cron_tools.agent.queries import SimpleConnectionPool

agent_argument_parser = argparse.ArgumentParser()
agent_argument_parser.add_argument("config_file", type=str, help="JSON Configuration file for the agent.")


def build_app(args=None, config=None):
    args = args or agent_argument_parser.parse_args()
    config = config or AgentConfiguration.from_file(args.config_file)
    server = AgentUnixStreamRPCServer(config.listen_socket_path)
    attach_agent_functions(
        server, SimpleConnectionPool(config.sqlite_database_path)
    )
    server_thread = Thread(target=server.serve_forever)
    shutdown_event = Event()

    def run():
        server_thread.start()
        while not shutdown_event.is_set():
            time.sleep(1)
        server.shutdown()
        server.server_close()

    def shutdown():
        shutdown_event.set()

    return run, shutdown


def main(args=None, config=None):
    run, shutdown = build_app(args=args, config=config)
    signal.signal(signal.SIGTERM, lambda *args, **kwargs: shutdown())
    signal.signal(signal.SIGHUP, lambda *args, **kwargs: shutdown())
    return run()
