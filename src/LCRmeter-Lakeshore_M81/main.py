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
# * Module: LCRmeter
# * Instrument: Lakeshore M81

import time
import math
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for using the VS-10 and CM-10 modules of the
     Lakeshore M81 Synchronous Source Measure System as an LCRmeter."""
    def __init__(self):
        EmptyDevice.__init__(self)

        self.port_manager = True
        self.port_types = ["COM", "GPIB", "TCPIP", "SOCKET"]

        self.port_properties = {
            "baudrate": 921600,
            "EOL": "\n",
            "timeout": 15,
            "TCPIP_EOLwrite": "\n",
            "TCPIP_EOLread": "\n",
            "SOCKET_EOLwrite": "\n",
            "SOCKET_EOLread": "\n",
        }

        # Sweep Parameter
        self.sweepmode = None
        self.stepmode = None

        # Current range limits for the CM-10 in A
        self.measurement_ranges = {
            "Auto": 0.0,  # 0 = Auto
            "100 mA": 100e-3,
            "10 mA": 10e-3,
            "1 mA": 1e-3,
            "100 µA": 100e-6,
            "10 µA": 10e-6,
            "1 µA": 1e-6,
            "100 nA": 100e-9,
            "10 nA": 10e-9,
            "1 nA": 1e-9,
        }

        # Measurement Parameters
        self.src_slot: str = ""     # VS-10 source slot
        self.meas_slot: str = ""    # CM-10 measurement slot

        self.amplitude: float = 0.01  # sine amplitude (peak, V)
        self.frequency: float = 1000.0
        self.offset: float = 0.0
        self.measure_range: float = 0.1  # in A
        self.speed_nplcs = {
            "Fast (0.1 NPLC)": 0.1,
            "Medium (1.0 NPLC)": 1.0,
            "Slow (10.0 NPLC)": 10.0,
        }
        self.nplc: float = 1.0
        self.number_of_cycles: int = 10  # Healthy default of 10 for averaging cycles
        self.x: float = float("nan")
        self.y: float = float("nan")
        self.freq_read: float = float("nan")

        self.Z: complex = complex(float("nan"), float("nan"))

        # --- SweepMe result variables --------------------------------------
        self.variables = ["R", "X", "Frequency", "Voltage bias"]
        self.units = ["Ohm", "Ohm", "Hz", "V"]
        self.plottype = [True] * 4
        self.savetype = [True] * 4

    def update_gui_parameters(self, parameters):
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        gui_parameters = {
            "Channel": ["S1 + M1","S1 + M2","S1 + M3",
                        "S2 + M1","S2 + M2","S2 + M3",
                        "S3 + M1","S3 + M2","S3 + M3",],
            "SweepMode": ["None", "Frequency in Hz", "Voltage bias in V", "AC Voltage level in V"],
            "StepMode": ["None", "Frequency in Hz", "Voltage bias in V",  "AC Voltage level in V"],
            "ValueTypeRMS": ["Voltage RMS in V"],
            "ValueTypeBias": ["Voltage bias in V"],
            "ValueRMS": 0.02,
            "ValueBias": 0.0,
            "Frequency": 1000.0,
            "Integration": list(self.speed_nplcs),
            "Range": list(self.measurement_ranges),
            "Trigger": ["Internal Sync"],
            "Average": list(range(1, 33)),  # maximum of 32 cycles
        }
        return gui_parameters

    def apply_gui_parameters(self, parameter):
        """Update parameter from SweepMe! GUI."""
        channel = parameter.get("Channel")
        if len(channel) == 7:
            self.src_slot = channel[1]  # e.g. "1 for "S1 + M3"
            self.meas_slot = channel[-1]  # e.g. "3 for "S1 + M3"
        self.sweepmode = parameter["SweepMode"]
        self.stepmode = parameter["StepMode"]

        self.amplitude = float(parameter["ValueRMS"])
        self.offset = float(parameter["ValueBias"])
        self.frequency = float(parameter["Frequency"])
        self.nplc = self.speed_nplcs.get(parameter["Integration"], 1.0)
        self.measure_range = self.measurement_ranges.get(parameter["Range"],0.0)
        self.number_of_cycles = int(parameter["Average"])

        self.shortname = f"LCR @ S{self.src_slot} + M{self.meas_slot}"

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def initialize(self):
        # Reset source and measurement modules
        self.port.write(f"SOURce{self.src_slot}:PRESet")
        self.port.write(f"SENSe{self.meas_slot}:PRESet")

    def configure(self) -> None:
        # --- VS-10: sine excitation ---------------------------------------
        self.port.write(f"SOURce{self.src_slot}:FUNCtion:SHAPe SINusoid")  # Shape is always Sine for LCRmeter
        # Amplitude, Frequency and Offset
        if self.sweepmode.startswith("AC Voltage") or self.stepmode.startswith("AC Voltage"):
            self.set_amplitude(0)  # Safe starting condition, sweep-value will be set in apply
        else:
            self.set_amplitude(self.amplitude)
        if self.sweepmode.startswith("Voltage bias") or self.stepmode.startswith("Voltage bias"):
            self.set_offset(0)  # Safe starting condition, sweep-value will be set in apply
        else:
            self.set_offset(self.offset)
        if not (self.sweepmode.startswith("Frequency") or self.stepmode.startswith("Frequency")):
            self.set_frequency(self.frequency)

        # --- CM-10: Lock-In configuration ---------------------------------
        self.port.write(f"SENSe{self.meas_slot}:MODE LIA")  # Mode is always LockIn for LCRmeter
        self.port.write(f"SENSe{self.meas_slot}:LIA:RSOurce S{self.src_slot}")  # Source slot is always reference for LCRmeter
        self.port.write(f"SENSe{self.meas_slot}:LIA:DPHase:AUTO")
        self.set_nplc(self.nplc)
        self.set_range(self.measure_range)
        self.set_average(self.number_of_cycles)


        time.sleep(1)  # wait to stabilize

    def poweron(self):
        # Turn on output
        self.port.write(f"SOURce{self.src_slot}:STATe 1")

    def apply(self) -> None:
        """Apply values."""
        if self.sweepmode != "None":
            sweep_value = float(self.value)
            self.handle_set_value(self.sweepmode, sweep_value)

        if self.stepmode != "None":
            step_value = float(self.stepvalue)
            self.handle_set_value(self.stepmode, step_value)

        # Wait for settling to 0.1% (same as auto-settle in LockIn module)
        self.port.write(f"SENSe{self.meas_slot}:LIA:STIMe?")
        settling_time = self.port.read()
        time.sleep(float(settling_time))

    def measure(self):
        # Lock-In runs continuously; nothing to trigger
        pass

    def read_result(self):
        # Fetch X and Y
        self.port.write(f"FETCh:MULTiple? MX,{self.meas_slot},MY,{self.meas_slot}")
        resp = self.port.read().split(",")

        self.x = float(resp[0])
        self.y = float(resp[1])

        # Fetch lock-in frequency
        self.port.write(f"FETCh:SENSe{self.meas_slot}:LIA:FREQuency?")
        self.freq_read = float(self.port.read())

        # Compute complex impedance
        self.Z = self.calculate_impedance(
            voltage=self.amplitude,
            x=self.x,
            y=self.y
        )

    def call(self):
        if self.Z is None or math.isnan(self.Z.real):
            return [float("nan")] * 4

        return [
            self.Z.real,
            self.Z.imag,
            self.freq_read,
            self.offset,
        ]

    def poweroff(self):
        # Turn off output
        self.port.write(f"SOURce{self.src_slot}:STATe 0")

    """ here wrapped functions start """

    @staticmethod
    def calculate_impedance(voltage: float, x: float, y: float) -> complex:
        """
        Wrapper function to calculate complex impedance Z = V / (X + jY)

        This function intentionally does NOT apply any equivalent circuit model.
        Post-processing (R, C, L extraction) is done in the SweepMe LCR-meter device class.
        """
        current = complex(x, y)

        if abs(current) == 0:
            return complex(float("nan"), float("nan"))

        return voltage / current

    def set_amplitude(self, amplitude: float):
        """Set source amplitude (peak)."""
        self.port.write(f"SOURce{self.src_slot}:VOLTage:LEVel:AMPLitude:RMS {amplitude}")

    def set_offset(self, offset: float):
        """Set voltage offset."""
        self.port.write(f"SOURce{self.src_slot}:VOLTage:LEVel:OFFSet {offset}")

    def set_frequency(self, frequency: float) -> None:
        """Set the frequency in Hz."""
        if not (0.0001 <= frequency <= 100000):
            raise ValueError("Frequency must be between 0.1 mHz and 100 kHz for sine waves.")
        self.port.write(f"SOURce{self.src_slot}:FREQuency:FIXed {frequency}")

    def set_range(self, limit):
        if limit == 0:
            self.port.write(f'SENSe{self.meas_slot}:CURRent:RANGe:AUTO 1')
        else:
            self.port.write(f'SENSe{self.meas_slot}:CURRent:RANGe {limit}')

    def set_nplc(self, nplc):
        if not (600 >= nplc >= 0.01):
            raise ValueError("NPLC must be between 0.01 and 600.00.")
        self.port.write(f'SENSe{self.meas_slot}:NPLCycles {nplc}')

    def set_average(self, number):
        if not (1000000 >= number >= 1):
            raise ValueError("Number of reference cycles must be >= 1 and <= 1,000,000.")
        self.port.write(f"SENSe{self.meas_slot}:LIA:REFerence:CYCLes {number}")

    def handle_set_value(self, mode: str, value: float) -> None:
        """Depending on the mode, set the value."""
        if mode == "Voltage bias in V":
            self.offset = value
            self.set_offset(value)

        elif mode == "AC Voltage level in V":
            self.amplitude = value
            self.set_amplitude(value)

        elif mode == "Frequency in Hz":
            self.frequency = value
            self.set_frequency(value)