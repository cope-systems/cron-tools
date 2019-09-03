import argparse
import json

from cron_tools.agent.config import AgentConfiguration
from cron_tools.common.rpc_client import RPCClient

agent_admin_argument_parser = argparse.ArgumentParser()
agent_admin_argument_parser.add_argument("-v", "--verbose", action="store_true", help="Extra verbose output.")
agent_admin_argument_parser.add_argument("-j", "--json-output", action="store_true", help="Format output as JSON.")
agent_admin_argument_parser.add_argument(
    "-f", "--config-file", default=None, type=str, help="The agent configuration file."
)
subparsers = agent_admin_argument_parser.add_subparsers(title='command', dest='command')

show_active_jobs_parser = subparsers.add_parser('show-active-jobs')

ping_agent_parser = subparsers.add_parser("ping-agent")


def main(args=None, config=None):
    args = args or agent_admin_argument_parser.parse_args()
    if config:
        pass
    elif args.config_file:
        config = AgentConfiguration.from_file(args.config_file)
    else:
        config = AgentConfiguration.default()

    rpc_client = RPCClient(config.listen_socket_path)
    rpc_client.connect()
    if args.command == "show-active-jobs":
        pass
    elif args.command == "ping-agent":
        if args.json_output:
            print(json.dumps(rpc_client.handle_rpc_call('ping', {})))
        else:
            print(rpc_client.handle_rpc_call('ping', {})['response'])
