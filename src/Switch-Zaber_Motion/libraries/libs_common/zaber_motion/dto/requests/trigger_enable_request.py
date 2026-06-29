# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class TriggerEnableRequest:

    interface_id: int = 0

    device: int = 0

    trigger_number: int = 0

    count: int = 0

    @staticmethod
    def zero_values() -> 'TriggerEnableRequest':
        return TriggerEnableRequest(
            interface_id=0,
            device=0,
            trigger_number=0,
            count=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TriggerEnableRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TriggerEnableRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'triggerNumber': int(self.trigger_number),
            'count': int(self.count),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TriggerEnableRequest':
        return TriggerEnableRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            trigger_number=data.get('triggerNumber'),  # type: ignore
            count=data.get('count'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "TriggerEnableRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "TriggerEnableRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "TriggerEnableRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "TriggerEnableRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "TriggerEnableRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "TriggerEnableRequest" is not integer value.')

        if self.trigger_number is None:
            raise ValueError(f'Property "TriggerNumber" of "TriggerEnableRequest" is None.')

        if not isinstance(self.trigger_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TriggerNumber" of "TriggerEnableRequest" is not a number.')

        if int(self.trigger_number) != self.trigger_number:
            raise ValueError(f'Property "TriggerNumber" of "TriggerEnableRequest" is not integer value.')

        if self.count is None:
            raise ValueError(f'Property "Count" of "TriggerEnableRequest" is None.')

        if not isinstance(self.count, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Count" of "TriggerEnableRequest" is not a number.')

        if int(self.count) != self.count:
            raise ValueError(f'Property "Count" of "TriggerEnableRequest" is not integer value.')
