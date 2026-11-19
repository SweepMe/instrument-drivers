# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025-2026 SweepMe! GmbH (sweep-me.net)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# SweepMe! driver
# * Module: Signal
# * Instrument: Rohde&Schwarz SMB100A

from __future__ import annotations

import math
import re
from typing import Annotated, Any, Literal

from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

# What the communication commands take and answer (checked by @command on every call). The instrument commands are
# taken from the R&S SMB100A Operating Manual, version 23 (firmware 5.00.116), chapter 6 "Remote Control Commands".
Hertz = Annotated[float, Unit("Hz")]
Degrees = Annotated[float, Unit("deg")]
Seconds = Annotated[float, Unit("s")]
Decibel = Annotated[float, Unit("dB")]
Percent = Annotated[float, Unit("%")]
Ohm = Annotated[float, Unit("Ohm")]
# The RF level is set and read in the unit selected with set_power_unit (dBm, dBuV or V; :UNIT:POWer, section 6.18),
# so no unit is declared for it. Its range depends on the frequency option and the attenuator (section 2.2 and
# [:SOURce<hw>]:POWer[:LEVel][:IMMediate][:AMPLitude], "Minimum level ... Maximum level"), so no Range is declared.
Level = float

FrequencyMode = Literal["CW", "FIX", "SWE", "LIST"]  # [:SOURce<hw>]:FREQuency:MODE
PowerMode = Literal["CW", "FIX", "SWE"]  # [:SOURce<hw>]:POWer:MODE
PowerUnit = Literal["DBM", "DBUV", "V"]  # :UNIT:POWer
RfMode = Literal["NORM", "LOWN", "LOWD"]  # [:SOURce<hw>]:POWer:LMODe: normal, low noise, low distortion
AmplitudeModulationType = Literal["LIN", "EXP"]  # [:SOURce<hw>]:AM:TYPE
DataFormat = Literal["ASC", "PACK"]  # :FORMat[:DATA]

# The amplitude choices of the Signal module and the power unit each one needs (:UNIT:POWer)
AMPLITUDE_UNITS: dict[str, PowerUnit] = {
    "Amplitude in V": "V",
    "Amplitude in dBm": "DBM",
    "Amplitude in dBuV": "DBUV",
}

# The impedance answers of :OUTPut<hw>:IMPedance? in Ohm; the instrument may also answer the plain number
IMPEDANCES: dict[str, float] = {"G50": 50.0, "G1K": 1000.0, "G10K": 10000.0}


