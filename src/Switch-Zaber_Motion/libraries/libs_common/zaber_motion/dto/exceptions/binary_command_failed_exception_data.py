# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class BinaryCommandFailedExceptionData:
    """
    Contains additional data for BinaryCommandFailedException.
    """

    response_data: int
    """
    The response data.
    """

    @staticmethod
    def zero_values() -> 'BinaryCommandFailedExceptionData':
        return BinaryCommandFailedExceptionData(
            response_data=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'BinaryCommandFailedExceptionData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return BinaryCommandFailedExceptionData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'responseData': int(self.response_data),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BinaryCommandFailedExceptionData':
        return BinaryCommandFailedExceptionData(
            response_data=data.get('responseData'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.response_data is None:
            raise ValueError(f'Property "ResponseData" of "BinaryCommandFailedExceptionData" is None.')

        if not isinstance(self.response_data, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ResponseData" of "BinaryCommandFailedExceptionData" is not a number.')

        if int(self.response_data) != self.response_data:
            raise ValueError(f'Property "ResponseData" of "BinaryCommandFailedExceptionData" is not integer value.')
