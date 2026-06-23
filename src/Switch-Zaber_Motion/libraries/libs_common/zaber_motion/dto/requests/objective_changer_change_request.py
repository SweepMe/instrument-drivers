# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from ..measurement import Measurement


@dataclass
class ObjectiveChangerChangeRequest:

    interface_id: int = 0

    turret_address: int = 0

    focus_address: int = 0

    focus_axis: int = 0

    objective: int = 0

    focus_offset: Optional[Measurement] = None

    @staticmethod
    def zero_values() -> 'ObjectiveChangerChangeRequest':
        return ObjectiveChangerChangeRequest(
            interface_id=0,
            turret_address=0,
            focus_address=0,
            focus_axis=0,
            objective=0,
            focus_offset=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'ObjectiveChangerChangeRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return ObjectiveChangerChangeRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'turretAddress': int(self.turret_address),
            'focusAddress': int(self.focus_address),
            'focusAxis': int(self.focus_axis),
            'objective': int(self.objective),
            'focusOffset': self.focus_offset.to_dict() if self.focus_offset is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ObjectiveChangerChangeRequest':
        return ObjectiveChangerChangeRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            turret_address=data.get('turretAddress'),  # type: ignore
            focus_address=data.get('focusAddress'),  # type: ignore
            focus_axis=data.get('focusAxis'),  # type: ignore
            objective=data.get('objective'),  # type: ignore
            focus_offset=Measurement.from_dict(data.get('focusOffset')) if data.get('focusOffset') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "ObjectiveChangerChangeRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "ObjectiveChangerChangeRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "ObjectiveChangerChangeRequest" is not integer value.')

        if self.turret_address is None:
            raise ValueError(f'Property "TurretAddress" of "ObjectiveChangerChangeRequest" is None.')

        if not isinstance(self.turret_address, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TurretAddress" of "ObjectiveChangerChangeRequest" is not a number.')

        if int(self.turret_address) != self.turret_address:
            raise ValueError(f'Property "TurretAddress" of "ObjectiveChangerChangeRequest" is not integer value.')

        if self.focus_address is None:
            raise ValueError(f'Property "FocusAddress" of "ObjectiveChangerChangeRequest" is None.')

        if not isinstance(self.focus_address, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "FocusAddress" of "ObjectiveChangerChangeRequest" is not a number.')

        if int(self.focus_address) != self.focus_address:
            raise ValueError(f'Property "FocusAddress" of "ObjectiveChangerChangeRequest" is not integer value.')

        if self.focus_axis is None:
            raise ValueError(f'Property "FocusAxis" of "ObjectiveChangerChangeRequest" is None.')

        if not isinstance(self.focus_axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "FocusAxis" of "ObjectiveChangerChangeRequest" is not a number.')

        if int(self.focus_axis) != self.focus_axis:
            raise ValueError(f'Property "FocusAxis" of "ObjectiveChangerChangeRequest" is not integer value.')

        if self.objective is None:
            raise ValueError(f'Property "Objective" of "ObjectiveChangerChangeRequest" is None.')

        if not isinstance(self.objective, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Objective" of "ObjectiveChangerChangeRequest" is not a number.')

        if int(self.objective) != self.objective:
            raise ValueError(f'Property "Objective" of "ObjectiveChangerChangeRequest" is not integer value.')

        if self.focus_offset is not None:
            if not isinstance(self.focus_offset, Measurement):
                raise ValueError(f'Property "FocusOffset" of "ObjectiveChangerChangeRequest" is not an instance of "Measurement".')

            self.focus_offset.validate()
