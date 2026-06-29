import typing

if typing.TYPE_CHECKING:
    from typing_extensions import Protocol
else:
    Protocol = object


class DtoObject(Protocol):
    """ Protocol for DTO objects. """

    def to_binary(self) -> bytes:
        """" Serializes to a binary. """
        ...

    def validate(self) -> None:
        """" Checks if the object is valid. """
        ...
