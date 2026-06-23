# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class AxisToStringRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    type_override: str = ""

    @staticmethod
    def zero_values() -> 'AxisToStringRequest':
        return AxisToStringRequest(
            interface_id=0,
            device=0,
            axis=0,
            type_override="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'AxisToStringRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return AxisToStringRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'typeOverride': str(self.type_override or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AxisToStringRequest':
        return AxisToStringRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            type_override=data.get('typeOverride'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "AxisToStringRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "AxisToStringRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "AxisToStringRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "AxisToStringRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "AxisToStringRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "AxisToStringRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "AxisToStringRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "AxisToStringRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "AxisToStringRequest" is not integer value.')

        if self.type_override is not None:
            if not isinstance(self.type_override, str):
                raise ValueError(f'Property "TypeOverride" of "AxisToStringRequest" is not a string.')
