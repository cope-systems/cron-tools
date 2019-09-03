import bottle
from bottle_swagger import SwaggerPlugin
import argparse


from cron_tools.aggregator.config import AggregatorConfiguration


aggregator_argument_parser = argparse.ArgumentParser()
aggregator_argument_parser.add_argument(
    "-f", "--config-file", type=str, default=None, help="JSON Configuration file for the agent."
)


def build_app(config):
    app = bottle.Bottle()
    return app


def main(args=None, config=None):
    args = args or aggregator_argument_parser.parse_args()

    if config:
        pass
    if args.config_file:
        config = AggregatorConfiguration.from_file(args.config_file)
    else:
        config = AggregatorConfiguration.default()

    app = build_app(config)
    app.run(host=config.bind_address, port=config.bind_port)
