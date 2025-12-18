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

        self.modes = {  # Possible measurement modes
            "DC": "DC",
            "AC": "RMS",
            #,"Lock-In": "LIA"  Not yet implemented by SweepMe!
        }

        self.range_limits = {  # Voltage range limits in V
            "10 mV (7.07 mV RMS)" : 0.01,
            "100 mV (70.7 mV RMS)": 0.1,
            "1 V (707 mV RMS)": 1,
            "10 V (7.07 V RMS)": 10
        }

        self.input_configurations = {  # Possible input configurations
            "A-B": "AB",
            "A": "A",
            "Ground": "GROund"
        }

        # Measurement Parameters with default values
        self.slot: str = ""
        self.port_string: str = ""
        self.nplc: float = 3  # Averaging time in Number of Power-Line-Cycles (i.e. 1/50 s)
        self.mode_set: str = "DC"  # Direct or alternating current setting
        self.mode_read: str = "DC"  # Read command depending on mode_set
        self.range_mode: str = "Auto"  # Automatic or manual setting of the range
        self.limit: float = 0.1  # Manual range limit setting
        self.input_config: str = "AB"  # Relation of the two inputs. See touch panel for explanation.
        self.voltage: float = float('nan')  # Measured datapoints
            
    def update_gui_parameters(self, parameters):
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        gui_parameters = {"Channel": ["M1", "M2", "M3"],  # physical channels of the M81 System
                        "Mode": list(self.modes.keys()),
                        "Range mode": ["Auto", "Manual"],  # Automatically set the range?
        }
        meas_range = parameters.get("Range mode")
        if meas_range:  # Safeguard to avoid KeyError during startup, when gui parameters are being loaded
            if meas_range == "Manual":  # Ask for manual range, only if "Manual" is selected
                gui_parameters["Manual range limit"] = list(self.range_limits.keys())  # Selection for manual range
        gui_parameters["Averaging time (NPLC)"] = 0.1
        gui_parameters["Input configuration"] = list(self.input_configurations.keys())
        return gui_parameters


    def apply_gui_parameters(self, parameter):
        channel = parameter["Channel"]
        if len(channel) == 2:
            self.slot = channel[1] 

        self.port_string = parameter["Port"] # use this string to open the right port object later during 'connect'
        self.mode_set = parameter["Mode"]
        self.mode_read = self.modes.get(self.mode_set, "")
        self.range_mode = parameter["Range mode"]
        if parameter.get("Manual range limit"):
            self.limit = self.range_limits.get(parameter["Manual range limit"], 0.0)
        self.input_config = self.input_configurations.get(parameter["Input configuration"], "")


        try:
            self.nplc = float(parameter["Averaging time (NPLC)"])
        except ValueError:  # Do not fail, if parameter is not yet loaded or empty
            self.nplc = 0.1

        self.shortname = "VM-10 @ M" + self.slot  # short name will be shown in the sequencer

        self.variables = ["Voltage " + self.mode_read] # Voltage DC or Voltage RMS, depending on mode
        self.units = ["V"] # make sure that you have as many units as you have variables
        self.plottype = [True]   # True to plot data, corresponding to self.variables
        self.savetype = [True]   # True to save data, corresponding to self.variables

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """
        
    def connect(self):
        pass

    def disconnect(self):
        pass

    def initialize(self):
        self.check_device()
        self.port.write(f'SENSe{self.slot}:PRESet')  # Load power-on defaults
    
    def deinitialize(self):
        # called only once at the end of the measurement
        pass

    """ the following functions are called if a new branch is entered
     and the module was not part of the previous branch """

    def configure(self):
        self.set_mode(self.mode_set)
        self.set_range(self.limit)
        self.set_nplc(self.nplc)
        self.set_input_config(self.input_config)

    """ the following functions are called for each measurement point """

    def measure(self):
        self.port.write(f"READ:SENS{self.slot}:{self.mode_read}?")
        
    def read_result(self):
        
        res = self.port.read()
        self.voltage = float(res)

    def call(self):
        return [self.voltage]

    """ wrapped functions """

    def set_mode(self, mode):
        self.port.write(f'SENSe{self.slot}:MODE {mode}')

    def set_range(self, limit):
        # Set range during initialize
        if self.range_mode == "Manual":
            self.port.write(f'SENSe{self.slot}:VOLTage:RANGe:AUTO 0')  # Manual ranging
            self.port.write(f'SENSe{self.slot}:VOLTage:RANGe {limit}')
        else:
            self.port.write(f'SENSe{self.slot}:VOLTage:RANGe:AUTO 1')  # Auto ranging

    def set_nplc(self, nplc):
        #Set averaging time during initialize
        if not (600 >= nplc >= 0.01):
            raise ValueError("NPLC must be between 0.01 and 600.00.")
        self.port.write(f'SENSe{self.slot}:NPLCycles {nplc}')

    def set_input_config(self, input_config):  # Set input configuration during initialize
        self.port.write(f'SENSe{self.slot}:CONFiguration {input_config}')

    def check_device(self):
        # Check, if connected device is actually a VM-10 module:
        model = self.port.query(f'SENSe{self.slot}:MODel?')
        if 'VM-10' not in model:
            raise ValueError(
                f"Device connected on channel M{self.slot} does not match this driver. "
                f"Found: '{model}'")

