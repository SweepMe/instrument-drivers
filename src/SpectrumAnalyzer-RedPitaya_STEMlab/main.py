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
# * Module: SpectrumAnalyzer
# * Instrument: Red Pitaya STEMlab (fast analog inputs, FFT computed in the driver)

from __future__ import annotations

import math
import time
from typing import Annotated, Any, Literal

import numpy as np
from pysweepme import Label, Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug

# What the communication commands take and answer (checked by @command on every call)
Channel = Annotated[int, Range(1, 2)]
Decimation = Annotated[int, Range(1, 65536)]  # a power of two
AveragingOn = Annotated[bool, Label("Averaging")]
DataUnits = Annotated[Literal["VOLTS", "RAW"], Label("Data units")]
Gain = Literal["LV", "HV"]
TriggerSource = Annotated[
    Literal["DISABLED", "NOW", "CH1_PE", "CH1_NE", "CH2_PE", "CH2_NE", "EXT_PE", "EXT_NE", "AWG_PE", "AWG_NE"],
    Label("Trigger source"),
]
TriggerLevel = Annotated[float, Unit("V"), Label("Trigger level")]
TriggerDelay = Annotated[int, Unit("samples")]
Samples = Annotated[int, Range(1, 16384)]
Seconds = Annotated[float, Unit("s")]
Window = Literal["Hann", "Hamming", "Blackman", "Flat top", "Rectangular"]
Segments = Annotated[int, Range(1, 64)]
Impedance = Annotated[float, Unit("Ohm")]
Frequencies = Annotated[np.ndarray, Unit("Hz"), Label("Frequency")]
Powers = Annotated[np.ndarray, Unit("dBm"), Label("Power")]


