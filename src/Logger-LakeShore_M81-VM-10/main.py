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
# * Instrument: LakeShore M81 VM-10


from pysweepme.EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    ## here you can add html formatted description to your device class that is shown by modules like 'Logger' or 'Switch' that have a description field.
    description =   """
    <p><strong>VM-10 module of LakeShore M81:</strong></p>
    <ul>
    <li>Log voltage using the VM-10 module of the LakeShore M81 Synchronous Source Measurement System.</li>
    <li>Three physical measurement channels are available at the M81. Connect your VM-10 module to one of them.</li>
    <li>Select the corresponding channel number in SweepMe!</li> 
    </ul>"""

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.port_manager = True 
           
        self.port_types = ["COM", "GPIB", "TCPIP"]
        
        self.port_properties = {
                                "baudrate": 921600,
                                "EOL": "\n",
                                "timeout": 1,
                                }
            
            
    def update_gui_parameters(self, parameters):
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        gui_parameters = {"Channel": ["M1", "M2", "M3"],  # physical channels of the M81 System
                        "Mode": ["DC", "AC"],  # Direct or alternating current
                        "Range": ["Auto", "Manual"],  # Automatically set the range?
        }
        meas_range = parameters.get("Range")
        if meas_range:  # Saveguard to avoid KeyError during startup, when gui parameters are being loaded
            if meas_range == "Manual":  # Ask for manual range, only if not "Manual" is selected
                gui_parameters["Manual range setting"] = [  # Settings for manual range, if not Auto
                    "10 mV (7.07 mV RMS)",
                    "100 mV (70.7 mV RMS)",
                    "1 V (707 mV RMS)",
                    "10 V (7.07 V RMS)"]
        gui_parameters["Averaging Time (NPLC)"] = []  # Averaging time in Number of Power-Line-Cycles (i.e. 1/50 s)
        gui_parameters["Input Configuration"] = ["A-B", "A", "Ground"]  # See touch panel for explanation
        return gui_parameters


    def apply_gui_parameters(self, parameter):
        self.slot = parameter["Channel"]

        self.port_string = parameter["Port"] # use this string to open the right port object later during 'connect'
        self.mode = parameter["Mode"]

        self.shortname = "VM-10 @ " + self.slot  # short name will be shown in the sequencer

        self.variables = ["Voltage " + self.mode] # define as many variables you need
        self.units = ["V"] # make sure that you have as many units as you have variables
        self.plottype = [True]   # True to plot data, corresponding to self.variables
        self.savetype = [True]   # True to save data, corresponding to self.variables


    def reconfigure(self, parameters={}, keys=[]):
        if self.get_GUIparameter(self, "Range") == "Auto":
            parameters = self.set_GUIparameter()
            del parameters['Manual range setting']
            self.update_gui_parameters(self, parameters)

  
    """ here, semantic standard functions start that are called by SweepMe! during a measurement """
        
    def connect(self):
        
        self.port.write("*IDN?")
        res = self.port.read()
            

    def disconnect(self):
        pass
        

    def initialize(self):
        pass
        
    
    def deinitialize(self):
        # called only once at the end of the measurement
        print("deinitialize")
        
        
    """ the following functions are called for each measurement point """

    def measure(self):
        self.port.write(f"READ:SENS{self.slot[1]}:{self.mode}?")
        
    def read_result(self):
        
        res = self.port.read()
        self.current = float(res)
        

    def call(self):
        return [self.current]
        
