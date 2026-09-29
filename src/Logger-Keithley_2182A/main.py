# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2026 SweepMe! GmbH (sweep-me.net)
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
# * Module: Logger
# * Instrument: Keithley 2182A

"""SweepMe! driver for the Keithley 2182A nanovoltmeter."""

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keithley 2182A nanovoltmeter to measure voltages or thermocouple temperatures."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "Keithley 2182A"

        self.port_manager = True
        self.port_types = ["GPIB", "COM"]

        self.port_properties = {
            "timeout": 10,
            "baudrate": 19200,
            "EOL": "\r",
        }

        self.channels = {
            "Channel 1": 1,
            "Channel 2": 2,
        }

        self.modes = {
            "Voltage": "VOLT",
            "Temperature": "TEMP",
        }

        # voltage ranges as shown in the GUI and the expected reading in V that is sent to the instrument
        self.voltage_ranges = {
            "Channel 1": {
                "Auto": 0.0,
                "10 mV": 0.01,
                "100 mV": 0.1,
                "1 V": 1.0,
                "10 V": 10.0,
                "100 V": 100.0,
            },
            "Channel 2": {
                "Auto": 0.0,
                "100 mV": 0.1,
                "1 V": 1.0,
                "10 V": 10.0,
            },
        }

        self.nplc_types = {
            "Fastest (0.01)": 0.01,
            "Fast (0.1)": 0.1,
            "Medium (1)": 1.0,
            "Default (5)": 5.0,
            "Slow (10)": 10.0,
            "Slowest (50)": 50.0,
        }

        self.digital_filters = {
            "Off": "",
            "Moving": "MOV",
            "Repeat": "REP",
        }

        self.thermocouple_types = ["J", "K", "T", "E", "N", "R", "S", "B"]

        self.temperature_units = ["°C", "K", "°F"]

        # GUI parameters
        self.port_string: str = ""
        self.channel: str = "Channel 1"
        self.mode: str = "Voltage"
        self.voltage_range: str = "Auto"
        self.nplc: float = 5.0
        self.digital_filter: str = "Off"
        self.filter_count: int = 10
        self.analog_filter: bool = False
        self.thermocouple_type: str = "J"
        self.temperature_unit: str = "°C"
        self.display: str = "On"

        # measured value
        self.measured_value: float = float("nan")

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the GUI parameters and their options depending on the current selection."""
        channel = parameters.get("Channel", "Channel 1")
        mode = parameters.get("Mode", "Voltage")
        digital_filter = parameters.get("Digital filter", "Off")

        new_parameters: dict[str, Any] = {
            "Channel": list(self.channels.keys()),
            "Mode": list(self.modes.keys()),
        }

        if mode == "Voltage":
            new_parameters["Range"] = list(self.voltage_ranges.get(channel, self.voltage_ranges["Channel 1"]).keys())
        else:
            new_parameters["Thermocouple type"] = self.thermocouple_types
            new_parameters["Temperature unit"] = self.temperature_units

        new_parameters.update(
            {
                "NPLC": list(self.nplc_types.keys()),
                "Digital filter": list(self.digital_filters.keys()),
            },
        )

        if digital_filter != "Off":
            new_parameters["Filter count"] = 10

        new_parameters.update(
            {
                "Analog filter": False,
                "Display": ["On", "Off"],
            },
        )

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the GUI parameters selected by the user and update the returned variables."""
        self.port_string = parameters.get("Port", "")
        self.channel = parameters.get("Channel", "Channel 1")
        self.mode = parameters.get("Mode", "Voltage")
        self.nplc = self.nplc_types.get(parameters.get("NPLC", "Default (5)"), 5.0)
        self.analog_filter = bool(parameters.get("Analog filter", False))
        self.display = parameters.get("Display", "On")

        if self.mode == "Voltage":
            self.voltage_range = parameters.get("Range", "Auto")
        else:
            self.thermocouple_type = parameters.get("Thermocouple type", "J")
            self.temperature_unit = parameters.get("Temperature unit", "°C")

        self.digital_filter = parameters.get("Digital filter", "Off")
        if self.digital_filter != "Off":
            self.filter_count = int(parameters.get("Filter count", 10))

        if self.mode == "Voltage":
            self.variables = ["Voltage"]
            self.units = ["V"]
        else:
            self.variables = ["Temperature"]
            self.units = [self.temperature_unit]

        self.plottype = [True]
        self.savetype = [True]

        # One conversion takes up to NPLC/50 s (50 Hz) and autozero roughly doubles it. The filter needs 'count'
        # conversions per reading and the analog filter adds 125 ms settling time to each conversion.
        count = self.filter_count if self.digital_filter != "Off" else 1
        conversion_time = 2 * self.nplc / 50 + (0.125 if self.analog_filter else 0.0)
        self.port_properties["timeout"] = max(10.0, 2 * count * conversion_time + 5.0)

    def initialize(self) -> None:
        """Reset the instrument once at the beginning of the measurement."""
        self.reset()
        self.clear_status()
        self.set_beeper(False)

        # no instance has configured a channel and function yet
        self.device_communication[self.port_string] = {"setup": None}

    def deinitialize(self) -> None:
        """Restore the front panel settings at the end of the measurement."""
        if self.display == "Off":
            self.set_display(True)
        self.set_beeper(True)

    def configure(self) -> None:
        """Configure the channel, the measurement function, and the trigger."""
        # needed to use the "READ?" command
        self.set_continuous_initiation(False)

        self.configure_measurement()

        if self.display == "Off":
            self.set_display(False)

        self.print_errors()

    def unconfigure(self) -> None:
        """Switch the display on again if it was switched off."""
        if self.display == "Off":
            self.set_display(True)

    def measure(self) -> None:
        """Trigger a measurement and read the result.

        Triggering and reading are done in the same phase, so that several driver instances sharing the same
        instrument, e.g. one for each channel, cannot interleave their requests.
        """
        # another driver instance on the same instrument might have changed the channel or function
        if self.device_communication[self.port_string]["setup"] != self.get_setup_key():
            self.configure_measurement()

        self.measured_value = self.read_value()

    def call(self) -> list[float]:
        """Return the measured value."""
        return [self.measured_value]

    """ here, convenience functions start """

    def get_setup_key(self) -> tuple[Any, ...]:
        """Return the settings of this instance that other instances on the same instrument might change."""
        return (
            self.channel,
            self.mode,
            self.nplc,
            self.voltage_range,
            self.digital_filter,
            self.filter_count,
            self.analog_filter,
            self.thermocouple_type,
            self.temperature_unit,
        )

    def configure_measurement(self) -> None:
        """Set channel, function, integration time, range, filters, and temperature settings."""
        function = self.modes[self.mode]
        channel = self.channels[self.channel]

        self.set_function(function)
        self.set_channel(channel)
        self.set_nplc(function, self.nplc)

        if self.mode == "Voltage":
            voltage_range = self.voltage_ranges[self.channel][self.voltage_range]
            if voltage_range == 0.0:
                self.set_voltage_autorange(channel, True)
            else:
                self.set_voltage_range(channel, voltage_range)
        else:
            self.set_temperature_transducer("TC")
            self.set_thermocouple_type(self.thermocouple_type)
            self.set_temperature_unit(self.temperature_unit.replace("°", ""))

        if self.digital_filter == "Off":
            self.set_digital_filter(function, channel, False)
        else:
            self.set_digital_filter_type(function, channel, self.digital_filters[self.digital_filter])
            self.set_digital_filter_count(function, channel, self.filter_count)
            self.set_digital_filter(function, channel, True)

        self.set_analog_filter(function, channel, self.analog_filter)

        self.device_communication[self.port_string]["setup"] = self.get_setup_key()

    def print_errors(self) -> None:
        """Read the error queue and print all errors to the debug widget."""
        # the error queue holds up to 10 messages
        for _ in range(10):
            error = self.read_error()
            if int(error.split(",")[0]) == 0:
                break
            print(f"Keithley 2182A error: {error}")  # noqa: T201

    """ here, communication commands are wrapped into python convenience functions """

    def get_identification(self) -> str:
        """Return the identification string of the instrument."""
        return str(self.port.query("*IDN?"))

    def reset(self) -> None:
        """Reset the instrument to its default settings."""
        self.port.write("*RST")

    def clear_status(self) -> None:
        """Clear the status registers and the error queue."""
        self.port.write("*CLS")

    def read_error(self) -> str:
        """Return the oldest message of the error queue."""
        return str(self.port.query(":SYST:ERR?"))

    def set_beeper(self, state: bool) -> None:
        """Switch the beeper on or off."""
        self.port.write(f":SYST:BEEP:STAT {'ON' if state else 'OFF'}")

    def set_display(self, state: bool) -> None:
        """Switch the front panel display on or off."""
        self.port.write(f":DISP:ENAB {'ON' if state else 'OFF'}")

    def set_continuous_initiation(self, state: bool) -> None:
        """Switch continuous initiation of the trigger model on or off."""
        self.port.write(f":INIT:CONT {'ON' if state else 'OFF'}")

    def set_function(self, function: str) -> None:
        """Set the measurement function, i.e. 'VOLT' or 'TEMP'."""
        self.port.write(f':SENS:FUNC "{function}"')

    def set_channel(self, channel: int) -> None:
        """Select the measurement channel 1 or 2."""
        self.port.write(f":SENS:CHAN {channel}")

    def set_nplc(self, function: str, nplc: float) -> None:
        """Set the integration time in number of power line cycles for the given function."""
        self.port.write(f":SENS:{function}:NPLC {nplc}")

    def set_voltage_autorange(self, channel: int, state: bool) -> None:
        """Switch the voltage autorange of the given channel on or off."""
        self.port.write(f":SENS:VOLT:CHAN{channel}:RANG:AUTO {'ON' if state else 'OFF'}")

    def set_voltage_range(self, channel: int, voltage_range: float) -> None:
        """Set the voltage range of the given channel by the expected reading in V, which disables autorange."""
        self.port.write(f":SENS:VOLT:CHAN{channel}:RANG {voltage_range}")

    def set_temperature_transducer(self, transducer: str) -> None:
        """Set the temperature transducer, i.e. 'TC' (thermocouple) or 'INT' (internal)."""
        self.port.write(f":SENS:TEMP:TRAN {transducer}")

    def set_thermocouple_type(self, thermocouple_type: str) -> None:
        """Set the thermocouple type: B, E, J, K, N, R, S, or T."""
        self.port.write(f":SENS:TEMP:TC {thermocouple_type}")

    def set_temperature_unit(self, unit: str) -> None:
        """Set the temperature unit, i.e. 'C', 'K', or 'F'."""
        self.port.write(f":UNIT:TEMP {unit}")

    def set_digital_filter(self, function: str, channel: int, state: bool) -> None:
        """Switch the digital filter of the given function and channel on or off."""
        self.port.write(f":SENS:{function}:CHAN{channel}:DFIL {'ON' if state else 'OFF'}")

    def set_digital_filter_type(self, function: str, channel: int, filter_type: str) -> None:
        """Set the digital filter type of the given function and channel, i.e. 'MOV' or 'REP'."""
        self.port.write(f":SENS:{function}:CHAN{channel}:DFIL:TCON {filter_type}")

    def set_digital_filter_count(self, function: str, channel: int, count: int) -> None:
        """Set the number of readings averaged by the digital filter (1 to 100)."""
        self.port.write(f":SENS:{function}:CHAN{channel}:DFIL:COUN {count}")

    def set_analog_filter(self, function: str, channel: int, state: bool) -> None:
        """Switch the analog low-pass filter of the given function and channel on or off."""
        self.port.write(f":SENS:{function}:CHAN{channel}:LPAS {'ON' if state else 'OFF'}")

    def read_value(self) -> float:
        """Trigger a single measurement and return the reading."""
        return float(self.port.query(":READ?"))
