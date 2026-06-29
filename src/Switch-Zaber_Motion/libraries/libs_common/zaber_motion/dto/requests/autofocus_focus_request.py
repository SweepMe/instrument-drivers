# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class AutofocusFocusRequest:

    provider_id: int = 0

    interface_id: int = 0

    focus_address: int = 0

    focus_axis: int = 0

    turret_address: int = 0

    scan: bool = False

    once: bool = False

    timeout: int = 0

    @staticmethod
    def zero_values() -> 'AutofocusFocusRequest':
        return AutofocusFocusRequest(
            provider_id=0,
            interface_id=0,
            focus_address=0,
            focus_axis=0,
            turret_address=0,
            scan=False,
            once=False,
            timeout=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'AutofocusFocusRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return AutofocusFocusRequest.from_dict(data)

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
            'scan': bool(self.scan),
            'once': bool(self.once),
            'timeout': int(self.timeout),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AutofocusFocusRequest':
        return AutofocusFocusRequest(
            provider_id=data.get('providerId'),  # type: ignore
            interface_id=data.get('interfaceId'),  # type: ignore
            focus_address=data.get('focusAddress'),  # type: ignore
            focus_axis=data.get('focusAxis'),  # type: ignore
            turret_address=data.get('turretAddress'),  # type: ignore
            scan=data.get('scan'),  # type: ignore
            once=data.get('once'),  # type: ignore
            timeout=data.get('timeout'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.provider_id is None:
            raise ValueError(f'Property "ProviderId" of "AutofocusFocusRequest" is None.')

        if not isinstance(self.provider_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ProviderId" of "AutofocusFocusRequest" is not a number.')

        if int(self.provider_id) != self.provider_id:
            raise ValueError(f'Property "ProviderId" of "AutofocusFocusRequest" is not integer value.')

        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "AutofocusFocusRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "AutofocusFocusRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "AutofocusFocusRequest" is not integer value.')

        if self.focus_address is None:
            raise ValueError(f'Property "FocusAddress" of "AutofocusFocusRequest" is None.')

        if not isinstance(self.focus_address, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "FocusAddress" of "AutofocusFocusRequest" is not a number.')

        if int(self.focus_address) != self.focus_address:
            raise ValueError(f'Property "FocusAddress" of "AutofocusFocusRequest" is not integer value.')

        if self.focus_axis is None:
            raise ValueError(f'Property "FocusAxis" of "AutofocusFocusRequest" is None.')

        if not isinstance(self.focus_axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "FocusAxis" of "AutofocusFocusRequest" is not a number.')

        if int(self.focus_axis) != self.focus_axis:
            raise ValueError(f'Property "FocusAxis" of "AutofocusFocusRequest" is not integer value.')

        if self.turret_address is None:
            raise ValueError(f'Property "TurretAddress" of "AutofocusFocusRequest" is None.')

        if not isinstance(self.turret_address, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TurretAddress" of "AutofocusFocusRequest" is not a number.')

        if int(self.turret_address) != self.turret_address:
            raise ValueError(f'Property "TurretAddress" of "AutofocusFocusRequest" is not integer value.')

        if self.timeout is None:
            raise ValueError(f'Property "Timeout" of "AutofocusFocusRequest" is None.')

        if not isinstance(self.timeout, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Timeout" of "AutofocusFocusRequest" is not a number.')

        if int(self.timeout) != self.timeout:
            raise ValueError(f'Property "Timeout" of "AutofocusFocusRequest" is not integer value.')
