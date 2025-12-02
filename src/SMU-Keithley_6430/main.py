# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025 SweepMe! GmbH (sweep-me.net)
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
#
# SweepMe! driver
# * Module: SMU
# * Instrument: Keithley 6430

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keithley 6430."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "6430"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["GPIB", "COM", "TCPIP"]

        # Measurement parameters
        self.channel: int = 1

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "Channel": [1, 2, 3],
            "SweepMode": ["None", "Voltage in V", "Current in A"],
            "Compliance": 0.0,
            "Range": ["AUTO", "MIN", "MAX"],
            "RangeVoltage": ["AUTO", "MIN", "MAX"],
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")
        self.channel = parameters.get("Channel", 1)

        self.sweep_mode = parameters.get("SweepMode", "")
        self.measure_function = parameters.get("MeasureFunction", "")
        self.compliance = parameters.get("Compliance", 0.0)
        self.range = parameters.get("Range", "")

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # set compliance, range and speed
        if self.sweep_mode.startswith("Voltage"):
            self.set_compliance_current(self.compliance)
        elif self.sweep_mode.startswith("Current"):
            self.set_compliance_voltage(self.compliance)

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        self.output_off()

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.sweep_mode.startswith("Voltage"):
            self.set_voltage(self.value)
        elif self.sweep_mode.startswith("Current"):
            self.set_current(self.value)

    def call(self) -> list:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.voltage, self.current]
    
    # Wrapped Functions

    def output_on(self) -> None:
        """Turn the instrument output on (:OUTPut:STATe ON)."""
        self.port.write(":OUTPut:STATe ON")

    def output_off(self) -> None:
        """Turn the instrument output off (:OUTPut:STATe OFF)."""
        self.port.write(":OUTPut:STATe OFF")

    def set_output(self, enable: bool) -> None:
        """Convenience wrapper to set output ON/OFF."""
        self.port.write(f":OUTPut:STATe {'ON' if enable else 'OFF'}")

    # Sourcing
    def set_voltage(self, value: float) -> None:
        """Set source voltage level (V-Source). Uses SOURce:VOLTage:LEVel."""
        self.port.write(f":SOURce:VOLTage:LEVel {value}")

    def set_current(self, value: float) -> None:
        """Set source current level (I-Source). Uses SOURce:CURRent:LEVel."""
        self.port.write(f":SOURce:CURRent:LEVel {value}")

    def set_compliance_voltage(self, v_limit: float) -> None:
        """When sourcing current, set voltage compliance (SOURce:VOLTage:LEVel:PROTection or SENSe:VOLT:PROT?).
        Using SENSe:VOLTage:PROTection is common for SCPI-capable SourceMeters.
        """
        # Many Keithley instruments use :SOURce:VOLTage:LEVel and :SENSe:VOLTage:PROTection; try the SENSe form first.
        self.port.write(f":SENSe:VOLTage:PROTection {v_limit}")

    def set_compliance_current(self, i_limit: float) -> None:
        """When sourcing voltage, set current compliance (SOURce:CURRent:LEVel:PROTection or SENSe:CURR:PROT?)."""
        self.port.write(f":SENSe:CURRent:PROTection {i_limit}")

    # Measurement wrappers
    def measure_voltage(self) -> float:
        """Measure DC voltage using :MEASure:VOLTage?"""
        resp = self.query_raw(":MEASure:VOLTage:DC?")
        return float(resp)

    def measure_current(self) -> float:
        """Measure DC current using :MEASure:CURRent?"""
        resp = self.query_raw(":MEASure:CURRent:DC?")
        return float(resp)

    def measure_resistance(self) -> float:
        """Measure resistance using :MEASure:RESistance?"""
        resp = self.query_raw(":MEASure:RESistance?")
        return float(resp)

    def read_measurement(self) -> float:
        """
        Use :READ? to trigger a source/measure and return numeric value.
        :READ? typically returns a comma-separated list (value, unit, status...).
        Here we read the first numeric value from the response.
        """
        raw = self.query_raw(":READ?")
        # parse the first token that looks like a float
        for token in raw.replace(",", " ").split():
            try:
                return float(token)
            except Exception:
                continue
        # couldn't parse numeric value; raise error
        raise RuntimeError(f"Could not parse numeric measurement from response: '{raw}'")
