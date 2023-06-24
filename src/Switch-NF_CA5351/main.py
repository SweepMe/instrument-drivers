# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022 Gennaro Tortone (Istituto Nazionale di Fisica Nucleare - Sezione di Napoli - tortone@na.infn.it)
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
# Type: Switch
# Device: NFCorporation CA5351

import time
from collections import OrderedDict
from EmptyDeviceClass import EmptyDevice
from ErrorMessage import debug

class Device(EmptyDevice):

    description =   """
<style>
    table, th, td { border:1px solid black; padding: 2px1}
</style>
<h3>NF Corporation CA5351 - current amplifier</h3>
<div>
<table>
    <tbody>
        <tr>
            <th>CS range</th>
            <th>settable range of CS value</th>
            <th>resolution</th>
        </tr>
        <tr>
            <td>8 nA</td>
            <td>-8 nA to +8 nA</td>
            <td>0.001 nA (1 pA)</td>
        </tr>
        <tr>
            <td>80 nA</td>
            <td>-80 nA to +80 nA</td>
            <td>0.01 nA (10 pA)</td>
        </tr>
        <tr>
            <td>800 nA</td>
            <td>-800 nA to +800 nA</td>
            <td>0.1 nA (100 pA)</td>
        </tr>
        <tr>
            <td>8 μA</td>
            <td>-8 μA to +8 μA</td>
            <td>0.001 μA (1 nA)</td>
        </tr>
        <tr>
            <td>80 μA</td>
            <td>-80 μA to +80 μA</td>
            <td>0.01 μA (10 nA)</td>
        </tr>
        <tr>
            <td>800 μA</td>
            <td>-800 μA to +800 μA</td>
            <td>0.1 μA (100 nA)</td>
        </tr>
        <tr>
            <td>8 mA</td>
            <td>-8 mA to +8 mA</td>
            <td>0.001 mA (1 μA)</td>
        </tr>
    </tbody>
</table>
<div>
<br>
<strong>Filter: </strong>
Setting the filter to OFF (not use) will disable noise rejection, but response properties
will become the fastest. When the fastest response is required, turn off the filter
function.
</div>
</div>
                    """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "NF-CA5351"    # short name will be shown in the sequencer

        self.port_manager = True
        self.port_types = ["TCPIP", "GPIB"]

        self.inputs = {
            "front": "FRONT",
            "rear": "REAR"
        }

        self.cs_ranges = OrderedDict([          # current suppression (CS) range
            ("auto", 0),
            ("8 nA", 8E-9),
            ("80 nA", 80E-9),
            ("800 nA", 800E-9),
            ("8 μA", 8E-6),
            ("80 μA", 80E-6),
            ("800 μA", 800E-6),
            ("8 mA", 8E-3)
        ])

        self.filter_rtimes = OrderedDict([      # filter rise time
            ("auto", 0),
            ("1 us", 1E-6),
            ("3 μs", 3E-6),
            ("10 μs", 10E-6),
            ("30 μs", 30E-6),
            ("100 μs", 100E-6),
            ("300 μs", 300E-6),
            ("1 ms", 1E-3),
            ("3 ms", 3E-3),
            ("10 ms", 10E-3),
            ("30 ms", 30E-3),
            ("100 ms", 100E-3),
            ("300 ms", 300E-3)
        ])

        self.gains = {
            "1E03": 1,
            "1E04": 2,
            "1E05": 3,
            "1E06": 4,
            "1E07": 5,
            "1E08": 6,
            "1E09": 7,
            "1E010": 8
        }


    def set_GUIparameter(self):
        GUIparameter =  {
            "SweepMode" : ["None"],
            "Display:": None,
            "Backlight": True,
            "Input:": None,
            "Terminals" : list(self.inputs.keys()),
            "Zero check": False,
            "Amplification": None,
            "I/V Gain": list(self.gains.keys()),
            "Current suppression:" : None,
            "Use current suppression": False,
            "Auto settings": False,
            "Current in A": 0.0,
            "Range": list(self.cs_ranges.keys()),
            "Filter:": None,
            "Use filter": False,
            "Rise time": list(self.filter_rtimes.keys()),
        }

        return GUIparameter

    def get_GUIparameter(self, parameter={}):
        self.backlight = parameter["Backlight"]
        self.input = parameter["Terminals"]
        self.zero_check = parameter["Zero check"]
        self.cs_enable = parameter["Use current suppression"]
        self.auto_settings = parameter["Auto settings"]
        self.cs_value = parameter["Current in A"]
        self.cs_range = parameter["Range"]
        self.gain = parameter["I/V Gain"]
        self.filter_enable = parameter["Use filter"]
        self.filter_rtime = parameter["Rise time"]

        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        if self.cs_enable and self.cs_range == "auto":
            self.variables.append("Current suppression")
            self.units.append("A")
            self.plottype.append(True)
            self.savetype.append(True)

            self.variables.append("Range")
            self.units.append("A")
            self.plottype.append(True)
            self.savetype.append(True)

        if self.filter_enable and self.filter_rtime == "auto":
            self.variables.append("Filter rise time")
            self.units.append("s")
            self.plottype.append(True)
            self.savetype.append(True)
        
    def initialize(self):
        self.port.port.read_termination = '\n'
        self.port.port.write_termination = '\n'
        self.port.write("*RST") # reset to default settings

    def configure(self):
        if self.backlight:
            self.port.write(":DISPLAY:BRIGHTNESS 3")
        else:
            self.port.write(":DISPLAY:BRIGHTNESS 0")

        self.port.write(f":ROUTE:TERMINALS {self.input}")

        if self.zero_check:
            self.port.write(f":INPUT:STATE ON")
        else:
            self.port.write(f":INPUT:STATE OFF")

        if self.cs_enable:

            # reset ESR register
            self.port.write("*CLS")
            if self.auto_settings is False:
                # set range
                if self.cs_range == "auto":
                    self.port.write(":INPUT:BIAS:CURRENT:RANGE:AUTO ON")
                else:
                    self.port.write(f":INPUT:BIAS:CURRENT:RANGE {list(self.cs_ranges.keys()).index(self.cs_range)}")
                # set CS level
                self.port.write(f":INPUT:BIAS:CURRENT {self.cs_value}")
            else:
                self.port.write(":INPUT:BIAS:CURRENT:AUTO EXEC; *OPC")
                timeout = 20
                telapsed = 0
                completed = False
                while telapsed < timeout:
                    if int(self.port.port.query("*OPC?")) == 1:
                        completed = True
                        break
                    time.sleep(0.5)
                    telapsed += 0.5
                if completed is False:
                    raise Exception(f"auto settings timeout")

            # CS setting or auto settings could raise errors
            esr = self.read_esr()

            if (esr & (1<<4)):
                raise Exception("execution error during current suppression setup - verify CS value and range")

            # enable CS
            self.port.write(":INPUT:BIAS:CURRENT:STATE ON")

        # set gain
        self.port.write(f":INPUT:GAIN {self.gains[self.gain]}")

        # set filter
        if self.filter_enable:
            if self.filter_rtime == "auto":
                self.port.write(":INPUT:FILTER:TIME:AUTO ON")
            else:
                self.port.write(f":INPUT:FILTER:TIME {list(self.filter_rtimes.keys()).index(self.filter_rtime)}")

            self.port.write(":INPUT:FILTER:STATE ON")

    def call(self):
        retarr = []
        if (self.cs_enable and self.cs_range == "auto"):
            retarr.append(float(self.port.port.query(":INPUT:BIAS:CURRENT?")))
            id = int(self.port.port.query(":INPUT:BIAS:CURRENT:RANGE?"))
            retarr.append(list(self.cs_ranges.items())[id][1])
        if self.filter_enable and self.filter_rtime == "auto":
            id = int(self.port.port.query(":INPUT:FILTER:TIME?"))
            retarr.append(list(self.filter_rtimes.items())[id][1])
            
        return retarr

    # check ESR (standard event status register)
    def read_esr(self):
        self.port.write("*ESR?")
        answer = int(self.port.read())
        return answer
