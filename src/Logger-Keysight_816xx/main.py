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
# * Module: Logger
# * Instrument: Keysight 816xx Lightwave Multimeter/Measurement System/Multichannel System

from __future__ import annotations

import time

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keysight 816xx Lightwave system."""

    description = """
    <h3>Keysight 816xx-Lightwave Multimeter/Measurement System/Multichannel System</h3>
    This driver supports the 8163A/B Lightwave Multimeter, 8164A/B Lightwave Measurement System, & 8166A/B Lightwave 
    Multichannel System
    <h4>Parameters</h4>
    <ul>
    <li>Channel: If your power meter supports multiple channels. Otherwise, choose 1.</li>
    <li>Slot: Choose the slot your powermeter is connected to.</li>
    <li>Wavelength: If no wavelength should be set, set to 0.</li>
    </ul>
    """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "816xx"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Power"]
        self.units = ["W"]
        self.plottype = [True]
        self.savetype = [True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["GPIB"]
        # self.port_properties = {
        #     "timeout": 20,
        #     "baudrate": 9600,
        #     "stopbits": 1,
        #     "parity": "N",
        #     "EOL": "\n",
        # }

        # Measurement parameters
        self.slot: str = "1"  # Slot number of the power meter
        self.channel: str = "1"  # In case the connected power meter has multiple channels
        self.averaging_time: str = "0.1"  # in seconds
        self.power_units = ["W", "dBm"]
        self.power_unit: str = "W"  # can be "W" or "dBm"
        self.automatic_power_ranging: bool = True  # Enable automatic power ranging
        self.wavelength: str = "1550"

    def update_gui_parameters(self, parameters: dict) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        del parameters  # no dynamic parameters needed
        return {
            "Channel": "1",
            "Slot": "1",
            "Power unit": self.power_units,
            "Automatic Power Ranging": True,
            "Averaging in s": 0.1,
            "Wavelength in nm": 1550,  # Default wavelength, can be changed later
        }

    def apply_gui_parameters(self, parameters: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")
        self.channel = parameters.get("Channel", "1")
        self.slot = parameters.get("Slot", "1")

        self.power_unit = parameters.get("Power unit", "W")
        self.units = [self.power_unit]

        self.automatic_power_ranging = parameters.get("Automatic Power Ranging", True)
        self.averaging_time = parameters.get("Averaging in s", "0.1")
        self.wavelength = parameters.get("Wavelength in nm", "1550")

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        print("ID:", self.port.query("*IDN?"))

        self.set_power_unit(self.power_unit)
        self.set_averaging_time(float(self.averaging_time))
        self.set_automatic_power_ranging(True)  # Enable automatic power ranging
        self.set_wavelength(float(self.wavelength))

        # TODO: Decide if additional methods are needed: Upper power limit, reference state

    def call(self) -> float:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return self.get_power()

    # Wrapper Functions

    def set_averaging_time(self, averaging_time: float) -> None:
        """Set the averaging time for the power measurement."""
        self.port.write(f"sens{self.slot}:chan{self.channel}:pow:atim {averaging_time}")
        self.wait_for_opc()

    def set_automatic_power_ranging(self, enable: bool = True) -> None:
        """Enable or disable automatic power ranging.

        Can only be set for both channels at the same time.
        """
        if enable:
            self.port.write(f"sens{self.slot}:pow:rang:auto on")
        else:
            self.port.write(f"sens{self.slot}:pow:rang:auto off")
        self.wait_for_opc()

    def set_power_unit(self, unit: str) -> None:
        """Set the power unit to either W or dBm."""
        if unit.lower() not in ["w", "dbm"]:
            msg = "Unit must be 'W' or 'dBm'."
            raise ValueError(msg)
        self.port.write(f"sens{self.slot}:chan{self.channel}:pow:unit {unit.upper()}")
        self.wait_for_opc()

    def set_wavelength(self, wavelength_nm: float) -> None:
        """Sets the sensor wavelength.

        Frequent use of this command can conflict with the timing of autoranging in some configurations.
        Auto range can be disabled before and enabled after the command if needed.
        The changes are applied to all channels
        """
        if wavelength_nm == 0:
            return

        if wavelength_nm < 0:
            msg = f"Invalid wavelength: {wavelength_nm}"
            raise ValueError(msg)
        self.port.write(f"sens{self.slot}:pow:wav {wavelength_nm}nm")
        self.wait_for_opc()

    def get_power(self) -> float:
        """Get the current power measurement."""
        response = self.port.query(f"sens{self.slot}:chan{self.channel}:pow:val?")
        return float(response.strip())

    def wait_for_opc(self, timeout_s: float = 10.0) -> None:
        """Wait for the operation complete (OPC) bit to be set."""
        start_time = time.time()
        while time.time() - start_time < timeout_s:
            status = self.port.query("*OPC?")
            if status.strip() == "1":
                break

    # Currently unused wrapper functions

    def get_averaging_time(self) -> float:
        """Get the current averaging time for the power measurement."""
        response = self.port.query(f"sens{self.slot}:chan{self.channel}:pow:atim?")
        return float(response.strip())

    def get_wavelength(self) -> float:
        """Get the current wavelength setting of the power meter."""
        response = self.port.query(f"sens{self.slot}:chan{self.channel}:pow:wav?")
        return float(response.strip())


