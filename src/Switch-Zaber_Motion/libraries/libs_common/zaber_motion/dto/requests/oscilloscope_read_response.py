# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class OscilloscopeReadResponse:

    data_ids: List[int] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'OscilloscopeReadResponse':
        return OscilloscopeReadResponse(
            data_ids=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'OscilloscopeReadResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return OscilloscopeReadResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'dataIds': [int(item) for item in self.data_ids] if self.data_ids is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'OscilloscopeReadResponse':
        return OscilloscopeReadResponse(
            data_ids=data.get('dataIds'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.data_ids is not None:
            if not isinstance(self.data_ids, Iterable):
                raise ValueError('Property "DataIds" of "OscilloscopeReadResponse" is not iterable.')

            for i, data_ids_item in enumerate(self.data_ids):
                if data_ids_item is None:
                    raise ValueError(f'Item {i} in property "DataIds" of "OscilloscopeReadResponse" is None.')

                if not isinstance(data_ids_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "DataIds" of "OscilloscopeReadResponse" is not a number.')

                if int(data_ids_item) != data_ids_item:
                    raise ValueError(f'Item {i} in property "DataIds" of "OscilloscopeReadResponse" is not integer value.')
