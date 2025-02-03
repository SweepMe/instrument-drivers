# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2024-2025 SweepMe! GmbH (sweep-me.net)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Contribution: We like to thank Peter Hegarty (TU Dresden) for providing the initial version of this driver.

# SweepMe! driver
# * Module: Logger
# * Instrument: Tektronix DPOseries


from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class configure and read out measure slots in Tektronix DPO Series Oscilloscopes."""

    description = """
        <h3>Tektronix DPO Series Oscilloscope Slot Measurement</h3>
        <p>This driver allows read out of measurement slots for DPO devices.</p>
        <p>Parameters:</p>
        <ul>
        <li>Count: Number of points measured for one result.</li>
        <li>Weighting: Number of waveforms that are averaged for one point.</li>
        </ul>
    """

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "DPOseries"

        self.port_manager = True
        self.port_types = ["USB", "GPIB", "TCPIP"]
        # self.port_identifications = ['TEKTRONIX,DPO7354C*']

        self.port_properties = {
            "timeout": 5.0,
            "delay": 1.0,
        }

        self.measure_types = {
            "Amplitude": "AMPlitude",
            "Area": "AREa",
            "Burst": "BURst",
            "Cycle area": "CARea",
            "Cycle mean": "CMEan",
            "Cycle rms": "CRMs",
            "Delay": "DELay",
            "Fall": "FALL",
            "Frequency": "FREQuency",
            "High": "HIGH",
            "Histogram hits": "HITS",
            "Low": "LOW",
            "Maximum": "MAXimum",
            "Mean": "MEAN",
            "Median": "MEDian",
            "Minimum": "MINImum",
            "Negative Duty Cycle": "NDUty",
            "Negative edge count": "NEDGECount",
            "Negative overshoot": "NOVershoot",
            "Negative pulse count": "NPULSECount",
            "Negative width": "NWIdth",
            "Peak hits": "PEAKHits",
            "Peak edge count": "PEDGECount",
            "Positive duty cycle": "PDUty",
            "Period": "PERIod",
            "Phase": "PHAse",
            "Peak to peak": "PK2Pk",
            "Positive overshoot": "POVershoot",
            "Positive pulse count": "PPULSECount",
            "Positive width": "PWIdth",
            "Rise time": "RISe",
            "RMS": "RMS",
            "1 sigma histogram": "SIGMA1",
            "2 sigma histogram": "SIGMA2",
            "3 sigma histogram": "SIGMA3",
            "Standard deviation": "STDdev",
            "Waveform count": "WAVEFORMS",
        }

        self.measure_type_units = {
            "Amplitude": "V",
            "Area": "Vs",
            "Burst": "s",
            "Cycle area": "Vs",
            "Cycle mean": "V",
            "Cycle rms": "V",
            "Delay": "s",
            "Fall": "s",
            "Frequency": "Hz",
            "High": "V",
            "Histogram hits": "",
            "Low": "V",
            "Maximum": "V",
            "Mean": "V",
            "Median": "V",
            "Minimum": "V",
            "Negative Duty Cycle": "%",
            "Negative edge count": "",
            "Negative overshoot": "%",
            "Negative pulse count": "",
            "Negative width": "s",
            "Peak hits": "",
            "Peak edge count": "",
            "Positive duty cycle": "%",
            "Period": "s",
            "Phase": "°",
            "Peak to peak": "V",
            "Positive overshoot": "%",
            "Positive pulse count": "",
            "Positive width": "s",
            "Rise time": "s",
            "RMS": "V",
            "1 sigma histogram": "%",
            "2 sigma histogram": "%",
            "3 sigma histogram": "%",
            "Standard deviation": "V",
            "Waveform count": "",
        }
        self.measure_statistics = [
            "Current",
            "Average",
            "Minimum",
            "Maximum",
        ]

        # Measurement Parameters
        self.slot_channels: dict = {}
        """Dict with slot 1-9 as key and the measured channel (1-4) as value."""

        self.slot_measure_types: dict = {}
        """Dict with slot 1-9 as key and the measurement type (Amplitude, ...) as value."""

        self.slot_statistics: dict = {}
        """Dict with slot 1-9 as key and the used statistics mode (Current, Average, Minimum, Maximum) as value."""

        # The device waits for 'weighting' number of waveforms for a single point. The device then calculates the mean/
        # min/max/... of 'count' number of points.
        self.statistics_count: int = 0  # Number of points measured for one result
        self.statistics_weighting: int = 10  # Number of waveforms that are averaged for one point
        self.results: list = []

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        gui_parameter = {
            "Count": "1",
            "Weighting": "10",
        }

        for slot in range(1, 9):
            gui_parameter[" " * slot] = None  # Empty line
            gui_parameter[f"Slot {slot} channel"] = ["None", "1", "2", "3", "4"]
            gui_parameter[f"Slot {slot} measure type"] = ["None", *list(self.measure_types.keys())]
            gui_parameter[f"Slot {slot} statistics"] = ["None", *self.measure_statistics]

        return gui_parameter

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.slot_channels = {}
        self.slot_measure_types = {}
        self.slot_statistics = {}
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        for slot in range(1, 9):
            self.slot_channels[slot] = parameter[f"Slot {slot} channel"]
            self.slot_measure_types[slot] = parameter[f"Slot {slot} measure type"]
            self.slot_statistics[slot] = parameter[f"Slot {slot} statistics"]

            if self.slot_channels[slot] != "None" and self.slot_measure_types[slot] != "None":
                self.variables.append("Ch" + self.slot_channels[slot] + " - " + self.slot_measure_types[slot])
                self.units.append(self.measure_type_units[self.slot_measure_types[slot]])
                self.plottype.append(True)
                self.savetype.append(True)

        self.statistics_count = int(parameter["Count"])
        self.statistics_weighting = int(parameter["Weighting"])

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""

    def configure(self) -> None:
        """Configure the measurement slots."""
        self.set_measure_statistics_mode(True)
        self.set_statistics_weighting(self.statistics_weighting)

        for slot in range(1, 9):
            if self.slot_channels[slot] != "None" and self.slot_measure_types[slot] != "None":
                self.set_measure_state(slot, "ON")

                # sets the measurement type to a measurement place
                measure_type = self.slot_measure_types[slot]
                self.port.write(f"MEASUrement:MEAS{slot}:TYPe {measure_type}")

                # sets the channel to a measurement place
                channel = self.slot_channels[slot]
                self.port.write(f"MEASUrement:MEAS{slot}:SOUrce1 CH{channel}")  # from channel (used for single channel)
                self.port.write(f"MEASUrement:MEAS{slot}:SOUrce2 CH{channel}")  # to channel

            else:
                self.set_measure_state(slot, "OFF")

        self.set_measure_statistics_count(self.statistics_count)

    def measure(self) -> None:
        """Trigger the acquisition of new data.

        Alternative measurement modes are "MEASUrement?" and "MEASUrement:IMMed?".
        """
        # empty list to store the value of each channel
        self.results = []

        # clears the statistics
        self.reset_measurement_statistics()

        # Waiting for all channels to reach enough measured points for statistic analysis
        for slot in range(1, 9):
            if (
                self.slot_channels[slot] == "None"
                or self.slot_measure_types[slot] == "None"
                or self.slot_statistics[slot] in ("None", "Current")  # No need to wait for measurement of current value
            ):
                continue

            while not self.is_run_stopped():
                measured_points = self.get_measurement_count(slot)
                if measured_points >= self.statistics_count:
                    break

    def request_result(self) -> None:
        """Retrieve measured data."""
        for slot in range(1, 9):
            if self.slot_channels[slot] == "None" or self.slot_measure_types[slot] == "None":
                continue

            if self.statistics_count == 1 or self.slot_statistics[slot] == "Current":
                value = self.get_measure_value(slot)
            elif self.slot_statistics[slot] == "Minimum":
                value = self.get_measure_minimum(slot)
            elif self.slot_statistics[slot] == "Maximum":
                value = self.get_measure_maximum(slot)
            else:  # "Average" or any other type
                value = self.get_measure_mean(slot)

            self.results.append(value)

    def call(self) -> [float, float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return self.results

    """ wrapped communication commands """

    def get_identification(self) -> str:
        """Query the device name."""
        self.port.write("*IDN?")  # Query device name
        return self.port.read()

    def reset(self) -> None:
        """Reset the device."""
        self.port.write("*RST")

    def get_acquisition_number(self) -> int:
        """Get the number of acquisitions."""
        self.port.write("ACQ:NUMACQ?")
        answer = self.port.read()
        return int(answer)

    def get_measure_type(self, slot: int) -> str:
        """Get the measurement type of a slot."""
        self.port.write(f"MEASUrement:MEAS{slot}?")
        return self.port.read()

    def get_measure_unit(self, slot: int) -> str:
        """Get the measurement unit of a slot."""
        self.port.write(f"MEASUrement:MEAS{slot}:UNIts?")
        return self.port.read()

    def get_measure_value(self, slot: int) -> float:
        """Get the measurement value of a slot."""
        self.port.write(f"MEASUrement:MEAS{slot}:VALue?")
        answer = self.port.read()
        return float(answer)

    def get_measure_minimum(self, slot: int) -> float:
        """Get the minimum measurement value of a slot."""
        self.port.write(f"MEASUrement:MEAS{slot}:MINImum?")
        answer = self.port.read()
        return float(answer)

    def get_measure_maximum(self, slot: int) -> float:
        """Get the maximum measurement value of a slot."""
        self.port.write(f"MEASUrement:MEAS{slot}:MAXImum?")
        answer = self.port.read()
        return float(answer)

    def get_measure_mean(self, slot: int) -> float:
        """Get the mean measurement value of a slot."""
        self.port.write(f"MEASUrement:MEAS{slot}:MEAN?")
        answer = self.port.read()
        return float(answer)

    def get_measure_standard_deviation(self, slot: int) -> float:
        """Get the standard deviation of a slot."""
        self.port.write(f"MEASUrement:MEAS{slot}:STDdev?")
        answer = self.port.read()
        return float(answer)

    def set_measure_state(self, slot: int, state: (str, bool, int)) -> None:
        """Set the state of a measurement slot."""
        state = self.convert_state_to_string(state)
        self.port.write(f"MEASUrement:MEAS{slot}:STATE {state}")

    @staticmethod
    def convert_state_to_string(state: (str, bool, int)) -> str:
        """Convert a state of type str, bool, or int to a string."""
        if isinstance(state, bool):
            state = "ON" if state else "OFF"

        elif isinstance(state, int):
            if state not in [0, 1]:
                msg = "Only integers 0 and 1 are accepted"
                raise ValueError(msg)
            state = "ON" if state == 1 else "OFF"

        elif isinstance(state, str):
            if state.lower() not in ["on", "off"]:
                msg = "Only ON or OFF are accepted"
                raise ValueError(msg)
            state = state.upper()

        return state

    def set_statistics_weighting(self, weighting: int) -> None:
        """Set the number of waveforms that are averaged for one point. Standard is 10."""
        self.port.write(f"MEASUrement:STATIstics:WEIghting {weighting}")

    def get_measurement_statistics(self) -> str:
        """Get the measurement statistics."""
        self.port.write("MEASUrement:STATIstics?")
        return self.port.read()

    def get_measurement_count(self, slot: int) -> int:
        """Get the number of measurements since the last reset of statistics for given slot."""
        self.port.write(f"MEASU:MEAS{slot}:COUN?")
        return int(self.port.read())

    def reset_measurement_statistics(self) -> None:
        """Reset the measurement statistics."""
        self.port.write("MEASUrement:STATIstics RESET")

    def set_measure_statistics_mode(self, state: (str, bool, int)) -> None:
        """Set the measurement statistics mode on or off."""
        state = self.convert_state_to_string(state)
        self.port.write(f"MEASUrement:STATIstics:MODE {state}")

    def get_measure_statistics_mode(self) -> str:
        """Get the measurement statistics mode."""
        self.port.write("MEASUrement:STATIstics:MODE?")
        return self.port.read()

    def set_measure_statistics_count(self, count: int) -> None:
        """Set the measurement statistics count."""
        self.port.write(f"MEASUrement:STATIstics:WEIghting {count}")

    def get_measure_statistics_count(self) -> int:
        """Get the measurement statistics count."""
        self.port.write("MEASUrement:STATIstics:WEIghting?")
        answer = self.port.read()
        return int(answer)
