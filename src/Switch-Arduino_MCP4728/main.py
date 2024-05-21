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
# *Module: Switch
# *Instrument: Arduino MCP4728

from __future__ import annotations

from pysweepme import EmptyDevice


class Device(EmptyDevice):
    """Base class to control MCP4728 boards through Arduino."""

    description = """
        <h3>Arduino MCP4728</h3>
        <p>
            This driver allows to set output voltages at MCP 4728 boards with 12-bit resolution. It can control up to 8
            boards, each with 4 pins.
        </p>
        <h4>Setup</h4>
        <p>
            Load the Switch-Arduino_MCP.ino sketch onto your Arduino. Set <em>baudrate</em> to 115200 and
            <em>terminator</em> to "\n". Install the Adafruit_MCP4728 library on your Arduino.
        </p>
        <h4>Parameters</h4>
        <p>
            Set <em>Channel </em>to the pin number you want to set, or <em>all </em>to set all four channels. The
            voltage values must be passed as a colon-separated string: <em>1.0:2.5:0:4.2</em>
        </p>
        <p>
        The I&sup2;C address is set as integer 0-7, corresponding to the boards standard addresses 0x60-0x67 (HEX). You
        can check your devices' address by using an
        <a href="https://playground.arduino.cc/Main/I2cScanner/">I&sup2;C Scanner</a>.
        </p>
        <p>
            The maximum voltage is defined by the Voltage reference, which can either be internal (2.048 V or 4.096 V by
            using 2x gain) or from an external source, e.g. the Arduino's 5 V or 3.3 V output. When using an external
            reference, the voltage must be given.
        </p>
        <p>
            To use multiple MCPs, their I&sup2;C addresses need to be changed individually, as described
            <a href="https://github.com/jknipper/mcp4728_program_address">here</a>. Choose <em>Channel: all </em>and
            set a comma-separated list for <em>I2C Address: 0, 1, 2</em>.
        </p>
    """

    def __init__(self) -> None:
        """Initialize the Device Class."""
        EmptyDevice.__init__(self)

        self.shortname = "Arduino MCP4728"
        self.variables = []
        self.units = []

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "EOL": "\n",
            "timeout": 5,
            "baudrate": 115200,
        }
        self.port_str: str = ""
        self.driver_name: str = ""
        self.instance_key: str = ""

        self.pin: int = 0
        self.sweepmode: str = ""
        self.reference_voltage: str = "Internal 4.096 V"
        self.external_voltage: float = 5.0
        self.value_list: list[float] = []
        self.volt: float = 0

        self.multi_pins = False
        self.multi_mcp = False
        self.max_voltage = None
        self.addresses = []

        self.unit = {
            "Voltage in V": "V",
            "Output in %": "%",
        }

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set standard GUI parameters for the SweepMe! software."""
        return {
            "Channel": ["0", "1", "2", "3", "all"],
            "I2C Address": "0",
            "SweepMode": ["Voltage in V", "Output in %"],
            "Voltage reference": ["Internal 2.048 V", "Internal 4.096 V", "External"],
            "External voltage in V": 5.0,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle input from GUI."""
        # Handle output pins
        channel = parameter["Channel"]
        if channel == "all":
            self.multi_pins = True
        else:
            self.pin = int(channel)

        # Handle I2C addresses
        self.addresses = []
        address_list = parameter["I2C Address"].split(",")
        if len(address_list) == 1:
            self.addresses.append(int(parameter["I2C Address"]))
        else:
            for addr in address_list:
                self.addresses.append(int(addr))
            self.multi_mcp = True

        self.sweepmode = str(parameter["SweepMode"])

        # Reference can either be internal (2.048 V or 4.096 V) or external (custom V)
        self.reference_voltage = str(parameter["Voltage reference"])
        if self.reference_voltage == "External":
            self.external_voltage = float(parameter["External voltage in V"])

        # Set variables and units
        if channel == "all" and self.multi_mcp:
            channel_num = len(self.addresses) * 4
        elif channel == "all" and not self.multi_mcp:
            channel_num = 4
        else:
            channel_num = 1

        self.variables = []
        self.units = []
        for n in range(channel_num):
            # If single channel, use the correct pin
            pin = self.pin if channel_num == 1 else n
            self.variables.append(f"Channel{pin}")
            self.units.append(self.unit[self.sweepmode])

        self.port_str = parameter["Port"]
        self.driver_name = parameter["Device"]

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self) -> None:
        """Initialize Arduino and register the device in the communication manager."""
        # Set Name/Number of COM Port as key
        self.instance_key = f"{self.driver_name}_{self.port_str}"

        if self.instance_key not in self.device_communication:
            # Wait for Arduino initialization
            self.port.read()
            self.device_communication[self.instance_key] = "Connected"

    def disconnect(self) -> None:
        """Unregister the device from the communication manager."""
        if self.instance_key in self.device_communication:
            self.device_communication.pop(self.instance_key)

    def configure(self) -> None:
        """Configure the MCP4728 reference voltages."""
        # Initialize single MCP4728 with given I2C address - multi MCPs are set in apply
        if not self.multi_mcp:
            self.set_address(self.addresses[0])

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

    def unconfigure(self) -> None:
        """Set all outputs to 0 V after measurement finishes."""
        if self.multi_pins:
            for address in self.addresses:
                self.set_address(address)
                for pin in range(4):
                    self.set_voltage(pin, 0)
        else:
            self.set_voltage(self.pin, 0)

    def apply(self) -> None:
        """Set the voltages to the pins."""
        if self.multi_pins:
            # Replace , with . to enable float conversion
            dot_separated_values = self.value.replace(",", ".")
            # Input values are separated by colons
            sweep_values = dot_separated_values.split(":")
            self.value_list = list(map(float, sweep_values))

            # Adjust number of channels depending on number of boards and pins
            number_of_channels = 4 * len(self.addresses) if self.multi_mcp else 4

            if len(self.value_list) != number_of_channels:
                msg = f"Incorrect number of voltages received. Expected {number_of_channels} got {len(self.value_list)}"
                raise Exception(msg)

            for n, value in enumerate(self.value_list):
                # Convert individual values to 12 Bit and set voltages
                if self.sweepmode == "Output in %":
                    volt_bit = self.voltage_to_12bit(value, relative_voltage=True)
                else:
                    volt_bit = self.voltage_to_12bit(value)

                # Iterate through pins (0-3) and initialize MCP for each pin=0
                pin = n % 4
                if pin == 0:
                    mcp_num = int(n / 4)
                    self.set_address(self.addresses[mcp_num])

                self.set_voltage(pin, volt_bit)

        else:
            # set voltage for single pin
            try:
                self.volt = float(self.value)
            except ValueError as e:
                msg = "Single Channel Mode activated. Expects float or int from self.value"
                raise ImportError(msg) from e

            if self.sweepmode == "Output in %":
                volt_bit = self.voltage_to_12bit(self.volt, relative_voltage=True)
            else:
                volt_bit = self.voltage_to_12bit(self.volt)

            self.set_voltage(self.pin, volt_bit)

    def call(self) -> list[float]:
        """Return the voltages set to the pins."""
        return self.value_list if self.multi_pins else [self.volt]

    """ here, convenience functions start """

    def voltage_to_12bit(self, voltage: float, relative_voltage: bool = False) -> int:
        """Convert given voltage to integer between 0 and 4095 (max voltage)."""
        voltage_bit = int(voltage / 100 * 4095) if relative_voltage else int(4095 / self.max_voltage * voltage)

        max_bit = 4095
        if not 0 <= voltage_bit < max_bit:
            msg = f"Voltage {voltage} out of bound. Either larger than max voltage or negative."
            raise ValueError(msg)

        return voltage_bit

    def set_voltage(self, pin: int, bit_value: int) -> None:
        """Send command to set voltage (in bit) at given pin."""
        command_string = f"CH{pin}={bit_value}"
        self.port.write(command_string)

        # Check Arduino response
        ret = self.port.read()
        if ret == f"ACK{pin}={bit_value}":
            pass
        elif ret[:3] == "NAK":
            msg = f"Failed to set voltage at pin {pin}"
            raise Exception(msg)
        else:
            msg = f"Failed to set voltage of {bit_value} at pin {pin}. Arduino response: {ret}"
            raise Exception(msg)

    def set_address(self, address: int) -> None:
        """Initialize MCP at Arduino to receive further commands."""
        max_address = 7
        if not 0 <= address <= max_address:
            msg = "I2C Address must be 0-7"
            raise Exception(msg)

        command_string = f"AD={address}"

        # Check Arduino response
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
        else:
            msg = f"Failed to set address to {address}. Arduino response: {ret}"
            raise Exception(msg)

    def set_vref(self, use_internal_vref: bool = True) -> None:
        """Set reference voltage as internal or external."""
        v_ref = "I" if use_internal_vref else "E"

        command_string = f"VR={v_ref}"
        self.port.write(command_string)

        # Check Arduino response
        ret = self.port.read()
        if ret != f"ACK{v_ref}":
            msg = f"Failed to set reference voltage (vref). Arduino response: {ret}"
            raise Exception(msg)

    def set_gain(self, gain: int) -> None:
        """For internal reference voltage, choose 1x or 2x gain."""
        if gain not in [1, 2]:
            msg = "gain can only be 1 or 2"
            raise ValueError(msg)

        command_string = f"GN={gain}"
        self.port.write(command_string)

        # Check Arduino response
        ret = self.port.read()
        if ret != f"ACK{gain}":
            msg = f"Failed to set gain (vref). Arduino response: {ret}"
            raise Exception(msg)
