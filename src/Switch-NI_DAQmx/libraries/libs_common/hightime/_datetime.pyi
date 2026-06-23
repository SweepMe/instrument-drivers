import datetime as std_datetime
from typing import Any, ClassVar, Optional, SupportsIndex, overload

import hightime

class datetime(std_datetime.datetime):
    min: ClassVar[datetime]
    max: ClassVar[datetime]
    resolution: ClassVar[hightime.timedelta]
    def __add__(self, other: std_datetime.timedelta, /) -> datetime: ...
    def __eq__(self, other: object, /) -> bool: ...
    def __ge__(self, other: std_datetime.date, /) -> bool: ...
    def __gt__(self, other: std_datetime.date, /) -> bool: ...
    def __hash__(self) -> int: ...
    def __le__(self, other: std_datetime.date, /) -> bool: ...
    def __lt__(self, other: std_datetime.date, /) -> bool: ...
    def __ne__(self, other: object, /) -> bool: ...
    @overload
    @staticmethod
    def __new__(
        cls,
        year: SupportsIndex,
        month: SupportsIndex,
        day: SupportsIndex,
        hour: SupportsIndex,
        minute: SupportsIndex,
        second: SupportsIndex,
        microsecond: SupportsIndex,
        tzinfo: Optional[std_datetime._TzInfo],
        *,
        fold: int = ...,
    ) -> datetime: ...
    @overload
    @staticmethod
    def __new__(
        cls,
        year: SupportsIndex,
        month: SupportsIndex,
        day: SupportsIndex,
        hour: SupportsIndex = ...,
        minute: SupportsIndex = ...,
        second: SupportsIndex = ...,
        microsecond: SupportsIndex = ...,
        femtosecond: SupportsIndex = ...,
        yoctosecond: SupportsIndex = ...,
        tzinfo: Optional[std_datetime._TzInfo] = ...,
        *,
        fold: int = ...,
    ) -> datetime: ...
    @classmethod
    def _new_impl(
        cls,
        year: SupportsIndex,
        month: SupportsIndex,
        day: SupportsIndex,
        hour: SupportsIndex = ...,
        minute: SupportsIndex = ...,
        second: SupportsIndex = ...,
        microsecond: SupportsIndex = ...,
        femtosecond: SupportsIndex = ...,
        yoctosecond: SupportsIndex = ...,
        tzinfo: Optional[std_datetime._TzInfo] = ...,
        *,
        fold: int = ...,
    ) -> datetime: ...
    def __repr__(self) -> str: ...
    @overload  # type: ignore[override]
    def __sub__(self, value: datetime, /) -> hightime.timedelta: ...
    @overload
    def __sub__(self, value: std_datetime.timedelta, /) -> datetime: ...
    def _cmp(self, other: std_datetime.datetime, /) -> int: ...
    @classmethod
    def _from_base(cls, base_datetime: std_datetime.datetime, /) -> datetime: ...
    def astimezone(self, tz: Optional[std_datetime._TzInfo] = ...) -> datetime: ...
    @property
    def femtosecond(self) -> int: ...
    @classmethod
    def fromtimestamp(
        cls, t: float, tz: Optional[std_datetime._TzInfo] = ...
    ) -> datetime: ...
    def isoformat(self, sep: str = ..., timespec: str = ...) -> str: ...
    def replace(  # type: ignore[override]
        self,
        year: SupportsIndex = ...,
        month: SupportsIndex = ...,
        day: SupportsIndex = ...,
        hour: SupportsIndex = ...,
        minute: SupportsIndex = ...,
        second: SupportsIndex = ...,
        microsecond: SupportsIndex = ...,
        femtosecond: SupportsIndex = ...,
        yoctosecond: SupportsIndex = ...,
        tzinfo: Optional[std_datetime._TzInfo] = ...,
        *,
        fold: int = ...,
    ) -> datetime: ...
    @classmethod
    def utcfromtimestamp(cls, t: float, /) -> datetime: ...
    @property
    def yoctosecond(self) -> int: ...
