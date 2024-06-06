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
# * Module: Temperature
# * Instrument: Accretech UF series

from __future__ import annotations

import os

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug
from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()

# standard import
# import accretech_uf
# importlib.reload(accretech_uf)

# direct import by path
import imp

accretech_uf = imp.load_source(
    "accretech_uf_temperature",
    os.path.dirname(os.path.abspath(__file__)) + os.sep + r"libs\accretech_uf.py",
)

# this is needed as a fallback solutions as pysweepme.UserInterface is not available for all 1.5.5 update versions
try:
    from pysweepme.UserInterface import message_box
except ModuleNotFoundError:
    message_box = print
    print(
        "Accretech driver: Please use the latest version of SweepMe! to use this "
        "driver to display a message box. "
        "Fallback to 'print' method.",
    )


class Device(EmptyDevice):
    """Device class for Accretech UF series."""

    def __init__(self) -> None:
        """Initialize the device."""
        EmptyDevice.__init__(self)

        self.instance_key = None
        self.port_str = None
        self.prober: accretech_uf.AccretechProber = None
        self.temperature: float = 0.0

        self.shortname = "Accretech"
        self.variables = ["Temperature"]
        self.units = [""]
        self.plottype = [True]
        self.savetype = [True]

        self.port_manager = True
        self.port_types = ["GPIB"]
        self.port_properties = {
            "timeout": 5,  # only for write&read messages, SRQ&STB commands have own timeout
            "GPIB_EOLwrite": "\r\n",
            "GPIB_EOLread": "\r\n",
        }

        self.port_str = "undefined_port"

        self.verbosemode = True

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set initial GUI parameters."""
        return {
            "SweepMode": ["None", "Temperature"],
            "TemperatureUnit": ["°C"],
            "IdleTemperature": 30,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle SweepMe GUI parameters."""
        self.port_str = parameter["Port"]
        self.units[0] = parameter["TemperatureUnit"]
        self.idle_temperature = parameter["IdleTemperature"]

    def connect(self) -> None:
        """Connect to the device and handle multiple instances."""

        # creating an AccretechProber instance that handles all communication
        self.prober = accretech_uf.AccretechProber(self.port)
        self.prober.set_verbose(self.verbosemode)

        # This identifier must be equal with the identifier used by the WaferProber_Accretech_UFseries driver
        self.unique_identifier = "Driver_Accretech_UFseries_" + self.port_str
        if self.unique_identifier not in self.device_communication:
            self.device_communication[self.unique_identifier] = None

    def disconnect(self) -> None:
        """Disconnect from the device."""
        if self.unique_identifier in self.device_communication:
            self.prober.unregister_srq_event()  # this makes sure the event mechanism is disabled
            del self.device_communication[self.unique_identifier]
        del self.prober  

    def initialize(self) -> None:
        """Initialize the device."""
        self.prober.reset_alarm()

    def deinitialize(self):
        pass

    def unconfigure(self):
        if self.idle_temperature != "":
            _, target_temperature = self.prober.request_chuck_temperature()
            if target_temperature != float(self.idle_temperature):
                self.prober.set_chuck_temperature(float(self.idle_temperature))
            else:
                debug("Idle temperature already set.")
        
    def apply(self) -> None:
        """Apply the given temperature."""
        _, target_temperature = self.prober.request_chuck_temperature()
        if target_temperature != float(self.value):
            self.prober.set_chuck_temperature(self.value)
        else:
            debug("Target temperature already set.")

    def measure(self) -> None:
        """Measure the temperature."""
        # TODO: chuck_temperature or hot_chuck_temperature?
        self.temperature, target_temperature = self.prober.request_chuck_temperature()

    def call(self) -> list[float]:
        """Return measured temperature to SweepMe GUI."""
        return [self.temperature]

    """ Convenience functions. """

    def measure_temperature(self) -> float:
        """Measure the temperature."""
        _temperature, _target_temperature = self.prober.request_chuck_temperature()
        return _temperature
