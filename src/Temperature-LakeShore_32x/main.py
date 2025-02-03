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

# SweepMe! device class
# * Type: Temperature
# * Instrument: Lake Shore Model 33x

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class to implement functionalities of a Lake Shore Model 33x temperature controller."""
    description = """
                       make sure port options are set correctly according to instrument settings: Tools/Port manager:
                       baudrate: 1200/300
                       terminator: \r\n
                       parity: odd (O)

                       Some properties like the heater output mode and remote PID parameter setting are not implemented.
                   """

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Lake Shore 32x"

        self.port_manager = True
        self.port_types = ["COM"]

        self.port_properties = {
            "timeout": 5,
            "EOL": "\r\n",
            "baudrate": 1200,
            "bytesize": 7,
            "stopbits": 1,
            "parity": "O",
            "delay": 0.5,  # needed to avoid problems with reading temperature
        }

        # Instrument Parameters
        self.heater_ranges = {
            "Off": 0,
            "Low": 2,
            "High": 3,
            # "Zones": None,  # no heater range but user can specify to use Zones instead of heater range, not implemented yet
        }

        # Measurement Parameters
        self.sweep_mode: str = "None"
        self.measureT: bool = True
        self.reachT: bool = True
        self.temperature_unit: str = "K"
        self.ramprate: str = ""
        self.heater_range: str = "Off"
        self.zero_power_afterwards: bool = True
        self.idle_temperature: str = ""

        self.temperature_measured: float = 0
        self.output_power: float = 0

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set initial GUI parameter in SweepMe!."""
        return {
            "SweepMode": ["None", "Temperature"],  # "Output in %", not implemented yet
            "TemperatureUnit": ["K", "°C"],  # "Output would use Volts additionally
            "HeaterRange": list(self.heater_ranges.keys()),
            "ZeroPowerAfterSweep": True,
            "IdleTemperature": "",
            "MeasureT": True,
            "ReachT": True,
            "Rate": "",
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Update parameter from SweepMe! GUI."""
        if "HeaterRange" not in parameter:
            msg = (
                "Please update to the latest Temperature module to use this driver as"
                " new user interface options are needed"
            )
            raise Exception(msg)

        self.measureT = parameter["MeasureT"]
        self.reachT = parameter["ReachT"]

        self.sweep_mode = parameter["SweepMode"]

        self.temperature_unit = parameter["TemperatureUnit"]
        self.ramprate = parameter["Rate"]
        self.heater_range = parameter["HeaterRange"]

        self.zero_power_afterwards = parameter["ZeroPowerAfterSweep"]
        self.idle_temperature = parameter["IdleTemperature"]

        self.variables = ["Temperature", "Power"]
        self.units = [self.temperature_unit, "%"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

    """ semantic standard functions start here """

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.get_identification()

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""
        if self.zero_power_afterwards:
            self.set_heater_range(0)  # Off

        if self.idle_temperature != "":
            self.set_temperature(float(self.idle_temperature))

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # Output mode
        if self.sweep_mode.startswith("Temperature"):
            # Optional ramp of set temperature, default = 0 (directly set temperature)
            if self.ramprate == "":
                self.set_setpoint_ramp_parameter(0, 0.0)
            else:
                self.set_setpoint_ramp_parameter(1, float(self.ramprate))

        # Set temperature unit according to GUI
        if self.temperature_unit == "°C":
            self.port.write("CUNI C")
        else:
            self.port.write("CUNI K")

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        if self.zero_power_afterwards:
            self.set_heater_range(0)  # Off

        if self.idle_temperature != "":
            self.set_temperature(float(self.idle_temperature))

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        # Set heater range if selected (0 = Off, 2 = Low, 3 = High)
        if self.heater_ranges[self.heater_range] is not None:
            self.set_heater_range(self.heater_ranges[self.heater_range])

        if self.sweep_mode == "Temperature":
            self.value = float(self.value)
            self.set_temperature(self.value)

    def read_result(self) -> None:
        """Read the measured data from a buffer."""
        self.temperature_measured = self.get_temperature()
        self.output_power = self.get_heater_output()

    def call(self) -> [float, float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.temperature_measured, self.output_power]

    """ button related functions start here """

    def measure_temperature(self) -> float:
        """Used by reach functionality."""
        temperature = self.get_temperature()
        return float(temperature)

    """ setter/getter functions start here """

    def get_identification(self) -> str:
        """Get the identification of the device."""
        self.port.write("*IDN?")
        return self.port.read()

    def reset(self) -> None:
        """Reset the device."""
        self.port.write("*RST")

    def clear(self) -> None:
        """Clear the device."""
        self.port.write("*CLS")

    def get_temperature(self) -> float:
        """Get the temperature of the device."""
        self.port.write("CDAT?")
        temperature = self.port.read()

        # this is needed as sometimes accidentally a ";" is returned
        # in this case we read the temperature again
        if temperature == ";":
            self.port.write("CDAT?")
            temperature = self.port.read()

        return float(temperature)

    def set_temperature(self, temperature: float) -> None:
        """Set the temperature of the device."""
        self.port.write("SETP %1.3f" % (float(temperature)))

    def get_temperature_setpoint(self) -> float:
        """Get the setpoint temperature of the device."""
        self.port.write("SETP?")
        answer = self.port.read()
        return float(answer)

    def set_manual_output(self, power: float) -> None:
        """Set the manual output of the device."""
        self.port.write("MOUT %1.2f" % (float(power)))

    def get_manual_output(self) -> float:
        """Get the manual output of the device."""
        self.port.write("MOUT?")
        answer = self.port.read()
        return float(answer)

    def get_heater_output(self) -> float:
        """Get the heater output of the device."""
        self.port.write("HEAT?")
        answer = self.port.read()
        return float(answer)

    def set_heater_range(self, heater_range: int) -> None:
        """Set the heater range.

        Args:
        heater_range: range number (int)
            0 = Off, 2 = Low, 3 = High
        """
        self.port.write("RANG %i" % (int(heater_range)))

    def get_heater_range(self) -> int:
        """Get the heater range of the device as int: 0 = Off, 2 = Low, 3 = High."""
        self.port.write("RANG?")
        answer = self.port.read()
        return int(answer)

    def set_setpoint_ramp_parameter(self, ramp_enable: int, ramprate: float) -> None:
        """Set the ramprate and enable ramping."""
        self.port.write("RAMPR %1.2f" % float(ramprate))
        self.port.write("RAMP %i" % int(ramp_enable))

    def get_setpoint_ramp_parameter(self) -> [int, float]:
        """Get the ramprate and ramp status."""
        self.port.write("RAMPR?")
        ramp_rate = self.port.read()

        self.port.write("RAMPS?")
        ramp_status = self.port.read()
        return int(ramp_status), float(ramp_rate)
