# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class OscilloscopeDataGetRequest:

    data_id: int = 0

    unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'OscilloscopeDataGetRequest':
        return OscilloscopeDataGetRequest(
            data_id=0,
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'OscilloscopeDataGetRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return OscilloscopeDataGetRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'dataId': int(self.data_id),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'OscilloscopeDataGetRequest':
        return OscilloscopeDataGetRequest(
            data_id=data.get('dataId'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.data_id is None:
            raise ValueError(f'Property "DataId" of "OscilloscopeDataGetRequest" is None.')

        if not isinstance(self.data_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "DataId" of "OscilloscopeDataGetRequest" is not a number.')

        if int(self.data_id) != self.data_id:
            raise ValueError(f'Property "DataId" of "OscilloscopeDataGetRequest" is not integer value.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "OscilloscopeDataGetRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "OscilloscopeDataGetRequest" is not Units.')
