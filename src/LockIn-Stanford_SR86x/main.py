# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2021-2022 SweepMe! GmbH (sweep-me.net)
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


# SweepMe! device class
# * Module: LockIn
# * Instrument: SR86x

import math
import time
from collections import OrderedDict

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class for Stanford Research Instruments SR86x Lock-In Amplifier."""
    def __init__(self) -> None:
        """Initialize device parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "SR86x"

        # here the port handling is done
        # the MeasClass automatically creates the PortObject during in the connect function of the MeasClass
        self.port_manager = True
        self.port_types = ["USB", "COM", "GPIB", "TCPIP"]
        self.port_identifications = ["Stanford Research Instruments,SR8"]
        # port_identifications does not work at the moment
        # plan is to hand it over to PortManager who only gives PortObjects back who match at least one of these strings
        # by that multiple devices could be found and related to one DeviceClass
        self.port_properties = {
            "EOL": "\r",
            "timeout": 60,
            "baudrate": 9600,
            "Exception": True,
        }

        # self.options_dict = OrderedDict([

        # no similar command to ILIN was found. The user manual did not indicate any specific notch filter settings.
        # ("No Filter", "ILIN 0"),
        # ("Line", "ILIN 1"),
        # ("2xLine", "ILIN 2"),
        # ("Line + 2xLine", "ILIN 3"),

        # no similar command to RMOD (dynamic reserve) was found. The user manual (p. 48) says there is no settings
        # for this matter.
        # ("High Reserve", "RMOD 0"),
        # ("Normal", "RMOD 1"),
        # ("Low Noise", "RMOD 2"),

        # ])

        self.sensitivities_dict_voltages = OrderedDict(
            [
                ("1 nV", "27"),
                ("2 nV", "26"),
                ("5 nV", "25"),
                ("10 nV", "24"),
                ("20 nV", "23"),
                ("50 nV", "22"),
                ("100 nV", "21"),
                ("200 nV", "20"),
                ("500 nV", "19"),
                ("1 µV", "18"),
                ("2 µV", "17"),
                ("5 µV", "16"),
                ("10 µV", "15"),
                ("20 µV", "14"),
                ("50 µV", "13"),
                ("100 µV", "12"),
                ("200 µV", "11"),
                ("500 µV", "10"),
                ("1 mV", "9"),
                ("2 mV", "8"),
                ("5 mV", "7"),
                ("10 mV", "6"),
                ("20 mV", "5"),
                ("50 mV", "4"),
                ("100 mV", "3"),
                ("200 mV", "2"),
                ("500 mV", "1"),
                ("1 V", "0"),
            ],
        )

        self.sensitivities_dict_currents = OrderedDict(
            [
                ("1 fA", "27"),
                ("2 fA", "26"),
                ("5 fA", "25"),
                ("10 fA", "24"),
                ("20 fA", "23"),
                ("50 fA", "22"),
                ("100 fA", "21"),
                ("200 fA", "20"),
                ("500 fA", "19"),
                ("1 pA", "18"),
                ("2 pA", "17"),
                ("5 pA", "16"),
                ("10 pA", "15"),
                ("20 pA", "14"),
                ("50 pA", "13"),
                ("100 pA", "12"),
                ("200 pA", "11"),
                ("500 pA", "10"),
                ("1 nA", "9"),
                ("2 nA", "8"),
                ("5 nA", "7"),
                ("10 nA", "6"),
                ("20 nA", "5"),
                ("50 nA", "4"),
                ("100 nA", "3"),
                ("200 nA", "2"),
                ("500 nA", "1"),
                ("1 µA", "0"),
            ],
        )

        self.sensitivities_dict = OrderedDict()
        self.sensitivities_dict.update(reversed(self.sensitivities_dict_voltages.items()))
        self.sensitivities_dict.update(reversed(self.sensitivities_dict_currents.items()))

        self.sensitivities_dict_voltages_inverted = {v: k for k, v in self.sensitivities_dict_voltages.items()}
        self.sensitivities_dict_currents_inverted = {v: k for k, v in self.sensitivities_dict_currents.items()}

        self.timeconstant_id_dict = OrderedDict(
            [
                ("1µ", "0"),
                ("3µ", "1"),
                ("10µ", "2"),
                ("30µ", "3"),
                ("100µ", "4"),
                ("300µ", "5"),
                ("1m", "6"),
                ("3m", "7"),
                ("10m", "8"),
                ("30m", "9"),
                ("100m", "10"),
                ("300m", "11"),
                ("1", "12"),
                ("3", "13"),
                ("10", "14"),
                ("30", "15"),
                ("100", "16"),
                ("300", "17"),
                ("1k", "18"),
                ("3k", "19"),
                ("10k", "20"),
                ("30k", "21"),
            ],
        )

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set the standard GUI parameters."""
        return {
            "SweepMode": ["None", "Frequency in Hz", "Time constant in s"],
            "Source": [
                "Internal",
                "External (Sine) @ 50 Ohms",
                "External (Positive TTL) @ 50 Ohms",
                "External (Negative TTL) @ 50 Ohms",
                "External (Sine) @ 1 MOhms",
                "External (Positive TTL) @ 1 MOhms",
                "External (Negative TTL) @ 1 MOhms",
            ],
            "Input": [
                "A @ 1 V",
                "A @ 300 mV",
                "A @ 100 mV",
                "A @ 30 mV",
                "A @ 10 mV",
                "A-B @ 1 V",
                "A-B @ 300 mV",
                "A-B @ 100 mV",
                "A-B @ 30 mV",
                "A-B @ 10 mV",
                "I @ 1 µA",
                "I @ 10 nA",
            ],
            # "Reserve": ["Low Noise", "Normal", "High Reserve"],
            # "Filter1": ["No Filter", "Line", "2xLine", "Line + 2xLine"],
            "Filter1": ["Advanced filter on", "Advanced filter off"],
            "Filter2": ["Sync filter on", "Sync filter off"],
            # "Channel1": ["X", "R", "X*10", "R*10", "X*100", "R*100"],
            # "Channel2": ["Y", "Y*10", "Y*100", "Phase"],
            "Channel1": ["X", "R"],
            "Channel2": ["Y", "Phase"],
            "TimeConstant": list(self.timeconstant_id_dict.keys()),  # ["Auto time", "As is"] +
            "Sensitivity": ["Auto", "As is"] + list(self.sensitivities_dict.keys()),
            "Slope": ["6 dB", "12 dB", "18 dB", "24 dB"],
            "Coupling": ["AC", "DC"],
            "Ground": ["Float", "Ground"],
            "WaitTimeConstants": 4.0,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle the SweepMe! GUI parameter inputs."""
        self.sweepmode = parameter["SweepMode"]
        self.source = parameter["Source"]
        self.input = parameter["Input"]
        self.coupling = parameter["Coupling"]
        self.slope = parameter["Slope"]
        self.ground = parameter["Ground"]
        # self.reserve = parameter["Reserve"]
        self.advanced_filter = parameter["Filter1"]
        self.sync_filter = parameter["Filter2"]
        self.sensitivity = parameter["Sensitivity"]
        self.timeconstant = parameter["TimeConstant"]

        self.channel1 = parameter["Channel1"]
        self.channel2 = parameter["Channel2"]
        self.waittimeconstants = float(parameter["WaitTimeConstants"])

        self.variables = ["Magnitude", "Phase", "Frequency", "X", "Y", "Sensitivity", "Time constant"]
        self.units = []

        if self.input == "I @ 1 µA":
            self.add_Units_Channels("A")
        elif self.input == "I @ 10 nA":
            self.add_Units_Channels("A")
        else:
            self.add_Units_Channels("V")

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def initialize(self):
        self.identification = self.get_identification().split(",")
        print("Identification of the device:", self.identification)

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        if "X" in self.channel1:
            self.set_output_channel(0, 0)
        elif "R" in self.channel1:
            self.set_output_channel(0, 1)
        if self.channel2 == "Y":
            self.set_output_channel(1, 0)
        elif self.channel2 == "Phase":
            self.set_output_channel(1, 1)

        # The Dual and Chop modes for source are not included in the GUI.

        if self.source == "Internal":
            self.set_ref_source(0)
        else:
            self.set_ref_source(1)
            if "50 Ohms" in self.source:
                self.set_external_ref_input_imp(0)
                if "External (Sine)" in self.source:
                    self.set_external_ref_trigger(0)
                elif "External (Positive TTL)" in self.source:
                    self.set_external_ref_trigger(1)
                elif "External (Negative TTL)" in self.source:
                    self.set_external_ref_trigger(2)
            elif "1 MOhms" in self.source:
                self.set_external_ref_input_imp(1)
                if "External (Sine)" in self.source:
                    self.set_external_ref_trigger(0)
                elif "External (Positive TTL)" in self.source:
                    self.set_external_ref_trigger(1)
                elif "External (Negative TTL)" in self.source:
                    self.set_external_ref_trigger(2)
            # self.set_ref_source(self.options_dict[self.source])
            # self.set_external_ref_trigger(1)

        if self.input == "I @ 1 µA":
            self.set_input("Current")
            self.set_current_input_range(0)
        elif self.input == "I @ 10 nA":
            self.set_input("Current")
            self.set_current_input_range(1)
        elif self.input.startswith("A"):
            self.set_input("Voltage")
            if "A-B" in self.input:
                self.set_voltage_input_mode("A-B")
            else:
                self.set_voltage_input_mode("A")
            if "10 mV" in self.input:
                self.set_voltage_input_range(4)
            elif "30 mV" in self.input:
                self.set_voltage_input_range(3)
            elif "100 mV" in self.input:
                self.set_voltage_input_range(2)
            elif "300 mV" in self.input:
                self.set_voltage_input_range(1)
            else:
                self.set_voltage_input_range(0)

        self.set_coupling(self.coupling)

        if self.slope == "6 dB":
            self.set_slope_filter(0)
        elif self.slope == "12 dB":
            self.set_slope_filter(1)
        elif self.slope == "18 dB":
            self.set_slope_filter(2)
        elif self.slope == "24 dB":
            self.set_slope_filter(3)

        self.set_input_shield(self.ground)

        self.set_sync_filter(self.sync_filter)
        self.set_advanced_filter(self.advanced_filter)

        if self.sensitivity == "Auto":
            pass
        elif self.sensitivity == "As is":
            pass
        else:
            if self.input.startswith("I") and "A" in self.sensitivity:
                self.set_sensitivity(self.sensitivities_dict[self.sensitivity])
            elif self.input.startswith("A") and "V" in self.sensitivity:
                self.set_sensitivity(self.sensitivities_dict[self.sensitivity])
            else:
                raise Exception("The input mode and sensitivity should match.")
        if self.timeconstant not in ["Auto time", "As is"] and self.timeconstant in self.timeconstant_id_dict:
            self.set_time_constant(self.timeconstant_id_dict[self.timeconstant])

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.sweepmode.startswith("Frequency"):
            self.set_frequency(self.value, self.identification[1])

        elif self.sweepmode == "Time constant in s":
            conversion = {
                1e3: "ks",
                1e0: "s",
                1e-3: "ms",
                1e-6: "µs",
            }

            for exp_step in list(conversion.keys()):
                if self.value >= 0.65 * exp_step:
                    number = round(self.value / exp_step, 0)

                    # print(number)

                    for multiplicator in [1, 10, 100]:
                        if number <= 2 * multiplicator:
                            number = 1 * multiplicator
                            break

                        elif number <= 6.5 * multiplicator:
                            number = 3 * multiplicator
                            break
                    break

            self.timeconstant = str(number) + " " + conversion[exp_step]
            self.set_time_constant(self.timeconstant_id_dict[self.timeconstant])

    def adapt(self) -> None:
        """'adapt' can be used to adapt an instrument to a new situation after other instruments got a new setvalue."""
        if self.sensitivity == "Auto":
            self.set_auto_scale()
        self.port.write("*OPC?")

    def adapt_ready(self) -> None:
        """'adapt_ready' can be used to make sure that a procedure started in 'adapt' is finished.

        Thus, multiple instrument can start an adapt-procedure simultaneously.
        """
        # waiting for operation complete from 'adapt'
        answer = self.port.read()

        # This time reference to wait several time constants.
        self.time_ref = time.perf_counter()

    def trigger_ready(self) -> None:
        """Make sure that at least several time constants have passed since 'Auto sensitivity' was called."""
        delta_time = (self.waittimeconstants * self.unit_to_float(self.timeconstant)) - (
            time.perf_counter() - self.time_ref
        )
        if delta_time > 0.0:
            # wait several time constants to allow for a renewal of the result
            time.sleep(delta_time)

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        sens_id = str(self.get_sensitivity())
        if self.input.startswith("A"):  # Voltage related sensitivities
            self.sensitivity_value = self.unit_to_float(self.sensitivities_dict_voltages_inverted[sens_id])
        elif self.input.startswith("I"):  # Current related sensitivities
            self.sensitivity_value = self.unit_to_float(self.sensitivities_dict_currents_inverted[sens_id])

        if self.source == "Internal":
            self.port.write("SNAP? 2,3,15")  # R, θ, Internal Reference Frequency
        elif self.source != "Internal":
            self.port.write("SNAP? 2,3,16")  # R, θ, External Reference Frequency

    def read_result(self) -> None:
        """Read the measured data from a buffer."""
        self.R, self.Phase, self.F = map(float, self.port.read().split(","))
        self.X, self.Y = self.R * math.cos(self.Phase), self.R * math.sin(self.Phase)
        # self.Phase, self.F = map(float, self.port.read().split(","))

    def call(self) -> list:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        results = [self.R, self.Phase, self.F, self.X, self.Y]

        # adding sensitivity
        results += [self.sensitivity_value]

        time_constant = self.unit_to_float(self.timeconstant)
        results += [time_constant]

        return results

    @staticmethod
    def unit_to_float(unit) -> float:
        """Takes a string representing a sensitivity or time constant and gives back a corresponding float."""
        chars = OrderedDict(
            [
                ("V", ""),
                ("A", ""),
                ("s", ""),
                (" ", ""),
                ("n", "e-9"),
                ("µ", "e-6"),
                ("u", "e-6"),
                ("m", "e-3"),
                ("k", "e3"),
            ],
        )

        for char in chars:
            unit = unit.replace(char, chars[char])
        return float(unit)

    def add_Units_Channels(self, AorV="V") -> None:
        self.units.append(AorV)
        self.units += ["°", "Hz"]
        self.units += [AorV, AorV, AorV]

        self.units += ["s"]

    """ here, convenience functions start """

    def get_identification(self) -> str:
        """This function return the identification number of the instrument.

        The format is:
        Stanford_Research_Systems,<device type>,<serial number>,<firmware version>; e.g.
        Stanford_Research_Systems,SR860,000111,v1.23
        Returns:
            str: identification string
        """
        self.port.write("*IDN?")
        return self.port.read()

    def operation_complete(self) -> str:
        self.port.write("*OPC?")
        return self.port.read()

    def set_output_channel(self, channel, parameter) -> None:
        """This function sets a certain parameter to the selected output channel.

        Args:
            channel: string or int
            model: string or int
        Returns:
            None
        """
        if str(parameter).upper() in ["XY", "RTHETA", "0", "1"] and str(channel).upper() in ["OCH1", "OCH2", "0", "1"]:
            self.port.write("COUT %s, %s" % (channel, parameter))
        else:
            msg = "Wrong channel and/or parameter."
            raise Exception(msg)

    def set_output_expansion(self, parameter, multiplicator) -> None:
        """This function sets an expansion multiplicator to the selected output parameter.

        Args:
            parameter: string or int
            multiplicator: string or int
        Returns:
            None
        """
        if str(parameter).upper() in ["X", "Y", "R", "0", "1", "2"] and str(multiplicator).upper() in [
            "X10",
            "X100",
            "0",
            "1",
            "2",
        ]:
            self.port.write("CEXP %s, %s" % (parameter, multiplicator))
        else:
            msg = "Wrong parameter and/or multiplicator."
            raise Exception(msg)

    def set_frequency(self, frequency, model) -> None:
        """This function sets the internal osc. frequency in Hz.

        The value of frequency is limited to 1 mHz ≤ f ≤ 500 kHz
        for SR860 and 1 mHz ≤ f ≤ 4 MHz for SR865.

        Args:
            frequency: float
            model: string
        Returns:
            None
        """
        if (model == "SR860" and 0.001 <= frequency <= 500000) or (model == "SR865" and 0.001 <= frequency <= 4000000):
            self.port.write("FREQ %f" % frequency)
        else:
            msg = "Wrong model name and/or out-of-range frequency."
            raise Exception(msg)

    def get_frequency(self) -> str:
        """This function gets the internal oscillator or external frequency in Hz.

        Args:
            None
        Returns:
            str: frequency
        """
        self.port.write("FREQ?")
        return self.port.read()

    def set_ref_source(self, mode) -> None:
        """This function sets reference source.

        Args:
            mode: str or int
        Returns:
            None
        """
        if str(mode).upper() in ["INT", "EXT", "DUAL", "CHOP", "0", "1", "2", "3"]:
            self.port.write("RSRC %s" % mode)
        else:
            msg = "Reference source string is not correct."
            raise Exception(msg)

    def set_external_ref_input_imp(self, imp) -> None:
        """This function sets "external" reference trigger input impedence.

        Args:
            imp: str or int
        Returns:
            None
        """
        if str(imp).upper() in ["50", "50OHMS", "0", "1M", "1MEG", "1"]:
            self.port.write("REFZ %s" % imp)
        else:
            msg = "External Reference trigger input impedence is not correct."
            raise Exception(msg)

    def set_external_ref_trigger(self, mode) -> None:
        """This function sets "external" reference trigger mode.

        Args:
            mode: str or int
        Returns:
            None
        """
        if str(mode).upper() in ["SIN", "POSTTL", "POS", "NEGTTL", "NEG", "0", "1", "2"]:
            self.port.write("RTRG %s" % mode)
        else:
            msg = "Reference trigger mode is not correct."
            raise Exception(msg)

    def set_input(self, input) -> None:
        """This function sets the input to voltage or current.

        Args:
            input: str or int
        Returns:
            None
        """
        if str(input).upper() in ["VOLTAGE", "VOL", "CURRENT", "CUR", "0", "1"]:
            self.port.write("IVMD %s" % input)
        else:
            msg = "Voltage input mode is not correct."
            raise Exception(msg)

    def set_current_input_range(self, range) -> None:
        """This function sets the input current range.

        Args:
            input: str or int
        Returns:
            None
        """
        if str(range).upper() in ["1MEG", "100MEG", "0", "1"]:
            self.port.write("ICUR %s" % range)
        else:
            msg = "Current input range is not correct."
            raise Exception(msg)

    def set_voltage_input_range(self, range) -> None:
        """This function sets the input voltage range.

        Args:
            input: str or int
        Returns:
            None
        """
        if str(range).upper() in ["1VOLT", "300MVOLT", "100MVOLT", "30MVOLT", "10MVOLT", "0", "1", "2", "3", "4"]:
            self.port.write("IRNG %s" % range)
        else:
            msg = "Voltage input range is not correct."
            raise Exception(msg)

    def set_voltage_input_mode(self, voltage_input) -> None:
        """This function sets the voltage input mode. Available input strings are "A" or 0, "A-B or 1.

        Args:
            voltage_input: str or int
        Returns:
            None
        """
        if str(voltage_input).upper() in ["A", "A-B", "0", "1"]:
            self.port.write("ISRC %s" % voltage_input)
        else:
            msg = "Voltage input mode is not correct."
            raise Exception(msg)

    def set_coupling(self, coupling) -> None:
        """This function sets the input coupling mode. Available options are "AC", "DC".

        Args:
            coupling: str or int
        Returns:
            None
        """
        if str(coupling).upper() in ["AC", "DC", "0", "1"]:
            self.port.write("ICPL %s" % coupling)
        else:
            msg = "Coupling mode is not correct."
            raise Exception(msg)

    def set_slope_filter(self, slope_id) -> None:
        """This function sets the filter slope.

        Allowed values: 6 dB/oct (slope_id=0), 12 dB/oct (slope_id=1), 18 dB/oct
        (slope_id=2) or 24 dB/oct (slope_id=3).

        Args:
            slope_id: str or int
        Returns:
            None
        """
        if str(slope_id) in ["0", "1", "2", "3"]:
            self.port.write("OFSL %s" % slope_id)
        else:
            msg = "Slope id is not correct."
            raise Exception(msg)

    def set_input_shield(self, shield) -> None:
        """This function command sets the voltage input shields to float (FLO) or ground (GRO)..

        Args:
            shield: str or int
        Returns:
            None
        """
        if str(shield).upper() in ["FLO", "FLOAT", "GRO", "GROUND", "0", "1"]:
            self.port.write("IGND %s" % shield)
        else:
            msg = "The input shield argument is not correct."
            raise Exception(msg)

    def set_advanced_filter(self, status) -> None:
        """This function turns the advanced filter off  or on.

        Args:
            status: str or int
        Returns:
            None
        """
        status = status.replace("Advanced filter ", "")

        if str(status).upper() in ["ON", "OFF", "0", "1"]:
            self.port.write("ADVFILT %s" % status)
        else:
            msg = "The input status for advanced filter is not correct."
            raise Exception(msg)

    def set_sync_filter(self, status) -> None:
        """This function turns the synchronous filter off  or on.

        Args:
            status: str or int
        Returns:
            None
        """
        status = status.replace("Sync filter ", "")

        if str(status).upper() in ["ON", "OFF", "0", "1"]:
            self.port.write("SYNC %s" % status)
        else:
            msg = "The input status for sync filter is not correct."
            raise Exception(msg)

    def set_sensitivity(self, sensitivity_id) -> None:
        """This function sets the sensitivity according to the table list on the page 112.

        Args:
            sensitivity_id: int
        Returns:
            None
        """
        if int(sensitivity_id) in range(28):
            self.port.write("SCAL %s" % sensitivity_id)
        else:
            msg = "The input sensitivity id is not correct."
            raise Exception(msg)

    def get_sensitivity(self) -> int:
        """This function returns the sensitivity according to the table list on the page 112.

        Args:
            sensitivity_id: int
        Returns:
            int: answer
        """
        self.port.write("SCAL?")
        return int(self.port.read())

    def set_auto_scale(self) -> None:
        """This function enables the auto scale function, which also sets the sensitivity automatically.

        Returns:
            None
        """
        self.port.write("ASCL")

    def set_time_constant(self, tau_id) -> None:
        """The function sets the time constant according to the table list on the page 113.

        Args:
            tau_id: int
        Returns:
            None
        """
        if int(tau_id) in range(22):
            self.port.write("OFLT %s" % tau_id)
        else:
            msg = "The input time constant id is not correct."
            raise Exception(msg)
