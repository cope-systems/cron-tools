import unittest
from assertpy import assert_that
import datetime
from dateutil.tz import tzlocal

from cron_tools.common.time import from_any_time_to_utc_seconds, from_utc_seconds_to_datetime, \
    from_any_time_to_datetime


class CommonTimeToolsUnitTestCases(unittest.TestCase):
    def test_time_conversion_idempotency(self):
        """
        Ensure that our functions for converting to and from UTC Epoch seconds have (roughly) idempotent behavior.
        """

        now = datetime.datetime.now().replace(tzinfo=tzlocal())

        assert_that(
            from_utc_seconds_to_datetime(from_any_time_to_utc_seconds(now))
        ).is_instance_of(datetime.datetime).is_between(
            now - datetime.timedelta(microseconds=250),
            now + datetime.timedelta(microseconds=250),
        )

        assert_that(
            from_any_time_to_datetime(from_any_time_to_utc_seconds(now))
        ).is_instance_of(datetime.datetime).is_between(
            now - datetime.timedelta(microseconds=250),
            now + datetime.timedelta(microseconds=250),
        )

        # now do it a bunch of times
        current = now
        for _ in range(1000):
            assert_that(current).is_instance_of(datetime.datetime).is_between(
                now - datetime.timedelta(microseconds=250),
                now + datetime.timedelta(microseconds=250),
            )
            current = from_utc_seconds_to_datetime(from_any_time_to_utc_seconds(current))

        current = now
        for _ in range(1000):
            assert_that(current).is_instance_of(datetime.datetime).is_between(
                now - datetime.timedelta(microseconds=250),
                now + datetime.timedelta(microseconds=250),
            )
            current = from_any_time_to_datetime(from_any_time_to_utc_seconds(current))

        # If we apply the any functions multiple times, it should always be the same
        current = now
        for _ in range(1000):
            assert_that(current).is_instance_of(datetime.datetime).is_between(
                now - datetime.timedelta(microseconds=250),
                now + datetime.timedelta(microseconds=250),
            )
            current = from_any_time_to_datetime(current)

        first = current = from_any_time_to_utc_seconds(now)
        for _ in range(1000):
            assert_that(current).is_instance_of(float).is_equal_to(
                first
            )
            current = from_any_time_to_utc_seconds(current)

    def test_time_conversion_types(self):
        """
        Ensure that our functions for converting time can handle the right types.
        """

        now = datetime.datetime.now().replace(tzinfo=tzlocal())

        assert_that(from_any_time_to_utc_seconds(now)).is_equal_to(from_any_time_to_utc_seconds(now.isoformat()))\
            .is_instance_of(float)

        assert_that(from_any_time_to_datetime(now.isoformat())).is_instance_of(datetime.datetime).is_equal_to(now)
