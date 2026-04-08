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
# * Module: Temperature
# * Instrument: Thorlabs Series 4000

from __future__ import annotations

import time
from enum import Enum
from typing import Any

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
    """Driver class Thorlabs Series 4000 temperature controllers."""

    description = """
    <h3>Thorlabs Series 4000</h3>
    <p>E.g. TED4015, ITC40xx. LDC is not supported as it does not allow for direct temperature control.</p>
    <h4>Parameters</h4>
    <ul>
         <li>Reach Temperature: Use the SweepMe! reach temperature feature, which continuously measures the temperature until the target temperature is reached..</li>
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
            "timeout": 1,
            # "baudrate": 57600,
            # "stopbits": 1,
            # "parity": "N",
            # "EOL": "\n",
        }
        self.channel: str = "1"
        self.device_type: str = ""  # "TED" or "ITC"

        # Measurement Parameter
        self.sweep_mode: str = "Temperature"
        self.use_reach: bool = True  # use the SweepMe! reach temperature feature, which continuously measures the temperature until the target temperature is reached.
        self.temperature_units = {
            "°C": "C",
            "°F": "F",
            "K": "K",
        }
        self.temperature_unit: str = "C"
        self.measured_temperature: float = 0.0

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "SweepMode": ["Temperature", "None"],
            "TemperatureUnit": list(self.temperature_units.keys()),
            # "Channel": ["1", "2"],  # Only needed for PID control, which is currently not used
            "ReachT": True,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Apply the parameters received from the SweepMe GUI or the pysweepme instance to the driver instance."""
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.channel = parameters.get("Channel", "1")

        self.temperature_unit = self.temperature_units[parameters.get("TemperatureUnit", "C")]
        self.units = [parameters["TemperatureUnit"]]

        self.use_reach = bool(parameters["ReachT"])

    def connect(self) -> None:
        """Establish connection to device."""
        # In some instances the device does not respond to the first command, so the IDN command is tried multiple times
        for _ in range(4):
            try:
                identification = self.get_identification()
            except Exception:
                pass
            else:
                break

        if "TED" in identification:
            self.device_type = "TED"
        elif "ITC" in identification:
            self.device_type = "ITC"
        else:
            msg = f"Unsupported device type: {identification}. Only TED and ITC series are supported."
            raise RuntimeError(msg)

    def poweron(self) -> None:
        """Switch on the TEC output device."""
        self.set_output_state(True)

    def poweroff(self) -> None:
        """Switch off the TEC output of the device."""
        self.set_output_state(False)

    def configure(self) -> None:
        """Configure the device."""
        self.port.write("CONF:TEMP")  # Set the device to temperature mode
        self.port.write(f"UNIT:TEMP {self.temperature_unit}")  # Possible values: C, F, K

    def unconfigure(self) -> None:
        """Unconfigure the device.

        The 'ABORt' command cancels ongoing measurement operations and returns the device to an idle state.
        Currently unsure if it should be used, as it results in timeout errors sometimes.
        """
        # self.port.write("ABOR")
        # self.wait_for_operation_complete()

    def apply(self) -> None:
        """Set the target temperature."""
        if self.sweep_mode == "Temperature":
            self.set_temperature(self.value)
        self.wait_for_operation_complete()

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        self.port.write("INIT")

    def read_result(self) -> None:
        """Read the measured data."""
        self.measured_temperature = float(self.port.query("FETC:TEMP?"))

    def call(self) -> float:
        """Return the current temperature."""
        return self.measured_temperature

    def get_identification(self) -> str:
        """Return the device identification string."""
        return str(self.port.query("*IDN?").strip())

    # Wrapper Functions

    def set_temperature(self, temperature: float) -> None:
        """Sets the target temperature.

        This corresponds to the TEC Temperature Setpoint (see manual 3.11.5)
        """
        # For TED4000 Series instruments the command suffix is 1 (can be omitted), for ITC4000 Series instruments its 2.
        suffixes = {
            "TED": "1",  # TED4000 Series
            "ITC": "2",  # ITC4000 Series
        }
        if self.device_type not in suffixes:
            msg = f"Unsupported device type: {self.device_type}. Only TED and ITC series are supported."
            raise RuntimeError(msg)

        self.port.write(f"SOUR{suffixes[self.device_type]}:TEMP {temperature}")

    def set_output_state(self, state: bool) -> None:
        """Set the output state of the device.

        Depending on the device type, the temperature control is either denoted as output 2 or without a number.
        """
        channel_num = "2" if self.device_type == "ITC" else ""
        state_command = "ON" if state else "OFF"
        self.port.write(f"OUTPut{channel_num} {state_command}")

    def measure_temperature(self) -> float:
        """Retrieve measured temperature directly.

        LDC Series does not support temperature measurement.
        This command is simple, but does not offer any additional configuration options.
        """
        return float(self.port.query("MEAS:TEMP?"))

    def wait_for_operation_complete(self, timeout: float = 10.0 ) -> bool:
        """Checks the Operation complete query and continues when it returns 1 (completed)."""
        start_time = time.time()
        while not self.is_run_stopped():
            self.port.write("*OPC?")
            time.sleep(0.01)
            complete_status = self.port.read()

            if complete_status == "1":
                return True

            if time.time() - start_time > timeout:
                return False

        return False

    # PID Control Functions - currently not used

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

    def wait_for_pid_auto_tune(self) -> None:
        """Waits for the PID auto-tuning procedure to finish."""
        while not self.is_run_stopped():
            state = self.get_pid_auto_tune_status()

            if state == PIDState.FINISHED:
                break

            if state in [PIDState.FAILED, PIDState.CANCELED, PIDState.NEVER_RUN]:
                msg = f"PID auto-tuning failed or was canceled. Current state: {state}"
                raise RuntimeError(msg)

            time.sleep(0.5)
