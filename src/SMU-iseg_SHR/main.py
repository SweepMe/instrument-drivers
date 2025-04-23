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


class Device(EmptyDevice):
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
        self.ramp_rate: float = 100  # Ramp rate in V/s or %/s, use %/s for now
        self.modes = {
            "2kV/4mA": 1,
            "4kV/3mA": 2,
            "6kV/2mA": 3,
        }
        self.mode: int = 1

        self.measured_voltage: float = 0.0
        self.measured_current: float = 0.0

    def set_GUIparameter(self) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Voltage in V", "Current in A", "None"],
            "Channel": ["0", "1", "2", "3"],
            "Average": 1,
            "Speed": [100],  # use speed as placeholder for ramp rate
            "Range": list(self.modes.keys()),  # use range as placeholder for mode
            "RangeVoltage": self.polarity_modes,  # use voltage range as placeholder for polarity
        }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweepmode = parameter["SweepMode"]
        self.channel = parameter["Channel"]

        # Receive the port string to decide if echoing is used with COM ports
        self.port_string = parameter["Port"]

        self.average = parameter["Average"]
        self.ramp_rate = float(parameter["Speed"])
        self.polarity_mode = parameter["RangeVoltage"]
        self.mode = parameter["Range"]

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.clear_event_status()

        # TODO: Device if the device should be reset, as it resets the ramp rates as well
        self.reset_device()

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.set_local_lockout(True)

        if self.polarity_mode == "Positive":
            self.set_output_polarity("p")
        elif self.polarity_mode == "Negative":
            self.set_output_polarity("n")

        self.set_average(self.average)
        self.set_output_mode(self.mode)

        self.set_voltage_ramp_rate(self.ramp_rate, "%/s")

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        self.set_local_lockout(False)

    def poweron(self) -> None:
        """Turn on the device when entering a sequencer branch if it was not already used in the previous branch."""
        self.set_output_state(True)

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""
        self.set_output_state(False)

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
                self.set_output_polarity(change_polarity)

    def reach(self) -> None:
        """Wait until the device has reached the set value. This function is called after 'apply'."""
        timeout_in_s = 30
        level_reached = False

        while not level_reached and timeout_in_s > 0:
            # TODO: Some values are skipped because the device status still says 'constant' even though a new value was set
            status = self.get_channel_status()
            # print(status)
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

    def write(self, command: str) -> None:
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
        self.write(command)
        return self.port.read()

    # Wrapped SCPI commands

    def clear_event_status(self) -> None:
        """Clear the event status of the device."""
        # TODO: Why do i need to query? should not return something
        self.query("*CLS")

    def reset_device(self) -> None:
        """Reset the device to its default state."""
        # TODO: Why do i need to query? should not return something
        self.port.query("*RST")

    def get_identification(self) -> str:
        """Get the identification string of the device."""
        return self.query("*IDN?")

    def set_local_lockout(self, lockout: bool) -> None:
        """Enable/disable the front panel buttons."""
        if lockout:
            self.write("*LLO")
        else:
            self.write("*GTL")

    # Voltage and current

    def set_voltage(self, voltage: float) -> None:
        """Set the output voltage."""
        self.write(f"VOLT {voltage},(@{self.channel})")

    def set_voltage_bounds(self, voltage_limit: float) -> None:
        """Set the output voltage limit/bounds."""
        self.write(f"VOLT:BOUNDS {voltage_limit},(@{self.channel})")

    def get_voltage(self) -> float:
        """Get the measured voltage."""
        return self.get_value("MEAS:VOLT?")

    def get_value(self, command: str) -> float:
        """Get the value of a command for the channel."""
        answer = self.query(f"{command} (@{self.channel})")
        return float(answer[:-1])

    def get_voltage_set(self) -> float:
        """Get the set output voltage in V."""
        return self.get_value("READ:VOLT?")

    def set_current(self, current: float) -> None:
        """Set the output current."""
        self.write(f"CURR {current},(@{self.channel})")

    def set_current_bounds(self, current_limit: float) -> None:
        """Set the output current limit/bounds."""
        self.write(f"CURR:BOUNDS {current_limit},(@{self.channel})")

    def get_current_set(self) -> float:
        """Get the set output current in A."""
        return self.get_value("READ:CURR?")

    def get_current(self) -> float:
        """Get the measured current."""
        return self.get_value("MEAS:CURR?")

    # Polarity

    def set_output_polarity(self, polarity: str = "p") -> None:
        """Set the output polarity."""
        if polarity not in ["p", "n"]:
            msg = "Polarity must be 'p' or 'n'"
            raise ValueError(msg)

        # Can only set polarity when the output is off
        turn_on_again = False
        if self.get_output_state():
            self.set_output_state(False)
            turn_on_again = True

        self.write(f"CONF:OUTPUT:POL {polarity},(@{self.channel})")
        self.output_polarity = polarity
        self.wait_for_operation_complete()

        if not self.value_applied_correctly(self.output_polarity, self.get_output_polarity):
            msg = f"Output polarity {self.output_polarity} could not be set correctly."
            raise Exception(msg)

        if turn_on_again:
            self.set_output_state(True)

    def get_output_polarity(self) -> str:
        """Get the output polarity."""
        return self.query(f"CONF:OUTPUT:POL? (@{self.channel})")

    # Output

    def set_output_state(self, state: bool) -> None:
        """Set the output state to on or off."""
        if state:
            self.write(f"VOLT ON,(@{self.channel})")
        else:
            self.write(f"VOLT OFF,(@{self.channel})")

    def get_output_state(self) -> bool:
        """Get the output state."""
        state = self.query(f"READ:VOLT:ON? (@{self.channel})")
        return str(state) == "1"

    # Configure

    def set_average(self, average: int) -> None:
        """Set the number of digital filter averaging steps."""
        if average not in self.averages:
            msg = f"Average {average} is not allowed. Allowed values are {self.averages}."
            raise ValueError(msg)

        self.write(f"CONF: AVER {average}")

    def wait_for_operation_complete(self) -> None:
        """Query the *OPC? command until it returns 1."""
        # TODO: Check if this is needed
        ret = self.query("*OPC?")
        while ret != "1":
            time.sleep(0.1)
            ret = self.port.read()

    def set_output_mode(self, mode: int) -> None:
        """Set the output mode."""
        supported_modes = self.get_supported_output_modes()
        mode_number = self.modes[mode]
        # print(f"Mode number: {mode_number}")
        if mode_number not in supported_modes:
            msg = f"Mode {mode} is not supported. Supported modes are {supported_modes}."
            raise ValueError(msg)

        # Can only set mode when the output is off
        turn_on_again = False
        if self.get_output_state():
            self.set_output_state(False)
            turn_on_again = True

        # TODO: Setting the mode does not work consistently yet
        self.query(f"CONF:OUTPUT:MODE {mode_number},(@{self.channel})")

        if not self.value_applied_correctly(mode_number, self.get_output_mode):
            msg = f"Output mode {mode_number} not set correctly."
            raise Exception(msg)

        if turn_on_again:
            self.set_output_state(True)

    def value_applied_correctly(self, value: int | str, getter: callable, timeout_s: int = 5) -> bool:
        """Wait until the getter function returns the set value."""
        while timeout_s > 0 and not self.is_run_stopped():
            if getter() == value:
                return True
            time.sleep(0.1)
            timeout_s -= 0.1

        return False

    def get_output_mode(self) -> int:
        """Get the output mode."""
        return int(self.query(f"CONF:OUTPUT:MODE? (@{self.channel})"))

    def get_supported_output_modes(self) -> list[int]:
        """Get the available channel output modes."""
        supported_modes = self.query(f"CONF:OUTPUT:MODE:LIST? (@{self.channel})")
        return list(map(int, supported_modes.split(",")))

    def get_channel_status(self) -> list:
        """Get the channel status."""
        status = self.query(f"READ:CHAN:STATUS? (@{self.channel})")
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

    # Ramp

    def set_voltage_ramp_rate(self, rate: float, mode: str = "V/s", direction: str = "up") -> None:
        """Set the voltage ramp rate.

        rate: Ramp rate in V/s or %/s
        mode: "V/s" or "%/s"
        direction: "up" or "down". Only relevant for V/s mode.
        """
        if mode == "V/s":
            direction = "UP" if direction == "up" else "DOWN"
            self.write(f"CONF:RAMP:VOLT:{direction} {rate},(@{self.channel})")
        else:
            # %/s is set for both directions
            self.write(f"CONF:RAMP:VOLT {rate}")

