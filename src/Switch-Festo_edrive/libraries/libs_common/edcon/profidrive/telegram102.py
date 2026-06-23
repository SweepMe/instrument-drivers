"""Contains code that is related to PROFIDRIVE telegram 102"""
from dataclasses import dataclass, field
from edcon.profidrive.telegram_base import TelegramBase
from edcon.profidrive.words import \
    STW1_SM, NSOLL_B, STW2, MOMRED, G1_STW, ZSW1_SM, \
    NIST_B, ZSW2, MELDW, G1_ZSW, G1_XIST1, G1_XIST2


@dataclass(repr=False)
class Telegram102(TelegramBase):
    """Holds the implementation of PROFIDRIVE telegram 102"""
    # pylint: disable=too-many-instance-attributes
    # Twelve is needed here
    stw1: STW1_SM = field(default_factory=STW1_SM)
    nsoll_b: NSOLL_B = field(default_factory=NSOLL_B)
    stw2: STW2 = field(default_factory=STW2)
    momred: MOMRED = field(default_factory=MOMRED)
    g1_stw: G1_STW = field(default_factory=G1_STW)

    zsw1: ZSW1_SM = field(default_factory=ZSW1_SM)
    nist_b: NIST_B = field(default_factory=NIST_B)
    zsw2: ZSW2 = field(default_factory=ZSW2)
    meldw: MELDW = field(default_factory=MELDW)
    g1_zsw: G1_ZSW = field(default_factory=G1_ZSW)
    g1_xist1: G1_XIST1 = field(default_factory=G1_XIST1)
    g1_xist2: G1_XIST2 = field(default_factory=G1_XIST2)

    def input_bytes(self, data: bytes):
        """Sets the input words from provided byte data"""
        self.zsw1 = ZSW1_SM.from_bytes(data[0:2])
        self.nist_b = NIST_B.from_bytes(data[2:6])
        self.zsw2 = ZSW2.from_bytes(data[6:8])
        self.meldw = MELDW.from_bytes(data[8:10])
        self.g1_zsw = G1_ZSW.from_bytes(data[10:12])
        self.g1_xist1 = G1_XIST1.from_bytes(data[12:16])
        self.g1_xist2 = G1_XIST2.from_bytes(data[16:20])

    def output_bytes(self) -> bytes:
        """Returns the byte representation of the output words"""
        return self.stw1.to_bytes() + self.nsoll_b.to_bytes() + self.stw2.to_bytes() + \
            self.momred.to_bytes() + self.g1_stw.to_bytes()
