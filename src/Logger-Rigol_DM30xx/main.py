# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 Axel Fischer (sweep-me.net)
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
# Device: Rigol DM30xx


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """
                    <p><strong>Usage:</strong></p>
                    <p>Select the measurement mode and the driver will return the corresponding value and standard unit. You can select a rate which is only supported by some measurement modes (Voltage DC/AC, Current DC/AC, Resistance, 4W Resistance, Sensor). Other paraemters such as Range and Resolution are currently not support by this driver.</p>
                    <p><strong>Communication:</strong></p>
                    <ul>
                    <li>GPIB default address is 7</li>
                    <li>COM (RS-232) default is baudrate 9600 and parity None. it might be necessary to use a nullmodem adapter.</li>
                    </ul>
                    <p><strong>Known issues:</strong></p>
                    <p>When using COM port the measurement stops after some time with Timeout error (typically after 17-25 s). The reason is unknown. A new measurement can be started, but changing to another port type, e.g. USBTMC fails afterwards and one needs to restart the instrument.&nbsp;</p>
                  """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "DM30xx"
        
        self.port_manager = True
        self.port_types = ["GPIB", "USB", "COM", "TCPIP"]
        
        self.port_properties = { 
                                    "timeout": 4.0,
                                    "EOLwrite": "\r\n", # for COM port       
                                    "EOLread": "\n",    # for COM port    
                                    "baudrate": 9600,   # factory default
                                    "bytesize": 8,      # factory default
                                    "parity": "N",      # factory default
                                    "Exception": True,
                                    "delay": 0.05,
                                }   
                                 
        
        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        self.modes = {
                        "Voltage DC":    ":VOLT:DC",   
                        "Voltage AC":    ":VOLT:AC",
                        "Current DC":    ":CURR:DC",
                        "Current AC":    ":CURR:AC",
                        "Resistance":    ":RES",                         
                        "4W Resistance": ":FRES",
                        "Capacitance":   ":CAP",
                        "Diode":         ":DIOD",
                        "Continuity":    ":CONT",
                        "Periode":       ":PER",
                        "Frequency":     ":FREQ",
                        }
                        
        self.return_modes = {
                            "DCV"  : "Voltage DC",
                            "ACV"  : "Voltage AC",
                            "DCI"  : "Current DC",
                            "ACI"  : "Current AC",
                            "2WR"  : "Resistance",
                            "4WR"  : "4W Resistance",
                            "CAP"  : "Capacitance",
                            "DIODE": "Diode",
                            "CONT" : "Continuity",
                            "PERI" : "Periode",
                            "FREQ" : "Frequency",
                            }
                     
        # this dictionary sets the unit of each mode
        self.mode_units = {
                            "Voltage DC":     "V", 
                            "Voltage AC":     "V",
                            "Current DC":     "A",
                            "Current AC":     "A",
                            "Resistance":     "Ohm", 
                            "4W Resistance":  "Ohm", 
                            "Capacitance":    "F",
                            "Diode":          "V",
                            "Continuity":     "Ohm",
                            "Periode":        "s",
                            "Frequency":      "Hz",
                        }
          
        self.rates = {
                        "Fast":   "F",
                        "Medium": "M",
                        "Slow":   "S",
                        }
            
        # section below is maybe needed later
        """  
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
  
                            }   
        """                    
                                
                                                                 
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "Mode" : list(self.modes.keys()),        
                        "Rate": list(self.rates.keys()),
                        }
                        
        return GUIparameter
                                 
    def get_GUIparameter(self, parameter = {}):
    
        # these two lines will be commented later. Just printing all GUI parameters here
        # print()
        # print(parameter)
    
        self.mode = parameter['Mode']
        
        self.rate = parameter['Rate']

        # we can retrieve the selected port, 
        self.port_string = parameter["Port"]
        
        ## here, the variables and units are defined, based on the selection of the user
        self.variables = [self.mode]  # we add the selected measurement mode as variable, e.g. 'Voltage DC'
        self.units = [self.mode_units[self.mode]] 
        self.plottype =  [True]  # True to plot data
        self.savetype =  [True]  # True to save data

                
    def initialize(self):
    
        ## Identification
        # idn = self.get_identification()
        # print(idn)
    
        ## Serial number
        # sn = self.get_serial_number()
        # print(sn)
        
        ## Let's make sure that the DMM used the right command set
        if not self.port_string.startswith("COM"): # it looks like that this command is not supported with COM
            cs = self.get_command_set()
            if cs != "RIGOL":
                self.set_command_set("RIGOL")
    
        ## Resetting all properties is not a bad idea. 
        ## However, as long as we do not support all parameters, we would overwrite manually selected parameters.
        # self.port.write("*RST")
        
        self.port.write("*CLS") # reset all values
        

    def deinitialize(self):
        pass

    def configure(self):
        
        
        ## Mode
        self.port.write(":FUNC?")
        current_mode = self.port.read()
        
        if self.return_modes[current_mode] != self.mode:
            self.port.write(":FUNC" + self.modes[self.mode])
            
        ## Speed
        self.port.write(":RATE" + self.modes[self.mode] + " " + self.rates[self.rate])
        
        ## Range
        # if not self.mode in ["Temperature", "Continuity", "Diode"]:
            # self.port.write(":SENS:%s:RANG:AUTO ON" % (self.modes[self.mode]))

            
        ## Trigger
        #print("Configuring trigger")
        # self.port.write("INIT:CONT OFF")  # needed to use "READ?" command
        #self.port.write("TRIG:SOUR %s" % self.trigger_types[self.trigger_type])
        
     
    def unconfigure(self):
        pass

            
    def measure(self): 
        self.port.write(":MEAS" + self.modes[self.mode] + "?")  # triggers a new measurement                      

    def call(self):

        answer = self.port.read()  # here we read the response from the ":MEAS:...?" request in 'measure'
        # print("Response to MEAS? command:", answer)

        return [float(answer)] 
        
    
    """ here, setter/getter functions are listed """
    
    
    def get_identification(self):
        
        self.port.write("*IDN?")
        return self.port.read()
    
    def get_serial_number(self):
        
        self.port.write(":SYST:SERI?")
        return self.port.read()
        
    def get_command_set(self):
        
        self.port.write("CMDS?")
        return self.port.read()
        
    def set_command_set(self, cmd_set):
    
        if cmd_set in ["RIGOL", "AGILENT", "FLUKE"]:
            self.port.write("CMDS " + cmd_set)
        else:
            raise Exception("Command set '%s' for 'set_command_set' is not a valid key." % cmd_set) 

        
        
    """
    """