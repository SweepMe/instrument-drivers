# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022 SweepMe! GmbH
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

# Contribution: We like to thank GRIP Molecular Technologies, Inc/John Myers-Bangsund, Ph.D. for providing the initial version of this driver.

# SweepMe! device class
# Type: Logger
# Device: Keithley 2700


import time

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """
                  no help defined yet
                  """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Keithley2700"
        self.port_manager = True
        self.port_types = ["COM", "GPIB", "TCPIP"]  # Keithley 2701 has Ethernet connection
        self.port_properties = {
                                    "timeout": 10,
                                    "EOL": "\r",
                                    "baudrate": 9600, # factory default
                                }
                                
        self.variables = ["Channels"]
        self.units = ["#"]

    def set_GUIparameter(self):
        GUIparameter = {
                        "SweepMode" : ["Channels"],
                        "Switch settling time in ms" : 20,
                        }
        return GUIparameter

    def get_GUIparameter(self, parameter = {}):
        self.switch_settling_time_s = float(parameter["Switch settling time in ms"])/1000
        self.sweepmode = parameter["SweepMode"]

    def initialize(self):

        # once at the beginning of the measurement
        self.port.write("*RST")

        self.port.write("*CLS") # reset all values

        self.port.write("SYST:BEEP:STAT OFF")     # control-Beep off
        # Open all channels
        self.port.write("route:open:all")

    def configure(self):
        pass

    def deinitialize(self):

        self.port.write("SYST:BEEP:STAT ON")     # control-Beep on

        
    def measure(self):
        pass
        
    def apply(self):
        self.port.write("route:close (@" + str(self.value) + ")")
        
    def reach(self):
        time.sleep(self.switch_settling_time_s)
        
    def call(self):
        return int(self.value)



    """
    """
