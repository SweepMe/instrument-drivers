# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson


@dataclass
class StreamExecutionExceptionData:
    """
    Contains additional data for StreamExecutionException.
    """

    error_flag: str
    """
    The error flag that caused the exception.
    """

    reason: str
    """
    The reason for the exception.
    """

    @staticmethod
    def zero_values() -> 'StreamExecutionExceptionData':
        return StreamExecutionExceptionData(
            error_flag="",
            reason="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StreamExecutionExceptionData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StreamExecutionExceptionData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'errorFlag': str(self.error_flag or ''),
            'reason': str(self.reason or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StreamExecutionExceptionData':
        return StreamExecutionExceptionData(
            error_flag=data.get('errorFlag'),  # type: ignore
            reason=data.get('reason'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.error_flag is not None:
            if not isinstance(self.error_flag, str):
                raise ValueError(f'Property "ErrorFlag" of "StreamExecutionExceptionData" is not a string.')

        if self.reason is not None:
            if not isinstance(self.reason, str):
                raise ValueError(f'Property "Reason" of "StreamExecutionExceptionData" is not a string.')
