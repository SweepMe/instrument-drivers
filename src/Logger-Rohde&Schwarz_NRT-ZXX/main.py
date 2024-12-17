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
# * Module: Logger
# * Instrument: Rohde&Schwarz NRT-ZXX

import time

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Child class to implement functionalities of a measurement device."""

    description = """
                    <h3>Rohde&Schwarz NRT-Z14/44 Directional Power Sensor</h3>
                    <p>Direct control of the sensor via NRT-Z3 adapter.</p>
                    <ul>
                    <li>Average power mode requires carrier frequency.</li>
                    <li>Reverse power mode depends on selected forward measurement. Except for the crest factor, peak
                    envelope power and complementary cumulative distribution function measurements, the command measures
                    the reverse power corresponding to the selected forward measurement</li>
                    </ul>
                    """

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Template"

        # SweepMe return parameters
        self.variables = ["Forward", "Reverse"]
        self.units = ["Unit1", "Unit2"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Communication Parameters
        self.port_types = ["COM"]
        self.port_manager = True
        self.port_string: str = ""
        self.port_properties = {
            "baudrate": 38400,  # default
            "EOL": "\n",
        }

        # Device parameters
        self.averaging_counts = [1, 2, 4, 8, 16, 32, 64, 128, 256]
        self.averaging: int = 1
        self.integration: float = 0.0
        self.carrier_frequency: float = 0.0

        self.forward_modes = {
            "Average power": "AVER",  # needs carrier frequency
            # "Calculated burst average": "CBAV",  # needs BURS:WIDT and BURS:PER
            "Complementary cumulative distribution function": "CCDF",  # Needs correct video bandwidth
            "Crest factor": "CF",  # Needs correct video bandwidth
            "Measured burst average": "MBAV",  # instead of duty cycle needs video bandwidth
            # "Peak envelope power": "PEP",  # needs PEP:HOLD and PEP:TIME
        }
        self.forward_mode: str = "Average power"

        self.reverse_modes = {
            "Reverse power": "POW",
            "Reflection coefficient": "RCO",
            "Return loss": "RL",
            "Standing wave ratio": "SWR",
        }
        self.reverse_mode = "Return loss"

        self.video_bandwidths = {
            "4 kHz": 4e3,
            "200 kHz": 2e5,
            "600 kHz": 6e5,  # only Z14
            "4 MHz": 4e6,  # only Z
        }
        self.video_bandwidth: float = 2e5

        # Measurement results
        self.forward_result: float = 0.0
        self.reverse_result: float = 0.0

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "Forward mode": list(self.forward_modes.keys()),
            "Reverse mode": list(self.reverse_modes.keys()),
            "Carrier frequency in Hz": 0.0,
            "Video bandwidth": list(self.video_bandwidths.keys()),
            "Averaging": self.averaging_counts,
            "Integration time in s": 0.0,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.forward_mode = parameter["Forward mode"]
        self.reverse_mode = parameter["Reverse mode"]
        self.carrier_frequency = float(parameter["Carrier frequency in Hz"])
        self.averaging = int(parameter["Averaging"])
        self.video_bandwidth = self.video_bandwidths[parameter["Video bandwidth"]]
        self.integration = float(parameter["Integration time in s"])

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        # The device starts with max 10s boot mode followed by 7s self test. Afterward it is ready and returns @8E oper
        for _ in range(30):
            self.port.write("APPL")
            ret = self.port.read()
            if ret.startswith("@8E oper"):
                break

            time.sleep(1)
        else:
            msg = "Device not ready"
            raise Exception(msg)

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.port.write("RESET")  # Reset the device
        self.port.read()  # always read out after setting

        if self.forward_mode == "Average power":
            self.set_carrier_frequency(self.carrier_frequency)

        elif self.forward_mode in [
            "Complementary cumulative distribution function",
            "Crest factor",
            "Measured burst average",
        ]:
            self.set_video_bandwidth(self.video_bandwidth)

        # TODO: Check if both are necessary/possible
        if self.integration > 0:
            self.set_integration(self.integration)

        self.set_averaging(self.averaging)

        # Sensor automatically assigns direction
        self.port.write("DIR AUTO")
        self.port.read()

        self.set_forward_mode(self.forward_mode)
        self.set_reverse_mode(self.reverse_mode)

    def measure(self) -> None:
        """'measure' should be used to trigger the acquisition of new data."""
        self.forward_result, self.reverse_result = self.trigger_remote_controlled_measurement()

    def call(self) -> [float, float]:
        """'call' is a mandatory function that must be used to return as many values as defined in self.variables."""
        return self.forward_result, self.reverse_result

    """Wrapper Functions"""

    def set_carrier_frequency(self, frequency: float) -> None:
        """Set the carrier frequency of the device."""
        if float(self.carrier_frequency) > 0:
            self.port.write(f"FREQ {frequency}")
            self.port.read()

    def set_averaging(self, count: int) -> None:
        """Set the averaging count of the device."""
        if count not in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
            msg = f"Invalid averaging count {count}. Must be one of [1, 2, 4, 8, 16, 32, 64, 128, 256]."
            raise ValueError(msg)

        # automatically sets FILT:AVER:MODE to USER
        self.port.write(f"FILT:AVER:COUN {count}")
        self.port.read()

    def set_integration(self, time_s: float) -> None:
        """Set the integration time of the device."""
        min_time = 5e-3
        max_time = 0.1111
        if time_s < min_time or time_s > max_time:
            msg = f"Invalid integration time {time_s}. Must be in range [{min_time}, {max_time}]."
            raise ValueError(msg)

        # automatically sets FILT:INT:MODE to TIME
        self.port.write(f"FILT:INT:TIME {time_s}")
        self.port.read()

    def trigger_remote_controlled_measurement(self) -> [float, float]:
        """Start new measurement and read out result. If averaging is enabled it is used."""
        self.port.write("RTRG")
        ret = self.port.read()
        split_answer = ret.split(" ")

        forward_result = float(split_answer[1])
        reverse_result = float(split_answer[2])
        return forward_result, reverse_result

    def set_forward_mode(self, mode: str) -> None:
        """Set the forward measurement mode of the device."""
        self.port.write(f"FOR:{self.forward_modes[mode]}")
        self.port.read()

    def set_reverse_mode(self, mode: str) -> None:
        """Set the reverse measurement mode of the device."""
        self.port.write(f"REV:{self.forward_modes[mode]}")
        self.port.read()

    def set_video_bandwidth(self, bandwidth: float) -> None:
        """Set the video bandwidth of the device."""
        self.port.write(f"FILT:VID {bandwidth}")
        self.port.read()

    """ Currently not used functions """

    def get_idn(self) -> str:
        """Get the identification string of the device."""
        self.port.write("ID")
        return self.port.read()

    def clear_buffer(self) -> None:
        """Clear the buffer of the device."""
        self.port.write("PURGE")
        self.port.read()

    def start_continuous_measurement(self) -> [float, float]:
        """Start the continues measurement and read out the last result.

        Starts a continuous measurement at a high speed controlled by an internal timer, without any reference to an
        external trigger. Reads the last result. No effect of set averaging.
        """
        self.port.write("FTRG")
        ret = self.port.read()
        split_answer = ret.split(" ")

        forward_result = float(split_answer[1])
        reverse_result = float(split_answer[2])
        return forward_result, reverse_result
