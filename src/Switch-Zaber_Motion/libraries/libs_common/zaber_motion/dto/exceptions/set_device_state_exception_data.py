# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from .set_peripheral_state_exception_data import SetPeripheralStateExceptionData


@dataclass
class SetDeviceStateExceptionData:
    """
    Contains additional data for a SetDeviceStateFailedException.
    """

    settings: List[str]
    """
    A list of settings which could not be set.
    """

    stream_buffers: List[str]
    """
    The reason the stream buffers could not be set.
    """

    pvt_buffers: List[str]
    """
    The reason the pvt buffers could not be set.
    """

    triggers: List[str]
    """
    The reason the triggers could not be set.
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

    peripherals: List[SetPeripheralStateExceptionData]
    """
    Errors for any peripherals that could not be set.
    """

    @staticmethod
    def zero_values() -> 'SetDeviceStateExceptionData':
        return SetDeviceStateExceptionData(
            settings=[],
            stream_buffers=[],
            pvt_buffers=[],
            triggers=[],
            servo_tuning="",
            stored_positions=[],
            storage=[],
            peripherals=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SetDeviceStateExceptionData':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SetDeviceStateExceptionData.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'settings': [str(item or '') for item in self.settings] if self.settings is not None else [],
            'streamBuffers': [str(item or '') for item in self.stream_buffers] if self.stream_buffers is not None else [],
            'pvtBuffers': [str(item or '') for item in self.pvt_buffers] if self.pvt_buffers is not None else [],
            'triggers': [str(item or '') for item in self.triggers] if self.triggers is not None else [],
            'servoTuning': str(self.servo_tuning or ''),
            'storedPositions': [str(item or '') for item in self.stored_positions] if self.stored_positions is not None else [],
            'storage': [str(item or '') for item in self.storage] if self.storage is not None else [],
            'peripherals': [item.to_dict() for item in self.peripherals] if self.peripherals is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SetDeviceStateExceptionData':
        return SetDeviceStateExceptionData(
            settings=data.get('settings'),  # type: ignore
            stream_buffers=data.get('streamBuffers'),  # type: ignore
            pvt_buffers=data.get('pvtBuffers'),  # type: ignore
            triggers=data.get('triggers'),  # type: ignore
            servo_tuning=data.get('servoTuning'),  # type: ignore
            stored_positions=data.get('storedPositions'),  # type: ignore
            storage=data.get('storage'),  # type: ignore
            peripherals=[SetPeripheralStateExceptionData.from_dict(item) for item in data.get('peripherals')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.settings is not None:
            if not isinstance(self.settings, Iterable):
                raise ValueError('Property "Settings" of "SetDeviceStateExceptionData" is not iterable.')

            for i, settings_item in enumerate(self.settings):
                if settings_item is not None:
                    if not isinstance(settings_item, str):
                        raise ValueError(f'Item {i} in property "Settings" of "SetDeviceStateExceptionData" is not a string.')

        if self.stream_buffers is not None:
            if not isinstance(self.stream_buffers, Iterable):
                raise ValueError('Property "StreamBuffers" of "SetDeviceStateExceptionData" is not iterable.')

            for i, stream_buffers_item in enumerate(self.stream_buffers):
                if stream_buffers_item is not None:
                    if not isinstance(stream_buffers_item, str):
                        raise ValueError(f'Item {i} in property "StreamBuffers" of "SetDeviceStateExceptionData" is not a string.')

        if self.pvt_buffers is not None:
            if not isinstance(self.pvt_buffers, Iterable):
                raise ValueError('Property "PvtBuffers" of "SetDeviceStateExceptionData" is not iterable.')

            for i, pvt_buffers_item in enumerate(self.pvt_buffers):
                if pvt_buffers_item is not None:
                    if not isinstance(pvt_buffers_item, str):
                        raise ValueError(f'Item {i} in property "PvtBuffers" of "SetDeviceStateExceptionData" is not a string.')

        if self.triggers is not None:
            if not isinstance(self.triggers, Iterable):
                raise ValueError('Property "Triggers" of "SetDeviceStateExceptionData" is not iterable.')

            for i, triggers_item in enumerate(self.triggers):
                if triggers_item is not None:
                    if not isinstance(triggers_item, str):
                        raise ValueError(f'Item {i} in property "Triggers" of "SetDeviceStateExceptionData" is not a string.')

        if self.servo_tuning is not None:
            if not isinstance(self.servo_tuning, str):
                raise ValueError(f'Property "ServoTuning" of "SetDeviceStateExceptionData" is not a string.')

        if self.stored_positions is not None:
            if not isinstance(self.stored_positions, Iterable):
                raise ValueError('Property "StoredPositions" of "SetDeviceStateExceptionData" is not iterable.')

            for i, stored_positions_item in enumerate(self.stored_positions):
                if stored_positions_item is not None:
                    if not isinstance(stored_positions_item, str):
                        raise ValueError(f'Item {i} in property "StoredPositions" of "SetDeviceStateExceptionData" is not a string.')

        if self.storage is not None:
            if not isinstance(self.storage, Iterable):
                raise ValueError('Property "Storage" of "SetDeviceStateExceptionData" is not iterable.')

            for i, storage_item in enumerate(self.storage):
                if storage_item is not None:
                    if not isinstance(storage_item, str):
                        raise ValueError(f'Item {i} in property "Storage" of "SetDeviceStateExceptionData" is not a string.')

        if self.peripherals is not None:
            if not isinstance(self.peripherals, Iterable):
                raise ValueError('Property "Peripherals" of "SetDeviceStateExceptionData" is not iterable.')

            for i, peripherals_item in enumerate(self.peripherals):
                if peripherals_item is None:
                    raise ValueError(f'Item {i} in property "Peripherals" of "SetDeviceStateExceptionData" is None.')

                if not isinstance(peripherals_item, SetPeripheralStateExceptionData):
                    raise ValueError(f'Item {i} in property "Peripherals" of "SetDeviceStateExceptionData" is not an instance of "SetPeripheralStateExceptionData".')

                peripherals_item.validate()
