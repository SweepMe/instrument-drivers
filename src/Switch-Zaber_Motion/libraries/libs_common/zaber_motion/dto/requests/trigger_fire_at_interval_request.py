# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class TriggerFireAtIntervalRequest:

    interface_id: int = 0

    device: int = 0

    trigger_number: int = 0

    interval: float = 0

    unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'TriggerFireAtIntervalRequest':
        return TriggerFireAtIntervalRequest(
            interface_id=0,
            device=0,
            trigger_number=0,
            interval=0,
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TriggerFireAtIntervalRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TriggerFireAtIntervalRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'triggerNumber': int(self.trigger_number),
            'interval': float(self.interval),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TriggerFireAtIntervalRequest':
        return TriggerFireAtIntervalRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            trigger_number=data.get('triggerNumber'),  # type: ignore
            interval=data.get('interval'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "TriggerFireAtIntervalRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "TriggerFireAtIntervalRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "TriggerFireAtIntervalRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "TriggerFireAtIntervalRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "TriggerFireAtIntervalRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "TriggerFireAtIntervalRequest" is not integer value.')

        if self.trigger_number is None:
            raise ValueError(f'Property "TriggerNumber" of "TriggerFireAtIntervalRequest" is None.')

        if not isinstance(self.trigger_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TriggerNumber" of "TriggerFireAtIntervalRequest" is not a number.')

        if int(self.trigger_number) != self.trigger_number:
            raise ValueError(f'Property "TriggerNumber" of "TriggerFireAtIntervalRequest" is not integer value.')

        if self.interval is None:
            raise ValueError(f'Property "Interval" of "TriggerFireAtIntervalRequest" is None.')

        if not isinstance(self.interval, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Interval" of "TriggerFireAtIntervalRequest" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "TriggerFireAtIntervalRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "TriggerFireAtIntervalRequest" is not Units.')
