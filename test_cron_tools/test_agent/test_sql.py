import unittest
from assertpy import assert_that

from cron_tools.agent.queries import create_connection, get_and_increment_counter, \
    immediate_transaction_manager, write_schema, get_all_key_value_pairs, get_key_value_pair, \
    set_key_value_pair, del_key_value_pair, transaction_manager


class AgentSqliteQueryUnitTests(unittest.TestCase):
    def setUp(self):
        self.test_conn = create_connection(":memory:")
        write_schema(self.test_conn)

    def test_counter_functionality(self):
        expected_value = 0

        for _ in range(10000):
            with immediate_transaction_manager(self.test_conn) as t:
                assert_that(get_and_increment_counter(t, "TEST_COUNTER")).is_equal_to(
                    expected_value
                )
                expected_value += 1

    def test_key_value_pair_functionality(self):
        assert_that(get_all_key_value_pairs(self.test_conn)).is_empty().is_instance_of(dict)
        assert_that(get_key_value_pair(self.test_conn, "foobar")).is_none()

        with transaction_manager(self.test_conn) as t:
            set_key_value_pair(t, "foobar", {"a": 2})

        assert_that(get_key_value_pair(self.test_conn, "foobar")).is_equal_to(
            {"a": 2}
        )
        assert_that(get_all_key_value_pairs(self.test_conn)).is_not_empty().contains_entry(
            {"foobar": {"a": 2}}
        )

        with transaction_manager(self.test_conn) as t:
            del_key_value_pair(t, "foobar")

        assert_that(get_all_key_value_pairs(self.test_conn)).is_empty().is_instance_of(dict)
        assert_that(get_key_value_pair(self.test_conn, "foobar")).is_none()

    def test_job_crud(self):
        pass