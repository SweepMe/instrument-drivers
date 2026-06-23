# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson


@dataclass
class DiscoverMdnsRequest:

    duration: int = 0

    interface_ip_address: Optional[str] = None

    @staticmethod
    def zero_values() -> 'DiscoverMdnsRequest':
        return DiscoverMdnsRequest(
            duration=0,
            interface_ip_address=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DiscoverMdnsRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DiscoverMdnsRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'duration': int(self.duration),
            'interfaceIpAddress': str(self.interface_ip_address) if self.interface_ip_address is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DiscoverMdnsRequest':
        return DiscoverMdnsRequest(
            duration=data.get('duration'),  # type: ignore
            interface_ip_address=data.get('interfaceIpAddress'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.duration is None:
            raise ValueError(f'Property "Duration" of "DiscoverMdnsRequest" is None.')

        if not isinstance(self.duration, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Duration" of "DiscoverMdnsRequest" is not a number.')

        if int(self.duration) != self.duration:
            raise ValueError(f'Property "Duration" of "DiscoverMdnsRequest" is not integer value.')

        if self.interface_ip_address is not None:
            if not isinstance(self.interface_ip_address, str):
                raise ValueError(f'Property "InterfaceIpAddress" of "DiscoverMdnsRequest" is not a string.')
