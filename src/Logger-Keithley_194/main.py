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
# * Module: Logger
# * Instrument: Keithley 194


from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """<p><strong>Keithley 194 High Speed Voltmeter</strong></p>
                     <p>4.5/3.5 digit voltmeter with up to 1MS/s sampling rate</p>
                     <p>Waveform capture mode not implemented in this Logger module.</p>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "Keithley194Logger"

        self.port_manager = True
        self.port_types = ["GPIB"]

        self.port_properties = {
            "timeout": 3,
            "delay": 0.05,
        }

        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        self.modes = {
            "Average": "F1",
            "True RMS": "F2",
            "Pos. Peak": "F3",
            "Neg. Peak": "F4",
            "Peak-to-Peak": "F5",
            "Standard Deviation": "F6",
            "Integral": "F7",
            "CH1 - CH2": "F20",
            "CH1 / CH2": "F21",
        }

        # this dictionary sets the unit of each mode
        self.mode_units = {
            "Average": "V",
            "True RMS": "V",
            "Pos. Peak": "V",
            "Neg. Peak": "V",
            "Peak-to-Peak": "V",
            "Standard Deviation": "V",
            "Integral": "V^2",
            "CH1 - CH2": "V",
            "CH1 / CH2": "x",
        }

        # this dictionary connects channels to commands. The channels will be displayed in the field 'Channel'
        self.channels = {
            "Channel 1": "C1",
            "Channel 2": "C2",
            "Composite CH1 and CH2": "C3",
        }

        # measuring range
        self.ranges = {
            "Auto": "R0",
            "320 mV": "R1",
            "3.2 V": "R2",
            "32 V": "R3",
            "200 V": "R4",
        }

        # choice of trigger; T26&T27 are executed on X command immediately, T6&T7 on external trigger signal, T20-23 on slope of signal
        self.triggers = {
            "Continuous (int)": "T26",
            "Single (int)": "T27",
            "Continuous (ext)": "T6",
            "Single (ext)": "T7",
            "Continuous (pos. slope)": "T20",
            "Single (pos. slope)": "T21",
            "Continuous (neg. slope)": "T22",
            "Single (neg. slope)": "T23",
        }

        # filter settings
        self.filters = {
            "Off": "P0",
            "500kHz": "P1",
            "50kHz": "P2",
        }

        # coupling
        self.couplings = {
            "DC": "I0",
            "AC": "I1",
            "Ground": "I2",
        }

        # delay
        # self.delays = {
        #    "Delay (samples)": "W0",
        #    "Delay (seconds)": "W1",
        # }

    def update_gui_parameters(self, parameters: dict) -> dict:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        # retrieve currently set "Trigger" setting, default to "Single (int)" if unset
        self.trigger = parameters.get("Trigger", "Single (int)")
        new_parameters = {
            "Function Mode": list(self.modes.keys()),
            "Channel": list(self.channels.keys()),
            "Sampling Rate in S/s": "1E+04",
            "Sampling Time in s": "1E-03",
            "Range": list(self.ranges.keys()),
            "Trigger": list(self.triggers.keys()),
            "Filter": list(self.filters.keys()),
            "Coupling": list(self.couplings.keys()),
            # "Delay Type": list(self.delays.keys()),
            "Delay in s": 0.000,
        }

        if "slope" in self.trigger:
            new_parameters["Trigger Level (V)"] = 0.000

        return new_parameters

    def apply_gui_parameters(self, parameters: dict) -> None:
        """Apply the parameters received from the SweepMe GUI or the pysweepme instance to the driver instance."""
        self.trigger = parameters.get("Trigger", "Single (int)")

        self.channel = parameters.get("Channel", "Channel 1")
        self.mode = parameters.get("Function Mode", "Average")
        self.rate = parameters.get("Sampling Rate in S/s", "1E+04")
        self.samplingtime = parameters.get("Sampling Time in s", "1E-03")
        self.range = parameters.get("Range", "Auto")
        self.trigger = parameters.get("Trigger", "Continuous (int)")
        if "slope" in self.trigger:
            self.triggerlevel = parameters.get("Trigger Level (V)", 0.000)
        self.filter = parameters.get("Filter", "Off")
        self.coupling = parameters.get("Coupling", "DC")
        self.delay = parameters.get("Delay in s", 0.000)
        self.port_string = parameters.get("Port", "")

        # Set variable name, unit, plottype and savetype depending on mode
        self.variables = [self.mode]
        self.units = [self.mode_units[self.mode]]
        self.plottype = [True]
        self.savetype = [True]

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        # K2 is used to enable EOI on GPIB communication and disable the holding of the bus
        self.port.write("K2X")

        # Data output format; sets output to ASCII, 1 reading, no prefix, no suffix
        self.port.write("G1X")

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # Channel

        if self.channel.endswith("1"):
            # if channel 1 is used, set channel 2 to its external trigger to disable it
            self.port.write("C2T7X")
        elif self.channel.endswith("2"):
            # if channel 2 is used, set channel 1 to its external trigger to disable it
            self.port.write("C1T7X")

        # set active channel
        self.port.write("%sX" % self.channels[self.channel])

        # Mode
        self.port.write("%sX" % self.modes[self.mode])

        # Rate
        self.port.write("S1,%sX" % "{:.5E}".format(round(float(self.rate))))

        # Sampling Time (s)
        self.port.write("N1,%sX" % "{:.5E}".format(float(self.samplingtime)))

        # Range
        self.port.write("%sX" % self.ranges[self.range])

        # Filter
        self.port.write("%sX" % self.filters[self.filter])

        # Coupling
        self.port.write("%sX" % self.couplings[self.coupling])

        # Delay
        self.port.write("W1,%sX" % self.delay)

        # reading buffer disabled
        self.port.write("Q0X")

        # set SRQ for "reading done" state
        # self.port.write("M8X")

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        # sets the trigger back to continuous trigger
        self.port.write("T26X")

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        if self.trigger.endswith("(int)") or self.trigger.endswith("(ext)"):
            self.port.write("%sX" % self.triggers[self.trigger])
        elif self.trigger.endswith("slope)"):
            self.port.write("%s,%sX" % (self.triggers[self.trigger], self.triggerlevel))

    def read_result(self) -> None:
        """Read the result

        In case an external trigger or slope-dependent trigger was configured and did not happen yet, the command will
        wait for the result to appear or run into timeout.
        """
        self.data = self.port.read()

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [float(self.data)]
