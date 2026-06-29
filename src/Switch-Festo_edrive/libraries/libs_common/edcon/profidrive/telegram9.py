"""Contains code that is related to PROFIDRIVE telegram 9"""
from dataclasses import dataclass, field
from edcon.profidrive.telegram_base import TelegramBase
from edcon.profidrive.words import \
    STW1_PM, SATZANW, STW2, MDI_TARPOS, MDI_VELOCITY, MDI_ACC, MDI_MOD, \
    MDI_DEC, ZSW1_PM, AKTSATZ, ZSW2, XIST_A


@dataclass(repr=False)
class Telegram9(TelegramBase):
    """Holds the implementation of PROFIDRIVE telegram 9"""
    # pylint: disable=too-many-instance-attributes
    # Twelve is needed here
    stw1: STW1_PM = field(default_factory=STW1_PM)
    satzanw: SATZANW = field(default_factory=SATZANW)
    stw2: STW2 = field(default_factory=STW2)
    mdi_tarpos: MDI_TARPOS = field(default_factory=MDI_TARPOS)
    mdi_velocity: MDI_VELOCITY = field(default_factory=MDI_VELOCITY)
    mdi_acc: MDI_ACC = field(default_factory=MDI_ACC)
    mdi_dec: MDI_DEC = field(default_factory=MDI_DEC)
    mdi_mod: MDI_MOD = field(default_factory=MDI_MOD)

    zsw1: ZSW1_PM = field(default_factory=ZSW1_PM)
    aktsatz: AKTSATZ = field(default_factory=AKTSATZ)
    zsw2: ZSW2 = field(default_factory=ZSW2)
    xist_a: XIST_A = field(default_factory=XIST_A)

    def input_bytes(self, data: bytes):
        """Sets the input words from provided byte data"""
        self.zsw1 = ZSW1_PM.from_bytes(data[0:2])
        self.aktsatz = AKTSATZ.from_bytes(data[2:4])
        self.zsw2 = ZSW2.from_bytes(data[4:6])
        self.xist_a = XIST_A.from_bytes(data[6:10])

    def output_bytes(self) -> bytes:
        """Returns the byte representation of the output words"""
        out_bytes = self.stw1.to_bytes()
        out_bytes += self.satzanw.to_bytes()
        out_bytes += self.stw2.to_bytes()
        out_bytes += self.mdi_tarpos.to_bytes()
        out_bytes += self.mdi_velocity.to_bytes()
        out_bytes += self.mdi_acc.to_bytes()
        out_bytes += self.mdi_dec.to_bytes()
        out_bytes += self.mdi_mod.to_bytes()
        return out_bytes
