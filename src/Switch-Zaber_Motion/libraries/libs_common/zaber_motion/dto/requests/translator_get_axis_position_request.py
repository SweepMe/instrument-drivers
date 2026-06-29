# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class TranslatorGetAxisPositionRequest:

    translator_id: int = 0

    axis: str = ""

    unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'TranslatorGetAxisPositionRequest':
        return TranslatorGetAxisPositionRequest(
            translator_id=0,
            axis="",
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TranslatorGetAxisPositionRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TranslatorGetAxisPositionRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'translatorId': int(self.translator_id),
            'axis': str(self.axis or ''),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TranslatorGetAxisPositionRequest':
        return TranslatorGetAxisPositionRequest(
            translator_id=data.get('translatorId'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.translator_id is None:
            raise ValueError(f'Property "TranslatorId" of "TranslatorGetAxisPositionRequest" is None.')

        if not isinstance(self.translator_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TranslatorId" of "TranslatorGetAxisPositionRequest" is not a number.')

        if int(self.translator_id) != self.translator_id:
            raise ValueError(f'Property "TranslatorId" of "TranslatorGetAxisPositionRequest" is not integer value.')

        if self.axis is not None:
            if not isinstance(self.axis, str):
                raise ValueError(f'Property "Axis" of "TranslatorGetAxisPositionRequest" is not a string.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "TranslatorGetAxisPositionRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "TranslatorGetAxisPositionRequest" is not Units.')
