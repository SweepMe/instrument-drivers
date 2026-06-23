# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class AxisEmptyRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    @staticmethod
    def zero_values() -> 'AxisEmptyRequest':
        return AxisEmptyRequest(
            interface_id=0,
            device=0,
            axis=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'AxisEmptyRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return AxisEmptyRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AxisEmptyRequest':
        return AxisEmptyRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "AxisEmptyRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "AxisEmptyRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "AxisEmptyRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "AxisEmptyRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "AxisEmptyRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "AxisEmptyRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "AxisEmptyRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "AxisEmptyRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "AxisEmptyRequest" is not integer value.')
