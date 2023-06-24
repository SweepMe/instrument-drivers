# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 SweepMe! GmbH
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
# Device: Nanotec SMCI


from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!


class Device(EmptyDevice):

    description =   """
                    <p><strong>Usage</strong></p>
                    <ul>
                    <li>Position values are given in steps in absolute mode.</li>
                    <li>This driver does not support all motor parameters. Use the software NanoPro 1.70 to adjust other parameters and write them to the memory of the motor controller.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Caution</strong></p>
                    <ul>
                    <li>Before you use this driver, please make sure that the motor controller is correctly configured. For example, home positioning (reference mode) only works if all end position switches are set in the right manner.</li>
                    </ul>
                    <ul>
                    <li>Reference mode is done with the set moving direction. If this direction is changed in the memory of the motor controller to wrong direction, accidental moves can happen as no reference switch is found in the other direction or the reference position is incorrect!</li>
                    </ul>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "SMCI" # short name will be shown in the sequencer
        self.variables = ["Position"] # define as many variables you need
        self.units = ["steps"] # make sure that you have as many units as you have variables
        self.plottype = [True]   # True to plot data, corresponding to self.variables
        self.savetype = [True]   # True to save data, corresponding to self.variables
        
        
        ### use/uncomment the next line to use the port manager
        self.port_manager = True 
           
        ### use/uncomment the next line to let SweepMe! search for ports of these types. Also works if self.port_manager is False or commented.
        self.port_types = ["COM"]
        
        self.port_properties = {
                                "baudrate": 115200, # default
                                "timeout": 10.0,
                                "EOL": "\r",
                                }
                                
        self._verbose_mode = True
                                
        self.ramp_modes = {
                            0: "Trapez",
                            1: "Sinus",
                            2: "Jerkfree",
                          }
            
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode": ["Absolute position in steps"],
                        "Channel": list(range(1, 256, 1)),
                        
                        "Minimum frequency in Hz": 400,
                        "Maximum frequency in Hz": 1000,
                        "Go home after run": True,
                        }

        return GUIparameter

    def get_GUIparameter(self, parameter):

        self.channel = int(parameter["Channel"])
        self.go_home_after_run = parameter["Go home after run"]
        
        self.frequency_min = parameter["Minimum frequency in Hz"]
        self.frequency_max = parameter["Maximum frequency in Hz"]
        
    def connect(self):
        
        self.get_firmware()
        
        ready, zero, error = self.get_status()
        
        if error:
            self.set_position(0) # if there is an error, we have to reset the position to also remove position error
        
        self.get_parameter_configuration()
        self.get_last_error()
        self.get_position_mode() 
        self.get_direction()
        self.get_move_position()
        
        
    def initialize(self):
        
        
        self.set_automatic_status(0) # this is need to get an automatic status update once the move of the motor has finished
        self.is_motor_referenced() # needs latest firmware
        
        # self.set_direction(0)  # !!! only for now needs to be removed later !!!
        
        self.set_maximum_frequency(self.frequency_max)
        self.set_minimum_frequency(self.frequency_min)
        
        self.set_position_mode(4) # change to external reference mode
        self.start_motor()       
        self.reach()
                
        self.set_position_mode(2) # change to absolute positions
               
                
    def deinitialize(self):
                
        if self.go_home_after_run:
              
            self.set_move_position(0)
            self.start_motor()  
        
            """
            self.set_position_mode(4) # change to external reference mode
            self.start_motor()
            """
            # print("Auto status:", self.port.read())
        
            self.reach()
                    
            self.set_position_mode(2) # change to absolute positions
            
            self.stop_motor_decel()   

        
    def configure(self):
           
        self.set_maximum_frequency(self.frequency_max)
        self.set_minimum_frequency(self.frequency_min)
        
    def unconfigure(self):
        pass
        # self.stop_motor_decel()
        
        
    def apply(self):
        self.set_move_position(int(float(self.value)))
        self.start_motor()
      
    def reach(self):
        # print("Auto status:", self.port.read())
        
        while True:
            ready, zero, error = self.get_status()
            
            # print(ready)
            
            if ready:
                break
            if error:
                self.stop_measurement("Error during reaching position")
                return False


    def call(self):
   
        pos = self.get_position()
        
        return [pos]
        
        
    def write_command(self, cmd, val = ""):
    
        self.port.write("#%i"% int(self.channel) + cmd + val)


    def get_status(self):
        """\
            get status byte with the following bit mask: 
        
            Die Bitmaske hat 8 Bit.
            Bit 0: 1: Steuerung bereit
            Bit 1: 1: Nullposition erreicht
            Bit 2: 1: Positionsfehler
            Bit 3: 1: Eingang 1 ist gesetzt während Steuerung wieder bereit ist. Tritt dann auf, wenn die Steuerung über Eingang 1 gestartet wurde und die Steuerung schneller wieder bereit ist, als der Eingang zurückgesetzt wurde.
            Bit 4 und 6 sind immer auf 0, Bit 5 und 7 immer auf 1 gestellt.
            
        """
        
        cmd = "$"
        self.write_command(cmd)
            
        answer = self.port.read()
        self.verboseprint("Status:", answer)
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
        
        bit_string = '{:08b}'.format(value)[::-1]
        
        self.verboseprint("Status:", bit_string)
        
        self.verboseprint("Ready:", bit_string[0])
        self.verboseprint("At zero position:", bit_string[0])
        self.verboseprint("Position error:", bit_string[2])
       

        return bit_string[0] == "1", bit_string[1] == "1", bit_string[2] == "1"
        
        
    def set_automatic_status(self, val = 1):
        """\
            sets whether the status is automatically sent after the end of a move

            0: don't send status automatically
            1: send status automatically
        """
                
        cmd = "J"
        self.write_command(cmd + str(int(val)))
            
        answer = self.port.read()
        self.verboseprint("Set automatic status:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value

    def get_firmware(self):
        
        cmd = "v"
        self.write_command(cmd)
            
        answer = self.port.read()
        self.verboseprint("Firmware:",answer)
        
        index = answer.find(cmd)
        
        value = answer[index+len(cmd)+1:] # +1 to remove space after command v

        return value
    
    def set_position_mode(self, val):
        """ \
            sets the positions mode with val being in an index from 1 to 4:
                   
            1: Relative Positionierung; Der Befehl 2.6.7 Verfahrweg einstellen 's' gibt den Verfahrweg relativ zur aktuellen Position an. Der Befehl 2.6.15 Drehrichtung einstellen 'd' gibt die Richtung an. Der Parameter 2.6.7 Verfahrweg einstellen 's' muss positiv sein.
            2: Absolute Positionierung; Der Befehl 2.6.7 Verfahrweg einstellen 's' gibt die Zielposition relativ zur Referenzposition an. Der Befehl 2.6.15 Drehrichtung einstellen 'd' wird ignoriert.
            3: Interne Referenzfahrt; Der Motor läuft mit der unteren Geschwindigkeit in die Richtung, die in Befehl 2.6.15 Drehrichtung einstellen 'd' eingestellt ist, bis er den Indexstrich des Drehgeber erreicht. Danach läuft der Motor eine feste Anzahl von Schritten, so dass er den Indexstrich wieder verlässt. Für die Richtung des Freifahrens siehe Befehl 2.5.9 Endschalterverhalten einstellen 'l'. Dieser Modus macht nur bei Motoren mit eingebautem und angeschlossenem Drehgeber Sinn.
            4: Externe Referenzfahrt; Der Motor läuft mit der oberen Geschwindigkeit in die Richtung, die in Befehl 2.6.15 Drehrichtung einstellen 'd' eingestellt ist, bis er den Endschalter erreicht hat. Danach wird je nach Einstellung eine Freifahrt durchgeführt. Siehe Befehl 2.5.9 Endschalterverhalten einstellen 'l'.
            
            Drehzahlmodus not supported
            5: Drehzahlmodus; Wird der Motor gestartet, dreht der Motor bis zur Maximaldrehzahl mit der eingestellten Rampe hoch. Änderungen in der Geschwindigkeit oder Drehrichtung werden mit der eingestellten Rampe sofort angefahre
        """
        
        val = int(val)
        
        if val == 5:
            raise ValueError("Nanotec SMCI: engine speed mode (p=5) is not supported, yet.")
        
        if val < 0 or val > 4:
            raise ValueError("Nanotec SMCI: position mode index out of range.")
        
        cmd = "p"
        self.write_command(cmd + str(val))
            
        answer = self.port.read()
        self.verboseprint("Set position mode:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value
    
    def get_position_mode(self):
        
        cmd = "Zp"
        self.write_command(cmd)
            
        answer = self.port.read()
        self.verboseprint("Position mode", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value
        
        
    def set_minimum_frequency(self, val):
        """ sets the minimum frequency in Hz """
                
        cmd = "u"
        self.write_command(cmd + str(int(val)))
            
        answer = self.port.read()
        self.verboseprint("Set minimum frequency:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value
        
    
    def get_minimum_frequency(self):
        """ gets the minimum frequency in Hz """
    
        cmd = "Zu"
        self.write_command(cmd)
            
        answer = self.port.read()
        self.verboseprint("Minimum frequency:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value    
        
    
    def set_maximum_frequency(self, val):
        """ sets the maximum frequency in Hz """
                
        cmd = "o"
        self.write_command(cmd + str(int(val)))
            
        answer = self.port.read()
        self.verboseprint("Set maximum frequency:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value
        
    
    def get_maximum_frequency(self):
        """ gets the maximum frequency in Hz """
    
        cmd = "Zu"
        self.write_command(cmd)
            
        answer = self.port.read()
        self.verboseprint("Maximum frequency:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value  
        
    def set_move_position(self, val):
        """ sets the move position according to absolute or relative mode that is used when motor is started """
                
        cmd = "s"
        self.write_command(cmd + str(int(val)))
            
        answer = self.port.read()
        self.verboseprint("Set move position:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value
        
    
    def get_move_position(self):
        """ gets the move position according to absolute or relative mode that is when motor is started """
    
        cmd = "Zs"
        self.write_command(cmd)
            
        answer = self.port.read()
        self.verboseprint("Move position:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value

    def set_direction(self, val):
        """\
            sets the rotation direction for relative mode

            0: left
            1: right
            
        """
        
        cmd = "d"
        self.write_command(cmd + str(int(val)))
            
        answer = self.port.read()
        self.verboseprint("Set direction:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value
    
    def set_direction_left(self):
        """ sets the rotation direction for relative mode to left """
        
        return self.set_direction(0)
        
    def set_direction_right(self):
        """ sets the rotation direction for relative mode to right """
        
        return self.set_direction(1)
        

    
    def get_direction(self):
        
        cmd = "Zd"
        self.write_command(cmd)
            
        answer = self.port.read()
        self.verboseprint("Direction:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value
        
    def start_motor(self):
        """ starts the motor move with the current set parameters """
                
        cmd = "A"
        self.write_command(cmd)
            
        answer = self.port.read()
        self.verboseprint("Start motor:", answer)
           
    def stop_motor(self, val=0):
        """\
            stops the motor move with the following modes:
            
            0: quick stop
            1: stop with deceleration
        """
                
        cmd = "S"
        self.write_command(cmd+str(int(val)))
            
        answer = self.port.read()
        self.verboseprint("Stop motor:", answer)
        
    def stop_motor_quick(self):
        """ stops the motor quickly """
        
        self.stop_motor(0)
        
    def stop_motor_decel(self):
        """ stops the motor with a deceleration phase """
        
        self.stop_motor(1)
        
        
    def set_ramp_mode(self, val):
        """ sets the ramp mode where val ia an index from 0 to 2 """
        
        cmd = ":ramp_mode="
        self.write_command(cmd + str(int(val)))
            
        answer = self.port.read()
        self.verboseprint("Set ramp mode:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value
        

    def get_ramp_mode(self):
        """ get the current ramp mode """
        
        cmd = ":ramp_mode"
        self.write_command(cmd)
            
        answer = self.port.read()
        self.verboseprint("Ramp mode:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value
        
        
        
    def set_position(self, val):
        """ sets the position according to absolute or relative mode """
        
        cmd = "D"
        self.write_command(cmd + str(int(val)))
            
        answer = self.port.read()
        self.verboseprint("Set position:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value
        
    
    def get_position(self):
        """ gets the absolute position of the internal position counter, counter is zeroed after reference move """
    
        cmd = "C"
        self.write_command(cmd)
            
        answer = self.port.read()
        self.verboseprint("Position:", answer)
       
        index = answer.find(cmd)
        
        value = int(answer[index+len(cmd):])
            
        return value
        
    def move_to_position(self):
        """ move to position by setting by setting move position and start motor """
        
        pass
        
        
        
    def is_motor_referenced(self):
        """\
            queries whether motor already did a reference positioning

            Return values:
            
            0: is not referenced
            1: is referenced
            """
        
        cmd = ":is_referenced"
        self.write_command(cmd)
            
        answer = self.port.read()
        self.verboseprint("Is referenced:", answer)
       
        index = answer.find(cmd)
        value = (answer[index+len(cmd):]) == "1"
            
        return value
        
        
    def get_parameter_configuration(self):
    
        cmd = "Z|"
        self.write_command(cmd)
            
        answer = self.port.read()
        self.verboseprint("Configuration:", answer)
       
        index = answer.find(cmd)
        
        value = answer[index+len(cmd):]
            
        return value
        
        
    def get_last_error(self):
        
        cmd = "E"
        self.write_command(cmd)
            
        answer = self.port.read()
        self.verboseprint("Last error index:", answer)
       
        index = answer.find(cmd)
        
        value = answer[index+len(cmd):]
        
        cmd = "Z"
        self.write_command(cmd + str(value) + "E")
            
        answer = self.port.read()
        self.verboseprint("Last error:", answer)
       
        index = answer.find(cmd)
        
        value = answer[index+len(cmd):]

        return value
        
    def verboseprint(self, *args, **kwargs):
        if self._verbose_mode:
            print(*args, **kwargs)
            
""" """