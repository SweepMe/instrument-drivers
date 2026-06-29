# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class StreamSetupStoreRequest:

    interface_id: int = 0

    device: int = 0

    stream_id: int = 0

    pvt: bool = False

    stream_buffer: int = 0

    pvt_buffer: int = 0

    axes: List[int] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'StreamSetupStoreRequest':
        return StreamSetupStoreRequest(
            interface_id=0,
            device=0,
            stream_id=0,
            pvt=False,
            stream_buffer=0,
            pvt_buffer=0,
            axes=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StreamSetupStoreRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StreamSetupStoreRequest.from_dict(data)

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
            'streamBuffer': int(self.stream_buffer),
            'pvtBuffer': int(self.pvt_buffer),
            'axes': [int(item) for item in self.axes] if self.axes is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StreamSetupStoreRequest':
        return StreamSetupStoreRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            stream_id=data.get('streamId'),  # type: ignore
            pvt=data.get('pvt'),  # type: ignore
            stream_buffer=data.get('streamBuffer'),  # type: ignore
            pvt_buffer=data.get('pvtBuffer'),  # type: ignore
            axes=data.get('axes'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "StreamSetupStoreRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "StreamSetupStoreRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "StreamSetupStoreRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "StreamSetupStoreRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "StreamSetupStoreRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "StreamSetupStoreRequest" is not integer value.')

        if self.stream_id is None:
            raise ValueError(f'Property "StreamId" of "StreamSetupStoreRequest" is None.')

        if not isinstance(self.stream_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "StreamId" of "StreamSetupStoreRequest" is not a number.')

        if int(self.stream_id) != self.stream_id:
            raise ValueError(f'Property "StreamId" of "StreamSetupStoreRequest" is not integer value.')

        if self.stream_buffer is None:
            raise ValueError(f'Property "StreamBuffer" of "StreamSetupStoreRequest" is None.')

        if not isinstance(self.stream_buffer, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "StreamBuffer" of "StreamSetupStoreRequest" is not a number.')

        if int(self.stream_buffer) != self.stream_buffer:
            raise ValueError(f'Property "StreamBuffer" of "StreamSetupStoreRequest" is not integer value.')

        if self.pvt_buffer is None:
            raise ValueError(f'Property "PvtBuffer" of "StreamSetupStoreRequest" is None.')

        if not isinstance(self.pvt_buffer, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "PvtBuffer" of "StreamSetupStoreRequest" is not a number.')

        if int(self.pvt_buffer) != self.pvt_buffer:
            raise ValueError(f'Property "PvtBuffer" of "StreamSetupStoreRequest" is not integer value.')

        if self.axes is not None:
            if not isinstance(self.axes, Iterable):
                raise ValueError('Property "Axes" of "StreamSetupStoreRequest" is not iterable.')

            for i, axes_item in enumerate(self.axes):
                if axes_item is None:
                    raise ValueError(f'Item {i} in property "Axes" of "StreamSetupStoreRequest" is None.')

                if not isinstance(axes_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "Axes" of "StreamSetupStoreRequest" is not a number.')

                if int(axes_item) != axes_item:
                    raise ValueError(f'Item {i} in property "Axes" of "StreamSetupStoreRequest" is not integer value.')
