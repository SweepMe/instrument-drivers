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

# Contribution: We like to thank Shayan Miri A. S. for providing the initial version of this driver.


# SweepMe! device class
# Type: Logger
# Device: Inficon SQM-160


import time

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """
                  
                  """
    
    actions = ["reset_thickness"]
    
    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "SQM-160"
    
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {    "timeout": 1,
                                    "baudrate": 115200,
                                    "bytesize": 8,
                                    "xonxoff": True,
                                    "raw_read": True,
                                    "raw_write": True,
                                    }

        
        self.sync_character = "!"
       
        
        self.response_characters = {
                                    "A": "Command understood, normal response",
                                    "C": "Invalid command",
                                    "D": "Problem with data in command",
                                }
                                
        self.reading_timeout = 2

        
    def set_GUIparameter(self):
        # GUIparameter = {"Reset thickness": False}
        
        # self.chan = self.get_number_channels()
        
        # for i in range(1,7,1):
        
            # GUIparameter["Sensor%i"%i] = True
        GUIparameter = {
                       
                        # "Channel": ["1", "2", "3", "4"],
                        
                        "Reset thickness": False,
                        # "Film" : "1",
                        
                        "Sensor1": True,
                        # "Film1" : [ "15", "14", "13", "12", "11", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "As is"],
                        # "Set Density1": False,
                        # "Density1 in g/cm^3" : "1.3",
                        # "Set Tooling1" : False,
                        # "Tooling1 in %" : "100.0",
                        "Sensor2": True,
                        "Sensor3": False,
                        "Sensor4": False,
                        "Sensor5": False,
                        "Sensor6": False,
                        }
                        
        return GUIparameter
        
    def get_GUIparameter(self, parameter={}):
    
        # As there are many parameters, we just make the dictionary available in the entire class
        self.parameter = parameter
    
        # some empty lists that we can fill whenever a sensor is selected
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []
        
        for i in range(1,7,1):
            if self.parameter["Sensor%i" % i]:
            
                self.variables += ["Thickness%i" % i, "Rate%i" % i, "Xtal%i life" % i]
                self.units += ["nm", "A/s", "%"]
                self.plottype += [True, True, True]
                self.savetype += [True, True, True]
            
        
    def initialize(self):
    
        self.number_channels = self.get_number_channels()
        
        # version_string = self.get_version()
        # print("Version:", version_string)

        
    def configure(self):
        pass
        # self.writeCommand("B 0.25 0 0 1 1 %s %s 100 100 100 100" %(self.Tooling1, self.Tooling2))
        # answer = self.readAnswer()
        # print(answer)
        
        # if self.Sensor1:
            # if self.ResetThickness1:
                # self.reset_thickness()
                
            # if self.SetDensity1:    
                # self.writeCommand("J%s,2 = %s" % (self.Density1))
                # answer = self.readAnswer()
            
            # if self.SetTooling1:
                # self.writeCommand("J%s,4 = %s" % (self.Tooling1))
                # answer = self.readAnswer()

            
                
        # if self.Sensor2:    
            # if self.ResetThickness2:
                # self.reset_thickness()
                
            # if self.SetDensity2:    
                # self.writeCommand("J%s,2 = %s" % (self.Density2))
                # answer = self.readAnswer()
            
            # if self.SetTooling2:
                # self.writeCommand("B_0.25_0_0_1_1_%s_%s_100_100_100_100" %(self.Tooling1) %(self.Tooling2))
                # answer = self.readAnswer()
            
    def call(self):
    
        values = []
        
        for i in range(1,7,1):             
            if self.parameter["Sensor%i" % i]:
            
                # Thickness
                self.send_message("N%i" %i)
                answer = self.receive_message()
                self.d = float(answer)*100.0 # conversion from kA to nm

                # Rate
                self.send_message("L%i?" %i)
                answer = self.receive_message()
                self.r = float(answer)
                
                # Xtal used
                self.send_message("R%i?" %i)
                answer = self.receive_message()
                try:
                    self.v = float(answer)
                except:
                    self.v = float('nan')
            
                # Frequency
                # self.send_message("P1")
                # answer = self.readAnswer()
                # print(answer[1:-2])
                # self.p1 = float(answer[1:-2])
            
                values += [self.d, self.r, self.v]

        return values

    def get_lengthcharacter(self, cmd, write_or_read = "write"):
    
        if write_or_read == "write":
            return chr(len(cmd) + 34) # 34 is always added to be not accidentally the sync character "!"
        else:
            return chr(len(cmd) + 35) # 35 is added to returning messages


    def send_message(self, cmd):
    
        # print("Command sent", cmd)
        # print(len(cmd))
        cmd = cmd.replace(".", "").replace(",","") # decimal points are removed
        length_character = self.get_lengthcharacter(cmd)
        
        crc = self.checksum(length_character + cmd)
        command = self.sync_character + length_character + cmd + crc[0] + crc[1]
        b = bytearray()
        b.extend(command.encode('latin1'))
        self.port.write(b)
        
        # print(command)
        # self.port.write(command.encode())
        # self.port.write(command)
        
        self.last_message = cmd

        
    def receive_message(self):
       
        # 1. read until sync_character !
        starttime = time.perf_counter()
        while True:
            if self.port.read(1) == self.sync_character.encode():
                # print("sync character found")
                break
               
            if time.perf_counter() - starttime > self.reading_timeout:
                # print("Timeout reached")
                return False
               
        # 2. read length_character
        length_character = self.port.read(1)
        
        # 3. calculate length 
        length_message = ord(length_character) - 35  # including response character and message
        # print(length_character, length_message)
        # print(self.port.in_waiting())
        
        # 4. read message completely
        message = self.port.read(length_message)
        
        
        # print("Message:", message)

        # 5. read response character
        response_character = chr(message[0])
               
        # 6. read real message
        reply = message[1:]
        
        # 7. read crc1 and crc2 
        crc1_read = self.port.read(1)
        crc2_read = self.port.read(1)
        
        # 8. evaluate responce character
        if response_character in self.response_characters:
            if response_character != "A":
                print()
                print("Last message:", self.last_message)
                print(self.response_characters[response_character])
                return True
                
            else:
                pass
                # print("Message received successfully.")
           
        else:
            print("Unknown response character:", response_character)

        # 9. convert reply
        reply = reply.decode()
        # print("Reply:", reply)

        # 10. check crc 
        length_character = self.get_lengthcharacter(reply, write_or_read = "read")
        
        #crc1_calc, crc2_calc = self.checksum(length_character + reply)
        #if crc1_read == crc1_calc and crc2_read == crc2_calc:
        #    pass
        #else:
        #    print("Received checksums:", crc1_read, crc2_read)
        #    print("Calculated checksums:", crc1_calc, crc2_calc)
        #    print("Warning: Checksum for message '%s' does not match" % reply)
            
        return reply
        
    def readAnswer(self):
               
        x = self.port.read(1)

        if x[0] == ord(self.STX):
            length = self.port.read(1)[0]-35
            answer = self.port.read(length)
            self.port.read(1)
            return answer[1:] # we cut off the first byte as it is the return error code 
                 
        else:
            x = self.port.read(1)

            if x[0] == ord(self.STX):
            
                length = self.port.read(1)[0]
                answer = self.port.read(length)

                return answer[1:].decode(), chr(answer[0])
                
            else:
                print(self.port.read(self.port.in_waiting()))
        return None    
                        
    def writeCommand(self, cmd):
        
        length = chr(len(cmd)+34)
        # print('command:',cmd)
        # print('length:',length)
        # checksum = chr(sum([ord(char) for char in cmd]) % 256)
        checksum = self.crc_calc(length+cmd)
        # print('crc:',checksum)
        cmd_to_write = self.STX + length + cmd + checksum[0] + checksum[1]
        # print('command to write:',cmd_to_write)
        # print(type(cmd_to_write))
        self.port.write(bytes(cmd_to_write,'latin1'))


    def reset_thickness(self):
        # if self.Sensor1:
            # self.reset_thickness1()
            
        # if self.Sensor2:
            # self.reset_thickness2()
        self.writeCommand("S") 
        answer = self.readAnswer()
        
    # def reset_thickness1(self):
        # self.writeCommand("S") 
        # answer = self.readAnswer()
        
    # def reset_thickness2(self):
        # self.writeCommand("S") 
        # answer = self.readAnswer()

        
    def get_number_channels(self):

        #Request number_channels
        self.send_message("J")
        #Get number_channels
        answer = self.receive_message()
        number_channels = int(answer)
        # print("Number channels:", number_channels)
    
        return number_channels
        
    def get_version(self):
    
        # Request version
        self.send_message("@")
        answer = self.receive_message()
        # print("Rate Monitor Version:", answer)  
        return answer
    
    def checksum(self, cmd): 
    
        # return "00" # can be used for testing, the SQC-310C will ignore checksums in this case
        
        crc = 0x3fff               # crc always starts with 0x3fff
        chars = [ord(x) for x in cmd]
        for char in chars:
            crc ^= char            # exclusive OR with crc
            
            for i in range(8):        
                if crc % 2 == 1:   # if bit position 0 has a valeu of 1
                    crc >>= 1      # 1 bit shifted to the right
                    crc ^= 0x2001  # OR'd with 0x2001 
                else:
                    crc >>= 1      # 1 bit shifted to the right 
                    
        crc &= 0x3fff              # the final crc is masked with 0x3fff using logical AND
        
        bits = '{0:014b}'.format(crc) # string of the 14 significant bits
        
        crc1 = int(bits[7:14], 2)  # crc1 are the first seven bits  
        crc2 = int(bits[0:7], 2)   # crc2 are thelast seven bits  
        
        crc1 = chr(crc1 + 34)      # 34 has be added to make sure the synchronization character "!" is not returned
        crc2 = chr(crc2 + 34)      # 34 has be added to make sure the synchronization character "!" is not returned
        
        # print(ord(crc1), ord(crc2))
        
        # testing mode: The crcs are overwritten with chr(0)
        # The SQC-160 ignores the crc in this case
        # crc1 = chr(0)
        # crc2 = chr(0)
        
        return crc1, crc2    