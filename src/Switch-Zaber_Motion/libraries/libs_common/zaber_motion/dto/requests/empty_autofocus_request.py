# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class EmptyAutofocusRequest:

    provider_id: int = 0

    interface_id: int = 0

    focus_address: int = 0

    focus_axis: int = 0

    turret_address: int = 0

    @staticmethod
    def zero_values() -> 'EmptyAutofocusRequest':
        return EmptyAutofocusRequest(
            provider_id=0,
            interface_id=0,
            focus_address=0,
            focus_axis=0,
            turret_address=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'EmptyAutofocusRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return EmptyAutofocusRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'providerId': int(self.provider_id),
            'interfaceId': int(self.interface_id),
            'focusAddress': int(self.focus_address),
            'focusAxis': int(self.focus_axis),
            'turretAddress': int(self.turret_address),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'EmptyAutofocusRequest':
        return EmptyAutofocusRequest(
            provider_id=data.get('providerId'),  # type: ignore
            interface_id=data.get('interfaceId'),  # type: ignore
            focus_address=data.get('focusAddress'),  # type: ignore
            focus_axis=data.get('focusAxis'),  # type: ignore
            turret_address=data.get('turretAddress'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.provider_id is None:
            raise ValueError(f'Property "ProviderId" of "EmptyAutofocusRequest" is None.')

        if not isinstance(self.provider_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ProviderId" of "EmptyAutofocusRequest" is not a number.')

        if int(self.provider_id) != self.provider_id:
            raise ValueError(f'Property "ProviderId" of "EmptyAutofocusRequest" is not integer value.')

        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "EmptyAutofocusRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "EmptyAutofocusRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "EmptyAutofocusRequest" is not integer value.')

        if self.focus_address is None:
            raise ValueError(f'Property "FocusAddress" of "EmptyAutofocusRequest" is None.')

        if not isinstance(self.focus_address, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "FocusAddress" of "EmptyAutofocusRequest" is not a number.')

        if int(self.focus_address) != self.focus_address:
            raise ValueError(f'Property "FocusAddress" of "EmptyAutofocusRequest" is not integer value.')

        if self.focus_axis is None:
            raise ValueError(f'Property "FocusAxis" of "EmptyAutofocusRequest" is None.')

        if not isinstance(self.focus_axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "FocusAxis" of "EmptyAutofocusRequest" is not a number.')

        if int(self.focus_axis) != self.focus_axis:
            raise ValueError(f'Property "FocusAxis" of "EmptyAutofocusRequest" is not integer value.')

        if self.turret_address is None:
            raise ValueError(f'Property "TurretAddress" of "EmptyAutofocusRequest" is None.')

        if not isinstance(self.turret_address, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TurretAddress" of "EmptyAutofocusRequest" is not a number.')

        if int(self.turret_address) != self.turret_address:
            raise ValueError(f'Property "TurretAddress" of "EmptyAutofocusRequest" is not integer value.')
