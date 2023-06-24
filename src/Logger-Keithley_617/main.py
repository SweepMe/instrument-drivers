# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021-2022 Axel Fischer (sweep-me.net)
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
# Device: Keithley 617


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    actions = ["auto_zero"]

    description = """
                  <table>
<tbody>
  <tr>
<td>Command</td>
<td>Volts</td>
<td>Amps</td>
<td>Ohms</td>
<td>Coulombs</td>
<td>External feedback</td>
<td>V/I Ohms</td>
</tr>
<tr>
<td>R0</td>
<td>Auto</td>
<td>Auto</td>
<td>Auto</td>
<td>Auto</td>
<td>Auto</td>
<td>Auto</td>
</tr>
<tr>
<td>R1</td>
<td>200mV</td>
<td>2pA</td>
<td>2kOhm</td>
<td>200pC</td>
<td>200mV</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>R2</td>
<td>2V</td>
<td>20pA</td>
<td>20kOhm</td>
<td>2nC</td>
<td>2V</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>R3</td>
<td>20V</td>
<td>200pA</td>
<td>200kOhm</td>
<td>20nC</td>
<td>20V</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>R4</td>
<td>200V</td>
<td>2nA</td>
<td>2MOhm</td>
<td>20nC</td>
<td>200V</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>R5</td>
<td>200V</td>
<td>20nA</td>
<td>20MOhm</td>
<td>20nC</td>
<td>200V</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>R6</td>
<td>200V</td>
<td>200nA</td>
<td>200MOhm</td>
<td>20nC</td>
<td>200V</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>R7</td>
<td>200V</td>
<td>2µA</td>
<td>2GOhm</td>
<td>20nC</td>
<td>200V</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>R8</td>
<td>200V</td>
<td>20µA</td>
<td>20GOhm</td>
<td>20nC</td>
<td>200V</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>R9</td>
<td>200V</td>
<td>200µA</td>
<td>200GOhm</td>
<td>20nC</td>
<td>200V</td>
<td>&nbsp;</td>
</tr>
  <tr>
<td>R10</td>
<td>200V</td>
<td>2mA</td>
<td>200GOhm</td>
<td>20nC</td>
<td>200V</td>
<td>&nbsp;</td>
</tr>
  <tr>
<td>R11</td>
<td>200V</td>
<td>20mA</td>
<td>200GOhm</td>
<td>20nC</td>
<td>200V</td>
<td>&nbsp;</td>
</tr>
  <tr>
<td>R12</td>
<td>Cancel</td>
<td>Cancel</td>
<td>Cancel</td>
<td>Cancel</td>
<td>Cancel</td>
<td>Cancel</td>

</tr>
</tbody>
</table>
                  """
                  
    

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Keithley617"
        
        self.port_manager = True
        self.port_types = ["GPIB"] 
                                         
        self.port_properties = {
                                "timeout": 3.0,
                                "delay": 0.1,
                                }
        
        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        self.modes = {
                        "Volts":             "F0",
                        "Amps":              "F1",           
                        "Ohms":              "F2",      
                        "Coulombs":          "F3",         
                        "External feedback": "F4",    
                        "V/I Ohms":          "F5",          
                        }
                        
        self.mode_variables = {
                                "Volts":             "Voltage",
                                "Amps":              "Current",           
                                "Ohms":              "Resistance",      
                                "Coulombs":          "Charge",         
                                "External feedback": "Voltage",    
                                "V/I Ohms":          "Resistance V/I",  
                                }
                                                                    
        # this dictionary sets the unit of each mode
        self.mode_units = {
                        "Volts":             "V", 
                        "Amps":              "A", 
                        "Ohms":              "Ohm", 
                        "Coulombs":          "C", 
                        "External feedback": "V", 
                        "V/I Ohms":          "Ohm", 
                        }
                 
                               
                                                                 
    def set_GUIparameter(self):
        
        GUIparameter = {
                
                        "Mode": list(self.modes.keys()),
                        "Range": ["R%i" %i for i in range(15)],

                        "Voltage source in V": "0.0",
                        
                        "Auto zero": ["Off", "On"],
                        # "Zero check": ["Off", "On", "As is"],
                        "Zero correct": ["Disabled", "Enabled", "As is"],
                        "Baseline suppression": ["Disabled", "Enabled", "As is"],
                        
                        "Display mode": ["Electrometer", "Voltage source"],
                        
                        "Trigger": ["Internal", "External"],
                        
                        }
                        
        return GUIparameter
                                 
    def get_GUIparameter(self, parameter = {}):
    
        self.mode = parameter["Mode"]
            
        self.range = parameter['Range']

        self.port_string = parameter["Port"]
        
        self.voltage_source_value = parameter["Voltage source in V"]
        
        self.zero_auto = parameter["Auto zero"] # to not mix up with function auto_zero
        
        # self.zero_check = parameter["Zero check"]
        
        self.zero_correct = parameter["Zero correct"]
        
        self.baseline_suppression = parameter["Baseline suppression"]
        
        self.display_mode = parameter["Display mode"]

        self.trigger_mode = parameter['Trigger']
        
        # here, the variables and units are defined, based on the selection of the user
        # we have as many variables as channels are selected
        self.variables = [self.mode_variables[self.mode]]
        self.units = [self.mode_units[self.mode]]  
        self.plottype = [True] # True to plot data
        self.savetype = [True] # True to save data

                
    def initialize(self):
        pass
        # self.port.write("DCL")
        # self.port.write("LLO")
        
    def deinitialize(self):
        
        pass
        # self.port.write("GTL")

    def configure(self):
    
        # Mode
        self.port.write(self.modes[self.mode] + "X")

        
        # Trigger
        if self.trigger_mode == "Internal":
            self.port.write("T2X")  # Continuous Mode, Triggered by GET
        elif self.trigger_mode == "External":
            self.port.write("T6X")  # Continuous Mode, Triggered with External Trigger
            
        # Range
        self.port.write(self.range + "X")
      
        # automatic zero at the beginning
        if self.zero_auto == "On":
            self.port.write("C1XZ1XC0X") # as proposed in the manual
        
    
        # if self.zero_check == "Off":
            # self.port.write("C0X")
        # elif self.zero_check == "On":
            # self.port.write("C1X")
             
        if self.zero_correct == "Disabled":
            self.port.write("Z0X")
        elif self.zero_correct == "Enabeld":
            self.port.write("Z1X")
            
        if self.baseline_suppression == "Disabled":
            self.port.write("N0X")
        elif self.baseline_suppression == "Enabled":
            self.port.write("N1X")
            
        # Reading mode    
        self.port.write("B0X") # Electrometer
        
        # Display mode
        if self.display_mode == "Electrometer":
            self.port.write("D0X")
        elif self.display_mode == "Voltage source":
            self.port.write("D1X")
          
        # Data store
        self.port.write("Q7X")  # disabled
        
        # Data format
        self.port.write("G0X") # Reading with prefix (NDCV-1.23456E+00)
 
        # Voltage source
        val = round(float(self.voltage_source_value) * 2.0,1) / 2.0 # this way we round to 50 mV steps
        self.port.write("V%1.4fX" % val)
        
        # Voltage source operate
        if float(self.voltage_source_value) == 0.0:
            self.port.write("O0X")
        else:
            self.port.write("O1X")
        
        
    def reconfigure(self, parameters, keys):
        """ This function is called if a parameter of GUI changes during the run by using the parameter syntax """
    
        # print(parameters, keys)
        
        if "Voltage source in V" in keys:
        
            self.voltage_source_value = parameters["Voltage source in V"]
            val = round(float(self.voltage_source_value) * 2.0,1) / 2.0 # this way we round to 50 mV steps
            self.port.write("V%1.4fX" % val)
 
 
    def deinitialize(self):
        pass
            
            
    def measure(self):    
        if self.trigger_mode == "Internal":
            self.port.write("GET")  # triggers a new measurement                                

    def call(self):
    
        answer = self.port.read()  # here we read the response from the "READ?" request in 'measure'
        # print("Response to Get command:", answer)

        val = float(answer[4:])
        
        return [val]  # an arbitrary value that needs to be replaced by the real measurement value

        
        
    def auto_zero(self):
        self.port.write("C1XZ1XC0X") # as proposed in the manual
       
    """
    """