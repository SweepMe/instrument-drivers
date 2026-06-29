# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from ..binary.message import Message


@dataclass
class BinaryMessageCollection:

    messages: List[Message] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'BinaryMessageCollection':
        return BinaryMessageCollection(
            messages=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'BinaryMessageCollection':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return BinaryMessageCollection.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'messages': [item.to_dict() for item in self.messages] if self.messages is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BinaryMessageCollection':
        return BinaryMessageCollection(
            messages=[Message.from_dict(item) for item in data.get('messages')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.messages is not None:
            if not isinstance(self.messages, Iterable):
                raise ValueError('Property "Messages" of "BinaryMessageCollection" is not iterable.')

            for i, messages_item in enumerate(self.messages):
                if messages_item is None:
                    raise ValueError(f'Item {i} in property "Messages" of "BinaryMessageCollection" is None.')

                if not isinstance(messages_item, Message):
                    raise ValueError(f'Item {i} in property "Messages" of "BinaryMessageCollection" is not an instance of "Message".')

                messages_item.validate()
