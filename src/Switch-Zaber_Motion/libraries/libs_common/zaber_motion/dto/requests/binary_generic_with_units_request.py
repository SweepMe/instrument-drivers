# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..binary.command_code import CommandCode
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class BinaryGenericWithUnitsRequest:

    interface_id: int = 0

    device: int = 0

    command: CommandCode = next(first for first in CommandCode)

    data: float = 0

    from_unit: UnitsAndLiterals = Units.NATIVE

    to_unit: UnitsAndLiterals = Units.NATIVE

    timeout: float = 0

    @staticmethod
    def zero_values() -> 'BinaryGenericWithUnitsRequest':
        return BinaryGenericWithUnitsRequest(
            interface_id=0,
            device=0,
            command=next(first for first in CommandCode),
            data=0,
            from_unit=Units.NATIVE,
            to_unit=Units.NATIVE,
            timeout=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'BinaryGenericWithUnitsRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return BinaryGenericWithUnitsRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'command': self.command.value,
            'data': float(self.data),
            'fromUnit': units_from_literals(self.from_unit).value,
            'toUnit': units_from_literals(self.to_unit).value,
            'timeout': float(self.timeout),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BinaryGenericWithUnitsRequest':
        return BinaryGenericWithUnitsRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            command=CommandCode(data.get('command')),  # type: ignore
            data=data.get('data'),  # type: ignore
            from_unit=Units(data.get('fromUnit')),  # type: ignore
            to_unit=Units(data.get('toUnit')),  # type: ignore
            timeout=data.get('timeout'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "BinaryGenericWithUnitsRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "BinaryGenericWithUnitsRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "BinaryGenericWithUnitsRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "BinaryGenericWithUnitsRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "BinaryGenericWithUnitsRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "BinaryGenericWithUnitsRequest" is not integer value.')

        if self.command is None:
            raise ValueError(f'Property "Command" of "BinaryGenericWithUnitsRequest" is None.')

        if not isinstance(self.command, CommandCode):
            raise ValueError(f'Property "Command" of "BinaryGenericWithUnitsRequest" is not an instance of "CommandCode".')

        if self.data is None:
            raise ValueError(f'Property "Data" of "BinaryGenericWithUnitsRequest" is None.')

        if not isinstance(self.data, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Data" of "BinaryGenericWithUnitsRequest" is not a number.')

        if self.from_unit is None:
            raise ValueError(f'Property "FromUnit" of "BinaryGenericWithUnitsRequest" is None.')

        if not isinstance(self.from_unit, (Units, str)):
            raise ValueError(f'Property "FromUnit" of "BinaryGenericWithUnitsRequest" is not Units.')

        if self.to_unit is None:
            raise ValueError(f'Property "ToUnit" of "BinaryGenericWithUnitsRequest" is None.')

        if not isinstance(self.to_unit, (Units, str)):
            raise ValueError(f'Property "ToUnit" of "BinaryGenericWithUnitsRequest" is not Units.')

        if self.timeout is None:
            raise ValueError(f'Property "Timeout" of "BinaryGenericWithUnitsRequest" is None.')

        if not isinstance(self.timeout, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Timeout" of "BinaryGenericWithUnitsRequest" is not a number.')
