# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class StreamBufferList:

    interface_id: int = 0

    device: int = 0

    pvt: bool = False

    @staticmethod
    def zero_values() -> 'StreamBufferList':
        return StreamBufferList(
            interface_id=0,
            device=0,
            pvt=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StreamBufferList':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StreamBufferList.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'pvt': bool(self.pvt),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StreamBufferList':
        return StreamBufferList(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            pvt=data.get('pvt'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "StreamBufferList" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "StreamBufferList" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "StreamBufferList" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "StreamBufferList" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "StreamBufferList" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "StreamBufferList" is not integer value.')
