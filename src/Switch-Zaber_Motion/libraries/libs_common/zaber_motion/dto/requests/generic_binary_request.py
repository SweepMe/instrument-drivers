# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..binary.command_code import CommandCode


@dataclass
class GenericBinaryRequest:

    interface_id: int = 0

    device: int = 0

    command: CommandCode = next(first for first in CommandCode)

    data: int = 0

    check_errors: bool = False

    timeout: float = 0

    @staticmethod
    def zero_values() -> 'GenericBinaryRequest':
        return GenericBinaryRequest(
            interface_id=0,
            device=0,
            command=next(first for first in CommandCode),
            data=0,
            check_errors=False,
            timeout=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GenericBinaryRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GenericBinaryRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'command': self.command.value,
            'data': int(self.data),
            'checkErrors': bool(self.check_errors),
            'timeout': float(self.timeout),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GenericBinaryRequest':
        return GenericBinaryRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            command=CommandCode(data.get('command')),  # type: ignore
            data=data.get('data'),  # type: ignore
            check_errors=data.get('checkErrors'),  # type: ignore
            timeout=data.get('timeout'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "GenericBinaryRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "GenericBinaryRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "GenericBinaryRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "GenericBinaryRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "GenericBinaryRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "GenericBinaryRequest" is not integer value.')

        if self.command is None:
            raise ValueError(f'Property "Command" of "GenericBinaryRequest" is None.')

        if not isinstance(self.command, CommandCode):
            raise ValueError(f'Property "Command" of "GenericBinaryRequest" is not an instance of "CommandCode".')

        if self.data is None:
            raise ValueError(f'Property "Data" of "GenericBinaryRequest" is None.')

        if not isinstance(self.data, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Data" of "GenericBinaryRequest" is not a number.')

        if int(self.data) != self.data:
            raise ValueError(f'Property "Data" of "GenericBinaryRequest" is not integer value.')

        if self.timeout is None:
            raise ValueError(f'Property "Timeout" of "GenericBinaryRequest" is None.')

        if not isinstance(self.timeout, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Timeout" of "GenericBinaryRequest" is not a number.')
