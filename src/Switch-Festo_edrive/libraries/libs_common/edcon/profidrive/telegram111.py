"""Contains code that is related to PROFIDRIVE telegram 111"""
from dataclasses import dataclass, field
from edcon.profidrive.telegram_base import TelegramBase
from edcon.profidrive.words import \
    STW1_PM, POS_STW1, POS_STW2, STW2, OVERRIDE, MDI_TARPOS, MDI_VELOCITY, MDI_ACC, \
    MDI_DEC, ZSW1_PM, POS_ZSW1, POS_ZSW2, ZSW2, MELDW, XIST_A, NIST_B, FAULT_CODE, WARN_CODE


@dataclass(repr=False)
class Telegram111(TelegramBase):
    """Holds the implementation of PROFIDRIVE telegram 111"""
    # pylint: disable=too-many-instance-attributes
    # Eighteen is needed here
    stw1: STW1_PM = field(default_factory=STW1_PM)
    pos_stw1: POS_STW1 = field(default_factory=POS_STW1)
    pos_stw2: POS_STW2 = field(default_factory=POS_STW2)
    stw2: STW2 = field(default_factory=STW2)
    override: OVERRIDE = field(default_factory=OVERRIDE)
    mdi_tarpos: MDI_TARPOS = field(default_factory=MDI_TARPOS)
    mdi_velocity: MDI_VELOCITY = field(default_factory=MDI_VELOCITY)
    mdi_acc: MDI_ACC = field(default_factory=MDI_ACC)
    mdi_dec: MDI_DEC = field(default_factory=MDI_DEC)

    zsw1: ZSW1_PM = field(default_factory=ZSW1_PM)
    pos_zsw1: POS_ZSW1 = field(default_factory=POS_ZSW1)
    pos_zsw2: POS_ZSW2 = field(default_factory=POS_ZSW2)
    zsw2: ZSW2 = field(default_factory=ZSW2)
    meldw: MELDW = field(default_factory=MELDW)
    xist_a: XIST_A = field(default_factory=XIST_A)
    nist_b: NIST_B = field(default_factory=NIST_B)
    fault_code: FAULT_CODE = field(default_factory=FAULT_CODE)
    warn_code: WARN_CODE = field(default_factory=WARN_CODE)

    def input_bytes(self, data: bytes):
        """Sets the input words from provided byte data"""
        self.zsw1 = ZSW1_PM.from_bytes(data[0:2])
        self.pos_zsw1 = POS_ZSW1.from_bytes(data[2:4])
        self.pos_zsw2 = POS_ZSW2.from_bytes(data[4:6])
        self.zsw2 = ZSW2.from_bytes(data[6:8])
        self.meldw = MELDW.from_bytes(data[8:10])
        self.xist_a = XIST_A.from_bytes(data[10:14])
        self.nist_b = NIST_B.from_bytes(data[14:18])
        self.fault_code = FAULT_CODE.from_bytes(data[18:20])
        self.warn_code = WARN_CODE.from_bytes(data[20:22])

    def output_bytes(self) -> bytes:
        """Returns the byte representation of the output words"""
        out_bytes = self.stw1.to_bytes()
        out_bytes += self.pos_stw1.to_bytes()
        out_bytes += self.pos_stw2.to_bytes()
        out_bytes += self.stw2.to_bytes()
        out_bytes += self.override.to_bytes()
        out_bytes += self.mdi_tarpos.to_bytes()
        out_bytes += self.mdi_velocity.to_bytes()
        out_bytes += self.mdi_acc.to_bytes()
        out_bytes += self.mdi_dec.to_bytes()
        return out_bytes
