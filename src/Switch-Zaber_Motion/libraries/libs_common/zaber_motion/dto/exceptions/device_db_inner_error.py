# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from ..device_db_source_type import DeviceDbSourceType


@dataclass
class DeviceDbInnerError:
    """
    One of the errors that occurred while trying to access information from the device database.
    """

    code: str
    """
    Code describing type of the error.
    """

    source_type: DeviceDbSourceType
    """
    The type of database source that caused the error.
    """

    message: str
    """
    Description of the error.
    """

    inner_errors: List['DeviceDbInnerError']
    """
    A list of errors that occurred while trying to access information from the device database.
    """

    @staticmethod
    def zero_values() -> 'DeviceDbInnerError':
        return DeviceDbInnerError(
            code="",
            source_type=next(first for first in DeviceDbSourceType),
            message="",
            inner_errors=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceDbInnerError':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceDbInnerError.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'code': str(self.code or ''),
            'sourceType': self.source_type.value,
            'message': str(self.message or ''),
            'innerErrors': [item.to_dict() for item in self.inner_errors] if self.inner_errors is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceDbInnerError':
        return DeviceDbInnerError(
            code=data.get('code'),  # type: ignore
            source_type=DeviceDbSourceType(data.get('sourceType')),  # type: ignore
            message=data.get('message'),  # type: ignore
            inner_errors=[DeviceDbInnerError.from_dict(item) for item in data.get('innerErrors')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.code is not None:
            if not isinstance(self.code, str):
                raise ValueError(f'Property "Code" of "DeviceDbInnerError" is not a string.')

        if self.source_type is None:
            raise ValueError(f'Property "SourceType" of "DeviceDbInnerError" is None.')

        if not isinstance(self.source_type, DeviceDbSourceType):
            raise ValueError(f'Property "SourceType" of "DeviceDbInnerError" is not an instance of "DeviceDbSourceType".')

        if self.message is not None:
            if not isinstance(self.message, str):
                raise ValueError(f'Property "Message" of "DeviceDbInnerError" is not a string.')

        if self.inner_errors is not None:
            if not isinstance(self.inner_errors, Iterable):
                raise ValueError('Property "InnerErrors" of "DeviceDbInnerError" is not iterable.')

            for i, inner_errors_item in enumerate(self.inner_errors):
                if inner_errors_item is None:
                    raise ValueError(f'Item {i} in property "InnerErrors" of "DeviceDbInnerError" is None.')

                if not isinstance(inner_errors_item, DeviceDbInnerError):
                    raise ValueError(f'Item {i} in property "InnerErrors" of "DeviceDbInnerError" is not an instance of "DeviceDbInnerError".')

                inner_errors_item.validate()
