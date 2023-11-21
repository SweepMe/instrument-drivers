# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2020-2023 SweepMe! GmbH (sweep-me.net)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# SweepMe! device class
# Type: Logger
# Device: Inficon SQC-310C

import time
from collections import OrderedDict

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = '''
                    <h3>Inficon SQC-310C</h3>
                    <p>Device class for a 4-channel deposition controller. Supported is the readout of 4 channels that can be individually selected. In case of a SQC-310, only sensor 1 and sensor 2 can be readout.</p>
                    <p>Basically, this device classes treats the instrument like a rate monitor and does not support the deposition features.<br />&nbsp;</p>
                    <p><strong>Setup:</strong></p>
                    <ul>
                    <li>Default baudrate is 19200. Please make sure your instruments works at this baudrate or use the port manager of SweepMe! to change the baudrate.</li>
                    </ul>
                    <p><strong>Known issues:</strong></p>
                    <ul>
                    <li>Checksums are not supported or checked yet.&nbsp;</li>
                    </ul>
                    <p><strong>Return variables:</strong></p>
                    <ul>
                    <li>Rate in A/s</li>
                    <li>Thickness in nm</li>
                    <li>Xtal life: 100 % = new, 0% = dead</li>
                    </ul>
                  '''
                  
    
    ## not supported yet: changing tooling, density or z-factor must still be implemented
    ## at the moment one can just readout the current rate, thickness, xtal life     
    """
    Concept: 
    - For each sensor a tooling is set
    - For each sensor a material is defined with density and z-factor 
    - For each sensor a film is created
    - To use each sensor independently, the sensors, the films and the materials are connected:
     
    Sensor 1 - Film 1 - Material 1 
    Sensor 2 - Film 2 - Material 2 
    Sensor 3 - Film 3 - Material 3
    Sensor 4 - Film 4 - Material 4
    
    """
    
    def __init__(self):
    
        EmptyDevice.__init__(self)
    
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {    "timeout": 2,
                                    "baudrate": 19200, # 19200 (default), 115200
                                    "bytesize": 8,
                                    "stopbits": 1,
                                    "xonxoff": True,
                                    "raw_read": True,
                                    "raw_write": True,
                                    }

        self.variables = ["Thickness", "Rate", "XTAL used"]
        self.units = ["nm", "Ang/s", "%"]
        
        self.sync_character = "!"
        
        self.response_characters = {
            "A": "Command understood, normal response",
            "C": "Invalid command",
            "D": "Problem with data in command",
            "E": "SQC-310 in wrong mode for this command",
            "F": "Invalid CRC",
            "G": "Response length exceeds 221 characters",
        }
                                
        self.reading_timeout = 2
    
    def set_GUIparameter(self):
    
        gui_parameter = {
                        # "Channel": ["1", "2", "3", "4"],
                        
                        "Reset thickness": False,
                        # "Film" : "1",
                        
                        "": None, # Empty line
                        
                        "Sensor1": True,
                        # "Film1" : [ "15", "14", "13", "12", "11", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "As is"],
                        # "Set Density1": False,
                        # "Density1 in g/cm^3" : "1.3",
                        # "Set Tooling1" : False,
                        # "Tooling1 in %" : "100.0",
                        
                        " ": None, # Empty line
                        
                        "Sensor2": False,
                        # "Film2" : [ "15", "14", "13", "12", "11", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "As is"],
                        # "Set Density2": False,
                        # "Density2 in g/cm^3" : "1.3",
                        # "Set Tooling2" : False,
                        # "Tooling2 in %" : "100.0",
                        
                        "  ": None, # Empty line
                        
                        "Sensor3": False,
                        # "Film3" : [ "15", "14", "13", "12", "11", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "As is"],
                        # "Set Density3": False,
                        # "Density3 in g/cm^3" : "1.3",
                        # "Set Tooling3" : False,
                        # "Tooling3 in %" : "100.0",
                        
                        "   ": None, # Empty line
                        
                        "Sensor4": False,
                        # "Film4" : [ "15", "14", "13", "12", "11", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "As is"],
                        # "Reset thickness4" : False,  # To avoid accidental resetting when recording 
                        # "Set Density4": False,
                        # "Density4 in g/cm^3" : "1.3",
                        # "Set Tooling4" : False,
                        # "Tooling4 in %" : "100.0",
                        }
        
        return gui_parameter
        
    def get_GUIparameter(self, parameter={}):
    
        # As there are many parameters, we just make the dictionary available in the entire class
        self.parameter = parameter
    
        # some empty lists that we can fill whenever a sensor is selected
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []
        
        for i in range(1, 5, 1):
            if self.parameter["Sensor%i" % i]:
            
                self.variables += ["Thickness%i" % i, "Rate%i" % i, "Xtal%i life" % i]
                self.units += ["nm", "A/s", "%"]
                self.plottype += [True, True, True]
                self.savetype += [True, True, True]

    def initialize(self):
        
        # Request version
        self.send_message("@")
        answer = self.receive_message()
        # print("Version:", answer)
        
        # check whether it is a SQC-310 (2 channels) or a SQC-310C (4 channels)
        number_channels = self.get_number_channels()

        # if sensor 3 or 4 is used, but only two sensors are available (it is then a SQC-310),
        # we have to stop the measurement
        if number_channels == 2:
            for i in [3,4]:
                if self.parameter["Sensor%i" % i]:
                    self.stop_Measurement("Sensor %i cannot be used as the SQC-310 can only readout 2 sensors" % i)
                    return False
                
    def configure(self):
    
        if self.parameter["Reset thickness"]:
            self.reset_thickness()

        """
        # 1. empty process or delete and create process
        self.delete_all_layer_in_process(100)
        
        # 2. set active process
        self.set_active_process(100)

        ## not used yet: changing tooling, density or z-factor must still be implemented
        ## at the moment one can just readout the current rate, thickness, xtal life
        

        for i in range(1,5,1):
            if self.parameter["Sensor%i" % i]:
            
                ## set material name
                self.set_material_name(95+i, "Material Sensor%i" % (95+i))
            
                ## set tooling
                if self.parameter["Set Tooling%i" % i]:
                    self.set_sensor_tooling(i, self.parameter["Tooling%i in %%" % i])            
                    
                ## set density
                if self.parameter["Set Density%i" % i]:
                    self.set_material_density(95+i, self.parameter["Density%i in g/cm^3" % i])
                    
                ## set z-factor
                # not supported yet
                
                ## link film and material
                self.set_film_material(45+i,95+i) # we use identical numbers for film and material

                ## Add codep layers to process for each sensor/material/film to be processed
                self.add_layer_to_process(100, 1, 45+i, codep = True)
                
                
        # 100 Materials
        # 50 Films
        # 1000 Layers
        # 100 Processes
        """

    def measure(self):
    
        self.return_values = []
        
        for i in range(1 ,5, 1):
            if self.parameter["Sensor%i" % i]:

                # Empty line to separate all channels
                print()
                
                #Request thickness
                self.send_message("N%i" % i)
                #Get thickness
                answer = self.receive_message()
                thickness = float(answer) * 100 # in nm
                # print("Thickness%i:" % i, thickness)
                
                #Request rate
                self.send_message("L%i" % i)            
                #Get rate
                answer = self.receive_message()
                rate = float(answer)
                # print("Rate%i:" % i, rate)
                

                # Request crystal live
                status, frequency, xtal_life = self.get_crystal_life(i)

                # adding the values for each sensor
                self.return_values += [thickness, rate, xtal_life]

    def read_result(self):
        pass
        
    def call(self):
        return self.return_values

    # commands that are introduced by the device class #

    def get_number_channels(self):
        
        # Request number_channels
        self.send_message("J")
        # Get number_channels
        answer = self.receive_message()
        number_channels = int(answer)
        # print("Number channels:", number_channels)
        
        return number_channels

    def reset_thickness(self):
        # reset thickness
        self.send_message("U32")
        answer = self.receive_message()
       
    def reset_time(self):
        # reset time
        self.send_message("U33")
        answer = self.receive_message()
    
    def set_sensor_tooling(self, sensor, tooling):
        # set sensor tooling
        self.send_message("HA%s 1 %s" % (str(sensor), str(tooling)))
        answer = self.receive_message()
        
    def get_sensor_tooling(self, sensor):
        
        # Request tooling
        self.send_message("HA%s? 1" % str(sensor))
        # Get tooling
        answer = self.receive_message()
        tooling = float(answer)
        # print("Tooling%s:" % str(sensor), tooling)
        
        return tooling
        
    def get_crystal_life(self, sensor):
        """ """
        self.send_message("PA%i" % (int(sensor)))
        answer = self.receive_message()
        
        try:
            answer = answer.split(' ') 

            try:
                status = answer[0]
            except:
                status = "Status fail"
                
            try:
                frequency = float(answer[1])
            except:
                frequency = float('nan')
                
            try:
                xtal_life = float(answer[2]) 
            except:
                xtal_life = float('nan')

        except:
            status = "Error"
            frequency = float('nan')
            xtal_life = float('nan')
            
        return status, frequency, xtal_life
    
    def set_film_name(self, film, name):
    
        self.send_message("A2 %i %i" % (int(film), int(material)))
        answer = self.receive_message()
    
    def set_film_material(self, film, material):
        """ set which material is used for a certain film """
    
        self.send_message("A2 %i 4 %i" % (int(film), int(material)))
        answer = self.receive_message()

    def set_material_name(self, material_number, name):
        """ set a name for a given material number, maximum 16 characters """
    
        self.send_message("F%i 1 %s" % (int(material_number), str(name)[0:16] ))
        answer = self.receive_message()

    def get_material_name(self, material_number):
        """ get the name for a given material number """
        
        self.send_message("F%i? 1" % (int(material_number)))
        answer = self.receive_message()
        name = str(answer)
        
        return name

    def set_material_density(self, material_number, density):
        """ set a density for a given material number """
        
        self.send_message("F%i 2 %s" % (int(material_number), str(density)))
        answer = self.receive_message()
        
    def get_material_density(self, material_number):
        """ get the density for a given material number """
        
        self.send_message("F%i? 2" % (int(material_number)))
        answer = self.receive_message()
        density = float(answer)
        
        return density

    def set_material_zfactor(self, material_number, zfactor):
        """ set a z-factor for a given material number """
        
        self.send_message("F%i 3 %i" % (int(material_number), int(zfactor)))
        answer = self.receive_message()
        
    def get_material_zfactor(self, material_number):
        """ get the z-factor for a given material number """
        
        self.send_message("F%i? 3" % (int(material_number)))
        
        answer = self.receive_message()
        zfactor = float(answer)
        
        return zfactor

    def set_active_process(self, process_number):
        """ set the active process number """
        
        self.send_message("T%i" % (int(process_number)))
        answer = self.receive_message()
        
    def stop_active_process(self):
    
        self.send_message("U1")
        answer = self.receive_message()

    def delete_process(self, process_number):
        
        self.send_message("CA%i? 2" % (int(process_number)))
        answer = self.receive_message()
    
    def delete_all_layer_in_process(self, process_number):
    
        self.send_message("CA%i? 3" % (int(process_number)))
        answer = self.receive_message()
        
    def add_layer_to_process(self, process_number, layer_number, film_number, codep = False):
        
        self.send_message("CC%i %i %i? %i" % (int(process_number), int(layer_number), int(film_number), int(codep)+1))
        answer = self.receive_message()

    # additional convenience functions #
   
    def send_message(self, cmd):
    
        # print()
        # print("Command sent", cmd)
    
        cmd = cmd.replace(".", "").replace(",", "")  # decimal points are removed
        length_character = self.get_lengthcharacter(cmd)
        
        crc = self.calculate_crc(length_character + cmd)
        command = self.sync_character + length_character + cmd + crc[0] + crc[1]
        b = bytearray()
        b.extend(command.encode('latin1'))
        self.port.write(b)

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
        length_character = self.port.read(1).decode()
        
        # 3. calculate length 
        length_message = ord(length_character) - 35  # including response character and message
        
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
        
        # 8. evaluate response character
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
        length_character = self.get_lengthcharacter(reply, write_or_read="read")
        
        #crc1_calc, crc2_calc = self.calculate_crc(length_character + reply)
        #if crc1_read == crc1_calc and crc2_read == crc2_calc:
        #    pass
        #else:
        #    print("Received checksums:", crc1_read, crc2_read)
        #    print("Calculated checksums:", crc1_calc, crc2_calc)
        #    print("Warning: Checksum for message '%s' does not match" % reply)
            
        return reply
        
    def get_lengthcharacter(self, cmd, write_or_read="write"):
    
        if write_or_read == "write":
            return chr(len(cmd) + 34) # 34 is always added to be not accidentally the sync character "!"
        else:
            return chr(len(cmd) + 35) # 35 is added to returning messages

    def calculate_crc(self, cmd): 
    
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
        crc1 = chr(0)
        crc2 = chr(0)
        
        return crc1, crc2    
