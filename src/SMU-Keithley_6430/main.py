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
#
# SweepMe! driver
# * Module: SMU
# * Instrument: Keithley 6430

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keithley 6430."""

    description = """
                    <h3>Keithley 6430 Driver</h3>
                    <p>Setup:</p>
                    <ul>
                    <li>Enable remote control at device</li>
                    <li>Current range: -105e-3 - 105e-3 A</li>
                    <li>Voltage range: -210 - 210 V</li>
                    <li>Speed in NPLC (0.01 - 10)</li>
                    </ul>
                """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "6430"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["GPIB", "COM", "TCPIP"]

        # Measurement parameters
        self.sweep_mode: str = "None"
        self.compliance: float = 0.0
        self.speeds: dict[str, float] = {
            "Fast": 0.01,
            "Medium": 0.1,
            "Slow": 1.0,
            "Very Slow": 10.0,
        }
        self.speed: float = 1.0  # NPLC
        self.averages: int = 1
        self.measured_current: float = 0.0
        self.measured_voltage: float = 0.0

        # Current range
        self.current_measurement_ranges: dict[str, float] = {"Auto": 0.0}
        # Add current ranges from 1 pA to 100 mA for limited and fixed mode
        for prefix in ["m", "µ", "n", "p"]:
            for number in [100, 10, 1]:
                exponent = {"m": -3, "µ": -6, "n": -9, "p": -12}[prefix]
                value = number * 10**exponent
                key = f"{number} {prefix}A"
                self.current_measurement_ranges[key] = value
        self.current_measurement_range: str = "Auto"

        self.voltage_measurement_ranges: dict[str, float] = {
            "Auto": 0.0,  # float value is only a placeholder for "Auto"
            "200 V": 200.0,
            "20 V": 20.0,
            "2 V": 2.0,
            "200 mV": 0.2,
        }
        self.voltage_measurement_range: str = "Auto"

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "SweepMode": ["None", "Voltage in V", "Current in A"],
            "Compliance": 0.0,
            "Range": list(self.current_measurement_ranges.keys()),
            "RangeVoltage": list(self.voltage_measurement_ranges.keys()),
            "Speed": list(self.speeds.keys()),
            "Average": 1,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")

        self.sweep_mode = parameters.get("SweepMode", "None")
        self.compliance = parameters.get("Compliance", 0.0)

        self.current_measurement_range = parameters.get("Range", "Auto")
        self.voltage_measurement_range = parameters.get("RangeVoltage", "Auto")

        try:
            self.speed = self.speeds[parameters.get("Speed", "Medium")]
        except KeyError:
            self.speed = float(parameters.get("Speed", 1.0))

        self.averages = int(float(parameters.get("Average", 1)))

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.port.write("*RST")          # reset instrument state
        self.port.write(":SYSTem:CLEar") # clear error queue
        self.port.write(":OUTPut:STATe OFF")  # explicit safety

    def poweron(self) -> None:
        """Turn on the device when entering a sequencer branch if it was not already used in the previous branch."""
        self.output_on()

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""
        self.output_off()

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.port.write("SYSTem:BEEPer:STATe OFF")  # turn off beeper

        # set compliance, range and speed
        if self.sweep_mode.startswith("Voltage"):
            self.set_compliance_current(self.compliance)
            self.set_current_measurement_range(self.current_measurement_range)
            self.set_measurement_speed("CURR", self.speed)

            self.port.write("SOURce:VOLTage:MODE FIXed")  # Alternative: list, sweep

        elif self.sweep_mode.startswith("Current"):
            self.set_compliance_voltage(self.compliance)
            self.set_voltage_measurement_range(self.voltage_measurement_range)
            self.set_measurement_speed("VOLT", self.speed)

            self.port.write("SOURce:CURRent:MODE FIXed")  # Alternative: list, sweep

        self.port.write("SENSe:FUNCtion:OFF:ALL")  # reset measurement functions
        self.set_measurement_functions(["VOLT", "CURR"])

        self.port.query(":SENSe:FUNCtion:ON?")

        if self.averages < 1 or self.averages > 100:
            msg = f"Invalid average: {self.averages}. Averages must be between 1 and 100"
            raise ValueError(msg)
        if self.averages > 1:
            # Moving filter average
            self.port.write(f":SENSe:AVERage:COUNt {self.averages}")
            self.port.write(":SENSe:AVERage:STATe ON")
        else:
            self.port.write(":SENSe:AVERage:STATe OFF")

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.sweep_mode.startswith("Voltage"):
            self.set_voltage(self.value)
        elif self.sweep_mode.startswith("Current"):
            self.set_current(self.value)

    def reach(self) -> None:
        """'reach' is used to wait until the setvalue is reached. For most instruments, this is not needed."""
        self.wait_for_complete()

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        # self.port.write("TRIGger:INITiate:IMMediate")
        self.port.write("INIT")

    def request_result(self) -> None:
        """Write command to ask the instrument to send measured data."""
        self.port.write("FETCh?")
        # self.port.write("READ?")

    def read_result(self) -> None:
        """Read the measured data from a buffer that was requested during 'request_result'."""
        # When using FETCh?, the response is a comma-separated list of values:
        # voltage, current, resistance, time_stamp, status code
        results = self.port.read()
        values = results.split(",")
        self.measured_voltage = float(values[0])
        self.measured_current = float(values[1])

        if self.measured_voltage >= 9.9E37:
            self.measured_voltage = float("nan")
        if self.measured_current >= 9.9E37:
            self.measured_current = float("nan")

        status_int = int(float(values[4]))
        # Extract 24 bits
        bits = [(status_int >> i) & 1 for i in range(24)]
        status_bits = {
            0: "Over range",
            # 1: "Filter enabled",  # no error
            3: "In compliance",  # 2 is not used
            4: "Over voltage protection reached",
            16: "In range compliance"
        }
        for bit_index, description in status_bits.items():
            if bits[bit_index]:
                print(f"Measurement status: {description}")

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.measured_voltage, self.measured_current]
    
    # Wrapped Functions

    def get_identification(self) -> str:
        """Get the instrument identification string (*IDN?)."""
        return str(self.port.query("*IDN?"))

    def set_measurement_functions(self, functions: list[str]) -> None:
        """Set the measurements: VOLT, CURR, RES."""
        for func in functions:
            if func not in ["VOLT", "CURR", "RES"]:
                raise ValueError(f"Invalid measurement function: {func}")
        # functions must be set as comma separated with quotes "func1","func2"
        func_str = ",".join([f'"{func}"' for func in functions])
        self.port.write(f":SENSe:FUNCtion:ON {func_str}")

    def set_voltage_measurement_range(self, range_value: str = "Auto") -> None:
        """Set the voltage measurement range."""
        if range_value not in self.voltage_measurement_ranges:
            msg = f"Invalid voltage range: {range_value}. Valid ranges are: {list(self.voltage_measurement_ranges.keys())}"
            raise ValueError(msg)

        if range_value == "Auto":
            self.port.write(f":SENSe:VOLTage:RANGe:AUTO ON")
        else:
            self.port.write(f":SENSe:VOLTage:RANGe {self.voltage_measurement_ranges[range_value]}")

    def set_current_measurement_range(self, range_value: str = "Auto") -> None:
        """Set the current measurement range."""
        if range_value not in self.current_measurement_ranges:
            msg = f"Invalid current range: {range_value}. Valid ranges are: {list(self.current_measurement_ranges.keys())}"
            raise ValueError(msg)

        if range_value == "Auto":
            self.port.write(f":SENSe:CURRent:RANGe:AUTO ON")
        else:
            self.port.write(f":SENSe:CURRent:RANGe {self.current_measurement_ranges[range_value]}")

    def set_measurement_speed(self, mode: str, nplc: float) -> None:
        """Set the measurement speed in NPLC."""
        if nplc > 10 or nplc < 0.01:
            raise ValueError("NPLC must be between 0.01 and 10")
        if mode not in ["VOLT", "CURR"]:
            raise ValueError("Mode must be 'VOLT' or 'CURR'")
        self.port.write(f":SENSe:{mode}:NPLCycles {nplc}")

    def output_on(self) -> None:
        """Turn the instrument output on (:OUTPut:STATe ON)."""
        self.port.write(":OUTPut:STATe ON")

    def output_off(self) -> None:
        """Turn the instrument output off."""
        self.port.write(":SOURce1:CLEar:IMMediate")

    # Sourcing
    def set_voltage(self, value: float) -> None:
        """Set source voltage level (V-Source). Uses SOURce:VOLTage:LEVel."""
        self.port.write(f":SOURce:VOLTage:LEVel {value}")

    def set_current(self, value: float) -> None:
        """Set source current level (I-Source). Uses SOURce:CURRent:LEVel."""
        self.port.write(f":SOURce:CURRent:LEVel {value}")

    def set_compliance_voltage(self, voltage_limit: float) -> None:
        """When sourcing current, set voltage compliance (SOURce:VOLTage:LEVel:PROTection or SENSe:VOLT:PROT?).
        Using SENSe:VOLTage:PROTection is common for SCPI-capable SourceMeters.
        """
        # Many Keithley instruments use :SOURce:VOLTage:LEVel and :SENSe:VOLTage:PROTection; try the SENSe form first.
        self.port.write(f":SENSe:VOLTage:PROTection {voltage_limit}")

    def set_compliance_current(self, current_limit: float) -> None:
        """When sourcing voltage, set current compliance (SOURce:CURRent:LEVel:PROTection or SENSe:CURR:PROT?)."""
        self.port.write(f":SENSe:CURRent:PROTection {current_limit}")

    # Measurement wrappers
    def measure_voltage(self) -> float:
        """Measure DC voltage using :MEASure:VOLTage?"""
        resp = self.port.query(":MEASure:VOLTage:DC?")
        return float(resp)

    def measure_current(self) -> float:
        """Measure DC current using :MEASure:CURRent?"""
        resp = self.port.query(":MEASure:CURRent:DC?")
        return float(resp)

    def measure_resistance(self) -> float:
        """Measure resistance using :MEASure:RESistance?"""
        resp = self.port.query(":MEASure:RESistance?")
        return float(resp)

    def read_measurement(self) -> float:
        """
        Use :READ? to trigger a source/measure and return numeric value.
        :READ? typically returns a comma-separated list (value, unit, status...).
        Here we read the first numeric value from the response.
        """
        raw = self.port.query(":READ?")
        # parse the first token that looks like a float
        for token in raw.replace(",", " ").split():
            try:
                return float(token)
            except Exception:
                continue
        # couldn't parse numeric value; raise error
        raise RuntimeError(f"Could not parse numeric measurement from response: '{raw}'")

    def wait_for_complete(self) -> None:
        """Waits for the operation queue to be completed."""
        self.port.query("*OPC?")