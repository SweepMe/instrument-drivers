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
# * Module: Switch
# * Instrument: Keysight 8160xx

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keysight 8160xx Laser module."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "8160xx"  # short name will be shown in the sequencer

        # No measured variables - laser is a source
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["GPIB"]

        # Measurement parameters
        self.channel: int = 1

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "SweepMode": ["None", "Wavelength", "Power"],
            "Slot": 0,  # TLS module slot number
            # "Output Path": [1, 2],  # 1 = low power/high sens, 2 = high power
            "Wavelength in nm": 1550.0,
            "Power unit": ["dBm", "W"],
            "Power": 0.0,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")
        self.channel = parameters.get("Channel", 1)

        self.slot = parameters.get("Slot", "")
        # self.output_path = parameters.get("Output Path", "")
        self.wavelength = parameters.get("Wavelength in nm", "")
        self.power = parameters.get("Power", "")
        self.power_unit = parameters.get("Power unit", "dBm")
        self.sweep_mode = parameters.get("SweepMode", "")

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        idn = self.port.query("*IDN?")
        print(f"Connected to: {idn.strip()}")

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""

    def poweron(self) -> None:
        """Turn on the power."""
        self.turn_on()

    def poweroff(self) -> None:
        """Turn off the power."""
        self.turn_off()

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # Reset / Preset
        self.port.write("*CLS")
        self.port.write(":SYSTem:PRESet")

        self.set_wavelength(float(self.wavelength))

        # Configure output
        # self.port.write(f"OUTPut{self.slot}:PATH {self.output_path}")
        self.set_power_unit(self.power_unit)
        self.set_power(float(self.power))

        # # Sweep settings if enabled
        # if self.sweep_mode == "Continuous":
        #     self.port.write("WAVelength:SWEep:MODE CONTinuous")
        #     self.port.write(f"WAVelength:SWEep:SPEed {self.sweep_speed}NM/S")
        #     self.port.write(f"WAVelength:SWEep:STARt {self.sweep_start}NM")
        #     self.port.write(f"WAVelength:SWEep:STOP {self.sweep_stop}NM")
        #     self.port.write(f"WAVelength:SWEep:STEP:WIDTh {self.sweep_step}NM")
        # elif self.sweep_mode == "Step":
        #     self.port.write("WAVelength:SWEep:MODE STEP")
        #     self.port.write(f"WAVelength:SWEep:STARt {self.sweep_start}NM")
        #     self.port.write(f"WAVelength:SWEep:STOP {self.sweep_stop}NM")
        #     self.port.write(f"WAVelength:SWEep:STEP:WIDTh {self.sweep_step}NM")

        # Output ON/OFF
        # self.port.write(f"OUTPut{self.slot}:STATe {self.output_state}")

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        self.port.write(f"SOURce{self.slot}:WAVelength {self.value}NM")
        if self.sweep_mode.startswith("Wavelength"):
            self.set_wavelength(float(self.value))
        elif self.sweep_mode.startswith("Power"):
            self.set_power(float(self.value))

    # --- Helper functions ---
    def set_wavelength(self, wavelength_nm: float) -> None:
        """Set the wavelength in nm."""
        self.port.write(f"SOURce{self.slot}:WAVelength {wavelength_nm}NM")

    def get_wavelength(self) -> float:
        """Get the current wavelength in nm."""
        return float(self.port.query(f"SOURce{self.slot}:WAVelength?")) * 1e9

    def set_power(self, power_dbm: float) -> None:
        """Set the power in dBm."""
        self.port.write(f"SOURce{self.slot}:POWer:LEVel:IMMediate:AMPLitude {power_dbm}")

    def get_power(self) -> float:
        """Get the current power in dBm."""
        return float(self.port.query(f"SOURce{self.slot}:POWer:LEVel:IMMediate:AMPLitude?"))

    def set_power_unit(self, unit: str = "DBM") -> None:
        """Set the laser power unit. Options: 'DBM' or 'W'."""
        if unit.upper() not in ["DBM", "W"]:
            msg = f"Invalid power unit '{unit}'. Use 'DBM' or 'W'."
            raise ValueError(msg)
        self.port.write(f"SOURce{self.slot}:POWer:UNIT {unit}")

    def turn_on(self) -> None:
        """Turn laser output ON."""
        self.port.write(f"OUTPut{self.slot}:STATe 1")

    def turn_off(self) -> None:
        """Turn laser output OFF."""
        self.port.write(f"OUTPut{self.slot}:STATe 0")

    def is_sweeping(self) -> bool:
        """Check if a wavelength sweep is active."""
        state = self.port.query(f"SOURce{self.slot}:WAV:SWEep:STATe?")
        return state.strip() != "0"

