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


# SweepMe! device class
# Device: Arduino MCP4728


from pysweepme import EmptyDevice


class Device(EmptyDevice):
    description = """
                        <h3>MCP4728</h3>
                        <p>0x60 is standard. I2C Address is given either as 0-7 (HEX) or 0x60-0x67 (DEC)</p>
                        If uncertain, you can use I2C scanner with arduino to check your I2C address
                        Voltage Reference: Use either internal 2V, which can be amplified to internal 4V
                        When using external reference voltage, set it
                        Multi Channel Use: Parameter need to be set as string devided by ":"
                        Multi Board use: only works with multi channel. Give list of number of boards * 4 inputs
                        """

    def __init__(self) -> None:
        EmptyDevice.__init__(self)

        self.shortname = "Arduino MCP4728"
        self.variables = []
        self.units = []

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "EOL": "\n",
            "timeout": 15,
            "baudrate": 115200,
        }

        self.multi_pins = False
        self.multi_mcp = False
        self.max_voltage = None

        self.unit = {
            "Voltage in V": "V",
            "Output in %": "%",
        }

    def set_GUIparameter(self):
        return {
            "Channel": ["0", "1", "2", "3", "all"],
            "I2C Address": "0",
            "SweepMode": ["Voltage in V", "Output in %"],
            "Voltage reference": ["External", "Internal 2.048 V", "Internal 4.096 V"],
            "External voltage in V": 5.0,
        }

    def get_GUIparameter(self, parameter={}):
        channel = parameter["Channel"]
        if channel == "all":
            self.multi_pins = True
        else:
            self.pin = int(channel)
            self.variables.append(f"Channel{self.pin}")
            self.units.append("V")

        address_list = parameter["I2C Address"].split(",")
        if len(address_list) == 1:
            self.address = int(parameter["I2C Address"])
        else:
            self.address = []
            for addr in address_list:
                self.address.append(int(addr))
            self.multi_mcp = True

        self.sweepmode = str(parameter["SweepMode"])

        self.reference_voltage = str(parameter["Voltage reference"])
        if self.reference_voltage == "External":
            self.external_voltage = float(parameter["External voltage in V"])

        # Set variables and units
        if channel == "all" and self.multi_mcp:
            channel_num = len(self.address) * 4
        elif channel == "all" and not self.multi_mcp:
            channel_num = 4
        else:
            channel_num = 1

        for n in range(channel_num):
            # If single channel, use the correct pin number
            if channel_num == 1:
                n = self.pin
            self.variables.append(f"Channel{n}")
            self.units.append(self.unit[self.sweepmode])

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):
        # Set Name/Number of COM Port as key
        instance_key = f"mcp4728_{self.port.port.port}"

        if instance_key in self.device_communication:
            pass
        else:
            # Check for Ready
            self.port.read()
            self.device_communication[instance_key] = "Connected"

    def initialize(self):
        pass

    def deinitialize(self):
        pass

    def configure(self):
        # Initialize MCP4728 with given I2C address
        if not self.multi_mcp:
            self.set_address(self.address)

        # Set Reference Voltage and Gain
        if self.reference_voltage == "Internal 2.048 V":
            self.set_vref(use_internal_vref=True)
            self.set_gain(1)
            self.max_voltage = 2.048
        elif self.reference_voltage == "Internal 4.096 V":
            self.set_vref(use_internal_vref=True)
            self.set_gain(2)
            self.max_voltage = 4.096
        elif self.reference_voltage == "External":
            self.set_vref(use_internal_vref=False)
            self.max_voltage = self.external_voltage

    def apply(self):
        if self.multi_pins:
            # Receive values as list, split by ":"
            value_list = self.value.split(":")

            # Adjust number of channels depending on number of boards and pins
            number_of_channels = 4 * len(self.address) if self.multi_mcp else 4

            if len(value_list) != number_of_channels:
                msg = f"Incorrect number of voltages received. Expected {number_of_channels}, got {len(value_list)}"
                raise Exception(msg)

            for n, value in enumerate(value_list):
                # Convert individual values to 12 Bit and set voltages
                if self.sweepmode == "Output in %":
                    volt_bit = self.voltage_to_12bit(float(value), relative_voltage=True)
                else:
                    volt_bit = self.voltage_to_12bit(float(value))

                # If number of pin is higher than 3, change address to next board
                pin = n % 4
                print(n, pin)
                if pin == 0:
                    mcp_num = int(n / 4)
                    self.set_address(self.address[mcp_num])

                self.set_voltage(pin, volt_bit)

        else:
            # set voltage for single pin

            try:
                volt = float(self.value)
            except ValueError as e:
                msg = "Single Channel Mode activated. Expects float or int from self.value"
                raise ImportError(msg) from e

            if self.sweepmode == "Output in %":
                volt_bit = self.voltage_to_12bit(volt, relative_voltage=True)
            else:
                volt_bit = self.voltage_to_12bit(volt)

            self.set_voltage(self.pin, volt_bit)

    def reach(self):
        pass

    def measure(self):
        pass

    def call(self):
        return self.value if self.multi_pins else [self.value]

    """ here, convenience functions start """

    def voltage_to_12bit(self, voltage, relative_voltage=False):
        voltage_bit = int(voltage / 100 * 4095) if relative_voltage else int(4095 / self.max_voltage * voltage)

        if not 0 <= voltage_bit < 4096:
            msg = f"Voltage {voltage} out of bound. Either larger than max voltage or negative."
            raise ValueError(msg)

        return voltage_bit

    def set_voltage(self, channel, bit_value):
        command_string = f"CH{channel}={bit_value}"

        self.port.write(command_string)
        ret = self.port.read()
        if ret == f"ACK{channel}={bit_value}":
            pass
        elif ret[:3] == "NAK":
            msg = f"Failed to set voltage at channel {channel}"
            raise Exception(msg)

    def set_address(self, address: int):
        # TODO: Check if 0-7 or 1-8
        if not 0 <= address <= 7:
            msg = "I2C Address must be 0-7"
            raise Exception(msg)

        command_string = f"AD={address}"
        self.port.write(command_string)
        ret = self.port.read()

        if ret[:3] == "ACK" and ret[-1] == str(address):
            pass
        elif ret[3:] != str(address):
            msg = f"Incorrect I2C connection to {ret[3:]} established. Expected: {address}."
            raise Exception(msg)
        elif ret[:3] == "NAK":
            msg = f"Failed I2C connection to address {ret[3:]}"
            raise Exception(msg)

    def set_vref(self, use_internal_vref=True):
        v_ref = "I" if use_internal_vref else "E"

        command_string = f"VR={v_ref}"
        self.port.write(command_string)
        ret = self.port.read()

        if ret[:3] != "ACK" and ret[-1] == v_ref:
            msg = "Failed to set reference voltage (vref)"
            raise Exception(msg)

    def set_gain(self, gain):
        if gain not in [1, 2]:
            msg = "gain can only be 1 or 2"
            raise ValueError(msg)

        command_string = f"GN={gain}"
        self.port.write(command_string)
        ret = self.port.read()

        if not ret[:3] == "ACK" and ret[-1] == gain:
            raise Exception("Failed to set gain (vref)")
