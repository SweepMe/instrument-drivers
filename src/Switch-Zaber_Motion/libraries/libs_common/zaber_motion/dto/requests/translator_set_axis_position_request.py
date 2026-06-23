# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class TranslatorSetAxisPositionRequest:

    translator_id: int = 0

    axis: str = ""

    position: float = 0

    unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'TranslatorSetAxisPositionRequest':
        return TranslatorSetAxisPositionRequest(
            translator_id=0,
            axis="",
            position=0,
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TranslatorSetAxisPositionRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TranslatorSetAxisPositionRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'translatorId': int(self.translator_id),
            'axis': str(self.axis or ''),
            'position': float(self.position),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TranslatorSetAxisPositionRequest':
        return TranslatorSetAxisPositionRequest(
            translator_id=data.get('translatorId'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            position=data.get('position'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.translator_id is None:
            raise ValueError(f'Property "TranslatorId" of "TranslatorSetAxisPositionRequest" is None.')

        if not isinstance(self.translator_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TranslatorId" of "TranslatorSetAxisPositionRequest" is not a number.')

        if int(self.translator_id) != self.translator_id:
            raise ValueError(f'Property "TranslatorId" of "TranslatorSetAxisPositionRequest" is not integer value.')

        if self.axis is not None:
            if not isinstance(self.axis, str):
                raise ValueError(f'Property "Axis" of "TranslatorSetAxisPositionRequest" is not a string.')

        if self.position is None:
            raise ValueError(f'Property "Position" of "TranslatorSetAxisPositionRequest" is None.')

        if not isinstance(self.position, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Position" of "TranslatorSetAxisPositionRequest" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "TranslatorSetAxisPositionRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "TranslatorSetAxisPositionRequest" is not Units.')
