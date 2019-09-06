import bottle
from bottle_swagger import SwaggerPlugin
import argparse


from cron_tools.aggregator.config import AggregatorConfiguration
from cron_tools.aggregator.queries import apply_migrations


aggregator_argument_parser = argparse.ArgumentParser()
aggregator_argument_parser.add_argument(
    "-f", "--config-file", type=str, default=None, help="JSON Configuration file for the agent."
)
aggregator_argument_parser.add_argument(
    "--auto-apply-migrations", action="store_true", help="Automatically apply any pending database migrations."
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

    if args.auto_apply_migrations:
        apply_migrations(config.postgres_database_url)

    app = build_app(config)
    app.run(host=config.bind_address, port=config.bind_port)
