# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022-2023 SweepMe! GmbH (sweep-me.net)
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
# Type: SMU
# Device: Rohde&Schwarz NGx

import time

from pysweepme.ErrorMessage import error
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """
    <p><strong>Usage:</strong></p>
    <ul>
    <li>The default channel is 1. The rear terminal also works with this channel. 
    Do not change it unless you need it.</li>
    <li>The USB protocol needs to be set to TMC manually from the front panel. 
    The setting can be found under "USB Class" from the "Network Connections" dialog.</li>
    <li>To use '4-wire' just include the Sense connectors of the instrument into your circuit and 
    it will automatically change to 4-wire mode.</li>
    </ul> 
    """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "NGx"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["COM", "USBTMC", "GPIB", "TCPIP"]

        self.port_properties = {"timeout": 1,
                                # "delay": 0.05,
                                # "Exception": False,
                                }

    #       self.commands = {
    #                      "Voltage in V" : "VOLT",
    #                      "Current in A" : "CURR",
    #                      }

    def set_GUIparameter(self):

        gui_parameter = {
            "SweepMode": ["Voltage in V", "Voltage in V (with wait)", "Current in A", "Current in A (with wait)"],
            "Channel": [1, 2],
            "RouteOut": ["Front"],
            "Compliance": 5.0,
            "Range": ["Auto", "10 µA", "1 mA", "10 mA", "100 mA", "3 A", "10 A"],
            "RangeVoltage": ["Auto", "20 V", "6 V"],
            "Speed": ["Fast", "Medium", "Slow"],
            # "4wire": False,
        }

        return gui_parameter

    def get_GUIparameter(self, parameter={}):
        self.port_string = parameter["Port"]
        self.source = parameter["SweepMode"]
        self.protection = parameter["Compliance"]
        self.channel = int(parameter["Channel"])
        self.current_range = parameter["Range"]
        self.voltage_range = parameter["RangeVoltage"]
        self.speed = parameter["Speed"]

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):
        if self.port_string.startswith("TCPIP"):
            if self.port_string.endswith("SOCKET"):
                self.port.port.write_termination = '\n'
                self.port.port.read_termination = '\n'

    def initialize(self):
        # identifier = self.get_identification()
        # print("Identifier:", identifier)  # can be used to check the instrument
        self.reset_instrument()

    def configure(self):
        self.set_voltage_range(self.voltage_range)
        self.set_current_range(self.current_range)
        self.set_channel(self.channel)
        if self.source.startswith("Voltage"):
            self.set_current_limit(self.protection)
            self.set_voltage(0.0)
            self.set_current(self.protection)
        elif self.source.startswith("Current"):
            self.set_voltage_limit(self.protection)
            self.set_current(0.0)
            self.set_voltage(self.protection)
        if self.speed == "Fast":
            self.set_nplc(0.1)
        if self.speed == "Medium":
            self.set_nplc(1)
        if self.speed == "Slow":
            self.set_nplc(10)

    def unconfigure(self):

        if self.source.startswith("Voltage"):
            self.set_voltage(0.0)
        elif self.source.startswith("Current"):
            self.set_current(0.0)

        self.unlock_local_interface()

    def deinitialize(self):
        pass

    def poweron(self):
        self.set_channel(self.channel)
        self.set_output_on()
        self.set_generation_on()

    def poweroff(self):
        self.set_channel(self.channel)
        self.set_generation_off()
        self.set_output_off()

    def apply(self):
        self.set_channel(self.channel)
        if self.source.startswith("Voltage"):
            self.set_voltage(self.value)

        elif self.source.startswith("Current"):
            self.set_current(self.value)

        # wait for achieving the set voltage or set current before
        # other channels are changed
        if "(with wait)" in self.source:
            time.sleep(0.5)

    def measure(self):
        self.set_channel(self.channel)
        self.v, self.i = self.read_data()
        # print(self.v, self.i)

    def call(self):
        return [self.v, self.i]

    """ here, convenience functions start """

    def get_identification(self):
        """
        This function return the identification number of the instrument, with the following format:
        Rohde&Schwarz,<device type>,<part number>/<serial number>,<firmware version>
        Returns:
            str: identification number
        """
        self.port.write("*IDN?")
        answer = self.port.read()
        return answer

    def get_options(self):
        """
        This function returns the options included in the instrument.
        Returns:
            str: option number
        """
        self.port.write("*OPT?")
        answer = self.port.read()
        return answer

    def reset_instrument(self):
        """
        This function resets the device to its default settings.
        Returns:
            None
        """
        self.port.write("*RST")

    def set_voltage_limit(self, protection):
        """
        This function turns on the safety limits of the instrument and sets a high threshold for the voltage. Note that
        a lower threshold is also available with these instruments.
        Args:
            protection: float or str
        Returns:
            None
        """
        self.port.write("ALIM 1")  # To make sure that the safety limits are on beforehand.
        self.port.write("VOLT:ALIM %1.3f" % float(protection))

    def get_voltage_limit(self):
        """
        This function gets the voltage limit of the instrument.
        Returns:
            float: answer
        """
        self.port.write("VOLT:ALIM?")
        answer = self.port.read()
        return answer

    def set_current_limit(self, protection):
        """
        This function turns on the safety limits of the instrument and sets a high threshold for the current. Note that
        a lower threshold is also available with this instrument.
        Args:
            protection: float ot str
        Returns:
            None
        """
        self.port.write("ALIM 1")
        self.port.write("CURR:ALIM %1.4f" % float(protection))

    def get_current_limit(self):
        """
        This function gets the current limit of the instrument.
        Returns:
            float: answer
        """
        self.port.write("CURR:ALIM?")
        answer = self.port.read()
        return answer

    def set_channel(self, channel):
        """
        This function selects a channel as the active channel of the instrument. Then the channel does not need to be
        specified anymore with other commands.
        Args:
            channel: int

        Returns:
            None
        """
        self.port.write("INST:OUT%i" % int(channel))

    def set_voltage(self, voltage):
        """
        This function sets a voltage to a selected output channel. The output then needs to be turned on.
        Args:
            voltage: float or str

        Returns:
            None
        """
        self.port.write("VOLT %1.3f" % float(voltage))

    def get_voltage(self):
        """
        This function measures the voltage difference of the terminals for a selected channel.
        Returns:
            float: voltage
        """
        self.port.write("MEAS:VOLT?")
        answer = float(self.port.read())
        return answer

    def set_current(self, current):
        """
        This function sets a current to a selected output channel. The output then needs to be turned on.
        Args:
            current: float or str

        Returns:
            None
        """
        self.port.write("CURR %1.4f" % float(current))

    def get_current(self):
        """
        This function measures the current through the terminals for a selected channel.
        Returns:
            float: current
        """
        self.port.write("MEAS:CURR?")
        answer = float(self.port.read())
        return answer

    def set_output_on(self):
        """
        This function switches the currently selected output on.
        Returns:
            None
        """
        self.port.write("OUTP:SEL 1")

    def set_output_off(self):
        """
        This function switches the currently selected output off.
        Returns:
            None
        """
        self.port.write("OUTP:SEL 0")

    def set_generation_on(self):
        """
        This function starts to generate the signal for the currently selected output.
        Returns:
            None
        """
        self.port.write("OUTP:GEN 1")

    def set_generation_off(self):
        """
        This function stops to generate the signal for the currently selected output.
        Returns:
            None
        """
        self.port.write("OUTP:GEN 0")

    def unlock_local_interface(self):
        """
        This function unlocks the front panel of the instrument, which has been locked with sending the first remote
        command.
        Returns:
            None
        """
        self.port.write("SYST:LOCal")

    def read_data(self):
        """
        This function reads both voltage and current simultaneously.
        Returns:
            float: voltage
            float: current
        """
        self.port.write("READ?")
        voltage, current = self.port.read().split(",")
        return float(voltage), float(current)

    def set_voltage_range(self, voltage_range):
        """
        This function sets the voltage measurement range of the instrument. Available ranges are:
        "20 V", "6 V", and "Auto".
        Args:
            voltage_range

        Returns:
            None
        """
        if voltage_range == "20 V":
            self.port.write("SENS:VOLT:RANG 20")
        elif voltage_range == "6 V":
            self.port.write("SENS:VOLT:RANG 6")
        elif voltage_range == "Auto":
            self.port.write("SENS:VOLT:RANG:AUTO 1")
        else:
            raise Exception("The input voltage range is not valid.")

    def set_current_range(self, current_range):
        """
        This function sets the current measurement range of the instrument. Available ranges are:
        "10 A", "3 A", "100 mA", "10 mA", "1 mA", "10 µA", and "Auto".
        Args:
            current_range

        Returns:
            None
        """
        if current_range == "10 A":
            self.port.write("SENS:CURR:RANG 10")
        elif current_range == "3 A":
            self.port.write("SENS:CURR:RANG 3")
        elif current_range == "100 mA":
            self.port.write("SENS:CURR:RANG 0.1")
        elif current_range == "10 mA":
            self.port.write("SENS:CURR:RANG 0.01")
        elif current_range == "1 mA":
            self.port.write("SENS:CURR:RANG 0.001")
        elif current_range == "10 µA":
            self.port.write("SENS:CURR:RANG 0.0001")
        elif current_range == "Auto":
            self.port.write("SENS:CURR:RANG:AUTO 1")
        else:
            raise Exception("The input current range is not valid.")

    def set_nplc(self, nplc):
        """
        This function sets the number of power line cycles value. high NPLC means slow integration/speed and vice versa.
        Args:
            nplc
        Returns:
            None
        """
        self.port.write("NPLC %0.1f" % nplc)


if __name__ == "__main__":

    ngx = Device()
    print("Driver instance:", ngx)
    print("Options:", ngx.get_options())
    print("Identifier:", ngx.get_identification())
