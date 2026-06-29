# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from ..ascii.digital_output_action import DigitalOutputAction


@dataclass
class DeviceSetAllDigitalOutputsRequest:

    interface_id: int = 0

    device: int = 0

    values: List[DigitalOutputAction] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'DeviceSetAllDigitalOutputsRequest':
        return DeviceSetAllDigitalOutputsRequest(
            interface_id=0,
            device=0,
            values=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceSetAllDigitalOutputsRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceSetAllDigitalOutputsRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'values': [item.value for item in self.values] if self.values is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceSetAllDigitalOutputsRequest':
        return DeviceSetAllDigitalOutputsRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            values=[DigitalOutputAction(item) for item in data.get('values')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DeviceSetAllDigitalOutputsRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DeviceSetAllDigitalOutputsRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DeviceSetAllDigitalOutputsRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "DeviceSetAllDigitalOutputsRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "DeviceSetAllDigitalOutputsRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "DeviceSetAllDigitalOutputsRequest" is not integer value.')

        if self.values is not None:
            if not isinstance(self.values, Iterable):
                raise ValueError('Property "Values" of "DeviceSetAllDigitalOutputsRequest" is not iterable.')

            for i, values_item in enumerate(self.values):
                if values_item is None:
                    raise ValueError(f'Item {i} in property "Values" of "DeviceSetAllDigitalOutputsRequest" is None.')

                if not isinstance(values_item, DigitalOutputAction):
                    raise ValueError(f'Item {i} in property "Values" of "DeviceSetAllDigitalOutputsRequest" is not an instance of "DigitalOutputAction".')
