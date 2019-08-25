import argparse
import asyncore

from cron_tools.agent.config import AgentConfiguration
from cron_tools.agent.rpc_server import AgentUnixStreamRPCServer

agent_argument_parser = argparse.ArgumentParser()
agent_argument_parser.add_argument("config_file", type=str, help="JSON Configuration file for the agent.")


def main():
    args = agent_argument_parser.parse_args()
    config = AgentConfiguration.from_file(args.config_file)
    server = AgentUnixStreamRPCServer(config.listen_socket_path, config.sqlite_database_url)
    server.serve_forever()
