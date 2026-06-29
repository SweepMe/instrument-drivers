# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable, too-many-return-statements, no-else-raise
from dataclasses import dataclass
from typing import Any, Dict, Union
import zaber_bson
from .pvt_partial_point import PvtPartialPoint
from .pvt_call_action import PvtCallAction
from .pvt_set_digital_output_action import PvtSetDigitalOutputAction
from .pvt_set_all_digital_outputs_action import PvtSetAllDigitalOutputsAction
from .pvt_set_analog_output_action import PvtSetAnalogOutputAction
from .pvt_set_all_analog_outputs_action import PvtSetAllAnalogOutputsAction
from .pvt_cancel_output_schedule_action import PvtCancelOutputScheduleAction
from .pvt_cancel_all_outputs_schedule_action import PvtCancelAllOutputsScheduleAction


PvtPartialSequenceItem = Union[PvtPartialPoint, PvtCallAction, PvtSetDigitalOutputAction, PvtSetAllDigitalOutputsAction, PvtSetAnalogOutputAction, PvtSetAllAnalogOutputsAction, PvtCancelOutputScheduleAction, PvtCancelAllOutputsScheduleAction]
"""
Union of all data types that can appear in a PVT sequence with missing point data columns.
"""


@dataclass
class PvtPartialSequenceItemWireFormat:
    """
    Serialization wrapper for PvtPartialSequenceItem variant. Not part of the public API; do not use.
    """

    variantValueType: str

    pvtPartialPointValue: PvtPartialPoint

    pvtCallActionValue: PvtCallAction

    pvtSetDigitalOutputActionValue: PvtSetDigitalOutputAction

    pvtSetAllDigitalOutputsActionValue: PvtSetAllDigitalOutputsAction

    pvtSetAnalogOutputActionValue: PvtSetAnalogOutputAction

    pvtSetAllAnalogOutputsActionValue: PvtSetAllAnalogOutputsAction

    pvtCancelOutputScheduleActionValue: PvtCancelOutputScheduleAction

    pvtCancelAllOutputsScheduleActionValue: PvtCancelAllOutputsScheduleAction

    def __init__(self, value: PvtPartialSequenceItem) -> None:
        if value is None:
            raise ValueError("Cannot initialize PvtPartialSequenceItem with None value")
        elif isinstance(value, PvtPartialPoint):
            self.pvtPartialPointValue = value
            self.variantValueType = 'PvtPartialPoint'
        elif isinstance(value, PvtCallAction):
            self.pvtCallActionValue = value
            self.variantValueType = 'PvtCallAction'
        elif isinstance(value, PvtSetDigitalOutputAction):
            self.pvtSetDigitalOutputActionValue = value
            self.variantValueType = 'PvtSetDigitalOutputAction'
        elif isinstance(value, PvtSetAllDigitalOutputsAction):
            self.pvtSetAllDigitalOutputsActionValue = value
            self.variantValueType = 'PvtSetAllDigitalOutputsAction'
        elif isinstance(value, PvtSetAnalogOutputAction):
            self.pvtSetAnalogOutputActionValue = value
            self.variantValueType = 'PvtSetAnalogOutputAction'
        elif isinstance(value, PvtSetAllAnalogOutputsAction):
            self.pvtSetAllAnalogOutputsActionValue = value
            self.variantValueType = 'PvtSetAllAnalogOutputsAction'
        elif isinstance(value, PvtCancelOutputScheduleAction):
            self.pvtCancelOutputScheduleActionValue = value
            self.variantValueType = 'PvtCancelOutputScheduleAction'
        elif isinstance(value, PvtCancelAllOutputsScheduleAction):
            self.pvtCancelAllOutputsScheduleActionValue = value
            self.variantValueType = 'PvtCancelAllOutputsScheduleAction'
        else:
            raise TypeError(f"Cannot initialize PvtPartialSequenceItem with value of type {type(value)}")

    def convert_back(self) -> PvtPartialSequenceItem:
        if self.variantValueType == 'PvtPartialPoint':
            return self.pvtPartialPointValue
        if self.variantValueType == 'PvtCallAction':
            return self.pvtCallActionValue
        if self.variantValueType == 'PvtSetDigitalOutputAction':
            return self.pvtSetDigitalOutputActionValue
        if self.variantValueType == 'PvtSetAllDigitalOutputsAction':
            return self.pvtSetAllDigitalOutputsActionValue
        if self.variantValueType == 'PvtSetAnalogOutputAction':
            return self.pvtSetAnalogOutputActionValue
        if self.variantValueType == 'PvtSetAllAnalogOutputsAction':
            return self.pvtSetAllAnalogOutputsActionValue
        if self.variantValueType == 'PvtCancelOutputScheduleAction':
            return self.pvtCancelOutputScheduleActionValue
        if self.variantValueType == 'PvtCancelAllOutputsScheduleAction':
            return self.pvtCancelAllOutputsScheduleActionValue

        raise ValueError(f"Invalid variant type tag value: {self.variantValueType}")

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtPartialSequenceItemWireFormat':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtPartialSequenceItemWireFormat.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            'variantValueType': self.variantValueType,
        }

        if self.variantValueType == 'PvtPartialPoint':
            d['pvtPartialPointValue'] = self.pvtPartialPointValue.to_dict()
        elif self.variantValueType == 'PvtCallAction':
            d['pvtCallActionValue'] = self.pvtCallActionValue.to_dict()
        elif self.variantValueType == 'PvtSetDigitalOutputAction':
            d['pvtSetDigitalOutputActionValue'] = self.pvtSetDigitalOutputActionValue.to_dict()
        elif self.variantValueType == 'PvtSetAllDigitalOutputsAction':
            d['pvtSetAllDigitalOutputsActionValue'] = self.pvtSetAllDigitalOutputsActionValue.to_dict()
        elif self.variantValueType == 'PvtSetAnalogOutputAction':
            d['pvtSetAnalogOutputActionValue'] = self.pvtSetAnalogOutputActionValue.to_dict()
        elif self.variantValueType == 'PvtSetAllAnalogOutputsAction':
            d['pvtSetAllAnalogOutputsActionValue'] = self.pvtSetAllAnalogOutputsActionValue.to_dict()
        elif self.variantValueType == 'PvtCancelOutputScheduleAction':
            d['pvtCancelOutputScheduleActionValue'] = self.pvtCancelOutputScheduleActionValue.to_dict()
        elif self.variantValueType == 'PvtCancelAllOutputsScheduleAction':
            d['pvtCancelAllOutputsScheduleActionValue'] = self.pvtCancelAllOutputsScheduleActionValue.to_dict()
        else:
            raise ValueError(f"Invalid variant type tag {self.variantValueType} value")

        return d

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtPartialSequenceItemWireFormat':
        tag = data.get('variantValueType')
        if tag == 'PvtPartialPoint':
            return PvtPartialSequenceItemWireFormat(PvtPartialPoint.from_dict(data.get('pvtPartialPointValue')))  # type: ignore
        if tag == 'PvtCallAction':
            return PvtPartialSequenceItemWireFormat(PvtCallAction.from_dict(data.get('pvtCallActionValue')))  # type: ignore
        if tag == 'PvtSetDigitalOutputAction':
            return PvtPartialSequenceItemWireFormat(PvtSetDigitalOutputAction.from_dict(data.get('pvtSetDigitalOutputActionValue')))  # type: ignore
        if tag == 'PvtSetAllDigitalOutputsAction':
            return PvtPartialSequenceItemWireFormat(PvtSetAllDigitalOutputsAction.from_dict(data.get('pvtSetAllDigitalOutputsActionValue')))  # type: ignore
        if tag == 'PvtSetAnalogOutputAction':
            return PvtPartialSequenceItemWireFormat(PvtSetAnalogOutputAction.from_dict(data.get('pvtSetAnalogOutputActionValue')))  # type: ignore
        if tag == 'PvtSetAllAnalogOutputsAction':
            return PvtPartialSequenceItemWireFormat(PvtSetAllAnalogOutputsAction.from_dict(data.get('pvtSetAllAnalogOutputsActionValue')))  # type: ignore
        if tag == 'PvtCancelOutputScheduleAction':
            return PvtPartialSequenceItemWireFormat(PvtCancelOutputScheduleAction.from_dict(data.get('pvtCancelOutputScheduleActionValue')))  # type: ignore
        if tag == 'PvtCancelAllOutputsScheduleAction':
            return PvtPartialSequenceItemWireFormat(PvtCancelAllOutputsScheduleAction.from_dict(data.get('pvtCancelAllOutputsScheduleActionValue')))  # type: ignore

        raise ValueError(f"Invalid variant type tag {tag} in response data")

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.variantValueType == 'PvtPartialPoint':
            if self.pvtPartialPointValue is None:
                raise ValueError(f'Property "PvtPartialPoint" of "PvtPartialSequenceItem" is None.')

            if not isinstance(self.pvtPartialPointValue, PvtPartialPoint):
                raise ValueError(f'Property "PvtPartialPoint" of "PvtPartialSequenceItem" is not an instance of "PvtPartialPoint".')

            self.pvtPartialPointValue.validate()

        elif self.variantValueType == 'PvtCallAction':
            if self.pvtCallActionValue is None:
                raise ValueError(f'Property "PvtCallAction" of "PvtPartialSequenceItem" is None.')

            if not isinstance(self.pvtCallActionValue, PvtCallAction):
                raise ValueError(f'Property "PvtCallAction" of "PvtPartialSequenceItem" is not an instance of "PvtCallAction".')

            self.pvtCallActionValue.validate()

        elif self.variantValueType == 'PvtSetDigitalOutputAction':
            if self.pvtSetDigitalOutputActionValue is None:
                raise ValueError(f'Property "PvtSetDigitalOutputAction" of "PvtPartialSequenceItem" is None.')

            if not isinstance(self.pvtSetDigitalOutputActionValue, PvtSetDigitalOutputAction):
                raise ValueError(f'Property "PvtSetDigitalOutputAction" of "PvtPartialSequenceItem" is not an instance of "PvtSetDigitalOutputAction".')

            self.pvtSetDigitalOutputActionValue.validate()

        elif self.variantValueType == 'PvtSetAllDigitalOutputsAction':
            if self.pvtSetAllDigitalOutputsActionValue is None:
                raise ValueError(f'Property "PvtSetAllDigitalOutputsAction" of "PvtPartialSequenceItem" is None.')

            if not isinstance(self.pvtSetAllDigitalOutputsActionValue, PvtSetAllDigitalOutputsAction):
                raise ValueError(f'Property "PvtSetAllDigitalOutputsAction" of "PvtPartialSequenceItem" is not an instance of "PvtSetAllDigitalOutputsAction".')

            self.pvtSetAllDigitalOutputsActionValue.validate()

        elif self.variantValueType == 'PvtSetAnalogOutputAction':
            if self.pvtSetAnalogOutputActionValue is None:
                raise ValueError(f'Property "PvtSetAnalogOutputAction" of "PvtPartialSequenceItem" is None.')

            if not isinstance(self.pvtSetAnalogOutputActionValue, PvtSetAnalogOutputAction):
                raise ValueError(f'Property "PvtSetAnalogOutputAction" of "PvtPartialSequenceItem" is not an instance of "PvtSetAnalogOutputAction".')

            self.pvtSetAnalogOutputActionValue.validate()

        elif self.variantValueType == 'PvtSetAllAnalogOutputsAction':
            if self.pvtSetAllAnalogOutputsActionValue is None:
                raise ValueError(f'Property "PvtSetAllAnalogOutputsAction" of "PvtPartialSequenceItem" is None.')

            if not isinstance(self.pvtSetAllAnalogOutputsActionValue, PvtSetAllAnalogOutputsAction):
                raise ValueError(f'Property "PvtSetAllAnalogOutputsAction" of "PvtPartialSequenceItem" is not an instance of "PvtSetAllAnalogOutputsAction".')

            self.pvtSetAllAnalogOutputsActionValue.validate()

        elif self.variantValueType == 'PvtCancelOutputScheduleAction':
            if self.pvtCancelOutputScheduleActionValue is None:
                raise ValueError(f'Property "PvtCancelOutputScheduleAction" of "PvtPartialSequenceItem" is None.')

            if not isinstance(self.pvtCancelOutputScheduleActionValue, PvtCancelOutputScheduleAction):
                raise ValueError(f'Property "PvtCancelOutputScheduleAction" of "PvtPartialSequenceItem" is not an instance of "PvtCancelOutputScheduleAction".')

            self.pvtCancelOutputScheduleActionValue.validate()

        elif self.variantValueType == 'PvtCancelAllOutputsScheduleAction':
            if self.pvtCancelAllOutputsScheduleActionValue is None:
                raise ValueError(f'Property "PvtCancelAllOutputsScheduleAction" of "PvtPartialSequenceItem" is None.')

            if not isinstance(self.pvtCancelAllOutputsScheduleActionValue, PvtCancelAllOutputsScheduleAction):
                raise ValueError(f'Property "PvtCancelAllOutputsScheduleAction" of "PvtPartialSequenceItem" is not an instance of "PvtCancelAllOutputsScheduleAction".')

            self.pvtCancelAllOutputsScheduleActionValue.validate()
