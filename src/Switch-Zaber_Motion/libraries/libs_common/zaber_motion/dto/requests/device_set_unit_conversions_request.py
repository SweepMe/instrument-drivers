# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from ..ascii.conversion_factor import ConversionFactor


@dataclass
class DeviceSetUnitConversionsRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    key: str = ""

    conversions: List[ConversionFactor] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'DeviceSetUnitConversionsRequest':
        return DeviceSetUnitConversionsRequest(
            interface_id=0,
            device=0,
            axis=0,
            key="",
            conversions=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceSetUnitConversionsRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceSetUnitConversionsRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'key': str(self.key or ''),
            'conversions': [item.to_dict() for item in self.conversions] if self.conversions is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceSetUnitConversionsRequest':
        return DeviceSetUnitConversionsRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            key=data.get('key'),  # type: ignore
            conversions=[ConversionFactor.from_dict(item) for item in data.get('conversions')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DeviceSetUnitConversionsRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DeviceSetUnitConversionsRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DeviceSetUnitConversionsRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "DeviceSetUnitConversionsRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "DeviceSetUnitConversionsRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "DeviceSetUnitConversionsRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "DeviceSetUnitConversionsRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "DeviceSetUnitConversionsRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "DeviceSetUnitConversionsRequest" is not integer value.')

        if self.key is not None:
            if not isinstance(self.key, str):
                raise ValueError(f'Property "Key" of "DeviceSetUnitConversionsRequest" is not a string.')

        if self.conversions is not None:
            if not isinstance(self.conversions, Iterable):
                raise ValueError('Property "Conversions" of "DeviceSetUnitConversionsRequest" is not iterable.')

            for i, conversions_item in enumerate(self.conversions):
                if conversions_item is None:
                    raise ValueError(f'Item {i} in property "Conversions" of "DeviceSetUnitConversionsRequest" is None.')

                if not isinstance(conversions_item, ConversionFactor):
                    raise ValueError(f'Item {i} in property "Conversions" of "DeviceSetUnitConversionsRequest" is not an instance of "ConversionFactor".')

                conversions_item.validate()
