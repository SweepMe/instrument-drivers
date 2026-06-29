# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from .device_port_type import DevicePortType


@dataclass
class DeviceDiscoveryResult:
    """
    Represents result of mDNS discovery for devices connected to network.
    """

    hostname: str
    """
    Host name of the discoverd device.
    """

    address: str
    """
    IP address of the discoverd device.
    """

    port: int
    """
    Port number of the discovered device.
    """

    port_type: DevicePortType
    """
    Indicates if discovery result represents a single device or a device chain.
    """

    device_id: int
    """
    Device id of discovered device or head of discovered device chain.
    """

    serial_number: int
    """
    Serial number of discovered device or head of discovered device chain.
    """

    @staticmethod
    def zero_values() -> 'DeviceDiscoveryResult':
        return DeviceDiscoveryResult(
            hostname="",
            address="",
            port=0,
            port_type=next(first for first in DevicePortType),
            device_id=0,
            serial_number=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceDiscoveryResult':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceDiscoveryResult.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'hostname': str(self.hostname or ''),
            'address': str(self.address or ''),
            'port': int(self.port),
            'portType': self.port_type.value,
            'deviceId': int(self.device_id),
            'serialNumber': int(self.serial_number),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceDiscoveryResult':
        return DeviceDiscoveryResult(
            hostname=data.get('hostname'),  # type: ignore
            address=data.get('address'),  # type: ignore
            port=data.get('port'),  # type: ignore
            port_type=DevicePortType(data.get('portType')),  # type: ignore
            device_id=data.get('deviceId'),  # type: ignore
            serial_number=data.get('serialNumber'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.hostname is not None:
            if not isinstance(self.hostname, str):
                raise ValueError(f'Property "Hostname" of "DeviceDiscoveryResult" is not a string.')

        if self.address is not None:
            if not isinstance(self.address, str):
                raise ValueError(f'Property "Address" of "DeviceDiscoveryResult" is not a string.')

        if self.port is None:
            raise ValueError(f'Property "Port" of "DeviceDiscoveryResult" is None.')

        if not isinstance(self.port, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Port" of "DeviceDiscoveryResult" is not a number.')

        if int(self.port) != self.port:
            raise ValueError(f'Property "Port" of "DeviceDiscoveryResult" is not integer value.')

        if self.port_type is None:
            raise ValueError(f'Property "PortType" of "DeviceDiscoveryResult" is None.')

        if not isinstance(self.port_type, DevicePortType):
            raise ValueError(f'Property "PortType" of "DeviceDiscoveryResult" is not an instance of "DevicePortType".')

        if self.device_id is None:
            raise ValueError(f'Property "DeviceId" of "DeviceDiscoveryResult" is None.')

        if not isinstance(self.device_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "DeviceId" of "DeviceDiscoveryResult" is not a number.')

        if int(self.device_id) != self.device_id:
            raise ValueError(f'Property "DeviceId" of "DeviceDiscoveryResult" is not integer value.')

        if self.serial_number is None:
            raise ValueError(f'Property "SerialNumber" of "DeviceDiscoveryResult" is None.')

        if not isinstance(self.serial_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "SerialNumber" of "DeviceDiscoveryResult" is not a number.')

        if int(self.serial_number) != self.serial_number:
            raise ValueError(f'Property "SerialNumber" of "DeviceDiscoveryResult" is not integer value.')
