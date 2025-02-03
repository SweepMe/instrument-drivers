# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022 SweepMe! GmbH (sweep-me.net)
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
# Type: Temperature
# Device: Lake Shore Model 33x

# Update 30 Jan, 2025: The device class was adapted to run a Lakeshore 321 (older version) by Anton Kirch (anton.kirch@umu.se).
# It worked for temperature controlling. Some properties like the heater output mode and remote PID parameter setting are not implemented.


from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """
                       make sure port options are set correctly according to instrument settings: Tools/Port manager:
                       baudrate: 1200/300
                       terminator: \r\n
                       parity: odd (O)
                   """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "Lake Shore 321"

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

        self.heater_ranges = {
            "Off": 0,
            "Low": 2,
            "High": 3,
            # "Zones": None,  # no heater range but user can specify to use Zones instead of heater range, not implemented yet
        }

    def set_GUIparameter(self):
        GUIparameter = {
            "SweepMode": ["None", "Temperature"],  # "Output in %", not implemented yet
            "TemperatureUnit": ["K", "°C"],  # "Output would use Volts additionally
            "HeaterRange": list(self.heater_ranges.keys()),
            "ZeroPowerAfterSweep": True,
            "IdleTemperature": "",
            "MeasureT": True,
            "ReachT": True,
            # "SetT": True,
            "Rate": "",
        }

        return GUIparameter

    def get_GUIparameter(self, parameter={}):
        if "HeaterRange" not in parameter:
            raise Exception(
                "Please update to the latest Temperature module to use this driver as"
                " new user interface options are needed",
            )

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

    def connect(self):
        pass

    def initialize(self):
        self.port.write("*IDN?")
        identification = self.port.read()

    def deinitialize(self):
        if self.zero_power_afterwards:
            outputmode = 0  # Off
            powerup_enable = 0
            self.set_heater_range(0)  # Off

        if self.idle_temperature != "":
            self.set_temperature(float(self.idle_temperature))

    def configure(self):
        # Output mode
        if self.sweep_mode.startswith("Temperature"):
            # Optional ramp of set temperature, default = 0 (directly set temperature)
            if self.ramprate == "":
                self.set_setpoint_ramp_parameter(0, 0.0)
            else:
                self.set_setpoint_ramp_parameter(1, self.ramprate)

        else:
            pass

        # Set temperature unit according to GUI
        if self.temperature_unit == "°C":
            self.port.write("CUNI C")

        else:
            self.port.write("CUNI K")

    def unconfigure(self):
        if self.zero_power_afterwards:
            outputmode = 0  # Off
            powerup_enable = 0
            self.set_heater_range(0)  # Off

        if self.idle_temperature != "":
            self.set_temperature(float(self.idle_temperature))

    def apply(self):
        # Set heater range if selected (0 = Off, 2 = Low, 3 = High)
        if self.heater_ranges[self.heater_range] is not None:
            self.set_heater_range(self.heater_ranges[self.heater_range])

        self.value = float(self.value)
        heater_range = self.heater_range

        if self.sweep_mode == "Temperature":
            self.value = float(self.value)
            self.set_temperature(self.value)

    def read_result(self):
        self.temperature_measured = self.get_temperature()
        self.output_power = self.get_heater_output()

    def call(self):
        return [self.temperature_measured, self.output_power]

    """ button related functions start here """

    def measure_temperature(self):
        """Used by reach functionality"""
        temperature = self.get_temperature()
        return float(temperature)

    """ setter/getter functions start here """

    def get_identification(self):
        self.port.write("*IDN?")
        return self.port.read()

    def reset(self):
        self.port.write("*RST")

    def clear(self):
        self.port.write("*CLS")

    def get_temperature(self):
        self.port.write("CDAT?")
        temperature = self.port.read()

        # this is needed as sometimes accidentally a ";" is returned
        # in this case we read the temperature again
        if temperature == ";":
            self.port.write("CDAT?")
            temperature = self.port.read()

        return float(temperature)

    def set_temperature(self, temperature):
        self.port.write("SETP %1.3f" % (float(temperature)))

    def get_temperature_setpoint(self, temperature):
        self.port.write("SETP?")
        answer = self.port.read()
        return float(answer)

    def set_manual_output(self, power):
        self.port.write("MOUT %1.2f" % (float(power)))

    def get_manual_output(self, output):
        self.port.write("MOUT?")
        answer = self.port.read()
        return float(answer)

    def get_heater_output(self):
        self.port.write("HEAT?")
        answer = self.port.read()
        return float(answer)

    def set_heater_range(self, heater_range):
        """Args:
        heater_range: range number (int)
            0 = Off, 2 = Low, 3 = High
        """
        self.port.write("RANG %i" % (int(heater_range)))

    def get_heater_range(self):
        self.port.write("RANG?")
        answer = self.port.read()
        return int(answer)

    def set_setpoint_ramp_parameter(self, ramp_enable, ramprate):
        self.port.write("RAMPR %1.2f" % float(ramprate))
        self.port.write("RAMP %i" % int(ramp_enable))

    def get_setpoint_ramp_parameter(self):
        self.port.write("RAMPR?")
        ramp_rate = self.port.read()

        self.port.write("RAMPS?")
        ramp_status = self.port.read()
        return float(ramp_status, ramp_rate)
