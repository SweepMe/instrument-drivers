# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class ForgetDevicesRequest:

    interface_id: int = 0

    except_devices: List[int] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'ForgetDevicesRequest':
        return ForgetDevicesRequest(
            interface_id=0,
            except_devices=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'ForgetDevicesRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return ForgetDevicesRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'exceptDevices': [int(item) for item in self.except_devices] if self.except_devices is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ForgetDevicesRequest':
        return ForgetDevicesRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            except_devices=data.get('exceptDevices'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "ForgetDevicesRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "ForgetDevicesRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "ForgetDevicesRequest" is not integer value.')

        if self.except_devices is not None:
            if not isinstance(self.except_devices, Iterable):
                raise ValueError('Property "ExceptDevices" of "ForgetDevicesRequest" is not iterable.')

            for i, except_devices_item in enumerate(self.except_devices):
                if except_devices_item is None:
                    raise ValueError(f'Item {i} in property "ExceptDevices" of "ForgetDevicesRequest" is None.')

                if not isinstance(except_devices_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "ExceptDevices" of "ForgetDevicesRequest" is not a number.')

                if int(except_devices_item) != except_devices_item:
                    raise ValueError(f'Item {i} in property "ExceptDevices" of "ForgetDevicesRequest" is not integer value.')
