import unittest
from webtest import TestApp
from assertpy import assert_that
import os


from cron_tools.aggregator.app import build_app
from cron_tools.aggregator.config import AggregatorConfiguration
from cron_tools.aggregator.queries import apply_migrations, transaction_wrapper, create_pg_connection

from test_cron_tools.test_aggregator.utils import clear_postgres_database


class CronToolsAggregatorApplicationUnitTest(unittest.TestCase):
    DATABASE_URL = os.environ.get("TEST_POSTGRES_URL")

    def setUp(self):
        if self.DATABASE_URL is None:
            raise AssertionError("No Postgres Database to test against!")
        apply_migrations(self.DATABASE_URL)

    def tearDown(self):
        conn = None
        try:
            conn = create_pg_connection(self.DATABASE_URL)
            with transaction_wrapper(conn) as t:
                clear_postgres_database(t)
        finally:
            if conn:
                conn.close()

    def build_test_app(self, config=None):
        app = build_app(config or AggregatorConfiguration.default())
        return TestApp(app)

    def test_basic_aggregator_start_up(self):
        app = self.build_test_app()
