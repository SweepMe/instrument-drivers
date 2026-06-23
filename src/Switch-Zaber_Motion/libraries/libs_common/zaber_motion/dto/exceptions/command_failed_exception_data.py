# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class CommandFailedExceptionData:
    """
    Contains additional data for CommandFailedException.
    """

    command: str
    """
    The command that got rejected.
    """

    response_data: str
    """
    The data from the reply containing the rejection reason.
    """

    reply_flag: str
    """
    The flag indicating that the command was rejected.
    """

    status: str
    """
    The current device or axis status.
    """

    warning_flag: str
    """
    The highest priority warning flag on the device or axis.
    """

    device_address: int
    """
    The address of the device that rejected the command.
    """

    axis_number: int
    """
    The number of the axis which the rejection relates to.
    """

    id: int
    """
    The message ID of the reply.
    """

    @staticmethod
    def zero_values() -> 'CommandFailedExceptionData':
        return CommandFailedExceptionData(
            command="",
            response_data="",
            reply_flag="",
            status="",
            warning_flag="",
            device_address=0,
            axis_number=0,
            id=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'CommandFailedExceptionData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return CommandFailedExceptionData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'command': str(self.command or ''),
            'responseData': str(self.response_data or ''),
            'replyFlag': str(self.reply_flag or ''),
            'status': str(self.status or ''),
            'warningFlag': str(self.warning_flag or ''),
            'deviceAddress': int(self.device_address),
            'axisNumber': int(self.axis_number),
            'id': int(self.id),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'CommandFailedExceptionData':
        return CommandFailedExceptionData(
            command=data.get('command'),  # type: ignore
            response_data=data.get('responseData'),  # type: ignore
            reply_flag=data.get('replyFlag'),  # type: ignore
            status=data.get('status'),  # type: ignore
            warning_flag=data.get('warningFlag'),  # type: ignore
            device_address=data.get('deviceAddress'),  # type: ignore
            axis_number=data.get('axisNumber'),  # type: ignore
            id=data.get('id'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.command is not None:
            if not isinstance(self.command, str):
                raise ValueError(f'Property "Command" of "CommandFailedExceptionData" is not a string.')

        if self.response_data is not None:
            if not isinstance(self.response_data, str):
                raise ValueError(f'Property "ResponseData" of "CommandFailedExceptionData" is not a string.')

        if self.reply_flag is not None:
            if not isinstance(self.reply_flag, str):
                raise ValueError(f'Property "ReplyFlag" of "CommandFailedExceptionData" is not a string.')

        if self.status is not None:
            if not isinstance(self.status, str):
                raise ValueError(f'Property "Status" of "CommandFailedExceptionData" is not a string.')

        if self.warning_flag is not None:
            if not isinstance(self.warning_flag, str):
                raise ValueError(f'Property "WarningFlag" of "CommandFailedExceptionData" is not a string.')

        if self.device_address is None:
            raise ValueError(f'Property "DeviceAddress" of "CommandFailedExceptionData" is None.')

        if not isinstance(self.device_address, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "DeviceAddress" of "CommandFailedExceptionData" is not a number.')

        if int(self.device_address) != self.device_address:
            raise ValueError(f'Property "DeviceAddress" of "CommandFailedExceptionData" is not integer value.')

        if self.axis_number is None:
            raise ValueError(f'Property "AxisNumber" of "CommandFailedExceptionData" is None.')

        if not isinstance(self.axis_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "AxisNumber" of "CommandFailedExceptionData" is not a number.')

        if int(self.axis_number) != self.axis_number:
            raise ValueError(f'Property "AxisNumber" of "CommandFailedExceptionData" is not integer value.')

        if self.id is None:
            raise ValueError(f'Property "Id" of "CommandFailedExceptionData" is None.')

        if not isinstance(self.id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Id" of "CommandFailedExceptionData" is not a number.')

        if int(self.id) != self.id:
            raise ValueError(f'Property "Id" of "CommandFailedExceptionData" is not integer value.')
