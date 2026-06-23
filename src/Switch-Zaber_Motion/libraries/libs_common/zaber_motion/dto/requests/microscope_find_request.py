# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from ..microscopy.third_party_components import ThirdPartyComponents


@dataclass
class MicroscopeFindRequest:

    interface_id: int = 0

    third_party: Optional[ThirdPartyComponents] = None

    @staticmethod
    def zero_values() -> 'MicroscopeFindRequest':
        return MicroscopeFindRequest(
            interface_id=0,
            third_party=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MicroscopeFindRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MicroscopeFindRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'thirdParty': self.third_party.to_dict() if self.third_party is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MicroscopeFindRequest':
        return MicroscopeFindRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            third_party=ThirdPartyComponents.from_dict(data.get('thirdParty')) if data.get('thirdParty') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "MicroscopeFindRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "MicroscopeFindRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "MicroscopeFindRequest" is not integer value.')

        if self.third_party is not None:
            if not isinstance(self.third_party, ThirdPartyComponents):
                raise ValueError(f'Property "ThirdParty" of "MicroscopeFindRequest" is not an instance of "ThirdPartyComponents".')

            self.third_party.validate()
