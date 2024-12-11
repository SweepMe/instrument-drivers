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
# * Instrument: Rohde&Schwarz RTX

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Logger driver to read out MEAS channels of Rohde&Schwarz Oscilloscope RT(A-X)."""
    description = """
                    <h3>Rohde & Schwarz Oscilloscope Meas Slots</h3>
                    <p>Setup:</p>
                    <ul>
                    <li>Enable remote control at device</li>
                    <li>If use preset, the defined measurement modes from the devices are used.</li>
                    </ul>
                    """

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "RTX"

        # Communication Parameters
        self.port_manager = True
        self.port_types = ["GPIB", "TCPIP", "USB"]
        self.port_properties = {
            "timeout": 20,  # higher timeout if noise is measured, some mode need more time
        }

        # SweepMe return parameters
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        # Device parameters
        self.modes = {
            "None": "NONE",
            "Frequency in Hz": "FREQ",
            "Period time in s": "PER",
            "Peak to peak in V": "PEAK",
            "Maximum peak in V": "UPE",
            "Minimum peak in V": "LPE",
            "Positive pulse count": "PPC",
            "Negative pulse count": "NPC",
            "Rising edge count": "REC",
            "Falling edge count": "FEC",
            "High reference in V": "HIGH",
            "Low reference in V": "LOW",
            "Amplitude in V": "AMPL",
            "Mean in V": "MEAN",
            "RMS in V": "RMS",
            "Rise time in s": "RTIM",
            "Fall time in s": "FTIM",
            "Positive duty cycle in %": "PDCY",
            "Negative duty cycle in %": "NDCY",
            "Positive pulse width in s": "PPW",
            "Negative pulse width in s": "NPW",
            "Cycle mean in V": "CYCM",
            "Cycle RMS in V": "CYCR",
            "STDDev": "STDD",
            "CYCStddev": "CYCS",
            "Delay in s": "DEL",
            "Phase difference in °": "PHAS",
            "Burst width in s": "BWID",
            "Positive overshoot in %": "POV",
            "Negative overshoot in %": "NOV",
        }

        # Measurement places
        self.maximum_measurement_places: int = 6

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        parameters = {
            "Use preset": False,
            "Averaging": False,
        }
        # Each measurement place can be configured with a channel and a mode
        for i in range(1, self.maximum_measurement_places + 1):
            parameters[f"{i}. Place"] = ["None", "CH1", "CH2", "CH3", "CH4"]
            parameters[f"{i}. Mode"] = list(self.modes.keys())

        return parameters

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]

        self.use_preset = bool(parameter["Use preset"])
        self.use_averaging = bool(parameter["Averaging"])

        self.measurement_places = {}
        """Use a dict to have the postion as the place number."""

        if self.use_preset:
            self.variables = [f"Place {n}" for n in range(1, self.maximum_measurement_places + 1)]
            self.units = [""] * self.maximum_measurement_places
            self.plottype = [True] * self.maximum_measurement_places
            self.savetype = [True] * self.maximum_measurement_places

        else:
            for place in range(1, self.maximum_measurement_places + 1):
                channel = parameter[f"{place}. Place"]
                mode = parameter[f"{place}. Mode"]
                if channel != "None" and mode != "None":
                    channel_num = int(channel[-1])
                    self.measurement_places[place] = (channel_num, self.modes[mode])

                    mode_short = mode.split(" in ")[0]
                    self.variables.append(f"{channel} {mode_short}")
                    self.units.append(mode.split(" in ")[-1])
                    self.plottype.append(True)
                    self.savetype.append(True)

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        if self.use_preset:
            self.measurement_places = {}
            for place in range(1, self.maximum_measurement_places + 1):
                command = f"MEAS{place}:SOUR?"
                self.port.write(command)
                source = self.port.read()

                self.port.write(f"MEAS{place}:MAIN?")
                mode = self.port.read()

                # print(f"Place: {place}, Channel: {source}, Mode: {mode}")
                if mode != "NONE":
                    self.measurement_places[place] = (source, mode)

                    self.variables.append(f"{source} {mode}")
                    # TODO: Handle units for each mode
                    self.units.append("")
                    self.plottype.append(True)
                    self.savetype.append(True)

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        # do not use "SYST:PRES" as it will destroy all settings which is in conflict with using 'As is'
        self.port.write("*CLS")

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        for place, (channel, mode) in self.measurement_places.items():
            if not self.use_preset:
                # print(f"Slot: {place}, Channel: {channel}, Mode: {mode}")
                self.select_source(place, channel)
                self.select_measurement_mode(place, mode)

        if self.use_averaging or self.use_preset:
            # Enable statistical evaluation for all places. Place number is irrelevant.
            self.port.write("MEAS1:STAT:ENAB ON")

            for place in self.measurement_places:
                self.reset_statistical_measurement(place)

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""

    def measure(self) -> None:
        """'measure' should be used to trigger the acquisition of new data.

        If all drivers use this function for this purpose, the data acquisition can start almost simultaneously.
        """
        if self.use_averaging or self.use_preset:
            for place in self.measurement_places:
                self.reset_statistical_measurement(place)

    def call(self) -> list[float]:
        """'call' is a mandatory function that must be used to return as many values as defined in self.variables.

        This function can only be omitted if no variables are defined in self.variables.
        """
        measured_results = []
        for place, (channel, mode) in self.measurement_places.items():
            if self.use_averaging:
                measured_results.append(self.get_averaged_measurement(place))
            else:
                measured_results.append(self.get_measurement(place, mode))

        # TODO: Handle missing values
        if self.use_preset and len(measured_results) < self.maximum_measurement_places:
            diff = self.maximum_measurement_places - len(measured_results)
            measured_results += [None] * diff

        return measured_results

    """ Wrapped Functions """

    def select_source(self, place: int, channel: int) -> None:
        """Select the source channel for the measurement place."""
        self.port.write(f"MEAS{place}:SOUR CH{channel}")

    def select_measurement_mode(self, place: int, mode: str) -> None:
        """Select the measurement mode for the measurement place."""
        self.port.write(f"MEAS{place}:MAIN {mode}")

        # activate measurement
        self.port.write(f"MEAS{place}:ENAB ON")

    def reset_statistical_measurement(self, place: int) -> None:
        """Deletes the statistical results of the indicated measurement.

        Starts a new statistical evaluation if the acquisition is running.
        """
        self.port.write(f"MEAS{place}:STAT:RES")

    def get_measurement(self, place: int, mode: str) -> float:
        """Read out the measurement value of the given place."""
        self.port.write(f"MEAS{place}:RES:ACT? {mode}")
        ret = self.port.read()
        # 9.91E+37 is the error code
        return float(ret) if ret != "9.91E+37" else float("nan")

    def get_averaged_measurement(self, place: int) -> float:
        """Read out the averaged measurement value of the given place."""
        self.port.write(f"MEAS{place}:RES:AVG?")
        ret = self.port.read()
        return float(ret) if ret != "9.91E+37" else float("nan")
