# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from .interface_type import InterfaceType


@dataclass
class OpenBinaryInterfaceRequest:

    interface_type: InterfaceType = next(first for first in InterfaceType)

    port_name: str = ""

    baud_rate: int = 0

    host_name: str = ""

    port: int = 0

    use_message_ids: bool = False

    @staticmethod
    def zero_values() -> 'OpenBinaryInterfaceRequest':
        return OpenBinaryInterfaceRequest(
            interface_type=next(first for first in InterfaceType),
            port_name="",
            baud_rate=0,
            host_name="",
            port=0,
            use_message_ids=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'OpenBinaryInterfaceRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return OpenBinaryInterfaceRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceType': self.interface_type.value,
            'portName': str(self.port_name or ''),
            'baudRate': int(self.baud_rate),
            'hostName': str(self.host_name or ''),
            'port': int(self.port),
            'useMessageIds': bool(self.use_message_ids),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'OpenBinaryInterfaceRequest':
        return OpenBinaryInterfaceRequest(
            interface_type=InterfaceType(data.get('interfaceType')),  # type: ignore
            port_name=data.get('portName'),  # type: ignore
            baud_rate=data.get('baudRate'),  # type: ignore
            host_name=data.get('hostName'),  # type: ignore
            port=data.get('port'),  # type: ignore
            use_message_ids=data.get('useMessageIds'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_type is None:
            raise ValueError(f'Property "InterfaceType" of "OpenBinaryInterfaceRequest" is None.')

        if not isinstance(self.interface_type, InterfaceType):
            raise ValueError(f'Property "InterfaceType" of "OpenBinaryInterfaceRequest" is not an instance of "InterfaceType".')

        if self.port_name is not None:
            if not isinstance(self.port_name, str):
                raise ValueError(f'Property "PortName" of "OpenBinaryInterfaceRequest" is not a string.')

        if self.baud_rate is None:
            raise ValueError(f'Property "BaudRate" of "OpenBinaryInterfaceRequest" is None.')

        if not isinstance(self.baud_rate, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "BaudRate" of "OpenBinaryInterfaceRequest" is not a number.')

        if int(self.baud_rate) != self.baud_rate:
            raise ValueError(f'Property "BaudRate" of "OpenBinaryInterfaceRequest" is not integer value.')

        if self.host_name is not None:
            if not isinstance(self.host_name, str):
                raise ValueError(f'Property "HostName" of "OpenBinaryInterfaceRequest" is not a string.')

        if self.port is None:
            raise ValueError(f'Property "Port" of "OpenBinaryInterfaceRequest" is None.')

        if not isinstance(self.port, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Port" of "OpenBinaryInterfaceRequest" is not a number.')

        if int(self.port) != self.port:
            raise ValueError(f'Property "Port" of "OpenBinaryInterfaceRequest" is not integer value.')
