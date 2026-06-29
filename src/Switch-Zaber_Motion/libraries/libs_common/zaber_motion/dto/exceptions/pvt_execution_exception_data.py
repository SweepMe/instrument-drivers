# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from .invalid_pvt_point import InvalidPvtPoint


@dataclass
class PvtExecutionExceptionData:
    """
    Contains additional data for PvtExecutionException.
    """

    error_flag: str
    """
    The error flag that caused the exception.
    """

    reason: str
    """
    The reason for the exception.
    """

    invalid_points: List[InvalidPvtPoint]
    """
    A list of points that cause the error (if applicable).
    """

    @staticmethod
    def zero_values() -> 'PvtExecutionExceptionData':
        return PvtExecutionExceptionData(
            error_flag="",
            reason="",
            invalid_points=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtExecutionExceptionData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtExecutionExceptionData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'errorFlag': str(self.error_flag or ''),
            'reason': str(self.reason or ''),
            'invalidPoints': [item.to_dict() for item in self.invalid_points] if self.invalid_points is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtExecutionExceptionData':
        return PvtExecutionExceptionData(
            error_flag=data.get('errorFlag'),  # type: ignore
            reason=data.get('reason'),  # type: ignore
            invalid_points=[InvalidPvtPoint.from_dict(item) for item in data.get('invalidPoints')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.error_flag is not None:
            if not isinstance(self.error_flag, str):
                raise ValueError(f'Property "ErrorFlag" of "PvtExecutionExceptionData" is not a string.')

        if self.reason is not None:
            if not isinstance(self.reason, str):
                raise ValueError(f'Property "Reason" of "PvtExecutionExceptionData" is not a string.')

        if self.invalid_points is not None:
            if not isinstance(self.invalid_points, Iterable):
                raise ValueError('Property "InvalidPoints" of "PvtExecutionExceptionData" is not iterable.')

            for i, invalid_points_item in enumerate(self.invalid_points):
                if invalid_points_item is None:
                    raise ValueError(f'Item {i} in property "InvalidPoints" of "PvtExecutionExceptionData" is None.')

                if not isinstance(invalid_points_item, InvalidPvtPoint):
                    raise ValueError(f'Item {i} in property "InvalidPoints" of "PvtExecutionExceptionData" is not an instance of "InvalidPvtPoint".')

                invalid_points_item.validate()
