# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class WdiGenericRequest:

    interface_id: int = 0

    register_id: int = 0

    size: int = 0

    count: int = 0

    offset: int = 0

    register_bank: str = ""

    data: List[int] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'WdiGenericRequest':
        return WdiGenericRequest(
            interface_id=0,
            register_id=0,
            size=0,
            count=0,
            offset=0,
            register_bank="",
            data=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'WdiGenericRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return WdiGenericRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'registerId': int(self.register_id),
            'size': int(self.size),
            'count': int(self.count),
            'offset': int(self.offset),
            'registerBank': str(self.register_bank or ''),
            'data': [int(item) for item in self.data] if self.data is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'WdiGenericRequest':
        return WdiGenericRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            register_id=data.get('registerId'),  # type: ignore
            size=data.get('size'),  # type: ignore
            count=data.get('count'),  # type: ignore
            offset=data.get('offset'),  # type: ignore
            register_bank=data.get('registerBank'),  # type: ignore
            data=data.get('data'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "WdiGenericRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "WdiGenericRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "WdiGenericRequest" is not integer value.')

        if self.register_id is None:
            raise ValueError(f'Property "RegisterId" of "WdiGenericRequest" is None.')

        if not isinstance(self.register_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "RegisterId" of "WdiGenericRequest" is not a number.')

        if int(self.register_id) != self.register_id:
            raise ValueError(f'Property "RegisterId" of "WdiGenericRequest" is not integer value.')

        if self.size is None:
            raise ValueError(f'Property "Size" of "WdiGenericRequest" is None.')

        if not isinstance(self.size, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Size" of "WdiGenericRequest" is not a number.')

        if int(self.size) != self.size:
            raise ValueError(f'Property "Size" of "WdiGenericRequest" is not integer value.')

        if self.count is None:
            raise ValueError(f'Property "Count" of "WdiGenericRequest" is None.')

        if not isinstance(self.count, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Count" of "WdiGenericRequest" is not a number.')

        if int(self.count) != self.count:
            raise ValueError(f'Property "Count" of "WdiGenericRequest" is not integer value.')

        if self.offset is None:
            raise ValueError(f'Property "Offset" of "WdiGenericRequest" is None.')

        if not isinstance(self.offset, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Offset" of "WdiGenericRequest" is not a number.')

        if int(self.offset) != self.offset:
            raise ValueError(f'Property "Offset" of "WdiGenericRequest" is not integer value.')

        if self.register_bank is not None:
            if not isinstance(self.register_bank, str):
                raise ValueError(f'Property "RegisterBank" of "WdiGenericRequest" is not a string.')

        if self.data is not None:
            if not isinstance(self.data, Iterable):
                raise ValueError('Property "Data" of "WdiGenericRequest" is not iterable.')

            for i, data_item in enumerate(self.data):
                if data_item is None:
                    raise ValueError(f'Item {i} in property "Data" of "WdiGenericRequest" is None.')

                if not isinstance(data_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "Data" of "WdiGenericRequest" is not a number.')

                if int(data_item) != data_item:
                    raise ValueError(f'Item {i} in property "Data" of "WdiGenericRequest" is not integer value.')
