# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import decimal
from collections.abc import Iterable
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class GetSetting:
    """
    Specifies a setting to get with one of the multi-get commands.
    """

    setting: str
    """
    The setting to read.
    """

    axes: Optional[List[int]] = None
    """
    The list of axes to read.
    """

    unit: Optional[UnitsAndLiterals] = None
    """
    The unit to convert the read settings to.
    """

    @staticmethod
    def zero_values() -> 'GetSetting':
        return GetSetting(
            setting="",
            axes=None,
            unit=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GetSetting':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GetSetting.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'setting': str(self.setting or ''),
            'axes': [int(item) for item in self.axes] if self.axes is not None else [],
            'unit': units_from_literals(self.unit).value if self.unit is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GetSetting':
        return GetSetting(
            setting=data.get('setting'),  # type: ignore
            axes=data.get('axes'),  # type: ignore
            unit=Units(data.get('unit')) if data.get('unit') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.setting is not None:
            if not isinstance(self.setting, str):
                raise ValueError(f'Property "Setting" of "GetSetting" is not a string.')

        if self.axes is not None:
            if not isinstance(self.axes, Iterable):
                raise ValueError('Property "Axes" of "GetSetting" is not iterable.')

            for i, axes_item in enumerate(self.axes):
                if axes_item is None:
                    raise ValueError(f'Item {i} in property "Axes" of "GetSetting" is None.')

                if not isinstance(axes_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "Axes" of "GetSetting" is not a number.')

                if int(axes_item) != axes_item:
                    raise ValueError(f'Item {i} in property "Axes" of "GetSetting" is not integer value.')

        if self.unit is not None:
            if not isinstance(self.unit, (Units, str)):
                raise ValueError(f'Property "Unit" of "GetSetting" is not Units.')
