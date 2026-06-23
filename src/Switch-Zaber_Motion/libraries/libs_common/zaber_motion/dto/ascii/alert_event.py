# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class AlertEvent:
    """
    Alert message received from the device.
    """

    device_address: int
    """
    Number of the device that sent the message.
    """

    axis_number: int
    """
    Number of the axis which the response applies to. Zero denotes device scope.
    """

    status: str
    """
    The device status contains BUSY when the axis is moving and IDLE otherwise.
    """

    warning_flag: str
    """
    The warning flag contains the highest priority warning currently active for the device or axis.
    """

    data: str
    """
    Response data which varies depending on the request.
    """

    @staticmethod
    def zero_values() -> 'AlertEvent':
        return AlertEvent(
            device_address=0,
            axis_number=0,
            status="",
            warning_flag="",
            data="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'AlertEvent':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return AlertEvent.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'deviceAddress': int(self.device_address),
            'axisNumber': int(self.axis_number),
            'status': str(self.status or ''),
            'warningFlag': str(self.warning_flag or ''),
            'data': str(self.data or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AlertEvent':
        return AlertEvent(
            device_address=data.get('deviceAddress'),  # type: ignore
            axis_number=data.get('axisNumber'),  # type: ignore
            status=data.get('status'),  # type: ignore
            warning_flag=data.get('warningFlag'),  # type: ignore
            data=data.get('data'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.device_address is None:
            raise ValueError(f'Property "DeviceAddress" of "AlertEvent" is None.')

        if not isinstance(self.device_address, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "DeviceAddress" of "AlertEvent" is not a number.')

        if int(self.device_address) != self.device_address:
            raise ValueError(f'Property "DeviceAddress" of "AlertEvent" is not integer value.')

        if self.axis_number is None:
            raise ValueError(f'Property "AxisNumber" of "AlertEvent" is None.')

        if not isinstance(self.axis_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "AxisNumber" of "AlertEvent" is not a number.')

        if int(self.axis_number) != self.axis_number:
            raise ValueError(f'Property "AxisNumber" of "AlertEvent" is not integer value.')

        if self.status is not None:
            if not isinstance(self.status, str):
                raise ValueError(f'Property "Status" of "AlertEvent" is not a string.')

        if self.warning_flag is not None:
            if not isinstance(self.warning_flag, str):
                raise ValueError(f'Property "WarningFlag" of "AlertEvent" is not a string.')

        if self.data is not None:
            if not isinstance(self.data, str):
                raise ValueError(f'Property "Data" of "AlertEvent" is not a string.')
