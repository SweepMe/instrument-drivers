# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from .translate_message import TranslateMessage


@dataclass
class TranslateResult:
    """
    Represents a result of a G-code block translation.
    """

    commands: List[str]
    """
    Stream commands resulting from the block.
    """

    warnings: List[TranslateMessage]
    """
    Messages informing about unsupported codes and features.
    """

    @staticmethod
    def zero_values() -> 'TranslateResult':
        return TranslateResult(
            commands=[],
            warnings=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TranslateResult':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TranslateResult.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'commands': [str(item or '') for item in self.commands] if self.commands is not None else [],
            'warnings': [item.to_dict() for item in self.warnings] if self.warnings is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TranslateResult':
        return TranslateResult(
            commands=data.get('commands'),  # type: ignore
            warnings=[TranslateMessage.from_dict(item) for item in data.get('warnings')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.commands is not None:
            if not isinstance(self.commands, Iterable):
                raise ValueError('Property "Commands" of "TranslateResult" is not iterable.')

            for i, commands_item in enumerate(self.commands):
                if commands_item is not None:
                    if not isinstance(commands_item, str):
                        raise ValueError(f'Item {i} in property "Commands" of "TranslateResult" is not a string.')

        if self.warnings is not None:
            if not isinstance(self.warnings, Iterable):
                raise ValueError('Property "Warnings" of "TranslateResult" is not iterable.')

            for i, warnings_item in enumerate(self.warnings):
                if warnings_item is None:
                    raise ValueError(f'Item {i} in property "Warnings" of "TranslateResult" is None.')

                if not isinstance(warnings_item, TranslateMessage):
                    raise ValueError(f'Item {i} in property "Warnings" of "TranslateResult" is not an instance of "TranslateMessage".')

                warnings_item.validate()
