# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from ..firmware_version import FirmwareVersion


@dataclass
class CanSetStateRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    state: str = ""

    firmware_version: Optional[FirmwareVersion] = None

    @staticmethod
    def zero_values() -> 'CanSetStateRequest':
        return CanSetStateRequest(
            interface_id=0,
            device=0,
            axis=0,
            state="",
            firmware_version=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'CanSetStateRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return CanSetStateRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'state': str(self.state or ''),
            'firmwareVersion': self.firmware_version.to_dict() if self.firmware_version is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CanSetStateRequest':
        return CanSetStateRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            state=data.get('state'),  # type: ignore
            firmware_version=FirmwareVersion.from_dict(data.get('firmwareVersion')) if data.get('firmwareVersion') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "CanSetStateRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "CanSetStateRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "CanSetStateRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "CanSetStateRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "CanSetStateRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "CanSetStateRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "CanSetStateRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "CanSetStateRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "CanSetStateRequest" is not integer value.')

        if self.state is not None:
            if not isinstance(self.state, str):
                raise ValueError(f'Property "State" of "CanSetStateRequest" is not a string.')

        if self.firmware_version is not None:
            if not isinstance(self.firmware_version, FirmwareVersion):
                raise ValueError(f'Property "FirmwareVersion" of "CanSetStateRequest" is not an instance of "FirmwareVersion".')

            self.firmware_version.validate()
