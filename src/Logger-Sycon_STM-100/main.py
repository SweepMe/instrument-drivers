# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018-2021 Axel Fischer (sweep-me.net)
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
# Device: STM-100


import time

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    """
    <h4>Connection</h4>
    Device has to be connected via a Null modem cable and the baudrate has to be selected correctly via the dip switches in the back.<br>
    Further informations can be found at the Sweep-me <a href="https://sweep-me.net/device/85/Sycon_STM-100/">device page</a>
    <h4>Parameters</h4>
    All settings from the Parameter section are applied once upon measurement start or on hitting the 'Retrieve' button!
    <h4>Channel</h4>
    Channel to be used 
    <h4>Density</h4>
    Density values have to be in the range [0.500 ... 99.99] g/cm^3
    <h4>Tooling</h4>
    Tooling values have to be in the range [10.0 .. 399] %
    <h4>XTAL</h4>
    The variable XTAL used returns the crystal life percentage: 100% is fresh, 0% is dead. If XTAL FAIL 'not-a-number' is returned.
    """
    
    actions = ["reset_thickness", "reset_timer"]
    
    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "STM100"
    
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {    "timeout": 2,
                                    "baudrate": 9600,
                                    "bytesize": 8,
                                    "stopbits": 1,
                                    "raw_read": True,
                                    "raw_write": True,
                                    "rstrip": False,
                                    }

        self.variables = ["Thickness", "Rate", "Tooling", "Density", "XTAL life"]
        self.units = ["nm", "A/s", "%", "g/cm^3", "%"]
        self.plottype = [True, True, False, False, True]
        self.savetype = [True, True, True, True, True]
        
        self.STX = chr(0x02)
        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "Reset thickness" : False,  # To avoid accidental reseting when recording 
                        "Reset time" : False,       # ongoing experiment - Better opt-in than opt-outs
                        "Channel" : [ "9", "8", "7", "6", "5", "4", "3", "2", "1", "As is"],
                        "Set Density": False,
                        "Density in g/cm^3" : "1.35",
                        "Set Tooling" : False,
                        "Tooling in %" : "32.2",
                        }
                        
        return GUIparameter
        
    def get_GUIparameter(self, parameter = {}):  
    
        self.ResetThickness = parameter["Reset thickness"]
        self.ResetTime = parameter["Reset time"]
        self.Channel = parameter["Channel"]
        self.SetDensity = parameter["Set Density"]
        self.SetTooling = parameter["Set Tooling"]
        self.Tooling = parameter["Tooling in %"]
        self.Density = parameter["Density in g/cm^3"]
            
        
    """ semantic standard functions start here """    
        
    def initialize(self):
    
        self.writeCommand("@")
        self.model = self.readAnswer()
        
        #self.writeCommand("J?")
        #self.t = self.readAnswer()
        
    def configure(self): 
    
        if self.Channel != "As is":
            self.writeCommand("i%s" % self.Channel)
            self.readAnswer()
            
        if self.ResetThickness:
            self.writeCommand("C") 
            self.readAnswer()
            
        if self.ResetTime:
            self.writeCommand("D")
            self.readAnswer()
            
        if self.SetDensity:
            self.writeCommand("E=" + self.Density)
            answer = self.readAnswer()
            if not answer[1] in ['B', 'A']:
                self.stop_Measurement("There was an error while writing density - check format, see description")
                return False
            
        if self.SetTooling:
            self.writeCommand("J=" + self.Tooling)
            answer = self.readAnswer()
            if not answer[1] in ['B', 'A']:
                self.stop_Measurement("There was an error while writing tooling - check format, see description")
                return False
                
        # Tooling factor
        self.writeCommand("J?")
        self.t = self.readAnswer()[0]
        self.t = float(self.t)
        
        # Density
        self.writeCommand("E?")
        self.e = self.readAnswer()[0]
        self.e = float(self.e)
           

    def call(self):
    
        # Thickness
        self.writeCommand("S")    
        self.d = self.readAnswer()[0]
        try:
            self.d = float(self.d)/10 
        except:
            self.d = float('nan')
        
        # Rate
        self.writeCommand("T")
        self.r = self.readAnswer()[0]
        try:
            self.r = float(self.r)
        except:
            self.r = float('nan')
        
        
        # Xtal used
        self.writeCommand("M")
        if self.readAnswer()[0] == "@":
            self.writeCommand("V")
            self.v = self.readAnswer()[0]
            self.v = float(self.v)
        else:
            self.v = float('nan')
        
        return [self.d, self.r, self.t, self.e, self.v]
        
        
    """ convenience functions start here """
        
    def readAnswer(self):
        """ returns a tuple containing answer string and success character """
                       
        x = self.port.read(1)
        #print("First character:", x[0])       
        
        if x[0] == ord(self.STX):
                    
            length = self.port.read(1)[0]  # read length character
            #print("Length:", length)
            
            success = self.port.read(1).decode('latin-1') # read success character
            #print("Success:", success)
            
            if length > 1:
                answer = self.port.read(length-1).decode('latin-1') # read message
            else:
                answer = ""
                
            #print("Answer:", answer)    
                
            checksum = self.port.read(1).decode('latin-1')  # read check sum
            
            if not checksum == self.calculate_checksum(success + answer):       
                self.message_Box("Sycon STM-100: Incorrect checksum. Please check whether you have a proper connection!")
                
            return answer, success
 
    def writeCommand(self, cmd):
    
        length = chr(len(cmd))
        checksum = self.calculate_checksum(cmd)
        cmd_to_write = (self.STX + length + cmd + checksum).encode("latin1")
        self.port.write(cmd_to_write)
        
        
    def calculate_checksum(self, cmd):
        
        return chr(sum([ord(char) for char in cmd]) % 256)


    """ setter/getter functions start here """
    
    def reset_thickness(self):
        """ resets thickness to zero """
        self.writeCommand("C")
        self.readAnswer()
        
    def reset_timer(self):
        """ resets timer to zero """
        self.writeCommand("D")
        self.readAnswer()
        
    def get_thickness(self):
        """ returns thickness in nm """
        
        self.writeCommand("S")
        d = self.readAnswer()[0]
        
        try: 
            d = float(d)/10  # in nm
        except:
            d =  float('nan')
        
        return d
 
        
    def get_rate(self):
        """ returns rate in A/s """
        self.writeCommand("T")
        r = self.readAnswer()[0]
        
        try: 
            r = float(r)
        except:
            r = float('nan')    
        
        return r
    