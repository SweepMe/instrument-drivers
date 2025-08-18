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
# * Module: Switch
# * Instrument: Rohde & Schwarz NGPV

# from pysweepme.ErrorMessage import error
from pysweepme.EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):
    """<p><strong>Rohde & Schwarz NGPV Power Supply</strong></p>
    <ul>
    <li>Attention: the NGPV only offers to receive commands to setup its output.</li>
    <li>Measured output values are only available via the analogue displays on 
    the instrument's front panel and therefore cannot be transmitted digitally.</li>
    <li>In addition, please be reminded that the line of NGPV instruments 
    (with the exception of the 8/10, see manual) will shutdown if the full 
    nominal value is requested, e.g. 300V for the NGPV 300. Maximum value is 
    full nominal value minus 1 on the last digit, e.g. 299.9V for the NGPV 300.
    Refer to the manual for details.</li>
    </ul>
    """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "NGPV"

        self.variables = ["requested Voltage"]
        self.units = ["V"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        self.port_manager = True
        self.port_types = ["GPIB"]

        self.port_properties = {
            "delay": 0.1,
            "timeout": 3,
        }
        
        # Selection of NGPV Models and its specific current mode dictionary using nested dictionaries
        self.ngpvmodels = {
            "NGPV 8/10": {
            "Low, 0-999mA": "\"{:0.3f}\".format(self.currentlimit)",
            "High, 0-9.99A": "\"{:1.2f}\".format(self.currentlimit)"
            },
            "NGPV 20/5": {
            "Low, 0-999mA": "\"{:0.3f}\".format(self.currentlimit)",
            "High, 0-4.99A": "\"{:1.2f}\".format(self.currentlimit)"
            },
            "NGPV 20/10": {
            "Low, 0-999mA": "\"{:0.3f}\".format(self.currentlimit)",
            "High, 0-9.99A": "\"{:1.2f}\".format(self.currentlimit)"
            },
            "NGPV 40/3": {
            "Low, 0-999mA": "\"{:0.3f}\".format(self.currentlimit)",
            "High, 0-2.99A": "\"{:1.2f}\".format(self.currentlimit)"
            },
            "NGPV 40/5": {
            "Low, 0-999mA": "\"{:0.3f}\".format(self.currentlimit)",
            "High, 0-4.99A": "\"{:1.2f}\".format(self.currentlimit)"
            },
            "NGPV 100/1": {
            "Low, 0-99.9mA": "\"{:0.4f}\".format(self.currentlimit)",
            "High, 0-999mA": "\"{:0.3f}\".format(self.currentlimit)"
            },
            "NGPV 100/2": {
            "Low, 0-99.9mA": "\"{:0.4f}\".format(self.currentlimit)",
            "High, 0-1.99A": "\"{:1.2f}\".format(self.currentlimit)"
            },
            "NGPV 300/0.3": {
            "Low, 0-99.9mA": "\"{:0.4f}\".format(self.currentlimit)",
            "High, 0-299mA": "\"{:0.3f}\".format(self.currentlimit)"
            },
            "NGPV 300/0.6": {
            "Low, 0-99.9mA": "\"{:0.4f}\".format(self.currentlimit)",
            "High, 0-599mA": "\"{:0.3f}\".format(self.currentlimit)"
            }
        } 
        
        # Selection of model-depending Voltage input format
        self.voltageformat = {
            "NGPV 8/10": "\"{:2.2f}\".format(self.value)",
            "NGPV 20/5": "\"{:2.2f}\".format(self.value)",
            "NGPV 20/10": "\"{:2.2f}\".format(self.value)",
            "NGPV 40/3": "\"{:2.2f}\".format(self.value)",
            "NGPV 40/5": "\"{:2.2f}\".format(self.value)",
            "NGPV 100/1": "\"{:2.1f}\".format(self.value)",
            "NGPV 100/2": "\"{:2.1f}\".format(self.value)",
            "NGPV 300/0.3": "\"{:3.1f}\".format(self.value)",
            "NGPV 300/0.6": "\"{:3.1f}\".format(self.value)"
        } 
        
    def update_gui_parameters(self, parameters):
        
        # retrieve currently set NGPV Model, default to "NGPV 8/10" if unset
        self.ngpvmodel = parameters.get("NGPV Model", "NGPV 8/10")
        
        new_parameters = {
            "NGPV Model": list(self.ngpvmodels.keys()),
            "Current Mode": list(self.ngpvmodels[self.ngpvmodel].keys()),
            "SweepMode": ["Voltage in V"],
            "RouteOut": ["Front and Rear"],
            "Compliance": 0.01,
            "Output Capacitor":["Disabled", "Enabled"],
        }

        return new_parameters

    def apply_gui_parameters(self, parameters):
        
        self.ngpvmodel = parameters.get("NGPV Model")
        self.currentmode = parameters.get("Current Mode")
        self.port_string = parameters.get("Port")
        self.source = parameters.get("SweepMode")
        self.route_out = parameters.get("RouteOut")
        self.currentlimit = float(parameters.get("Compliance"))
        self.outputcap = parameters.get("Output Capacitor")

    def initialize(self):
        pass
        

    def configure(self):
        # sets current mode and output smoothing capacitor enabled/disabled
        if self.outputcap == "Disabled":
            if self.currentmode.startswith("Low"):
                # sets output cap disabled and low current range
                self.port.write("0R")
            else:
                # sets output cap disabled and high current range
                self.port.write("1R")
        else:
            if self.currentmode.startswith("Low"):
                # sets output cap enabled and low current range
                self.port.write("3R")
            else:
                # sets output cap enabled and high current range
                self.port.write("4R")
        
        # check if the requested compliance limit is within the range of the selected current mode
        # 1. extract only the last 6 characters; this will return "-999mA", "99.9mA" or "-x.99A"
        compliancelimit = self.currentmode[-6:]
        # 2. remove "m" (if present) and "A"
        compliancelimit = compliancelimit.replace ('m','')
        compliancelimit = compliancelimit.replace ('A','')
        # 3. convert to float; in cases where the last 6 characters contain the minus sign, remove it via abs function
        compliancelimit = abs(float(compliancelimit))
        # 4. if the original extracted string contained an "m" for "milli", divide value by 1000 to convert from mA to A
        if "m" in self.currentmode[-6:]:
            compliancelimit = compliancelimit/1000
        if compliancelimit >= self.currentlimit:
            # the format expression stored in self.currentMODE gets applied on self.currentLIMIT to prepare it for GPIB transmission
            self.currentlimit = eval(self.ngpvmodels[self.ngpvmodel][self.currentmode])
            self.port.write(str(self.currentlimit)+"A")
        else:
            msg = "Entered compliance value is above the range of the selected current operation mode of the instrument."
            raise Exception(msg)

    def unconfigure(self):
        pass

    def deinitialize(self):
        # GO TO LOCAL, disable remote access
        # as of 17.08.2025, this does not seem to work
        self.port.write("GTL")

    def poweron(self):
        # closing the output relay, activating output
        self.port.write("C")

    def poweroff(self):
        # setting the instrument into standby
        self.port.write("S")

    def apply(self):
        self.value = eval(self.voltageformat[self.ngpvmodel])
        self.port.write(str(self.value)+"V")

    def measure(self):
        pass
        
    def call(self):
        return float(self.value)
