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
# Type: Switch
# Device: Biophysical Tools P2CS


from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!
# If you like to see the source code of EmptyDevice, take a look at the pysweepme package that contains this file

class Device(EmptyDevice):

    ## here you can add html formatted description to your device class that is shown by modules like 'Logger' or 'Switch' that have a description field.
    description =   """
                    no description yet
                    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "P2CS" # short name will be shown in the sequencer

        self.port_manager = True 
        self.port_types = ["COM"]
        self.port_properties = {
                                "timeout": 2.0,
                                "baudrate": 115200,
                                #"delay": 0.1,
                                "EOL": "\r\n",
                                }
            
            
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "SweepMode": ["Pressure in mbar", "External", "None"],
                        "Channel": ["1", "2", "3", "4"],
                        # "Pressure range": ["low", "high"],
                        "Pressure limit low in mbar": -500,
                        "Pressure limit high in mbar": 500,
                        }

        return GUIparameter

    def get_GUIparameter(self, parameter):
    
        self.sweepmode = parameter["SweepMode"]
        self.channel = int(parameter["Channel"])
        # self.pressure_range = parameter["Pressure range"]
        self.pressure_limit_low = float(parameter["Pressure limit low in mbar"])
        self.pressure_limit_high = float(parameter["Pressure limit high in mbar"])
        
        self.variables = ["Pressure"] # define as many variables you need
        self.units = ["mbar"] # make sure that you have as many units as you have variables
        self.plottype = [True]   # True to plot data, corresponding to self.variables
        self.savetype = [True]   # True to save data, corresponding to self.variables
       
        if self.sweepmode == "Pressure in mbar":
            self.variables.append("Pressure, set")
            self.units.append("mbar")
            self.plottype.append(True)
            self.savetype.append(True)

    def initialize(self):
        pass
        #self.port.write("*idn?")
        #identification = self.port.read()
        #print("Identification:", identification)
        
        #self.port.write("get:system:serialnumber")
        #serial_number = self.port.read()
        #print("Serial number:", serial_number)
        #
        #self.port.write("get:system:serialnumber")
        #serial_number = self.port.read()
        #self.port.read(2)
        #print("Serial number:", serial_number)
        
        #self.port.write("get:system:sensors")
        #print(self.port.read())
        #print(self.port.read())
        #print(self.port.read())
        #print(self.port.read())
        #sensors = self.port.read()
        #print("Sensors:\n", sensors)
        
        #self.port.write("get:system:options")
        #options = self.port.read()
        #print("Options:\n", options)
        
        if self.pressure_limit_low > -500:
            self.stop_Measurement("Pressure low limit exceeds minimal possible value. Please use -500 mbar or lower.")
            return False
            
        if self.pressure_limit_high <= 0:
            self.stop_Measurement("Pressure high limit must be above 0 mbar.")
            return False    

        self.pressure_setvalue = float('nan')

    def deinitialize(self):

        self.port.write("output:pressure:reset") # will switch all channels to 0 mbar
        answer = self.port.read()
        #print(answer)
               

    def configure(self):
        
        #pass
        #self.port.write("get:setvalues")
        #setvalues = self.port.read()
        #print("Set values:\n", setvalues)
        #
        ## Pressure range or pressure sensor??
        # self.port.write("set:mode:pressure:{low,high}          self.pressure_range
        # set:mode:pressure:standard and set:mode:pressure:hires
        
        self.port.write("set:pressure:limit:lo %1.1f" % self.pressure_limit_low)
        answer = self.port.read()
        #print(answer)
 
        self.port.write("set:pressure:limit:hi %1.1f" % self.pressure_limit_high)
        answer = self.port.read()
        #print(answer)
        
#        if self.sweepmode == "Pressure in mbar":
#            self.port.write("set:mode:usb")
#            answer = self.port.read()
#            print(answer)
#
#        elif self.sweepmode == "External":
#            self.port.write("set:mode:analog")
#            answer = self.port.read()
#            print(answer)
        
    def unconfigure(self):
        # called if the measurement procedure leaves a branch of the sequencer and the module is not used in the next branch
        pass
                   
    def apply(self):
    
        if self.sweepmode == "Pressure in mbar":
            new_pressure = ["x", "x", "x", "x"]
            new_pressure[self.channel-1] = "%1.2f" % float(self.value)
            self.port.write("outp:pres %s;%s;%s;%s" % tuple(new_pressure))
            self.port.read()
              
            self.pressure_setvalue = float(self.value)
            
    def measure(self):
        self.port.write("measure:pres")
        # self.port.write("measure:pres NONE")
      

    def read_result(self):
        answer = self.port.read()
        #print(answer)
        self.pressure_value = float(answer.split(";")[self.channel-1])
        
    def call(self):
    
        if self.sweepmode == "Pressure in mbar":
            return [self.pressure_value, self.pressure_setvalue]
        else:
            return [self.pressure_value]
        
