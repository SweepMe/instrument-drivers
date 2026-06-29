# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class OscilloscopeDataGetSamplesResponse:

    data: List[float] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'OscilloscopeDataGetSamplesResponse':
        return OscilloscopeDataGetSamplesResponse(
            data=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'OscilloscopeDataGetSamplesResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return OscilloscopeDataGetSamplesResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'data': [float(item) for item in self.data] if self.data is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'OscilloscopeDataGetSamplesResponse':
        return OscilloscopeDataGetSamplesResponse(
            data=data.get('data'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.data is not None:
            if not isinstance(self.data, Iterable):
                raise ValueError('Property "Data" of "OscilloscopeDataGetSamplesResponse" is not iterable.')

            for i, data_item in enumerate(self.data):
                if data_item is None:
                    raise ValueError(f'Item {i} in property "Data" of "OscilloscopeDataGetSamplesResponse" is None.')

                if not isinstance(data_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "Data" of "OscilloscopeDataGetSamplesResponse" is not a number.')
