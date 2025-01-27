# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH
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
# * Module: Scope
# * Instrument: Simulation Oscilloscope

import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Simulated Oscilloscope Driver Class.

    This driver returns a simulated sine (Ch1) and cosine (Ch2) wave signal with a frequency of 1 kHz.
    """

    def __init__(self) -> None:
        """Initialize the simulated oscilloscope."""
        EmptyDevice.__init__(self)

        self.shortname = "Simulation"

        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        self.sampling_rate_type: str = "Sampling rate in Hz"
        self.sampling_rate = 1e3
        self.time_range: float = 1e-3

        self.channel1: bool = False
        self.channel1_range: float = 5.0
        self.channel1_offset: float = 0.0

        self.channel2: bool = False
        self.channel2_range: float = 5.0
        self.channel2_offset: float = 0.0

    @staticmethod
    def find_ports() -> list[str]:
        """Return dummy port."""
        return ["Simulation Scope"]

    @staticmethod
    def set_GUIparameter() -> dict:  # noqa: N802
        """Set the GUI parameter for the device."""
        return {
            # Timing:
            "TimeRange": ["Time range in s"],
            "TimeRangeValue": 1e-3,
            "SamplingRateType": ["Sampling rate in Hz"],
            "SamplingRate": "1e3",
            # Channels:
            "Channel1": True,
            "Channel2": False,
            "Channel1_Name": "Ch1",
            "Channel2_Name": "Ch2",
            "Channel1_Range": [5.0, 2.0, 1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01],
            "Channel2_Range": [5.0, 2.0, 1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01],
            "Channel1_Offset": 0.0,
            "Channel2_Offset": 0.0,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Get the GUI parameters and choose driver parameters accordingly."""
        self.port = parameter["Port"]

        self.time_range = float(parameter["TimeRangeValue"])
        self.sampling_rate_type = parameter["SamplingRate"]
        self.sampling_rate = float(parameter["SamplingRate"])

        self.channel1 = parameter["Channel1"]
        if self.channel1:
            self.channel1_range = float(parameter["Channel1_Range"])
            self.channel1_offset = float(parameter["Channel1_Offset"])

            self.variables += [parameter["Channel1_Name"]]
            self.units += ["V"]
            self.plottype += [True]  # True to plot data
            self.savetype += [True]  # True to save data

        self.channel2 = parameter["Channel2"]
        if self.channel2:
            self.channel2_range = float(parameter["Channel2_Range"])
            self.channel2_offset = float(parameter["Channel2_Offset"])

            self.variables += [parameter["Channel2_Name"]]
            self.units += ["V"]
            self.plottype += [True]  # True to plot data
            self.savetype += [True]  # True to save data

    def configure(self) -> None:
        """Configure the device."""
        # If the Signal-Simulation driver is used in the sequencer, use its signal
        self.use_simulated_signal = "Simulated signal" in self.device_communication

    def call(self) -> tuple:
        """Generate simulated data."""
        time = np.arange(0, self.time_range, 1 / self.sampling_rate)
        data = [time]

        if self.channel1:
            if self.use_simulated_signal:
                generate_waveform = self.device_communication["Simulated signal"]
                channel_1 = generate_waveform(time)
            else:
                channel_1 = np.sin(time * 2 * np.pi * 1e3) * self.channel1_range + self.channel1_offset
            data.append(channel_1)

        if self.channel2:
            channel_2 = np.cos(time * 2 * np.pi * 1e3) * self.channel2_range + self.channel2_offset
            data.append(channel_2)

        return tuple(data)
