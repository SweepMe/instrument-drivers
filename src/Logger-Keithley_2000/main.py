# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2020-2026 SweepMe! GmbH (sweep-me.net)
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
# * Module: Logger
# * Instrument: Keithley 2000

"""SweepMe! driver for the Keithley 2000 digital multimeter."""

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keithley 2000 digital multimeter."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "Keithley2000"

        self.port_manager = True
        self.port_types = ["COM", "GPIB"]

        self.port_properties = {
            # AC functions with slow rate need 1.2 s per reading, auto range can need several readings
            "timeout": 10,
            "EOL": "\r",
            "baudrate": 9600,  # factory default
        }

        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        self.modes = {
            "Voltage DC": "VOLT:DC",
            "Voltage AC": "VOLT:AC",
            "Current DC": "CURR:DC",
            "Current AC": "CURR:AC",
            "Resistance": "RES",
            "FResistance": "FRES",
            "Frequency": "FREQ",
            "Period": "PER",
            "Temperature": "TEMP",
            "Diode": "DIOD",
            "Continuity": "CONT",
        }

        # this dictionary sets the unit of each mode, the temperature unit is chosen by the user
        self.mode_units = {
            "Voltage DC": "V",
            "Voltage AC": "V",
            "Current DC": "A",
            "Current AC": "A",
            "Resistance": "Ohm",
            "FResistance": "Ohm",
            "Frequency": "Hz",
            "Period": "s",
            "Diode": "V",
            "Continuity": "Ohm",
        }

        # the integration time cannot be set for frequency, period, diode test, and continuity
        self.nplc_modes = [
            "Voltage DC",
            "Voltage AC",
            "Current DC",
            "Current AC",
            "Resistance",
            "FResistance",
            "Temperature",
        ]

        # auto range is only available for voltage, current, and resistance
        self.autorange_modes = ["Voltage DC", "Voltage AC", "Current DC", "Current AC", "Resistance", "FResistance"]

        self.nplc_types = {
            "Fastest (0.01)": 0.01,
            "Fast (0.1)": 0.1,
            "Medium (1.0)": 1.0,
            "Slow (10.0)": 10.0,
        }

        self.temperature_units = ["°C", "K", "°F"]

        # GUI parameters
        self.port_string: str = ""
        self.mode: str = "Voltage DC"
        self.nplc: float = 1.0
        self.display: str = "On"
        self.temperature_unit: str = "°C"

        # measured value
        self.value_measured: float = float("nan")

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the GUI parameters and their options depending on the current selection."""
        mode = parameters.get("Mode", "Voltage DC")

        new_parameters: dict[str, Any] = {
            "Mode": list(self.modes.keys()),
        }

        if mode in self.nplc_modes:
            new_parameters["NPLC"] = list(self.nplc_types.keys())

        new_parameters.update(
            {
                "Range": ["Auto"],
                "Display": ["On", "Off"],
            },
        )

        if mode == "Temperature":
            new_parameters["Temperature unit"] = self.temperature_units

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the GUI parameters selected by the user and update the returned variables."""
        self.port_string = parameters.get("Port", "")
        self.mode = parameters.get("Mode", "Voltage DC")
        if self.mode in self.nplc_modes:
            self.nplc = self.nplc_types.get(parameters.get("NPLC", "Medium (1.0)"), 1.0)
        self.display = parameters.get("Display", "On")

        self.variables = [self.mode]

        if self.mode == "Temperature":
            self.temperature_unit = parameters.get("Temperature unit", "°C")
            self.units = [self.temperature_unit]
        else:
            self.units = [self.mode_units[self.mode]]

        self.plottype = [True]
        self.savetype = [True]

    def initialize(self) -> None:
        """Reset the instrument once at the beginning of the measurement."""
        self.reset()
        self.clear_status()
        self.set_beeper(False)

        # no instance has configured a measurement function yet
        self.device_communication[self.port_string] = {"mode": None}

    def deinitialize(self) -> None:
        """Restore the front panel settings at the end of the measurement."""
        if self.display == "Off":
            self.set_display(True)
        self.set_beeper(True)

    def configure(self) -> None:
        """Configure the measurement function and the trigger."""
        self.configure_mode()

        if self.display == "Off":
            self.set_display(False)

        # needed to use the "READ?" command
        self.set_continuous_initiation(False)

    def unconfigure(self) -> None:
        """Switch the display on again if it was switched off."""
        if self.display == "Off":
            self.set_display(True)

    def measure(self) -> None:
        """Trigger a measurement and read the result.

        Triggering and reading are done in the same phase, so that several driver instances sharing the same
        instrument cannot interleave their requests.
        """
        # another driver instance on the same instrument might have changed the measurement function
        if self.device_communication[self.port_string]["mode"] != self.mode:
            self.configure_mode()

        self.value_measured = self.read_value()

    def call(self) -> list[float]:
        """Return the measured value."""
        return [self.value_measured]

    def configure_mode(self) -> None:
        """Set the measurement function including its temperature unit, integration time, and range."""
        self.set_function(self.modes[self.mode])

        if self.mode == "Temperature":
            self.set_temperature_unit(self.temperature_unit.replace("°", ""))

        if self.mode in self.nplc_modes:
            self.set_nplc(self.modes[self.mode], self.nplc)

        if self.mode in self.autorange_modes:
            self.set_autorange(self.modes[self.mode], True)

        self.device_communication[self.port_string]["mode"] = self.mode

    """ here, communication commands are wrapped into python convenience functions """

    def get_identification(self) -> str:
        """Return the identification string of the instrument."""
        return str(self.port.query("*IDN?"))

    def reset(self) -> None:
        """Reset the instrument to its default settings."""
        self.port.write("*RST")

    def clear_status(self) -> None:
        """Clear the status registers and the error queue."""
        self.port.write("*CLS")

    def set_beeper(self, state: bool) -> None:
        """Switch the beeper on or off."""
        self.port.write(f"SYST:BEEP:STAT {'ON' if state else 'OFF'}")

    def set_display(self, state: bool) -> None:
        """Switch the front panel display on or off."""
        self.port.write(f":DISP:ENAB {'ON' if state else 'OFF'}")

    def set_function(self, function: str) -> None:
        """Set the measurement function, e.g. 'VOLT:DC'."""
        self.port.write(f':SENS:FUNC "{function}"')

    def set_temperature_unit(self, unit: str) -> None:
        """Set the temperature unit, i.e. 'C', 'K', or 'F'."""
        self.port.write(f":UNIT:TEMP {unit}")

    def set_nplc(self, function: str, nplc: float) -> None:
        """Set the integration time in number of power line cycles for the given function."""
        self.port.write(f":SENS:{function}:NPLC {nplc}")

    def set_autorange(self, function: str, state: bool) -> None:
        """Switch auto range on or off for the given function."""
        self.port.write(f":SENS:{function}:RANG:AUTO {'ON' if state else 'OFF'}")

    def set_continuous_initiation(self, state: bool) -> None:
        """Switch continuous initiation of the trigger model on or off."""
        self.port.write(f"INIT:CONT {'ON' if state else 'OFF'}")

    def read_value(self) -> float:
        """Trigger a single measurement and return the reading."""
        return float(self.port.query("READ?"))
