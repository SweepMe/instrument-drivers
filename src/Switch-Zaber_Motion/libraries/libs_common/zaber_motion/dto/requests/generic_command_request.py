# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class GenericCommandRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    command: str = ""

    check_errors: bool = False

    timeout: int = 0

    @staticmethod
    def zero_values() -> 'GenericCommandRequest':
        return GenericCommandRequest(
            interface_id=0,
            device=0,
            axis=0,
            command="",
            check_errors=False,
            timeout=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GenericCommandRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GenericCommandRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'command': str(self.command or ''),
            'checkErrors': bool(self.check_errors),
            'timeout': int(self.timeout),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GenericCommandRequest':
        return GenericCommandRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            command=data.get('command'),  # type: ignore
            check_errors=data.get('checkErrors'),  # type: ignore
            timeout=data.get('timeout'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "GenericCommandRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "GenericCommandRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "GenericCommandRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "GenericCommandRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "GenericCommandRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "GenericCommandRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "GenericCommandRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "GenericCommandRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "GenericCommandRequest" is not integer value.')

        if self.command is not None:
            if not isinstance(self.command, str):
                raise ValueError(f'Property "Command" of "GenericCommandRequest" is not a string.')

        if self.timeout is None:
            raise ValueError(f'Property "Timeout" of "GenericCommandRequest" is None.')

        if not isinstance(self.timeout, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Timeout" of "GenericCommandRequest" is not a number.')

        if int(self.timeout) != self.timeout:
            raise ValueError(f'Property "Timeout" of "GenericCommandRequest" is not integer value.')
