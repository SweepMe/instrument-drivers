# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson


@dataclass
class TestResponseLong:

    data_pong: List[str] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'TestResponseLong':
        return TestResponseLong(
            data_pong=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TestResponseLong':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TestResponseLong.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'dataPong': [str(item or '') for item in self.data_pong] if self.data_pong is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TestResponseLong':
        return TestResponseLong(
            data_pong=data.get('dataPong'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.data_pong is not None:
            if not isinstance(self.data_pong, Iterable):
                raise ValueError('Property "DataPong" of "TestResponseLong" is not iterable.')

            for i, data_pong_item in enumerate(self.data_pong):
                if data_pong_item is not None:
                    if not isinstance(data_pong_item, str):
                        raise ValueError(f'Item {i} in property "DataPong" of "TestResponseLong" is not a string.')
