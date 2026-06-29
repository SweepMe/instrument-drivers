# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class Ge1xGripperOpenConnectionRequest:

    port_name: str = ""

    device_address: int = 0

    timeout: int = 0

    @staticmethod
    def zero_values() -> 'Ge1xGripperOpenConnectionRequest':
        return Ge1xGripperOpenConnectionRequest(
            port_name="",
            device_address=0,
            timeout=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'Ge1xGripperOpenConnectionRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return Ge1xGripperOpenConnectionRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'portName': str(self.port_name or ''),
            'deviceAddress': int(self.device_address),
            'timeout': int(self.timeout),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Ge1xGripperOpenConnectionRequest':
        return Ge1xGripperOpenConnectionRequest(
            port_name=data.get('portName'),  # type: ignore
            device_address=data.get('deviceAddress'),  # type: ignore
            timeout=data.get('timeout'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.port_name is not None:
            if not isinstance(self.port_name, str):
                raise ValueError(f'Property "PortName" of "Ge1xGripperOpenConnectionRequest" is not a string.')

        if self.device_address is None:
            raise ValueError(f'Property "DeviceAddress" of "Ge1xGripperOpenConnectionRequest" is None.')

        if not isinstance(self.device_address, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "DeviceAddress" of "Ge1xGripperOpenConnectionRequest" is not a number.')

        if int(self.device_address) != self.device_address:
            raise ValueError(f'Property "DeviceAddress" of "Ge1xGripperOpenConnectionRequest" is not integer value.')

        if self.timeout is None:
            raise ValueError(f'Property "Timeout" of "Ge1xGripperOpenConnectionRequest" is None.')

        if not isinstance(self.timeout, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Timeout" of "Ge1xGripperOpenConnectionRequest" is not a number.')

        if int(self.timeout) != self.timeout:
            raise ValueError(f'Property "Timeout" of "Ge1xGripperOpenConnectionRequest" is not integer value.')
