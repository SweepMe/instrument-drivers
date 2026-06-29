# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class SetPeripheralStateExceptionData:
    """
    Contains additional data for a SetPeripheralStateFailedException.
    """

    axis_number: int
    """
    The number of axis where the exception originated.
    """

    settings: List[str]
    """
    A list of settings which could not be set.
    """

    servo_tuning: str
    """
    The reason servo tuning could not be set.
    """

    stored_positions: List[str]
    """
    The reasons stored positions could not be set.
    """

    storage: List[str]
    """
    The reasons storage could not be set.
    """

    @staticmethod
    def zero_values() -> 'SetPeripheralStateExceptionData':
        return SetPeripheralStateExceptionData(
            axis_number=0,
            settings=[],
            servo_tuning="",
            stored_positions=[],
            storage=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SetPeripheralStateExceptionData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SetPeripheralStateExceptionData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'axisNumber': int(self.axis_number),
            'settings': [str(item or '') for item in self.settings] if self.settings is not None else [],
            'servoTuning': str(self.servo_tuning or ''),
            'storedPositions': [str(item or '') for item in self.stored_positions] if self.stored_positions is not None else [],
            'storage': [str(item or '') for item in self.storage] if self.storage is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SetPeripheralStateExceptionData':
        return SetPeripheralStateExceptionData(
            axis_number=data.get('axisNumber'),  # type: ignore
            settings=data.get('settings'),  # type: ignore
            servo_tuning=data.get('servoTuning'),  # type: ignore
            stored_positions=data.get('storedPositions'),  # type: ignore
            storage=data.get('storage'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.axis_number is None:
            raise ValueError(f'Property "AxisNumber" of "SetPeripheralStateExceptionData" is None.')

        if not isinstance(self.axis_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "AxisNumber" of "SetPeripheralStateExceptionData" is not a number.')

        if int(self.axis_number) != self.axis_number:
            raise ValueError(f'Property "AxisNumber" of "SetPeripheralStateExceptionData" is not integer value.')

        if self.settings is not None:
            if not isinstance(self.settings, Iterable):
                raise ValueError('Property "Settings" of "SetPeripheralStateExceptionData" is not iterable.')

            for i, settings_item in enumerate(self.settings):
                if settings_item is not None:
                    if not isinstance(settings_item, str):
                        raise ValueError(f'Item {i} in property "Settings" of "SetPeripheralStateExceptionData" is not a string.')

        if self.servo_tuning is not None:
            if not isinstance(self.servo_tuning, str):
                raise ValueError(f'Property "ServoTuning" of "SetPeripheralStateExceptionData" is not a string.')

        if self.stored_positions is not None:
            if not isinstance(self.stored_positions, Iterable):
                raise ValueError('Property "StoredPositions" of "SetPeripheralStateExceptionData" is not iterable.')

            for i, stored_positions_item in enumerate(self.stored_positions):
                if stored_positions_item is not None:
                    if not isinstance(stored_positions_item, str):
                        raise ValueError(f'Item {i} in property "StoredPositions" of "SetPeripheralStateExceptionData" is not a string.')

        if self.storage is not None:
            if not isinstance(self.storage, Iterable):
                raise ValueError('Property "Storage" of "SetPeripheralStateExceptionData" is not iterable.')

            for i, storage_item in enumerate(self.storage):
                if storage_item is not None:
                    if not isinstance(storage_item, str):
                        raise ValueError(f'Item {i} in property "Storage" of "SetPeripheralStateExceptionData" is not a string.')
