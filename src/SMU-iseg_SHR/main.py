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
# * Instrument: iseg SHR

from __future__ import annotations

import time

from pysweepme import debug
from pysweepme.EmptyDeviceClass import EmptyDevice
from shr import IsegDevice


class Device(EmptyDevice, IsegDevice):
    """Driver for the iseg SHR."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "SHR"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["COM", "TCPIP"]
        self.port_properties = {
            "timeout": 2,
        }

        # Measurement parameters
        self.channel: int = 0
        self.sweepmode: str = "Voltage in V"

        # Polarity
        self.polarity_modes = [
            "Auto",
            "Positive",
            "Negative",
        ]
        self.polarity_mode = "Auto"
        self.output_polarity: str = ""

        self.averages: list = [1, 16, 64, 256, 512, 1024]
        self.average: int = 64
        self.ramp_rate: str = "100 V/s"  # Ramp rate in V/s or %/s, use %/s for now
        self.modes = {
            "2kV/4mA": 1,
            "4kV/3mA": 2,
            "6kV/2mA": 3,
        }
        self.mode: int = 1

        self.measured_voltage: float = 0.0
        self.measured_current: float = 0.0

    def update_gui_parameters(self, parameter: dict) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Voltage in V", "Current in A"],
            "Channel": ["0", "1", "2", "3"],
            "Average": 1,
            "Speed": ["50 V/s", "100 V/s", "200 V/s", "500 V/s"],  # use speed as placeholder for ramp rate
            "Range": list(self.modes.keys()),  # use range as placeholder for mode
            "RangeVoltage": self.polarity_modes,  # use voltage range as placeholder for polarity
        }

    def apply_gui_parameters(self, parameter: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweepmode = parameter["SweepMode"]
        self.channel = parameter["Channel"]

        # Receive the port string to decide if echoing is used with COM ports
        self.port_string = parameter["Port"]

        self.average = parameter["Average"]
        self.ramp_rate = parameter["Speed"]
        self.polarity_mode = parameter["RangeVoltage"]
        self.mode = parameter["Range"]

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.clear_event_status()

        # TODO: Decide if the device should be reset, as it resets the ramp rates as well
        self.reset()
        self.set_local_lockout(True)

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""
        self.set_local_lockout(False)

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        if self.polarity_mode == "Positive":
            self.set_polarity("p")
        elif self.polarity_mode == "Negative":
            self.set_polarity("n")

        self.set_averaging(self.average)
        self.set_voltage_range(self.mode)

        # TODO: Ramp rate cannot be changed as the GUI parameter does not allow line editing
        self.handle_ramp_rate(self.ramp_rate)

    def poweron(self) -> None:
        """Turn on the device when entering a sequencer branch if it was not already used in the previous branch."""
        self.voltage_on()

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""
        self.voltage_off()

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        self.handle_polarity(self.value)

        if self.sweepmode.startswith("Voltage"):
            # TODO: Decide whether 0.1V is the minimum step size
            voltage_changes = abs(self.get_voltage_set() - self.value) > 0.1
            self.set_voltage(self.value)

            # wait for the device to start a ramp. Use 5s timeout in case the level is already reached
            if voltage_changes:
                timeout_s = 5
                while timeout_s > 0:
                    if "Is Voltage Ramp" in self.get_channel_status():
                        break
                    time.sleep(0.1)
                    timeout_s -= 0.1
                else:
                    debug("Device did not start ramping in 5s. Check if the level is reached.")

        elif self.sweepmode.startswith("Current"):
            # TODO: Currently untested
            self.set_current(self.value)

    def reach(self) -> None:
        """Wait until the device has reached the set value. This function is called after 'apply'."""
        timeout_in_s = 30
        level_reached = False

        while not level_reached and timeout_in_s > 0:
            # TODO: Some values are skipped because the device status still says 'constant' even though a new value was set
            status = self.get_channel_status()

            if self.sweepmode.startswith("Voltage"):
                level_reached = "Is Constant Voltage" in status and "Is Voltage Ramp" not in status
            elif self.sweepmode.startswith("Current"):
                level_reached = "Is Constant Current" in status and "Is Current Ramp" not in status

            # if the value is 0, the device will not yiel constant current/voltage
            # TODO: Ensure that the value is reached
            if self.value == 0:
                level_reached = "Is Voltage Ramp" not in status and "Is Current Ramp" not in status

            if not status:
                level_reached = False

            time.sleep(0.1)
            timeout_in_s -= 0.1

            if self.is_run_stopped():
                return

    def call(self) -> list:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        self.measured_voltage = self.get_voltage()
        self.measured_current = self.get_current()

        return [self.measured_voltage, self.measured_current]

    # Configuration

    def set_local_lockout(self, lockout: bool) -> None:
        """Enable/disable the front panel buttons."""
        if lockout:
            self.local_lockout()
        else:
            self.goto_local()

    def handle_polarity(self, value: float) -> None:
        """Verify the polarity of the set value. Optionally, set the polarity automatically based on the set value."""
        if value > 0 and self.polarity_mode == "Negative":
            msg = f"Polarity mode is set to negative, the value of {value} can not be reached."
            raise ValueError(msg)

        if value < 0 and self.polarity_mode == "Positive":
            msg = f"Polarity mode is set to positive, the value of {value} can not be reached."
            raise ValueError(msg)

        if self.polarity_mode == "Auto":
            change_polarity = ""
            if value > 0 and self.output_polarity != "p":
                change_polarity = "p"
            elif value < 0 and self.output_polarity != "n":
                change_polarity = "n"

            if change_polarity:
                self.set_polarity(change_polarity)

    def set_polarity(self, polarity: str = "p") -> None:
        """Set the output polarity."""
        if polarity not in ["p", "n"]:
            msg = "Polarity must be 'p' or 'n'"
            raise ValueError(msg)

        # Can only set polarity when the output is off
        turn_on_again = False
        if self.voltage_is_on():
            self.voltage_off()
            turn_on_again = True

        self.set_output_polarity(polarity)
        self.output_polarity = polarity
        self.wait_for_operation_complete()

        if not self.value_applied_correctly(self.output_polarity, self.get_output_polarity):
            msg = f"Output polarity {self.output_polarity} could not be set correctly."
            raise Exception(msg)

        if turn_on_again:
            self.voltage_on()

    def set_voltage_range(self, mode: int) -> None:
        """Set the voltage range/output mode to either 2kV/4mA, 4kV/3mA, or 6kV/2mA."""
        supported_modes = self.get_supported_output_modes()
        mode_number = self.modes[mode]

        if mode_number not in supported_modes:
            msg = f"Mode {mode} is not supported. Supported modes are {supported_modes}."
            raise ValueError(msg)

        # Can only set mode when the output is off
        turn_on_again = False
        if self.voltage_is_on():
            self.voltage_off()
            turn_on_again = True

        # TODO: Setting the mode does not work consistently yet
        self.set_output_mode(mode_number)

        if not self.value_applied_correctly(mode_number, self.get_output_mode):
            msg = f"Output mode {mode_number} not set correctly."
            raise Exception(msg)

        if turn_on_again:
            self.voltage_on()

    def handle_ramp_rate(self, rate: str) -> None:
        """Handle the ramp rate. The rate is given in V/s or %/s.

        rate: Ramp rate in V/s or %/s
        mode: "V/s" or "%/s"
        direction: "up" or "down". Only relevant for V/s mode.
        """
        if rate.endswith("V/s"):
            ramp_rate = float(rate[:-3].strip())
            self.set_voltage_ramp_up_down_speed(ramp_rate)

        elif rate.endswith("%/s"):
            # %/s is set for both directions
            ramp_rate = float(rate[:-3].strip())
            # TODO: Check if the module ramp speed sets it for all channels - might effect other SMU driver instances
            self.set_module_voltage_ramp_speed(ramp_rate)
        else:
            msg = f"No unit detected for ramp rate of {rate}. Use V/s or %/s."
            raise ValueError(msg)

    # Communication

    def value_applied_correctly(self, value: int | str, getter: callable, timeout_s: int = 5) -> bool:
        """Wait until the getter function returns the updated value or a timeout is reached."""
        while timeout_s > 0 and not self.is_run_stopped():
            if getter() == value:
                return True
            time.sleep(0.1)
            timeout_s -= 0.1

        return False

    def write(self, command: str) -> None:
        """Write a command to the device. Check via *OPC if the command was received."""
        self._write(command)

        # wait for the device to process the command
        # TODO: Check if this is necessary for all commands
        self.wait_for_operation_complete()

    def _write(self, command: str) -> None:
        """Write a command to the device. Handle echo if USB connection is used."""
        self.port.write(command)

        # Handle echo for COM port
        if self.port_string.startswith("COM"):
            echo = self.port.read()
            if echo == "":
                echo = self.port.read()

            if echo != command:
                msg = f"Echo mismatch: expected {command}, got {echo}"
                raise Exception(msg)

    def query(self, command: str) -> str:
        """Send a command to the device and read the response."""
        self._write(command)
        return self.port.read()

    def wait_for_operation_complete(self, timeout_s: float = 5) -> None:
        """Query the *OPC? command until it returns 1."""
        while not self.get_operation_complete() and not self.is_run_stopped() and timeout_s > 0:
            time.sleep(0.1)
            timeout_s -= 0.1

    def get_channel_status(self) -> list:
        """Get the channel status."""
        status = self.get_channel_status_register()
        return self.decode_channel_status(int(status))

    @staticmethod
    def decode_channel_status(status_int: int) -> list:
        """Decode the channel status."""
        status_bits = {
            0: "Is Positive",
            1: "Is Arc",
            2: "Is Input Error",
            3: "Is On",
            4: "Is Voltage Ramp",
            5: "Is Emergency Off",
            6: "Is Constant Current",
            7: "Is Constant Voltage",
            8: "Is Low Current Range",
            9: "Is Arc Number Exceeded",
            10: "Is Current Bounds",
            11: "Is Voltage Bounds",
            12: "Is External Inhibit",
            13: "Is Current Trip",
            14: "Is Current Limit",
            15: "Is Voltage Limit",
            16: "Is Current Ramp",
            17: "Is Current Ramp Up",
            18: "Is Current Ramp Down",
            19: "Is Voltage Ramp Up",
            20: "Is Voltage Ramp Down",
            21: "Is Voltage Bound Upper",
            22: "Is Voltage Bound Lower",
            23: "Reserved",
            24: "Reserved",
            25: "Reserved",
            26: "Is Flashover",
            27: "Is Flashover Number Exceeded",
            28: "Reserved",
            29: "Reserved",
            30: "Reserved",
            31: "Reserved",
        }

        active_statuses = []
        for bit in range(32):
            if (status_int >> bit) & 1:
                desc = status_bits.get(bit, f"Unknown Bit {bit}")
                active_statuses.append(desc)

        return active_statuses
