# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class TranslateMessage:
    """
    Represents a message from translator regarding a block translation.
    """

    message: str
    """
    The message describing an occurrence.
    """

    from_block: int
    """
    The index in the block string that the message regards to.
    """

    to_block: int
    """
    The end index in the block string that the message regards to.
    The end index is exclusive.
    """

    @staticmethod
    def zero_values() -> 'TranslateMessage':
        return TranslateMessage(
            message="",
            from_block=0,
            to_block=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TranslateMessage':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TranslateMessage.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'message': str(self.message or ''),
            'fromBlock': int(self.from_block),
            'toBlock': int(self.to_block),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TranslateMessage':
        return TranslateMessage(
            message=data.get('message'),  # type: ignore
            from_block=data.get('fromBlock'),  # type: ignore
            to_block=data.get('toBlock'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.message is not None:
            if not isinstance(self.message, str):
                raise ValueError(f'Property "Message" of "TranslateMessage" is not a string.')

        if self.from_block is None:
            raise ValueError(f'Property "FromBlock" of "TranslateMessage" is None.')

        if not isinstance(self.from_block, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "FromBlock" of "TranslateMessage" is not a number.')

        if int(self.from_block) != self.from_block:
            raise ValueError(f'Property "FromBlock" of "TranslateMessage" is not integer value.')

        if self.to_block is None:
            raise ValueError(f'Property "ToBlock" of "TranslateMessage" is None.')

        if not isinstance(self.to_block, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ToBlock" of "TranslateMessage" is not a number.')

        if int(self.to_block) != self.to_block:
            raise ValueError(f'Property "ToBlock" of "TranslateMessage" is not integer value.')
