# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson


@dataclass
class MockPeripheral:
    """
    Definition of a mock peripheral.
    """

    peripheral_id: int
    """
    A valid Zaber peripheral ID.
    """

    is_modified: Optional[bool] = None
    """
    The peripheral has hardware modifications. Defaults to false.
    """

    resolution: Optional[int] = None
    """
    The number of microsteps per full step for peripheral. Defaults to device database default.
    """

    @staticmethod
    def zero_values() -> 'MockPeripheral':
        return MockPeripheral(
            peripheral_id=0,
            is_modified=None,
            resolution=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MockPeripheral':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MockPeripheral.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'peripheralId': int(self.peripheral_id),
            'isModified': bool(self.is_modified) if self.is_modified is not None else None,
            'resolution': int(self.resolution) if self.resolution is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MockPeripheral':
        return MockPeripheral(
            peripheral_id=data.get('peripheralId'),  # type: ignore
            is_modified=data.get('isModified'),  # type: ignore
            resolution=data.get('resolution'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.peripheral_id is None:
            raise ValueError(f'Property "PeripheralId" of "MockPeripheral" is None.')

        if not isinstance(self.peripheral_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "PeripheralId" of "MockPeripheral" is not a number.')

        if int(self.peripheral_id) != self.peripheral_id:
            raise ValueError(f'Property "PeripheralId" of "MockPeripheral" is not integer value.')

        if self.resolution is not None:
            if not isinstance(self.resolution, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "Resolution" of "MockPeripheral" is not a number.')

            if int(self.resolution) != self.resolution:
                raise ValueError(f'Property "Resolution" of "MockPeripheral" is not integer value.')
