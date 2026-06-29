# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class WaitToClearWarningsRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    timeout: float = 0

    warning_flags: List[str] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'WaitToClearWarningsRequest':
        return WaitToClearWarningsRequest(
            interface_id=0,
            device=0,
            axis=0,
            timeout=0,
            warning_flags=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'WaitToClearWarningsRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return WaitToClearWarningsRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'timeout': float(self.timeout),
            'warningFlags': [str(item or '') for item in self.warning_flags] if self.warning_flags is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'WaitToClearWarningsRequest':
        return WaitToClearWarningsRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            timeout=data.get('timeout'),  # type: ignore
            warning_flags=data.get('warningFlags'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "WaitToClearWarningsRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "WaitToClearWarningsRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "WaitToClearWarningsRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "WaitToClearWarningsRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "WaitToClearWarningsRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "WaitToClearWarningsRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "WaitToClearWarningsRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "WaitToClearWarningsRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "WaitToClearWarningsRequest" is not integer value.')

        if self.timeout is None:
            raise ValueError(f'Property "Timeout" of "WaitToClearWarningsRequest" is None.')

        if not isinstance(self.timeout, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Timeout" of "WaitToClearWarningsRequest" is not a number.')

        if self.warning_flags is not None:
            if not isinstance(self.warning_flags, Iterable):
                raise ValueError('Property "WarningFlags" of "WaitToClearWarningsRequest" is not iterable.')

            for i, warning_flags_item in enumerate(self.warning_flags):
                if warning_flags_item is not None:
                    if not isinstance(warning_flags_item, str):
                        raise ValueError(f'Item {i} in property "WarningFlags" of "WaitToClearWarningsRequest" is not a string.')
