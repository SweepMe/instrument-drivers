# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2023, 2025 SweepMe! GmbH (sweep-me.net)
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
# * Module: Switch
# * Instrument: Keysight N777x Tunable Laser

from __future__ import annotations

import contextlib
import struct
import time

import numpy as np
from pysweepme import debug
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keysight N777x Tunable Laser Module."""

    description = """
                <h3>Driver for the Keysight N777x Tunable Laser</h3>
                <p>The driver supports wavelength and power sweeps in various units<br></p>
                <p><FONT COLOR="#ff0000"> <b>Safety Warning</b>: the user is responsible for the
                 safe operation of the laser and checking that the laser is in a safe state after
                 each SweepMe! run finishes.</p>
                <p>&nbsp;</p>

                <h4>Parameters</h4>
                <ul>
                    <li>List Mode: If enabled, the laser will perform a wavelength sweep between the start and stop
                    values with the specified step size and scan speed. The laser will output a trigger signal at
                    the end of each wavelength step. The power can be set to a fixed value in this mode.</li>
                    <li>Sweep Mode: Choose between sweeping the wavelength or the power.</li>
                    <li>Wavelength: Set the wavelength in the selected unit. Only used if Sweep Mode is not set to
                    Wavelength and List Mode is disabled.</li>
                    <li>Power Level: Set the power level in the selected unit. Only used if Sweep Mode is not set to Power.</li>
                    <li>Power Unit: Choose between W, mW, and dBm.</li>
                    <li>Wavelength Unit: Choose between nm, µm, mm, m, and pm.</li>
                    <li>The scan speed can only be set to discrete values depending on your device type. Check the
                    manual or the device interface for available speed values.</li>
                </ul>
                """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "N777x"  # short name will be shown in the sequencer
        self.variables = ["Wavelength", "Power"]
        self.units = ["nm", "W"]  # will be overwritten in get_GUIparameter
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Port configuration
        self.port_manager = True
        self.port_types = ["GPIB", "USBTMC", "TCPIP"]
        self.port_properties = {
            "timeout": 10,
            "EOL": "\n",
        }
        self.port_string = ""

        # Power
        self.power_level: float = -1
        self.power_units = {
            "dBm": 1,  # default
            "W": 1,
            "mW": 1e-3,  # instrument doesnt directly support mW
        }
        self.power_unit: str = ""
        self.power_conversion: float = 1
        self.pow_max: float = -1
        self.pow_min: float = -1

        # Wavelength
        self.wavelength: float = -1
        self.wavelength_conversions = {
            "nm": 1e-9,
            "µm": 1e-6,
            "mm": 1e-3,
            "m": 1e0,
            "pm": 1e-12,
        }
        self.wavelength_unit: str = ""
        self.wavelength_conversion: float = 1
        self.wln_max: float = -1
        self.wln_min: float = -1

        # Measurement variables
        self.sweepmode: str = "None"
        self.measured_power: float = -1
        self.measured_wavelength: float | np.ndarray = -1

        # List mode
        self.list_mode: bool = False
        self.list_start: float = 0.0  # Start of the list in nm
        self.list_stop: float = 0.0  # Stop of the list in nm
        self.list_step: float = 10  # step size in nm
        self.scan_speed: float = 10.0  # Scan speed in nm/s
        self.previous_trigger_config: str = "2"  # to restore after list mode, default is 2 (passthrough)

        self.debug_mode: bool = False  # Debug errors and warnings

    def update_gui_parameters(self, parameters: dict) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        new_parameters = {
            "Power level": "0.0",  # default is 0 dBm = 1 mW
            "Power unit": list(self.power_units.keys()),
            "Wavelength": "1550.0",
            "Wavelength unit": list(self.wavelength_conversions.keys()),
            "SweepMode": ["None", "Wavelength", "Power"],
            "Mode": ["Single", "List"],
        }

        if "List" in parameters.get("Mode", "Single"):
            new_parameters.update({
                "List Start in nm": "1250",
                "List Stop in nm": "1650",
                "List Step in nm": "10",
                "Scan speed in nm/s": "10",
            })

            # remove wavelength from parameters
            with contextlib.suppress(KeyError):
                del new_parameters["Wavelength"]
                del new_parameters["Wavelength unit"]

        return new_parameters

    def apply_gui_parameters(self, parameters: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweepmode = parameters.get("SweepMode", "None")
        self.port_string = parameters.get("Port", "")  # auto used by port manager

        self.power_level = float(parameters.get("Power level", "0.0"))
        self.wavelength = float(parameters.get("Wavelength", "1550.0"))
        self.power_unit = parameters.get("Power unit", "W")
        self.power_conversion = self.power_units[self.power_unit]
        self.wavelength_unit = parameters.get("Wavelength unit", "nm")
        self.wavelength_conversion = self.wavelength_conversions[self.wavelength_unit]

        self.units = [self.wavelength_unit, self.power_unit]

        if parameters.get("Mode", "Single") == "List":
            self.list_mode = True
            self.list_start = float(parameters.get("List Start in nm", "1250"))
            self.list_stop = float(parameters.get("List Stop in nm", "1650"))
            self.list_step = float(parameters.get("List Step in nm", "10"))
            self.scan_speed = float(parameters.get("Scan speed in nm/s", "10"))

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.reset()
        self.clear_status()

        self.set_power_unit(self.power_unit)
        self.get_power_range()
        self.get_wavelength_range()

        if not self.check_key_turned():
            msg = "Laser key is in OFF state."
            raise ValueError(msg)

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""
        errors = self.check_errors()
        if errors and self.debug_mode:
            debug("Errors for laser after measurement: ", errors)

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        if self.list_mode:
            if self.sweepmode == "Wavelength":
                msg = "SweepMe! cannot sweep wavelength if the device does a wavelength sweep."
                raise ValueError(msg)
            self.configure_list_mode()

        if self.sweepmode != "Power":
            self.set_power(self.power_level, self.power_unit)

        if self.sweepmode != "Wavelength" and not self.list_mode:
            self.set_wavelength(wavelength_m=self.wavelength * self.wavelength_conversion)

    def unconfigure(self) -> None:
        if self.list_mode:
            # Restore previous trigger configuration, e.g. 2 for passthrough
            self.port.write(f":TRIGger:CONFiguration {self.previous_trigger_config}")

    def configure_list_mode(self) -> None:
        """Configure the device for wavelength sweeps in list mode."""
        # Configure trigger: The Input Trigger Connector is activated, the incoming trigger response for each slot.
        self.configure_trigger_output("STF")  # Trigger when a sweep step finishes

        # Configure list parameters
        # Save the previous trigger configuration to restore it later
        self.previous_trigger_config = self.port.query(":TRIGger:CONFiguration?")
        self.port.write(":TRIGger:CONFiguration 1")  # default
        self.port.write(":sour0:wav:swe:mode CONT")  # Set sweep mode to continuous
        self.set_sweep_cycles(1)
        self.set_sweep_speed(self.scan_speed)
        self.set_sweep_start(self.list_start)
        self.set_sweep_stop(self.list_stop)
        self.set_sweep_step(self.list_step)

        # use lambda logging?
        self.port.write(":sour0:wav:swe:llog ON")

        # Check the sweep parameters
        status = self.port.query(":sour0:wav:swe:chec?")
        if status != "0,OK":
            msg = f"Sweep parameters not set correctly. Status: {status}"
            raise ValueError(msg)

    def poweron(self) -> None:
        """Turn on the device when entering a sequencer branch if it was not already used in the previous branch."""
        self.set_laser_on()

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""
        self.set_laser_off()

    def apply(self) -> None:
        """This function is called if the set value has changed. Applies the new value available as self.value.

        If the device is in list mode, it should only set the power
        """
        value = float(self.value)

        if self.sweepmode == "Wavelength":
            self.set_wavelength(value * self.wavelength_conversion)
        elif self.sweepmode == "Power":
            self.set_power(value, self.power_unit)

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        if self.list_mode:
            self.port.write(":sour0:wav:swe START")
        else:
            self.measured_wavelength = self.get_wavelength()
            self.measured_power = self.get_power()

    def request_result(self) -> None:
        """Wait for the sweep to finish."""
        if self.list_mode:
            self.wait_for_sweep_completion()
            self.measured_wavelength = self.get_lambda_logging_data()
            self.measured_power = self.get_power()

    def wait_for_sweep_completion(self) -> None:
        """Wait until the sweep is completed, the measurement is aborted, or the timeout is reached."""
        # Calculate expected measurement time
        expected_time = (self.list_stop - self.list_start) / self.scan_speed
        timeout_s = expected_time * 2

        while True:
            # the status is returned with a leading '+'
            status = self.port.query(":sour0:wav:swe:stat?")[-1]

            if status == "0":
                # Sweep finished successfully
                break

            if self.is_run_stopped():
                break

            if timeout_s <= 0:
                msg = f"Sweep did not finish within the timeout period of {expected_time * 2}s."
                raise TimeoutError(msg)

            time.sleep(0.1)
            timeout_s -= 0.1

    def get_lambda_logging_data(self) -> np.ndarray:
        """Get the lambda logging data after a sweep in list mode.

        Data is returned from the device as a binary stream that contains each wavelength step of the lambda logging
        operation
        Each binary block is an 8-byte long double in Intel byte order, therefore we use read_raw()
        """
        self.port.write("sour0:read:data? llog")
        raw_data = self.port.port.read_raw()

        # Strip header if any (IEEE 488.2 format block: starts with '#' and size header)
        if raw_data[0:1] == b"#":
            header_len = int(raw_data[1:2])
            num_bytes = int(raw_data[2:2 + header_len])
            data = raw_data[2 + header_len:2 + header_len + num_bytes]
        else:
            msg = "Lambda logging data does not start with a header. This is unexpected."
            raise ValueError(msg)

        # Parse the binary data: each value is an 8-byte little-endian double
        num_values = len(data) // 8
        return np.array(list(struct.unpack("<" + "d" * num_values, data)))

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [
            self.measured_wavelength / self.wavelength_conversion,
            self.measured_power / self.power_conversion,
        ]

    # wrapped communication commands below

    def get_identification(self) -> str:
        """Get the instrument identification string."""
        return self.port.query("*IDN?")

    def reset(self) -> None:
        """Reset the instrument to its default state."""
        self.port.write("*RST")

    def clear_status(self) -> None:
        """Clear the instrument status and error queue."""
        self.port.write("*CLS")

    def get_power(self) -> float:
        """Returns the power in W or dB."""
        response = float(self.port.query("sour0:pow?"))
        error_value = 3.402823E38
        return float("nan") if response == error_value else response

    def get_power_range(self) -> None:
        """Save the power range in mW as self.pow_min and self.pow_max."""
        self.pow_min = float(self.port.query(":sour0:pow? min"))
        self.pow_max = float(self.port.query(":sour0:pow? max"))

    def set_power_unit(self, unit: str = "W") -> None:
        """Set the power unit to W or dBm."""
        if unit.lower() == "mw":
            unit = "w"  # instrument does not support mW directly, use W instead and calculate the conversion in call()
            self.power_conversion = 1e-3
        elif unit.lower() not in ["w", "dbm"]:
            msg = f"Invalid power unit {unit}. Choose either W or DBM."
            raise ValueError(msg)
        self.port.write(f":sour0:pow:unit {unit.lower()}")

    def get_power_unit(self) -> str:
        """Get the current power unit."""
        return self.port.query(":sour0:pow:unit?")

    def set_power(self, power_level: float, unit: str = "W") -> None:
        """Set the power level in W or dBm."""
        if unit not in self.power_units:
            msg = f"Invalid power unit {unit}. Choose from {list(self.power_units.keys())}."
            raise ValueError(msg)
        elif unit == "W":
            unit = "Watt"  # this command requires W written in full

        # Check if the power level is within the allowed range
        if self.pow_max < 0 or self.pow_min < 0:
            self.get_power_range()

        if power_level * self.power_conversion < self.pow_min:
            power_level = "MIN"  # set to minimum if below
            if self.debug_mode:
                debug(f"Warning: Power level {power_level * self.power_conversion} {unit} below minimum {self.pow_min} "
                      f"{unit}, setting to minimum.")

        elif power_level * self.power_conversion > self.pow_max:
            power_level = "MAX"  # set to maximum if above
            if self.debug_mode:
                debug(f"Warning: Power level {power_level * self.power_conversion} {unit} above maximum {self.pow_max} "
                      f"{unit}, setting to maximum.")

        else:
            power_level = f"{power_level} {unit.upper()}"

        self.port.write(f"sour0:pow {power_level}")
        self.power_level = power_level

    def set_wavelength(self, wavelength_m: float) -> None:
        """Set the laser wavelength m."""
        wavelength_m = float(wavelength_m)
        if not self.wln_max >= wavelength_m >= self.wln_min:
            msg = (f"Invalid wavelength {wavelength_m * 1e9:.0f} nm not in instrument range "
                   f"[{self.wln_min * 1e9:.0f} nm ,{self.wln_max * 1e9:.0f} nm]")
            raise ValueError(msg)

        self.port.write(f":sour0:wav {wavelength_m}")
        self.port.query("*OPC?")

        self.wavelength = wavelength_m

    def get_wavelength(self) -> float:
        """Get the laser wavelength in meters."""
        return float(self.port.query(":sour0:wav?"))

    def get_wavelength_range(self) -> tuple[float, float]:
        """Get the allowed laser wavelength range in meters."""
        self.wln_min = float(self.port.query(":sour0:wav? min"))
        self.wln_max = float(self.port.query(":sour0:wav? max"))

        return self.wln_min, self.wln_max

    def turn_key(self, onoff=0, password=1234):
        """Change the state of the laser safety key. WARNING: THIS IS A POSSIBLE SAFETY RISK!"""
        self.port.write(f":LOCK {onoff},{password}")

    def check_key_turned(self) -> bool:
        """Check if the laser safety key is turned."""
        return bool(self.port.query(":LOCK?"))

    def set_laser_on(self) -> None:
        """Switch the laser on."""
        self.port.write("SOUR0:POW:STATE 1")

    def set_laser_off(self) -> None:
        """Switch the laser off."""
        self.port.write("SOUR0:POW:STATE 0")

    def is_laser_on(self) -> bool:
        """Returns True if the laser is on, False if it is off."""
        return bool(int(self.port.query("SOUR0:POW:STATE?")))

    def check_errors(self) -> str:
        """Get error list if any and parse it based on manual."""
        err_count = int(self.port.query(":SYSTem:ERRor:COUNt?"))
        if err_count == 0:
            return ""

        errors = []
        for _ in range(err_count):
            err = self.port.query("SYST:ERR?")
            if not err.startswith("0"):
                errors.append(err)

        return ",".join(errors)

    # List Mode Functions

    def set_sweep_cycles(self, cycles: int = 1) -> None:
        """Set the number of sweep cycles to be performed."""
        if not isinstance(cycles, int) or cycles < 1:
            msg = "Number of cycles must be a positive integer."
            raise ValueError(msg)
        self.port.write(f":sour0:wav:swe:cycl {cycles}")

    def set_sweep_speed(self, speed: float = 10.0) -> None:
        """Sets the speed for continuous sweeping in nm/s."""
        if not isinstance(speed, (int, float)) or speed <= 0:
            msg = "Sweep speed must be a positive number."
            raise ValueError(msg)
        self.port.write(f":sour0:wav:swe:spe {speed}nm/s")

    def set_sweep_start(self, start: float = 1250.0) -> None:
        """Set the start wavelength for the sweep in nm."""
        if not isinstance(start, (int, float)) or start < self.wln_min * 1e9 or start > self.wln_max * 1e9:
            msg = f"Start wavelength must be between {self.wln_min * 1e9:.0f} nm and {self.wln_max * 1e9:.0f} nm."
            raise ValueError(msg)
        self.port.write(f":sour0:wav:swe:star {start}nm")

    def set_sweep_stop(self, stop: float = 1650.0) -> None:
        """Set the stop wavelength for the sweep in nm."""
        if not isinstance(stop, (int, float)) or stop < self.wln_min * 1e9 or stop > self.wln_max * 1e9:
            msg = f"Stop wavelength must be between {self.wln_min * 1e9:.0f} nm and {self.wln_max * 1e9:.0f} nm."
            raise ValueError(msg)
        self.port.write(f":sour0:wav:swe:stop {stop}nm")

    def set_sweep_step(self, step: float = 1.0) -> None:
        """Set the step size for the sweep in nm."""
        if not isinstance(step, (int, float)) or step <= 0:
            msg = "Sweep step size must be a positive number."
            raise ValueError(msg)
        self.port.write(f":sour0:wav:swe:step {step}nm")

    def configure_trigger_output(self, output: str = "STF") -> None:
        """Specifies when an output trigger is generated and arms the module."""
        supported_modes = [
            "DIS",  # Never output a trigger
            "STF",  # Trigger when a sweep step finishes
            "SWF",  # Trigger when sweep cycle finishes
            "SWST",  # Trigger when a sweep cycle starts
        ]
        if output.upper() not in supported_modes:
            msg = f"Invalid output trigger mode {output}. Choose from {supported_modes}."
            raise ValueError(msg)

        self.port.write(f":trig0:outp {output.lower()}")