class Device(EmptyDevice):
    """Driver for the Rohde & Schwarz SMB100A RF and microwave signal generator."""

    def __init__(self) -> None:
        """Define the returned variables and the port."""
        super().__init__()

        self.shortname = "SMB100A"

        self.port_manager = True
        self.port_types = ["USB", "TCPIP"]

        self.variables = ["Frequency", "RF Power level"]
        self.units = ["Hz", "V"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # GUI parameters, exactly as they arrive from the GUI; converted in configure()
        self.gui_parameters: dict[str, Any] = {}
        self.sweep_mode: str = "None"
        self.period_frequency_mode: str = "Frequency in Hz"
        self.amplitude_mode: str = "Amplitude in V"
        self.delay_phase_mode: str = "Delay in s"

        # Values derived from the GUI parameters
        self.frequency: float = 2e6
        self.amplitude: float = 1.0
        self.power_unit: PowerUnit = "V"
        self.delay_phase_value: float = 0.0

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI fields of the Signal module."""
        return {
            "SweepMode": [
                "None",
                "Frequency in Hz",
                "Period in s",
                *AMPLITUDE_UNITS,
                "Phase in deg",
                "Delay in s",
            ],
            "Waveform": ["Sinus"],
            "PeriodFrequency": ["Frequency in Hz", "Period in s"],
            "PeriodFrequencyValue": 2e6,
            "AmplitudeHiLevel": list(AMPLITUDE_UNITS),
            "AmplitudeHiLevelValue": 1.0,
            "DelayPhase": ["Delay in s", "Phase in deg"],
            "DelayPhaseValue": 0.0,
            "Impedance": ["50"],
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the user's selections and derive the returned variables from them.

        The values are kept as they arrive and converted to numbers in configure(), because this method is called
        repeatedly, also with incomplete dictionaries.
        """
        self.gui_parameters = dict(parameters)
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.period_frequency_mode = parameters.get("PeriodFrequency", "Frequency in Hz")
        self.amplitude_mode = parameters.get("AmplitudeHiLevel", "Amplitude in V")
        self.delay_phase_mode = parameters.get("DelayPhase", "Delay in s")

        # "Period in s" -> variable "Period" in "s"; the level is returned in the unit of the amplitude choice
        quantity, _, unit = self.period_frequency_mode.partition(" in ")
        self.variables = [quantity, "RF Power level"]
        self.units = [unit, self.amplitude_mode.partition(" in ")[2]]

    def initialize(self) -> None:
        """Check the user input, reset the instrument and lock its front panel."""
        self.convert_gui_parameters()
        self.reset_instrument()
        self.set_user_interface_lock(True)

    def configure(self) -> None:
        """Set level, frequency and phase in CW mode and switch the RF output on."""
        self.convert_gui_parameters()

        self.set_power_mode("CW")
        self.set_power_unit(self.power_unit)
        self.set_amplitude(self.amplitude)

        self.set_frequency_mode("CW")
        self.set_frequency(self.frequency)

        self.apply_delay_phase(self.delay_phase_mode, self.delay_phase_value)

        self.set_output(True)

    def unconfigure(self) -> None:
        """Log the errors of the run, switch the RF output off and unlock the front panel."""
        for error in self.get_errors():
            self.message_log(f"SMB100A reported: {error}")

        self.set_output(False)
        self.set_user_interface_lock(False)

    def reconfigure(self, parameters: dict[str, Any], keys: list[str]) -> None:
        """Re-apply only the GUI values that changed through the parameter syntax during a run."""
        self.gui_parameters.update(parameters)

        if "PeriodFrequencyValue" in keys or "PeriodFrequency" in keys:
            self.period_frequency_mode = parameters.get("PeriodFrequency", self.period_frequency_mode)
            value = float(parameters.get("PeriodFrequencyValue", self.frequency))
            self.frequency = self.to_frequency(self.period_frequency_mode, value)
            self.set_frequency(self.frequency)

        if "AmplitudeHiLevelValue" in keys:
            self.amplitude = float(parameters.get("AmplitudeHiLevelValue", self.amplitude))
            self.set_amplitude(self.amplitude)

        if "DelayPhaseValue" in keys or "DelayPhase" in keys:
            self.delay_phase_mode = parameters.get("DelayPhase", self.delay_phase_mode)
            self.delay_phase_value = float(parameters.get("DelayPhaseValue", self.delay_phase_value))
            self.apply_delay_phase(self.delay_phase_mode, self.delay_phase_value)

    def apply(self) -> None:
        """Set the new sweep value."""
        value = float(self.value)

        if self.sweep_mode in AMPLITUDE_UNITS:
            # The sweep value comes in the unit of the sweep mode, which may differ from the amplitude choice;
            # call() switches back before reading the level in the unit of self.units
            sweep_unit = AMPLITUDE_UNITS[self.sweep_mode]
            if sweep_unit != self.power_unit:
                self.set_power_unit(sweep_unit)
            self.set_amplitude(value)

        elif self.sweep_mode.startswith("Frequency"):
            self.frequency = value
            self.set_frequency(self.frequency)

        elif self.sweep_mode.startswith("Period"):
            self.frequency = self.to_frequency(self.sweep_mode, value)
            self.set_frequency(self.frequency)

        elif self.sweep_mode.startswith("Phase"):
            self.set_phase(value)

        elif self.sweep_mode.startswith("Delay"):
            self.set_delay(value)

    def call(self) -> list[float]:
        """Return the frequency or period and the level at the RF output."""
        frequency = self.get_frequency()

        if self.sweep_mode in AMPLITUDE_UNITS and AMPLITUDE_UNITS[self.sweep_mode] != self.power_unit:
            self.set_power_unit(self.power_unit)
        power_level = self.get_power_level()

        if self.period_frequency_mode.startswith("Period"):
            return [1.0 / frequency if frequency else float("nan"), power_level]
        return [frequency, power_level]

    # Communication commands, one per instrument command. Section numbers refer to the operating manual.

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the identification: Rohde&Schwarz,<device type>,<part number>/<serial number>,<firmware>."""
        return str(self.port.query("*IDN?"))

    @command(warnings="Switches the RF output off and resets level, frequency, phase and power unit to their defaults.")
    def reset_instrument(self) -> None:
        """Reset the instrument to its default settings (*RST)."""
        self.port.write("*RST")

    @command(returns=("self_test_passed",))
    def run_self_test(self) -> bool:
        """Run the self test of the instrument (*TST?), which takes longer than a normal query; True when it passed."""
        return int(self.port.query("*TST?")) == 0

    @command(returns=("errors",), reads="state")
    def get_errors(self) -> list[str]:
        """Return and clear all entries of the error queue as "<code>,<description>"; empty when there is none."""
        answer = str(self.port.query("SYST:ERR:ALL?")).strip()
        # Entries come as <number>,"<description>"[,<number>,"<description>"...]; 0,"No error" for an empty queue
        # (section 6.17). The example of the manual quotes with ' instead of ", so both are accepted.
        entries = re.findall(r"""(-?\d+)\s*,\s*["']([^"']*)["']""", answer)
        if not entries:
            return [] if answer.startswith("0") else [answer]
        return [f"{code},{description}" for code, description in entries if int(code) != 0]

    @command
    def set_user_interface_lock(self, user_interface_lock: bool) -> None:
        """Lock (True) or unlock (False) the front panel controls; the display keeps showing the settings."""
        # :SYSTem:ULOCk DONLy locks the controls only; DISabled (lock with VNC) is not offered (section 6.17)
        self.port.write(f"SYST:ULOC {'DONL' if user_interface_lock else 'ENAB'}")

    @command(returns=("user_interface_lock",), reads="setpoint")
    def get_user_interface_lock(self) -> bool:
        """Return whether the front panel controls are locked."""
        return not str(self.port.query("SYST:ULOC?")).strip().upper().startswith("ENAB")

    @command(warnings="Restarts the firmware: the connection is lost and every setting returns to its default.")
    def restart_firmware(self) -> None:
        """Restart the firmware of the instrument; the operating system keeps running."""
        self.port.write("SYST:REST")

    @command(warnings="Switches the instrument off: the connection is lost; switch it on again at the front panel.")
    def shutdown_device(self) -> None:
        """Shut the instrument down."""
        self.port.write("SYST:SHUT")

    @command
    def set_data_format(self, data_format: DataFormat) -> None:
        """Set the format of the data the instrument returns; the readers of this driver expect ASC."""
        self.port.write(f"FORM {data_format}")

    @command(returns=("data_format",), reads="setpoint")
    def get_data_format(self) -> DataFormat:
        """Return the format of the data the instrument returns."""
        return str(self.port.query("FORM?")).strip()  # type: ignore[return-value]  # one of DataFormat

    @command
    def set_frequency_mode(self, frequency_mode: FrequencyMode) -> None:
        """Set the frequency mode: fixed (CW, FIX), sweep (SWE) or list (LIST)."""
        self.port.write(f"SOUR:FREQ:MODE {frequency_mode}")

    @command(returns=("frequency_mode",), reads="setpoint")
    def get_frequency_mode(self) -> FrequencyMode:
        """Return the frequency mode."""
        return str(self.port.query("SOUR:FREQ:MODE?")).strip()  # type: ignore[return-value]  # one of FrequencyMode

    @command
    def set_frequency(self, frequency: Hertz) -> None:
        """Set the frequency of the RF output; the range depends on the installed frequency option (B101 to B140)."""
        self.port.write(f"SOUR:FREQ {frequency}")
        self.frequency = float(frequency)  # set_delay converts a delay at the frequency set last

    @command(returns=("frequency",), reads="setpoint")
    def get_frequency(self) -> Hertz:
        """Return the frequency of the RF output, including a frequency offset and multiplier if set."""
        return float(self.port.query("SOUR:FREQ?"))

    @command
    def set_phase(self, phase: Degrees) -> None:
        """Set the phase of the RF signal relative to its reference phase (the "Delta Phase" of the instrument)."""
        # [:SOURce<hw>]:PHASe takes radians (section 6.13.10); the bound of -720 to 720 given there is not declared
        # because the manual does not say whether it applies to radians or degrees
        self.port.write(f"SOUR:PHAS {math.radians(phase)}")

    @command(returns=("phase",), reads="setpoint")
    def get_phase(self) -> Degrees:
        """Return the phase of the RF signal relative to its reference phase."""
        return math.degrees(float(self.port.query("SOUR:PHAS?")))

    @command
    def reset_phase_reference(self) -> None:
        """Adopt the current phase as the new reference phase, so that the phase reads 0 afterwards."""
        self.port.write("SOUR:PHAS:REF")

    @command(composite=True)
    def set_delay(self, delay: Seconds) -> None:
        """Set the phase as a delay of the RF signal at the frequency set last; a positive delay is a positive phase."""
        # fmod keeps the sign of the delay, so a negative delay stays a negative phase
        self.set_phase(math.fmod(delay * self.frequency * 360.0, 360.0))

    @command
    def set_power_mode(self, power_mode: PowerMode) -> None:
        """Set the level mode: constant level (CW, FIX) or level sweep (SWE)."""
        self.port.write(f"SOUR:POW:MODE {power_mode}")

    @command(returns=("power_mode",), reads="setpoint")
    def get_power_mode(self) -> PowerMode:
        """Return the level mode."""
        return str(self.port.query("SOUR:POW:MODE?")).strip()  # type: ignore[return-value]  # one of PowerMode

    @command
    def set_power_unit(self, power_unit: PowerUnit) -> None:
        """Set the unit of every level value that is sent to or read from the instrument: DBM, DBUV or V."""
        self.port.write(f"UNIT:POW {power_unit}")

    @command(returns=("power_unit",), reads="setpoint")
    def get_power_unit(self) -> PowerUnit:
        """Return the unit of the level values."""
        return str(self.port.query("UNIT:POW?")).strip()  # type: ignore[return-value]  # one of PowerUnit

    @command
    def set_amplitude(self, amplitude: Level) -> None:
        """Set the RF level, in the power unit, as shown on the display: the level at the output plus the offset."""
        self.port.write(f"SOUR:POW:LEV:IMM:AMPL {amplitude}")

    @command(returns=("amplitude",), reads="setpoint")
    def get_amplitude(self) -> Level:
        """Return the RF level, in the power unit, as shown on the display: the level at the output plus the offset."""
        return float(self.port.query("SOUR:POW:LEV:IMM:AMPL?"))

    @command(returns=("power_level",), reads="setpoint")
    def get_power_level(self) -> Level:
        """Return the level at the RF output connector, in the power unit, without the level offset."""
        return float(self.port.query("SOUR:POW:POW?"))

    @command
    def set_level_offset(self, level_offset: Annotated[Decibel, Range(-100.0, 100.0)]) -> None:
        """Set the level offset of a downstream attenuator or amplifier; it does not change the output level."""
        self.port.write(f"SOUR:POW:LEV:IMM:OFFS {level_offset}")

    @command(returns=("level_offset",), reads="setpoint")
    def get_level_offset(self) -> Decibel:
        """Return the level offset."""
        return float(self.port.query("SOUR:POW:LEV:IMM:OFFS?"))

    @command
    def set_rf_mode(self, rf_mode: RfMode) -> None:
        """Set the RF level mode: normal (NORM), low noise (LOWN) or low distortion (LOWD)."""
        self.port.write(f"SOUR:POW:LMOD {rf_mode}")

    @command(returns=("rf_mode",), reads="setpoint")
    def get_rf_mode(self) -> RfMode:
        """Return the RF level mode."""
        return str(self.port.query("SOUR:POW:LMOD?")).strip()  # type: ignore[return-value]  # one of RfMode

    @command
    def set_output(self, output: bool) -> None:
        """Switch the RF output on (True) or off (False)."""
        self.port.write(f"OUTP {'ON' if output else 'OFF'}")

    @command(returns=("output",), reads="setpoint")
    def get_output(self) -> bool:
        """Return whether the RF output is on."""
        return self.to_bool(str(self.port.query("OUTP?")))

    @command(returns=("impedance",), reads="state")
    def get_impedance(self) -> Ohm:
        """Return the impedance of the RF output, which cannot be changed."""
        answer = str(self.port.query("OUTP:IMP?")).strip().upper()
        if answer in IMPEDANCES:
            return IMPEDANCES[answer]
        try:
            return float(answer)
        except ValueError:
            msg = f"The SMB100A answered '{answer}' to the impedance query, expected G50, G1K, G10K or a number."
            raise ValueError(msg) from None

    @command
    def set_amplitude_modulation(self, amplitude_modulation: bool) -> None:
        """Switch the amplitude modulation on (True) or off (False)."""
        self.port.write(f"SOUR:AM:STAT {'ON' if amplitude_modulation else 'OFF'}")

    @command(returns=("amplitude_modulation",), reads="setpoint")
    def get_amplitude_modulation(self) -> bool:
        """Return whether the amplitude modulation is on."""
        return self.to_bool(str(self.port.query("SOUR:AM:STAT?")))

    @command
    def set_amplitude_modulation_type(self, amplitude_modulation_type: AmplitudeModulationType) -> None:
        """Set linear (LIN) or exponential (EXP) amplitude modulation; EXP needs a 12 GHz or higher frequency option."""
        self.port.write(f"SOUR:AM:TYPE {amplitude_modulation_type}")

    @command(returns=("amplitude_modulation_type",), reads="setpoint")
    def get_amplitude_modulation_type(self) -> AmplitudeModulationType:
        """Return the amplitude modulation type."""
        return str(self.port.query("SOUR:AM:TYPE?")).strip()  # type: ignore[return-value]  # one of the type

    @command
    def set_linear_modulation_depth(self, linear_modulation_depth: Annotated[Percent, Range(0.0, 100.0)]) -> None:
        """Set the depth of the linear amplitude modulation."""
        self.port.write(f"SOUR:AM:DEPT:LIN {linear_modulation_depth}")

    @command(returns=("linear_modulation_depth",), reads="setpoint")
    def get_linear_modulation_depth(self) -> Percent:
        """Return the depth of the linear amplitude modulation."""
        return float(self.port.query("SOUR:AM:DEPT:LIN?"))

    @command
    def set_exponential_modulation_depth(
        self,
        exponential_modulation_depth: Annotated[Decibel, Range(-40.0, 40.0)],
    ) -> None:
        """Set the depth of the exponential amplitude modulation."""
        self.port.write(f"SOUR:AM:DEPT:EXP {exponential_modulation_depth}")

    @command(returns=("exponential_modulation_depth",), reads="setpoint")
    def get_exponential_modulation_depth(self) -> Decibel:
        """Return the depth of the exponential amplitude modulation."""
        return float(self.port.query("SOUR:AM:DEPT:EXP?"))

    # Helpers

    # check_driver: ignore DC004 - a helper of the semantic functions, not a command
    def convert_gui_parameters(self) -> None:
        """Convert the GUI parameters to numbers and check them, with a message for the user where they are wrong."""
        try:
            period_frequency_value = float(self.gui_parameters.get("PeriodFrequencyValue", 2e6))
            self.amplitude = float(self.gui_parameters.get("AmplitudeHiLevelValue", 1.0))
            self.delay_phase_value = float(self.gui_parameters.get("DelayPhaseValue", 0.0))
        except (TypeError, ValueError) as e:
            msg = f"SMB100A: the frequency, amplitude and delay/phase fields need numbers: {e}"
            raise ValueError(msg) from e

        self.frequency = self.to_frequency(self.period_frequency_mode, period_frequency_value)

        if self.amplitude_mode not in AMPLITUDE_UNITS:
            choices = ", ".join(AMPLITUDE_UNITS)
            msg = f"SMB100A: the amplitude choice '{self.amplitude_mode}' is unknown; choose one of {choices}."
            raise ValueError(msg)
        self.power_unit = AMPLITUDE_UNITS[self.amplitude_mode]

    # check_driver: ignore DC004 - a helper of the semantic functions, not a command
    def apply_delay_phase(self, delay_phase_mode: str, delay_phase_value: float) -> None:
        """Send a phase in degrees or a delay in seconds, as selected in the DelayPhase field."""
        if delay_phase_mode.startswith("Phase"):
            self.set_phase(delay_phase_value)
        elif delay_phase_mode.startswith("Delay"):
            self.set_delay(delay_phase_value)

    @staticmethod
    def to_frequency(period_frequency_mode: str, period_frequency_value: float) -> float:
        """Return the frequency in Hz of a frequency or period value; a period of 0 s stops with a message."""
        if period_frequency_mode.startswith("Period"):
            if period_frequency_value == 0:
                msg = "SMB100A: the period must not be 0 s."
                raise ValueError(msg)
            return 1.0 / period_frequency_value
        return period_frequency_value

    @staticmethod
    def to_bool(answer: str) -> bool:
        """Return True for a 1 or ON answer of the instrument."""
        return answer.strip().upper() in ("1", "ON")
