# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson


@dataclass
class AxisDefinition:
    """
    Defines an axis of the translator.
    """

    peripheral_id: int
    """
    ID of the peripheral.
    """

    microstep_resolution: Optional[int] = None
    """
    Microstep resolution of the axis.
    Can be obtained by reading the resolution setting.
    Leave empty if the axis does not have the setting.
    """

    @staticmethod
    def zero_values() -> 'AxisDefinition':
        return AxisDefinition(
            peripheral_id=0,
            microstep_resolution=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'AxisDefinition':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return AxisDefinition.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'peripheralId': int(self.peripheral_id),
            'microstepResolution': int(self.microstep_resolution) if self.microstep_resolution is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AxisDefinition':
        return AxisDefinition(
            peripheral_id=data.get('peripheralId'),  # type: ignore
            microstep_resolution=data.get('microstepResolution'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.peripheral_id is None:
            raise ValueError(f'Property "PeripheralId" of "AxisDefinition" is None.')

        if not isinstance(self.peripheral_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "PeripheralId" of "AxisDefinition" is not a number.')

        if int(self.peripheral_id) != self.peripheral_id:
            raise ValueError(f'Property "PeripheralId" of "AxisDefinition" is not integer value.')

        if self.microstep_resolution is not None:
            if not isinstance(self.microstep_resolution, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "MicrostepResolution" of "AxisDefinition" is not a number.')

            if int(self.microstep_resolution) != self.microstep_resolution:
                raise ValueError(f'Property "MicrostepResolution" of "AxisDefinition" is not integer value.')
