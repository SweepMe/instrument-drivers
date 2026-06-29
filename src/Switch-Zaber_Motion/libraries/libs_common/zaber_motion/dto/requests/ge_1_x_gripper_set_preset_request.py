# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class Ge1xGripperSetPresetRequest:

    connection_id: int = 0

    preset_number: int = 0

    position: float = 0

    force: int = 0

    speed: int = 0

    save_to_flash: bool = False

    @staticmethod
    def zero_values() -> 'Ge1xGripperSetPresetRequest':
        return Ge1xGripperSetPresetRequest(
            connection_id=0,
            preset_number=0,
            position=0,
            force=0,
            speed=0,
            save_to_flash=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'Ge1xGripperSetPresetRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return Ge1xGripperSetPresetRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'connectionId': int(self.connection_id),
            'presetNumber': int(self.preset_number),
            'position': float(self.position),
            'force': int(self.force),
            'speed': int(self.speed),
            'saveToFlash': bool(self.save_to_flash),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Ge1xGripperSetPresetRequest':
        return Ge1xGripperSetPresetRequest(
            connection_id=data.get('connectionId'),  # type: ignore
            preset_number=data.get('presetNumber'),  # type: ignore
            position=data.get('position'),  # type: ignore
            force=data.get('force'),  # type: ignore
            speed=data.get('speed'),  # type: ignore
            save_to_flash=data.get('saveToFlash'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.connection_id is None:
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperSetPresetRequest" is None.')

        if not isinstance(self.connection_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperSetPresetRequest" is not a number.')

        if int(self.connection_id) != self.connection_id:
            raise ValueError(f'Property "ConnectionId" of "Ge1xGripperSetPresetRequest" is not integer value.')

        if self.preset_number is None:
            raise ValueError(f'Property "PresetNumber" of "Ge1xGripperSetPresetRequest" is None.')

        if not isinstance(self.preset_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "PresetNumber" of "Ge1xGripperSetPresetRequest" is not a number.')

        if int(self.preset_number) != self.preset_number:
            raise ValueError(f'Property "PresetNumber" of "Ge1xGripperSetPresetRequest" is not integer value.')

        if self.position is None:
            raise ValueError(f'Property "Position" of "Ge1xGripperSetPresetRequest" is None.')

        if not isinstance(self.position, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Position" of "Ge1xGripperSetPresetRequest" is not a number.')

        if self.force is None:
            raise ValueError(f'Property "Force" of "Ge1xGripperSetPresetRequest" is None.')

        if not isinstance(self.force, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Force" of "Ge1xGripperSetPresetRequest" is not a number.')

        if int(self.force) != self.force:
            raise ValueError(f'Property "Force" of "Ge1xGripperSetPresetRequest" is not integer value.')

        if self.speed is None:
            raise ValueError(f'Property "Speed" of "Ge1xGripperSetPresetRequest" is None.')

        if not isinstance(self.speed, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Speed" of "Ge1xGripperSetPresetRequest" is not a number.')

        if int(self.speed) != self.speed:
            raise ValueError(f'Property "Speed" of "Ge1xGripperSetPresetRequest" is not integer value.')
