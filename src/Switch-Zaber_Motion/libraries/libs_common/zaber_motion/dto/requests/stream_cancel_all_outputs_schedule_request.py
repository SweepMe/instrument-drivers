# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class StreamCancelAllOutputsScheduleRequest:

    interface_id: int = 0

    device: int = 0

    stream_id: int = 0

    pvt: bool = False

    analog: bool = False

    channels: List[bool] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'StreamCancelAllOutputsScheduleRequest':
        return StreamCancelAllOutputsScheduleRequest(
            interface_id=0,
            device=0,
            stream_id=0,
            pvt=False,
            analog=False,
            channels=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StreamCancelAllOutputsScheduleRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StreamCancelAllOutputsScheduleRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'streamId': int(self.stream_id),
            'pvt': bool(self.pvt),
            'analog': bool(self.analog),
            'channels': [bool(item) for item in self.channels] if self.channels is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StreamCancelAllOutputsScheduleRequest':
        return StreamCancelAllOutputsScheduleRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            stream_id=data.get('streamId'),  # type: ignore
            pvt=data.get('pvt'),  # type: ignore
            analog=data.get('analog'),  # type: ignore
            channels=data.get('channels'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "StreamCancelAllOutputsScheduleRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "StreamCancelAllOutputsScheduleRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "StreamCancelAllOutputsScheduleRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "StreamCancelAllOutputsScheduleRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "StreamCancelAllOutputsScheduleRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "StreamCancelAllOutputsScheduleRequest" is not integer value.')

        if self.stream_id is None:
            raise ValueError(f'Property "StreamId" of "StreamCancelAllOutputsScheduleRequest" is None.')

        if not isinstance(self.stream_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "StreamId" of "StreamCancelAllOutputsScheduleRequest" is not a number.')

        if int(self.stream_id) != self.stream_id:
            raise ValueError(f'Property "StreamId" of "StreamCancelAllOutputsScheduleRequest" is not integer value.')

        if self.channels is not None:
            if not isinstance(self.channels, Iterable):
                raise ValueError('Property "Channels" of "StreamCancelAllOutputsScheduleRequest" is not iterable.')
