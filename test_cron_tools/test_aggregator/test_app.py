import unittest
from webtest import TestApp
from assertpy import assert_that


from cron_tools.aggregator.app import build_app
from cron_tools.aggregator.config import AggregatorConfiguration


class CronToolsAggregatorApplicationUnitTest(unittest.TestCase):
    @staticmethod
    def build_test_app(config=None):
        app = build_app(config or AggregatorConfiguration.default())
        return TestApp(app)

    def test_basic_aggregator_start_up(self):
        app = self.build_test_app()