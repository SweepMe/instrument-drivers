# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import decimal
from collections.abc import Iterable
import zaber_bson
from .interface_type import InterfaceType
from ..ascii.mock_device import MockDevice


@dataclass
class OpenInterfaceRequest:

    interface_type: InterfaceType = next(first for first in InterfaceType)

    port_name: str = ""

    baud_rate: int = 0

    host_name: str = ""

    port: int = 0

    transport: int = 0

    reject_routed_connection: bool = False

    cloud_id: str = ""

    token: str = ""

    api: str = ""

    test_port: bool = False

    connection_name: Optional[str] = None

    realm: Optional[str] = None

    mock_devices: Optional[List[MockDevice]] = None

    @staticmethod
    def zero_values() -> 'OpenInterfaceRequest':
        return OpenInterfaceRequest(
            interface_type=next(first for first in InterfaceType),
            port_name="",
            baud_rate=0,
            host_name="",
            port=0,
            transport=0,
            reject_routed_connection=False,
            cloud_id="",
            connection_name=None,
            realm=None,
            token="",
            api="",
            test_port=False,
            mock_devices=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'OpenInterfaceRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return OpenInterfaceRequest.from_dict(data)

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
            'transport': int(self.transport),
            'rejectRoutedConnection': bool(self.reject_routed_connection),
            'cloudId': str(self.cloud_id or ''),
            'connectionName': str(self.connection_name) if self.connection_name is not None else None,
            'realm': str(self.realm) if self.realm is not None else None,
            'token': str(self.token or ''),
            'api': str(self.api or ''),
            'testPort': bool(self.test_port),
            'mockDevices': [item.to_dict() for item in self.mock_devices] if self.mock_devices is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'OpenInterfaceRequest':
        return OpenInterfaceRequest(
            interface_type=InterfaceType(data.get('interfaceType')),  # type: ignore
            port_name=data.get('portName'),  # type: ignore
            baud_rate=data.get('baudRate'),  # type: ignore
            host_name=data.get('hostName'),  # type: ignore
            port=data.get('port'),  # type: ignore
            transport=data.get('transport'),  # type: ignore
            reject_routed_connection=data.get('rejectRoutedConnection'),  # type: ignore
            cloud_id=data.get('cloudId'),  # type: ignore
            connection_name=data.get('connectionName'),  # type: ignore
            realm=data.get('realm'),  # type: ignore
            token=data.get('token'),  # type: ignore
            api=data.get('api'),  # type: ignore
            test_port=data.get('testPort'),  # type: ignore
            mock_devices=[MockDevice.from_dict(item) for item in data.get('mockDevices')] if data.get('mockDevices') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_type is None:
            raise ValueError(f'Property "InterfaceType" of "OpenInterfaceRequest" is None.')

        if not isinstance(self.interface_type, InterfaceType):
            raise ValueError(f'Property "InterfaceType" of "OpenInterfaceRequest" is not an instance of "InterfaceType".')

        if self.port_name is not None:
            if not isinstance(self.port_name, str):
                raise ValueError(f'Property "PortName" of "OpenInterfaceRequest" is not a string.')

        if self.baud_rate is None:
            raise ValueError(f'Property "BaudRate" of "OpenInterfaceRequest" is None.')

        if not isinstance(self.baud_rate, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "BaudRate" of "OpenInterfaceRequest" is not a number.')

        if int(self.baud_rate) != self.baud_rate:
            raise ValueError(f'Property "BaudRate" of "OpenInterfaceRequest" is not integer value.')

        if self.host_name is not None:
            if not isinstance(self.host_name, str):
                raise ValueError(f'Property "HostName" of "OpenInterfaceRequest" is not a string.')

        if self.port is None:
            raise ValueError(f'Property "Port" of "OpenInterfaceRequest" is None.')

        if not isinstance(self.port, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Port" of "OpenInterfaceRequest" is not a number.')

        if int(self.port) != self.port:
            raise ValueError(f'Property "Port" of "OpenInterfaceRequest" is not integer value.')

        if self.transport is None:
            raise ValueError(f'Property "Transport" of "OpenInterfaceRequest" is None.')

        if not isinstance(self.transport, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Transport" of "OpenInterfaceRequest" is not a number.')

        if int(self.transport) != self.transport:
            raise ValueError(f'Property "Transport" of "OpenInterfaceRequest" is not integer value.')

        if self.cloud_id is not None:
            if not isinstance(self.cloud_id, str):
                raise ValueError(f'Property "CloudId" of "OpenInterfaceRequest" is not a string.')

        if self.connection_name is not None:
            if not isinstance(self.connection_name, str):
                raise ValueError(f'Property "ConnectionName" of "OpenInterfaceRequest" is not a string.')

        if self.realm is not None:
            if not isinstance(self.realm, str):
                raise ValueError(f'Property "Realm" of "OpenInterfaceRequest" is not a string.')

        if self.token is not None:
            if not isinstance(self.token, str):
                raise ValueError(f'Property "Token" of "OpenInterfaceRequest" is not a string.')

        if self.api is not None:
            if not isinstance(self.api, str):
                raise ValueError(f'Property "Api" of "OpenInterfaceRequest" is not a string.')

        if self.mock_devices is not None:
            if not isinstance(self.mock_devices, Iterable):
                raise ValueError('Property "MockDevices" of "OpenInterfaceRequest" is not iterable.')

            for i, mock_devices_item in enumerate(self.mock_devices):
                if mock_devices_item is None:
                    raise ValueError(f'Item {i} in property "MockDevices" of "OpenInterfaceRequest" is None.')

                if not isinstance(mock_devices_item, MockDevice):
                    raise ValueError(f'Item {i} in property "MockDevices" of "OpenInterfaceRequest" is not an instance of "MockDevice".')

                mock_devices_item.validate()
