# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class LockstepMoveSinRequest:

    interface_id: int = 0

    device: int = 0

    lockstep_group_id: int = 0

    amplitude: float = 0

    amplitude_units: UnitsAndLiterals = Units.NATIVE

    period: float = 0

    period_units: UnitsAndLiterals = Units.NATIVE

    count: float = 0

    wait_until_idle: bool = False

    @staticmethod
    def zero_values() -> 'LockstepMoveSinRequest':
        return LockstepMoveSinRequest(
            interface_id=0,
            device=0,
            lockstep_group_id=0,
            amplitude=0,
            amplitude_units=Units.NATIVE,
            period=0,
            period_units=Units.NATIVE,
            count=0,
            wait_until_idle=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'LockstepMoveSinRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return LockstepMoveSinRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'lockstepGroupId': int(self.lockstep_group_id),
            'amplitude': float(self.amplitude),
            'amplitudeUnits': units_from_literals(self.amplitude_units).value,
            'period': float(self.period),
            'periodUnits': units_from_literals(self.period_units).value,
            'count': float(self.count),
            'waitUntilIdle': bool(self.wait_until_idle),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LockstepMoveSinRequest':
        return LockstepMoveSinRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            lockstep_group_id=data.get('lockstepGroupId'),  # type: ignore
            amplitude=data.get('amplitude'),  # type: ignore
            amplitude_units=Units(data.get('amplitudeUnits')),  # type: ignore
            period=data.get('period'),  # type: ignore
            period_units=Units(data.get('periodUnits')),  # type: ignore
            count=data.get('count'),  # type: ignore
            wait_until_idle=data.get('waitUntilIdle'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "LockstepMoveSinRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "LockstepMoveSinRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "LockstepMoveSinRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "LockstepMoveSinRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "LockstepMoveSinRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "LockstepMoveSinRequest" is not integer value.')

        if self.lockstep_group_id is None:
            raise ValueError(f'Property "LockstepGroupId" of "LockstepMoveSinRequest" is None.')

        if not isinstance(self.lockstep_group_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "LockstepGroupId" of "LockstepMoveSinRequest" is not a number.')

        if int(self.lockstep_group_id) != self.lockstep_group_id:
            raise ValueError(f'Property "LockstepGroupId" of "LockstepMoveSinRequest" is not integer value.')

        if self.amplitude is None:
            raise ValueError(f'Property "Amplitude" of "LockstepMoveSinRequest" is None.')

        if not isinstance(self.amplitude, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Amplitude" of "LockstepMoveSinRequest" is not a number.')

        if self.amplitude_units is None:
            raise ValueError(f'Property "AmplitudeUnits" of "LockstepMoveSinRequest" is None.')

        if not isinstance(self.amplitude_units, (Units, str)):
            raise ValueError(f'Property "AmplitudeUnits" of "LockstepMoveSinRequest" is not Units.')

        if self.period is None:
            raise ValueError(f'Property "Period" of "LockstepMoveSinRequest" is None.')

        if not isinstance(self.period, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Period" of "LockstepMoveSinRequest" is not a number.')

        if self.period_units is None:
            raise ValueError(f'Property "PeriodUnits" of "LockstepMoveSinRequest" is None.')

        if not isinstance(self.period_units, (Units, str)):
            raise ValueError(f'Property "PeriodUnits" of "LockstepMoveSinRequest" is not Units.')

        if self.count is None:
            raise ValueError(f'Property "Count" of "LockstepMoveSinRequest" is None.')

        if not isinstance(self.count, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Count" of "LockstepMoveSinRequest" is not a number.')
