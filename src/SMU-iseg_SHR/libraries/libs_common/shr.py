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

from __future__ import annotations

from abc import ABC, abstractmethod


class IsegDevice(ABC):
    """This class contains the wrapped SCPI commands for iseg devices of type EHS, NRH, SHR, NHS, and MICC.

    The implementation requires the following methods:
        - write(command: str) -> None. Write a command to the device.
        - query(command: str) -> str. Query the device and return the response.
    """

    def __init__(self) -> None:
        """Initialize the wrapper class with a channel parameter."""
        super().__init__()
        self.channel = "0"  # Default, can be overridden via GUI parameters or set_parameters()

    @abstractmethod
    def write(self, command: str) -> None:
        """Writes a command to the device."""

    @abstractmethod
    def query(self, command: str) -> str:
        """Queries the device and returns the response."""

    # Basic commands

    def get_identification(self) -> str:
        """Get the identification string of the device."""
        return self.query("*IDN?")

    def clear_event_status(self) -> None:
        """Clear the event status of the device. The device responds with an empty string."""
        self.query("*CLS")

    def reset(self) -> None:
        """Reset the device to its default state.  The device responds with an empty string.

        - turn high voltage off with ramp for all channel
        - set voltage set Vset to zero for all channels
        - set current set Iset to the current nominal for all channels
        """
        self.query("*RST")

    def get_instruction_set(self) -> str:
        """Get the currently selected instruction set.

        All devices support the EDCP command set. Some devices (HPS, EHQ) support further command sets, refer to the
        devices manual for them.
        """
        return self.query("*INSTR?")

    def local_lockout(self) -> None:
        """Local Lockout: Disable the front panel, the device can only be controlled remotely.

        The device responds with an empty string.
        """
        self.query("*LLO")

    def goto_local(self) -> None:
        """Front panel buttons and rotary encoders are enabled.  The device responds with an empty string."""
        self.query("*GTL")

    def get_operation_complete(self) -> bool:
        """Check if the operation is complete.

        Returns:
            True if the operation is complete, False otherwise.
        """
        response = self.query("*OPC?")
        return response.strip() == "1"

    # Channel Voltage Commands - Page 33

    def set_voltage(self, voltage: float) -> None:
        """Set the voltage setpoint (Vset) in Volts."""
        self.write(f":VOLT {voltage},(@{self.channel})")

    def voltage_on(self) -> None:
        """Switch on high voltage with configured ramp speed."""
        self.write(f":VOLT ON,(@{self.channel})")

    def voltage_off(self) -> None:
        """Switch off high voltage with configured ramp speed."""
        self.write(f":VOLT OFF,(@{self.channel})")

    def voltage_emergency_off(self) -> None:
        """Immediately shut down high voltage output without ramp."""
        self.write(f":VOLT EMCY OFF,(@{self.channel})")

    def voltage_emergency_clear(self) -> None:
        """Clear emergency off state, return channel to off state."""
        self.write(f":VOLT EMCY CLR,(@{self.channel})")

    def set_voltage_bounds(self, bounds: float) -> None:
        """Set the voltage bounds (Vbounds) tolerance in Volts."""
        self.write(f":VOLT:BOUNDS {bounds},(@{self.channel})")


    # Channel current commands - page 33

    def set_current(self, current: float) -> None:
        """Set the current setpoint (Iset) in Amperes."""
        self.write(f":CURR {current},(@{self.channel})")

    def set_current_bounds(self, bounds: float) -> None:
        """Set the current bounds (Ibounds) tolerance in Amperes."""
        self.write(f":CURR:BOUNDS {bounds},(@{self.channel})")


    # Channel event commands - page 33

    def clear_event(self) -> None:
        """Clear the Channel Event Status register."""
        self.write(f":EVENT CLEAR,(@{self.channel})")

    def clear_event_mask(self, mask: int) -> None:
        """Clear specific bits in Channel Event Status register by mask."""
        self.write(f":EVENT {mask},(@{self.channel})")

    def set_event_mask(self, mask: int) -> None:
        """Set the Channel Event Mask register."""
        self.write(f":EVENT:MASK {mask},(@{self.channel})")


    # Channel configuration commands - Page 34

    def set_trip_timeout(self, time_ms: int) -> None:
        """Set the delayed trip timeout in milliseconds (1..4095ms)."""
        max_timeout = 4095
        if time_ms < 1 or time_ms > max_timeout:
            msg = f"Timeout must be between 1 and {max_timeout} ms."
            raise ValueError(msg)
        self.write(f":CONF:TRIP:TIME {time_ms},(@{self.channel})")

    def get_trip_timeout(self) -> int:
        """Query the programmed trip timeout in milliseconds."""
        response = self.query(f":CONF:TRIP:TIME? (@{self.channel})")
        if response.endswith("ms"):
            response = response[:-3]
        return int(response)

    def set_trip_action(self, action: int) -> None:
        """Set the action that happens when a current trip occurs.

        Action values:
            0: No action, status flag Trip will be set after timeout
            1: Turn off channel with ramp
            2: Shut down channel without ramp
            3: Shut down the module without ramp
            4: Disable the delayed trip function
        """
        self.write(f":CONF:TRIP:ACTION {action},(@{self.channel})")

    def get_trip_action(self) -> int:
        """Query the configured trip action."""
        response = self.query(f":CONF:TRIP:ACTION? (@{self.channel})")
        return int(response)

    def set_inhibit_action(self, action: int) -> None:
        """Set the action that happens when external inhibit occurs.

        Action values:
            0: No action, status flag External Inhibit will be set
            1: Turn off channel with ramp
            2: Shut down channel without ramp
            3: Shut down the module without ramp
            4: Disable the External Inhibit function
        """
        self.write(f":CONF:INH:ACTION {action},(@{self.channel})")

    def get_inhibit_action(self) -> int:
        """Query the configured external inhibit action."""
        response = self.query(f":CONF:INH:ACTION? (@{self.channel})")
        return int(response)

    def set_output_mode(self, mode: int) -> None:
        """Set the channel output mode.

        Mode values:
            1: Normal mode
            2: Alternate mode 1
            3: Alternate mode 2
        """
        self.write(f":CONF:OUTP:MODE {mode},(@{self.channel})")

    def get_output_mode(self) -> int:
        """Query the channel output mode. Returns -1 if the device has currently no mode and returns 1,2,3."""
        mode = self.query(f":CONF:OUTP:MODE? (@{self.channel})")
        return int(mode)

    def get_supported_output_modes(self) -> list[int]:
        """Query the available output modes."""
        response = self.query(f":CONF:OUTP:MODE:LIST? (@{self.channel})")
        return list(map(int, response.split(",")))

    def set_output_polarity(self, polarity: str) -> None:
        """Set the output polarity.

        Polarity values:
            'POS' - Positive polarity
            'NEG' - Negative polarity
        """
        self.write(f":CONF:OUTP:POL {polarity},(@{self.channel})")

    def get_output_polarity(self) -> str:
        """Query the channel output polarity."""
        response = self.query(f":CONF:OUTP:POL? (@{self.channel})")
        return response.strip()

    def get_supported_output_polarities(self) -> list[str]:
        """Query the available output polarities."""
        response = self.query(f":CONF:OUTP:POL:LIST? (@{self.channel})")
        return response.split(",")


    # Read channel commands - Page 35
    # Voltage read commands

    def get_voltage_set(self) -> float:
        """Get the voltage set V_set in Volt. Returns 'nan' if no voltage is set."""
        response = self.query(f":READ:VOLT? (@{self.channel})")
        if not response:
            return float("nan")
        return float(response[:-1])

    def get_voltage_limit(self) -> float:
        """Get the voltage limit V_lim in Volt."""
        response = self.query(f":READ:VOLT:LIM? (@{self.channel})")
        return float(response[:-1])

    def get_voltage_nominal(self) -> float:
        """Get the channel voltage nominal Vnom in Volt."""
        response = self.query(f":READ:VOLT:NOM? (@{self.channel})")
        return float(response[:-1])

    def get_voltage_mode(self) -> str:
        """Get the configured channel voltage mode with polarity sign in Volt."""
        response = self.query(f":READ:VOLT:MODE? (@{self.channel})")
        return response.strip()

    def get_supported_voltage_modes(self) -> list[float]:
        """Get the available voltage modes."""
        response = self.query(f":READ:VOLT:MODE:LIST? (@{self.channel})")
        supported_modes = response.split(",")
        return [float(mode[:-1]) for mode in supported_modes]

    def get_voltage_bounds(self) -> float:
        """Get the voltage bounds V_bounds in Volt."""
        response = self.query(f":READ:VOLT:BOUNDS? (@{self.channel})")
        return float(response[:-1])

    def voltage_is_on(self) -> bool:
        """Get the channel voltage on state."""
        response = self.query(f":READ:VOLT:ON? (@{self.channel})")
        return response.strip() == "1"

    def get_voltage_emergency(self) -> bool:
        """Get the channel emergency off state."""
        response = self.query(f":READ:VOLT:EMCY? (@{self.channel})")
        return response.strip() == "1"


    # Current read commands

    def get_current_set(self) -> float:
        """Get the current set I_set in Ampere."""
        response = self.query(f":READ:CURR? (@{self.channel})")
        return float(response[:-1])

    def get_current_limit(self) -> float:
        """Get the current limit I_lim in Ampere."""
        response = self.query(f":READ:CURR:LIM? (@{self.channel})")
        return float(response[:-1])

    def get_current_nominal(self) -> float:
        """Get the channel current nominal I_nom in Ampere."""
        response = self.query(f":READ:CURR:NOM? (@{self.channel})")
        return float(response[:-1])

    def get_current_mode(self) -> str:
        """Get the configured channel current mode with polarity sign in Ampere."""
        response = self.query(f":READ:CURR:MODE? (@{self.channel})")
        return response.strip()

    def get_supported_current_modes(self) -> list[float]:
        """Get the available current modes."""
        response = self.query(f":READ:CURR:MODE:LIST? (@{self.channel})")
        supported_modes = response.split(",")
        return [float(mode[:-1]) for mode in supported_modes]

    def get_current_bounds(self) -> float:
        """Get the current bounds I_bounds in Ampere."""
        response = self.query(f":READ:CURR:BOUNDS? (@{self.channel})")
        return float(response[:-1])


    # Ramp read commands

    def get_voltage_ramp_speed(self) -> float:
        """Get the ramp speed in V/s."""
        response = self.query(f":READ:RAMP:VOLT? (@{self.channel})")
        return float(response[:-3])

    def get_voltage_ramp_speed_minimum(self) -> float:
        """Get the minimum ramp speed in V/s."""
        response = self.query(f":READ:RAMP:VOLT:MIN? (@{self.channel})")
        return float(response[:-3])

    def get_voltage_ramp_speed_maximum(self) -> float:
        """Get the maximum ramp speed in V/s."""
        response = self.query(f":READ:RAMP:VOLT:MAX? (@{self.channel})")
        return float(response[:-3])

    def get_current_ramp_speed(self) -> float:
        """Get the ramp speed in A/s."""
        response = self.query(f":READ:RAMP:CURR? (@{self.channel})")
        return float(response[:-3])

    def get_current_ramp_speed_minimum(self) -> float:
        """Get the minimum ramp speed in A/s."""
        response = self.query(f":READ:RAMP:CURR:MIN? (@{self.channel})")
        return float(response[:-3])

    def get_current_ramp_speed_maximum(self) -> float:
        """Get the maximum ramp speed in A/s."""
        response = self.query(f":READ:RAMP:CURR:MAX? (@{self.channel})")
        return float(response[:-3])


    # Channel status

    def get_channel_control_register(self) -> str:
        """Get the channel control register."""
        return self.query(f":READ:CHAN:CONTROL? (@{self.channel})")

    def get_channel_status_register(self) -> str:
        """Get the channel status register."""
        return self.query(f":READ:CHAN:STATUS? (@{self.channel})")

    def get_channel_event_status_register(self) -> str:
        """Get the channel event status register."""
        return self.query(f":READ:CHAN:EVENT:STATUS? (@{self.channel})")

    def get_channel_event_mask_register(self) -> str:
        """Get the channel event mask register."""
        return self.query(f":READ:CHAN:EVENT:MASK? (@{self.channel})")


    # Measure commands - Page 35

    def get_voltage(self) -> float:
        """Get the measured voltage in Volts."""
        response = self.query(f":MEAS:VOLT? (@{self.channel})")
        return float(response[:-1])

    def get_current(self) -> float:
        """Get the measured current in Amperes."""
        response = self.query(f":MEAS:CURR? (@{self.channel})")
        return float(response[:-1])


    # Configure Module Ramps (for all channels) commands - Page 35

    def set_module_voltage_ramp_speed(self, speed: float) -> None:
        """Set the module voltage ramp speed in %/s."""
        self.write(f":CONF:RAMP:VOLT {speed}")

    def get_module_voltage_ramp_speed(self) -> float:
        """Get the module voltage ramp speed in %/s."""
        response = self.query(":CONF:RAMP:VOLT?")
        return float(response[:-3])

    def set_module_voltage_ramp_speed_emergency(self, speed: float) -> None:
        """Set the module voltage ramp speed emergency in %/s."""
        self.write(f":CONF:RAMP:VOLT:EMCY {speed}")

    def get_module_voltage_ramp_speed_emergency(self) -> float:
        """Get the module voltage ramp speed emergency in %/s.

        This function is not implemented in the SHR device, but works for other iseg SMU devices.
        """
        response = self.query(":CONF:RAMP:VOLT:EMCY?")
        return float(response[:-3])

    def get_module_voltage_ramp_speed_emergency_minimum(self) -> float:
        """Get the module voltage ramp speed emergency minimum in %/s.

        This function is not implemented in the SHR device, but works for other iseg SMU devices.
        """
        response = self.query(":CONF:RAMP:VOLT:EMCY:MIN?")
        return float(response[:-3])

    def get_module_voltage_ramp_speed_emergency_maximum(self) -> float:
        """Get the module voltage ramp speed emergency maximum in %/s.

        This function is not implemented in the SHR device, but works for other iseg SMU devices.
        """
        response = self.query(":CONF:RAMP:VOLT:EMCY:MAX?")
        return float(response[:-3])

    def set_module_current_ramp_speed(self, speed: float) -> None:
        """Set the module current ramp speed in %/s."""
        self.write(f":CONF:RAMP:CURR {speed}")

    def get_module_current_ramp_speed(self) -> float:
        """Get the module current ramp speed in %/s."""
        response = self.query(":CONF:RAMP:CURR?")
        return float(response[:-3])


    # Set ramp speed for up and down commands - Page 36

    def set_voltage_ramp_up_down_speed(self, speed: float) -> None:
        """Set the channel voltage ramp speed for up and down in Volt/second."""
        self.write(f":CONF:RAMP:VOLT {speed},(@{self.channel})")

    def set_voltage_ramp_up_speed(self, speed: float) -> None:
        """Set the channel voltage ramp up speed in Volt/second."""
        self.write(f":CONF:RAMP:VOLT:UP {speed},(@{self.channel})")

    def get_voltage_ramp_up_speed(self) -> float:
        """Get the channel voltage ramp up speed in Volt/second."""
        response = self.query(f":CONF:RAMP:VOLT:UP? (@{self.channel})")
        return float(response[:-3])

    def set_voltage_ramp_down_speed(self, speed: float) -> None:
        """Set the channel voltage ramp down speed in Volt/second."""
        self.write(f":CONF:RAMP:VOLT:DOWN {speed},(@{self.channel})")

    def get_voltage_ramp_down_speed(self) -> float:
        """Get the channel voltage ramp down speed in Volt/second."""
        response = self.query(f":CONF:RAMP:VOLT:DOWN? (@{self.channel})")
        return float(response[:-3])

    def set_current_ramp_up_down_speed(self, speed: float) -> None:
        """Set the channel current ramp speed for up and down in Ampere/second."""
        self.write(f":CONF:RAMP:CURR {speed},(@{self.channel})")

    def set_current_ramp_up_speed(self, speed: float) -> None:
        """Set the channel current ramp up speed in Ampere/second."""
        self.write(f":CONF:RAMP:CURR:UP {speed},(@{self.channel})")

    def get_current_ramp_up_speed(self) -> float:
        """Get the channel current ramp up speed in Ampere/second."""
        response = self.query(f":CONF:RAMP:CURR:UP? (@{self.channel})")
        return float(response[:-3])

    def set_current_ramp_down_speed(self, speed: float) -> None:
        """Set the channel current ramp down speed in Ampere/second."""
        self.write(f":CONF:RAMP:CURR:DOWN {speed},(@{self.channel})")

    def get_current_ramp_down_speed(self) -> float:
        """Get the channel current ramp down speed in Ampere/second."""
        response = self.query(f":CONF:RAMP:CURR:DOWN? (@{self.channel})")
        return float(response[:-3])


    # Configure Module commands - Page 38

    def set_averaging(self, average: int) -> None:
        """Set the number of digital filter averaging steps. Factory default is 64."""
        supported_averages = [1, 16, 64, 256, 512, 1024]
        if average not in supported_averages:
            msg = f"Average {average} not supported. Average must be one of: {', '.join(map(str, supported_averages))}."
            raise ValueError(msg)
        self.write(f":CONF:AVER {average}")

    def get_averaging(self) -> int:
        """Get the number of digital filter averaging steps."""
        response = self.query(":CONF:AVER?")
        return int(response)

    def set_kill_enable_function(self, enable: int) -> None:
        """Enable or disable the kill function."""
        if enable not in [0, 1]:
            msg = "Enable must be 0 or 1."
            raise ValueError(msg)
        self.write(f":CONF:KILL {enable}")

    def get_kill_enable_function(self) -> int:
        """Get the kill function enable state."""
        response = self.query(":CONF:KILL?")
        return int(response)

    def set_fine_adjustment(self, enable: int) -> None:
        """Enable or disable the fine adjustment function."""
        if enable not in [0, 1]:
            msg = "Enable must be 0 or 1."
            raise ValueError(msg)
        self.write(f":CONF:ADJUST {enable}")

    def get_fine_adjustment(self) -> int:
        """Get the fine adjustment function enable state."""
        response = self.query(":CONF:ADJUST?")
        return int(response)

    def reset_module_event_status_register(self) -> None:
        """Reset the Module Event Status register."""
        self.write("CONF:EVENT CLEAR")

    def clear_module_event_status_register(self, mask: int) -> None:
        """Clears single bits or bit combinations in the Module Event Status register."""
        self.write(f"CONF:EVENT {mask}")

    def set_module_event_mask_register(self, mask: int) -> None:
        """Set the Module Event Mask register."""
        self.write(f"CONF:EVENT:MASK {mask}")

    def get_module_event_mask_register(self) -> int:
        """Get the Module Event Mask register."""
        response = self.query("CONF:EVENT:MASK?")
        return int(response)

    def set_module_event_channel_mask_register(self, mask: int) -> None:
        """Set the Module Event Channel Mask register."""
        self.write(f"CONF:EVENT:CHANMASK {mask}")

    def get_module_event_channel_mask_register(self) -> int:
        """Get the Module Event Channel Mask register."""
        response = self.query("CONF:EVENT:CHANMASK?")
        return int(response)

    def set_module_can_bus_address(self, address: int) -> None:
        """Set the CAN bus address of the module. Can only be set in configuration mode.

        This function is not implemented in the SHR device, but works for other iseg SMU devices.
        """
        maximum_address = 63
        if address < 0 or address > maximum_address:
            msg = f"CAN bus address must be between 0 and {maximum_address}."
            raise ValueError(msg)
        self.write(f"CONF:CAN:ADDR {address}")

    def get_module_can_bus_address(self) -> int:
        """Get the CAN bus address of the module.

        This function is not implemented in the SHR device, but works for other iseg SMU devices.
        """
        response = self.query("CONF:CAN:ADDR?")
        return int(response)

    def set_can_bus_bit_rate(self, bitrate: int) -> None:
        """Set the CAN bus bit rate of the module to 125 kBit/s or 250 kBit/s. Can only be set in configuration mode."""
        if bitrate not in [125000, 250000]:
            msg = "CAN bus bit rate must be one of: 125000, 250000."
            raise ValueError(msg)
        self.write(f"CONF:CAN:BITRATE {bitrate}")

    def get_can_bus_bit_rate(self) -> int:
        """Get the CAN bus bit rate of the module."""
        response = self.query("CONF:CAN:BITRATE?")
        return int(response)

    def get_serial_baud_rate(self) -> int:
        """Get the serial baud rate of the module.

        This function is not implemented in the SHR device, but works for other iseg SMU devices.
        """
        response = self.query(":CONF:SERIAL:BAUD?")
        return int(response)

    def set_serial_baud_rate(self) -> None:
        """Dynamically switches the serial connection to 115200 Baud.

        This function is not implemented in the SHR device, but works for other iseg SMU devices.
        """
        baud_rate = 115200
        self.write(f"CONF:SERIAL:BAUD {baud_rate}")

    def get_echo_enabled(self) -> bool:
        """Get the echo enabled state of the module."""
        response = self.query("CONF:SERIAL:ECHO?")
        return response.strip() == "1"

    def set_echo_enabled(self, enable: int) -> None:
        """Enable or disable the echo function."""
        if enable not in [0, 1]:
            msg = "Enable must be 0 or 1."
            raise ValueError(msg)
        self.write(f"CONF:SERIAL:ECHO {enable}")


    # Configure module read commands - Page 40

    def get_module_voltage_limit(self) -> float:
        """Get the module voltage limit in Volts."""
        response = self.query(":READ:VOLT:LIM?")
        return float(response[:-1])

    def get_module_current_limit(self) -> float:
        """Get the module current limit in Amperes."""
        response = self.query(":READ:CURR:LIM?")
        return float(response[:-1])

    def get_module_voltage_ramp_speed_percent(self) -> float:
        """Get the module voltage ramp speed in %/s."""
        response = self.query(":READ:RAMP:VOLT?")
        return float(response[:-3])

    def get_module_current_ramp_speed_percent(self) -> float:
        """Get the module current ramp speed in %/s."""
        response = self.query(":READ:RAMP:CURR?")
        return float(response[:-3])

    def get_module_control_register(self) -> str:
        """Get the module control register."""
        return self.query(":READ:MODULE:CONTROL?")

    def get_module_status_register(self) -> str:
        """Get the module status register."""
        return self.query(":READ:MODULE:STATUS?")

    def get_module_event_status_register(self) -> str:
        """Get the module event status register."""
        return self.query(":READ:MODULE:EVENT:STATUS?")

    def get_module_event_mask_register_read(self) -> str:
        """Get the module event mask register.

        This is the same as get_module_event_mask_register, but uses the READ command.
        """
        return self.query(":READ:MODULE:EVENT:MASK?")

    def get_module_event_channel_status_register(self) -> str:
        """Get the module event channel status register."""
        return self.query(":READ:MODULE:EVENT:CHANSTATUS?")

    def get_module_event_channel_mask_register_read(self) -> str:
        """Get the module event channel mask register.

        This is the same as get_module_event_channel_mask_register, but uses the READ command.
        """
        return self.query(":READ:MODULE:EVENT:CHANMASK?")

    def get_module_supply(self, index: int = 0) -> float:
        """Get one of the module supplies specified by Index.

        This is the same as get_module_supply_voltage, but uses the READ command.
        """
        response = self.query(f":READ:MODULE:SUPPLY? (@{index})")
        return float(response[:-1])

    def get_module_supply_voltage(self, supply: str = "+24") -> float:
        """Get the module supply voltage in V.

        Args:
            supply: The supply to query. Can be '+24', '-24', '+5', '+3.3', '+12', or '-12'.
        """
        commands = {
            "+24": "P24V",
            "-24": "N24V",
            "+5": "P5V",
            "+3.3": "P3V",
            "+12": "P12V",
            "-12": "N12V",
        }
        if supply not in commands:
            msg = f"Invalid supply '{supply}'. Valid options are: {', '.join(commands.keys())}."
            raise ValueError(msg)

        response = self.query(f":READ:MODULE:SUPPLY:{commands[supply]}?")
        return float(response[:-1])

    def get_temperature(self) -> float:
        """Get the module temperature in Celsius."""
        response = self.query(":READ:MODULE:TEMPERATURE?")
        return float(response[:-1])

    def get_channel_number(self) -> int:
        """Get the channel number."""
        response = self.query(":READ:MODULE:CHANNELNUMBER?")
        return int(response)

    def get_set_value_changes(self) -> int:
        """Get the number of set value changes."""
        response = self.query(":READ:MODULE:SETVALUE?")
        return int(response)

    def get_firmware(self) -> str:
        """Get the firmware name."""
        response = self.query(":READ:FIRMWARE:NAME?")
        return response.strip()

    def get_release(self) -> str:
        """Get the firmware release version."""
        response = self.query(":READ:FIRMWARE:RELEASE?")
        return response.strip()

    def set_config_mode(self, serial_number: int) -> None:
        """Set the device to configuration mode to change the CAN bitrate or address.

        Only possible if all channels are off. As parameter, the device serial number must be given.
        """
        self.write(f":SYSTEM:USER:CONFIG {serial_number}")

    def set_normal_mode(self) -> None:
        """Set the device to normal mode."""
        self.write(":SYSTEM:USER:CONFIG 0")

    def get_config_mode(self) -> str:
        """Returns 1 in configuration mode, otherwise 0."""
        return self.query(":SYSTEM:USER:CONFIG?")

    def save_config(self) -> None:
        """Saves the changed output mode or polarity to icsConfig.xml."""
        self.write(":SYSTEM:USER:CONFIG SAVE")
