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

import contextlib
import importlib
import time

import shr
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.PortManager import PortManager
from pysweepme.Ports import Port

# Reload the shr module to ensure the latest version is used
importlib.reload(shr)
from shr import IsegDevice


class Device(EmptyDevice, IsegDevice):
    """Driver for the iseg SHR."""

    description = "Averaing will be set for all channels in the module."

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
        self.port_types = [
            "COM",
            # "TCPIP",  # For TCPIP, the device must be installed as raw socket via NI Max - better use socket directly
            "SOCKET",
        ]
        self.port_properties = {
            "timeout": 0.5,
            "SOCKET_EOLwrite": "\r\n",
            "SOCKET_EOLread": "\r\n",
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
        self.mode: str = "2kV/4mA"
        self.compliance: float = 0.004  # Default compliance for 2kV/4mA mode in A
        self.nominal_voltage: float = 0.0
        """The maximum output voltage of the device. This is used to determine the voltage accuracy for low voltages."""

        self.measured_voltage: float = 0.0
        self.measured_current: float = 0.0

        self.last_query_time: float = 0.0
        self.measurement_is_running = None
        """Flag to indicate if a measurement is running to avoid querying the supported modes during measurement."""

    def update_gui_parameters(self, parameters: dict) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        port_string = parameters.get("Port", "")
        channel = parameters.get("Channel", "0")
        if port_string:
            self.modes = self.get_supported_modes_with_fallback(port_string, channel)

        return {
            "SweepMode": ["Voltage in V", "Current in A"],
            "Channel": ["0", "1", "2", "3"],
            "Compliance": "0.004",  # 4 mA compliance for 2kV/4mA mode
            # "Average": 1,
            "Mode": list(self.modes.keys()),
            "Polarity": self.polarity_modes,
            "Ramp rate": "50 V/s",
        }

    def get_supported_modes_with_fallback(self, port_string: str, channel: str) -> dict[str, int]:
        """Get the supported modes with a fallback if the time since the last query is too short.

        This function queries the supported output modes from the device.
        Do not query the modes if:
        - The time since the last query is less than 10 seconds to avoid flooding increased GUI loading times.
        - The measurement is running to avoid communication issues.
        - The port cannot be opened, e.g., if the device is not connected or the port string is invalid.

        As a fallback, return self.modes (Which might have been updated on an earlier run of apply_gui_parameters).
        """
        # Check the parameter store if the modes have been queried before
        # Data is saved as dictionary of format {'modes': {mode_string: mode_number}, 'last_query_time': time}}
        # key must include port_string and channel to distinguish between multiple connected devices and channels
        parameter_key = f"{port_string}_{channel}"
        saved_parameters = self.restore_parameter(parameter_key)

        # 10s time between queries should be sufficient to only query once during the GUI loading and small enough to
        # update if a new device is connected
        # If the measurement is running, do not query the modes to avoid communication issues
        if (saved_parameters is not None and
                (time.time() - saved_parameters.get("last_query_time", 0) < 10 or self.measurement_is_running)):
            modes = saved_parameters.get("modes", {})
            if modes:
                return modes

        # check if self.port is already open
        close_port = False

        port_not_ready = (
            not hasattr(self, "port") or
            self.port is None or
            not self.port or
            not self.port.port_properties.get("is_open", False)
        )

        if port_not_ready:
            try:
                port_manager = PortManager()
                self.port = port_manager.get_port(port_string, self.port_properties)

                # Need to double-check if self.port is a valid Port instance, as the PortManager might ignore Exceptions during
                # port opening and return False or None
                if not isinstance(self.port, Port):
                    return self.modes
            except:
                return self.modes
            else:
                close_port = True

        # Set the channel to allow querying modes for a specific channel
        self.channel = int(channel)

        try:
            # Create supported modes dictionary
            mode_numbers = self.get_supported_output_modes()
            voltage_modes = self.get_supported_voltage_modes()
            current_modes = self.get_supported_current_modes()

            supported_modes = {}
            for n, number in enumerate(mode_numbers):
                voltage_range = float(voltage_modes[n]) / 1000  # Convert V to kV
                current_range = float(current_modes[n]) * 1000  # Convert A to mA
                mode_string = f"{int(voltage_range)}kV/{int(current_range)}mA"
                supported_modes[mode_string] = number

            self.store_parameter(parameter_key, {"modes": supported_modes, "last_query_time": time.time()})
        except:
            supported_modes = self.modes
        finally:
            # close if it was not opened before
            if close_port:
                with contextlib.suppress(Exception):
                    self.port.close()

        return supported_modes

    def apply_gui_parameters(self, parameters: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweepmode = parameters.get("SweepMode", "Voltage in V")
        self.channel = parameters.get("Channel", 0)

        # Receive the port string to decide if echoing is used with COM ports
        self.port_string = parameters.get("Port", "")

        self.compliance = parameters.get("Compliance", "0.004")  # Default 4 mA for 2kV/4mA mode
        # self.average = parameters.get("Average", 64)
        self.ramp_rate = parameters.get("Ramp rate", "100 V/s")
        self.polarity_mode = parameters.get("Polarity", "Auto")
        self.mode = parameters.get("Mode", "2kV/4mA")

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.measurement_is_running = True
        self.port.clear()
        self.clear_event_status()

        # TODO: Decide if the device should be reset, as it resets the ramp rates as well
        self.reset()
        self.set_local_lockout(True)
        self.nominal_voltage = self.get_voltage_nominal()
        self.output_polarity = self.get_output_polarity()

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""
        self.set_local_lockout(False)
        self.measurement_is_running = False

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        if self.polarity_mode == "Positive":
            self.set_polarity("p")
        elif self.polarity_mode == "Negative":
            self.set_polarity("n")

        # For voltage mode, set the current limit (in this case the current value) to the compliance value
        compliance = float(self.compliance)
        if self.sweepmode.startswith("Voltage"):
            self.set_current_with_confirmation(compliance)
            # Start with voltage off to ensure the device does not ramp up on poweron
            self.set_voltage_with_confirmation(0)

        # For current mode, set the voltage limit (in this case the voltage value) to the compliance value
        elif self.sweepmode.startswith("Current"):
            self.set_voltage_with_confirmation(compliance)
            # Start with current off to ensure the device does not ramp up on poweron
            self.set_current_with_confirmation(0)

        # Currently, averaging is not implemented, because the average can only be set for all channels at once and
        # changing the average will change the voltage measurement mode.
        # self.handle_averaging(int(self.average))
        self.set_voltage_range(self.mode)
        self.handle_ramp_rate(self.ramp_rate)

    def poweron(self) -> None:
        """Turn on the device when entering a sequencer branch if it was not already used in the previous branch."""
        self.voltage_on()
        self.value_applied_correctly(True, self.voltage_is_on)

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""
        self.voltage_off()

    def apply(self) -> None:
        """'apply' is used to set the new set value that is always available as 'self.value'."""
        try:
            self.value = float(self.value)
        except:
            msg = f"Value '{self.value}' is not a valid number. Please check the 'Value' or 'Sweep value' input."
            raise ValueError(msg)

        self.handle_polarity(self.value)

        if self.sweepmode.startswith("Voltage"):
            self.set_voltage_with_confirmation(self.value)

        elif self.sweepmode.startswith("Current"):
            if abs(self.value) < 20e-6:
                msg = (f"Current value of {self.value} A is too low. For current mode, the driver only supports "
                       f"currents above 20 µA, because setting lower currents changes the voltage ramp rate.")
                raise ValueError(msg)

            self.set_current_with_confirmation(self.value)

        else:
            return

        # If compliance is reached, the device will not ramp up to the set value
        if self.is_in_compliance():
            return

        # Timeout of 5s for the device to start a ramp to prevent endless loop in reach()
        timeout_s = 5
        while timeout_s > 0 and not self.is_run_stopped():
            status = self.get_channel_status()

            # Do not check for 'Is On', as the device might still be 'On' from the previous set point
            # Do not distinguish between Sweep Modes, as even in current mode the device might ramp voltage
            if "Is Voltage Ramp" in status or "Is Current Ramp" in status:
                break

            time.sleep(0.1)
            timeout_s -= 0.1
        else:
            print(f"Device did not start ramping in {round(5-timeout_s)} s to reach {self.value} {self.sweepmode[-1]}. "
                  f"Value change compared to previous set value might be too small.")

    def reach(self) -> None:
        """Wait until the device has reached the set value. This function is called after 'apply'.

        The device status will be checked every 100ms until the status does not contain any Ramping and instead contains
        a constant current or voltage message.
        """
        timeout_in_s = 30
        level_reached = False

        while timeout_in_s > 0:
            status = self.get_channel_status()

            if self.sweepmode.startswith("Voltage"):
                # For voltages <6V the device will not return 'Is Constant Voltage'
                if abs(self.value) <= 6:
                    level_reached = "Is Voltage Ramp" not in status
                else:
                    level_reached = "Is Constant Voltage" in status and "Is Voltage Ramp" not in status

            elif self.sweepmode.startswith("Current"):
                # For currents <0.1% of max current, the device will not return 'Is Constant Current'
                max_current = float(self.mode.split("/")[1].strip("mA"))
                if abs(self.value) <= max_current * 0.001:
                    level_reached = "Is Current Ramp" not in status
                else:
                    level_reached = "Is Constant Current" in status and "Is Current Ramp" not in status

            # if the value is 0, the device will not yield constant current/voltage
            if self.value == 0:
                level_reached = "Is Voltage Ramp" not in status and "Is Current Ramp" not in status

            if not status:
                level_reached = False

            # Check the exit conditions before the timeout to speed up the first loop iteration
            if level_reached or self.is_run_stopped():
                break

            time.sleep(0.1)
            timeout_in_s -= 0.1
        else:
            print("Device did not reach the set value in 30s. Check if the level is reached.")

    def read_result(self) -> None:
        """Retrieve the measurement results. This function is called after 'reach'."""
        self.measured_voltage = self.get_voltage()
        self.measured_current = self.get_current()

    def call(self) -> list:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.measured_voltage, self.measured_current]

    # Configuration

    def set_local_lockout(self, lockout: bool) -> None:
        """Enable/disable the front panel buttons."""
        if lockout:
            self.local_lockout()
        else:
            self.goto_local()

    def handle_averaging(self, average: int) -> None:
        """Set the average number and ensure it is set correctly."""
        if average not in self.averages:
            msg = f"Average {average} not supported. Average must be one of: {', '.join(map(str, self.averages))}."
            raise ValueError(msg)

        self.set_averaging(average)
        set_average = self.get_averaging()
        if average != set_average:
            msg = f"Average {average} not set correctly."
            raise Exception(msg)

    def handle_polarity(self, value: float) -> None:
        """Verify the polarity of the set value. Optionally, set the polarity automatically based on the set value."""
        self.output_polarity = self.get_output_polarity()
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

        if self.get_output_polarity() == polarity:
            # Polarity is already set, no need to change it
            return

        # Can only set polarity when the output is off
        turn_on_again = False
        if self.voltage_is_on():
            self.voltage_off()
            turn_on_again = True

        # Wait until the voltage close to 0V
        timeout_s = 10
        voltage_accuracy = self.nominal_voltage * 1e-4  # 0.01% of the nominal voltage, e.g., 0.2V for 2kV
        while abs(self.get_voltage()) > voltage_accuracy and timeout_s > 0:
            if self.is_run_stopped():
                return

            time.sleep(0.1)
            timeout_s -= 0.1

        self.set_output_polarity(polarity)
        self.output_polarity = polarity
        self.wait_for_operation_complete()

        # Unclear why, but the event status must be cleared or the device will not ramp up again after changing polarity
        self.clear_event_status()

        if not self.value_applied_correctly(self.output_polarity, self.get_output_polarity):
            msg = f"Output polarity {self.output_polarity} could not be set correctly."
            raise Exception(msg)

        if turn_on_again:
            # Wait for the device to be ready before turning on the voltage again
            time.sleep(1)
            self.voltage_on()

    def set_voltage_range(self, mode: str) -> None:
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

        self.set_output_mode(mode_number)

        if not self.value_applied_correctly(mode_number, self.get_output_mode):
            msg = f"Output mode {mode_number} not set correctly."
            raise Exception(msg)

        if turn_on_again:
            self.voltage_on()

    def handle_ramp_rate(self, rate: str) -> None:
        """Handle the ramp rate. The rate is given as string containing the unit (V/s or A/s).

        Ramp rate in %/s is not supported, as it sets the ramp speed for all channels.
        """
        rate = rate.strip()  # remove trailing whitespace
        if rate.endswith("V/s"):
            ramp_rate = float(rate.strip("V/s").strip())
            self.set_voltage_ramp_up_speed(ramp_rate)

            if not self.value_applied_correctly(ramp_rate, self.get_voltage_ramp_up_speed):
                msg = f"Voltage ramp up rate {ramp_rate} V/s was not set correctly. Check if the device supports this ramp rate."
                raise Exception(msg)

            self.set_voltage_ramp_down_speed(ramp_rate)
            if not self.value_applied_correctly(ramp_rate, self.get_voltage_ramp_down_speed):
                msg = f"Voltage ramp down rate {ramp_rate} V/s was not set correctly. Check if the device supports this ramp rate."
                raise Exception(msg)

        elif rate.endswith("A/s"):
            ramp_rate = float(rate.strip("A/s").strip())
            self.set_current_ramp_up_speed(ramp_rate)

            if not self.value_applied_correctly(ramp_rate, self.get_current_ramp_up_speed):
                msg = f"Current ramp up rate {ramp_rate} A/s was not set correctly. Check if the device supports this ramp rate."
                raise Exception(msg)

            self.set_current_ramp_down_speed(ramp_rate)
            if not self.value_applied_correctly(ramp_rate, self.get_current_ramp_down_speed):
                msg = f"Current ramp down rate {ramp_rate} A/s was not set correctly. Check if the device supports this ramp rate."
                raise Exception(msg)

        else:
            msg = f"No supported unit detected for ramp rate of {rate}. Use V/s or %/s."
            raise ValueError(msg)

    def set_current_with_confirmation(self, value: float) -> None:
        """Set the current value in A and wait until the device has set the new value."""
        # The firmware does not support setting negative currents, independent of the polarity mode.
        self.set_current(abs(value))
        self.value_applied_correctly(abs(value), self.get_current_set)

    def set_voltage_with_confirmation(self, value: float) -> None:
        """Set the voltage value in V and wait until the device has set the new value."""
        self.set_voltage(value)
        self.value_applied_correctly(value, self.get_voltage_set)

    def is_in_compliance(self) -> bool:
        """Check if the device is in compliance, and higher set values cannot be reached."""
        if self.sweepmode.startswith("Voltage"):
            compliance = self.get_current_set()
            applied_value = self.get_current()
        elif self.sweepmode.startswith("Current"):
            compliance = self.get_voltage_set()
            applied_value = self.get_voltage()
        else:
            return False

        # If the applied value is larger than 95% of the compliance, it is considered out of compliance
        if abs(applied_value) > abs(compliance) * 0.95:
            return True
        return False

    # Communication

    def value_applied_correctly(self, value: int | str | float, getter: callable, timeout_s: int = 5) -> bool:
        """Wait until the getter function returns the updated value or a timeout is reached."""
        while timeout_s > 0 and not self.is_run_stopped():
            if getter() == value:
                return True
            time.sleep(0.1)
            timeout_s -= 0.1

        return False

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
        if not self.port_string.startswith("COM"):
            # Some write commands seem to leave \r\n bytes in the buffer for socket connections
            # Workaround: clear the socket buffer before sending a query command
            # Add a delay to ensure the response to the previous command is fully read
            time.sleep(0.0)
            self.port.clear()
        self.write(command)
        return self.port.read()

    def wait_for_operation_complete(self, timeout_s: float = 5) -> None:
        """Query the *OPC? command until it returns 1."""
        self.write("*OPC?")
        while not self.is_run_stopped() and timeout_s > 0:
            ret = self.port.read()
            if ret == "1":
                break
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
