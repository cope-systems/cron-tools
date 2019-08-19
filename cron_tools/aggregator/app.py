import bottle
import argparse


aggregator_argument_parser = argparse.ArgumentParser()


def build_app():
    app = bottle.Bottle()
    return app


def main():
    args = aggregator_argument_parser.parse_args()
    app = build_app()
