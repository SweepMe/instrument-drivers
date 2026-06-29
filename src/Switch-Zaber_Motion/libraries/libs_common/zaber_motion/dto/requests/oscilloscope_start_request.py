# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class OscilloscopeStartRequest:

    interface_id: int = 0

    device: int = 0

    capture_length: int = 0

    @staticmethod
    def zero_values() -> 'OscilloscopeStartRequest':
        return OscilloscopeStartRequest(
            interface_id=0,
            device=0,
            capture_length=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'OscilloscopeStartRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return OscilloscopeStartRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'captureLength': int(self.capture_length),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'OscilloscopeStartRequest':
        return OscilloscopeStartRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            capture_length=data.get('captureLength'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "OscilloscopeStartRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "OscilloscopeStartRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "OscilloscopeStartRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "OscilloscopeStartRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "OscilloscopeStartRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "OscilloscopeStartRequest" is not integer value.')

        if self.capture_length is None:
            raise ValueError(f'Property "CaptureLength" of "OscilloscopeStartRequest" is None.')

        if not isinstance(self.capture_length, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "CaptureLength" of "OscilloscopeStartRequest" is not a number.')

        if int(self.capture_length) != self.capture_length:
            raise ValueError(f'Property "CaptureLength" of "OscilloscopeStartRequest" is not integer value.')
