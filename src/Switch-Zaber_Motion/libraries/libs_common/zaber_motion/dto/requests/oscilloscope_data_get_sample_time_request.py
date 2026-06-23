# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class OscilloscopeDataGetSampleTimeRequest:

    data_id: int = 0

    unit: UnitsAndLiterals = Units.NATIVE

    index: int = 0

    @staticmethod
    def zero_values() -> 'OscilloscopeDataGetSampleTimeRequest':
        return OscilloscopeDataGetSampleTimeRequest(
            data_id=0,
            unit=Units.NATIVE,
            index=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'OscilloscopeDataGetSampleTimeRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return OscilloscopeDataGetSampleTimeRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'dataId': int(self.data_id),
            'unit': units_from_literals(self.unit).value,
            'index': int(self.index),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'OscilloscopeDataGetSampleTimeRequest':
        return OscilloscopeDataGetSampleTimeRequest(
            data_id=data.get('dataId'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
            index=data.get('index'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.data_id is None:
            raise ValueError(f'Property "DataId" of "OscilloscopeDataGetSampleTimeRequest" is None.')

        if not isinstance(self.data_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "DataId" of "OscilloscopeDataGetSampleTimeRequest" is not a number.')

        if int(self.data_id) != self.data_id:
            raise ValueError(f'Property "DataId" of "OscilloscopeDataGetSampleTimeRequest" is not integer value.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "OscilloscopeDataGetSampleTimeRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "OscilloscopeDataGetSampleTimeRequest" is not Units.')

        if self.index is None:
            raise ValueError(f'Property "Index" of "OscilloscopeDataGetSampleTimeRequest" is None.')

        if not isinstance(self.index, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Index" of "OscilloscopeDataGetSampleTimeRequest" is not a number.')

        if int(self.index) != self.index:
            raise ValueError(f'Property "Index" of "OscilloscopeDataGetSampleTimeRequest" is not integer value.')
