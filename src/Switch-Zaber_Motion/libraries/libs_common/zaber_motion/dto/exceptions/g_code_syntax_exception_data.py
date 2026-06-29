# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class GCodeSyntaxExceptionData:
    """
    Contains additional data for GCodeSyntaxException.
    """

    from_block: int
    """
    The index in the block string that caused the exception.
    """

    to_block: int
    """
    The end index in the block string that caused the exception.
    The end index is exclusive.
    """

    @staticmethod
    def zero_values() -> 'GCodeSyntaxExceptionData':
        return GCodeSyntaxExceptionData(
            from_block=0,
            to_block=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GCodeSyntaxExceptionData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GCodeSyntaxExceptionData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'fromBlock': int(self.from_block),
            'toBlock': int(self.to_block),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GCodeSyntaxExceptionData':
        return GCodeSyntaxExceptionData(
            from_block=data.get('fromBlock'),  # type: ignore
            to_block=data.get('toBlock'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.from_block is None:
            raise ValueError(f'Property "FromBlock" of "GCodeSyntaxExceptionData" is None.')

        if not isinstance(self.from_block, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "FromBlock" of "GCodeSyntaxExceptionData" is not a number.')

        if int(self.from_block) != self.from_block:
            raise ValueError(f'Property "FromBlock" of "GCodeSyntaxExceptionData" is not integer value.')

        if self.to_block is None:
            raise ValueError(f'Property "ToBlock" of "GCodeSyntaxExceptionData" is None.')

        if not isinstance(self.to_block, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ToBlock" of "GCodeSyntaxExceptionData" is not a number.')

        if int(self.to_block) != self.to_block:
            raise ValueError(f'Property "ToBlock" of "GCodeSyntaxExceptionData" is not integer value.')
