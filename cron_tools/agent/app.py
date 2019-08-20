import argparse
import asyncore

from cron_tools.agent.config import AgentConfiguration

agent_argument_parser = argparse.ArgumentParser()
agent_argument_parser.add_argument("config_file", type=str, help="JSON Configuration file for the agent.")


def main():
    args = agent_argument_parser.parse_args()
    config = AgentConfiguration.from_file(args.config_file)

