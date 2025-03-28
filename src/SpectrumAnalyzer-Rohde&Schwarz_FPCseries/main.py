# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Rohde&Schwarz FPC Series

from __future__ import annotations

import math

import numpy as np
import pyvisa.errors
from pysweepme import debug
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class for the spectrum analyzer functions of Rohde&Schwarz FPC1000 and FPC1500."""

    description = """
    """

    def __init__(self) -> None:
        """Initialize the Device Class and measurement parameters."""
        super().__init__()

        self.shortname = "FPC Series"  # Works for 1500 and 1000 as well

        self.port_manager = True
        self.port_types = ["GPIB", "TCPIP", "USBTMC"]
        self.port_timeout = 5
        self.port_properties = {
            "timeout": self.port_timeout,
        }

        self.variables = ["Frequency", "Power"]
        self.units = ["Hz", "dbm"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Measurement Parameters
        self.center_frequency: float = 850e6
        self.span: float = 20e6
        self.frequency_start: float = 1e6
        self.frequency_stop: float = 10e6

        self.power_values: np.ndarray = np.array([0] * 1183)  # 1183 is the default number of points
        self.frequency_values: np.ndarray = np.array([0] * 1183)  # 1183 is the default number of points

        self.mode: str = "SAN"
        self.preamp: str = "OFF"
        self.attenuation: float = 0
        self.sweep_count: int = 1
        self.trace_number: int = 1

        self.bandwidth_resolution: float = 100e3
        self.bandwidth_video: float = 100e3
        self.bandwidth_resolution_values: dict[str, float] = {
            "Auto": 0,
            "1 Hz": 1,
            "3 Hz": 3,
            "10 Hz": 10,
            "30 Hz": 30,
            "100 Hz": 100,
            "300 Hz": 300,
            "1 kHz": 1e3,
            "3 kHz": 3e3,
            "10 kHz": 10e3,
            "30 kHz": 30e3,
            "100 kHz": 100e3,
            "200 kHz": 200e3,  # only for resolution, not for video
            "300 kHz": 300e3,
            "1 MHz": 1e6,
            "3 MHz": 3e6,
        }

        self.attenuation_values: dict[str, float] = {
            "Auto": 0,
            "0 dB": 0,
            "5 dB": 5,
            "10 dB": 10,
            "15 dB": 15,
            "20 dB": 20,
            "25 dB": 25,
            "30 dB": 30,
            "35 dB": 35,
            "40 dB": 40,
        }

        self.remote_modes: dict[str, str] = {
            "Spectrum": "SAN",  # why not SPEC???
            "Analog Demodulation": "ADEM",
            "Digital Demodulation": "DDEM",
            "Receiver": "REC",
            # NAN -> Wählt die VNA-Anwendung aus???
        }

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "Frequency label 1": ["Center frequency in Hz:", "Min frequency in Hz:"],
            "Frequency value 1": 5000,
            "Frequency label 2": ["Frequency span in Hz:", "Max frequency in Hz:"],
            "Frequency value 2": 1000,
            "Resolution bandwidth": list(self.bandwidth_resolution_values),
            "Video bandwidth": [bandwidth for bandwidth in self.bandwidth_resolution_values if bandwidth != "200 kHz"],
            "Trace mode integration type": ["Sweep count:"],
            "Trace mode integration": 1,
            # "Mode": list(self.remote_modes),  # Currently not implemented
            "Attenuation": list(self.attenuation_values),
            "Preamplifier": ["On", "Off"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.handle_frequency_input(parameter)

        self.bandwidth_resolution = self.bandwidth_resolution_values[parameter["Resolution bandwidth"]]
        self.bandwidth_video = self.bandwidth_resolution_values[parameter["Video bandwidth"]]

        self.attenuation = self.attenuation_values[parameter["Attenuation"]]
        self.preamp = parameter["Preamplifier"].upper()  # ON or OFF

        self.sweep_count = int(parameter["Trace mode integration"])
        max_sweep_count = 999
        if self.sweep_count < 0 or self.sweep_count > max_sweep_count:
            msg = f"Sweep count must be between 1 and {max_sweep_count}."
            raise ValueError(msg)

        self.trace_number = 1

    def handle_frequency_input(self, parameter: dict) -> None:
        """Calculate the frequency center, span, min, and max from the input values."""
        input_1_type = parameter["Frequency label 1"]
        input_1_value = float(parameter["Frequency value 1"])
        input_2_type = parameter["Frequency label 2"]
        input_2_value = float(parameter["Frequency value 2"])

        if input_1_type == "Center frequency in Hz:":
            self.frequency_center = input_1_value
            if input_2_type == "Frequency span in Hz:":
                self.frequency_span = input_2_value
                self.frequency_min = self.frequency_center - self.frequency_span / 2
                self.frequency_max = self.frequency_center + self.frequency_span / 2
            elif input_2_type == "Max frequency in Hz:":
                self.frequency_max = input_2_value
                self.frequency_span = (self.frequency_max - self.frequency_center) * 2
                self.frequency_min = self.frequency_center - self.frequency_span / 2

        elif input_1_type == "Min frequency in Hz:":
            self.frequency_min = input_1_value
            if input_2_type == "Frequency span in Hz:":
                self.frequency_span = input_2_value
                self.frequency_max = self.frequency_min + self.frequency_span
                self.frequency_center = (self.frequency_min + self.frequency_max) / 2
            elif input_2_type == "Max frequency in Hz:":
                self.frequency_max = input_2_value
                self.frequency_center = (self.frequency_min + self.frequency_max) / 2
                self.frequency_span = self.frequency_max - self.frequency_min

    def initialize(self) -> None:
        """Initialize the device."""
        self.port.write("*CLS")  # clear
        self.port.write("FORMAT:DATA REAL,32")  # data format, binary

    def configure(self) -> None:
        """Configure the device."""
        # Display on, can be switched off for faster operation
        self.port.write("SYST:DISP:UPD ON")

        self.port.write("DET SAMP")  # sampling mode

        # Set measurement mode
        self.port.write(f"INST {self.mode}")

        self.port.write("INIT:CONT OFF")  # switching off continuous trigger
        self.port.write("ABORT")
        self.port.write("*OPC?")
        self.port.read()

        # Set Frequency
        self.port.write(f"FREQ:CENT {self.center_frequency}HZ")

        if self.span == 0:
            debug("Span is 0, device will measure in time domain!")
        self.port.write(f"FREQ:SPAN {self.span}HZ")

        self.port.write("SENS:FREQ:START?")
        self.frequency_start = float(self.port.read())

        self.port.write("SENS:FREQ:STOP?")
        self.frequency_stop = float(self.port.read())

        self.set_bandwidth_resolution(self.bandwidth_resolution)
        self.set_video_bandwidth(self.bandwidth_video)
        self.set_attenuation(self.attenuation)

        # Set Preamplifier
        self.port.write(f"INP:GAIN:STAT {self.preamp}")

        # Set sweep count
        # only works in average trace mode
        # self.port.write(f"SWE:COUN {self.sweep_count}")

    def unconfigure(self) -> None:
        """Turn the display back on after the measurement."""
        self.port.write("SYST:DISP:UPD ON")

    def measure(self) -> None:
        """Start the measurement."""
        # Get sweep time to adjust port timeout
        self.port.write("SWE:TIME?")
        self.sweep_time = float(self.port.read())

        if self.sweep_time > self.port_timeout:
            debug(f"Long Sweep time detected: {self.sweep_time}s")
            max_sweep_time = 15
            if self.sweep_time > max_sweep_time:
                msg = f"Sweep time {self.sweep_time} is longer than max sweep time of {max_sweep_time}, please adjust settings."
                raise Exception(msg)

        self.port.write("INIT:IMM")

    def request_result(self) -> None:
        """Wait for the measurement to be complete."""
        self.port.write("*OPC?")  # This command will return "1" when the measurement is complete

        # Give 50% bonus to calculated sweep time and always round up number of tries
        number_of_tries = math.ceil(self.sweep_time * 1.5 / self.port_timeout)

        for _ in range(number_of_tries):
            try:
                self.port.read()
            except (TimeoutError, pyvisa.errors.VisaIOError):
                continue

    def read_result(self) -> None:
        """Read the measurement results and set them as self.power_values."""
        cmd = f"TRAC:DATA? TRACE{self.trace_number}"
        number_of_pixels = 1183

        # There are three options to retrieve trace data
        # Option 1 works, but uses slow ASCII data format
        # Option 2 would be best option, but there are still problems with reading the bytes correctly.
        # Option 3 works with binary data format, but uses pyisa function instead of functions from PortManager

        # Option 1: works!
        # self.port.write("FORMAT:DATA ASCII")  # data format, binary
        # self.port.write(cmd)
        # answer = self.port.read()
        # results = answer.split(",")
        # results = map(float, results)
        # results = list(results)
        # results = np.array(results)

        # Option 2: does not work yet, problems with byte conversion when reading digits
        # The pysweepme port manager does not support reading bytes yet
        # self.port.write(cmd)
        # digits = self.port.read_raw()
        # # print(digits)
        # digits = 1183
        # n_bytes = int(self.port.read(digits))
        # print(n_bytes)
        # answer = self.port.read_raw(n_bytes)
        # print(answer)
        # results = np.array(struct.unpack("f", answer))

        # Option 3: works!
        results = self.port.port.query_binary_values(cmd, datatype="f", container=np.ndarray)
        self.power_values = results

        points = len(self.power_values)

        # TODO: Check if frequency values are correct
        self.frequency_values = np.linspace(self.frequency_start, self.frequency_stop, points, endpoint=True)

    def call(self) -> list:
        """Return the measurement results."""
        return [self.frequency_values, self.power_values]

    """ Wrapped Functions """

    def set_bandwidth_resolution(self, resolution: float) -> None:
        """Set the bandwidth resolution of the device."""
        if resolution > 0:
            self.port.write(f"BAND {resolution}HZ")
        else:
            self.port.write("BAND:AUTO ON")

    def set_video_bandwidth(self, bandwidth: float) -> None:
        """Set the video bandwidth of the device."""
        if bandwidth > 0:
            self.port.write(f"BAND:VID {bandwidth}HZ")
        else:
            self.port.write("BAND:VID:AUTO ON")

    def set_attenuation(self, attenuation: float) -> None:
        """Set the attenuation of the device."""
        if attenuation > 0:
            self.port.write(f"INP:ATT {attenuation}dB")
        else:
            self.port.write("INP:ATT:AUTO ON")

    """
        Currently not used functions

        # self.port.write("*IDN?")
        # identifier = self.port.read()
        # print("Identification:", identifier)

        # Get current mode
        self.port.write("INST?")
        mode = self.port.read()

        self.port.write("SWE:COUN?")
        sweep_count = int(self.port.read())
        print("Sweep count:", sweep_count)

        self.port.write("SWE:TIME?")
        sweep_time = float(self.port.read())
        print("Sweep time:", sweep_time)

        self.port.write(":UNIT:POWer?")
        power_unit = self.port.read()
        print("Power unit:", power_unit)

        self.port.write(":BWIDth:RESolution?")
        bandwidth_resolution = float(self.port.read())
        print("Bandwidth resolution:", bandwidth_resolution)

        self.port.write("BANDwidth:VIDeo?")
        bandwidth_video = float(self.port.read())
        print("Bandwidth video:", bandwidth_video)

        self.port.write("SYSTem:ERRor:ALL?")
        errors = self.port.read()
        print("Errors:")
        print(errors)
    """
