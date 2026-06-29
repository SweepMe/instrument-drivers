# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class TranslatorTranslateRequest:

    translator_id: int = 0

    block: str = ""

    @staticmethod
    def zero_values() -> 'TranslatorTranslateRequest':
        return TranslatorTranslateRequest(
            translator_id=0,
            block="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TranslatorTranslateRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TranslatorTranslateRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'translatorId': int(self.translator_id),
            'block': str(self.block or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TranslatorTranslateRequest':
        return TranslatorTranslateRequest(
            translator_id=data.get('translatorId'),  # type: ignore
            block=data.get('block'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.translator_id is None:
            raise ValueError(f'Property "TranslatorId" of "TranslatorTranslateRequest" is None.')

        if not isinstance(self.translator_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TranslatorId" of "TranslatorTranslateRequest" is not a number.')

        if int(self.translator_id) != self.translator_id:
            raise ValueError(f'Property "TranslatorId" of "TranslatorTranslateRequest" is not integer value.')

        if self.block is not None:
            if not isinstance(self.block, str):
                raise ValueError(f'Property "Block" of "TranslatorTranslateRequest" is not a string.')
