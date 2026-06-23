# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class TranslatorSetTraverseRateRequest:

    translator_id: int = 0

    traverse_rate: float = 0

    unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'TranslatorSetTraverseRateRequest':
        return TranslatorSetTraverseRateRequest(
            translator_id=0,
            traverse_rate=0,
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TranslatorSetTraverseRateRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TranslatorSetTraverseRateRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'translatorId': int(self.translator_id),
            'traverseRate': float(self.traverse_rate),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TranslatorSetTraverseRateRequest':
        return TranslatorSetTraverseRateRequest(
            translator_id=data.get('translatorId'),  # type: ignore
            traverse_rate=data.get('traverseRate'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.translator_id is None:
            raise ValueError(f'Property "TranslatorId" of "TranslatorSetTraverseRateRequest" is None.')

        if not isinstance(self.translator_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TranslatorId" of "TranslatorSetTraverseRateRequest" is not a number.')

        if int(self.translator_id) != self.translator_id:
            raise ValueError(f'Property "TranslatorId" of "TranslatorSetTraverseRateRequest" is not integer value.')

        if self.traverse_rate is None:
            raise ValueError(f'Property "TraverseRate" of "TranslatorSetTraverseRateRequest" is None.')

        if not isinstance(self.traverse_rate, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TraverseRate" of "TranslatorSetTraverseRateRequest" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "TranslatorSetTraverseRateRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "TranslatorSetTraverseRateRequest" is not Units.')
