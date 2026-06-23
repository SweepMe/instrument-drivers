"""Contains code that is related to PROFIDRIVE telegram 1"""
from dataclasses import dataclass, field
from edcon.profidrive.telegram_base import TelegramBase
from edcon.profidrive.words import STW1_SM, ZSW1_SM, NSOLL_A, NIST_A


@dataclass(repr=False)
class Telegram1(TelegramBase):
    """Holds the implementation of PROFIDRIVE telegram 1"""
    stw1: STW1_SM = field(default_factory=STW1_SM)
    nsoll_a: NSOLL_A = field(default_factory=NSOLL_A)

    zsw1: ZSW1_SM = field(default_factory=ZSW1_SM)
    nist_a: NIST_A = field(default_factory=NIST_A)

    def input_bytes(self, data: bytes):
        """Sets the input words from provided byte data"""
        self.zsw1 = ZSW1_SM.from_bytes(data[0:2])
        self.nist_a = NIST_A.from_bytes(data[2:4])

    def output_bytes(self) -> bytes:
        """Returns the byte representation of the output words"""
        return self.stw1.to_bytes() + self.nsoll_a.to_bytes()
