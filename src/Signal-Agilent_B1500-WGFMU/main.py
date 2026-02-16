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
# * Module: Signal
# * Instrument: Agilent B1500

from __future__ import annotations

import time
from typing import Any

import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice
from pywgfmu import wgfmu


class Device(EmptyDevice):
    """Driver for the Agilent B1500."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "B1500"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Timestamp", "Voltage"]
        self.units = ["s", "V"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = False # True
        self.port_types = ["GPIB"]
        self.channel_string: str = "Slot 1, Channel 1"
        self.channel: int = 101
        self.is_master: bool = True

        # Sequence parameters
        self.csv_file_path: str = "Path to file"
        self.measure_events: list[tuple[float, int, float]] = []  # list of tuples (measure_start, points, interval)
        self.time_stamps: np.ndarray = np.array([])
        self.voltages: np.ndarray = np.array([])

        self.end_condition: str = "Repetitions"
        self.end_value: float = 1.0
        self.scaling_mode: str = "No scaling"
        self.scaling_value: float = 1.0

        # Measured values
        self.measured_timestamps: list[float] = []
        self.measured_voltages: list[float] = []

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "SweepMode": ["None"],
            "Waveform": ["Custom"],
            "Channel": "Slot 1, Channel 1",
            "PeriodFrequency": ["Repetitions", "Measurement time in s"],
            "PeriodFrequencyValue": 1.0,
            "AmplitudeHiLevel": ["Amplitude in V", "No scaling"],
            "AmplitudeHiLevelValue": 1.0,
            # "OffsetLoLevel": ['Offset in V', 'Low level in V'],
            # "OffsetLoLevelValue": 0.0,
            # "DelayPhase": ['Delay in s', 'Phase in °'],
            # "DelayPhaseValue": 0.0,
            # "DutyCyclePulseWidth": ['Duty cycle in %', 'Pulse width in s'],
            # "DutyCyclePulseWidthValue": 50.0,
            # "NumberSteps": 1,
            # "RiseTime": 1.0,
            # "FallTime": 1.0,
            # "TimeConstant": 1.0,
            # "OperationMode": ['None'],
            # "Impedance": ['Auto', 'High-Z', '50 Ohm'],
            # "Trigger": ['None', 'External', 'Internal'],
            "ArbitraryWaveformFile": "Path to file",
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")
        self.channel_string = parameters.get("Channel", "")
        # self.sweepmode = parameters.get("SweepMode", "Frequency in Hz")
        # self.waveform = parameters.get("Waveform", "Sine")
        self.end_condition = parameters.get("PeriodFrequency", "Repetitions")
        self.end_value = parameters.get("PeriodFrequencyValue", 1.0)
        self.scaling_mode = parameters.get("AmplitudeHiLevel", "No scaling")
        self.scaling_value = parameters.get("AmplitudeHiLevelValue", 1.0)
        # self.offsetlolevel = parameters.get("OffsetLoLevel", "Offset in V")
        # self.offsetlolevelvalue = parameters.get("OffsetLoLevelValue", 0.0)
        # self.delayphase = parameters.get("DelayPhase", "Delay in s")
        # self.delayphasevalue = parameters.get("DelayPhaseValue", 0.0)
        # self.dutycyclepulsewidth = parameters.get("DutyCyclePulseWidth", "Duty cycle in %")
        # self.dutycyclepulsewidthvalue = parameters.get("DutyCyclePulseWidthValue", 50.0)
        # self.numbersteps = parameters.get("NumberSteps", 1)
        # self.risetime = parameters.get("RiseTime", 1.0)
        # self.falltime = parameters.get("FallTime", 1.0)
        # self.timeconstant = parameters.get("TimeConstant", 1.0)
        # self.operationmode = parameters.get("OperationMode", "None")
        # self.impedance = parameters.get("Impedance", "Auto")
        # self.trigger = parameters.get("Trigger", "None")
        self.csv_file_path = parameters.get("ArbitraryWaveformFile", "Path to file")

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        if self.port_string not in self.device_communication:
            # First instance, load the dll and connect to the device
            wgfmu.load_dll()

            wgfmu.open_session(self.port_string)
            wgfmu.initialize()
            wgfmu.clear()  # clear any previous waveforms and sequences
            self.device_communication[self.port_string] = -1  # will be set to master channel in configure

        # retrieve slot and channel from channel_string
        # expected format: "Slot X, Channel Y"
        try:
            slot_str, channel_str = self.channel_string.split(",")
            slot = int(slot_str.strip().split(" ")[1])
            channel = int(channel_str.strip().split(" ")[1])
            self.channel = wgfmu.create_channel_id(slot, channel)
        except Exception as e:
            msg = f"Expected channel format 'Slot X, Channel Y', got '{self.channel_string}'. Error: {e}"
            raise ValueError(msg)

        wgfmu.connect(self.channel)

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""
        wgfmu.disconnect(self.channel)
        if self.port_string in self.device_communication:
            wgfmu.close_session()
            del self.device_communication[self.port_string]

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.read_csv()

        if self.scaling_mode == "Amplitude in V":
            # scale the voltage values to the specified amplitude while level
            max_voltage = np.max(np.abs(self.voltages))
            if max_voltage != 0:
                self.voltages *= float(self.scaling_value) / max_voltage

        pattern_name = f"sweepme_pattern_{self.channel}"

        if self.time_stamps[0] != 0.0:
            msg = f"Time stamps in the CSV file should start with 0.0, but got {self.time_stamps[0]}."
            raise ValueError(msg)

        wgfmu.create_pattern(pattern_name, self.voltages[0])
        wgfmu.add_vector_array(
            pattern_name,
            time_values=self.time_stamps[1:].tolist(),
            voltage_values=self.voltages[1:].tolist(),
        )

        count = self.calculate_repetitions()
        wgfmu.add_sequence(self.channel, pattern_name, count=count)

        # For long range box, there might be a different mode
        wgfmu.set_operation_mode(self.channel, wgfmu.OperationMode.FASTIV)

        # Add measurement events
        for number, measurement_event in enumerate(self.measure_events):
            measure_start, points, interval = measurement_event
            event_name = f"Event_{self.channel}_{number}"
            wgfmu.set_measure_event(
                pattern_name,
                event=event_name,
                start_time=measure_start,
                points=points,
                interval=interval,
                average=0,
                mode="average",
            )

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        if self.device_communication.get(self.port_string, -1) == self.channel:
            self.device_communication[self.port_string] = -1  # reset master channel when leaving the branch

    def measure(self) -> None:
        """Perform the measurement."""
        master_channel = self.device_communication[self.port_string]
        if master_channel < 0:  # no master channel set yet
            self.is_master = True
            self.device_communication[self.port_string] = self.channel
        elif master_channel == self.channel:
            self.is_master = True
        else:
            self.is_master = False

        if self.is_master:
            wgfmu.execute()

    def request_result(self) -> None:
        """Each channel waits until its status is not 'RUNNING'."""
        while True:
            if self.is_run_stopped():
                break

            status, elapsed_time, estimated_total_time = wgfmu.get_channel_status(self.channel)
            if status != wgfmu.ChannelStatus.RUNNING:
                break

            if elapsed_time > 2 * estimated_total_time:
                msg = f"Measurement is taking much longer than estimated (elapsed: {elapsed_time:.2f}s, estimated total: {estimated_total_time:.2f}s). Stopping measurement."
                raise RuntimeError(msg)

            time.sleep(0.5)

    def read_result(self) -> None:
        """Read the results."""
        completed_points, total_points = wgfmu.get_measure_value_size(self.channel)
        self.measured_timestamps, self.measured_voltages = wgfmu.get_measure_values(self.channel, 0, completed_points)

    def call(self) -> list:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.measured_timestamps, self.measured_voltages]

    # Helper functions

    def read_csv(self) -> None:
        """Read the csv file and extract measurement events, time stamps and voltage values."""
        self.measure_events = []

        with open(self.csv_file_path, "r", encoding="utf-8") as fh:
            number_of_header_lines = 0

            while True:
                next_line = fh.readline().strip()
                number_of_header_lines += 1

                if next_line.startswith("measure_start"):
                    continue

                elif next_line.startswith("time in s"):
                    break

                else:
                    measure_start, points, interval = next_line.split(";")
                    self.measure_events.append([float(measure_start), int(points), float(interval)])

        data = np.genfromtxt(self.csv_file_path, delimiter=";", skip_header=number_of_header_lines)
        self.time_stamps = data[:, 0]
        self.voltages = data[:, 1]

    def calculate_repetitions(self) -> int:
        """Calculate the number of repetitions based on the end condition and end value."""
        if self.end_condition == "Repetitions":
            return int(float(self.end_value))
        elif self.end_condition == "Measurement time in s":  # "Measurement time in s"
            pattern_length_s = self.time_stamps[-1]
            count = float(self.end_value) / pattern_length_s  # round up to next integer
            return int(np.ceil(count))
        else:
            return 1

