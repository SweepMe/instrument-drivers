# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson


@dataclass
class ToolsListSerialPortsResponse:

    ports: List[str] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'ToolsListSerialPortsResponse':
        return ToolsListSerialPortsResponse(
            ports=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'ToolsListSerialPortsResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return ToolsListSerialPortsResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'ports': [str(item or '') for item in self.ports] if self.ports is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ToolsListSerialPortsResponse':
        return ToolsListSerialPortsResponse(
            ports=data.get('ports'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.ports is not None:
            if not isinstance(self.ports, Iterable):
                raise ValueError('Property "Ports" of "ToolsListSerialPortsResponse" is not iterable.')

            for i, ports_item in enumerate(self.ports):
                if ports_item is not None:
                    if not isinstance(ports_item, str):
                        raise ValueError(f'Item {i} in property "Ports" of "ToolsListSerialPortsResponse" is not a string.')
