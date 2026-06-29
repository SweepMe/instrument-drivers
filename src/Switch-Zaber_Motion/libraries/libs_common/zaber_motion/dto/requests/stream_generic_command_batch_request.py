# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class StreamGenericCommandBatchRequest:

    interface_id: int = 0

    device: int = 0

    stream_id: int = 0

    pvt: bool = False

    batch: List[str] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'StreamGenericCommandBatchRequest':
        return StreamGenericCommandBatchRequest(
            interface_id=0,
            device=0,
            stream_id=0,
            pvt=False,
            batch=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StreamGenericCommandBatchRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StreamGenericCommandBatchRequest.from_dict(data)

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
            'batch': [str(item or '') for item in self.batch] if self.batch is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StreamGenericCommandBatchRequest':
        return StreamGenericCommandBatchRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            stream_id=data.get('streamId'),  # type: ignore
            pvt=data.get('pvt'),  # type: ignore
            batch=data.get('batch'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "StreamGenericCommandBatchRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "StreamGenericCommandBatchRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "StreamGenericCommandBatchRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "StreamGenericCommandBatchRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "StreamGenericCommandBatchRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "StreamGenericCommandBatchRequest" is not integer value.')

        if self.stream_id is None:
            raise ValueError(f'Property "StreamId" of "StreamGenericCommandBatchRequest" is None.')

        if not isinstance(self.stream_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "StreamId" of "StreamGenericCommandBatchRequest" is not a number.')

        if int(self.stream_id) != self.stream_id:
            raise ValueError(f'Property "StreamId" of "StreamGenericCommandBatchRequest" is not integer value.')

        if self.batch is not None:
            if not isinstance(self.batch, Iterable):
                raise ValueError('Property "Batch" of "StreamGenericCommandBatchRequest" is not iterable.')

            for i, batch_item in enumerate(self.batch):
                if batch_item is not None:
                    if not isinstance(batch_item, str):
                        raise ValueError(f'Item {i} in property "Batch" of "StreamGenericCommandBatchRequest" is not a string.')
