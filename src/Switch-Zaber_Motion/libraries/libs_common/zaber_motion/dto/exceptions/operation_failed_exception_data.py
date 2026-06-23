# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class OperationFailedExceptionData:
    """
    Contains additional data for OperationFailedException.
    """

    warnings: List[str]
    """
    The full list of warnings.
    """

    reason: str
    """
    The reason for the Exception.
    """

    device: int
    """
    The address of the device that attempted the failed operation.
    """

    axis: int
    """
    The number of the axis that attempted the failed operation.
    """

    @staticmethod
    def zero_values() -> 'OperationFailedExceptionData':
        return OperationFailedExceptionData(
            warnings=[],
            reason="",
            device=0,
            axis=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'OperationFailedExceptionData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return OperationFailedExceptionData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'warnings': [str(item or '') for item in self.warnings] if self.warnings is not None else [],
            'reason': str(self.reason or ''),
            'device': int(self.device),
            'axis': int(self.axis),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'OperationFailedExceptionData':
        return OperationFailedExceptionData(
            warnings=data.get('warnings'),  # type: ignore
            reason=data.get('reason'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.warnings is not None:
            if not isinstance(self.warnings, Iterable):
                raise ValueError('Property "Warnings" of "OperationFailedExceptionData" is not iterable.')

            for i, warnings_item in enumerate(self.warnings):
                if warnings_item is not None:
                    if not isinstance(warnings_item, str):
                        raise ValueError(f'Item {i} in property "Warnings" of "OperationFailedExceptionData" is not a string.')

        if self.reason is not None:
            if not isinstance(self.reason, str):
                raise ValueError(f'Property "Reason" of "OperationFailedExceptionData" is not a string.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "OperationFailedExceptionData" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "OperationFailedExceptionData" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "OperationFailedExceptionData" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "OperationFailedExceptionData" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "OperationFailedExceptionData" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "OperationFailedExceptionData" is not integer value.')
