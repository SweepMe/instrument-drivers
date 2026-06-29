# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson


@dataclass
class DeviceGetWarningsResponse:

    flags: List[str] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'DeviceGetWarningsResponse':
        return DeviceGetWarningsResponse(
            flags=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceGetWarningsResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceGetWarningsResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'flags': [str(item or '') for item in self.flags] if self.flags is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceGetWarningsResponse':
        return DeviceGetWarningsResponse(
            flags=data.get('flags'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.flags is not None:
            if not isinstance(self.flags, Iterable):
                raise ValueError('Property "Flags" of "DeviceGetWarningsResponse" is not iterable.')

            for i, flags_item in enumerate(self.flags):
                if flags_item is not None:
                    if not isinstance(flags_item, str):
                        raise ValueError(f'Item {i} in property "Flags" of "DeviceGetWarningsResponse" is not a string.')
