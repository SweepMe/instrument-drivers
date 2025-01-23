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
# * Module: Scope
# * Instrument: Tektronix DPO7000


from pysweepme.EmptyDeviceClass import EmptyDevice
import numpy as np

class Device(EmptyDevice):

    description = """
        Driver to configure and read out meausure slots
    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
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


    def set_GUIparameter(self):

        gui_parameter = {
            "Count": "1"
        }

        for slot in range(1, 9):
            gui_parameter[f"Slot {slot} channel"] = ["None", "1", "2", "3", "4"]
            gui_parameter[f"Slot {slot} measure type"] = ["None"] + list(self.measure_types.keys())

        return gui_parameter

    def get_GUIparameter(self, parameter={}):

        self.slot_channels = {}
        self.slot_measure_types = {}
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        for slot in range(1, 9):
            self.slot_channels[slot] = parameter[f"Slot {slot} channel"]
            self.slot_measure_types[slot] = parameter[f"Slot {slot} measure type"]

            if self.slot_channels[slot] != "None" and self.slot_measure_types[slot] != "None":
                self.variables.append("Ch" + self.slot_channels[slot] + " - " + self.slot_measure_types[slot])
                self.units.append(self.measure_type_units[self.slot_measure_types[slot]])
                self.plottype.append(True)
                self.savetype.append(True)

        self.statistics_count = int(parameter["Count"])

    def initialize(self):

        identifier = self.get_identification()
        print("Identifier:", identifier)

    def configure(self):

        self.set_measure_statistics_mode(True)

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

    def measure(self):

        # self.port.write("MEASUrement?")
        # answer = self.port.read()
        # print("Measurement:", answer)

        # unclear what an immediate measurement is
        # self.port.write("MEASUrement:IMMed?")
        # answer = self.port.read()
        # print("Measurement immediate:", answer)

        # empty list to store the value of each channel
        self.results = []

        # clears the statistics
        self.reset_measurement_statistics()

        # Waiting for all channels to have a non-zero standard deviation which means that enough repetitions are reached
        for slot in range(1, 9):
            if self.slot_channels[slot] != "None" and self.slot_measure_types[slot] != "None":
                while not self.is_run_stopped():
                    std_dev = self.get_measure_standard_deviation(slot)
                    print(std_dev)
                    if std_dev != 0.0:
                        break

    def request_result(self):
        for slot in range(1, 9):
            if self.slot_channels[slot] != "None" and self.slot_measure_types[slot] != "None":
                if self.statistics_count == 1:
                    value = self.get_measure_value(slot)
                    self.results.append(value)
                else:
                    value = self.get_measure_mean(slot)
                    self.results.append(value)

    def call(self):
        return self.results

        """
        FORWARDS;
        RISE;
        RISE;
        PERIOD;
        "s";
        CH1;
        CH2;

        FORWARDS;
        FORWARDS;
        FORWARDS;
        FORWARDS;
        FORWARDS;
        FORWARDS;
        FORWARDS;
        FORWARDS;

        RISE;
        RISE;
        RISE;
        RISE;
        RISE;
        RISE;
        RISE;
        RISE;

        RISE;
        RISE;
        RISE;
        RISE;
        RISE;
        RISE;
        RISE;
        RISE;

        FREQUENCY;
        PK2PK;
        PERIOD;
        PERIOD;
        PERIOD;
        PERIOD;
        PERIOD;
        PERIOD;

        "Hz";
        "V";
        "s";
        "s";
        "s";
        "s";
        "s";
        "s";

        CH1;
        CH2;
        CH1;
        CH2;
        CH1;
        CH2;
        CH1;
        CH2;

        CH1;
        CH2;
        CH1;
        CH2;
        CH1;
        CH2;
        CH1;
        CH2;

        1;
        1;
        0;
        0;
        0;
        0;
        0;
        0;

        AUTO;
        PERCENT;

        0.0E+0;
        0.0E+0;
        0.0E+0;
        0.0E+0;
        90.0000;
        10.0000;
        50.0000;
        50.0000;

        OFF;
        0;
        0;

        99.0000E+36;
        99.0000E+36;
        99.0000E+36;
        99.0000E+36;
        99.0000E+36;
        99.0000E+36;
        99.0000E+36;
        99.0000E+36;

        ALL;

        32;

        SCREEN
        """

    """ wrapped communication commands """

    def get_identification(self):
        self.port.write("*IDN?")  # Query device name
        answer = self.port.read()
        return answer

    def reset(self):
        self.port.write("*RST")

    def get_acquisition_number(self):
        self.port.write("ACQ:NUMACQ?")
        answer = self.port.read()
        return int(answer)

    def get_measure_type(self, slot: int):
        self.port.write(f"MEASUrement:MEAS{slot}?")
        answer = self.port.read()
        return answer

    def get_measure_unit(self, slot: int):
        self.port.write(f"MEASUrement:MEAS{slot}:UNIts?")
        answer = self.port.read()
        return answer

    def get_measure_value(self, slot: int):
        self.port.write(f"MEASUrement:MEAS{slot}:VALue?")
        answer = self.port.read()
        return float(answer)

    def get_measure_minimum(self, slot: int):
        self.port.write(f"MEASUrement:MEAS{slot}:MINImum?")
        answer = self.port.read()
        return float(answer)

    def get_measure_maximum(self, slot: int):
        self.port.write(f"MEASUrement:MEAS{slot}:MAXImum?")
        answer = self.port.read()
        return float(answer)

    def get_measure_mean(self, slot: int):
        self.port.write(f"MEASUrement:MEAS{slot}:MEAN?")
        answer = self.port.read()
        return float(answer)

    def get_measure_standard_deviation(self, slot: int):
        self.port.write(f"MEASUrement:MEAS{slot}:STDdev?")
        answer = self.port.read()
        return float(answer)

    def set_measure_state(self, slot: int, state: (str, bool, int)):

        if isinstance(state, bool):
            if state is True:
                state = "ON"
            elif state is False:
                state = "OFF"

        elif isinstance(state, int):
            if state == 1:
                state = "ON"
            elif state == 0:
                state = "OFF"
            else:
                msg = "Only integers 0 and 1 are accepted"
                raise ValueError(msg)

        elif isinstance(state, str):
           if state not in ["ON", "OFF"]:
               msg = "Only ON or OFF are accepted"
               raise ValueError(msg)

        self.port.write(f"MEASUrement:MEAS{slot}:STATE {state}")

    def get_measurement_statistics(self):
        self.port.write("MEASUrement:STATIstics?")
        answer = self.port.read()
        return answer

    def reset_measurement_statistics(self):
        self.port.write("MEASUrement:STATIstics RESET")

    def set_measure_statistics_mode(self, state: (str, bool, int)):

        if isinstance(state, bool):
            if state is True:
                state = "ON"
            elif state is False:
                state = "OFF"

        elif isinstance(state, int):
            if state == 1:
                state = "ON"
            elif state == 0:
                state = "OFF"
            else:
                msg = "Only integers 0 and 1 are accepted"
                raise ValueError(msg)

        elif isinstance(state, str):
           if state not in ["ON", "OFF"]:
               msg = "Only ON or OFF are accepted"
               raise ValueError(msg)

        self.port.write("MEASUrement:STATIstics:MODE {state}")

    def get_measure_statistics_mode(self):
        self.port.write("MEASUrement:STATIstics:MODE?")
        answer = self.port.read()
        return answer

    def set_measure_statistics_count(self, count: int):
        self.port.write(f"MEASUrement:STATIstics:WEIghting {count}")

    def get_measure_statistics_count(self):
        self.port.write("MEASUrement:STATIstics:WEIghting?")
        answer = self.port.read()
        return int(answer)

