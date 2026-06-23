# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class TranslatorGetAxisOffsetRequest:

    translator_id: int = 0

    coordinate_system: str = ""

    axis: str = ""

    unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'TranslatorGetAxisOffsetRequest':
        return TranslatorGetAxisOffsetRequest(
            translator_id=0,
            coordinate_system="",
            axis="",
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TranslatorGetAxisOffsetRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TranslatorGetAxisOffsetRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'translatorId': int(self.translator_id),
            'coordinateSystem': str(self.coordinate_system or ''),
            'axis': str(self.axis or ''),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TranslatorGetAxisOffsetRequest':
        return TranslatorGetAxisOffsetRequest(
            translator_id=data.get('translatorId'),  # type: ignore
            coordinate_system=data.get('coordinateSystem'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.translator_id is None:
            raise ValueError(f'Property "TranslatorId" of "TranslatorGetAxisOffsetRequest" is None.')

        if not isinstance(self.translator_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TranslatorId" of "TranslatorGetAxisOffsetRequest" is not a number.')

        if int(self.translator_id) != self.translator_id:
            raise ValueError(f'Property "TranslatorId" of "TranslatorGetAxisOffsetRequest" is not integer value.')

        if self.coordinate_system is not None:
            if not isinstance(self.coordinate_system, str):
                raise ValueError(f'Property "CoordinateSystem" of "TranslatorGetAxisOffsetRequest" is not a string.')

        if self.axis is not None:
            if not isinstance(self.axis, str):
                raise ValueError(f'Property "Axis" of "TranslatorGetAxisOffsetRequest" is not a string.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "TranslatorGetAxisOffsetRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "TranslatorGetAxisOffsetRequest" is not Units.')
