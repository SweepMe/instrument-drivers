# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from .oscilloscope_data_source import OscilloscopeDataSource
from .io_port_type import IoPortType


@dataclass
class OscilloscopeCaptureProperties:
    """
    The public properties of one channel of recorded oscilloscope data.
    """

    data_source: OscilloscopeDataSource
    """
    Indicates whether the data came from a setting or an I/O pin.
    """

    setting: str
    """
    The name of the recorded setting.
    """

    axis_number: int
    """
    The number of the axis the data was recorded from, or 0 for the controller.
    """

    io_type: IoPortType
    """
    Which kind of I/O port data was recorded from.
    """

    io_channel: int
    """
    Which I/O pin within the port was recorded.
    """

    @staticmethod
    def zero_values() -> 'OscilloscopeCaptureProperties':
        return OscilloscopeCaptureProperties(
            data_source=next(first for first in OscilloscopeDataSource),
            setting="",
            axis_number=0,
            io_type=next(first for first in IoPortType),
            io_channel=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'OscilloscopeCaptureProperties':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return OscilloscopeCaptureProperties.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'dataSource': self.data_source.value,
            'setting': str(self.setting or ''),
            'axisNumber': int(self.axis_number),
            'ioType': self.io_type.value,
            'ioChannel': int(self.io_channel),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'OscilloscopeCaptureProperties':
        return OscilloscopeCaptureProperties(
            data_source=OscilloscopeDataSource(data.get('dataSource')),  # type: ignore
            setting=data.get('setting'),  # type: ignore
            axis_number=data.get('axisNumber'),  # type: ignore
            io_type=IoPortType(data.get('ioType')),  # type: ignore
            io_channel=data.get('ioChannel'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.data_source is None:
            raise ValueError(f'Property "DataSource" of "OscilloscopeCaptureProperties" is None.')

        if not isinstance(self.data_source, OscilloscopeDataSource):
            raise ValueError(f'Property "DataSource" of "OscilloscopeCaptureProperties" is not an instance of "OscilloscopeDataSource".')

        if self.setting is not None:
            if not isinstance(self.setting, str):
                raise ValueError(f'Property "Setting" of "OscilloscopeCaptureProperties" is not a string.')

        if self.axis_number is None:
            raise ValueError(f'Property "AxisNumber" of "OscilloscopeCaptureProperties" is None.')

        if not isinstance(self.axis_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "AxisNumber" of "OscilloscopeCaptureProperties" is not a number.')

        if int(self.axis_number) != self.axis_number:
            raise ValueError(f'Property "AxisNumber" of "OscilloscopeCaptureProperties" is not integer value.')

        if self.io_type is None:
            raise ValueError(f'Property "IoType" of "OscilloscopeCaptureProperties" is None.')

        if not isinstance(self.io_type, IoPortType):
            raise ValueError(f'Property "IoType" of "OscilloscopeCaptureProperties" is not an instance of "IoPortType".')

        if self.io_channel is None:
            raise ValueError(f'Property "IoChannel" of "OscilloscopeCaptureProperties" is None.')

        if not isinstance(self.io_channel, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "IoChannel" of "OscilloscopeCaptureProperties" is not a number.')

        if int(self.io_channel) != self.io_channel:
            raise ValueError(f'Property "IoChannel" of "OscilloscopeCaptureProperties" is not integer value.')
