# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2023, 2025 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Keysight N777x Tunable Laser

from __future__ import annotations

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keysight N777x Tunable Laser Module."""

    description = """
                <h3>Driver for the Keysight N777x Tunable Laser</h3>
                <p>The driver supports wavelength and power sweeps in various units<br></p>
                <p><FONT COLOR="#ff0000"> <b>Safety Warning</b>: the user is responsible for the
                 safe operation of the laser and checking that the laser is in a safe state after
                 each SweepMe! run finishes.</p>
                <p>&nbsp;</p>
                """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "N777x"  # short name will be shown in the sequencer
        self.variables = ["Wavelength", "Power"]
        self.units = ["nm", "W"]  # will be overwritten in get_GUIparameter
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Port configuration
        self.port_manager = True
        self.port_types = ["GPIB", "USBTMC", "TCPIP"]
        self.port_properties = {
            "timeout": 10,
            "EOL": "\n",
        }

        # tracking & init
        self.wavelength = None
        self.measured_wavelength = None
        self.power_level = None
        self.measured_power = None
        self.pow_max = None
        self.pow_min = None
        self.wln_max = None
        self.wln_min = None
        self.power_conversion = 1
        self.wavelength_conversion = 1
        self.power_unit = None
        self.wavelength_unit = None
        self.sweepmode = "None"
        self.port_string = ""

        self.allowed_power_units = {
            "dBm": "DBM",  # default
            "W": "W",
            "mW": "W",  # instrument doesnt directly support mW
        }

        # conversion factors for wavelength (to get commands capitalize)
        self.wavelength_conversions = {
            "nm": 1e-9,
            "µm": 1e-6,
            "mm": 1e-3,
            "m": 1e0,
            "pm": 1e-12,
        }

    def set_GUIparameter(self) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "Power level": "0.0",  # default is 0 dBm = 1 mW
            "Power unit": list(self.allowed_power_units.keys()),
            "Wavelength": "1550.0",
            "Wavelength unit": list(self.wavelength_conversions.keys()),
            "SweepMode": ["None", "Wavelength", "Power"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweepmode: str = parameter["SweepMode"]
        self.port_string = parameter["Port"]  # auto used by port manager

        self.power_level = float(parameter["Power level"])
        self.wavelength = float(parameter["Wavelength"])
        self.power_unit = parameter["Power unit"]
        self.power_conversion = 1e-3 if self.power_unit == "mW" else 1
        self.wavelength_unit = parameter["Wavelength unit"]
        self.wavelength_conversion = self.wavelength_conversions[self.wavelength_unit]

        self.units = [self.wavelength_unit, self.power_unit]

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.reset()
        self.clear_status()
        id_ = self.get_identification()
        # print(f"N777x id: {id_}")

        self.set_power_units(self.power_unit)
        self.get_power_range()
        self.get_wavelength_range()

        if not self.check_key_turned():
            msg = "Laser key is in OFF state."
            raise ValueError(msg)

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""
        errors = self.check_errors()
        if errors:
            print("Errors for laser after measurement: ", errors)

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        if self.sweepmode != "Power":
            self.set_power(power_level=self.power_level * self.power_conversion)
        elif self.sweepmode != "Wavelength":
            self.set_wavelength(wavelength_m=self.wavelength * self.wavelength_conversion)

    def poweron(self) -> None:
        """Turn on the device when entering a sequencer branch if it was not already used in the previous branch."""
        self.set_laser_on()

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""
        self.set_laser_off()

    def apply(self) -> None:
        """This function is called if the set value has changed. Applies the new value available as self.value."""
        value = float(self.value)

        if self.sweepmode == "Wavelength":
            self.set_wavelength(value * self.wavelength_conversion)
        elif self.sweepmode == "Power":
            self.set_power(power_level=value * self.power_conversion)

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        self.measured_wavelength = self.get_wavelength()
        self.measured_power = self.get_power()

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [
            self.measured_wavelength / self.wavelength_conversion,
            self.measured_power / self.power_conversion,
        ]

    # wrapped communication commands below

    def get_identification(self) -> str:
        """Get the instrument identification string."""
        return self.port.query("*IDN?")

    def reset(self) -> None:
        """Reset the instrument to its default state."""
        self.port.write("*RST")

    def clear_status(self)-> None:
        """Clear the instrument status and error queue."""
        self.port.write("*CLS")

    def get_power(self) -> float:
        """Returns the power in W or dB."""
        return float(self.port.query("sour0:pow?"))

    def get_power_range(self) -> None:
        """Save the power range in mW as self.pow_min and self.pow_max."""
        self.pow_min = float(self.port.query(":sour0:pow? min"))
        self.pow_max = float(self.port.query(":sour0:pow? max"))

    def set_power_units(self, unit: str = "W") -> None:
        """Set the power units to W or dBm."""
        if unit.lower() not in ["w", "dbm"]:
            msg = f"Invalid power unit {unit}. Choose eiher W or DBM."
            raise ValueError(msg)
        self.port.write(f":sour0:pow:unit {unit}")

    def get_power_units(self) -> str:
        """Get the current power units."""
        return self.port.query(":sour0:pow:unit?")

    def set_power(self, power_level: float) -> None:
        """Set the power level in W or dBm."""
        if not self.pow_max >= power_level >= self.pow_min:
            msg = f"Power {power_level:.3f} out of range [{self.pow_min:.3f},{self.pow_max:.3f}] {self.power_unit}."
            raise ValueError(msg)

        self.port.write(f"sour0:pow {power_level}")
        self.power_level = power_level

    def set_wavelength(self, wavelength_m: float) -> None:
        """Set the laser wavelength m."""
        wavelength_m = float(wavelength_m)
        if not self.wln_max >= wavelength_m >= self.wln_min:
            msg = (f"Invalid wavelength {wavelength_m:.1f}m not in instrument range "
                   f"[{self.wln_min:.1f}m ,{self.wln_max:.1f}m]")
            raise ValueError(msg)

        self.port.write(f":sour0:wav {wavelength_m}")
        self.port.query("*OPC?")

        self.wavelength = wavelength_m

    def get_wavelength(self) -> float:
        """Get the laser wavelength in meters."""
        return float(self.port.query(":sour0:wav?"))

    def get_wavelength_range(self) -> tuple[float, float]:
        """Get the allowed laser wavelength range in meters."""
        self.wln_min = float(self.port.query(":sour0:wav? min"))
        self.wln_max = float(self.port.query(":sour0:wav? max"))

        return self.wln_min, self.wln_max

    def turn_key(self, onoff=0, password=1234):
        """Change the state of the laser safety key. WARNING: THIS IS A POSSIBLE SAFETY RISK!"""
        self.port.write(f":LOCK {onoff},{password}")

    def check_key_turned(self) -> bool:
        """Check if the laser safety key is turned."""
        return bool(self.port.query(":LOCK?"))

    def set_laser_on(self) -> None:
        """Switch the laser on."""
        self.port.write("SOUR0:POW:STATE 1")

    def set_laser_off(self) -> None:
        """Switch the laser off."""
        self.port.write("SOUR0:POW:STATE 0")

    def is_laser_on(self) -> bool:
        """Returns True if the laser is on, False if it is off."""
        return bool(int(self.port.query("SOUR0:POW:STATE?")))

    def check_errors(self) -> str:
        """Get error list if any and parse it based on manual."""
        err_count = int(self.port.query(":SYSTem:ERRor:COUNt?"))
        if err_count == 0:
            return ""

        errors = []
        for _ in range(err_count):
            err = self.port.query("SYST:ERR?")
            if not err.startswith("0"):
                errors.append(err)

        return ",".join(errors)
