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
# Device: PREVAC TMC-13


import time
import struct

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """
    
    """
    
    actions = ["reset_thickness"]
    
    def __init__(self):
    
        
        EmptyDevice.__init__(self)
        
        self.shortname = "TMC-13"
    
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {    "timeout": 1,
                                    "baudrate": 57600, # default
                                    "bytesize": 8,
                                    "stopbits": 1,
                                    "raw_read": True,
                                    "raw_write": True,
                                    }

        self.startbyte = chr(0xBB)
        #self.device_address = chr(0xC8)
        self.device_address = chr(0x01)
        self.host_address = chr(0xFF)
        
        
    def set_GUIparameter(self):
        
        GUIparameter = {
                
                        "Channel": ["1", "2", "3", "4", "5", "6"],
                       
                        "Reset thickness" : False,  # To avoid accidental resetting when recording 
                        
                        "Set Tooling" : False,
                        "Tooling in %" : "100.0",
                        
                        "Set Density": False,
                        "Density in g/cm^3" : "1.3",
                        
                        "Set Acoustic Impedance": False,
                        "Acoustic impedance in 1e5 g/cm²/s": 1.0,
                        }
                        
        return GUIparameter
        
    def get_GUIparameter(self, parameter = {}):  
    
        self.channel = "\x01" #, parameter["Channel"]
        
        self.ResetThickness = parameter["Reset thickness"]
        
        self.SetTooling = parameter["Set Tooling"]
        self.Tooling = parameter["Tooling in %"]
        
        self.SetDensity = parameter["Set Density"]
        self.Density = parameter["Density in g/cm^3"]
        
        self.SetAcousticImpedance = parameter["Set Acoustic Impedance"]
        self.AcousticImpedance = parameter["Acoustic impedance in 1e5 g/cm²/s"]
                
        
        self.variables = ["Thickness", "Rate", "XTAL life"]
        self.units = ["nm", "A/s", "%"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

    def connect(self):
    
        #print("get_host")
        self.host_address = self.get_host()
        print("Host address", self.host_address)
        
        #print("get_serial_number")
        serial_number = self.get_serial_number()
        print("Serial number:", serial_number)
        
        #print("get_product_number")
        product_number = self.get_product_number()
        print("Product number:", product_number)
        
        #print("get_device_version")
        device_version = self.get_device_version()
        print("Device version:", device_version)
        
        print("assign master")
        self.assign_master()
        

    #def disconnect(self):
    #    
    #    print("release master")
    #    self.release_master()
        
    def initialize(self):
    
        if self.SetTooling:
            if self.Tooling == "":
                self.stop_Measurement("Tooling is empty. Please enter a number")
                return False
    
        if self.SetDensity:    
            if self.Density == "":
                self.stop_Measurement("Density is empty. Please enter a number")
                return False

        if self.SetAcousticImpedance:
            if self.AcousticImpedance == "":
                self.stop_Measurement("Acoustic impedance is empty. Please enter a number")
                return False
                    
        self.frequency_min = self.get_minimum_frequency()          
        self.frequency_max = self.get_maximum_frequency()
        
   
    def configure(self): 
    
        if self.ResetThickness:
            self.reset_thickness()
            
        if self.SetDensity:    
            self.set_material_density(float(self.Density))

        if self.SetTooling:
            self.set_tooling_factor(float(self.Tooling))
            
        if self.SetAcousticImpedance:
            self.set_material_acoustic_impedance(float(self.AcousticImpedance))

    def call(self):
    
        values = []
   
        # Thickness
        self.d1 = self.get_thickness()

        # Rate
        self.r1 = self.get_rate()
        
        # Xtal life
        self.v1 = self.get_crystal_life()
        
        values += [self.d1, self.r1, self.v1]
            
        return values
        

    """ convenience functions """

    # Byte Description
    # 1 - HEADER First byte is responsible for identifying the serial protocol.
    # Header in hexadecimal is 0xBB
    # 2 - DATA LENGTH Length of the data 􀏐ield. Maximum data 􀏐ile length is 0xFF
    # (256 bytes). Prevac Serial Protocol
    # 3 - DEVICE ADDRESS Identification of hardware device address. Default value is
    # 0xC8
    # 4 - HOST ADDRESS Host identification address. Assigned to host during the
    # registration process (using a unique ID).
    # 5 - FUNCTION CODE - MSB First procedure function code byte
    # 8th (MSB) bit is the read(0)/write(1) select bit
    # 6 - FUNCTION CODE - LSB Second procedure function code byte
    # 7 .. [7 + DATA LENGTH] -
    # DATA FIELD
    # Data capture needed to realize defined functions.
    # [7 + DATA LENGTH] + 1(last
    # frame position) - CRC
    # CRC is simple module 256 calculated without protocol
    # header byte(see section 6.5.2.4)


    def get_value(self, code, value = ""):

        MSB, LSB = struct.pack(">H", code)
        MSB = MSB|0  # needed to indicate value will be read
        
        value = str(value)
        length = chr(len(value))
        # value = [chr(x) for x in value]
        
        message = length + self.device_address + self.host_address + chr(MSB) + chr(LSB) + value
        
        checksum = chr(sum([ord(char) for char in message]) % 256)
        cmd_to_write = (self.startbyte + message + checksum).encode("latin1")
        self.port.write(cmd_to_write)
    
    def set_value(self, code, value=""):
       
        MSB, LSB = struct.pack(">H", code)
        MSB = MSB|1 # needed to indicate value will be set

        value = str(value)
        length = chr(len(value))
        # value = [chr(x) for x in value]
        
        #print(MSB, LSB, type(MSB), type(LSB))
        
        message = length + self.device_address + self.host_address + chr(MSB) + chr(LSB) + value
        
        checksum = chr(sum([ord(char) for char in message]) % 256)
        cmd_to_write = (self.startbyte + message + checksum).encode("latin1")
        #print(cmd_to_write)
        self.port.write(cmd_to_write)
    
    
    
    def read_value(self):
    
        
        """ Error codes """
        # 0x00 No errors, order executed correctly
        # 0x91 Value is too large
        # 0x92 Value is too small
        # 0x93 Wrong parameter (probably wrong data format or index out of range)
        # 0x95 Read only parameter, write prohibited
        # 0x96 Host not know and not registered
        # 0x97 Host know but not selected to remote control
        # 0x98 Device configured to work in local mode
        # 0x99 Operation or parameter is not available
    
               
        x = self.port.read(1)

        if x[0] == ord(self.startbyte):
        
            length = self.port.read(1)[0] # should be already int because of indexing
            device = self.port.read(1)[0] 
            host = self.port.read(1)[0]
            self.port.read(1)[0]
            self.port.read(1)[0]
            #print("Length", length)
            answer = self.port.read(length).decode('latin1')
            self.port.read(1) # checksum
            
            # do some checksum check here
            
            if self.port.in_waiting() > 0:
                print("In waiting bytes:", self.port.read(self.port.in_waiting()))
            
            #print("Answer", answer, answer.encode('latin1'))
            
            return answer # we cut off the first byte as it is the return error code
            
        else:
            print("PREVAC TMC-13: Returned message does not start with correct byte (0xbb)")
              
    
    """ setter/getter functions """
    
    def get_host(self):
        
        code = 0x7FF0
        self.get_value(code, "SweepMe")
        host = self.read_value()
        
        return host

    def assign_master(self):
        
        # Example assign master
        # BB    01      C8     01    FF F1     01      BB
        # start length  device host  code      value   checksum
        
        # b'\xbb\x01\x01\x7f\x7f\xf11"'
        
        code = 0x7FF1
        self.set_value(code, 1) # Value 1 -> assign
        answer = self.read_value()
        
        
        #print(answer)
        
        
    def release_master(self):
    
        # b'\xbb\x01\x01\x7f\x7f\xf10!'

        code = 0x7FF1
        self.set_value(code, 0) # Value 0 -> release
        self.read_value()
        
        
    def get_product_number(self):
        """ returns the product number """
    
        code = 0x7F01
        
        self.get_value(code)
        pn = self.read_value()
        
        return pn
        
    def get_device_version(self):
        """ returns the device version """
        
        code = 0x7F03
        
        self.get_value(code)
        dv = self.read_value()
        
        return dv
        
    def get_serial_number(self):
        """ returns the serial number of the device """
        
        code = 0x7F02
        self.get_value(code)
        sn = self.read_value()
        
        return sn
        
    def get_thickness(self):
        """ returns thickness in nm """
    
        code = 0x0202
        self.get_value(code, self.channel)
        answer = self.read_value()      
        value = struct.unpack('>d', answer.encode('latin1'))[0]
        value = value/10.0 # strip off the channel number and change value from Angstrom to nm
        
        return value
        
       
    def get_thickness_unit(self):
        """ returns the unit in which the thickness is displayed """
        
        code = 0x0203
        self.get_value(code, self.channel)
        
        unit = self.read_value()[1:] # strip off the channel number
        # 0 - A
        # 1 - kA
        # 2 - nm
        
        
    def get_rate(self):
        """ returns the rate in A/s """
    
        code = 0x0204
        self.get_value(code, self.channel)
        
        answer = self.read_value()
        
        #print("Answer", answer, repr(answer))
        value = struct.unpack('>d', answer.encode('latin1'))[0]
        #print(value, type(value))
        
        #value = answer[1:] # strip off the channel number
        
        return value
        
    def get_tooling_factor(self):
        """ return tooling factor in % """
        
        code = 0x020D
        self.get_value(code, self.channel)
        value = self.read_value()[1:]
       
        return value
        
    def set_tooling_factor(self, value):
        """ set tooling factor in % """
        
        code = 0x020D
        value = struct.pack(">d", float(value)).decode('latin1')
        print(value, repr(value))
        self.set_value(code, self.channel + value)
        value = self.read_value()
       
    def get_material_density(self):
        """ returns density in g/cm³ """
        
        code = 0x0214
        self.get_value(code, self.channel)
        value = self.read_value()
        
        return value
        
    def set_material_density(self, value):
        """ set density in g/cm³ """
        
        code = 0x0214
        value = "%1.2f" % float(value)
        self.set_value(code, self.channel + value)
        value = self.read_value()
        
        return value
        
        
    def set_material_acoustic_impedance(self, value):
        """ set acoustic impedance in 1e5g/cm²/s """
        
        code = 0x0215
        value = struct.pack(">d", float(value)).decode('latin1')
        self.set_value(code, self.channel + value)
        value = self.read_value()
       
        
        
    def get_crystal_life(self):
        """ returns crystal life in % """
    
        frequency_current = self.get_crystal_frequency()
            
            
            
        life = (frequency_current - self.frequency_min)/(self.frequency_max - self.frequency_min) * 100.0

        return round(life, 2)
        
        
    def get_crystal_frequency(self):
        """ return tooling factor in % """
        
        code = 0x0201
        self.get_value(code, self.channel)
        
        answer = self.read_value()
        
        #print("Answer", answer, repr(answer))
        value = struct.unpack('>d', answer.encode('latin1'))[0]
        #print(value, type(value))
       
        return value
        
        
    def get_maximum_frequency(self):
        """ return tooling factor in % """
        
        code = 0x020F
        self.get_value(code, self.channel)
        
        answer = self.read_value()
        
        #print("Answer", answer, repr(answer))
        value = struct.unpack('>d', answer.encode('latin1'))[0]
        #print(value, type(value))
       
        return value

    def get_minimum_frequency(self):
        """ return tooling factor in % """
        
        code = 0x020E
        self.get_value(code, self.channel)
        
        answer = self.read_value()
        
        #print("Answer", answer, repr(answer))
        value = struct.unpack('>d', answer.encode('latin1'))[0]
        #print(value, type(value))
       
        return value

    def reset_thickness(self):
            
        code = 0x0211
        self.set_value(code, self.channel)
        value = self.read_value()
  
          
        
  
        