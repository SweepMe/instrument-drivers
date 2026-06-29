# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from .device_db_inner_error import DeviceDbInnerError


@dataclass
class DeviceDbFailedExceptionData:
    """
    Contains additional data for a DeviceDbFailedException.
    """

    code: str
    """
    Code describing type of the error.
    """

    inner_errors: List[DeviceDbInnerError]
    """
    A list of errors that occurred while trying to access information from the device database.
    """

    @staticmethod
    def zero_values() -> 'DeviceDbFailedExceptionData':
        return DeviceDbFailedExceptionData(
            code="",
            inner_errors=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceDbFailedExceptionData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceDbFailedExceptionData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'code': str(self.code or ''),
            'innerErrors': [item.to_dict() for item in self.inner_errors] if self.inner_errors is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceDbFailedExceptionData':
        return DeviceDbFailedExceptionData(
            code=data.get('code'),  # type: ignore
            inner_errors=[DeviceDbInnerError.from_dict(item) for item in data.get('innerErrors')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.code is not None:
            if not isinstance(self.code, str):
                raise ValueError(f'Property "Code" of "DeviceDbFailedExceptionData" is not a string.')

        if self.inner_errors is not None:
            if not isinstance(self.inner_errors, Iterable):
                raise ValueError('Property "InnerErrors" of "DeviceDbFailedExceptionData" is not iterable.')

            for i, inner_errors_item in enumerate(self.inner_errors):
                if inner_errors_item is None:
                    raise ValueError(f'Item {i} in property "InnerErrors" of "DeviceDbFailedExceptionData" is None.')

                if not isinstance(inner_errors_item, DeviceDbInnerError):
                    raise ValueError(f'Item {i} in property "InnerErrors" of "DeviceDbFailedExceptionData" is not an instance of "DeviceDbInnerError".')

                inner_errors_item.validate()
