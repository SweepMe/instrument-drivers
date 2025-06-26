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

# SweepMe! driver
# * Module: Temperature
# * Instrument: Thorlabs Series 4000

from __future__ import annotations

from typing import Any

import time
from enum import Enum

from pysweepme.EmptyDeviceClass import EmptyDevice


class PIDState(Enum):
    """Enumeration for PID auto-tuning states."""
    NEVER_RUN = "Never run for this sensor/configuration"
    RUNNING = "Auto-PID currently running"
    CANCELED = "Canceled by user"
    FAILED = "Auto-PID failed"
    FINISHED = "Auto-PID finished successfully"

pid_phase = {
    "0": "Full tuning Auto-PID procedure",
    "1": "Fine tuning Auto-PID procedure",
}


class Device(EmptyDevice):
    """Driver class for Velox Temperature Control."""

    description = """
    <h3>Thorlabs Series 4000</h3>
    <p>E.g. LDC40xx, TED4015, ITC40xx.</p>
    <h4>Parameters</h4>
    <ul>
         <li>Reach Temperature: Set the PID parameters.</li>
    </ul>
    """

    def __init__(self) -> None:
        """Initialize measurement and analysis parameter."""
        EmptyDevice.__init__(self)

        self.shortname = "Series 4000"
        self.variables = ["Temperature"]
        self.units = [""]
        self.plottype = [True]
        self.savetype = [True]

        # Device Communication
        self.port_manager = True
        self.port_types = ["USB", "COM", "GPIB"]
        self.port_properties = {
            "timeout": 5,
            "baudrate": 57600,
            "stopbits": 1,
            "parity": "N",
            "EOL": "\n",
        }
        self.channel: str = "1"

        # Measurement Parameter
        self.sweep_mode: str = "Temperature"
        self.use_reach: bool = True
        self.temperature_units = {
            "C": "C",
            "F": "F",
            "K": "K",
        }
        self.temperature_unit: str = "C"
        self.measure_temperature: bool = True
        self.measured_temperature: float = 0.0

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        new_parameters = {
            "SweepMode": ["Temperature", "None"], #[TemperatureMode.SET_TEMPERATURE.value],
            "TemperatureUnit": list(self.temperature_units.keys()),
            "Channel": ["1", "2"],
            "MeasureT": True,
            "ReachT": True,
        }

        # use_pid = parameters.get("Use PID", False)
        # if use_pid:
        #     new_parameters["PID Gain"] = "1.0"
        #     new_parameters["PID Integral"] = "0.1"
        #     new_parameters["PID Derivative"] = "0.0"
        #     new_parameters["PID Period"] = "1.0"

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Apply the parameters received from the SweepMe GUI or the pysweepme instance to the driver instance."""
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.channel = parameters.get("Channel", "1")

        self.measure_temperature = parameters.get("MeasureT", True)
        self.temperature_unit = self.temperature_units[parameters.get("TemperatureUnit", "C")]
        self.units = [parameters["TemperatureUnit"]]

        self.use_reach = bool(parameters["ReachT"])

    def connect(self) -> None:
        """Establish connection to Velox Software."""
        print(f"Connected to {self.get_identification()}")

    def disconnect(self) -> None:
        """Disconnect from Velox Software."""

    def configure(self) -> None:
        """Configure the device."""
        self.port.wrte("CONF:TEMP")  # Set the device to temperature mode

        # TODO: Add GUI parameters - extend Temperature Module with Parameter Box
        self.set_pid_constants()

    def unconfigure(self) -> None:
        """Unconfigure the device."""
        self.port.write("ABOR")

    def apply(self) -> None:
        """Set the target temperature."""
        if self.sweep_mode == "Temperature":
            self.set_temperature(self.value)

            if self.use_reach:
                self.start_pid_auto_tune()

    def reach(self) -> None:
        """Wait until set temperature is reached."""
        if self.use_reach:
            while True:
                state, phase, loop = self.get_pid_auto_tune_status()

                if state == PIDState.FINISHED:
                    break

                if state in [PIDState.FAILED, PIDState.CANCELED, PIDState.NEVER_RUN]:
                    msg = f"PID auto-tuning failed or was canceled. Current state: {state}"
                    raise RuntimeError(msg)

                if self.is_run_stopped():
                    break

                time.sleep(0.5)

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        self.port.write("INIT")

    def read_result(self) -> None:
        """Read the measured data."""
        self.measured_temperature = float(self.port.write("FETC:TEMP?"))

    def call(self) -> float:
        """Return the current temperature."""
        return self.measured_temperature

    # Wrapper Functions

    def get_identification(self) -> str:
        """Return the device identification string."""
        return self.port.query("*IDN?").strip()

    def get_temperature(self) -> float:
        """Reads the current temperature from given sensor."""
        return float(self.port.query("MEAS:TEMP?"))

    def set_temperature(self, temperature: float) -> None:
        """Sets the target temperature."""
        self.port.write(f"SOUR:TEMP:SET {temperature}")

    def is_temperature_reached(self) -> bool:
        """Reads the thermal Chuck status."""

    def set_temperature_setpoint(self, temperature: float) -> None:
        """Sets the temperature setpoint."""
        self.port.write(f"SOUR{self.channel}:TEMP:SET {temperature}")

    def set_pid_constants(self, gain: float = 1.0, integral: float = 0.1, derivative: float = 0, period: float = 1) -> None:
        """Sets the PID constants for the temperature control.

        The gain value (proportional) is in [A/K], its default value is 1.0. The integral value is in [A/K×s], its
        default value is 0.1. The derivative value is in [A×s/K], its default value is 0. The period value specifies the
        thermal load oscillation period in seconds [s], its default value is 1s.
        """
        self.port.write(f"SOUR:TEMP:LCON:GAIN {gain}; INT {integral}; DER {derivative}; PER {period}")

    def start_pid_auto_tune(self) -> None:
        """Starts the PID auto-tuning procedure."""
        self.port.write(f"SOUR{self.channel}:TEMP:ATUN:INIT")

    def stop_pid_auto_tune(self) -> None:
        """Stops the PID auto-tuning procedure."""
        self.port.write(f"SOUR{self.channel}:TEMP:ATUN:CANC")

    def get_pid_auto_tune_status(self) -> PIDState:
        """Returns the status of the PID auto-tuning procedure."""
        status = self.port.query(f"SOUR{self.channel}:TEMP:ATUN:STAT?").strip()
        state, phase, loop = status.split(",")

        pid_state = {
            "0": PIDState.NEVER_RUN,
            "1": PIDState.RUNNING,
            "2": PIDState.CANCELED,
            "3": PIDState.FAILED,
            "4": PIDState.FINISHED,
        }

        return pid_state[state]
