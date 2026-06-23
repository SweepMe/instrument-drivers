# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from collections.abc import Iterable
import zaber_bson
from .io_port_type import IoPortType


@dataclass
class PvtCancelAllOutputsScheduleAction:
    """
    Cancel pending scheduled output changes for multiple analog or digital output pins in a PVT sequence or buffer.
    """

    io_type: IoPortType
    """
    The type of the output port to cancel. Must be AO or DO; input types are not valid here.
    """

    cancel: Optional[List[bool]] = None
    """
    Specifies which pins to cancel. If absent, all pins in the port are cancelled.
    """

    @staticmethod
    def zero_values() -> 'PvtCancelAllOutputsScheduleAction':
        return PvtCancelAllOutputsScheduleAction(
            io_type=next(first for first in IoPortType),
            cancel=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtCancelAllOutputsScheduleAction':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtCancelAllOutputsScheduleAction.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'ioType': self.io_type.value,
            'cancel': [bool(item) for item in self.cancel] if self.cancel is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtCancelAllOutputsScheduleAction':
        return PvtCancelAllOutputsScheduleAction(
            io_type=IoPortType(data.get('ioType')),  # type: ignore
            cancel=data.get('cancel'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.io_type is None:
            raise ValueError(f'Property "IoType" of "PvtCancelAllOutputsScheduleAction" is None.')

        if not isinstance(self.io_type, IoPortType):
            raise ValueError(f'Property "IoType" of "PvtCancelAllOutputsScheduleAction" is not an instance of "IoPortType".')

        if self.cancel is not None:
            if not isinstance(self.cancel, Iterable):
                raise ValueError('Property "Cancel" of "PvtCancelAllOutputsScheduleAction" is not iterable.')