class Device(EmptyDevice):
    """Spectrum analyzer on the fast analog inputs of a Red Pitaya STEMlab.

    The board has no spectrum analyzer commands in its SCPI server - its spectrum analyzer is a
    web application on the C API. This driver therefore uses the acquisition commands of the
    SCPI server ('ACQ:...', the same ones the Scope driver uses) to record a time trace and
    computes the power spectrum itself: a windowed FFT of the buffer, converted to dBm into the
    configured impedance. Frequency range, resolution bandwidth and trace mode of the
    SpectrumAnalyzer module are mapped onto decimation, FFT segment averaging and repeated
    acquisitions.
    """

    def __init__(self) -> None:
        EmptyDevice.__init__(self)

        self.shortname = "STEMlab SA"

        self.variables = ["Frequency", "Power"]
        self.units = ["Hz", "dBm"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # The board is addressed through its SCPI server, a plain TCP socket that terminates
        # every line with CR LF. The port manager opens it, so the generator and scope drivers of
        # the same board share the connection. The port is entered as 'ip:5000'.
        self.port_manager = True
        self.port_types = ["SOCKET"]
        self.port_properties = {
            "SOCKET_EOLwrite": "\r\n",
            "SOCKET_EOLread": "\r\n",
            # A timeout is essential: without it a command the instrument does not know is never
            # answered and the driver would wait forever. It bounds the whole answer, a full
            # 16384-sample data buffer included.
            "timeout": 5,
            "fixed_port": 5000,  # the SCPI server always listens on 5000
        }

        #: ADC sample rate of the STEMlab family before decimation.
        self.base_samplerate = 125e6
        #: Largest decimation the SCPI server accepts.
        self.max_decimation = 65536

        self.windows = {
            "Hann": np.hanning,
            "Hamming": np.hamming,
            "Blackman": np.blackman,
            "Flat top": _flattop,
            "Rectangular": np.ones,
        }
        self.gains = {"Low voltage": "LV", "High voltage": "HV", "LV": "LV", "HV": "HV"}

        # Resolution bandwidth: how many FFT segments the buffer is split into and averaged over
        # (Welch). More segments mean a wider bin, a smoother trace, and the same acquisition time.
        self.rbw_segments = {"Auto (1 segment)": 1, "2 segments": 2, "4 segments": 4,
                             "8 segments": 8, "16 segments": 16}
        self.trace_modes = ["Current", "Max hold", "Min hold", "Average"]

        # GUI parameters, exactly as they arrive from the GUI
        self.gui_parameters: dict[str, Any] = {}

        # Values derived in configure()
        self.channel: int = 1
        self.frequency_min: float = 0.0
        self.frequency_max: float = 1e6
        self.decimation: int = 64
        self.samplerate: float = self.base_samplerate / 64
        self.segments: int = 1
        self.window: str = "Hann"
        self.impedance: float = 50.0
        self.gain: str = "LV"
        self.trace_mode: str = "Current"
        self.repetitions: int = 1
        self.hold_time: float = 0.0
        self.trigger_timeout: float = 5.0
        self.buffersize: int = 16384
        self.has_fill_query: bool = True

        # Results of the last measurement
        self.frequencies: np.ndarray = np.array([])
        self.powers: np.ndarray = np.array([])

    # -- GUI -----------------------------------------------------------------------------------
    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """The fields of the SpectrumAnalyzer module, plus this driver's own ones (they go into
        the module's parameter box): the input, the FFT window, the input range and the
        impedance the dBm refer to."""
        return {
            "Frequency label 1": ["Center frequency in Hz:", "Min frequency in Hz:"],
            "Frequency value 1": 500e3,
            "Frequency label 2": ["Frequency span in Hz:", "Max frequency in Hz:"],
            "Frequency value 2": 1e6,
            "Reference level in dBm": 10,
            "Resolution bandwidth": list(self.rbw_segments),
            "Video bandwidth": ["Auto"],
            "Trace mode": self.trace_modes,
            "Trace mode integration type": ["Repetitions:", "Hold time in s:"],
            "Trace mode integration": 1,
            "Video averaging": False,
            "Channel": ["1", "2"],
            "Window": list(self.windows),
            "Input range": ["Low voltage", "High voltage"],
            "Impedance in Ohm": 50.0,
            "Trigger timeout in s": 5.0,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Keep the selections as they arrive; they are converted in configure(), because this
        can be called with half-edited fields."""
        self.gui_parameters = dict(parameters)
        # The channel is taken over at once, so that the communication commands of an instance
        # created for IN2 address IN2 from the start.
        try:
            self.channel = int(parameters.get("Channel", 1))
        except (TypeError, ValueError):
            self.channel = 1

    def convert_gui_parameters(self) -> None:
        """Turn the GUI selections into numbers and settings, and check them."""
        p = self.gui_parameters
        try:
            self.channel = int(p.get("Channel", 1))
            value_1 = float(p.get("Frequency value 1", 500e3))
            value_2 = float(p.get("Frequency value 2", 1e6))
            self.impedance = float(p.get("Impedance in Ohm", 50.0))
            self.repetitions = 1
            self.hold_time = 0.0
            integration = float(p.get("Trace mode integration", 1) or 1)
            if str(p.get("Trace mode integration type", "Repetitions:")).startswith("Hold"):
                self.hold_time = integration
            else:
                self.repetitions = max(1, int(integration))
            self.trigger_timeout = float(p.get("Trigger timeout in s", 5.0))
        except (TypeError, ValueError):
            msg = "SpectrumAnalyzer-RedPitaya_STEMlab: Please enter numeric values into all number fields."
            raise ValueError(msg) from None

        self.frequency_min, self.frequency_max = self.frequency_range(
            str(p.get("Frequency label 1", "Center frequency in Hz:")), value_1,
            str(p.get("Frequency label 2", "Frequency span in Hz:")), value_2,
        )
        self.segments = self.rbw_segments.get(str(p.get("Resolution bandwidth", "Auto (1 segment)")), 1)
        self.window = str(p.get("Window", "Hann"))
        if self.window not in self.windows:
            msg = f"SpectrumAnalyzer-RedPitaya_STEMlab: Unknown window '{self.window}'."
            raise ValueError(msg)
        self.gain = self.gains.get(str(p.get("Input range", "Low voltage")), "LV")
        self.trace_mode = str(p.get("Trace mode", "Current"))
        if self.trace_mode not in self.trace_modes:
            msg = f"SpectrumAnalyzer-RedPitaya_STEMlab: Unknown trace mode '{self.trace_mode}'."
            raise ValueError(msg)
        if self.channel not in (1, 2):
            msg = "SpectrumAnalyzer-RedPitaya_STEMlab: The channel must be 1 or 2."
            raise ValueError(msg)
        if self.impedance <= 0:
            msg = "SpectrumAnalyzer-RedPitaya_STEMlab: The impedance must be positive."
            raise ValueError(msg)
        self.decimation = self.decimation_for_frequency(self.frequency_max)
        self.samplerate = self.base_samplerate / self.decimation

    @staticmethod
    def frequency_range(label_1: str, value_1: float, label_2: str, value_2: float) -> tuple[float, float]:
        """(f_min, f_max) from the module's two frequency fields, whichever pair was chosen."""
        if label_1.startswith("Center"):
            center = value_1
            span = value_2 if label_2.startswith("Frequency span") else 2 * (value_2 - center)
            f_min, f_max = center - span / 2, center + span / 2
        else:
            f_min = value_1
            f_max = f_min + value_2 if label_2.startswith("Frequency span") else value_2
        if f_max <= f_min:
            msg = "SpectrumAnalyzer-RedPitaya_STEMlab: The maximum frequency must be above the minimum."
            raise ValueError(msg)
        if f_max <= 0:
            msg = "SpectrumAnalyzer-RedPitaya_STEMlab: The maximum frequency must be positive."
            raise ValueError(msg)
        return max(0.0, f_min), f_max

    # -- sequencer ----------------------------------------------------------------------------
    def connect(self) -> None:
        """Check that the SCPI server answers (the socket itself is opened by the port manager)."""
        hint = ("Start the SCPI server on the board (web interface -> Development -> SCPI server) "
                "and enter the port as 'ip:5000'.")
        if self.port is None:
            msg = f"SpectrumAnalyzer-RedPitaya_STEMlab: The connection to the board could not be opened. {hint}"
            raise ConnectionError(msg)
        try:
            self.get_identification()
        except (OSError, TimeoutError) as e:
            msg = (f"SpectrumAnalyzer-RedPitaya_STEMlab: No SCPI server answers at "
                   f"{self.port.port_properties['ID']}. {hint} Error is: {e}.")
            raise ConnectionError(msg) from e

    def configure(self) -> None:
        self.convert_gui_parameters()
        self.has_fill_query = True
        self.reset_acquisition()
        self.set_data_units("VOLTS")
        self.buffersize = self.get_buffer_size()
        self.set_gain(self.channel, self.gain)
        self.set_decimation(self.decimation)
        self.set_averaging(True)
        self.set_trigger_delay(self.buffersize // 2)  # the whole buffer after the trigger
        if self.frequency_max > self.samplerate / 2:
            debug(f"SpectrumAnalyzer-RedPitaya_STEMlab: The maximum frequency {self.frequency_max:g} Hz "
                  f"is above half the sample rate ({self.samplerate / 2:g} Hz); the trace ends there.")
        rbw = self.resolution_bandwidth()
        if self.frequency_max - self.frequency_min < rbw:
            debug(f"SpectrumAnalyzer-RedPitaya_STEMlab: The span is narrower than one FFT bin "
                  f"({rbw:g} Hz); use a lower maximum frequency to get finer bins.")

    def measure(self) -> None:
        """Acquire the trace(s) the trace mode asks for and turn them into a spectrum."""
        spectra: list[np.ndarray] = []
        started = time.time()
        while True:
            frequencies, power = self.get_spectrum(self.channel, self.decimation, self.buffersize,
                                                   self.window, self.segments, self.impedance,
                                                   self.trigger_timeout)
            spectra.append(power)
            if self.is_run_stopped():
                return
            if self.trace_mode == "Current":
                break
            if self.hold_time > 0:
                if time.time() - started >= self.hold_time:
                    break
            elif len(spectra) >= self.repetitions:
                break

        stack = np.vstack(spectra)
        if self.trace_mode == "Max hold":
            power = stack.max(axis=0)
        elif self.trace_mode == "Min hold":
            power = stack.min(axis=0)
        elif self.trace_mode == "Average":
            # power average in the linear domain, then back to dBm
            power = 10 * np.log10(np.mean(10 ** (stack / 10), axis=0))
        else:
            power = stack[-1]

        keep = (frequencies >= self.frequency_min) & (frequencies <= self.frequency_max)
        self.frequencies = frequencies[keep]
        self.powers = power[keep]

    def call(self) -> list:
        return [self.frequencies, self.powers]

    # -- spectrum helpers -----------------------------------------------------------------------
    # acquire_trace and get_spectrum are commands built on the communication commands below. The arithmetic
    # (decimation_for_frequency, resolution_bandwidth, compute_spectrum, get_peak) talks to no instrument, so it is
    # not a command; a script that loads the driver with pysweepme can still use it.

    def decimation_for_frequency(self, frequency_max: float) -> int:
        """The smallest power-of-two decimation whose Nyquist frequency still covers
        'frequency_max' (125 MHz / decimation / 2 >= frequency_max), 1 .. 65536."""
        if frequency_max <= 0:
            return self.max_decimation
        wanted = self.base_samplerate / 2 / frequency_max
        exponent = int(math.floor(math.log2(wanted))) if wanted >= 1 else 0
        return int(min(self.max_decimation, max(1, 2 ** exponent)))

    def resolution_bandwidth(self, decimation: int | None = None, samples: int | None = None,
                             segments: int | None = None) -> float:
        """The width of one FFT bin in Hz for the given (or the configured) settings."""
        decimation = self.decimation if decimation is None else int(decimation)
        samples = self.buffersize if samples is None else int(samples)
        segments = self.segments if segments is None else int(segments)
        return self.base_samplerate / decimation / (samples // segments)

    @command(returns=("trace",), composite=True)
    def acquire_trace(self, channel: Channel, samples: Samples = 16384, timeout: Seconds = 5.0) -> list:
        """One immediate acquisition of an input: start, trigger now, wait for the buffer, read.

        The decimation, gain and trigger delay are whatever is set (see the set_ commands). The
        acquisition is stopped afterwards, also when it fails.
        """
        self.start_acquisition()
        started = time.time()
        try:
            self.set_trigger_source("NOW")  # arms; must come after start_acquisition
            while self.get_trigger_status() != "TD":
                if time.time() - started > timeout:
                    msg = (f"SpectrumAnalyzer-RedPitaya_STEMlab: No trigger within {timeout} s "
                           f"(the trigger source 'NOW' should fire at once).")
                    raise TimeoutError(msg)
                time.sleep(0.005)
            self._wait_for_buffer(started, timeout)
            return self.get_data(channel, samples)
        finally:
            try:
                self.stop_acquisition()
            except OSError:
                debug("SpectrumAnalyzer-RedPitaya_STEMlab: could not stop the acquisition.")

    def _wait_for_buffer(self, started: float, timeout: float) -> None:
        """Wait until the buffer is full after the trigger: by 'ACQ:TRig:FILL?' on OS 2.x, by
        the calculated fill time on ecosystems that do not answer it."""
        fill_time = self.buffersize * self.decimation / self.base_samplerate
        # Asks 'ACQ:TRig:FILL?' itself rather than through get_buffer_filled: an ecosystem without the query answers
        # something else or nothing, which has to be told apart from "not filled yet".
        while self.has_fill_query:
            try:
                answer = self.port.query("ACQ:TRig:FILL?").strip()
            except OSError:
                self.has_fill_query = False
                self.port.clear()
                break
            if answer == "1":
                return
            if answer not in ("0", "1"):
                self.has_fill_query = False
                break
            if time.time() - started > fill_time + timeout:
                msg = (f"SpectrumAnalyzer-RedPitaya_STEMlab: The buffer was not filled within "
                       f"{fill_time + timeout:.1f} s after the trigger.")
                raise TimeoutError(msg)
            time.sleep(0.005)
        time.sleep(max(fill_time - (time.time() - started), 0))

    def compute_spectrum(self, trace: list, samplerate: float, window: str = "Hann",
                         segments: int = 1, impedance: float = 50.0) -> tuple[list, list]:
        """The power spectrum of a voltage trace in dBm into 'impedance'.

        The trace is split into 'segments' equal parts, each windowed and transformed, and the
        powers are averaged (Welch's method). The window is amplitude-corrected, so a sine of
        amplitude A shows as A^2 / (2 R) at its frequency, whatever the window. Returns
        (frequencies in Hz, powers in dBm), from DC to the Nyquist frequency.
        """
        if window not in self.windows:
            msg = f"unknown window '{window}' (have: {', '.join(self.windows)})"
            raise ValueError(msg)
        data = np.asarray(trace, dtype=float)
        segments = max(1, int(segments))
        length = len(data) // segments
        if length < 2:
            msg = f"the trace has {len(data)} samples, too few for {segments} segments"
            raise ValueError(msg)
        taper = self.windows[window](length)
        gain = taper.sum()  # amplitude correction of the window
        power = np.zeros(length // 2 + 1)
        for k in range(segments):
            segment = data[k * length:(k + 1) * length]
            segment = segment - segment.mean()  # the DC bin would otherwise leak into its neighbours
            spectrum = np.fft.rfft(segment * taper)
            amplitude = np.abs(spectrum) * 2 / gain  # peak amplitude of a sine in V
            amplitude[0] /= 2  # DC and Nyquist are not doubled
            if length % 2 == 0:
                amplitude[-1] /= 2
            power += amplitude ** 2 / 2 / impedance  # W of a sine into R
        power /= segments
        power_dbm = 10 * np.log10(np.maximum(power, 1e-30) / 1e-3)
        frequencies = np.fft.rfftfreq(length, 1 / samplerate)
        return frequencies.tolist(), power_dbm.tolist()

    @command(returns=("frequencies", "powers"), composite=True)
    def get_spectrum(self, channel: Channel, decimation: Decimation = 64, samples: Samples = 16384,
                     window: Window = "Hann", segments: Segments = 1, impedance: Impedance = 50.0,
                     timeout: Seconds = 5.0) -> tuple[Frequencies, Powers]:
        """Acquire an input and return its spectrum: (frequencies in Hz, powers in dBm).

        Sets the decimation (sample rate 125 MHz / decimation, the trace spans
        samples * decimation / 125 MHz), acquires 'samples' samples immediately and computes
        the spectrum with compute_spectrum. Gain and data units are left as they are.
        """
        self.set_decimation(decimation)
        self.decimation = int(decimation)
        self.set_trigger_delay(int(samples) // 2)
        trace = self.acquire_trace(channel, samples, timeout)
        frequencies, power = self.compute_spectrum(trace, self.base_samplerate / int(decimation),
                                                   window, segments, impedance)
        return np.asarray(frequencies), np.asarray(power)

    # check_driver: ignore DC004 - arithmetic on a spectrum, it talks to no instrument
    def get_peak(self, frequencies: list, powers: list) -> dict:
        """The strongest bin of a spectrum: {'frequency': Hz, 'power': dBm}."""
        index = int(np.argmax(powers))
        return {"frequency": float(frequencies[index]), "power": float(powers[index])}

    @staticmethod
    def _parse_data(answer: str, channel: int) -> list[float]:
        """Turn the '{v1,v2,...}' answer of a data query into a list of floats.

        If the answer cannot be parsed as numbers, it is parsed again after removing every 'ERR!'
        marker (the server may put it anywhere in the answer, e.g. '{1.0,ERR!,2.0}') and the
        empty fields it leaves, so a single faulty readout does not abort a measurement.
        """
        try:
            return list(map(float, answer.strip("{}\n\r").replace("  ", "").split(",")))
        except ValueError:
            cleaned = answer.strip("{}\n\r").replace("ERR!", "").replace("  ", "")
            data = [float(value) for value in cleaned.split(",") if value.strip()]
            debug(f"SpectrumAnalyzer-RedPitaya_STEMlab: Error while reading the data of channel {channel}.")
            return data

    # -- Communication commands -----------------------------------------------------------------
    # One SCPI command each, declared with pysweepme's @command: the acquisition commands of the board ('ACQ:...'),
    # the same set the Scope driver offers, since a spectrum is an acquisition plus arithmetic. 'channel' is the
    # input, 1 or 2. The acquisition belongs to the board, not to an input: every scope or spectrum analyzer driver
    # instance on the board shares it. Reference:
    # https://redpitaya.readthedocs.io/en/latest/appsFeatures/remoteControl/command_list/commands-acq.html

    @command(hazards="Resets the acquisition settings of the whole board (decimation, trigger, gain of both inputs), "
                     "also those another scope or spectrum analyzer driver instance relies on.")
    def reset_acquisition(self) -> None:
        """Stop the acquisition and reset all acquisition parameters ('ACQ:RST')."""
        self.port.write("ACQ:RST")

    @command
    def start_acquisition(self) -> None:
        """Start the acquisition ('ACQ:START'); the trigger is armed separately."""
        self.port.write("ACQ:START")

    @command
    def stop_acquisition(self) -> None:
        """Stop the acquisition ('ACQ:STOP')."""
        self.port.write("ACQ:STOP")

    @command
    def set_decimation(self, decimation: Decimation) -> None:
        """Set the decimation, a power of two from 1 to 65536 ('ACQ:DEC'); sample rate = 125 MHz / decimation."""
        self.port.write("ACQ:DEC {0}".format(decimation))

    @command(returns=("decimation",), reads="setpoint")
    def get_decimation(self) -> Decimation:
        """Return the decimation."""
        return int(self.port.query("ACQ:DEC?"))

    @command
    def set_averaging(self, enabled: AveragingOn) -> None:
        """Switch averaging of the decimated samples on or off ('ACQ:AVG')."""
        self.port.write("ACQ:AVG {0}".format("ON" if enabled else "OFF"))

    @command(returns=("enabled",), reads="setpoint")
    def get_averaging(self) -> AveragingOn:
        """Return whether the decimated samples are averaged."""
        return self.port.query("ACQ:AVG?").strip().upper() in ("ON", "1")

    @command
    def set_data_units(self, units: DataUnits) -> None:
        """Set the units of the returned data: VOLTS or RAW ('ACQ:DATA:UNITS')."""
        self.port.write("ACQ:DATA:UNITS {0}".format(units))

    @command(returns=("units",), reads="setpoint")
    def get_data_units(self) -> DataUnits:
        """Return the units of the returned data, 'VOLTS' or 'RAW'."""
        return self.port.query("ACQ:DATA:UNITS?")

    @command(returns=("buffer_size",), reads="state")
    def get_buffer_size(self) -> int:
        """Return the size of the data buffer in samples ('ACQ:BUF:SIZE?')."""
        return int(self.port.query("ACQ:BUF:SIZE?"))

    @command
    def set_gain(self, channel: Channel, gain: Gain) -> None:
        """Select the input range an input is calibrated for: LV (+/- 1 V) or HV (+/- 20 V) ('ACQ:SOUR<n>:GAIN').

        Switches nothing in hardware - the range is set by the jumper behind the SMA connector -
        it only selects the calibration.
        """
        self.port.write("ACQ:SOUR{0}:GAIN {1}".format(channel, gain))

    @command(returns=("gain",), reads="setpoint")
    def get_gain(self, channel: Channel) -> Gain:
        """Return the input range setting of an input, 'LV' or 'HV'."""
        return self.port.query("ACQ:SOUR{0}:GAIN?".format(channel))

    @command
    def set_trigger_source(self, source: TriggerSource) -> None:
        """Set the trigger source, which arms the trigger ('ACQ:TRIG'); after start_acquisition().

        Sources: DISABLED, NOW, CH1_PE, CH1_NE, CH2_PE, CH2_NE, EXT_PE, EXT_NE, AWG_PE, AWG_NE.
        """
        self.port.write("ACQ:TRIG {0}".format(source))

    @command(returns=("trigger_status",), reads="state")
    def get_trigger_status(self) -> str:
        """Return the trigger status: 'WAIT' until the trigger fires, 'TD' afterwards."""
        return self.port.query("ACQ:TRIG:STAT?")

    @command
    def set_trigger_level(self, level: TriggerLevel) -> None:
        """Set the trigger level in V ('ACQ:TRIG:LEV')."""
        self.port.write("ACQ:TRIG:LEV {0}".format(level))

    @command(returns=("level",), reads="setpoint")
    def get_trigger_level(self) -> TriggerLevel:
        """Return the trigger level in V."""
        return float(self.port.query("ACQ:TRIG:LEV?"))

    @command
    def set_trigger_delay(self, trigger_delay: TriggerDelay) -> None:
        """Set the trigger delay in samples ('ACQ:TRIG:DLY'): 0 puts the trigger in the middle of
        the buffer, half the buffer size puts it at the start."""
        self.port.write("ACQ:TRIG:DLY {0}".format(trigger_delay))

    @command(returns=("trigger_delay",), reads="setpoint")
    def get_trigger_delay(self) -> TriggerDelay:
        """Return the trigger delay in samples."""
        return int(self.port.query("ACQ:TRIG:DLY?"))

    @command(returns=("buffer_filled",), reads="state")
    def get_buffer_filled(self) -> bool:
        """Return whether the buffer has been filled after the trigger ('ACQ:TRig:FILL?', OS 2.00 and up)."""
        return self.port.query("ACQ:TRig:FILL?").strip() == "1"

    @command(returns=("trace",), reads="last")
    def get_data(self, channel: Channel, samples: Samples) -> list:
        """Return the oldest 'samples' samples of an input's buffer ('ACQ:SOUR<n>:DATA:OLD:N?') -
        the acquired trace, in the units selected with set_data_units."""
        answer = self.port.query("ACQ:SOUR{0}:DATA:OLD:N? {1}".format(channel, samples))
        return self._parse_data(answer, channel)

    @command(returns=("trace",), reads="last")
    def get_buffer(self, channel: Channel) -> list:
        """Return the whole buffer of an input ('ACQ:SOUR<n>:DATA?'), 16384 samples."""
        answer = self.port.query("ACQ:SOUR{0}:DATA?".format(channel))
        return self._parse_data(answer, channel)

    @command(returns=("settings",), reads="state", composite=True)
    def get_settings(self) -> dict:
        """Return the acquisition settings and the spectrum settings derived from them."""
        decimation = self.get_decimation()
        return {
            "data_units": self.get_data_units(),
            "buffer_size": self.get_buffer_size(),
            "decimation": decimation,
            "sample_rate": self.base_samplerate / decimation,
            "frequency_max": self.base_samplerate / decimation / 2,
            "resolution_bandwidth": self.resolution_bandwidth(decimation),
            "averaging": self.get_averaging(),
            "trigger_delay": self.get_trigger_delay(),
            "trigger_status": self.get_trigger_status(),
            "gain_1": self.get_gain(1),
            "gain_2": self.get_gain(2),
        }

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the '*IDN?' string of the board."""
        return self.port.query("*IDN?")

    @command(returns=("system_version",), reads="state")
    def get_system_version(self) -> str:
        """Return the ecosystem version of the board ('SYST:VERS?')."""
        return self.port.query("SYST:VERS?")


def _flattop(length: int) -> np.ndarray:
    """A flat-top window (amplitude-accurate, wide main lobe), the SciPy coefficients."""
    n = np.arange(length)
    a = (0.21557895, 0.41663158, 0.277263158, 0.083578947, 0.006947368)
    x = 2 * np.pi * n / (length - 1) if length > 1 else np.zeros(length)
    return a[0] - a[1] * np.cos(x) + a[2] * np.cos(2 * x) - a[3] * np.cos(3 * x) + a[4] * np.cos(4 * x)
