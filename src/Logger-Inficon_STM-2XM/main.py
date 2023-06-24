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
# Device: Inficon STM-2XM


import time

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """
    <h4>Connection</h4>
    <ul>
    <li>So far only, the Sycon protocol is supported with a baudrate of 9600. Please use System settings -&gt;</li>
    <li>RS-232 -&gt; use SMDP address 16</li>
    <li>RS-485 -&gt; use SMDP address 17 to 254, all instruments need the same baudrate (protocol not supported yet!)</li>
    </ul>
    <h4>Handling</h4>
    <ul>
    <li>Make sure that different films are used if both sensors are used! Otherwise setting film properties for one sensor will overwrite the film properties of the other sensor.</li>
    <li>Select the sensors you like to read out.</li>
    <li>Use 'As is' to use the currently active film.</li>
    <li>All settings from the Parameter section are applied once upon measurement start or on hitting the 'Retrieve' button!</li>
    </ul>
    <h4>Film</h4>
    <p>Film to be used</p>
    <h4>Density</h4>
    <p>Density values have to be in the range [0.40 ... 99.99] g/cm^3</p>
    <h4>Tooling</h4>
    <p>Tooling values have to be in the range [10.0 .. 999.9] %</p>
    <h4>XTAL</h4>
    <p>The variable XTAL used returns the crystal life percentage: 0% is fresh, 100% is dead. If XTAL FAIL 'not-a-number' is returned.</p>
    """
    
    actions = ["reset_thickness", "reset_thickness1", "reset_thickness2"]
    
    def __init__(self):
    
        
    
        EmptyDevice.__init__(self)
        
        self.shortname = "STM-2XM"
    
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {    "timeout": 1,
                                    "baudrate": 9600, # So far only the 'Sycon protocol' is supported uses baudrate 9600 SMDP address 16 must be 16
                                    # Valid baudrates for the SMDP protocol are 9600, 38400, 115200 (not supported yet!)
                                    "bytesize": 8,
                                    "stopbits": 1,
                                    "raw_read": True,
                                    "raw_write": True,
                                    }

       
        self.STX = chr(0x02)
        
        ## Protocols: 1 - Sycon, 0 - SMDP
        
    def set_GUIparameter(self):
        
        GUIparameter = {
                       
                        
                        "Sensor1": True,
                        "Film1" : ["As is"] + ["%i" %i for i in range(1,16,1)],
                        "Reset thickness1" : False,  # To avoid accidental resetting when recording 
                        "Set Density1": False,
                        "Density1 in g/cm^3" : "1.3",
                        "Set Tooling1" : False,
                        "Tooling1 in %" : "100.0",
                        "": None,
                        "Sensor2": False,
                        "Film2" : ["As is"] + ["%i" %i for i in range(1,16,1)],
                        "Reset thickness2" : False,  # To avoid accidental resetting when recording 
                        "Set Density2": False,
                        "Density2 in g/cm^3" : "1.3",
                        "Set Tooling2" : False,
                        "Tooling2 in %" : "100.0",
                        }
                        
        return GUIparameter
        
    def get_GUIparameter(self, parameter = {}):  
    
        self.Sensor1 = parameter["Sensor1"]
        self.ResetThickness1 = parameter["Reset thickness1"]
        self.Film1 = parameter["Film1"]
        self.SetDensity1 = parameter["Set Density1"]
        self.SetTooling1 = parameter["Set Tooling1"]
        self.Tooling1 = parameter["Tooling1 in %"]
        self.Density1 = parameter["Density1 in g/cm^3"]
        
        self.Sensor2 = parameter["Sensor2"]
        self.ResetThickness2 = parameter["Reset thickness2"]
        self.Film2 = parameter["Film2"]
        self.SetDensity2 = parameter["Set Density2"]
        self.SetTooling2 = parameter["Set Tooling2"]
        self.Tooling2 = parameter["Tooling2 in %"]
        self.Density2 = parameter["Density2 in g/cm^3"]
        
        
        # self.variables = ["Thickness", "Rate", "Tooling", "Density", "XTAL life"]
        self.variables = []
        # self.units = ["nm", "A/s", "%", "g/cm^3", "%"]
        self.units = []
        # self.plottype = [True, True, False, False, True]
        self.plottype = []
        # self.savetype = [True, True, True, True, True]
        self.savetype = []
        
        if self.Sensor1:
        
            # self.variables = ["Thickness", "Rate", "Tooling", "Density", "XTAL life"]
            self.variables += ["Thickness1", "Rate1", "XTAL1 life"]
            # self.units = ["nm", "A/s", "%", "g/cm^3", "%"]
            self.units += ["nm", "A/s", "%"]
            # self.plottype = [True, True, False, False, True]
            self.plottype += [True, True, True]
            # self.savetype = [True, True, True, True, True]
            self.savetype += [True, True, True]
        
        if self.Sensor2:
        
            # self.variables = ["Thickness", "Rate", "Tooling", "Density", "XTAL life"]
            self.variables += ["Thickness2", "Rate2", "XTAL2 life"]
            # self.units = ["nm", "A/s", "%", "g/cm^3", "%"]
            self.units += ["nm", "A/s", "%"]
            # self.plottype = [True, True, False, False, True]
            self.plottype += [True, True, True]
            # self.savetype = [True, True, True, True, True]
            self.savetype += [True, True, True]
            
        
    def initialize(self):
    
        if self.Sensor1:
            if self.SetDensity1:    
                if self.Density1 == "":
                    self.stop_Measurement("Density1 is empty. Please enter a number")
                    return False

            if self.SetTooling1:
                if self.Tooling1 == "":
                    self.stop_Measurement("Tooling1 is empty. Please enter a number")
                    return False
                    
        if self.Sensor2:        
            if self.SetDensity2:    
                if self.Density2 == "":
                    self.stop_Measurement("Density2 is empty. Please enter a number")
                    return False
        
            if self.SetTooling2:
                if self.Tooling2 == "":
                    self.stop_Measurement("Tooling2 is empty. Please enter a number")
                    return False
    
        self.writeCommand("@")
        self.model = self.readAnswer()
        # print("Model", self.model)
        
        if self.Sensor1:
            # Query for first sensor the selected film
            
            if not self.Film1 == "As is":
                self.writeCommand("H1,0=%s" % self.Film1)
                answer = self.readAnswer()
                # print("Film1:", answer)
                
            else:
                self.writeCommand("G1,0")
                self.Film1 = self.readAnswer()
                # print("Film1:", self.Film2)
                
                
        if self.Sensor2:
            # Query for first sensor the selected film
            
            if not self.Film2 == "As is":
                self.writeCommand("H1,1=%s" % self.Film2)
                answer = self.readAnswer()
                # print("Film2:", answer)
                
            else:
                self.writeCommand("G1,1")
                self.Film2 = self.readAnswer()
                # print("Film2:", self.Film2)
             

        
    def configure(self): 
    
        # Property
        
        # 2 - Density
        # 3 - Z-factor
        # 4 - Tooling

        if self.Sensor1:
            if self.ResetThickness1:
                self.reset_thickness1()
                
            if self.SetDensity1:    
                self.writeCommand("J%s,2 = %s" % (self.Film1, self.Density1))
                answer = self.readAnswer()
            
            if self.SetTooling1:
                self.writeCommand("J%s,4 = %s" % (self.Film1, self.Tooling1))
                answer = self.readAnswer()

            
                
        if self.Sensor2:    
            if self.ResetThickness2:
                self.reset_thickness2()
                
            if self.SetDensity2:    
                self.writeCommand("J%s,2 = %s" % (self.Film2, self.Density2))
                answer = self.readAnswer()
            
            if self.SetTooling2:
                self.writeCommand("J%s,4 = %s" % (self.Film2, self.Tooling2))
                answer = self.readAnswer()
            
    def call(self):
    
        values = []
    
        if self.Sensor1:

            # Thickness
            self.writeCommand("Q2,0")
            answer = self.readAnswer()
            self.d1 = float(answer)*100.0 # conversion from kA to nm

            # Rate
            self.writeCommand("Q17,0")
            answer = self.readAnswer()
            self.r1 = float(answer)
            
            # Xtal used
            self.writeCommand("Q5,0")
            answer = self.readAnswer()
            try:
                self.v1 = float(answer)
            except:
                self.v1 = float('nan')
            
            values += [self.d1, self.r1, self.v1]
            
        if self.Sensor2:

            # Thickness
            self.writeCommand("Q2,1")
            answer = self.readAnswer()
            self.d2 = float(answer)*100.0 # conversion from kA to nm

            # Rate
            self.writeCommand("Q17,1")
            answer = self.readAnswer()
            self.r2 = float(answer)
            
            # Xtal used
            self.writeCommand("Q5,1")
            answer = self.readAnswer()
            try:
                self.v2 = float(answer)
            except:
                self.v2 = float('nan')
            
            values += [self.d2, self.r2, self.v2]
        
        
        # Tooling factor
        # self.writeCommand("J?")
        # self.t = self.readAnswer()[0]
        # self.t = float(self.t)
        
        # Density
        # self.writeCommand("E?")
        # self.e = self.readAnswer()[0]
        # self.e = float(self.e)
        
       
        return values
        
    def readAnswer(self):
               
        x = self.port.read(1)

        if x[0] == ord(self.STX):
        
            
            length = self.port.read(1)[0]
            answer = self.port.read(length)
            self.port.read(1)
            return answer[1:] # we cut off the first byte as it is the return error code 
              
        else:
            x = self.port.read(1)

            if x[0] == ord(self.STX):
            
                length = self.port.read(1)[0]
                answer = self.port.read(length)

                return answer[1:].decode(), chr(answer[0])
                
        #else:
        #    print(self.port.read(self.port.in_waiting()))
        #    return None    
                        
    def writeCommand(self, cmd):
        
        length = chr(len(cmd))
        checksum = chr(sum([ord(char) for char in cmd]) % 256)
        cmd_to_write = (self.STX + length + cmd + checksum).encode("latin1")
        self.port.write(cmd_to_write)


    def reset_thickness(self):
        if self.Sensor1:
            self.reset_thickness1()
            
        if self.Sensor2:
            self.reset_thickness2()

    def reset_thickness1(self):
        self.writeCommand("O2") 
        answer = self.readAnswer()
        
    def reset_thickness2(self):
        self.writeCommand("O3") 
        answer = self.readAnswer()  
        