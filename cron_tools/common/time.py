"""
Common  time related functions, mostly for converting between representations of time.
"""
import datetime
import math
from dateutil.parser import parse
from dateutil.tz import tzutc, tzlocal
from six import integer_types

UNIX_EPOCH = datetime.datetime(year=1970, month=1, day=1, hour=0, minute=0, tzinfo=tzutc())
NUMERIC_TYPES = tuple(list(integer_types) + [float])


def from_any_time_to_utc_seconds(t, offset_naive_ok=True):
    if isinstance(t, datetime.datetime):
        if offset_naive_ok and t.tzinfo is None:
            t = t.replace(tzinfo=tzlocal())
        return (t - UNIX_EPOCH).total_seconds()
    elif isinstance(t, NUMERIC_TYPES):
        return t
    else:
        parsed_dt = parse(t)
        if offset_naive_ok and parsed_dt.tzinfo is None:
            parsed_dt = parsed_dt.replace(tzinfo=tzlocal())
        return (parsed_dt - UNIX_EPOCH).total_seconds()


def from_utc_seconds_to_datetime(t):
    if not isinstance(t, NUMERIC_TYPES):
        raise ValueError("Expected incoming time to be numeric, was instead {0}({1})".format(type(t), t))
    else:
        dt = UNIX_EPOCH + datetime.timedelta(seconds=t)
        return dt


def from_any_time_to_datetime(t):
    if isinstance(t, NUMERIC_TYPES):
        return from_utc_seconds_to_datetime(t)
    elif isinstance(t, datetime.datetime):
        return t
    else:
        return parse(t)


def local_now():
    return datetime.datetime.now(tz=tzlocal())