# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024-2026 SweepMe! GmbH (sweep-me.net)
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

from __future__ import annotations

from typing import Annotated

import numpy as np
from pysweepme.commands import Range, Selector, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

Seconds = Annotated[float, Unit("s")]
Hertz = Annotated[float, Unit("Hz")]
Volts = Annotated[float, Unit("V")]
Channel = Annotated[int, Selector(), Range(1, 2)]


class Device(EmptyDevice):
    """Simulated Oscilloscope Driver Class.

    This driver returns a simulated sine (Ch1) and cosine (Ch2) wave signal with a frequency of 1 kHz and an amplitude
    of 1 V. Each channel clips the signal to its offset +/- voltage range.

    If a Signal-Simulation_Driver is used at the same time, channel 1 shows its signal instead of the sine.
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

        self.use_simulated_signal: bool = False
        """If True, the driver uses the simulated signal from a Signal-Simulation driver in the same branch."""

    def find_ports(self) -> list[str]:
        """Return dummy port."""
        return ["Simulation Scope"]

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set the GUI parameter for the device."""
        return {
            # Timing:
            "TimeRange": ["Time range in s"],
            "TimeRangeValue": ["1e-3"],
            "SamplingRateType": ["Sampling rate in Hz"],
            "SamplingRate": ["1e6"],
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
        self.port = parameter.get("Port", "Simulation Scope")

        self.time_range = float(parameter["TimeRangeValue"])
        self.sampling_rate_type = parameter["SamplingRateType"]
        self.sampling_rate = float(parameter["SamplingRate"])

        # Return Variables
        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        self.channel1 = parameter["Channel1"]
        if self.channel1:
            self.channel1_range = parameter["Channel1_Range"]
            self.channel1_offset = parameter["Channel1_Offset"]

            self.variables += [parameter["Channel1_Name"]]
            self.units += ["V"]
            self.plottype += [True]  # True to plot data
            self.savetype += [True]  # True to save data

        self.channel2 = parameter["Channel2"]
        if self.channel2:
            self.channel2_range = parameter["Channel2_Range"]
            self.channel2_offset = parameter["Channel2_Offset"]

            self.variables += [parameter["Channel2_Name"]]
            self.units += ["V"]
            self.plottype += [True]  # True to plot data
            self.savetype += [True]  # True to save data

    def configure(self) -> None:
        """Configure the device and convert GUI parameters to their destination formats.

        The conversions live here rather than in initialize() so they are redone on
        every reconfigure() (e.g. a live Control Widget change), where
        get_GUIparameter() has just re-read these values as raw strings.
        """
        if self.channel1:
            self.channel1_range = float(self.channel1_range)
            self.channel1_offset = float(self.channel1_offset)

        if self.channel2:
            self.channel2_range = float(self.channel2_range)
            self.channel2_offset = float(self.channel2_offset)

        # If the Signal-Simulation driver is used in the sequencer, use its signal
        self.use_simulated_signal = "Simulated signal" in self.device_communication

    def call(self) -> list[list[float]]:
        """Generate simulated data."""
        time = self._time_axis()
        data = [time]

        if self.channel1:
            data.append(self._digitize(self._input_signal(1, time), self.channel1_range, self.channel1_offset))

        if self.channel2:
            data.append(self._digitize(self._input_signal(2, time), self.channel2_range, self.channel2_offset))

        return data

    SIGNAL_AMPLITUDE: float = 1.0
    """Amplitude in V of the simulated 1 kHz sine (channel 1) and cosine (channel 2)."""

    def _time_axis(self) -> np.ndarray:
        """Return the sampling times; the number of points is rounded, so floating point steps add no extra point."""
        points = int(round(float(self.time_range) * float(self.sampling_rate)))
        return np.arange(points) / float(self.sampling_rate)

    @staticmethod
    def _digitize(signal: np.ndarray, voltage_range: float, offset: float) -> np.ndarray:
        """Clip the signal to the window offset +/- range, like an overdriven input of a real oscilloscope."""
        return np.clip(signal, offset - voltage_range, offset + voltage_range)

    def _input_signal(self, channel: int, time: np.ndarray) -> np.ndarray:
        """Return the signal in V at the input of a channel, before it is digitized.

        Channel 1 shows the signal of a Signal-Simulation_Driver if one shares it in device_communication. This is
        checked at every acquisition, so the oscilloscope also works on its own and follows a generator that is added
        or removed later.
        """
        shared_signal = None
        if channel == 1:
            shared_signal = self.device_communication.get("Simulated signal")
            self.use_simulated_signal = shared_signal is not None
        if shared_signal is not None:
            # Pass a copy, so a generator can never change the time axis of the oscilloscope.
            return np.asarray(shared_signal(time.copy()), dtype=float) * np.ones_like(time)
        wave = np.sin(time * 2 * np.pi * 1e3) if channel == 1 else np.cos(time * 2 * np.pi * 1e3)
        return self.SIGNAL_AMPLITUDE * wave

    """Communication commands, used e.g. by the SweepMe! Instrument Control.

    Channel 1 shows a 1 kHz sine and channel 2 a 1 kHz cosine, each with an amplitude of 1 V and clipped to the window
    offset +/- voltage range of the channel. If a Signal-Simulation_Driver is connected at the same time, channel 1
    shows its signal instead. The commands do not need 'initialize' or 'configure'.
    """

    @command
    def set_timebase(
        self,
        time_range: Annotated[Seconds, Range(0.0, None)],
        sampling_rate: Annotated[Hertz, Range(0.0, None)],
    ) -> None:
        """Set the acquisition time in s and the sampling rate in Hz. The waveform may have 2 to 1,000,000 points."""
        if time_range <= 0 or sampling_rate <= 0:
            msg = "Time range and sampling rate must be greater than 0."
            raise ValueError(msg)
        points = time_range * sampling_rate
        if not 2 <= points <= 1e6:
            msg = f"Time range and sampling rate give {points:.0f} points, but 2 to 1,000,000 are allowed."
            raise ValueError(msg)
        self.time_range = time_range
        self.sampling_rate = sampling_rate

    @command(returns=("time_range", "sampling_rate"), reads="setpoint")
    def get_timebase(self) -> tuple[Seconds, Hertz]:
        """Return (time range in s, sampling rate in Hz)."""
        return float(self.time_range), float(self.sampling_rate)

    @command(kind="run")
    def set_channel(
        self,
        channel: Channel,
        enabled: bool = True,
        voltage_range: Annotated[Volts, Range(0.0, None)] = 5.0,
        offset: Volts = 0.0,
    ) -> None:
        """Enable or disable a channel and set its voltage range in V and offset in V."""
        if voltage_range <= 0:
            msg = f"Voltage range {voltage_range} V must be greater than 0 V."
            raise ValueError(msg)
        setattr(self, f"channel{channel}", enabled)
        setattr(self, f"channel{channel}_range", voltage_range)
        setattr(self, f"channel{channel}_offset", offset)

    # check_driver: ignore DC012 - checks whether the channel is enabled, not its range
    @command(returns=("time", "voltage"))
    def acquire_waveform(
        self,
        channel: Channel,
    ) -> tuple[list[Seconds], list[Volts]]:
        """Acquire the waveform of an enabled channel and return (time in s, voltage in V) as lists."""
        if not getattr(self, f"channel{channel}"):
            msg = f"Channel {channel} is not enabled. Use 'set_channel' first."
            raise ValueError(msg)
        time = self._time_axis()
        voltage_range = float(getattr(self, f"channel{channel}_range"))
        offset = float(getattr(self, f"channel{channel}_offset"))
        voltage = self._digitize(self._input_signal(channel, time), voltage_range, offset)
        return time.tolist(), voltage.tolist()
