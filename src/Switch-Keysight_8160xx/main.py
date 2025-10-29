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
# * Module: Switch
# * Instrument: Keysight 8160xx

from __future__ import annotations

import struct
import time

import contextlib
import numpy as np

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keysight 8160xx Laser module."""

    description = """Driver for the Keysight 8160xx Laser module. Very close to the Keysight N777x driver.
    Lambda logging does continuous wavelength sweeps with data acquisition of the wavelength at each step.
    Changing the scan speed may change the allowed wavelength range. Unfortunately, the device does not report if the
    scan range is invalid after changing the speed. Check the allowed wavelength range after changing the speed on the
    device screen.
    """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "8160xx"  # short name will be shown in the sequencer

        self.variables = ["Wavelength", "Power"]
        self.units = ["nm", "W"]  # will be overwritten in get_GUIparameter
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["GPIB"]

        # Measurement parameters
        self.slot: int = 0
        self.output_path: str = "1"  # 1 = low power/high sens, 2 = high power
        self.output_paths_dict = {
            "High Power": "HIGHpower",
            "Low SSE": "LOWSse",
            "Both (High Power regulated)": "BHRegulated",
            "Both (Low SSE regulated)": "BLRegulated",
        }

        # Power
        self.power_level: str = ""
        self.power_units = {
            "dBm": 1,  # default
            "W": 1,
            "mW": 1e-3,  # instrument doesnt directly support mW
        }
        self.power_unit: str = ""
        self.power_min: float = -1  # in current unit
        self.power_max: float = -1  # in current unit

        # Wavelength
        self.wavelength: str = ""
        self.wavelength_unit: str = ""
        self.wavelength_max: float = -1  # in nm
        self.wavelength_min: float = -1  # in nm

        # Measurement variables
        self.sweep_mode: str = "None"
        self.measured_power: float = -1
        self.measured_wavelength: float | np.array = -1

        # List mode
        self.list_mode: bool = False
        self.list_start: float = 0.0  # Start of the list in nm
        self.list_stop: float = 0.0  # Stop of the list in nm
        self.list_step: float = 10  # step size in nm
        self.scan_speed: float = 10.0  # Scan speed in nm/s

    def update_gui_parameters(self, parameters: dict) -> dict:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        new_parameters: dict[str, Any] =  {
            "SweepMode": ["None", "Wavelength", "Power"],
            "Slot": 0,
            "Output Path": list(self.output_paths_dict.keys()),
            "Wavelength in nm": "1550.0",
            "Power unit": ["dBm", "W"],
            "Power": "0.0",
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
                del new_parameters["Wavelength in nm"]

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")
        self.sweep_mode = parameters.get("SweepMode", "")

        self.slot = parameters.get("Slot", "")

        self.output_path = parameters.get("Output Path", "Low SSE")
        self.wavelength = parameters.get("Wavelength in nm", "")
        self.power_level = parameters.get("Power", "")
        self.power_unit = parameters.get("Power unit", "dBm")

        if parameters.get("Mode", "Single") == "List":
            # TODO: add exceptions to prevent gui errors while changing
            self.list_mode = True
            self.list_start = float(parameters.get("List Start in nm", "1250"))
            self.list_stop = float(parameters.get("List Stop in nm", "1650"))
            self.list_step = float(parameters.get("List Step in nm", "10"))
            self.scan_speed = float(parameters.get("Scan speed in nm/s", "10"))

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        # Reset / Preset
        self.port.write("*CLS")
        self.port.write(":SYSTem:PRESet")

        self.get_wavelength_range()

    def poweron(self) -> None:
        """Turn on the power."""
        self.turn_on()

    def poweroff(self) -> None:
        """Turn off the power."""
        self.turn_off()

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.set_output_path(self.output_path)
        self.set_power_unit(self.power_unit)

        if self.list_mode:
            if self.sweep_mode == "Wavelength":
                msg = "SweepMe! cannot sweep wavelength if the device does a wavelength sweep."
                raise ValueError(msg)
            self.configure_list_mode()

        if self.sweep_mode != "Power":
            self.set_power(float(self.power_level))

        if self.sweep_mode != "Wavelength" and not self.list_mode:
            self.set_wavelength(float(self.wavelength))

    def configure_list_mode(self) -> None:
        """Configure the device for wavelength sweeps in list mode."""
        # activate trigger connectors (1 = DEFault)
        self.port.write("trigger:configuration 1")
        # Continuous sweep with lambda logging requires laser output trigger to be set to "Step Finished"
        self.port.write(f"trigger{self.slot}:output stf")

        # Laser Lambda Logging settings
        self.port.write("wavelength:sweep:mode continuous")

        # # only 0.5 5 40 nm/s allowed
        self.port.write(f"wavelength:sweep:speed {self.scan_speed}nm/s")
        self.get_wavelength_range()  # range might change depending on scan speed

        for wavelength in [self.list_start, self.list_stop]:
            self.verify_wavelength(wavelength)

        self.port.write(f"wavelength:sweep:start {self.list_start}nm")
        self.port.write(f"wavelength:sweep:step:width {self.list_step}nm")
        self.port.write(f"wavelength:sweep:stop {self.list_stop}nm")
        self.port.write("wavelength:sweep:cycles 1") # Set the number of cycles

        # Check if device accepts the settings
        status = self.port.query("wav:swe:chec?")
        if "OK" not in status:
            msg = f"Laser sweep configuration not accepted by the device. Status: {status}"
            raise ValueError(msg)

        # turn on lambda logging for the laser. Important to allow readout of wavelength data afterwards
        self.port.write(f"sour{self.slot}:wav:swe:llog ON")

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'.

        If the device is in list mode, it should only set the power
        """
        value = float(self.value)

        if self.sweep_mode.startswith("Wavelength"):
            self.set_wavelength(value)
        elif self.sweep_mode.startswith("Power"):
            self.set_power(value)

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        if self.list_mode:
            self.port.write(f":sour{self.slot}:wav:swe START")
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
        # TODO: Check if this is a good formula
        timeout_s = max(expected_time * 2, 15)

        while True:
            # the status is returned with a leading '+'
            status = self.port.query(f"source{self.slot}:wav:sweep:state?")[1]

            if status == "0":
                # Sweep finished successfully
                break

            if self.is_run_stopped():
                break

            if timeout_s <= 0:
                msg = f"Sweep did not finish within the timeout period of {max(expected_time * 2, 15)}s."
                raise TimeoutError(msg)

            time.sleep(0.1)
            timeout_s -= 0.1

    def get_lambda_logging_data(self) -> np.ndarray:
        """Get the lambda logging data in nm after a sweep in list mode.

        Data is returned from the device as a binary stream that contains each wavelength step of the lambda logging
        operation
        Each binary block is an 8-byte long double in Intel byte order, therefore we use read_raw()
        """
        self.port.write(f"sour{self.slot}:read:data? llog")
        raw_data = self.port.port.read_raw()

        # Strip header if any (IEEE 488.2 format block: starts with '#' and size header)
        if raw_data[0:1] == b"#":
            header_len = int(raw_data[1:2])
            num_bytes = int(raw_data[2:2+header_len])
            data = raw_data[2+header_len:2+header_len+num_bytes]
        else:
            msg = "Lambda logging data does not start with a header. This is unexpected."
            raise ValueError(msg)

        # Parse the binary data: each value is an 8-byte little-endian double
        num_values = len(data) // 8
        return np.array(list(struct.unpack("<" + "d"*num_values, data))) * 1E9

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [
            self.measured_wavelength,
            self.measured_power,
        ]

    def get_wavelength(self) -> float:
        """Get the current wavelength in nm."""
        return float(self.port.query(f"SOURce{self.slot}:WAVelength?")) * 1e9

    # --- Helper functions ---

    def set_wavelength(self, wavelength_nm: float) -> None:
        """Set the wavelength in nm."""
        self.verify_wavelength(wavelength_nm)
        self.port.write(f"SOURce{self.slot}:WAVelength {wavelength_nm}NM")

    def get_wavelength_range(self) -> tuple[float, float]:
        """Get the allowed laser wavelength range in nm."""
        self.wavelength_min = float(self.port.query(f"source{self.slot}:wav? min")) * 1e9
        self.wavelength_max = float(self.port.query(f"source{self.slot}:wav? max")) * 1e9
        return self.wavelength_min, self.wavelength_max

    def verify_wavelength(self, wavelength_nm: float) -> None:
        """Check if the given wavelength in nm is supported by the device."""
        if self.wavelength_max <= 0 or self.wavelength_min <= 0:
            self.get_wavelength_range()

        if not self.wavelength_max >= wavelength_nm >= self.wavelength_min:
            msg = (f"Invalid wavelength {wavelength_nm} nm not in instrument range "
                   f"[{round(self.wavelength_min)} nm, {round(self.wavelength_max)} nm]")
            raise ValueError(msg)

    def set_power(self, power: float) -> None:
        """Set the power in dBm or W depending on set_power_unit."""
        if power <= 0:
            msg = f"Invalid power {power} {self.power_unit}. The device does not support power levels <= 0."
            raise ValueError(msg)

        if self.power_max <= 0 or self.power_min <= 0:
            self.get_power_range()

        if not self.power_max >= power >= self.power_min:
            msg = f"Invalid power {power} {self.power_unit} not in instrument range [{self.power_min} {self.power_unit}, {self.power_max} {self.power_unit}]"
            raise ValueError(msg)

        self.port.write(f"SOURce{self.slot}:POWer:LEVel:IMMediate:AMPLitude {power}")
        set_power = self.get_power()
        if abs(set_power - power) / abs(power) > 0.05:
            msg = (f"Set power {power} {self.power_unit} differs from readback power {set_power} {self.power_unit} by "
                   f"more than 5%. Check attenuator settings.")
            print(msg)

    def get_power(self) -> float:
        """Get the output power in the current unit.

        The value returned is the actual amplitude that is output, which may be different from the value set for the
        output. If these two figures are not the same, it is indicated in the :STATus:OPERation register
        (see manual page 149)
        """
        # return float(self.port.query(f"SOURce{self.slot}:POWer:LEVel:IMMediate:AMPLitude?"))
        return float(self.port.query(f"sour{self.slot}:pow?"))

    def get_power_range(self) -> tuple[float, float]:
        """Get the allowed laser power range in current unit."""
        self.power_min = float(self.port.query(f"SOURce{self.slot}:POWer:LEVel:IMMediate:AMPLitude? MIN"))
        self.power_max = float(self.port.query(f"SOURce{self.slot}:POW? MAX"))
        return self.power_min, self.power_max

    def set_power_unit(self, unit: str = "DBM") -> None:
        """Set the laser power unit. Options: 'DBM' or 'W'."""
        if unit.upper() not in ["DBM", "W"]:
            msg = f"Invalid power unit '{unit}'. Use 'DBM' or 'W'."
            raise ValueError(msg)
        self.port.write(f"SOURce{self.slot}:POWer:UNIT {unit}")
        # reset power range
        self.get_power_range()

    def set_output_path(self, path: str = "Low SSE") -> None:
        """Set the output path of the tunable laser. Options: 1 (low power high sens) or 2 (high power)."""
        if path not in self.output_paths_dict:
            msg = f"Invalid output path '{path}'. Use {self.output_paths_dict.keys()}."
            raise ValueError(msg)
        self.port.write(f"output{self.slot}:path {self.output_paths_dict[path]}")

    def turn_on(self) -> None:
        """Turn laser output ON."""
        self.port.write(f"OUTPut{self.slot}:STATe 1")

    def turn_off(self) -> None:
        """Turn laser output OFF."""
        self.port.write(f"OUTPut{self.slot}:STATe 0")

    def is_sweeping(self) -> bool:
        """Check if a wavelength sweep is active."""
        state = self.port.query(f"SOURce{self.slot}:WAV:SWEep:STATe?")
        return state.strip() != "0"

    # Currently unused wrapper functions

    def get_identification(self) -> str:
        """Return the identification string of the device."""
        return self.port.query("*IDN?")

