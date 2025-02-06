# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Rohde&Schwarz RTx

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug


class Device(EmptyDevice):
    """Device class for the signal generator functions of Rohde&Schwarz RTx Oscilloscopes."""

    def __init__(self) -> None:
        """Initialize the Device Class."""
        super().__init__()

        self.shortname = "RTx"

        # Communication Parameters
        self.port_manager = True
        self.port_types = ["GPIB", "TCPIP", "USB"]
        self.port_properties = {
            "timeout": 2.0,
        }

        # SweepMe Parameters
        self.variables = []
        self.units = []
        self.plottype = []  # True to plot data
        self.savetype = []  # True to save data

        # Device Parameters
        self.waveforms = {
            "DC": "DC",
            "Sinus": "SIN",
            "Square": "SQU",
            "Pulse": "PULS",
            "Triangle": "TRI",
            "Ramp": "RAMP",
            "Sinc": "SINC",
            "Arbitrary": "ARB",
            "Exponential": "EXP",
        }
        self.waveform = "Sinus"
        self.impedances = {
            "50 Ohm": "R50",
            "High-Z": "HIGH",
        }
        self.impedance = "50 Ohm"

        self.sweep_mode: str = "None"

        self.frequency_mode: str = "Frequency in Hz"
        self.frequency: float = 1000
        self.amplitude_mode: str = "Amplitude in V"
        self.amplitude: float = 1.0
        self.offset_mode: str = "Offset in V"
        self.offset: float = 0.0
        self.duty_cycle_pulse_width_mode: str = "Duty cycle in %"
        self.duty_cycle_pulse_width: float = 50

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set the standard SweepMe GUI parameters."""
        return {
            "SweepMode": [
                "None",
                "Frequency in Hz",
                "Period in s",
                "Amplitude in V",
                # "High level in V",
                "Offset in V",
                # "Low level in V",
                # "Pulse width in s",
                "Duty cycle in %",
                # "Delay in s",
                # "Phase in deg",
            ],
            "PeriodFrequency": ["Frequency in Hz", "Period in s"],
            "PeriodFrequencyValue": 1000,
            "AmplitudeHiLevel": ["Amplitude in V"],
            "AmplitudeHiLevelValue": 1.0,
            "OffsetLoLevel": ["Offset in V"],
            "OffsetLoLevelValue": 0.0,
            "DutyCyclePulseWidth": ["Duty cycle in %"],
            "DutyCyclePulseWidthValue": 50,
            "Waveform": list(self.waveforms.keys()),
            "Impedance": list(self.impedances.keys()),
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle the SweepMe GUI parameters."""
        self.frequency_mode = parameter["PeriodFrequency"]
        self.frequency = parameter["PeriodFrequencyValue"]
        self.amplitude_mode = parameter["AmplitudeHiLevel"]
        self.amplitude = parameter["AmplitudeHiLevelValue"]
        self.offset_mode = parameter["OffsetLoLevel"]
        self.offset = parameter["OffsetLoLevelValue"]
        self.duty_cycle_pulse_width_mode = parameter["DutyCyclePulseWidth"]
        self.duty_cycle_pulse_width = parameter["DutyCyclePulseWidthValue"]
        self.waveform = parameter["Waveform"]
        self.impedance = parameter["Impedance"]

    def initialize(self) -> None:
        """Initialize the device."""
        self.port.write("*CLS")
        # do not use "SYST:PRES" as it will destroy all settings which is in conflict with using 'As is'

    def deinitialize(self) -> None:
        """Deinitialize the device."""
        self.port.write("SYST:KLOC OFF")  # unlocks the local control during measurement
        self.read_errors()  # read out the error queue

    def configure(self) -> None:
        """Configure the measurement."""
        self.set_impedance(self.impedance)
        self.set_waveform(self.waveform)

        self.set_amplitude(self.amplitude)
        self.set_offset(self.offset)

        if self.frequency_mode == "Period in s":
            self.frequency = 1 / self.frequency
        self.set_frequency(self.frequency)

        if self.duty_cycle_pulse_width_mode == "Duty cycle in %":
            self.set_duty_cycle(self.duty_cycle_pulse_width)

        self.enable_output(True)

    def unconfigure(self) -> None:
        """Unconfigure the measurement."""
        self.enable_output(False)

    def apply(self) -> None:
        """Apply the sweep value."""
        if self.sweep_mode.startswith("Frequency"):
            self.set_frequency(self.value)

        elif self.sweep_mode.startswith("Period"):
            self.set_frequency(1 / self.value)

        elif self.sweep_mode.startswith("Amplitude"):
            self.set_amplitude(self.value)

        elif self.sweep_mode.startswith("Offset"):
            self.set_offset(self.value)

        elif self.sweep_mode.startswith("Duty cycle"):
            self.set_duty_cycle(self.value)

    """ Wrapped commands """

    def read_errors(self) -> None:
        """Reads out all errors from the error queue and prints them to the debug."""
        self.port.write("SYST:ERR:COUN?")
        err_count = self.port.read()
        if int(err_count) > 0:
            self.port.write("SYST:ERR:CODE:ALL?")
            answer = self.port.read()
            for err in answer.split(","):
                debug("Signal R&S RTx error:", err)

    def get_identification(self) -> str:
        """Return the identification of the device."""
        self.port.write("*IDN?")
        return self.port.read()

    def set_impedance(self, impedance: str) -> None:
        """Set Impedance to either '50 Ohm' or 'High-Z'."""
        command = self.impedances[impedance]
        if command not in ("R50", "HIGH"):
            msg = f"Impedance {impedance} not supported."
            raise ValueError(msg)

        self.port.write(f"WGEN:OUTP:LOAD {command}")

    def set_waveform(self, waveform: str) -> None:
        """Set the function of the signal generator."""
        self.port.write(f"WGEN:FUNC {self.waveforms[waveform]}")

    def set_amplitude(self, amplitude: float) -> None:
        """Set the voltage of the signal generator."""
        max_amplitude = 6
        min_amplitude = 6e-2
        if amplitude < min_amplitude or amplitude > max_amplitude:
            msg = (
                f"Ampltiude {amplitude} out of range. Please set amplitude between {min_amplitude} and {min_amplitude}."
            )
            raise ValueError(msg)
        self.port.write(f"WGEN:VOLT {amplitude}")

    def set_offset(self, offset: float) -> None:
        """Set the offset of the signal generator."""
        max_offset = 3
        min_offset = -3
        if offset < min_offset or offset > max_offset:
            msg = f"Offset {offset} out of range. Please set offset between {min_offset} and {max_offset}."
            raise ValueError(msg)
        self.port.write(f"WGEN:VOLT:OFFS {offset}")

    def set_frequency(self, frequency: float) -> None:
        """Set the frequency of the signal generator."""
        max_frequency = 1e6
        min_frequency = 1e-6
        if frequency < min_frequency or frequency > max_frequency:
            msg = (
                f"Frequency {frequency} out of range. Please set frequency between {min_frequency} and {max_frequency}."
            )
            raise ValueError(msg)
        self.port.write(f"WGEN:FREQ {frequency}")

    def set_duty_cycle(self, duty_cycle_percent: float) -> None:
        """Set the duty cycle of the signal generator."""
        max_duty_cycle = 9e1
        min_duty_cycle = 1e1
        if duty_cycle_percent < min_duty_cycle or duty_cycle_percent > max_duty_cycle:
            msg = (f"Duty cycle {duty_cycle_percent} out of range. Please set duty cycle between {min_duty_cycle} "
                   f"and {max_duty_cycle}.")
            raise ValueError(msg)
        self.port.write(f"WGEN:FUNC:PULS:DCYC {duty_cycle_percent}")

    def enable_output(self, state: bool) -> None:
        """Enable or disable the output of the signal generator."""
        command = "ON" if state else "OFF"
        self.port.write(f"WGEN:OUTP {command}")
