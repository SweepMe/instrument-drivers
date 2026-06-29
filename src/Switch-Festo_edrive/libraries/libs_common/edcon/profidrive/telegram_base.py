"""Contains code that is related to PROFIDRIVE telegram base class"""
from dataclasses import fields


class TelegramBase:
    """Holds the base implementation of PROFIDRIVE telegrams"""

    def __post_init__(self):
        """Post initialization hook"""
        self.reset()

    def __len__(self):
        len_list = [len(getattr(self, item.name)) for item in fields(self)]
        return sum(len_list)

    def __repr__(self):
        """Implements a nicer representation for TelegramBase class"""
        attrs = [(item.name, getattr(self, item.name))
                 for item in fields(self)]
        val_str = ', '.join(
            [f"{n.upper()}=0x"
             f"{int.from_bytes(v.to_bytes(), 'little'):0{len(v) * 2}X}"
             for n, v in attrs])

        return f"{type(self).__name__}({val_str})"

    def reset(self):
        """Clears all attributes to default values."""
        for item in fields(self):
            if isinstance(getattr(self, item.name), int):
                setattr(self, item.name, item.default_factory().from_int(
                    getattr(self, item.name)))

            if not isinstance(getattr(self, item.name), type(item.default_factory())):
                raise ValueError(f"Invalid value type of {item.name}")
