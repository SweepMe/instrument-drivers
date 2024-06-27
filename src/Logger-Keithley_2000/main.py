# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2020 Axel Fischer (sweep-me.net)
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
# Type: Logger
# Device: Keithley 2000


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """
                <p>This driver is now in state 'beta'. It can be used for simple logging purposes and only a couple of options are supported.</p>
                <p>&nbsp;</p>
                <p><strong>Range<br /></strong>At the moment, auto range is set for all measurement modes</p>
                <p><strong>NPLC<br /></strong>Number of power line cycles can be set between "Fast (0.1)" to "Slow (10.0)".</p>
                <p><strong>Temperature unit</strong><br />The temperature unit can be &deg;C, K, or &deg;F</p>
                <p><strong>Display</strong><br />The display can be switched off during the measurement which can lead to faster measurements.</p>
                <p><strong>Known issues</strong><br />Measurement modes such as "Voltage AC", "Current AC", or "Resistance" leads to errors and further bugfixing is needed. When display is switched off, it sometimes does not switch on again although an appropriate command is sent.</p>
                  """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Keithley2000"
        
        self.port_manager = True
        self.port_types = ["COM", "GPIB"]
        
        self.port_properties = { 
                                    "timeout": 2,
                                    "EOL": "\r", 
                                    "baudrate": 9600, # factory default
                                }
                                 
        
        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        self.modes = {
                        "Voltage DC":   "VOLT:DC",   
                        "Voltage AC":   "VOLT:AC",  
                        "Current DC":   "CURR:DC",  
                        "Current AC":   "CURR:AC", 
                        "Resistance":   "RES",     
                        "FResistance":  "FRES",    
                        "Frequency":    "FREQ",    
                        "Period":       "PER",     
                        "Temperature":  "TEMP",     
                        "Diode":        "DIOD",
                        "Continuity":   "CONT",    
                        
                        }
                     
        # this dictionary sets the unit of each mode
        self.mode_units = {
                        "Voltage DC":   "V", 
                        "Voltage AC":   "V", 
                        "Current DC":   "A", 
                        "Current AC":   "A", 
                        "Resistance":   "Ohm", 
                        "FResistance":  "Ohm", 
                        "Frequency":    "Hz",
                        "Period":       "s",
                        "Temperature":  "K", 
                        "Continuity":   "", 
                        "Diode":        "",
                        }
          
        # a list of available resolutions as they can be sent to the instrument
        self.resolutions = [
                            "0.1",      # i.e., 100.0 V (3½ digits)
                            "0.01",     # i.e., 10.00 V (3½ digits)
                            "0.001",    # i.e., 1.000 V (3½ digits)
                            "0.0001",   # i.e., 1.0000 V (4½ digits)
                            "0.00001",  # i.e., 1.00000 V (5½ digits)
                            "0.000001", # i.e., 1.000000 V (6½ digits)
                            ]
                 
        # a dictionary of trigger types and their corresponding commands. The trigger types will be shown in the GUI field 'Trigger'
        self.trigger_types =    {
                                "Immediate": "IMM",
                                # "Timer":     "TIM",
                                # "Manual":    "MAN", 
                                "Internal":  "BUS",
                                # "External":  "EXT",
                                }
                                
        self.nplc_types = {
                                "Fastest (0.01)": 0.01,
                                "Fast (0.1)"  : 0.1,
                                "Medium (1.0)": 1.0,
                                "Slow (10.0)" : 10.0,
                            }   
                            
                                
                                                                 
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "Mode" : list(self.modes.keys()),
                        #"Resolution": self.resolutions,
                        # "Range": ["1", "2"],
                        #"Channel": ["%i-%02d" % (S, CH) for S in range(1,3,1) for CH in range(1,11,1)],
                        #"Trigger": list(self.trigger_types.keys()),
                        #"Average": "1",
                        
                        "NPLC": list(self.nplc_types.keys()),
                        "Range": ["Auto"],
                        "Display": ["On", "Off"],
                        
                        "Temperature unit": ["°C", "K", "°F"],
                        }
                        
        return GUIparameter
                                 
    def get_GUIparameter(self, parameter = {}):
    
        #print()
        #print(parameter)
    
        self.mode = parameter['Mode']
        #self.resolution = parameter['Resolution']
        #self.clist = parameter['Channel'].replace(" ", "").replace("-", "").split(",")
        #self.trigger_type = parameter['Trigger']
            
        self.range = parameter['Range']
        self.nplc = parameter['NPLC'].replace("(", "").replace(")", "").split()[-1]
        self.display = parameter['Display']
        
        self.temperature_unit = str(parameter["Temperature unit"])
        
        self.port_string = parameter["Port"]
        
        #average = int(parameter['Average'])            

        # here, the variables and units are defined, based on the selection of the user
        # we have as many variables as channels are selected
        self.variables = [self.mode]  # we add the channel name to each variable, e.g "Voltage DC@1-03"
        
        if "Temperature" in self.mode:
            self.units = [self.temperature_unit]
        else:
            self.units = [self.mode_units[self.mode]]
            
        self.plottype =  [True]  # True to plot data
        self.savetype =  [True]  # True to save data

                
    def initialize(self):
    
        #self.port.write("*IDN?")
        #print(self.port.read())
    
        # once at the beginning of the measurement
        self.port.write("*RST")
        
        self.port.write("*CLS") # reset all values
        
        self.port.write("SYST:BEEP:STAT OFF")     # control-Beep off

        ## does not seem to work although it should: results in error -113 undefined header
        #if self.port_string.startswith("COM"):
        #     self.port.write(":SYST:RWL")

    def deinitialize(self):
            
        self.port.write("SYST:BEEP:STAT ON")     # control-Beep on

        ## does not seem to work although it should: results in error -113 undefined header
        #if self.port_string.startswith("COM"):
        #    self.port.write("SYST:LOC")  # RS-232/COM-port only

    def configure(self):
        
        # range = "0"
        # channels = "(@" + ",".join(self.clist) + ")"        
        # print("Channels:", channels)
        
        ## Mode
        self.port.write(":SENS:FUNC \"%s\"" % self.modes[self.mode])
            
        ## Temperature unit
        if self.mode == "Temperature":
            self.port.write(":UNIT:TEMP %s" % self.temperature_unit.replace("°", ""))

        ## Speed    
        self.port.write(":SENS:%s:NPLC %s" % (self.modes[self.mode], str(self.nplc)))
        
        ## Range
        if not self.mode in ["Temperature", "Continuity", "Diode"]:
            self.port.write(":SENS:%s:RANG:AUTO ON" % (self.modes[self.mode]))

        ## Display
        if self.display == "Off":
            self.port.write(":DISP:ENAB OFF")
            
        ## Trigger
        #print("Configuring trigger")
        self.port.write("INIT:CONT OFF")  # needed to use "READ?" command
        #self.port.write("TRIG:SOUR %s" % self.trigger_types[self.trigger_type])
        
        ## Average
        # to be added
        
     
    def unconfigure(self):
        if self.display == "Off":
            self.port.write(":DISP:ENAB ON")  # We switch Display on again if it was switched off
     
            
    def measure(self): 
        self.port.write("READ?")  # triggers a new measurement                      

    def call(self):
        answer = self.port.read()  # here we read the response from the "READ?" request in 'measure'
        #print("Response to READ? command:", answer)

        return [float(answer)]

    def disconnect(self):
        self.port.close() 
        
        
    """
    """
