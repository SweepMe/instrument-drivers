"""This package extends the built-in datetime types to support sub-microsecond values.

The classes defined in this package are:

* :any:`hightime.datetime`: A subclass of :any:`datetime.datetime` with sub-microsecond
  capabilities.

* :any:`hightime.timedelta`: A subclass of :any:`datetime.timedelta` with sub-microsecond
  capabilities.

.. note::
   Due to floating point arithmetic inaccuracies, the ability to specify
   sub-microsecond values in terms of much larger units (weeks, days, seconds) has been
   limited. For the exact limitations, please consult the source code.
"""

import datetime as _std_datetime

from hightime._datetime import datetime
from hightime._timedelta import timedelta

__all__ = ["datetime", "timedelta"]

# Hide that it was defined in a helper file
datetime.__module__ = __name__
timedelta.__module__ = __name__


datetime.min = datetime(
    year=_std_datetime.datetime.min.year,
    month=_std_datetime.datetime.min.month,
    day=_std_datetime.datetime.min.day,
)
datetime.max = datetime(
    year=_std_datetime.datetime.max.year,
    month=_std_datetime.datetime.max.month,
    day=_std_datetime.datetime.max.day,
    hour=_std_datetime.datetime.max.hour,
    minute=_std_datetime.datetime.max.minute,
    second=_std_datetime.datetime.max.second,
    microsecond=_std_datetime.datetime.max.microsecond,
    femtosecond=999999999,
    yoctosecond=999999999,
)
datetime.resolution = timedelta(yoctoseconds=1)

timedelta.min = timedelta(days=_std_datetime.timedelta.min.days)
timedelta.max = timedelta(
    days=_std_datetime.timedelta.max.days,
    seconds=_std_datetime.timedelta.max.seconds,
    microseconds=_std_datetime.timedelta.max.microseconds,
    femtoseconds=999999999,
    yoctoseconds=999999999,
)
timedelta.resolution = timedelta(yoctoseconds=1)
